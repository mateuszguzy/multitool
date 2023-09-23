from typing import Optional
from urllib.parse import urljoin

from config.settings import directory_bruteforce_logger, steering_module_logger
from modules.task_queue.celery import app
from modules.network.request_manager.request_manager import RequestManager


# Constants for module names
STEERING_MODULE = "__main__"
DIRECTORY_BRUTEFORCE_MODULE = "modules.recon.directory_bruteforce.directory_bruteforce"

# Dictionary mapping module names to loggers
loggers = {
    STEERING_MODULE: steering_module_logger,
    DIRECTORY_BRUTEFORCE_MODULE: directory_bruteforce_logger
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
        loggers[STEERING_MODULE].error(f"Wrong type of module used: {module}")


@app.task
def web_request(request_method: str, url: str, word: str, module: str) -> Optional[str]:
    with RequestManager(method=request_method, url=urljoin(url, word)) as rm:
        response = rm.run()

        if response.ok:
            log_results.apply_async(args=[word, module], kwargs={'target': url})
            return word
        else:
            return  # type: ignore
