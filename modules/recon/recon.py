from typing import Optional

from config.settings import RECON_PHASE_MODULES
from modules.recon.directory_bruteforce.directory_bruteforce import DirectoryBruteforce
from utils.custom_dataclasses import ReconInput, DirectoryBruteforceInput
from utils.abstracts_classes import AbstractModule


class Recon(AbstractModule):
    def __init__(
        self, recon_input: ReconInput, target: str, single_module: Optional[str]
    ) -> None:
        super().__init__()
        self.directory_bruteforce_input: DirectoryBruteforceInput = getattr(recon_input, "directory_bruteforce")
        self.target = target
        self.single_module = single_module

    def run(self) -> None:
        if not self.single_module:
            for module in RECON_PHASE_MODULES:
                getattr(self, f"_run_{module}")()
        else:
            if self.single_module not in RECON_PHASE_MODULES:
                raise ValueError(
                    f"Invalid module name: {self.single_module}. "
                    f"Available modules: {RECON_PHASE_MODULES}"
                )
            getattr(self, f"_run_{self.single_module}")()

    def _run_directory_bruteforce(self) -> None:
        directory_bruteforce = DirectoryBruteforce(
            directory_bruteforce_input=self.directory_bruteforce_input,
            target=self.target,
        )
        directory_bruteforce.run()
