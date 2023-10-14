from unittest import mock

import celery  # type: ignore
import pytest

from config.settings import WORDLISTS_DIR
from tests.conftest import TEST_TARGET


class TestDirectoryBruteforce:
    test_target = TEST_TARGET
    expected_wordlist = {"word1", "word2", "word3"}
    module_name = "modules.recon.directory_bruteforce.directory_bruteforce"

    def test_read_wordlist(self, mocker, directory_bruteforce, mock_open_with_data):
        directory_bruteforce._read_wordlist()

        assert mock_open_with_data.call_count == 1
        assert mock_open_with_data.call_args == mocker.call(
            f"{WORDLISTS_DIR}/dir_bruteforce_small.txt", "r", encoding="utf-8"
        )

    def test_run_tasks_successfully(
        self,
        mocker,
        directory_bruteforce,
        mock_celery_group,
        mock_open_with_data,
        mock_web_request_task,
    ):
        """
        Test all calls for all words are made
        """
        mocker.patch(f"{self.module_name}.directory_bruteforce_web_request", mock_web_request_task)
        mocker.patch.object(celery, "group", mock_celery_group)

        mocker.patch(f"{self.module_name}.convert_list_or_set_to_dict")
        mocker.patch(f"{self.module_name}.store_module_results_in_database")

        directory_bruteforce._run_with_celery()

        assert mock_web_request_task.s.call_count == len(self.expected_wordlist)
        for call_arg in mock_web_request_task.s.call_args_list:
            assert call_arg in [
                mock.call(
                    request_method="GET",
                    target=self.test_target,
                    path=word,
                    module=self.module_name,
                    allow_redirects=False,
                )
                for word in self.expected_wordlist
            ]

    def test_handle_nonexistent_wordlist_file(
        self, directory_bruteforce, mock_open_with_file_not_found_error
    ):
        with pytest.raises(FileNotFoundError):
            directory_bruteforce._run_with_celery()

    def test_read_wordlist_successfully_converts_to_set(
        self, mocker, directory_bruteforce, mock_open_with_data
    ):
        directory_bruteforce._read_wordlist()

        assert directory_bruteforce.wordlist == self.expected_wordlist
        assert mock_open_with_data.call_args == mocker.call(
            f"{WORDLISTS_DIR}/dir_bruteforce_small.txt", "r", encoding="utf-8"
        )

    def test_empty_wordlist_file(
        self, mocker, directory_bruteforce, mock_open_without_data
    ):
        directory_bruteforce._read_wordlist()

        assert directory_bruteforce.wordlist == set()
        assert mock_open_without_data.call_args == mocker.call(
            f"{WORDLISTS_DIR}/dir_bruteforce_small.txt", "r", encoding="utf-8"
        )
