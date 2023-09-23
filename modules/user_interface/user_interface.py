from modules.user_interface.cli.cli_interface import CliInterface
from utils.abstracts_classes import AbstractModule


class UserInterface(AbstractModule):
    def __init__(self):
        super().__init__()

    def run(self):
        cli_interface = CliInterface()
        return cli_interface.run()
