from dataclasses import dataclass
from typing import Set, Optional


@dataclass
class DirectoryBruteforceInput:
    list_size: Optional[str]


@dataclass
class ReconInput:
    directory_bruteforce: dict


@dataclass
class UserInput:
    use_type: str
    phase: Optional[str]
    module: Optional[str]
    targets: Set[str]
    recon: dict
    output_after_every_phase: bool
    output_after_every_finding: bool
