import sys

from click import Abort

from modules.core.steering_module.steering_module import SteeringModule
from modules.task_queue.tasks import (
    log_results,
    results_listener_task,
    stop_listener_tasks,
)
from modules.user_interface.user_interface import UserInterface
from utils.custom_exceptions import (
    AbortException,
    UnhandledException,
)
from utils.utils import (
    prepare_final_results_dictionary,
    log_exception,
)


def main():
    sys.excepthook = log_exception
    user_interface = UserInterface()

    try:
        user_input = user_interface.run()

    except Abort:
        raise AbortException("Program aborted")

    except Exception:
        raise UnhandledException("Unhandled exception")

    if user_input.output_after_every_finding:
        results_listener_task.delay()

    steering_module = SteeringModule(user_input=user_input)
    steering_module.run()

    results = prepare_final_results_dictionary()
    log_results.delay(result=results, module=__name__)

    stop_listener_tasks()


if __name__ == "__main__":
    main()
