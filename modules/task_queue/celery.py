from celery import Celery  # type: ignore
from kombu.utils.json import register_type  # type: ignore

from config.settings import REDIS_PORT, REDIS_DB, REDIS_HOST
from utils.custom_dataclasses import StartModuleEvent, ResultEvent
from utils.custom_serializers.result_event_serializer import (
    result_event_encoder,
    result_event_data_load,
)
from utils.custom_serializers.start_module_event_serializer import (
    start_module_event_encoder,
    start_module_event_data_load,
)

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

# custom serializers for custom dataclasses
register_type(
    StartModuleEvent,
    "start_module_event_serializer",
    lambda obj: start_module_event_encoder(obj),
    lambda obj: start_module_event_data_load(obj),
)

register_type(
    ResultEvent,
    "result_event_serializer",
    lambda obj: result_event_encoder(obj),
    lambda obj: result_event_data_load(obj),
)
