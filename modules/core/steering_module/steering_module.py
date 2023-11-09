import uuid
from typing import Set

from config.settings import (
    AVAILABLE_FUNCTIONALITY,
    RECON_PHASE_MODULES,
    steering_module_logger,
    SCAN_PHASE_MODULES,
    ALL_MODULES,
)
from modules.task_queue.tasks import start_module_event
from utils.abstracts_classes import AbstractModule
from utils.custom_dataclasses import ReconInput, UserInput, ScanInput, StartModuleEvent

logger = steering_module_logger


class SteeringModule(AbstractModule):
    use_type: str = str()
    phase: str = str()
    module: str = str()
    targets: Set[str] = set()
    recon_input: ReconInput
    scan_input: ScanInput
    output_after_every_phase: bool = bool()
    output_after_every_finding: bool = bool()

    def __init__(self, user_input: UserInput) -> None:
        super().__init__()
        self._assign_user_input_to_class_attributes(user_input=user_input)

    def run(self) -> None:
        """
        First function to run after user input is passed. Defines app top level behaviour.
        """
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

    def _run_phase(self, phase: str) -> None:
        """
        Run single phase of hacking process.
        :param phase: e.g. recon / scan / gain_access / maintain_access / cover_tracks
        """
        phase_mapping = {"recon": self._run_recon, "scan": self._run_scan}
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
        # TODO: put this also to Redis to use it in other modules
        self.use_type = getattr(user_input, "use_type")
        self.phase = getattr(user_input, "phase")
        self.module = getattr(user_input, "module")
        self.targets = getattr(user_input, "targets")
        self.recon_input = getattr(user_input, "recon")
        self.scan_input = getattr(user_input, "scan")
        self.output_after_every_phase = getattr(user_input, "output_after_every_phase")
        self.output_after_every_finding = getattr(
            user_input, "output_after_every_finding"
        )
