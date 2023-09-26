from modules.recon.directory_bruteforce.directory_bruteforce import DirectoryBruteforce
from modules.recon.recon import Recon


class TestRecon:
    def test_recon_object_created_successfully(self, recon):
        assert isinstance(recon, Recon)

    def test_recon_object_runs_directory_bruteforce_module_successfully(
        self, mocker, recon
    ):
        mocker.patch.object(DirectoryBruteforce, "run")
        recon.run()
        DirectoryBruteforce.run.assert_called_once()
