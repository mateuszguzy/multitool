import click

from modules.user_interface.cli.cli_interface_dataclasses import (
    DirectoryBruteforceInput,
    ReconInput,
    UserInput,
)
from utils.abstracts_classes import AbstractModule
from utils.utils import clean_and_validate_input_targets

ABBREVIATIONS_DICTIONARY = {
    "use_type": {
        "a": "all",
        "sp": "single_phase",
        "sm": "single_module",
    },
    "phase": {
        "r": "recon",
    },
    "module": {
        "dirb": "directory_bruteforce",
    },
    "wordlist_size": {
        "s": "small",
        "m": "medium",
        "t": "test",
    },
}


class CliInterface(AbstractModule):
    phase: str or None = None  # type: ignore
    module: str or None = None  # type: ignore
    use_type: str = ""
    targets: list = []
    directory_bruteforce_list_size: str = ""
    directory_bruteforce_input: dict = {}
    recon_phase_input: dict = {}
    output_after_every_phase: bool = True
    output_after_every_finding: bool = True
    user_input: dict = {}

    def __init__(self):
        super().__init__()

    def run(self):
        try:
            self.use_type_question()
        except KeyError:
            self.separator()
            click.echo("Please provide correct value.")
            self.use_type_question()

        if self.use_type != "all":
            if self.use_type == "single_phase":
                self.phase_question()
            else:
                self.module_question()

        self.targets_question()

        while not self.targets:
            self.targets_helper_question()

        if self.use_type == "all" or self.phase == "recon":
            self.recon_phase_questions()
        elif self.module == "directory_bruteforce":
            self.directory_bruteforce_questions()
            self.recon_phase_input = ReconInput(
                directory_bruteforce=self.directory_bruteforce_input
            ).__dict__

        self.output_after_every_phase_question()
        self.output_after_every_finding_question()
        self.separator()

        self.user_input = UserInput(
            use_type=self.use_type,
            phase=self.phase,
            module=self.module,
            targets=self.targets,
            recon=self.recon_phase_input,
            output_after_every_phase=self.output_after_every_phase,
            output_after_every_finding=self.output_after_every_finding,
        ).__dict__

    def use_type_question(self):
        self.separator()
        raw_input = click.prompt(
            text="Choose Multitool use type:\n - all [a]\n - single phase [sp]\n - single module [sm]:\n\n",
            type=click.Choice(["a", "sp", "sm"], case_sensitive=False),
            default="a",
        )
        self.use_type = self._translate_abbreviations(key="use_type", abbreviation=raw_input)

    def phase_question(self):
        self.separator()
        raw_input = click.prompt(
            "Choose Phase to execute:\n - recon [r]\n\n",
            type=click.Choice(["r"], case_sensitive=False),
            default="r",
        )
        self.phase = self._translate_abbreviations(key="phase", abbreviation=raw_input)

    def module_question(self):
        self.separator()
        raw_input = click.prompt(
            "Choose Module to execute:\n - directory bruteforce [dirb]\n\n",
            type=click.Choice(["dirb"], case_sensitive=False),
            default="dirb",
        )
        self.module = self._translate_abbreviations(key="module", abbreviation=raw_input)

    def targets_question(self):
        self.separator()
        targets_raw = click.prompt(
            "Provide targets as comma separated values:\n", type=str
        )
        self.targets = clean_and_validate_input_targets(targets_raw)

    def targets_helper_question(self):
        targets_raw = click.prompt(
            "Provide at least one target with correct format:\n www.example.com | example.com | example.com:port\n",
            type=str,
        )
        self.targets = clean_and_validate_input_targets(targets_raw)

    def recon_phase_questions(self):
        self.directory_bruteforce_questions()
        self.recon_phase_input = ReconInput(
            directory_bruteforce=self.directory_bruteforce_input
        ).__dict__

    def directory_bruteforce_questions(self):
        self.directory_bruteforce_list_size_question()
        self.directory_bruteforce_input = DirectoryBruteforceInput(
            list_size=self.directory_bruteforce_list_size
        ).__dict__

    def directory_bruteforce_list_size_question(self):
        self.separator()
        raw_input = click.prompt(
            "Choose size or bruteforce wordlist:\n - small [s]\n - medium [m]\n - test [t]\n\n",
            type=click.Choice(["s", "m", "t"], case_sensitive=False),
            default="s",
        )
        self.directory_bruteforce_list_size = self._translate_abbreviations(key="wordlist_size", abbreviation=raw_input.lower())

    def output_after_every_phase_question(self):
        self.separator()
        self.output_after_every_phase = click.prompt(
            "Show output after every phase?\n\n",
            type=bool,
            # TODO: after develop phase change to False
            default=True,
        )

    def output_after_every_finding_question(self):
        self.separator()
        self.output_after_every_finding = click.prompt(
            "Show output after every finding?\n\n",
            type=bool,
            # TODO: after develop phase change to False
            default=True,
        )

    @staticmethod
    def separator():
        return click.echo("-" * 20)

    @staticmethod
    def _translate_abbreviations(key: str, abbreviation: str) -> str:
        return ABBREVIATIONS_DICTIONARY[key][abbreviation.lower()]
