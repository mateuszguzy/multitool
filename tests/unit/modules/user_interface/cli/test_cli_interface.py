import pytest

from modules.user_interface.cli.cli_interface import CliInterface
from utils.custom_dataclasses import (
    UserInput,
    DirectoryBruteforceInput,
    ReconInput,
    ScanInput,
    PortScanInput,
)


class TestCliInterface:
    test_url = "https://example.com"
    test_ports = {80}
    save_reusable_data_in_db_function_path = (
        "modules.user_interface.cli.cli_interface.CliInterface.save_reusable_data_in_db"
    )
    valid_targets_function_path = (
        "modules.user_interface.cli.cli_interface.CliInterface.valid_targets"
    )
    valid_ports_function_path = (
        "modules.user_interface.cli.cli_interface.CliInterface.valid_ports"
    )
    format_targets_as_urls_path = (
        "modules.user_interface.cli.cli_interface.CliInterface.format_targets_as_urls"
    )
    questionary_prompt_path = "modules.user_interface.cli.cli_interface.prompt"
    directory_bruteforce_expected_module = "recon|directory_bruteforce"
    port_scan_expected_module = "scan|port_scan"
    recon_phase_expected_modules = {directory_bruteforce_expected_module}
    scan_expected_modules = {port_scan_expected_module}
    run_all_expected_result = recon_phase_expected_modules | scan_expected_modules

    #  User selects 'all' use type and enters valid URLs as targets
    def test_all_use_type_valid_urls(self, mocker, cli_interface):
        """
        Test if CliInterface returns expected dictionary when user selects 'all' use type and enters valid URLs
        as targets
        """
        mocker.patch(
            self.save_reusable_data_in_db_function_path,
        )
        mocker.patch(self.format_targets_as_urls_path)
        mocker.patch(
            self.valid_targets_function_path,
            {self.test_url},
        )
        mocker.patch(
            self.valid_ports_function_path,
            self.test_ports,
        )
        mocker.patch(
            self.questionary_prompt_path,
            return_value={
                "use_type": "all",
                "targets": self.test_url,
                "directory_bruteforce_list_size": "small",
                "output_after_every_phase": True,
                "output_after_every_finding": True,
            },
        )
        result = cli_interface.run()

        assert result == UserInput(
            use_type="all",
            phase="",
            module=None,
            targets={self.test_url},
            recon=ReconInput(
                directory_bruteforce=DirectoryBruteforceInput(list_size="small")
            ),
            scan=ScanInput(port_scan=PortScanInput(ports=self.test_ports)),
            output_after_every_phase=True,
            output_after_every_finding=True,
        )

    def test_single_phase_recon_valid_urls(self, mocker, cli_interface):
        """
        Test if CliInterface returns expected dictionary when user selects 'single_phase' use type,
        'recon' phase and enters valid URLs as targets
        """
        mocker.patch(
            self.save_reusable_data_in_db_function_path,
        )
        mocker.patch(self.format_targets_as_urls_path)
        mocker.patch(
            self.valid_targets_function_path,
            {self.test_url},
        )
        mocker.patch(
            self.questionary_prompt_path,
            return_value={
                "use_type": "single_phase",
                "targets": self.test_url,
                "phase": "recon",
                "directory_bruteforce_list_size": "small",
                "output_after_every_phase": True,
                "output_after_every_finding": True,
            },
        )

        result = cli_interface.run()

        assert result == UserInput(
            use_type="single_phase",
            phase="recon",
            module=None,
            targets={self.test_url},
            recon=ReconInput(
                directory_bruteforce=DirectoryBruteforceInput(list_size="small")
            ),
            scan=ScanInput(PortScanInput(ports=set())),
            output_after_every_phase=True,
            output_after_every_finding=True,
        )

    def test_single_phase_scan_valid_urls(self, mocker, cli_interface):
        """
        Test if CliInterface returns expected dictionary when user selects 'single_phase' use type,
        'scan' phase and enters valid URLs as targets
        """
        mocker.patch(
            self.save_reusable_data_in_db_function_path,
        )
        mocker.patch(self.format_targets_as_urls_path)
        mocker.patch(
            self.valid_targets_function_path,
            {self.test_url},
        )
        mocker.patch(
            self.valid_ports_function_path,
            self.test_ports,
        )
        mocker.patch(
            self.questionary_prompt_path,
            return_value={
                "use_type": "single_phase",
                "targets": self.test_url,
                "phase": "scan",
                "ports_to_scan": "80",
                "output_after_every_phase": True,
                "output_after_every_finding": True,
            },
        )

        result = cli_interface.run()

        assert result == UserInput(
            use_type="single_phase",
            phase="scan",
            module=None,
            targets={self.test_url},
            recon=ReconInput(
                directory_bruteforce=DirectoryBruteforceInput(list_size=None)
            ),
            scan=ScanInput(PortScanInput(ports=self.test_ports)),
            output_after_every_phase=True,
            output_after_every_finding=True,
        )

    def test_single_module_directory_bruteforce_valid_urls(self, mocker, cli_interface):
        """
        Test if CliInterface returns expected dictionary when user selects 'single_module' use type,
        'directory_bruteforce' module and enters valid URLs as targets
        """
        mocker.patch(
            self.save_reusable_data_in_db_function_path,
        )
        mocker.patch(self.format_targets_as_urls_path)
        mocker.patch(
            self.valid_targets_function_path,
            {self.test_url},
        )
        mocker.patch(
            self.questionary_prompt_path,
            return_value={
                "use_type": "single_module",
                "targets": self.test_url,
                "phase": "recon",
                "module": "directory_bruteforce",
                "directory_bruteforce_list_size": "small",
                "output_after_every_phase": True,
                "output_after_every_finding": True,
            },
        )

        result = cli_interface.run()

        assert result == UserInput(
            use_type="single_module",
            phase="recon",
            module="directory_bruteforce",
            targets={self.test_url},
            recon=ReconInput(
                directory_bruteforce=DirectoryBruteforceInput(list_size="small")
            ),
            scan=ScanInput(PortScanInput(ports=set())),
            output_after_every_phase=True,
            output_after_every_finding=True,
        )

    def test_single_module_port_scan_valid_urls(self, mocker, cli_interface):
        """
        Test if CliInterface returns expected dictionary when user selects 'single_module' use type,
        'port_scan' module and enters valid URLs as targets
        """
        mocker.patch(
            self.save_reusable_data_in_db_function_path,
        )
        mocker.patch(self.format_targets_as_urls_path)
        mocker.patch(
            self.valid_targets_function_path,
            {self.test_url},
        )
        mocker.patch(
            self.valid_ports_function_path,
            self.test_ports,
        )
        mocker.patch(
            self.questionary_prompt_path,
            return_value={
                "use_type": "single_module",
                "targets": self.test_url,
                "phase": "scan",
                "module": "port_scan",
                "ports_to_scan": "80",
                "output_after_every_phase": True,
                "output_after_every_finding": True,
            },
        )

        result = cli_interface.run()

        assert result == UserInput(
            use_type="single_module",
            phase="scan",
            module="port_scan",
            targets={self.test_url},
            recon=ReconInput(
                directory_bruteforce=DirectoryBruteforceInput(list_size=None)
            ),
            scan=ScanInput(PortScanInput(ports=self.test_ports)),
            output_after_every_phase=True,
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
