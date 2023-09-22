from unittest import mock

import pytest

from config.settings import WORDLISTS_DIR
from modules.recon.directory_bruteforce.directory_bruteforce import DirectoryBruteforce


class TestDirectoryBruteforce:
    test_url = "http://example.com"
    expected_wordlist = {"word1", "word2", "word3"}
    test_list_size = "small"

    def test_store_results(self, mocker):
        mocker.patch(
            "modules.recon.directory_bruteforce.directory_bruteforce.DirectoryBruteforce._read_wordlist",
        )
        mock_store_results = mocker.patch(
            "modules.recon.directory_bruteforce.directory_bruteforce.store_module_results_in_database"
        )
        mocker.patch(
            "modules.recon.directory_bruteforce.directory_bruteforce.convert_list_or_set_to_dict",
        )
        mocker.patch(
            "modules.recon.directory_bruteforce.directory_bruteforce.web_request",
        )

        directory_bruteforce = DirectoryBruteforce(self.test_url, self.test_list_size)
        directory_bruteforce.run()

        assert mock_store_results.call_count == 1

    def test_handle_nonexistent_wordlist_file(self):
        directory_bruteforce = DirectoryBruteforce(self.test_url, self.test_list_size)

        with mock.patch("builtins.open", side_effect=FileNotFoundError):
            with pytest.raises(FileNotFoundError):
                directory_bruteforce.run()

    def test_read_wordlist_successfully_converts_to_set(self):
        directory_bruteforce = DirectoryBruteforce(self.test_url, self.test_list_size)
        with mock.patch(
            "builtins.open", mock.mock_open(read_data="word1\nword2\nword3")
        ) as mocked_open:
            directory_bruteforce._read_wordlist()

            assert directory_bruteforce.wordlist == self.expected_wordlist
            mocked_open.assert_called_with(
                f"{WORDLISTS_DIR}/dir_bruteforce_small.txt", "r", encoding="utf-8"
            )

    def test_empty_wordlist_file(self):
        directory_bruteforce = DirectoryBruteforce(self.test_url, self.test_list_size)
        with mock.patch(
            "modules.recon.directory_bruteforce.directory_bruteforce.open", mock.mock_open(read_data="")
        ) as mocked_open:
            directory_bruteforce._read_wordlist()

            assert directory_bruteforce.wordlist is None
            mocked_open.assert_called_with(
                f"{WORDLISTS_DIR}/dir_bruteforce_small.txt", "r", encoding="utf-8"
            )
