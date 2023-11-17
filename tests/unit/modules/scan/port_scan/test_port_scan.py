from unittest import mock

import celery  # type: ignore
import pytest

from config.settings import IMPORTANT_PORTS
from modules.scan.port_scan.port_scan import PortScan
from tests.conftest import (
    TEST_PORTS,
    TEST_PORT_SCAN_TARGET,
    TEST_TARGET,
    PORT_SCAN_MODULE_PATH,
)
from utils.custom_dataclasses import PortScanInput


class TestPortScan:
    test_socket_request_target = TEST_PORT_SCAN_TARGET
    test_target = TEST_TARGET
    test_ports = TEST_PORTS
    important_ports = IMPORTANT_PORTS
    module_path = PORT_SCAN_MODULE_PATH

    def test_port_scan_object_created_successfully(self, port_scan_fixture):
        """
        Test PortScan object is created successfully
        """
        assert port_scan_fixture.target == self.test_target
        assert port_scan_fixture.formatted_target == self.test_socket_request_target
        assert port_scan_fixture.ports == self.test_ports

    def test_all_ports_open_and_scanned_successfully(
        self,
        mocker,
        port_scan_fixture,
        mock_socket_request_task,
        mock_celery_group,
        mock_port_scan_convert_list_or_set_to_dict,
        mock_port_scan_store_module_results_in_database,
    ):
        """
        Test all calls for all ports are made
        """
        mocker.patch(f"{self.module_path}.socket_request", mock_socket_request_task)
        mocker.patch.object(celery, "group", mock_celery_group)

        port_scan_fixture._run_with_celery()

        assert mock_socket_request_task.s.call_count == len(self.test_ports)
        assert mock_socket_request_task.s.call_args_list == [
            mock.call(
                target=self.test_socket_request_target,
                port=port,
                module=self.module_path,
            )
            for port in self.test_ports
        ]

    @pytest.mark.parametrize(
        "port_scan_type, expected_ports",
        [
            ("all", set(range(1, 65536))),
            ("important", IMPORTANT_PORTS),
            ("top_1000", set(range(1, 1001))),
            ("custom", set()),
        ],
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
        ],
    )
    def test_port_scan_type_none_fail(self, invalid_port_scan_type):
        port_scan_input = PortScanInput(
            port_scan_type=invalid_port_scan_type, ports=set()
        )
        port_scan = PortScan(target=self.test_target, port_scan_input=port_scan_input)

        with pytest.raises(ValueError):
            port_scan._determine_use_type()
