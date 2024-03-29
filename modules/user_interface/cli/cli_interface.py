from typing import List, Set, Tuple

from questionary import prompt

from config.settings import (
    AVAILABLE_FUNCTIONALITY,
    AVAILABLE_PHASES,
    RECON_PHASE_MODULES,
    SCAN_PHASE_MODULES,
    REDIS_TARGETS_KEY,
    REDIS_USER_INPUT_KEY,
    REDIS_MODULES_KEY,
    REDIS_USE_TYPE_KEY,
    REDIS_OUTPUT_AFTER_EVERY_FINDING_KEY,
    REDIS_DIRECTORY_BRUTEFORCE_LIST_SIZE_KEY,
    REDIS_DIRECTORY_BRUTEFORCE_RECURSIVE_KEY,
    REDIS_DIRECTORY_BRUTEFORCE_INPUT_KEY,
    REDIS_PORT_SCAN_INPUT_KEY,
    REDIS_PORT_SCAN_TYPE_KEY,
    REDIS_PORT_SCAN_PORTS,
    GAIN_ACCESS_PHASE_MODULES,
    REDIS_ZAP_SPIDER_INPUT_KEY,
    REDIS_ZAP_SPIDER_AS_USER_KEY,
    REDIS_ZAP_SPIDER_ENHANCED_KEY,
)
from modules.helper.redis_client import RedisClient
from modules.zap.context import list_context_files, extract_targets_from_context_file
from utils.abstracts_classes import AbstractModule
from utils.custom_dataclasses import (
    DirectoryBruteforceInput,
    ReconInput,
    UserInput,
    ScanInput,
    PortScanInput,
    ZapSpiderInput,
)
from utils.redis_utils import put_single_value_in_db
from utils.url_utils import url_formatter
from utils.utils import (
    convert_list_or_set_to_dict,
    clean_and_validate_input_ports,
)

ALL, SINGLE_PHASE, SINGLE_MODULE = "all", "single_phase", "single_module"
PORT_SCAN_TYPES = ["important", "top_1000", "all", "custom"]
NEW_CONTEXT, EXISTING_CONTEXT = "new", "existing"


class CliInterface(AbstractModule):
    valid_targets: set = set()
    valid_ports: set = set()
    use_type: str
    output_after_every_finding: bool
    questions: List[dict] = list()
    choose_module_message: str = "Choose Module to execute:"
    context_files: List[str] = list()

    def __init__(self):
        super().__init__()
        self.questions = self.prepare_questions()
        self.context_files = list_context_files()

    def run(self) -> UserInput:
        answers = self.ask_questions()
        recon_phase_input, scan_phase_input = self.aggregate_phase_specific_data(
            answers=answers
        )
        used_modules = self.extract_used_phases_and_modules_data_from_user_input(
            answers=answers
        )

        include_targets = set()
        exclude_targets = set()

        if "targets" in answers and answers["targets"]:
            self.valid_targets = self.format_targets_as_urls(answers["targets"])

        elif "context_file_name" in answers and answers["context_file_name"]:
            self.valid_targets = extract_targets_from_context_file(
                context_name=answers["context_file_name"].split(".")[0]
            )

        if answers.get("include_targets", None):
            include_targets = self.format_targets_as_urls(answers["include_targets"])
            self.valid_targets = self.valid_targets.union(include_targets)

        if answers.get("exclude_targets", None):
            # do not format as URLs because keyword might be provided in input
            exclude_targets = {
                item.strip() for item in answers["exclude_targets"].split(",")
            }

        self.output_after_every_finding = answers.get(
            "output_after_every_finding", False
        )
        self.use_type = answers.get("use_type", "")
        self.save_reusable_data_in_db(
            used_modules=used_modules,
            recon_phase_input=recon_phase_input,
            scan_phase_input=scan_phase_input,
        )

        return UserInput(
            use_type=self.use_type,
            phase=answers.get("phase", ""),
            module=answers.get("module", None),
            context_file_name=answers.get("context_file_name", None),
            targets=self.valid_targets,
            include_targets=include_targets,
            exclude_targets=exclude_targets,
            recon=recon_phase_input,
            scan=scan_phase_input,
            output_after_every_finding=self.output_after_every_finding,
        )

    def ask_questions(self):
        """
        Function made for better testability of CLI Interface.
        """
        return prompt(self.questions)

    def prepare_questions(self) -> List[dict]:
        """
        Prepare questions for user input according to docs:
        https://questionary.readthedocs.io/en/stable/pages/advanced.html#create-questions-from-dictionaries
        """
        return [
            ##########################
            #         GENERAL        #
            ##########################
            {
                "type": "select",
                "name": "use_type",
                "message": "Choose Multitool use type:",
                "choices": [ALL, SINGLE_PHASE, SINGLE_MODULE],
                "default": ALL,
            },
            ##########################
            #         CONTEXT        #
            ##########################
            {
                "type": "select",
                "name": "context",
                "message": "Create new context or use existing one:",
                "choices": [NEW_CONTEXT, EXISTING_CONTEXT],
                "default": NEW_CONTEXT,
                "when": lambda answers: self.any_context_file_exist(),
            },
            {
                "type": "select",
                "name": "context_file_name",
                "choices": self.context_files,
                "message": "Choose context file:",
                "when": lambda answers: self.existing_context_is_used(answers=answers),
                "default": self.context_files[0] if self.context_files else None,
            },
            {
                "type": "text",
                "name": "include_targets",
                "message": "Enter URL targets to INCLUDE in the context (as comma separated values):",
                "when": lambda answers: self.existing_context_is_used(answers=answers),
            },
            {
                "type": "text",
                "name": "targets",
                "message": "Enter URL targets (as comma separated values):",
                "validate": lambda val: val != "",
                "when": lambda answers: self.new_context_is_used(answers=answers),
            },
            {
                "type": "text",
                "name": "exclude_targets",
                "message": "Enter URLs targets or keywords to EXCLUDE from the context (as comma separated values):",
            },
            ##########################
            #     MODULE SELECTION   #
            ##########################
            {
                "type": "select",
                "name": "phase",
                "message": "Choose Phase to execute:",
                "choices": AVAILABLE_PHASES,
                "default": "recon",
                "when": lambda answers: answers["use_type"] == "single_phase",
            },
            # this question allows to always have 'phase' populated,
            # so it's easier to determine if further questions need to be asked
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
                "message": self.choose_module_message,
                "choices": RECON_PHASE_MODULES,
                "default": "directory_bruteforce",
                "when": lambda answers: self.single_module_from_recon_phase_is_executed(
                    answers=answers
                ),
            },
            {
                "type": "select",
                "name": "module",
                "message": self.choose_module_message,
                "choices": SCAN_PHASE_MODULES,
                "default": "port_scan",
                "when": lambda answers: self.single_module_from_scan_phase_is_executed(
                    answers=answers
                ),
            },
            {
                "type": "select",
                "name": "module",
                "message": self.choose_module_message,
                "choices": GAIN_ACCESS_PHASE_MODULES,
                "default": "lfi",
                "when": lambda answers: self.single_module_from_gain_access_phase_is_executed(
                    answers=answers
                ),
            },
            ##########################
            #        ZAP SPIDER      #
            ##########################
            {
                "type": "confirm",
                "name": "zap_spider_enhanced",
                "message": "Enhance spider functionality with results from directory bruteforce module?",
                "default": False,
                "when": lambda answers: self.zap_spider_is_executed(answers=answers),
            },
            {
                "type": "confirm",
                "name": "zap_spider_as_user",
                "message": "Run spider as user? (DVWA only)",
                "default": False,
                "when": lambda answers: self.zap_spider_is_executed(answers=answers),
            },
            ##########################
            #  DIRECTORY BRUTEFORCE  #
            ##########################
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
                "type": "confirm",
                "name": "directory_bruteforce_recursive",
                "message": "Should bruteforce run recursively:",
                "default": False,
                "when": lambda answers: self.directory_bruteforce_is_executed(
                    answers=answers
                ),
            },
            ##########################
            #        PORT SCAN       #
            ##########################
            {
                "type": "select",
                "name": "port_scan_type",
                "message": "Choose ports to scan:",
                "choices": PORT_SCAN_TYPES,
                "default": "important",
                "when": lambda answers: self.port_scan_is_executed(answers=answers),
            },
            {
                "type": "text",
                "name": "ports_to_scan",
                "message": "Specify ports to scan as comma separated values:",
                "when": lambda answers: self.custom_port_scan_is_executed(
                    answers=answers
                ),
                "validate": lambda val: self.validate_ports_to_scan(ports_to_scan=val),
            },
            ##########################
            #         OUTPUT         #
            ##########################
            {
                "type": "confirm",
                "name": "output_after_every_finding",
                "message": "Show output after every finding?",
                "default": True,
            },
        ]

    ##########################
    #         CONTEXT        #
    ##########################
    def any_context_file_exist(self) -> bool:
        """
        Check if any context file exist.
        """
        if len(self.context_files) > 0:
            return True
        else:
            return False

    @staticmethod
    def existing_context_is_used(answers: dict) -> bool:
        """
        Check if existing context can be used in current run.
        """
        if "context" in answers and answers["context"] == EXISTING_CONTEXT:
            return True
        else:
            return False

    def new_context_is_used(self, answers: dict) -> bool:
        """
        Check if existing context can be used in current run.
        """
        if (
            "context" in answers
            and answers["context"] == NEW_CONTEXT
            or not self.any_context_file_exist()
        ):
            return True
        else:
            return False

    ##########################
    #     MODULE SELECTION   #
    ##########################
    @staticmethod
    def single_module_from_recon_phase_is_executed(answers: dict) -> bool:
        """
        Check if single module from recon phase is executed in current run by checking which modules are used.
        """
        if (
            "use_type" in answers
            and answers["use_type"] == "single_module"
            and "phase" in answers
            and answers["phase"] == "recon"
        ):
            return True
        else:
            return False

    @staticmethod
    def single_module_from_scan_phase_is_executed(answers: dict) -> bool:
        """
        Check if single module from recon phase is executed in current run by checking which modules are used.
        """
        if (
            "use_type" in answers
            and answers["use_type"] == "single_module"
            and "phase" in answers
            and answers["phase"] == "scan"
        ):
            return True
        else:
            return False

    @staticmethod
    def single_module_from_gain_access_phase_is_executed(answers: dict) -> bool:
        """
        Check if single module from 'gain access' phase is executed in current run by checking which modules are used.
        """
        if (
            "use_type" in answers
            and answers["use_type"] == "single_module"
            and "phase" in answers
            and answers["phase"] == "gain_access"
        ):
            return True
        else:
            return False

    ##########################
    #        ZAP SPIDER      #
    ##########################
    @staticmethod
    def zap_spider_is_executed(answers: dict) -> bool:
        """
        Check if zap spider is executed in current run by checking which modules are used.
        """
        if "use_type" in answers and answers["use_type"] == "all":
            return True

        elif (
            "use_type" in answers
            and answers["use_type"] == "single_phase"
            and "phase" in answers
            and answers["phase"] == "recon"
        ):
            return True

        elif (
            "phase" in answers
            and answers["phase"] == "recon"
            and "module" in answers
            and answers["module"] == "zap_spider"
        ):
            return True

        else:
            return False

    ##########################
    #  DIRECTORY BRUTEFORCE  #
    ##########################
    @staticmethod
    def directory_bruteforce_is_executed(answers: dict) -> bool:
        """
        Check if directory bruteforce is executed in current run by checking which modules are used.
        """
        if "use_type" in answers and answers["use_type"] == "all":
            return True

        elif (
            "use_type" in answers
            and answers["use_type"] == "single_phase"
            and "phase" in answers
            and answers["phase"] == "recon"
        ):
            return True

        elif (
            "phase" in answers
            and answers["phase"] == "recon"
            and "module" in answers
            and answers["module"] == "directory_bruteforce"
        ):
            return True

        elif (
            "module" in answers
            and answers["module"] == "zap_spider"
            and "zap_spider_enhanced" in answers
            and answers["zap_spider_enhanced"] is True
        ):
            return True

        else:
            return False

    ##########################
    #        PORT SCAN       #
    ##########################
    @staticmethod
    def port_scan_is_executed(answers: dict) -> bool:
        """
        Check if directory bruteforce is executed in current run by checking which modules are used.
        """
        if "use_type" in answers and answers["use_type"] == "all":
            return True

        elif (
            "use_type" in answers
            and answers["use_type"] == "single_phase"
            and "phase" in answers
            and answers["phase"] == "scan"
        ):
            return True

        elif (
            "phase" in answers
            and answers["phase"] == "scan"
            and "module" in answers
            and answers["module"] == "port_scan"
        ):
            return True

        else:
            return False

    @staticmethod
    def custom_port_scan_is_executed(answers: dict) -> bool:
        """
        Check if custom port scan is executed in current run by checking which modules are used.
        """
        if "port_scan_type" in answers and answers["port_scan_type"] == "custom":
            return True
        else:
            return False

    ##########################
    #          UTILS         #
    ##########################
    @staticmethod
    def format_targets_as_urls(targets: str) -> Set[str]:
        """
        Validate targets and return True if any of them are valid.
        """
        split_targets = targets.split(",")
        return {url_formatter(input_target=target.strip()) for target in split_targets}

    def validate_ports_to_scan(self, ports_to_scan: str) -> bool:
        """
        Validate ports to scan and return True if any of them are valid.
        """
        self.valid_ports = clean_and_validate_input_ports(ports_to_scan=ports_to_scan)
        if len(self.valid_ports) == 0:
            return False
        return True

    ##########################
    #     DATA AGGREGATION   #
    ##########################
    def aggregate_phase_specific_data(
        self, answers: dict
    ) -> Tuple[ReconInput, ScanInput]:
        """
        Aggregate phase specific data from user input and return it in form of dictionary.
        """
        recon_phase_input = self.aggregate_recon_phase_data(answers=answers)
        scan_phase_input = self.aggregate_scan_phase_data(answers=answers)

        return recon_phase_input, scan_phase_input

    def aggregate_recon_phase_data(self, answers: dict) -> ReconInput:
        """
        Aggregate recon phase data from user input and return it in form of dictionary.
        """
        directory_bruteforce_input = self.aggregate_directory_bruteforce_data(
            answers=answers
        )
        zap_spider_input = self.aggregate_zap_spider_data(answers=answers)
        return ReconInput(
            directory_bruteforce=directory_bruteforce_input, zap_spider=zap_spider_input
        )

    def aggregate_scan_phase_data(self, answers: dict) -> ScanInput:
        """
        Aggregate scan phase data from user input and return it in form of dictionary.
        """
        port_scan_input = self.aggregate_port_scan_data(answers=answers)
        return ScanInput(port_scan=port_scan_input)

    @staticmethod
    def aggregate_zap_spider_data(answers: dict) -> ZapSpiderInput:
        """
        Aggregate zap spider data from user input and return it in form of dictionary.
        """
        return ZapSpiderInput(
            as_user=answers.get("zap_spider_as_user", None),
            enhanced=answers.get("zap_spider_enhanced", None),
        )

    @staticmethod
    def aggregate_directory_bruteforce_data(answers: dict) -> DirectoryBruteforceInput:
        """
        Aggregate directory bruteforce data from user input and return it in form of dictionary.
        """
        return DirectoryBruteforceInput(
            list_size=answers.get("directory_bruteforce_list_size", None),
            recursive=answers.get("directory_bruteforce_recursive", None),
        )

    def aggregate_port_scan_data(self, answers: dict) -> PortScanInput:
        """
        Aggregate port scan data from user input and return it in form of dictionary.
        """
        return PortScanInput(
            port_scan_type=answers.get("port_scan_type", None),
            ports=self.valid_ports,
        )

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

    def save_reusable_data_in_db(
        self,
        used_modules: Set[str],
        recon_phase_input: ReconInput,
        scan_phase_input: ScanInput,
    ) -> None:
        """
        Save targets and modules data in Redis in form of dictionary for future use e.g. pulling results.

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
        modules_dictionary = convert_list_or_set_to_dict(list_of_items=used_modules)
        ports_dictionary = (
            convert_list_or_set_to_dict(list_of_items=scan_phase_input.port_scan.ports)
            if len(scan_phase_input.port_scan.ports) > 0
            else {1: None}
        )

        with RedisClient() as rc:
            ####################################
            #              GENERAL             #
            ####################################
            rc.mset(
                {
                    f"{REDIS_USER_INPUT_KEY}{REDIS_TARGETS_KEY}" + str(k): v
                    for k, v in targets_dictionary.items()
                }
            )
            rc.mset(
                {
                    f"{REDIS_USER_INPUT_KEY}{REDIS_MODULES_KEY}" + str(k): v
                    for k, v in modules_dictionary.items()
                }
            )
            put_single_value_in_db(
                key=f"{REDIS_USER_INPUT_KEY}{REDIS_USE_TYPE_KEY}", value=self.use_type
            )
            put_single_value_in_db(
                key=f"{REDIS_USER_INPUT_KEY}{REDIS_OUTPUT_AFTER_EVERY_FINDING_KEY}",
                value=str(self.output_after_every_finding),
            )
            ####################################
            #               RECON              #
            ####################################
            put_single_value_in_db(
                key=f"{REDIS_ZAP_SPIDER_INPUT_KEY}{REDIS_ZAP_SPIDER_AS_USER_KEY}",
                value=str(recon_phase_input.zap_spider.as_user),
            )
            put_single_value_in_db(
                key=f"{REDIS_ZAP_SPIDER_INPUT_KEY}{REDIS_ZAP_SPIDER_ENHANCED_KEY}",
                value=str(recon_phase_input.zap_spider.enhanced),
            )
            put_single_value_in_db(
                key=f"{REDIS_DIRECTORY_BRUTEFORCE_INPUT_KEY}"
                f"{REDIS_DIRECTORY_BRUTEFORCE_LIST_SIZE_KEY}",
                value=str(recon_phase_input.directory_bruteforce.list_size),
            )
            put_single_value_in_db(
                key=f"{REDIS_DIRECTORY_BRUTEFORCE_INPUT_KEY}"
                f"{REDIS_DIRECTORY_BRUTEFORCE_RECURSIVE_KEY}",
                value=str(recon_phase_input.directory_bruteforce.recursive),
            )
            ####################################
            #               SCAN               #
            ####################################
            put_single_value_in_db(
                key=f"{REDIS_PORT_SCAN_INPUT_KEY}{REDIS_PORT_SCAN_TYPE_KEY}",
                value=str(scan_phase_input.port_scan.port_scan_type),
            )
            rc.mset(
                {
                    f"{REDIS_PORT_SCAN_INPUT_KEY}{REDIS_PORT_SCAN_PORTS}"
                    + str(k): str(v)
                    for k, v in ports_dictionary.items()
                }
            )
