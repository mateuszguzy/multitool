import datetime
import sys
import time
import uuid

from click import Abort

from config.settings import steering_module_logger
from modules.core.steering_module.steering_module import SteeringModule
from modules.task_queue.tasks import (
    stop_listener_tasks,
    background_jobs_still_running,
    start_event_listeners,
    pass_result_event,
)
from modules.user_interface.user_interface import UserInterface
from utils.custom_dataclasses import ResultEvent
from utils.custom_exceptions import (
    AbortException,
    UnhandledException,
)
from utils.logging_utils import log_exception
from utils.redis_utils import prepare_final_results_dictionary

logger = steering_module_logger


def main():
    sys.excepthook = log_exception
    user_interface = UserInterface()

    try:
        user_input = user_interface.run()

    except Abort:
        raise AbortException("Program aborted")

    except Exception:
        raise UnhandledException("Unhandled exception")

    try:
        start = time.time()
        start_event_listeners(
            output_after_every_finding=user_input.output_after_every_finding
        )

        steering_module = SteeringModule(user_input=user_input)
        steering_module.run()

        # wait for all background jobs to finish before logging results
        tasks_running = True
        while tasks_running:
            tasks_running = background_jobs_still_running()

        pass_result_event.delay(
            event=ResultEvent(
                id=uuid.uuid4(),
                source_module=__name__,
                target="ALL",
                result=str(prepare_final_results_dictionary()),
            )
        )

    finally:
        stop_listener_tasks()
    stop = time.time()
    logger.info(
        f"Scan time: {str(datetime.timedelta(seconds=(round(stop-start, 2)))).split('.')[0]}"
    )


if __name__ == "__main__":
    main()
