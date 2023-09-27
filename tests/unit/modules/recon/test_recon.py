from modules.recon.directory_bruteforce.directory_bruteforce import DirectoryBruteforce
from modules.recon.recon import Recon


class TestRecon:
    def test_recon_object_created_successfully(self, recon_whole_phase):
        assert isinstance(recon_whole_phase, Recon)

    def test_recon_object_runs_directory_bruteforce_module_successfully(
        self, mocker, recon_whole_phase
    ):
        mocker.patch.object(DirectoryBruteforce, "run")
        recon_whole_phase.run()
        assert DirectoryBruteforce.run.call_count == 1
