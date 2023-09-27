import celery  # type: ignore
import pytest

from config.settings import WORDLISTS_DIR
from modules.task_queue.tasks import web_request


class TestDirectoryBruteforce:
    target = "http://example.com"
    expected_wordlist = {"word1", "word2", "word3"}
    module_name = "modules.recon.directory_bruteforce.directory_bruteforce"

    def test_read_wordlist_and_run_tasks(
        self, mocker, directory_bruteforce, mock_open_with_data, mock_celery_group
    ):
        mocker.patch(f"{self.module_name}.convert_list_or_set_to_dict")
        mocker.patch(f"{self.module_name}.store_module_results_in_database")

        directory_bruteforce.run()

        assert mock_open_with_data.call_count == 1
        assert mock_open_with_data.call_args == mocker.call(
            f"{WORDLISTS_DIR}/dir_bruteforce_small.txt", "r", encoding="utf-8"
        )
        assert celery.group.call_count == 1
        assert celery.group.call_args(
            [
                mocker.call(
                    web_request.s(
                        request_method="GET",
                        url=self.target,
                        word="word1",
                        module=self.module_name,
                    )
                ),
                mocker.call(
                    web_request.s(
                        request_method="GET",
                        url=self.target,
                        word="word2",
                        module=self.module_name,
                    )
                ),
                mocker.call(
                    web_request.s(
                        request_method="GET",
                        url=self.target,
                        word="word3",
                        module=self.module_name,
                    )
                ),
            ]
        )

    def test_handle_nonexistent_wordlist_file(
        self, directory_bruteforce, mock_open_with_file_not_found_error
    ):
        with pytest.raises(FileNotFoundError):
            directory_bruteforce.run()

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
