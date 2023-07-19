import redis

from config.settings import REDIS_HOST, REDIS_PORT, REDIS_DB


class TestRedisClient:

    def test_redis_server_is_alive(self):
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
        response = r.ping()

        assert response is True
