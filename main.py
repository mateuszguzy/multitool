from modules.helper.redis_client import RedisClient
from utils.utils import (
    create_steering_module_instance_with_user_input,
)

# USER_INPUT_MOCK = "tests/mocked_user_input/user_input_mock_run_all_1.json"
# USER_INPUT_MOCK = "tests/mocked_user_input/user_input_mock_single_phase_1.json"
USER_INPUT_MOCK = "tests/mocked_user_input/user_input_mock_single_module_1.json"


def main():
    steering_module = create_steering_module_instance_with_user_input(USER_INPUT_MOCK)
    steering_module.run()

    with RedisClient() as rc:
        keys = rc.keys("dir_bruteforce_*:")
        print(rc.mget(keys))
        rc.flushall()


if __name__ == "__main__":
    main()
