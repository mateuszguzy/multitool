import requests
from requests import Response
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

    def _make_request(self, method: str, url: str) -> Response or Exception:  # type: ignore
        if method.lower() == "get":
            try:
                return self.session.get(url=url, allow_redirects=False)

            except ConnectionError as exc:
                request_manager_logger.exception(
                    format_exception_with_traceback_for_logging(exc)
                )
                raise CustomConnectionError(exc=str(exc))

            except MissingSchema as exc:
                request_manager_logger.exception(
                    format_exception_with_traceback_for_logging(exc)
                )
                raise InvalidUrl(exc=str(exc))

            except Exception as exc:
                request_manager_logger.exception(
                    format_exception_with_traceback_for_logging(exc)
                )
                raise UnhandledException()
        else:
            raise UnhandledRequestMethod(method=method)
