import celery  # type: ignore

from config.settings import IMPORTANT_PORTS
from modules.task_queue.tasks import socket_request
from utils.abstracts_classes import AbstractModule
from utils.custom_dataclasses import PortScanInput
from utils.utils import (
    convert_list_or_set_to_dict,
    store_module_results_in_database,
    url_formatter,
)


class PortScan(AbstractModule):
    target: str = str()
    port_scan_type = str()
    ports: set = set()

    def __init__(self, target: str, port_scan_input: PortScanInput) -> None:
        super().__init__()
        self.target = target
        self.formatted_target = url_formatter(input_target=target, module="port_scan")
        self.port_scan_type = getattr(port_scan_input, "port_scan_type")
        self.ports = getattr(port_scan_input, "ports")

    def run(self):
        self._determine_use_type()
        self._run_with_celery()

    def _determine_use_type(self):
        # 'port_scan_type' is optional to None in case it's not used e.g. while 'recon' phase is run
        # Below check is to prevent 'None' while PortScan is executed
        if self.port_scan_type is None:
            raise ValueError("port_scan_type cannot be None")

        elif self.port_scan_type == "all":
            self.ports = set(range(1, 65536))

        elif self.port_scan_type == "important":
            self.ports = IMPORTANT_PORTS

        elif self.port_scan_type == "top_1000":
            self.ports = set(range(1, 1001))

    def _run_with_celery(self):
        """
        Runs celery tasks in parallel.
        """
        tasks = [
            socket_request.s(target=self.formatted_target, port=port, module=__name__)
            for port in self.ports
        ]

        results = convert_list_or_set_to_dict(
            list_of_items=celery.group(tasks).apply_async().join()
        )
        store_module_results_in_database(
            target=self.target, results=results, phase="scan", module="port_scan"
        )
