import pytest

from utils.utils import (
    convert_list_or_set_to_dict, url_formatter,
)


class TestUrlFormatter:
    directory_bruteforce = "directory_bruteforce"
    port_scan = "port_scan"
    expected_url_1 = "http://example.com/"
    expected_url_2 = "example.com"
    expected_url_3 = "www.example.com"

    @pytest.mark.parametrize(
        "url, expected_output",
        [
            ("example", "http://example/"),
            ("example.com", expected_url_1),
            ("http://example.com", expected_url_1),
        ],
    )
    def test_directory_bruteforce_url_formatting(self, url, expected_output):
        assert url_formatter(input_target=url, module=self.directory_bruteforce) == expected_output

    @pytest.mark.parametrize(
        "url, expected_output",
        [
            ("example", "example"),
            ("example.com", expected_url_2),
            ("http://example.com", expected_url_2),
            ("www.example.com", expected_url_3),
            ("http://www.example.com", expected_url_3),
        ],
    )
    def test_port_scan_url_formatting(self, url, expected_output):
        assert url_formatter(input_target=url, module=self.port_scan) == expected_output


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
