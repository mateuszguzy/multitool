from typing import Optional, Set

from config.settings import SCAN_PHASE_MODULES
from modules.scan.port_scan.port_scan import PortScan
from utils.abstracts_classes import AbstractModule
from utils.custom_dataclasses import ScanInput, PortScanInput


class Scan(AbstractModule):
    def __init__(self, scan_input: ScanInput, target: str, single_module: Optional[str]):
        super().__init__()
        self.port_scan_input: PortScanInput = getattr(scan_input, "port_scan")
        self.target = target
        self.single_module = single_module

    def run(self) -> None:
        if not self.single_module:
            for module in SCAN_PHASE_MODULES:
                getattr(self, f"_run_{module}")()
        else:
            if self.single_module not in SCAN_PHASE_MODULES:
                raise ValueError(
                    f"Invalid module name: {self.single_module}. "
                    f"Available modules: {SCAN_PHASE_MODULES}"
                )
            getattr(self, f"_run_{self.single_module}")()

    def _run_port_scan(self) -> None:
        port_scan = PortScan(
            port_scan_input=self.port_scan_input,
            target=self.target,
        )
        port_scan.run()
