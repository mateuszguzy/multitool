from .celery import app
from ..helper.logger import Logger
from ..network.request_manager.request_manager import RequestManager


@app.task
def log_results(result: str, module: str):
    logger = Logger(module)
    logger.log_info(result)
    logger.exit()


@app.task
def web_request(request_method: str, url: str, word: str, module: str):
    with RequestManager(method=request_method, url=url) as rm:
        response = rm.run()

        if response.status_code not in [404]:
            log_results.delay(result=word, module=module)
            return word
        else:
            return None
