import pytest

from tests.conftest import TEST_PORTS, TEST_TARGETS_SET
from utils.custom_dataclasses import (
    DirectoryBruteforceInput,
    ReconInput,
    ScanInput,
    PortScanInput,
    ZapSpiderInput,
)


class TestSteeringModule:
    testing_targets = TEST_TARGETS_SET
    test_ports = TEST_PORTS
    # couldn't use this as a fixture ¯\_(ツ)_/¯
    test_recon_input = ReconInput(
        ZapSpiderInput(as_user=False, enhanced=False),
        DirectoryBruteforceInput(list_size="small", recursive=False),
    )
    test_single_module_directory_bruteforce_input = ReconInput(
        ZapSpiderInput(as_user=None, enhanced=None),
        DirectoryBruteforceInput(list_size="small", recursive=False),
    )
    test_single_module_zap_spider_input = ReconInput(
        ZapSpiderInput(as_user=False, enhanced=False),
        DirectoryBruteforceInput(list_size=None, recursive=None),
    )
    test_recon_input_empty = ReconInput(
        ZapSpiderInput(as_user=None, enhanced=None),
        DirectoryBruteforceInput(list_size=None, recursive=None),
    )
    test_scan_input = ScanInput(
        PortScanInput(port_scan_type="custom", ports=test_ports)  # type: ignore
    )
    test_scan_input_empty = ScanInput(
        PortScanInput(port_scan_type="custom", ports=set())
    )

    @pytest.mark.parametrize(
        "steering_module_with_input, expected_output",
        [
            (
                pytest.lazy_fixture("steering_module_for_single_module_zap_spider_fixture"),  # type: ignore
                {
                    "use_type": "single_module",
                    "phase": "recon",
                    "module": "zap_spider",
                    "targets": testing_targets,
                    "context_file_name": None,
                    "include_targets": None,
                    "exclude_targets": None,
                    "recon": test_single_module_zap_spider_input,
                    "scan": test_scan_input_empty,
                    "output_after_every_finding": True,
                },
            ),
            (
                pytest.lazy_fixture("steering_module_for_single_module_directory_bruteforce_fixture"),  # type: ignore
                {
                    "use_type": "single_module",
                    "phase": "recon",
                    "module": "directory_bruteforce",
                    "targets": testing_targets,
                    "context_file_name": None,
                    "include_targets": None,
                    "exclude_targets": None,
                    "recon": test_single_module_directory_bruteforce_input,
                    "scan": test_scan_input_empty,
                    "output_after_every_finding": True,
                },
            ),
            (
                pytest.lazy_fixture("steering_module_for_single_module_port_scan_fixture"),  # type: ignore
                {
                    "use_type": "single_module",
                    "phase": "scan",
                    "module": "port_scan",
                    "targets": testing_targets,
                    "context_file_name": None,
                    "include_targets": None,
                    "exclude_targets": None,
                    "recon": test_recon_input_empty,
                    "scan": test_scan_input,
                    "output_after_every_finding": True,
                },
            ),
            (
                pytest.lazy_fixture("steering_module_for_single_phase_recon_fixture"),  # type: ignore
                {
                    "use_type": "single_phase",
                    "phase": "recon",
                    "module": None,
                    "targets": testing_targets,
                    "context_file_name": None,
                    "include_targets": None,
                    "exclude_targets": None,
                    "recon": test_recon_input,
                    "scan": test_scan_input_empty,
                    "output_after_every_finding": True,
                },
            ),
            (
                pytest.lazy_fixture("steering_module_for_single_phase_scan_fixture"),  # type: ignore
                {
                    "use_type": "single_phase",
                    "phase": "scan",
                    "module": None,
                    "targets": testing_targets,
                    "context_file_name": None,
                    "include_targets": None,
                    "exclude_targets": None,
                    "recon": test_recon_input_empty,
                    "scan": test_scan_input,
                    "output_after_every_finding": True,
                },
            ),
            (
                pytest.lazy_fixture("steering_module_for_all_fixture"),  # type: ignore
                {
                    "use_type": "all",
                    "phase": "",
                    "module": None,
                    "targets": testing_targets,
                    "context_file_name": None,
                    "include_targets": None,
                    "exclude_targets": None,
                    "recon": test_recon_input,
                    "scan": test_scan_input,
                    "output_after_every_finding": True,
                },
            ),
        ],
    )
    def test_assign_class_attributes_for_single_module_directory_bruteforce(
        self,
        steering_module_with_input,
        expected_output,
    ):
        sm = steering_module_with_input
        assert sm.use_type == expected_output["use_type"]
        assert sm.phase == expected_output["phase"]
        assert sm.module == expected_output["module"]
        assert sm.targets == expected_output["targets"]
        assert sm.context_file_name == expected_output["context_file_name"]
        assert sm.include_targets == expected_output["include_targets"]
        assert sm.exclude_targets == expected_output["exclude_targets"]
        assert sm.recon_input == expected_output["recon"]
        assert sm.scan_input == expected_output["scan"]
        assert (
            sm.output_after_every_finding
            == expected_output["output_after_every_finding"]
        )
