import sys

import click
from click import Abort

from config.settings import SHOW_TRACEBACKS
from modules.core.steering_module.steering_module import SteeringModule
from modules.helper.redis_client import RedisClient
from modules.task_queue.tasks import log_results
from modules.user_interface.user_interface import UserInterface
from tests.conftest import create_steering_module_instance_with_user_input

# USER_INPUT_MOCK = "tests/mocked_user_input/mock_user_input_all.json"
# USER_INPUT_MOCK = "tests/mocked_user_input/mock_user_input_single_phase_recon.json"
USER_INPUT_MOCK = "tests/mocked_user_input/mock_user_input_single_module_directory_bruteforce.json"


def main():
    sys.tracebacklimit = SHOW_TRACEBACKS
    user_interface = UserInterface()

    try:
        user_interface.run()
    except Abort:
        click.echo("\n\nKeyboard interrupted. Quitting.")
        sys.exit()

    # TODO to delete after development phase
    # steering_module = create_steering_module_instance_with_user_input(USER_INPUT_MOCK)

    steering_module = SteeringModule(user_interface.cli_interface.user_input)
    steering_module.run()

    with RedisClient() as rc:
        keys = rc.keys("directory_bruteforce_*:")
        result = (rc.mget(keys))
        rc.flushall()

    log_results.delay(result=result, module=__name__)


if __name__ == "__main__":
    main()
