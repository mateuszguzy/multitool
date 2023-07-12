from celery import Celery  # type: ignore

from config.settings import (
    REDIS_PORT,
    REDIS_DB,
    REDIS_URL,
)

app = Celery(
    "task_queue",
    broker=f"redis://{REDIS_URL}:{REDIS_PORT}/{REDIS_DB}",
    backend=f"redis://{REDIS_URL}:{REDIS_PORT}/{REDIS_DB}",
    include=["modules.task_queue.tasks"],
)

if __name__ == "__main__":
    app.start()
