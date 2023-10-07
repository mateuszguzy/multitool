import pytest

from utils.utils import (
    convert_list_or_set_to_dict, url_formatter,
)


class TestUrlFormatter:
    directory_bruteforce = "directory_bruteforce"
    expected_url_1 = "http://example.com/"

    @pytest.mark.parametrize(
        "url, expected_output",
        [
            ("example", "http://example/"),
            ("example.com", expected_url_1),
            ("http://example.com", expected_url_1),
        ],
    )
    def test_with_url_without_protocol(self, url, expected_output):
        assert url_formatter(input_target=url, module=self.directory_bruteforce) == expected_output


class TestConvertListOrSetToDict:
    def test_with_list_of_integers(self):
        input_list = [1, 2, 3, 4, 5]
        expected_output = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5}
        assert convert_list_or_set_to_dict(input_list) == expected_output

    def test_with_empty_list(self):
        input_list = []
        expected_output = {}
        assert convert_list_or_set_to_dict(input_list) == expected_output

    def test_with_list_containing_duplicates(self):
        input_list = [1, 2, 3, 2, 4, 5, 4]
        expected_output = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5}
        assert convert_list_or_set_to_dict(input_list) == expected_output

    def test_with_list_of_none_values(self):
        input_list = [None, None, None]
        expected_output = {}
        assert convert_list_or_set_to_dict(input_list) == expected_output
