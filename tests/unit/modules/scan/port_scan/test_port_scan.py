from unittest import mock

import celery  # type: ignore

from tests.conftest import TEST_PORTS, TEST_PORT_SCAN_TARGET, TEST_TARGET


class TestPortScan:
    test_socket_request_target = TEST_PORT_SCAN_TARGET
    test_target = TEST_TARGET
    test_ports = TEST_PORTS
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

        test_port_scan.run()

        assert mock_socket_request_task.s.call_count == len(self.test_ports)
        assert mock_socket_request_task.s.call_args_list == [
            mock.call(target=self.test_socket_request_target, port=port, module=self.module_name)
            for port in self.test_ports
        ]
