from modules.user_interface.cli.cli_interface import CliInterface
from utils.custom_dataclasses import UserInput, DirectoryBruteforceInput, ReconInput


class TestCliInterface:
    test_url = "https://example.com"
    save_reusable_data_in_db_function_path = (
        "modules.user_interface.cli.cli_interface.CliInterface.save_reusable_data_in_db"
    )
    valid_targets_function_path = (
        "modules.user_interface.cli.cli_interface.CliInterface.valid_targets"
    )
    questionary_prompt_path = "modules.user_interface.cli.cli_interface.prompt"
    expected_result = {"recon|directory_bruteforce"}

    #  User selects 'all' use type and enters valid URLs as targets
    def test_all_use_type_valid_urls(self, mocker):
        """
        Test if CliInterface returns expected dictionary when user selects 'all' use type and enters valid URLs
        as targets
        """
        mocker.patch(
            self.save_reusable_data_in_db_function_path,
        )
        mocker.patch(
            self.valid_targets_function_path,
            {self.test_url},
        )
        mocker.patch(
            self.questionary_prompt_path,
            return_value={
                "use_type": "all",
                "directory_bruteforce_list_size": "small",
                "output_after_every_phase": True,
                "output_after_every_finding": True,
            },
        )
        cli_interface = CliInterface()
        result = cli_interface.run()

        assert result == UserInput(
            use_type="all",
            phase="",
            module=None,
            targets={self.test_url},
            recon=ReconInput(
                directory_bruteforce=DirectoryBruteforceInput(list_size="small")
            ),
            output_after_every_phase=True,
            output_after_every_finding=True,
        )

    def test_single_phase_recon_valid_urls(self, mocker):
        """
        Test if CliInterface returns expected dictionary when user selects 'single_phase' use type,
        'recon' phase and enters valid URLs as targets
        """
        mocker.patch(
            self.save_reusable_data_in_db_function_path,
        )
        mocker.patch(
            self.valid_targets_function_path,
            {self.test_url},
        )
        mocker.patch(
            self.questionary_prompt_path,
            return_value={
                "use_type": "single_phase",
                "phase": "recon",
                "directory_bruteforce_list_size": "small",
                "output_after_every_phase": True,
                "output_after_every_finding": True,
            },
        )

        cli_interface = CliInterface()
        result = cli_interface.run()

        assert result == UserInput(
            use_type="single_phase",
            phase="recon",
            module=None,
            targets={self.test_url},
            recon=ReconInput(
                directory_bruteforce=DirectoryBruteforceInput(list_size="small")
            ),
            output_after_every_phase=True,
            output_after_every_finding=True,
        )

    def test_single_module_directory_bruteforce_valid_urls(self, mocker):
        """
        Test if CliInterface returns expected dictionary when user selects 'single_module' use type,
        'directory_bruteforce' module and enters valid URLs as targets
        """
        mocker.patch(
            self.save_reusable_data_in_db_function_path,
        )
        mocker.patch(
            self.valid_targets_function_path,
            {self.test_url},
        )
        mocker.patch(
            self.questionary_prompt_path,
            return_value={
                "use_type": "single_module",
                "phase": "recon",
                "module": "directory_bruteforce",
                "directory_bruteforce_list_size": "small",
                "output_after_every_phase": True,
                "output_after_every_finding": True,
            },
        )

        cli_interface = CliInterface()
        result = cli_interface.run()

        assert result == UserInput(
            use_type="single_module",
            phase="recon",
            module="directory_bruteforce",
            targets={self.test_url},
            recon=ReconInput(
                directory_bruteforce=DirectoryBruteforceInput(list_size="small")
            ),
            output_after_every_phase=True,
            output_after_every_finding=True,
        )

    def test_returns_set_of_modules_when_use_type_is_all(self):
        """
        Test if CliInterface returns expected set of modules when user selects 'all' use type
        """
        answers = {"use_type": "all"}
        expected_modules = self.expected_result

        result = CliInterface.extract_used_phases_and_modules_data_from_user_input(
            answers
        )

        assert result == expected_modules

    def test_returns_set_of_modules_when_use_type_is_single_phase_and_phase_is_valid(
        self,
    ):
        """
        Test if CliInterface returns expected set of modules when user selects 'single_phase' use type
        and 'recon' phase
        """
        answers = {"use_type": "single_phase", "phase": "recon"}
        expected_modules = self.expected_result

        result = CliInterface.extract_used_phases_and_modules_data_from_user_input(
            answers
        )

        assert result == expected_modules

    def test_returns_set_of_modules_when_use_type_is_single_module_and_module_is_valid(
        self,
    ):
        """
        Test if CliInterface returns expected set of modules when user selects 'single_module' use type
        and 'directory_bruteforce' module
        """
        answers = {
            "use_type": "single_module",
            "phase": "recon",
            "module": "directory_bruteforce",
        }
        expected_module = self.expected_result

        result = CliInterface.extract_used_phases_and_modules_data_from_user_input(
            answers
        )

        assert result == expected_module
