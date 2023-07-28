import pytest

from utils.utils import clean_and_validate_input_targets

VALID_URLS = [
    "https://www.example.com:8080",
    "https://www.example.com",
    "https://www.example:8080",
    "https://example.com:8080",
    "https://example.com",
    "https://example:8080",
    "http://www.example.com:8080",
    "http://www.example.com",
    "http://www.example:8080",
    "http://example.com:8080",
    "http://example.com",
    "http://example:8080",
    "www.example.com:8080",
    "www.example.com",
    "www.example:8080",
    "example.com:8080",
    "example.com",
    "example:8080",
]

INVALID_URLS = [
    "www.example",
    "example",
    "example example",
]


class TestCliInterface:
    """
    Test CLI Interface module.
    """

    @pytest.mark.parametrize(
        "test_input,expected", [(VALID_URLS, len(VALID_URLS)), (INVALID_URLS, 0)]
    )
    def test_valid_targets_validation(self, test_input, expected):
        """
        Test if URL checking Regexes are working correctly.
        """
        test_input = ", ".join(test_input)
        result = clean_and_validate_input_targets(test_input)

        assert len(result) == expected
