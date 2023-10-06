from dataclasses import dataclass
from typing import Set, Optional


@dataclass
class DirectoryBruteforceInput:
    list_size: Optional[str]


@dataclass
class PortScanInput:
    ports: Set[int]


@dataclass
class ReconInput:
    directory_bruteforce: DirectoryBruteforceInput


@dataclass
class ScanInput:
    port_scan: PortScanInput


@dataclass
class UserInput:
    use_type: str
    phase: str
    module: Optional[str]
    targets: Set[str]
    recon: ReconInput
    scan: ScanInput
    output_after_every_phase: bool
    output_after_every_finding: bool
