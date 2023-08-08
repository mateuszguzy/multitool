from multiprocessing import Pool

import celery  # type: ignore

from config.settings import (
    WORDLISTS_DIR,
    NUMBER_OF_AVAILABLE_CPU_CORES,
    DIRECTORY_BRUTEFORCE_REQUEST_METHOD,
)
from modules.network.request_manager.request_manager import RequestManager
from modules.task_queue.tasks import web_request
from utils.abstracts_classes import AbstractModule
from utils.utils import store_module_results_in_database, convert_list_or_set_to_dict


class DirectoryBruteforce(AbstractModule):
    request_method: str = DIRECTORY_BRUTEFORCE_REQUEST_METHOD
    request_url: str = str()
    file_path: str = str()
    wordlist: list[str] = list()
    results_after_multiprocessing: list = list()

    def __init__(self, request_url: str, list_size: str) -> None:
        super().__init__()
        self.request_url = request_url
        self.file_path = f"{WORDLISTS_DIR}/dir_bruteforce_{list_size}.txt"

    def run(self):
        # self._run_with_multiprocessing()
        self._run_with_celery()

    def _run_with_multiprocessing(self):
        self._read_wordlist()

        with Pool(NUMBER_OF_AVAILABLE_CPU_CORES) as pool:
            # 'imap_unordered' allows to return values in the middle of multiprocess running
            results = pool.imap_unordered(self._run_requests, self.wordlist)

            # iterates through the multiprocess functions results every time a new output occurs
            for result in results:
                # filter out all empty values (negative results) returned by multiprocess functions
                if result is not None:
                    self.results_after_multiprocessing.append(result)

    def _run_with_celery(self):
        self._read_wordlist()

        tasks = [
            web_request.s(
                request_method=self.request_method,
                url=self.request_url,
                word=word,
                module=__name__
            )
            for word in self.wordlist
        ]

        results = convert_list_or_set_to_dict(list_of_items=celery.group(tasks).apply_async().join())
        store_module_results_in_database(target=self.request_url, results=results, module="directory_bruteforce")

    def _read_wordlist(self) -> None:
        """
        Converts wordlist text file into Python list format.
        """
        with open(self.file_path) as wordlist:
            for line in wordlist.read().splitlines():
                self.wordlist.append(line)

    def _run_requests(self, word: str):
        url = f"{self.request_url}{word}"

        with RequestManager(method=self.request_method, url=url) as rm:
            response = rm.run()

            if response.status_code not in [404]:
                return word
            else:
                return None
