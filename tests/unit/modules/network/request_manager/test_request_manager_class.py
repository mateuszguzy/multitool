import pytest
import requests

from modules.network.request_manager.request_manager import RequestManager
from utils.custom_dataclasses import SessionRequestResponseObject
from utils.custom_exceptions import UnhandledRequestMethod, InvalidUrl


class TestRequestManager:
    test_target = "example.com"
    expected_target = "http://example.com"
    request_manager_path = "modules.network.request_manager.request_manager"
    request_response_output = SessionRequestResponseObject(
        status_code=200,
        url="http://example.com",
        ok=True,
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
            f"{self.request_manager_path}.RequestManager._get_request",
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
    def test_invalid_methods(self, mocker, test_target, method, expected_output):
        mocker.patch.object(requests.Session, method, return_value=InvalidUrl)
        request_manager = RequestManager(method=method, netloc="dvwa")

        with pytest.raises(expected_output):
            request_manager.run()

    # TODO: add tests for exceptions
