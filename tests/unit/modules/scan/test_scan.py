from modules.scan.port_scan.port_scan import PortScan
from modules.scan.scan import Scan


class TestScan:
    def test_scan_object_created_successfully(self, test_scan_whole_phase):
        assert isinstance(test_scan_whole_phase, Scan)

    def test_scan_object_runs_directory_bruteforce_module_successfully(
        self, mocker, test_scan_whole_phase
    ):
        mocker.patch.object(PortScan, "run")
        test_scan_whole_phase.run()
        assert PortScan.run.call_count == 1
