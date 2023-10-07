from utils.custom_dataclasses import DirectoryBruteforceInput, ReconInput, ScanInput, PortScanInput


class TestSteeringModule:
    testing_targets = {"http://dvwa:80/"}
    expected_recon_input = ReconInput(
        directory_bruteforce=DirectoryBruteforceInput(list_size="small")
    )
    expected_empty_recon_input = ReconInput(
        directory_bruteforce=DirectoryBruteforceInput(list_size=None)
    )
    expected_scan_input = ScanInput(
        port_scan=PortScanInput(ports={80})
    )
    expected_empty_scan_input = ScanInput(
        port_scan=PortScanInput(ports=set())
    )

    def test_assign_class_attributes_for_single_module_directory_bruteforce(
        self,
        steering_module_for_single_module_directory_bruteforce,
    ):
        sm = steering_module_for_single_module_directory_bruteforce

        assert sm.use_type == "single_module"
        assert sm.phase is None
        assert sm.module == "directory_bruteforce"
        assert sm.targets == self.testing_targets
        assert sm.recon_input == self.expected_recon_input
        assert sm.scan_input == self.expected_empty_scan_input
        assert sm.output_after_every_phase is False
        assert sm.output_after_every_finding is True

    def test_assign_class_attributes_for_single_module_port_scan(
        self,
        steering_module_for_single_module_port_scan,
    ):
        sm = steering_module_for_single_module_port_scan

        assert sm.use_type == "single_module"
        assert sm.phase is None
        assert sm.module == "port_scan"
        assert sm.targets == self.testing_targets
        assert sm.recon_input == self.expected_empty_recon_input
        assert sm.scan_input == self.expected_scan_input
        assert sm.output_after_every_phase is False
        assert sm.output_after_every_finding is True

    def test_assign_class_attributes_for_single_phase_recon(
        self,
        steering_module_for_single_phase_recon,
    ):
        sm = steering_module_for_single_phase_recon

        assert sm.use_type == "single_phase"
        assert sm.phase == "recon"
        assert sm.module is None
        assert sm.targets == self.testing_targets
        assert sm.recon_input == self.expected_recon_input
        assert sm.scan_input == self.expected_empty_scan_input
        assert sm.output_after_every_phase is False
        assert sm.output_after_every_finding is True

    def test_assign_class_attributes_for_single_phase_scan(
        self,
        steering_module_for_single_phase_scan,
    ):
        sm = steering_module_for_single_phase_scan

        assert sm.use_type == "single_phase"
        assert sm.phase == "scan"
        assert sm.module is None
        assert sm.targets == self.testing_targets
        assert sm.recon_input == self.expected_empty_recon_input
        assert sm.scan_input == self.expected_scan_input
        assert sm.output_after_every_phase is False
        assert sm.output_after_every_finding is True

    def test_assign_class_attributes_for_all(self, steering_module_for_all):
        sm = steering_module_for_all

        assert sm.use_type == "all"
        assert sm.phase is None
        assert sm.module is None
        assert sm.targets == self.testing_targets
        assert sm.recon_input == self.expected_recon_input
        assert sm.scan_input == self.expected_scan_input
        assert sm.output_after_every_phase is False
        assert sm.output_after_every_finding is True
