from config.settings import RECON_PHASE_MODULES
from modules.recon.credential_leaks_check.credential_leaks_check import (
    CredentialLeaksCheck,
)
from modules.recon.directory_bruteforce.directory_bruteforce import DirectoryBruteforce
from modules.recon.email_scraping.email_scraping import EmailScraping
from modules.scan.port_scan.port_scan import PortScan
from utils.abstracts_classes import AbstractModule


class SteeringModule(AbstractModule):
    use_type: str = str()
    phase: str = str()
    module: str = str()
    input_type: str = str()
    input: list[str] = list()
    dir_bruteforce_list_size: str = str()
    ports_to_scan: str = str()
    custom_ports_to_scan: list[int] = list()
    services_to_enumerate: list[str] = list()
    lfi_rfi_url_known: bool = bool()
    lfi_rfi_url: str = str()
    file_upload_url_known: bool = bool()
    file_upload_url: str = str()
    output_after_every_phase: bool = bool()
    output_after_every_finding: bool = bool()
    recon_phase_modules: list[str] = list()
    scan_phase_modules: list[str] = list()

    def __init__(self, user_input: dict) -> None:
        super().__init__()
        self._assign_json_values_to_class_attributes(user_input=user_input)
        self.recon_phase_modules = RECON_PHASE_MODULES

    def run(self, **kwargs) -> None:
        """
        First function to run after user input is passed. Defines app top level behaviour.
        """
        if self.use_type == "all":
            self._run_all()

        elif self.use_type == "single_phase":
            self._run_phase(phase=self.phase)

        elif self.use_type == "single_module":
            self._run_module(module=self.module)

    # --- MODULES
    def _dir_bruteforce(self) -> None:
        """
        Function launching directory bruteforce module.
        """
        for url_to_check in self.input:
            dir_bruteforce = DirectoryBruteforce(
                list_size=self.dir_bruteforce_list_size, request_url=url_to_check
            )
            dir_bruteforce.run()

    @staticmethod
    def _email_scraping() -> None:
        """
        Function launching email scraping module.
        """
        email_scraping = EmailScraping()
        email_scraping.run()

    @staticmethod
    def _credential_leaks_check() -> None:
        """
        Function launching credential leaks checking module.
        """
        credential_leaks_check = CredentialLeaksCheck()
        credential_leaks_check.run()

    @staticmethod
    def _port_scan() -> None:
        """
        Port scanner.
        """
        port_scan = PortScan()
        port_scan.run()

    # --- PHASES
    def _run_recon(self):
        for module in self.recon_phase_modules:
            self._run_module(module=module)

    def _run_scan(self):
        for module in self.scan_phase_modules:
            self._run_module(module=module)

    # --- MAIN
    def _run_all(self) -> None:
        """
        Run all the functionalities that app holds.
        """
        self._run_phase("recon")
        self._run_phase("scan")

    def _run_phase(self, phase: str) -> None:
        """
        Run single phase of hacking process.
        :param phase: e.g. recon / scan / gain_access / maintain_access / cover_tracks
        """
        if phase == "recon":
            self._run_recon()

        elif phase == "scan":
            self._run_scan()

    def _run_module(self, module: str) -> None:
        """
        Run single module of any hacking process phase.
        :param module: e.g. dir_bruteforce / port_scan / lfi_rfi
        """
        if module == "dir_bruteforce":
            self._dir_bruteforce()

        elif module == "email_scraping":
            self._email_scraping()

        elif module == "credential_leaks_check":
            self._credential_leaks_check()

        elif module == "port_scan":
            self._port_scan()

    # --- UTILS
    def _assign_json_values_to_class_attributes(self, user_input: dict) -> None:
        """
        Function responsible for assigning user input in form of JSON file to class specific attributes.
        :param user_input:
        """
        self.use_type = user_input["use_type"]
        self.phase = user_input["phase"]
        self.module = user_input["module"]
        self.input_type = user_input["input_type"]
        self.input = user_input["input"]
        self.dir_bruteforce_list_size = user_input["recon"]["dir_bruteforce"][
            "list_size"
        ]
        self.ports_to_scan = user_input["scan"]["port_scan"]["ports_to_scan"]
        self.custom_ports_to_scan = user_input["scan"]["port_scan"][
            "custom_ports_to_scan"
        ]
        self.services_to_enumerate = user_input["scan"]["enumeration"]["services"]
        self.lfi_rfi_url_known = user_input["gain_access"]["lfi_rfi"]["url_is_known"]
        self.lfi_rfi_url = user_input["gain_access"]["lfi_rfi"]["url"]
        self.file_upload_url_known = user_input["gain_access"]["file_upload"][
            "url_is_known"
        ]
        self.file_upload_url = user_input["gain_access"]["file_upload"]["url"]
        self.output_after_every_phase = user_input["output_after_every_phase"]
        self.output_after_every_finding = user_input["output_after_every_finding"]
