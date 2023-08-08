import pytest

from utils.utils import (
    clean_and_validate_input_targets,
    check_for_protocol_prefix_in_multiple_targets,
    check_for_trailing_slash_in_multiple_targets,
    target_is_url,
)

URLS_WITHOUT_TRAILING_SLASH = {
    "https://www.example.com:8080",
    "https://www.example.com",
    "http://www.example.com:8080",
    "http://www.example.com",
    "http://example.com",
    "www.example.com:8080",
    "www.example.com",
}

URLS_WITH_TRAILING_SLASH = {
    "https://www.example.com:8080/",
    "https://www.example.com/",
    "http://www.example.com:8080/",
    "http://www.example.com/",
    "http://example.com/",
    "www.example.com:8080/",
    "www.example.com/",
}

URLS_WITHOUT_PROTOCOL = {
    "www.example.com:8080",
    "www.example.com",
    "www.example:8080",
    "example.com:8080",
    "example.com",
    "example:8080",
}

URLS_WITH_PROTOCOL = {
    "http://www.example.com:8080",
    "http://www.example.com",
    "http://www.example:8080",
    "http://example.com:8080",
    "http://example.com",
    "http://example:8080",
}

INVALID_URLS = {
    "www.example",
    "example",
    "example example",
}

URLS_TO_VALIDATE = (
    INVALID_URLS
    | URLS_WITHOUT_TRAILING_SLASH
    | URLS_WITHOUT_PROTOCOL
    | URLS_WITH_TRAILING_SLASH
    | URLS_WITH_PROTOCOL
)

VALIDATED_URLS = {
    "http://example.com/",
    "http://example.com:8080/",
    "http://example:8080/",
    "http://www.example.com/",
    "http://www.example.com:8080/",
    "http://www.example:8080/",
    "https://www.example.com/",
    "https://www.example.com:8080/",
    "www.example.com/",
    "www.example.com:8080/",
}


class TestUtils:
    @pytest.mark.usefixtures("mock_check_for_protocol_prefix_in_multiple_targets")
    @pytest.mark.usefixtures("mock_check_for_trailing_slash_in_multiple_targets")
    @pytest.mark.parametrize(
        "test_input, expect",
        [(URLS_TO_VALIDATE, VALIDATED_URLS)],
    )
    def test_clean_and_validate_input_targets(self, test_input, expect):
        """
        Test if URL checking Regexes are working correctly.
        """
        test_input = ", ".join(test_input)
        result = clean_and_validate_input_targets(test_input)

        assert len(result) == len(expect)

    @pytest.mark.parametrize(
        "test_input, expect",
        [
            (URLS_WITHOUT_PROTOCOL, URLS_WITH_PROTOCOL),
        ],
    )
    def test_check_for_protocol_prefix_in_multiple_targets_success(
        self, test_input, expect
    ):
        """
        Test function adding protocol to URLs where it's missing.
        """
        results = check_for_protocol_prefix_in_multiple_targets(targets=test_input)

        assert len(results) == len(expect)
        assert results == expect

    @pytest.mark.parametrize(
        "test_input, expect",
        [
            (URLS_WITHOUT_TRAILING_SLASH, URLS_WITH_TRAILING_SLASH),
        ],
    )
    def test_check_for_trailing_slash_in_multiple_targets(self, test_input, expect):
        """
        Test function adding trailing slash to URLs where it's missing.
        """
        results = check_for_trailing_slash_in_multiple_targets(targets=test_input)

        assert len(results) == len(expect)
        assert results == expect

    @pytest.mark.parametrize(
        "test_input, expect",
        [
            (URLS_WITHOUT_TRAILING_SLASH, True),
            (URLS_WITHOUT_PROTOCOL, True),
            (INVALID_URLS, False),
        ],
    )
    def test_target_is_url(self, test_input, expect):
        """
        Test function verifying if given target can be treated as a URL.
        """
        for url in test_input:
            result = target_is_url(target=url)

            assert result == expect
