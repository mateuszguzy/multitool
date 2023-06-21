from celery import Celery

from config.settings import (
    RABBITMQ_USER,
    RABBITMQ_PASSWORD,
    RABBITMQ_VHOST,
    REDIS_PORT,
    REDIS_DB,
    REDIS_URL,
)

app = Celery(
    "task_queue",
    broker=f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@localhost:5672/{RABBITMQ_VHOST}",
    backend=f"redis://{REDIS_URL}:{REDIS_PORT}/{REDIS_DB}",
    include=["modules.task_queue.tasks"],
)

if __name__ == "__main__":
    app.start()
