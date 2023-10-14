from unittest import TestCase

import celery  # type: ignore
import pytest

from config.settings import WORDLISTS_DIR
from tests.conftest import TEST_TARGET


class TestDirectoryBruteforce:
    test_target = TEST_TARGET
    expected_wordlist = {"word1", "word2", "word3"}
    module_name = (
        "modules.recon.directory_bruteforce.directory_bruteforce.DirectoryBruteforce"
    )

    @pytest.mark.parametrize(
        "directory_bruteforce_input, is_recursive, expected_wordlist",
        [
            (
                pytest.lazy_fixture("directory_bruteforce_non_recursive"),  # type: ignore
                False,
                expected_wordlist,
            ),
            (
                pytest.lazy_fixture("directory_bruteforce_recursive"),  # type: ignore
                True,
                expected_wordlist,
            ),
        ],
    )
    def test_run_tasks_successfully(
        self,
        mocker,
        directory_bruteforce_input,
        is_recursive,
        expected_wordlist,
    ):
        """
        Test all calls for all words are made
        """
        mocker.patch(f"{self.module_name}._read_wordlist")
        mocker.patch(
            f"{self.module_name}._run_with_celery",
            return_value=list(self.expected_wordlist),
        )
        mocker.patch(f"{self.module_name}._run_recursively")
        mocker.patch(f"{self.module_name}._save_results")

        directory_bruteforce_input.run()

        TestCase().assertSetEqual(
            directory_bruteforce_input.final_results, self.expected_wordlist
        )
        assert directory_bruteforce_input._read_wordlist.call_count == 1
        assert directory_bruteforce_input.recursive == is_recursive
        assert directory_bruteforce_input._run_with_celery.call_count == 1
        assert directory_bruteforce_input._save_results.call_count == 1

    def test_handle_nonexistent_wordlist_file(
        self, directory_bruteforce_non_recursive, mock_open_with_file_not_found_error
    ):
        with pytest.raises(FileNotFoundError):
            directory_bruteforce_non_recursive._read_wordlist()

    def test_read_wordlist_successfully_converts_to_set(
        self, mocker, directory_bruteforce_non_recursive, mock_open_with_data
    ):
        directory_bruteforce_non_recursive._read_wordlist()
        print(self.expected_wordlist)
        assert directory_bruteforce_non_recursive.wordlist == self.expected_wordlist
        assert mock_open_with_data.call_count == 1
        assert mock_open_with_data.call_args == mocker.call(
            f"{WORDLISTS_DIR}/dir_bruteforce_small.txt", "r", encoding="utf-8"
        )

    def test_empty_wordlist_file(
        self, mocker, directory_bruteforce_non_recursive, mock_open_without_data
    ):
        directory_bruteforce_non_recursive._read_wordlist()

        assert directory_bruteforce_non_recursive.wordlist == set()
        assert mock_open_without_data.call_args == mocker.call(
            f"{WORDLISTS_DIR}/dir_bruteforce_small.txt", "r", encoding="utf-8"
        )

    @pytest.mark.parametrize(
        "path, word, expected_result",
        [
            ("", "word", "word"),
            ("", "/word", "/word"),
            ("", "word/", "word/"),
            ("", "/word/", "/word/"),
            ("word1", "word2", "word1/word2"),
            ("word1/", "word2", "word1//word2"),
            ("/word1", "word2", "/word1/word2"),
            ("word1/", "word2/", "word1//word2/"),
            ("word1", "", ""),
            ("", "", ""),
        ],
    )
    def test_concatenate_path_none_word(
        self, directory_bruteforce_non_recursive, path, word, expected_result
    ):
        dirb = directory_bruteforce_non_recursive
        result = dirb._concatenate_path(path, word)
        assert result == expected_result
