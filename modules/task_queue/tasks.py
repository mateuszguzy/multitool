from config.settings import directory_bruteforce_logger, steering_module_logger
from modules.task_queue.celery import app
from modules.network.request_manager.request_manager import RequestManager


@app.task
def log_results(result: str, module: str, target: str = "") -> None:
    if target:
        result = f"<{target}>: {result}"

    if "__main__" in module:
        steering_module_logger.info(result)
    elif "directory_bruteforce" in module:
        directory_bruteforce_logger.info(result)


@app.task
def web_request(request_method: str, url: str, word: str, module: str) -> str or None:  # type: ignore
    with RequestManager(method=request_method, url=f"{url}{word}") as rm:
        response = rm.run()

        if response.status_code not in [404]:
            log_results.delay(result=word, module=module, target=url)
            return word
        else:
            return None
