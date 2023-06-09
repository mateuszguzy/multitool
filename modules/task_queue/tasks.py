from .celery import app
from ..network.request_manager.request_manager import RequestManager


@app.task
def web_request(request_method: str, url: str, word: str):
    with RequestManager(method=request_method, url=url) as rm:
        response = rm.run()

        if response.status_code not in [404]:
            return word
        else:
            return None
