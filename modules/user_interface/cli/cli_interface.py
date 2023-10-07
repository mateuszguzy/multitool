from typing import List, Set, Tuple

from questionary import prompt

from config.settings import (
    AVAILABLE_FUNCTIONALITY,
    AVAILABLE_PHASES,
    RECON_PHASE_MODULES, SCAN_PHASE_MODULES,
)
from modules.helper.redis_client import RedisClient
from utils.abstracts_classes import AbstractModule
from utils.custom_dataclasses import (
    DirectoryBruteforceInput,
    ReconInput,
    UserInput,
    ScanInput,
    PortScanInput,
)
from utils.utils import convert_list_or_set_to_dict, url_formatter, clean_and_validate_input_ports

ALL, SINGLE_PHASE, SINGLE_MODULE = "all", "single_phase", "single_module"


class CliInterface(AbstractModule):
    valid_targets: set = set()
    valid_ports: set = set()
    questions: List[dict] = list()

    def __init__(self):
        super().__init__()
        self.questions = self.prepare_questions()

    def run(self) -> UserInput:
        answers = prompt(self.questions)
        recon_phase_input, scan_phase_input = self.aggregate_phase_specific_data(
            answers=answers
        )
        used_modules = self.extract_used_phases_and_modules_data_from_user_input(
            answers=answers
        )
        self.format_targets_as_urls(answers["targets"])
        self.save_reusable_data_in_db(used_modules=used_modules)

        return UserInput(
                use_type=answers.get("use_type", ""),
                phase=answers.get("phase", ""),
                module=answers.get("module", None),
                targets=self.valid_targets,
                recon=recon_phase_input,
                scan=scan_phase_input,
                output_after_every_phase=answers.get("output_after_every_phase", 0),
                output_after_every_finding=answers.get("output_after_every_finding", 0),
            )

    def prepare_questions(self) -> List[dict]:
        """
        Prepare questions for user input according to docs:
        https://questionary.readthedocs.io/en/stable/pages/advanced.html#create-questions-from-dictionaries
        """
        return [
            {
                "type": "select",
                "name": "use_type",
                "message": "Choose Multitool use type:",
                "choices": [ALL, SINGLE_PHASE, SINGLE_MODULE],
                "default": "all",
            },
            {
                "type": "text",
                "name": "targets",
                "message": "Enter URLs as comma separated values:",
            },
            {
                "type": "select",
                "name": "phase",
                "message": "Choose Phase to execute:",
                "choices": AVAILABLE_PHASES,
                "default": "recon",
                "when": lambda answers: answers["use_type"] == "single_phase",
            },
            {
                "type": "select",
                "name": "phase",
                "message": "From which phase a module should be executed:",
                "choices": AVAILABLE_PHASES,
                "default": "recon",
                "when": lambda answers: answers["use_type"] == "single_module",
            },
            {
                "type": "select",
                "name": "module",
                "message": "Choose Module to execute:",
                "choices": RECON_PHASE_MODULES,
                "default": "directory_bruteforce",
                "when": lambda answers: self.recon_single_module_is_used(answers),
            },
            {
                "type": "select",
                "name": "module",
                "message": "Choose Module to execute:",
                "choices": SCAN_PHASE_MODULES,
                "default": "port_scan",
                "when": lambda answers: self.scan_single_module_is_used(answers),
            },
            {
                "type": "select",
                "name": "directory_bruteforce_list_size",
                "message": "Choose size or bruteforce wordlist:",
                "choices": ["small", "medium", "test"],
                "default": "small",
                "when": lambda answers: self.directory_bruteforce_is_executed(
                    answers=answers
                ),
            },
            {
                "type": "text",
                "name": "ports_to_scan",
                "message": "Specify ports to scan as comma separated values:",
                "when": lambda answers: self.port_scan_is_executed(answers=answers),
                "validate": lambda val: self.validate_ports_to_scan(ports_to_scan=val),
            },
            {
                "type": "confirm",
                "name": "output_after_every_phase",
                "message": "Show output after every phase?",
                "default": True,
            },
            {
                "type": "confirm",
                "name": "output_after_every_finding",
                "message": "Show output after every finding?",
                "default": True,
            },
        ]

    @staticmethod
    def recon_single_module_is_used(answers: dict) -> bool:
        """
        Check if recon is used in current run by checking which modules are used.
        """
        if answers["use_type"] == "single_module" and answers["phase"] == "recon":
            return True
        else:
            return False

    @staticmethod
    def scan_single_module_is_used(answers: dict) -> bool:
        """
        Check if recon is used in current run by checking which modules are used.
        """
        if answers["use_type"] == "single_module" and answers["phase"] == "scan":
            return True
        else:
            return False

    @staticmethod
    def directory_bruteforce_is_executed(answers: dict) -> bool:
        """
        Check if directory bruteforce is executed in current run by checking which modules are used.
        """
        if "use_type" in answers and answers["use_type"] == "all":
            return True
        elif "phase" in answers and answers["phase"] == "recon":
            return True
        elif "module" in answers and answers["module"] == "directory_bruteforce":
            return True
        else:
            return False

    @staticmethod
    def port_scan_is_executed(answers: dict) -> bool:
        """
        Check if directory bruteforce is executed in current run by checking which modules are used.
        """
        if "use_type" in answers and answers["use_type"] == "all":
            return True
        elif "phase" in answers and answers["phase"] == "scan":
            return True
        elif "module" in answers and answers["module"] == "port_scan":
            return True
        else:
            return False

    def format_targets_as_urls(self, targets: str) -> None:
        """
        Validate targets and return True if any of them are valid.
        """
        split_targets = targets.split(",")
        self.valid_targets = {url_formatter(input_target=target.strip()) for target in split_targets}

    def validate_ports_to_scan(self, ports_to_scan: str) -> bool:
        """
        Validate ports to scan and return True if any of them are valid.
        """
        self.valid_ports = clean_and_validate_input_ports(ports_to_scan=ports_to_scan)
        if len(self.valid_ports) == 0:
            return False
        return True

    def aggregate_phase_specific_data(
        self, answers: dict
    ) -> Tuple[ReconInput, ScanInput]:
        """
        Aggregate phase specific data from user input and return it in form of dictionary.
        """
        recon_phase_input = self.aggregate_recon_phase_data(answers=answers)
        scan_phase_input = self.aggregate_scan_phase_data()

        return recon_phase_input, scan_phase_input

    def aggregate_recon_phase_data(self, answers: dict) -> ReconInput:
        """
        Aggregate recon phase data from user input and return it in form of dictionary.
        """
        directory_bruteforce_input = self.aggregate_directory_bruteforce_data(
            answers=answers
        )
        return ReconInput(directory_bruteforce=directory_bruteforce_input)

    def aggregate_scan_phase_data(self) -> ScanInput:
        """
        Aggregate scan phase data from user input and return it in form of dictionary.
        """
        port_scan_input = self.aggregate_port_scan_data()
        return ScanInput(port_scan=port_scan_input)

    @staticmethod
    def aggregate_directory_bruteforce_data(answers: dict) -> DirectoryBruteforceInput:
        """
        Aggregate directory bruteforce data from user input and return it in form of dictionary.
        """
        return DirectoryBruteforceInput(
                list_size=answers.get("directory_bruteforce_list_size", None)
            )

    def aggregate_port_scan_data(self) -> PortScanInput:
        """
        Aggregate port scan data from user input and return it in form of dictionary.
        """
        return PortScanInput(ports=self.valid_ports)

    @staticmethod
    def extract_used_phases_and_modules_data_from_user_input(answers: dict) -> Set[str]:
        """
        Extract used modules data from user input and save it in self.used_modules,
        for future use - saving in db and later - pulling results.
        """
        used_modules: set = set()

        if answers["use_type"] == ALL:
            for phase in AVAILABLE_PHASES:
                for module in AVAILABLE_FUNCTIONALITY[phase]:
                    used_modules.add(f"{phase}|{module}")

        elif answers["use_type"] == SINGLE_PHASE:
            for module in AVAILABLE_FUNCTIONALITY[answers["phase"]]:
                used_modules.add(f"{answers['phase']}|{module}")

        elif answers["use_type"] == SINGLE_MODULE:
            used_modules.add(f"{answers['phase']}|{answers['module']}")

        return used_modules

    def save_reusable_data_in_db(self, used_modules: Set[str]) -> None:
        """
        Save targets and modules data in Redis in form of dictionary for future use - pulling results.

        targets: {
            id: target
        }

        modules: {
            id: module
        }
        """
        targets_dictionary = convert_list_or_set_to_dict(
            list_of_items=self.valid_targets
        )
        modules_dictionary = convert_list_or_set_to_dict(
            list_of_items=used_modules
        )

        with RedisClient() as rc:
            rc.mset({"targets|" + str(k): v for k, v in targets_dictionary.items()})
            rc.mset({"modules|" + str(k): v for k, v in modules_dictionary.items()})
