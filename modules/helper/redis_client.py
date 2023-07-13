import redis

from config.settings import REDIS_PORT, REDIS_DB, REDIS_HOST
from utils.abstracts_classes import AbstractRedisContextManager


class RedisClient(AbstractRedisContextManager):
    client: redis.Redis = redis.Redis()

    class Config:
        arbitrary_types_allowed = True

    def __init__(self):
        super().__init__()
        self.client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

    def __enter__(self):
        return self.client

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.client.close()
