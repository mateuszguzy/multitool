from typing import Union

import requests
from requests.exceptions import ConnectionError, MissingSchema

from config.settings import request_manager_logger
from utils.abstracts_classes import AbstractContextManager
from utils.custom_exceptions import (
    CustomConnectionError,
    InvalidUrl,
    UnhandledException,
    UnhandledRequestMethod,
)
from utils.utils import (
    format_exception_with_traceback_for_logging,
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

            except ConnectionError as exc:
                request_manager_logger.exception(
                    format_exception_with_traceback_for_logging(exc)
                )
                raise CustomConnectionError(f"Connection error: {exc}")

            except MissingSchema as exc:
                request_manager_logger.exception(
                    format_exception_with_traceback_for_logging(exc)
                )
                raise InvalidUrl(f"Invalid URL: {self.url}")

            except Exception as exc:
                request_manager_logger.exception(
                    format_exception_with_traceback_for_logging(exc)
                )
                raise UnhandledException(f"Unhandled request manager error: {exc}")
        else:
            raise UnhandledRequestMethod(
                f"Unhandled request method used: {self.method}"
            )
