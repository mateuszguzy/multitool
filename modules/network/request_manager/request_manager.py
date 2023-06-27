from typing import ContextManager

import requests
from requests.exceptions import ConnectionError

from modules.helper.logger import Logger
from utils.abstracts_classes import AbstractModule



class RequestManager(ContextManager, AbstractModule):
    method: str = str()
    url: str = str()
    session: requests.Session = object()

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

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def run(self):
        return self._make_request(method=self.method, url=self.url)

    def _make_request(self, method: str, url: str):
        if method.lower() == "get":
            try:
                return self.session.get(url=url, allow_redirects=False)
            except ConnectionError as e:
                logger = Logger(__name__)
                logger.run(mode="info", message=f"Connection Error: {e}")
                logger.exit()
                # TODO: change app behaviour after ConnectionError
                exit()
