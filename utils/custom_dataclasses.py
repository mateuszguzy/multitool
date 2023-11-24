from dataclasses import dataclass
from typing import Set, Optional
from uuid import UUID


@dataclass
class DirectoryBruteforceInput:
    list_size: Optional[str]
    recursive: Optional[bool]


@dataclass
class PortScanInput:
    port_scan_type: Optional[str]
    ports: Set[Optional[int]]


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
    output_after_every_finding: bool


@dataclass
class SessionRequestResponseObject:
    ok: bool
    status_code: int
    url: str
    text: Optional[str]


@dataclass
class Event:
    id: UUID
    source_module: str
    target: str


@dataclass
class StartModuleEvent(Event):
    destination_module: Optional[str]
    result: Optional[str]


@dataclass
class ResultEvent(Event):
    result: str
