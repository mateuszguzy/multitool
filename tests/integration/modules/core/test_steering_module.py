from modules.helper.redis_client import RedisClient


def test_run_directory_bruteforce_module(integration_steering_module_with_directory_bruteforce_test_input):
    integration_steering_module_with_directory_bruteforce_test_input.run()

    with RedisClient() as rc:
        keys = rc.keys("directory_bruteforce_*:")
        result = (rc.mget(keys))

    assert result == [b'vulnerabilities']
