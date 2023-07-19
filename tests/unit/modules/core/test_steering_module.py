class TestSteeringModule:
    testing_targets = ["http://dvwa:80/"]

    def test_assign_class_attributes_for_single_module_directory_bruteforce(
        self,
        steering_module_for_single_module_directory_bruteforce,
    ):
        sm = steering_module_for_single_module_directory_bruteforce

        assert sm.use_type == "single_module"
        assert sm.phase is None
        assert sm.module == "directory_bruteforce"
        assert sm.targets == self.testing_targets
        assert sm.directory_bruteforce_list_size == "small"
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
        assert sm.directory_bruteforce_list_size == "small"
        assert sm.output_after_every_phase is False
        assert sm.output_after_every_finding is True

    def test_assign_class_attributes_for_all(self, steering_module_for_all):
        sm = steering_module_for_all

        assert sm.use_type == "all"
        assert sm.phase is None
        assert sm.module is None
        assert sm.targets == self.testing_targets
        assert sm.directory_bruteforce_list_size == "small"
        assert sm.output_after_every_phase is False
        assert sm.output_after_every_finding is True
