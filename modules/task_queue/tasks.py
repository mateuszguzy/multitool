from typing import Optional
from urllib.parse import urlparse

import redis

from config.settings import (
    directory_bruteforce_logger,
    steering_module_logger,
    port_scan_logger,
    REDIS_HOST,
    REDIS_PORT,
    REDIS_DB,
)
from modules.network.request_manager.request_manager import RequestManager
from modules.network.socket_manager.socket_manager import SocketManager
from modules.task_queue.celery import app

# Constants for module names
STEERING_MODULE = "__main__"
DIRECTORY_BRUTEFORCE_MODULE = "modules.recon.directory_bruteforce.directory_bruteforce"
PORT_SCAN_MODULE = "modules.scan.port_scan.port_scan"

# Dictionary mapping module names to loggers
loggers = {
    STEERING_MODULE: steering_module_logger,
    DIRECTORY_BRUTEFORCE_MODULE: directory_bruteforce_logger,
    PORT_SCAN_MODULE: port_scan_logger,
}
rc = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
pubsub = rc.pubsub()


@app.task
def log_results(result: str, module: str, target: str = "") -> None:
    """
    Logs the result using the appropriate logger based on the module name.
    If a target is provided, it is included in the log message.
    """
    if target:
        result = f"<{target}>: {result}"

    if module in loggers:
        loggers[module].info(result)
    else:
        loggers[STEERING_MODULE].error(f"No such logger: {module}")


@app.task
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
            pass_result_event.delay(result=url.path, module=module, target=target)
            return url.path
        else:
            return None


@app.task
def socket_request(target: str, port: int, module: str) -> Optional[int]:
    with SocketManager(target=target, port=port) as sm:
        response = sm.run()
        # the error indicator is 0 if the operation succeeded
        if response == 0:
            pass_result_event.delay(result=port, module=module, target=target)
            return port
        else:
            return None


@app.task()
def pass_result_event(result: str, module: str, target: str) -> None:
    rc.publish(
        channel="results",
        message=f"{result}::{module}::{target}",
    )


@app.task()
def results_listener_task():
    pubsub.subscribe("results")
    for result in pubsub.listen():
        if result["type"] == "message":
            r = result["data"].decode().split("::")
            log_results.delay(result=r[0], module=r[1], target=r[2])


def stop_listener_tasks():
    """
    This function clears all active tasks from the Celery queue,
    between application runs without stopping the workers.
    """
    active_tasks = app.control.inspect().active()

    for active_worker in active_tasks:
        for task in active_tasks[active_worker]:
            if "listener_task" in task["name"]:
                app.control.revoke(task["id"], terminate=True)
