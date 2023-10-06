import celery  # type: ignore

from modules.task_queue.tasks import socket_request
from utils.abstracts_classes import AbstractModule
from utils.custom_dataclasses import PortScanInput
from utils.utils import convert_list_or_set_to_dict, store_module_results_in_database


class PortScan(AbstractModule):
    target: str = str()
    ports: set = set()

    def __init__(self, target: str, port_scan_input: PortScanInput) -> None:
        super().__init__()
        self.target = target
        self.ports = getattr(port_scan_input, "ports")

    def run(self):
        self._run_with_celery()

    def _run_with_celery(self):
        """
        Runs celery tasks in parallel.
        """
        tasks = [
            socket_request.s(target=self.target, port=port, module=__name__)
            for port in self.ports
        ]

        results = convert_list_or_set_to_dict(
            list_of_items=celery.group(tasks).apply_async().join()
        )
        store_module_results_in_database(
            target=self.target, results=results, phase="scan", module="port_scan"
        )
