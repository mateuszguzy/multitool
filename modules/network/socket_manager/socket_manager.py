import socket

from utils.abstracts_classes import AbstractContextManager
from utils.custom_exceptions import UnhandledException


class SocketManager(AbstractContextManager):
    target: str = str()
    timeout: int = 1  # number of seconds after which connection will time out
    socket: socket.socket
    port: int = int()

    def __init__(self, target: str, port: int) -> None:
        super().__init__()
        self.target = target
        self.port = port
        self.socket = socket.socket()
        self.socket.settimeout(self.timeout)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.socket.close()

    def run(self):
        return self._make_request(target=self.target, port=self.port)

    def _make_request(self, target: str, port: int):
        try:
            return self.socket.connect_ex((target, port))

        except socket.gaierror:
            raise UnhandledException("Hostname could not be resolved")

        except Exception:
            raise UnhandledException("Unhandled exception")
