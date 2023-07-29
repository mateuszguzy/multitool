import sys

import click
from click import Abort

from config.settings import SHOW_TRACEBACKS
from modules.core.steering_module.steering_module import SteeringModule
from modules.task_queue.tasks import log_results
from modules.user_interface.user_interface import UserInterface
from utils.utils import prepare_final_results_dictionary


def main():
    sys.tracebacklimit = SHOW_TRACEBACKS
    user_interface = UserInterface()

    try:
        user_interface.run()
    except Abort:
        click.echo("\n\nKeyboard interrupted. Quitting.")
        sys.exit()

    steering_module = SteeringModule(user_interface.cli_interface.user_input)
    steering_module.run()

    results = prepare_final_results_dictionary()
    log_results.delay(result=results, module=__name__)


if __name__ == "__main__":
    main()
