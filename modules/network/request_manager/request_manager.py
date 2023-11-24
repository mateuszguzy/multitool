from typing import Union
from urllib.parse import urlunparse, ParseResult

import requests
from requests.exceptions import ConnectionError, MissingSchema

from utils.abstracts_classes import AbstractContextManager
from utils.custom_dataclasses import SessionRequestResponseObject
from utils.custom_exceptions import (
    CustomConnectionError,
    InvalidUrl,
    UnhandledException,
    UnhandledRequestMethod,
)


class RequestManager(AbstractContextManager):
    def __init__(
        self,
        method: str,
        scheme: str = "",
        netloc: str = "",
        path: str = "",
        params: str = "",
        query: str = "",
        fragment: str = "",
        allow_redirects: bool = True,
    ) -> None:
        super().__init__()
        self.method = method
        self.url = urlunparse(
            ParseResult(
                scheme=scheme,
                netloc=netloc,
                path=path,
                params=params,
                query=query,
                fragment=fragment,
            )
        )
        self.session = requests.Session()
        self.allow_redirects = allow_redirects

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.session is not None:
            self.session.close()

    def run(self) -> Union[SessionRequestResponseObject, Exception]:
        request_mapping = {
            "get": self._get_request,
        }
        if self.method.lower() in request_mapping:
            try:
                return request_mapping[self.method.lower()]()

            except ConnectionError:
                raise CustomConnectionError(f"Connection error on URL: {self.url}")

            except MissingSchema:
                raise InvalidUrl("Invalid URL")

            except Exception as e:
                raise UnhandledException(f"Unhandled request manager error: {e}")
        else:
            raise UnhandledRequestMethod(
                f"Unhandled request method used: {self.method}"
            )

    def _get_request(self) -> SessionRequestResponseObject:
        """
        Make request to the given URL.
        """
        response = self.session.get(url=self.url, allow_redirects=self.allow_redirects)

        return SessionRequestResponseObject(
            url=response.url,
            status_code=response.status_code,
            ok=response.ok,
            text=response.text,
        )
