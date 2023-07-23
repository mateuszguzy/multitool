from unittest.mock import patch

import pytest

from utils.custom_exceptions import UnhandledRequestMethod


class TestRequestManager:
    """
    Test Requests Manager responses.
    """

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

            assert rm.url == "https://www.example.com"
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
