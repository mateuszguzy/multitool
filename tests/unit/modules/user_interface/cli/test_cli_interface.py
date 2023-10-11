import pytest

from modules.user_interface.cli.cli_interface import CliInterface
from tests.conftest import (
    MOCK_USER_INPUT_ALL,
    convert_json_input_to_dict,
    test_scan_input,
    MOCK_USER_INPUT_SINGLE_PHASE_RECON,
    MOCK_USER_INPUT_SINGLE_PHASE_SCAN,
    MOCK_USER_INPUT_SINGLE_MODULE_DIRECTORY_BRUTEFORCE,
    MOCK_USER_INPUT_SINGLE_MODULE_PORT_SCAN,
)
from utils.custom_dataclasses import (
    UserInput,
)


class TestCliInterface:
    test_url = "https://example.com"
    test_ports = {80, 443}
    module_path = "modules.user_interface.cli.cli_interface.CliInterface"
    save_reusable_data_in_db_function_path = f"{module_path}.save_reusable_data_in_db"
    valid_targets_function_path = f"{module_path}.valid_targets"
    valid_ports_function_path = f"{module_path}.valid_ports"
    format_targets_as_urls_path = f"{module_path}.format_targets_as_urls"
    aggregate_results_function_path = f"{module_path}.aggregate_phase_specific_data"
    extract_used_phases_and_modules_data_from_user_input_path = (
        f"{module_path}.extract_used_phases_and_modules_data_from_user_input"
    )
    questionary_prompt_path = "modules.user_interface.cli.cli_interface.prompt"
    directory_bruteforce_expected_module = "recon|directory_bruteforce"
    port_scan_expected_module = "scan|port_scan"
    recon_phase_expected_modules = {directory_bruteforce_expected_module}
    scan_expected_modules = {port_scan_expected_module}
    run_all_expected_result = recon_phase_expected_modules | scan_expected_modules

    def test_all_use_type_valid_urls(
        self, mocker, cli_interface, test_recon_input, test_scan_input
    ):
        """
        Test if CliInterface returns expected dictionary when user selects 'all' use type and enters valid URLs
        as targets
        """
        mocker.patch(
            self.questionary_prompt_path,
            return_value=convert_json_input_to_dict(MOCK_USER_INPUT_ALL),
        )
        mocker.patch(
            self.aggregate_results_function_path,
            return_value=(test_recon_input, test_scan_input),
        )
        mocker.patch(
            self.extract_used_phases_and_modules_data_from_user_input_path,
        )
        mocker.patch(self.format_targets_as_urls_path)
        mocker.patch(
            self.save_reusable_data_in_db_function_path,
        )
        mocker.patch(
            self.valid_targets_function_path,
            {self.test_url},
        )
        mocker.patch(
            self.valid_ports_function_path,
            self.test_ports,
        )

        result = cli_interface.run()

        assert result == UserInput(
            use_type="all",
            phase="",
            module=None,
            targets={self.test_url},
            recon=test_recon_input,
            scan=test_scan_input,
            output_after_every_phase=False,
            output_after_every_finding=True,
        )

    def test_single_phase_recon_valid_urls(
        self, mocker, cli_interface, test_recon_input, test_scan_input
    ):
        """
        Test if CliInterface returns expected dictionary when user selects 'single_phase' use type,
        'recon' phase and enters valid URLs as targets
        """
        mocker.patch(
            self.questionary_prompt_path,
            return_value=convert_json_input_to_dict(MOCK_USER_INPUT_SINGLE_PHASE_RECON),
        )
        mocker.patch(
            self.aggregate_results_function_path,
            return_value=(test_recon_input, test_scan_input),
        )
        mocker.patch(
            self.extract_used_phases_and_modules_data_from_user_input_path,
        )
        mocker.patch(self.format_targets_as_urls_path)
        mocker.patch(
            self.save_reusable_data_in_db_function_path,
        )
        mocker.patch(
            self.valid_targets_function_path,
            {self.test_url},
        )

        result = cli_interface.run()

        assert result == UserInput(
            use_type="single_phase",
            phase="recon",
            module=None,
            targets={self.test_url},
            recon=test_recon_input,
            scan=test_scan_input,
            output_after_every_phase=False,
            output_after_every_finding=True,
        )

    def test_single_phase_scan_valid_urls(
        self, mocker, cli_interface, test_recon_input, test_scan_input
    ):
        """
        Test if CliInterface returns expected dictionary when user selects 'single_phase' use type,
        'scan' phase and enters valid URLs as targets
        """
        mocker.patch(
            self.questionary_prompt_path,
            return_value=convert_json_input_to_dict(MOCK_USER_INPUT_SINGLE_PHASE_SCAN),
        )
        mocker.patch(
            self.aggregate_results_function_path,
            return_value=(test_recon_input, test_scan_input),
        )
        mocker.patch(
            self.extract_used_phases_and_modules_data_from_user_input_path,
        )
        mocker.patch(self.format_targets_as_urls_path)
        mocker.patch(
            self.save_reusable_data_in_db_function_path,
        )
        mocker.patch(
            self.valid_targets_function_path,
            {self.test_url},
        )

        result = cli_interface.run()

        assert result == UserInput(
            use_type="single_phase",
            phase="scan",
            module=None,
            targets={self.test_url},
            recon=test_recon_input,
            scan=test_scan_input,
            output_after_every_phase=False,
            output_after_every_finding=True,
        )

    def test_single_module_directory_bruteforce_valid_urls(
        self, mocker, cli_interface, test_recon_input, test_scan_input
    ):
        """
        Test if CliInterface returns expected dictionary when user selects 'single_module' use type,
        'directory_bruteforce' module and enters valid URLs as targets
        """
        mocker.patch(
            self.questionary_prompt_path,
            return_value=convert_json_input_to_dict(
                MOCK_USER_INPUT_SINGLE_MODULE_DIRECTORY_BRUTEFORCE
            ),
        )
        mocker.patch(
            self.aggregate_results_function_path,
            return_value=(test_recon_input, test_scan_input),
        )
        mocker.patch(
            self.extract_used_phases_and_modules_data_from_user_input_path,
        )
        mocker.patch(self.format_targets_as_urls_path)
        mocker.patch(
            self.save_reusable_data_in_db_function_path,
        )
        mocker.patch(
            self.valid_targets_function_path,
            {self.test_url},
        )

        result = cli_interface.run()

        assert result == UserInput(
            use_type="single_module",
            phase="recon",
            module="directory_bruteforce",
            targets={self.test_url},
            recon=test_recon_input,
            scan=test_scan_input,
            output_after_every_phase=False,
            output_after_every_finding=True,
        )

    def test_single_module_port_scan_valid_urls(
        self, mocker, cli_interface, test_recon_input, test_scan_input
    ):
        """
        Test if CliInterface returns expected dictionary when user selects 'single_module' use type,
        'port_scan' module and enters valid URLs as targets
        """
        mocker.patch(
            self.questionary_prompt_path,
            return_value=convert_json_input_to_dict(
                MOCK_USER_INPUT_SINGLE_MODULE_PORT_SCAN
            ),
        )
        mocker.patch(
            self.aggregate_results_function_path,
            return_value=(test_recon_input, test_scan_input),
        )
        mocker.patch(
            self.extract_used_phases_and_modules_data_from_user_input_path,
        )
        mocker.patch(self.format_targets_as_urls_path)
        mocker.patch(
            self.save_reusable_data_in_db_function_path,
        )
        mocker.patch(
            self.valid_targets_function_path,
            {self.test_url},
        )

        result = cli_interface.run()

        assert result == UserInput(
            use_type="single_module",
            phase="scan",
            module="port_scan",
            targets={self.test_url},
            recon=test_recon_input,
            scan=test_scan_input,
            output_after_every_phase=False,
            output_after_every_finding=True,
        )

    def test_returns_set_of_modules_when_use_type_is_all(self):
        """
        Test if CliInterface returns expected set of modules from all the phases when user selects 'all' use type
        """
        answers = {"use_type": "all"}
        result = CliInterface.extract_used_phases_and_modules_data_from_user_input(
            answers
        )

        assert result == self.run_all_expected_result

    @pytest.mark.parametrize(
        "phase, expected_modules",
        [
            ("recon", recon_phase_expected_modules),
            ("scan", scan_expected_modules),
        ],
    )
    def test_returns_set_of_modules_when_use_type_is_single_phase_and_phase_is_valid(
        self, phase, expected_modules
    ):
        """
        Test if CliInterface returns expected set of ALL modules from a phase when user selects 'single_phase' use type
        """
        answers = {"use_type": "single_phase", "phase": phase}
        result = CliInterface.extract_used_phases_and_modules_data_from_user_input(
            answers
        )

        assert result == expected_modules

    @pytest.mark.parametrize(
        "phase, module, expected_modules",
        [
            ("recon", "directory_bruteforce", {directory_bruteforce_expected_module}),
            ("scan", "port_scan", {port_scan_expected_module}),
        ],
    )
    def test_returns_set_of_modules_when_use_type_is_single_module_dirb_and_module_is_valid(
        self, phase, module, expected_modules
    ):
        """
        Test if CliInterface returns expected set of modules when user selects 'single_module' use type
        """
        answers = {
            "use_type": "single_module",
            "phase": phase,
            "module": module,
        }
        result = CliInterface.extract_used_phases_and_modules_data_from_user_input(
            answers
        )

        assert result == expected_modules
