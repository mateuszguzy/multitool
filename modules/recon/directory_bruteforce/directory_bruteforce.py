from typing import Set, List, Optional

import celery  # type: ignore

from config.settings import (
    WORDLISTS_DIR,
    DIRECTORY_BRUTEFORCE_REQUEST_METHOD,
)
from modules.task_queue.tasks import directory_bruteforce_web_request
from utils.abstracts_classes import AbstractModule
from utils.custom_dataclasses import DirectoryBruteforceInput
from utils.utils import store_module_results_in_database, convert_list_or_set_to_dict


class DirectoryBruteforce(AbstractModule):
    request_method: str = DIRECTORY_BRUTEFORCE_REQUEST_METHOD
    file_path: str = str()
    allow_redirects: bool = False

    def __init__(
        self, directory_bruteforce_input: DirectoryBruteforceInput, target: str
    ) -> None:
        super().__init__()
        self.target: str = target
        list_size = getattr(directory_bruteforce_input, "list_size", "small")
        self.recursive = getattr(directory_bruteforce_input, "recursive", False)
        self.file_path: str = f"{WORDLISTS_DIR}/dir_bruteforce_{list_size}.txt"
        self.wordlist: Set[str] = set()
        self.directories_to_check_recursively: Set[str] = set()
        self.final_results: Set[str] = set()

    def run(self) -> None:
        self._read_wordlist()
        results = self._run_with_celery()
        self.final_results.update(results)

        if self.recursive:
            self.directories_to_check_recursively = set(results)
            self._run_recursively()

        self._save_results(self.final_results)

    def _run_with_celery(self, path: Optional[str] = None) -> List[str]:
        """
        Runs celery tasks in parallel.
        """
        tasks = [
            directory_bruteforce_web_request.s(
                request_method=self.request_method,
                target=self.target,
                path=self._concatenate_path(path, word),
                module=__name__,
                allow_redirects=self.allow_redirects,
            )
            for word in self.wordlist
        ]

        return [
            result
            for result in celery.group(tasks).apply_async().join()
            if result is not None
        ]

    def _run_recursively(self) -> None:
        """
        This uses 'run_directory_bruteforce' method to run directory bruteforce module recursively.
        If there are any results, it will run the same module again with the same wordlist. But this time,
        it will use the results from previous run to create new path.
        """
        while self.directories_to_check_recursively:
            results = self._run_with_celery(path=self.directories_to_check_recursively.pop())
            self.directories_to_check_recursively.update(set(results))
            self.final_results.update(results)

    def _read_wordlist(self) -> None:
        """
        Converts wordlist text file into Python set format.
        """
        with open(self.file_path, "r", encoding="utf-8") as wordlist:
            for line in wordlist:
                self.wordlist.add(line.strip())

    def _save_results(self, results) -> None:
        results = convert_list_or_set_to_dict(list_of_items=results)
        store_module_results_in_database(
            target=self.target,
            results=results,
            phase="recon",
            module="directory_bruteforce",
        )

    @staticmethod
    def _concatenate_path(path: Optional[str], word: str) -> str:
        """
        Concatenates path with word. Helpful in case of recursive directory bruteforce.
        """
        if path and word:
            return f"{path}/{word}"
        else:
            return word
