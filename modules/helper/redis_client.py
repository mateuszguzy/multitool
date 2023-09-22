from typing import Optional
import redis

from config.settings import REDIS_PORT, REDIS_DB, REDIS_HOST
from utils.abstracts_classes import AbstractContextManager


class RedisClient(AbstractContextManager):
    client: Optional[redis.Redis] = None

    def __init__(self):
        super().__init__()

    def __enter__(self):
        self.client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
        return self.client

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.client is not None:
            self.client.close()
            self.client = None
