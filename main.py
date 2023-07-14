import sys

import click
from click import Abort

from modules.core.steering_module.steering_module import SteeringModule
from modules.helper.redis_client import RedisClient
from utils.utils import (
    create_steering_module_instance_with_user_input,
)
from modules.task_queue.tasks import log_results
from modules.user_interface.user_interface import UserInterface

# USER_INPUT_MOCK = "tests/mocked_user_input/user_input_mock_run_all_1.json"
# USER_INPUT_MOCK = "tests/mocked_user_input/user_input_mock_single_phase_1.json"
USER_INPUT_MOCK = "tests/mocked_user_input/user_input_mock_single_module_1.json"


def main():
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
        keys = rc.keys("dir_bruteforce_*:")
        result = (rc.mget(keys))
        rc.flushall()

    log_results.delay(result=result, module=__name__)


if __name__ == "__main__":
    main()
