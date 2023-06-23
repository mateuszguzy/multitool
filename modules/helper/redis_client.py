import redis

from config.settings import REDIS_PORT, REDIS_DB, REDIS_HOST
from utils.abstracts_classes import AbstractContextManager


class RedisClient(AbstractContextManager):
    client: redis.Redis = None

    class Config:
        arbitrary_types_allowed = True

    def __init__(self):
        super().__init__()
        self.client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

    def __enter__(self):
        return self.client

    def __exit__(self, type, value, traceback):
        self.client.close()
