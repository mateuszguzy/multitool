import sys

from click import Abort

from config.settings import steering_module_logger, SHOW_TRACEBACKS
from modules.core.steering_module.steering_module import SteeringModule
from modules.user_interface.user_interface import UserInterface
from utils.custom_exceptions import (
    AbortException,
    UnhandledException,
)
from utils.utils import (
    prepare_final_results_dictionary,
    format_exception_with_traceback_for_logging,
)
from modules.task_queue.tasks import log_results


def main():
    sys.tracebacklimit = SHOW_TRACEBACKS
    user_interface = UserInterface()

    try:
        user_interface.run()
    except Abort as exc:
        steering_module_logger.exception(
            format_exception_with_traceback_for_logging(exc)
        )
        raise AbortException("Program aborted")
    except Exception as exc:
        steering_module_logger.exception(
            format_exception_with_traceback_for_logging(exc)
        )
        raise UnhandledException("Unhandled exception")

    user_input = getattr(user_interface.cli_interface, "user_input")
    steering_module = SteeringModule(user_input=user_input)
    steering_module.run()

    results = prepare_final_results_dictionary()
    log_results.delay(result=results, module=__name__)


if __name__ == "__main__":
    main()
