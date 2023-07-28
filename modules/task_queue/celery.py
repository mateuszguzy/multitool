from celery import Celery  # type: ignore

from config.settings import REDIS_PORT, REDIS_DB, REDIS_HOST

app = Celery(
    "task_queue",
    broker=f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
    backend=f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
    include=["modules.task_queue.tasks"],
)
