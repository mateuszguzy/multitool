import pytest

from utils.utils import (
    convert_list_or_set_to_dict, url_formatter, clean_and_validate_input_ports,
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


class TestCleanAndValidateInputPorts:
    """
    Test clean_and_validate_input_ports function.
    """
    @pytest.mark.parametrize(
        "input_ports, expected_output",
        [
            ("8080", {8080}),
            ("8080, 8081, 8082", {8080, 8081, 8082}),
            ("1, 65535", {1, 65535}),
            ("", set()),
            ("   ", set()),
            ("8080, abc, 123", {8080, 123}),
        ],
    )
    def test_port_number_input_validation(self, input_ports, expected_output):
        result = clean_and_validate_input_ports(input_ports)
        assert result == expected_output


class TestConvertListOrSetToDict:
    @pytest.mark.parametrize(
        "input_list, expected_output",
        [
            ([1, 2, 3, 4, 5], {0: 1, 1: 2, 2: 3, 3: 4, 4: 5}),
            ([], {}),
            ([1, 2, 3, 2, 4, 5, 4], {0: 1, 1: 2, 2: 3, 3: 4, 4: 5}),
            ([None, None, None], {}),
        ],
    )
    def test_with_list_of_integers(self, input_list, expected_output):
        assert convert_list_or_set_to_dict(input_list) == expected_output
