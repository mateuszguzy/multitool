from modules.user_interface.cli.cli_interface import CliInterface
from utils.abstracts_classes import AbstractModule


class UserInterface(AbstractModule):
    cli_interface: CliInterface = CliInterface()

    def __init__(self):
        super().__init__()

    def run(self):
        self.cli_interface.run()
