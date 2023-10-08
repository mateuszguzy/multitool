from typing import Optional
from urllib.parse import urljoin

from config.settings import directory_bruteforce_logger, steering_module_logger, port_scan_logger
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
def web_request(request_method: str, url: str, word: str, module: str) -> Optional[str]:
    with RequestManager(method=request_method, url=urljoin(url, word)) as rm:
        response = rm.run()

        if response.ok:
            log_results.delay(result=word, module=module, target=url)
            return word
        else:
            return None


@app.task
def socket_request(target: str, port: int, module: str) -> Optional[int]:
    with SocketManager(target=target, port=port) as sm:
        response = sm.run()
        # the error indicator is 0 if the operation succeeded
        if response == 0:
            log_results.delay(result=port, module=module, target=target)
            return port
        else:
            return None
