class TestSteeringModule:
    testing_targets = {"http://dvwa:80/"}

    def test_assign_class_attributes_for_single_module_directory_bruteforce(
        self,
        steering_module_for_single_module_directory_bruteforce,
        test_recon_input,
        test_scan_input_empty,
    ):
        sm = steering_module_for_single_module_directory_bruteforce

        assert sm.use_type == "single_module"
        assert sm.phase == "recon"
        assert sm.module == "directory_bruteforce"
        assert sm.targets == self.testing_targets
        assert sm.recon_input == test_recon_input
        assert sm.scan_input == test_scan_input_empty
        assert sm.output_after_every_phase is False
        assert sm.output_after_every_finding is True

    def test_assign_class_attributes_for_single_module_port_scan(
        self,
        steering_module_for_single_module_port_scan,
        test_recon_input_empty,
        test_scan_input,
    ):
        sm = steering_module_for_single_module_port_scan

        assert sm.use_type == "single_module"
        assert sm.phase == "scan"
        assert sm.module == "port_scan"
        assert sm.targets == self.testing_targets
        assert sm.recon_input == test_recon_input_empty
        assert sm.scan_input == test_scan_input
        assert sm.output_after_every_phase is False
        assert sm.output_after_every_finding is True

    def test_assign_class_attributes_for_single_phase_recon(
        self,
        steering_module_for_single_phase_recon,
        test_recon_input,
        test_scan_input_empty,
    ):
        sm = steering_module_for_single_phase_recon

        assert sm.use_type == "single_phase"
        assert sm.phase == "recon"
        assert sm.module is None
        assert sm.targets == self.testing_targets
        assert sm.recon_input == test_recon_input
        assert sm.scan_input == test_scan_input_empty
        assert sm.output_after_every_phase is False
        assert sm.output_after_every_finding is True

    def test_assign_class_attributes_for_single_phase_scan(
        self,
        steering_module_for_single_phase_scan,
        test_recon_input_empty,
        test_scan_input,
    ):
        sm = steering_module_for_single_phase_scan

        assert sm.use_type == "single_phase"
        assert sm.phase == "scan"
        assert sm.module is None
        assert sm.targets == self.testing_targets
        assert sm.recon_input == test_recon_input_empty
        assert sm.scan_input == test_scan_input
        assert sm.output_after_every_phase is False
        assert sm.output_after_every_finding is True

    def test_assign_class_attributes_for_all(
        self, steering_module_for_all, test_recon_input, test_scan_input
    ):
        sm = steering_module_for_all

        assert sm.use_type == "all"
        assert sm.phase == ""
        assert sm.module is None
        assert sm.targets == self.testing_targets
        assert sm.recon_input == test_recon_input
        assert sm.scan_input == test_scan_input
        assert sm.output_after_every_phase is False
        assert sm.output_after_every_finding is True
