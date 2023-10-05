from typing import Union

import requests
from requests.exceptions import ConnectionError, MissingSchema

from utils.abstracts_classes import AbstractContextManager
from utils.custom_exceptions import (
    CustomConnectionError,
    InvalidUrl,
    UnhandledException,
    UnhandledRequestMethod,
)


class RequestManager(AbstractContextManager):
    def __init__(self, method: str, url: str) -> None:
        super().__init__()
        self.method = method
        self.url = url
        self.session = requests.Session()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.session is not None:
            self.session.close()

    def run(self):
        return self._make_request()

    def _make_request(self) -> Union[requests.Response, Exception]:
        """
        Make request to the given URL.
        """
        if self.method.lower() == "get":
            try:
                return self.session.get(url=self.url, allow_redirects=False)

            except ConnectionError:
                raise CustomConnectionError("Connection error")

            except MissingSchema:
                raise InvalidUrl("Invalid URL")

            except Exception:
                raise UnhandledException("Unhandled request manager error")
        else:
            raise UnhandledRequestMethod(
                f"Unhandled request method used: {self.method}"
            )
