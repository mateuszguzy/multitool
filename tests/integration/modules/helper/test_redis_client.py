import pytest
import redis

from config.settings import REDIS_HOST, REDIS_PORT, REDIS_DB
from modules.helper.redis_client import RedisClient


class TestRedisClient:
    def test_redis_server_is_alive(self):
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
        response = r.ping()

        assert response is True

    def test_instantiation_without_arguments(self):
        redis_client = RedisClient()

        assert isinstance(redis_client, RedisClient)

    def test_context_manager_usage(self):
        with RedisClient() as redis_client:
            assert isinstance(redis_client, redis.Redis)

    @pytest.mark.parametrize(
        "key, value", [("key", b"value"), ("key", b"123"), (123, b"value")]
    )
    def test_get_and_set_values(self, key, value):
        with RedisClient() as redis_client:
            redis_client.set(key, value)
            assert redis_client.get(key) == value

    def test_invalid_arguments(self):
        with RedisClient() as redis_client:
            with pytest.raises(redis.exceptions.DataError):
                redis_client.set("key", "value", "extra_argument")
