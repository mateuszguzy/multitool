"""
Module by design takes only one url target and url path as input.
It's because it's supposed to receive input from directory bruteforce module.
"""
import re
import uuid
from typing import Set, Optional
from urllib.parse import urlunparse, ParseResult

from config.settings import (
    email_scraper_logger,
    EMAIL_SCRAPER_REGEX_PATTERN,
)
from modules.task_queue.tasks import log_results, email_scraper_web_request
from utils.abstracts_classes import AbstractModule
from utils.custom_dataclasses import ResultEvent
from utils.custom_exceptions import UnhandledException
from utils.utils import convert_list_or_set_to_dict, store_module_results_in_database

logger = email_scraper_logger


class EmailScraper(AbstractModule):
    email_regex_pattern = EMAIL_SCRAPER_REGEX_PATTERN
    url: str = str()

    def __init__(self, target: str, path: str) -> None:
        self.target = target
        self.url = urlunparse(
            ParseResult(
                scheme="",
                netloc=target,
                path=path,
                params="",
                query="",
                fragment="",
            )
        )[2:]
        # ^^[2:] is to remove "//" from the beginning of the url added from concatenation of schema to the rest of url

    def run(self) -> None:
        """
        Function to run the module.
        """
        html = self._get_html()

        if html:
            results = self._get_emails(html=html)

            if len(results) > 0:
                self._save_results(results=results)

    def _get_html(self) -> Optional[str]:
        """
        Function to get HTML from a website.
        """
        try:
            task_result = email_scraper_web_request.delay(target=self.url)
            result = task_result.get()

        except Exception as e:
            logger.error(f"HTTP error occurred: {e}")
            raise UnhandledException("Unhandled exception")

        else:
            return result

    def _get_emails(self, html: str) -> Set[str]:
        """
        Function to get emails from a website.
        """
        return self._by_regex(html=html)

    def _by_regex(self, html: str) -> Set[str]:
        """
        Function to get emails from a website using regex.
        """
        return set(re.findall(self.email_regex_pattern, html))

    def _save_results(self, results) -> None:
        results_for_db = convert_list_or_set_to_dict(list_of_items=results)

        store_module_results_in_database(
            target=self.target,
            results=results_for_db,
            phase="recon",
            module="email_scraper",
        )

        for result in results:
            event = ResultEvent(
                id=uuid.uuid4(),
                source_module=__name__,
                target=self.target,
                result=result,
            )
            log_results.delay(event=event)
