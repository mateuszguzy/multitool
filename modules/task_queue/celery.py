from celery import Celery  # type: ignore

from config.settings import REDIS_PORT, REDIS_DB, REDIS_HOST

app = Celery(
    "task_queue",
    broker=f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
    backend=f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
    include=["modules.task_queue.tasks"],
)

# new queue for task 'log_results' to avoid being blocked by other tasks
app.conf.task_routes = {
    "modules.task_queue.tasks.log_results": {"queue": "log_results"},
}
