import datetime
import uuid
from typing import Set, Tuple

from config.settings import (
    AVAILABLE_FUNCTIONALITY,
    RECON_PHASE_MODULES,
    steering_module_logger,
    SCAN_PHASE_MODULES,
    ALL_MODULES,
    GAIN_ACCESS_PHASE_MODULES,
    CURRENT_DATE,
    REDIS_ZAP_CONTEXT_ID_KEY,
    REDIS_ZAP_CONTEXT_NAME_KEY,
)
from modules.task_queue.tasks import start_module_event
from modules.zap.context import (
    create_new_context,
    include_in_context,
    export_context_file,
    exclude_from_context,
    import_context_file,
)
from utils.abstracts_classes import AbstractModule
from utils.custom_dataclasses import ReconInput, UserInput, ScanInput, StartModuleEvent
from utils.utils import put_single_value_in_db, hash_target_name

logger = steering_module_logger


class SteeringModule(AbstractModule):
    use_type: str = str()
    phase: str = str()
    module: str = str()
    targets: Set[str] = set()
    recon_input: ReconInput
    scan_input: ScanInput
    output_after_every_finding: bool = bool()

    def __init__(self, user_input: UserInput) -> None:
        super().__init__()
        self._assign_user_input_to_class_attributes(user_input=user_input)

    def run(self) -> None:
        """
        First function to run after user input is passed. Defines app top level behaviour.
        """
        self.context_setup()

        if self.use_type == "all":
            self._run_all()

        elif self.use_type == "single_phase":
            self._run_phase(phase=self.phase)

        elif self.use_type == "single_module":
            for target in self.targets:
                self._run_module(module=self.module, target=target)

        else:
            raise ValueError(f"Invalid use_type: {self.use_type}")

    # --- MAIN
    def _run_all(self) -> None:
        """
        Run all the functionalities that app holds.
        """
        for phase in AVAILABLE_FUNCTIONALITY:
            logger.debug("START::all")
            self._run_phase(phase=phase)

    # --- PHASES
    def _run_recon(self) -> None:
        """
        Function launching recon phase.
        """
        for target in self.targets:
            logger.debug(f"START::recon::{target}")
            for module in RECON_PHASE_MODULES:
                self._run_module(module=module, target=target)

    def _run_scan(self):
        """
        Function launching scan phase.
        """
        for target in self.targets:
            logger.debug(f"START::scan::{target}")
            for module in SCAN_PHASE_MODULES:
                self._run_module(module=module, target=target)

    def _run_gain_access(self):
        """
        Function launching 'gain access' phase.
        """
        for target in self.targets:
            logger.debug(f"START::gain_access::{target}")
            for module in GAIN_ACCESS_PHASE_MODULES:
                self._run_module(module=module, target=target)

    def _run_phase(self, phase: str) -> None:
        """
        Run single phase of hacking process.
        :param phase: e.g. recon / scan / gain_access / maintain_access / cover_tracks
        """
        phase_mapping = {
            "recon": self._run_recon,
            "scan": self._run_scan,
            "gain_access": self._run_gain_access,
        }
        if phase in phase_mapping:
            phase_mapping[phase]()
        # double validation, beside input validation on UI side - safety net
        else:
            raise ValueError(f"Invalid phase: {phase}")

    # --- MODULES
    @staticmethod
    def _run_module(module: str, target: str) -> None:
        """
        Run single module of any hacking process phase.
        :param module: e.g. directory_bruteforce / port_scan / lfi_rfi
        """
        if module in ALL_MODULES:
            logger.debug(f"START::{module}::{target}")
            event = StartModuleEvent(
                id=uuid.uuid4(),
                source_module=__name__,
                destination_module=module,
                target=target,
                result=None,
            )
            start_module_event.delay(event=event)
        else:
            raise ValueError(f"Invalid module: {module}")

    # --- UTILS
    def _assign_user_input_to_class_attributes(self, user_input: UserInput) -> None:
        """
        Function responsible for assigning user input in form of dictionary to class specific attributes.
        :param user_input:
        """
        self.use_type = getattr(user_input, "use_type")
        self.phase = getattr(user_input, "phase")
        self.module = getattr(user_input, "module")
        self.context_file_name = getattr(user_input, "context_file_name")
        self.targets = getattr(user_input, "targets")
        self.include_targets = getattr(user_input, "include_targets")
        self.exclude_targets = getattr(user_input, "exclude_targets")
        self.recon_input = getattr(user_input, "recon")
        self.scan_input = getattr(user_input, "scan")
        self.output_after_every_finding = getattr(
            user_input, "output_after_every_finding"
        )

    def context_setup(self) -> None:
        """
        Function responsible for setting up context for ZAP and storing relevant data in the database.
        """
        if not self.context_file_name:
            context_id, context_name = self._handle_context_creation()
        else:
            context_id = import_context_file(context_file_name=self.context_file_name)
            context_name = self.context_file_name.split(".")[
                0
            ]  # get rid of the extension

        self._add_targets_to_context(context_name=context_name)
        self._store_context_data_in_database(
            context_id=context_id, context_name=context_name
        )
        self._exclude_from_context(context_name=context_name)
        export_context_file(context_name=context_name)

    def _handle_context_creation(self) -> Tuple[int, str]:
        """
        Function responsible for creating context for ZAP.
        """
        current_time = datetime.datetime.now().strftime("%H%M")
        hashed_target_name = hash_target_name(target=list(self.targets)[0])
        context_name = f"{CURRENT_DATE}_{current_time}_{hashed_target_name}"
        context_id = create_new_context(context_name=context_name)

        return context_id, context_name

    def _add_targets_to_context(self, context_name: str) -> None:
        """
        Function responsible for adding targets to context for ZAP.
        """
        for target in self.targets:
            include_in_context(target=target, context_name=context_name)

    def _exclude_from_context(self, context_name: str) -> None:
        """
        Function responsible for excluding targets from context for ZAP.
        """
        exclude_from_context(targets=self.exclude_targets, context_name=context_name)

    @staticmethod
    def _store_context_data_in_database(context_id: int, context_name: str) -> None:
        """
        Store context data in Redis database for later use.
        """
        put_single_value_in_db(key=REDIS_ZAP_CONTEXT_ID_KEY, value=str(context_id))
        put_single_value_in_db(key=REDIS_ZAP_CONTEXT_NAME_KEY, value=context_name)
