from typing import Set

from config.settings import AVAILABLE_FUNCTIONALITY, RECON_PHASE_MODULES
from modules.recon.recon import Recon
from utils.custom_dataclasses import ReconInput, UserInput
from utils.abstracts_classes import AbstractModule


class SteeringModule(AbstractModule):
    use_type: str = str()
    phase: str = str()
    module: str = str()
    targets: Set[str] = set()
    recon_input: ReconInput
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
            self._run_module(module=self.module)

        else:
            raise ValueError(f"Invalid use_type: {self.use_type}")

    # --- PHASES
    def _run_recon(self) -> None:
        """
        Function launching recon phase.
        """
        for target in self.targets:
            recon_phase = Recon(
                recon_input=self.recon_input,
                target=target,
                single_module=self.module if self.module else None,
            )
            recon_phase.run()

    def _run_scan(self):
        """
        Function launching scan phase.
        """
        pass

    # --- MAIN
    def _run_all(self) -> None:
        """
        Run all the functionalities that app holds.
        """
        for phase in AVAILABLE_FUNCTIONALITY:
            self._run_phase(phase=phase)

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

    def _run_module(self, module: str) -> None:
        """
        Run single module of any hacking process phase.
        :param module: e.g. directory_bruteforce / port_scan / lfi_rfi
        """
        if module in RECON_PHASE_MODULES:
            self._run_recon()
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
        self.targets = getattr(user_input, "targets")
        self.recon_input = getattr(user_input, "recon")
        self.output_after_every_phase = getattr(user_input, "output_after_every_phase")
        self.output_after_every_finding = getattr(user_input, "output_after_every_finding")
