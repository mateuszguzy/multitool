import redis

from config.settings import REDIS_HOST, REDIS_PORT, REDIS_DB
from modules.helper.redis_client import RedisClient


class TestRedisClient:
    def test_redis_client_connect_to_server(self, mocker):
        mock_redis = mocker.Mock()
        mocker.patch('redis.Redis', return_value=mock_redis)

        with RedisClient() as redis_client:
            assert redis_client == mock_redis
