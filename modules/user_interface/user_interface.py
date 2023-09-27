from modules.user_interface.cli.cli_interface import CliInterface
from utils.abstracts_classes import AbstractModule
from utils.custom_dataclasses import UserInput


class UserInterface(AbstractModule):
    def __init__(self):
        super().__init__()

    def run(self) -> UserInput:
        cli_interface = CliInterface()
        return cli_interface.run()
