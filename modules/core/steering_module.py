import json
from collections.abc import Generator

from modules.scan.port_scan import PortScan
from utils.abstracts_classes import Module
from modules.recon.credential_leaks_check import CredentialLeaksCheck
from modules.recon.directory_bruteforce import DirectoryBruteforce
from modules.recon.email_scraping import EmailScraping


class SteeringModule(Module):
    recon_phase_modules = ["dir_bruteforce", "email_scraping", "credential_leaks_check"]
    scan_phase_modules = ["port_scan", "file_upload_form", "file_inclusion_url"]

    def __init__(self, user_input: json) -> None:
        self._assign_json_values_to_class_attributes(user_input=user_input)

    def run(self) -> Generator:
        """
        First function to run after user input is passed. Defines app top level behaviour.
        """
        if self.use_type == "all":
            for value in self._run_all():
                yield value

        elif self.use_type == "single_phase":
            for value in self._run_phase(phase=self.phase):
                yield value

        elif self.use_type == "single_module":
            for value in self._run_module(module=self.module):
                yield value

    # --- MODULES
    @staticmethod
    def _dir_bruteforce() -> Generator:
        """
        Function launching directory bruteforce module.
        """
        dir_bruteforce = DirectoryBruteforce()
        output = dir_bruteforce.run()

        yield output

    @staticmethod
    def _email_scraping() -> Generator:
        """
        Function launching email scraping module.
        """
        email_scraping = EmailScraping()
        output = email_scraping.run()

        yield output

    @staticmethod
    def _credential_leaks_check() -> Generator:
        """
        Function launching credential leaks checking module.
        """
        credential_leaks_check = CredentialLeaksCheck()
        output = credential_leaks_check.run()

        yield output

    @staticmethod
    def _port_scan():
        """
        Port scanner.
        """
        port_scan = PortScan()
        output = port_scan.run()

        yield output

    # --- PHASES
    def _run_recon(self):
        for module in self.recon_phase_modules:
            for value in self._run_module(module=module):
                yield value

    def _run_scan(self):
        for module in self.scan_phase_modules:
            for value in self._run_module(module=module):
                yield value

    # --- MAIN
    def _run_all(self):
        """
        Run all the functionalities that app holds.
        """
        # TODO: multithreading
        self._run_phase("recon")
        self._run_phase("scan")
        yield

    def _run_phase(self, phase: str) -> Generator:
        """
        Run single phase of hacking process.
        :param phase: e.g. recon / scan / gain_access / maintain_access / cover_tracks
        """
        # TODO: multithreading
        if phase == "recon":
            for value in self._run_recon():
                yield value

        elif phase == "scan":
            for value in self._run_scan():
                yield value

    def _run_module(self, module: str) -> Generator:
        """
        Run single module of any hacking process phase.
        :param module: e.g. dir_bruteforce / port_scan / lfi_rfi
        """
        if module == "dir_bruteforce":
            for value in self._dir_bruteforce():
                yield value

        elif module == "email_scraping":
            for value in self._email_scraping():
                yield value

        elif module == "credential_leaks_check":
            for value in self._credential_leaks_check():
                yield value

        elif module == "port_scan":
            for value in self._port_scan():
                yield value

    # --- UTILS
    def _assign_json_values_to_class_attributes(self, user_input: json) -> None:
        """
        Function responsible for assigning user input in form of JSON file to class specific attributes.
        :param user_input:
        """
        self.use_type = user_input["use_type"]
        self.phase = user_input["phase"]
        self.module = user_input["module"]
        self.input_type = user_input["input_type"]
        self.dir_bruteforce_list_size = user_input["recon"]["dir_bruteforce"][
            "list_size"
        ]
        self.ports_to_scan = user_input["scan"]["port_scan"]["ports_to_scan"]
        self.services_to_enumerate = user_input["scan"]["enumeration"]["services"]
        self.lfi_rfi_url_known = user_input["gain_access"]["lfi_rfi"]["url_is_known"]
        self.lfi_rfi_url = user_input["gain_access"]["lfi_rfi"]["url"]
        self.file_upload_url_known = user_input["gain_access"]["file_upload"][
            "url_is_known"
        ]
        self.file_upload_url = user_input["gain_access"]["file_upload"]["url"]
        self.output_after_every_phase = user_input["output_after_every_phase"]
        self.output_after_every_finding = user_input["output_after_every_finding"]
