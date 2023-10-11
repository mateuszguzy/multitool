import pytest
import requests

from modules.network.request_manager.request_manager import RequestManager
from utils.custom_exceptions import UnhandledRequestMethod, InvalidUrl


class TestRequestManager:
    test_target = "http://example.com"

    @pytest.mark.parametrize(
        "method, expected_output",
        [
            ("get", requests.Response()),
        ],
    )
    def test_valid_methods(self, mocker, method, expected_output):
        mocker.patch.object(requests.Session, method, return_value=expected_output)
        request_manager = RequestManager(method=method, url=self.test_target)
        response = request_manager._make_request()

        assert isinstance(response, requests.Response)
        assert request_manager.url == self.test_target
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
        request_manager = RequestManager(method=method, url=test_target)

        with pytest.raises(expected_output):
            request_manager._make_request()

    # TODO: add tests for exceptions
