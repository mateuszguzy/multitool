from dataclasses import dataclass
from typing import Set


@dataclass
class DirectoryBruteforceInput:
    list_size: str


@dataclass
class ReconInput:
    directory_bruteforce: DirectoryBruteforceInput or None  # type: ignore


@dataclass
class UserInput:
    use_type: str
    phase: str or None  # type: ignore
    module: str or None  # type: ignore
    targets: Set[str]
    recon: ReconInput or None  # type: ignore
    output_after_every_phase: bool
    output_after_every_finding: bool
