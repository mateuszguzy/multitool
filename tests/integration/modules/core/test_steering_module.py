from modules.helper.redis_client import RedisClient


class TestSteeringModule:
    def test_run_directory_bruteforce_module(
        self, integration_steering_module_with_directory_bruteforce_test_input
    ):
        integration_steering_module_with_directory_bruteforce_test_input.run()

        with RedisClient() as rc:
            keys = rc.keys("http://dvwa:80/|directory_bruteforce|*")
            result = rc.mget(keys)

        assert result == [b"vulnerabilities"]
