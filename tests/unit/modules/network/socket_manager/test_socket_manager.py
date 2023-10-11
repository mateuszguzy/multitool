import socket

import pytest

from modules.network.socket_manager.socket_manager import SocketManager
from tests.conftest import TEST_PORT_SCAN_TARGET
from utils.custom_exceptions import InvalidHostname, ConnectionTimedOut


class TestSocketManager:
    test_target = TEST_PORT_SCAN_TARGET
    test_port = 80

    def test_create_socket_manager_object(self):
        socket_manager = SocketManager(self.test_target, self.test_port)

        assert isinstance(socket_manager, SocketManager)
        assert socket_manager.target == self.test_target
        assert socket_manager.port == self.test_port

    def test_enter_and_exit_context_manager(self):
        with SocketManager(self.test_target, self.test_port) as socket_manager:
            assert isinstance(socket_manager, SocketManager)
        assert socket_manager.socket._closed

    def test_successful_connection(self, mocker, test_socket_manager):
        mocker.patch.object(socket.socket, "connect_ex", return_value=0)
        result = test_socket_manager.run()

        assert result == 0

    def test_raises_invalid_hostname_when_hostname_cannot_be_resolved(
        self, mocker, test_socket_manager
    ):
        mocker.patch.object(socket.socket, "connect_ex", side_effect=socket.gaierror)

        with pytest.raises(InvalidHostname):
            test_socket_manager.run()

    def test_raises_invalid_hostname_when_connection_timed_out(
        self, mocker, test_socket_manager
    ):
        mocker.patch.object(socket.socket, "connect_ex", side_effect=socket.timeout)

        with pytest.raises(ConnectionTimedOut):
            test_socket_manager.run()
