from unittest.mock import patch


def test_responses(request_manager):
    """
    Test Requests Manager responses.
    """
    rm = request_manager
    mocked_output = 200

    with patch("modules.network.request_manager.request_manager.requests.Session.get") as mock_get:
        mock_get.return_value = mocked_output
        output = rm.run()

        assert rm.url == "https://www.example.com"

        if rm.method.lower() in ["get"]:
            assert output == mocked_output

        # currently PATCH method not implemented
        elif rm.method.lower() in ["post", "delete"]:
            assert output != mocked_output
