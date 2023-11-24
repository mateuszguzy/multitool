import pytest
import requests
from requests.exceptions import MissingSchema, ConnectionError

from modules.network.request_manager.request_manager import RequestManager
from tests.conftest import REQUEST_MANAGER_MODULE_PATH
from utils.custom_dataclasses import SessionRequestResponseObject
from utils.custom_exceptions import (
    UnhandledRequestMethod,
    InvalidUrl,
    CustomConnectionError,
    UnhandledException,
)


class TestRequestManager:
    test_target = "example.com"
    expected_target = "http://example.com"
    module_path = REQUEST_MANAGER_MODULE_PATH
    request_response_output = SessionRequestResponseObject(
        status_code=200,
        url="http://example.com",
        ok=True,
        text=None,
    )

    @pytest.mark.parametrize(
        "method, expected_output",
        [
            ("get", request_response_output),
        ],
    )
    def test_valid_methods(self, mocker, method, expected_output):
        mocker.patch.object(requests.Session, method)
        mocker.patch(
            f"{self.module_path}.RequestManager._get_request",
            return_value=expected_output,
        )
        request_manager = RequestManager(
            method=method, scheme="http", netloc=self.test_target
        )
        response = request_manager.run()

        assert response == expected_output
        assert request_manager.url == self.expected_target
        assert request_manager.method == method

    @pytest.mark.parametrize(
        "test_target, method, expected_output",
        [
            (test_target, "post", UnhandledRequestMethod),
            (test_target, "delete", UnhandledRequestMethod),
            (test_target, "put", UnhandledRequestMethod),
        ],
    )
    def test_invalid_methods(
        self, mocker, test_target, method, expected_output, request_manager_fixture
    ):
        mocker.patch.object(requests.Session, method, return_value=InvalidUrl)
        request_manager_fixture.method = method
        request_manager_fixture.url = self.expected_target

        with pytest.raises(expected_output):
            request_manager_fixture.run()

    @pytest.mark.parametrize(
        "exception, expected_output",
        [
            (ConnectionError, CustomConnectionError),
            (MissingSchema, InvalidUrl),
            (Exception, UnhandledException),
        ],
    )
    def test_exceptions(
        self, mocker, exception, expected_output, request_manager_fixture
    ):
        mocker.patch(
            f"{self.module_path}.RequestManager._get_request", side_effect=exception
        )

        with pytest.raises(expected_output):
            request_manager_fixture.run()
