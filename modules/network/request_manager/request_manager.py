import requests
from requests.exceptions import ConnectionError

from modules.helper.logger import Logger
from utils.abstracts_classes import AbstractContextManager

logger = Logger(__name__)


class RequestManager(AbstractContextManager):
    method: str = str()
    url: str = str()
    session: requests.Session = requests.Session()

    # 'pydantic' required class - provide additional config to allow 'requests.Session' type check
    class Config:
        arbitrary_types_allowed = True

    def __init__(self, method: str, url: str) -> None:
        super().__init__()
        self.method = method
        self.url = url
        self.session = requests.Session()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.session.close()

    def run(self):
        return self._make_request(method=self.method, url=self.url)

    def _make_request(self, method: str, url: str):
        if method.lower() == "get":
            try:
                return self.session.get(url=url, allow_redirects=False)
            except ConnectionError as e:
                logger.run()
                logger.log_error(f"Connection Error: {e}")
                # TODO: change app behaviour after ConnectionError
                exit()
