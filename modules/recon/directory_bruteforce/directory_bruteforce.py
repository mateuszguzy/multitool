from multiprocessing import Pool

from pydantic import BaseModel

from config.settings import (
    WORDLISTS_DIR,
    NUMBER_OF_AVAILABLE_CPU_CORES,
    DIR_BRUTEFORCE_REQUEST_METHOD,
)
from modules.network.request_manager.request_manager import RequestManager
from utils.abstracts_classes import AbstractModule


class DirectoryBruteforce(AbstractModule, BaseModel):
    request_method: str = DIR_BRUTEFORCE_REQUEST_METHOD
    request_url: str = str()
    file_path: str = str()
    wordlist: list[str] = list()
    results: list = list()

    def __init__(self, request_url: str, list_size: str) -> None:
        super().__init__()
        self.request_url = request_url
        self.file_path = f"{WORDLISTS_DIR}/dir_bruteforce_{list_size}.txt"

    def run(self):
        # self._run_with_multiprocessing()
        for value in self.results:
            yield value

    def _run_with_multiprocessing(self):
        self._read_wordlist()

        with Pool(NUMBER_OF_AVAILABLE_CPU_CORES) as pool:
            # 'imap_unordered' allows to return values in the middle of multiprocess running
            results = pool.imap_unordered(self._run_requests, self.wordlist)

            # iterates through the multiprocess functions results every time a new output occurs
            for result in results:

                # filter out all empty values (negative results) returned by multiprocess functions
                if result is not None:
                    self.results.append(result)

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
