
import pytest

from modules.recon.directory_bruteforce.directory_bruteforce import DirectoryBruteforce
from modules.recon.recon import Recon


class TestRecon:
    test_url = "example.com"

    #  Recon object created successfully
    def test_recon_object_created_successfully(self):
        recon = Recon(directory_bruteforce_list_size="small", target=self.test_url)
        assert isinstance(recon, Recon)

    #  Recon object runs directory bruteforce module successfully
    def test_recon_object_runs_directory_bruteforce_module_successfully(self, mocker):
        recon = Recon(directory_bruteforce_list_size="small", target=self.test_url)
        mocker.patch.object(DirectoryBruteforce, 'run')
        recon.run()
        DirectoryBruteforce.run.assert_called_once()

