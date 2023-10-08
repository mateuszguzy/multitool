from unittest import mock

import celery  # type: ignore
import pytest

from config.settings import IMPORTANT_PORTS
from modules.scan.port_scan.port_scan import PortScan
from tests.conftest import TEST_PORTS, TEST_PORT_SCAN_TARGET, TEST_TARGET
from utils.custom_dataclasses import PortScanInput


class TestPortScan:
    test_socket_request_target = TEST_PORT_SCAN_TARGET
    test_target = TEST_TARGET
    test_ports = TEST_PORTS
    important_ports = IMPORTANT_PORTS
    module_name = "modules.scan.port_scan.port_scan"

    def test_port_scan_object_created_successfully(self, test_port_scan):
        """
        Test PortScan object is created successfully
        """
        assert test_port_scan.target == self.test_target
        assert test_port_scan.formatted_target == self.test_socket_request_target
        assert test_port_scan.ports == self.test_ports

    def test_all_ports_open_and_scanned_successfully(
        self, mocker, test_port_scan, mock_socket_request_task, mock_celery_group
    ):
        """
        Test all calls for all ports are made
        """
        mocker.patch(f"{self.module_name}.socket_request", mock_socket_request_task)
        mocker.patch.object(celery, "group", mock_celery_group)

        mocker.patch(f"{self.module_name}.convert_list_or_set_to_dict")
        mocker.patch(f"{self.module_name}.store_module_results_in_database")

        test_port_scan._run_with_celery()

        assert mock_socket_request_task.s.call_count == len(self.test_ports)
        assert mock_socket_request_task.s.call_args_list == [
            mock.call(target=self.test_socket_request_target, port=port, module=self.module_name)
            for port in self.test_ports
        ]

    @pytest.mark.parametrize(
        "port_scan_type, expected_ports",
        [
            ("all", set(range(1, 65536))),
            ("important", IMPORTANT_PORTS),
            ("top_1000", set(range(1, 1001))),
        ]
    )
    def test_port_scan_types(self, port_scan_type, expected_ports):
        port_scan_input = PortScanInput(port_scan_type=port_scan_type, ports=set())
        port_scan = PortScan(target=self.test_target, port_scan_input=port_scan_input)

        port_scan._determine_use_type()

        assert port_scan.ports == expected_ports

    @pytest.mark.parametrize(
        "invalid_port_scan_type",
        [
            None,
            "invalid",
            123,
        ]
    )
    def test_port_scan_type_none_fail(self, invalid_port_scan_type):
        port_scan_input = PortScanInput(port_scan_type=invalid_port_scan_type, ports=set())
        port_scan = PortScan(target=self.test_target, port_scan_input=port_scan_input)

        with pytest.raises(ValueError):
            port_scan._determine_use_type()


