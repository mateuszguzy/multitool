from unittest.mock import patch

import pytest

from modules.network.request_manager.request_manager import RequestManager
from utils.custom_exceptions import UnhandledRequestMethod, InvalidUrl, CustomConnectionError


class TestRequestManager:
    """
    Test Requests Manager responses.
    """
    test_url = "https://www.example.com"
    get_method = "GET"

    def test_get_request(self, request_manager_get_request):
        """
        Test simple GET request.
        """
        rm = request_manager_get_request
        mocked_output = 200

        with patch(
            "modules.network.request_manager.request_manager.requests.Session.get"
        ) as mock_get:
            mock_get.return_value = mocked_output
            output = rm.run()

            assert rm.url == self.test_url
            assert output == mocked_output

    def test_post_request(self, request_manager_post_request):
        """
        Test simple POST request.
        """
        rm = request_manager_post_request

        with pytest.raises(UnhandledRequestMethod):
            rm.run()

    def test_delete_request(self, request_manager_delete_request):
        """
        Test simple DELETE request.
        """
        rm = request_manager_delete_request

        with pytest.raises(UnhandledRequestMethod):
            rm.run()

    def test_request_manager_object_created_successfully(self):
        """
        Test if RequestManager object is created successfully.
        """
        request_manager = RequestManager(self.get_method, self.test_url)

        assert request_manager.method == self.get_method
        assert request_manager.url == self.test_url

    def test_request_manager_object_created_with_invalid_method_parameter(self):
        """
        Test if RequestManager object is created successfully.
        """
        invalid_method = "INVALID"
        request_manager = RequestManager(invalid_method, self.test_url)

        with pytest.raises(UnhandledRequestMethod):
            request_manager.run()

    def test_request_manager_object_created_with_invalid_url_parameter(self):
        """
        Test if RequestManager object is created successfully.
        """
        invalid_url = "invalid_url"
        request_manager = RequestManager(self.get_method, invalid_url)

        with pytest.raises(InvalidUrl):
            request_manager.run()
