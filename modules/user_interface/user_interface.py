from modules.user_interface.cli.cli_interface import CliInterface
from utils.abstracts_classes import AbstractModule


class UserInterface(AbstractModule):
    def __init__(self):
        super().__init__()
        self.cli_interface = CliInterface()

    def run(self):
        self.cli_interface.run()
