from config.settings import RECON_PHASE_MODULES
from modules.recon.directory_bruteforce.directory_bruteforce import DirectoryBruteforce
from utils.abstracts_classes import AbstractModule


class Recon(AbstractModule):
    recon_phase_modules: set = RECON_PHASE_MODULES
    directory_bruteforce_list_size: str = str()

    def __init__(self, directory_bruteforce_list_size: str, target: str) -> None:
        super().__init__()
        self.directory_bruteforce_list_size = directory_bruteforce_list_size
        self.target = target

    def run(self):
        for module in self.recon_phase_modules:
            getattr(self, f"_run_{module}")()

    def _run_directory_bruteforce(self):
        directory_bruteforce = DirectoryBruteforce(
            request_url=self.target, list_size=self.directory_bruteforce_list_size
        )
        directory_bruteforce.run()
