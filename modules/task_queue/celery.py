from celery import Celery  # type: ignore

from config.settings import (
    REDIS_PORT,
    REDIS_DB,
    CELERY_BROKER_URL,
    CELERY_BROKER_BACKEND
)

app = Celery(
    "task_queue",
    broker=f"{CELERY_BROKER_URL}:{REDIS_PORT}/{REDIS_DB}",
    backend=f"{CELERY_BROKER_BACKEND}:{REDIS_PORT}/{REDIS_DB}",
    include=["modules.task_queue.tasks"],
)

if __name__ == "__main__":
    app.start()
