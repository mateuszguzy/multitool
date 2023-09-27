from typing import Set

import celery  # type: ignore

from config.settings import (
    WORDLISTS_DIR,
    DIRECTORY_BRUTEFORCE_REQUEST_METHOD,
)
from modules.task_queue.tasks import web_request
from utils.custom_dataclasses import DirectoryBruteforceInput
from utils.abstracts_classes import AbstractModule
from utils.utils import store_module_results_in_database, convert_list_or_set_to_dict


class DirectoryBruteforce(AbstractModule):
    request_method: str = DIRECTORY_BRUTEFORCE_REQUEST_METHOD
    file_path: str = str()

    def __init__(self, directory_bruteforce_input: DirectoryBruteforceInput, target: str) -> None:
        super().__init__()
        self.target: str = target
        list_size = getattr(directory_bruteforce_input, "list_size")
        self.file_path: str = f"{WORDLISTS_DIR}/dir_bruteforce_{list_size}.txt"
        self.wordlist: Set[str] = set()

    def run(self):
        self._run_with_celery()

    def _run_with_celery(self):
        """
        Runs celery tasks in parallel.
        """
        self._read_wordlist()

        tasks = [
            web_request.s(
                request_method=self.request_method,
                url=self.target,
                word=word,
                module=__name__,
            )
            for word in self.wordlist
        ]

        results = convert_list_or_set_to_dict(
            list_of_items=celery.group(tasks).apply_async().join()
        )
        store_module_results_in_database(
            target=self.target, results=results, module="directory_bruteforce"
        )

    def _read_wordlist(self) -> None:
        """
        Converts wordlist text file into Python set format.
        """
        with open(self.file_path, "r", encoding="utf-8") as wordlist:
            for line in wordlist:
                self.wordlist.add(line.strip())
