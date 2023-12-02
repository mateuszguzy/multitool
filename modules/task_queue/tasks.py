import time
import uuid
from typing import Optional
from urllib.parse import urlparse

import celery  # type: ignore
import redis
import requests

from config.settings import (
    REDIS_HOST,
    REDIS_PORT,
    REDIS_DB,
    task_queue_logger,
    PUBSUB_RESULTS_CHANNEL_NAME,
    STEERING_MODULE,
    GET_REQUEST_TIMEOUT,
    SECONDS_TO_WAIT_FOR_MESSAGES_BEFORE_CLOSING,
    PUBSUB_LAST_MESSAGE_TIME_KEY,
)
from modules.core.dispatcher.dispatcher import Dispatcher
from modules.network.request_manager.request_manager import RequestManager
from modules.network.socket_manager.socket_manager import SocketManager
from modules.task_queue.celery import app, BaseCeleryTaskClass
from utils.custom_dataclasses import StartModuleEvent, ResultEvent
from utils.custom_serializers.result_event_serializer import (
    result_event_encoder,
    result_event_data_load,
)
from utils.custom_serializers.start_module_event_serializer import (
    start_module_event_encoder,
    start_module_event_data_load,
)
from utils.utils import (
    get_logger,
    pull_single_value_from_db,
    save_message_time,
)

logger = task_queue_logger

rc = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
pubsub = rc.pubsub()


@app.task(base=BaseCeleryTaskClass)
def log_results(event: ResultEvent) -> None:
    """
    Logs the result using the appropriate logger based on the module name.
    If a target is provided, it is included in the log message.
    """
    result = f"<{event.target}>: {event.result}"
    module_logger = get_logger(event.source_module)
    module_logger.info(result)


@app.task(base=BaseCeleryTaskClass)
def directory_bruteforce_web_request(
    request_method: str, target: str, path: str, module: str, allow_redirects: bool
) -> Optional[str]:
    url = urlparse(target)
    with RequestManager(
        method=request_method,
        scheme=url.scheme,
        netloc=url.netloc,
        path=path,
        allow_redirects=allow_redirects,
    ) as rm:
        response = rm.run()

        if response.ok:
            url = urlparse(response.url)
            pass_result_event.delay(
                event=ResultEvent(
                    id=uuid.uuid4(),
                    source_module=module,
                    target=target,
                    result=url.path,
                )
            )
            return url.path
        else:
            return None


@app.task(base=BaseCeleryTaskClass)
def lfi_web_request(
    request_method: str, target: str, allow_redirects: bool
) -> Optional[str]:
    url = urlparse(target)

    with RequestManager(
        method=request_method,
        scheme=url.scheme,
        netloc=url.netloc,
        path=url.path,
        params=url.params,
        query=url.query,
        fragment=url.fragment,
        allow_redirects=allow_redirects,
    ) as rm:
        response = rm.run()

        if response.ok:
            return response.text
        else:
            return None


@app.task(base=BaseCeleryTaskClass)
def email_scraper_web_request(target: str) -> Optional[str]:
    response = requests.get(url=target, timeout=GET_REQUEST_TIMEOUT)

    if response.ok:
        return response.text

    return None


@app.task(base=BaseCeleryTaskClass)
def socket_request(target: str, port: int, module: str) -> Optional[int]:
    with SocketManager(target=target, port=port) as sm:
        response = sm.run()
        # the error indicator is 0 if the operation succeeded
        if response == 0:
            pass_result_event.delay(
                event=ResultEvent(
                    id=uuid.uuid4(),
                    source_module=module,
                    target=target,
                    result=str(port),
                )
            )
            return port
        else:
            return None


@app.task(base=BaseCeleryTaskClass)
def pass_result_event(event: ResultEvent) -> None:
    task_name = pass_result_event.__name__
    logger.debug(f"START::{task_name}::{event}")
    event_dict = result_event_encoder(event)
    rc.publish(
        channel=PUBSUB_RESULTS_CHANNEL_NAME,
        message=event_dict,
    )
    logger.debug(f"PUBLISHED::{event.id}")


@app.task(base=BaseCeleryTaskClass)
def start_module_event(event: StartModuleEvent) -> None:
    task_name = start_module_event.__name__
    logger.debug(f"START::{task_name}::{event}")
    event_dict = start_module_event_encoder(event)
    rc.publish(
        channel=STEERING_MODULE,
        message=event_dict,
    )
    logger.debug(f"PUBLISHED::{event.id}")


@app.task(base=BaseCeleryTaskClass)
def live_results_listener_task():
    task_name = live_results_listener_task.__name__
    task_id = uuid.uuid4()
    logger.debug(f"START::{task_id}::{task_name}")
    pubsub.subscribe(PUBSUB_RESULTS_CHANNEL_NAME)

    for result in pubsub.listen():
        if result["type"] == "message":
            save_message_time()
            event = result_event_data_load(result["data"].decode())
            logger.debug(f"RECEIVED::{task_id}::{event.id}")
            # TODO add check of user input "show result after every finding"
            #  setting here to optionally not publish results
            log_results.delay(event=event)
            dispatcher = Dispatcher(event=event)
            dispatcher.run()


@app.task(base=BaseCeleryTaskClass)
def event_listener_task(module: str) -> None:
    task_name = event_listener_task.__name__
    task_id = uuid.uuid4()
    logger.debug(f"START::{task_id}::{task_name}::{module}")
    pubsub.subscribe(module)

    for result in pubsub.listen():
        if result["type"] == "message":
            save_message_time()
            event = start_module_event_data_load(result["data"].decode())
            logger.debug(f"RECEIVED::{task_id}::{event.id}")
            dispatcher = Dispatcher(event=event)
            dispatcher.run()


def background_jobs_still_running() -> bool:
    tasks_running = True
    messages_still_passed = True

    # wait for messages to be passed
    # (when single module is run this part can be reached before any message is passed)
    time.sleep(3)

    while any({messages_still_passed, tasks_running}):
        messages_still_passed = pubsub_still_active()
        tasks_running = check_tasks_running()

    return False


def pubsub_still_active() -> bool:
    last_message_time = float(
        pull_single_value_from_db(key=PUBSUB_LAST_MESSAGE_TIME_KEY)
    )

    if (last_message_time + SECONDS_TO_WAIT_FOR_MESSAGES_BEFORE_CLOSING) < time.time():
        logger.debug(
            f"CLOSING::No messages received in last {SECONDS_TO_WAIT_FOR_MESSAGES_BEFORE_CLOSING} seconds"
        )
        return False

    time.sleep(10)
    return True


def check_tasks_running() -> bool:
    # TODO: maybe this can be done better ?
    active_workers = [worker for worker in app.control.inspect().reserved().values()]
    reserved_tasks = [task for worker_data in active_workers for task in worker_data]
    logger.debug(f"FOUND::Reserved_tasks::{len(reserved_tasks)} {reserved_tasks}")

    if len(reserved_tasks) == 0:
        active_workers = [task for task in app.control.inspect().active().values()]
        active_tasks = [task for worker_data in active_workers for task in worker_data]
        logger.debug(f"FOUND::Active_tasks::{len(active_tasks)} {active_tasks}")

        listener_tasks_running = 0
        for task in active_tasks:
            if "listener_task" in task["name"]:
                listener_tasks_running += 1

        if len(active_tasks) == listener_tasks_running:
            logger.debug("CLOSING::Only listener tasks left")
            return False

    time.sleep(10)
    return True


def start_event_listeners(output_after_every_finding: bool) -> None:
    """
    Starts Celery tasks that listen for events from other modules.

    Currently, using only 'steering_module' as main listener and 'live_results_listener_task'
    as listener for results.
    """
    modules_to_run = [STEERING_MODULE]

    tasks = (
        event_listener_task.s(
            module=module,
        )
        for module in modules_to_run
    )
    if output_after_every_finding:
        live_results_listener_task.delay()

    celery.group(tasks).apply_async()
    # wait for event listeners to start before sending messages
    time.sleep(1)


def stop_listener_tasks() -> None:
    """
    This function clears all active tasks from the Celery queue,
    between application runs without a need to stop the workers.
    """
    logger.debug("START::Looking for active tasks")
    active_tasks = app.control.inspect().active()
    logger.debug(f"FOUND::{len(active_tasks)} active tasks")

    for active_worker in active_tasks:
        for task in active_tasks[active_worker]:
            if "listener_task" in task["name"]:
                app.control.revoke(task["id"], terminate=True)
