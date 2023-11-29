from celery.result import allow_join_result  # type: ignore

from config.settings import (
    task_queue_logger,
    DIRECTORY_BRUTEFORCE,
    PORT_SCAN,
)
from utils.custom_dataclasses import (
    DirectoryBruteforceInput,
    PortScanInput,
    StartModuleEvent,
)
from utils.utils import withdraw_input_from_db, expression_is_true

logger = task_queue_logger


def run_zap_spider_task(event: StartModuleEvent) -> None:
    from modules.zap.zap_spider import start_zap_spider

    # deliberately run twice to make sure that all the links are discovered
    start_zap_spider(target_url=event.target)
    start_zap_spider(target_url=event.target)


def run_directory_bruteforce_task(event: StartModuleEvent):
    from modules.recon.directory_bruteforce.directory_bruteforce import (
        DirectoryBruteforce,
    )

    input_dict = withdraw_input_from_db(module=DIRECTORY_BRUTEFORCE)
    directory_bruteforce_input = DirectoryBruteforceInput(
        list_size=input_dict.get("list_size", "small")[0].decode("utf-8"),
        # Redis stores only strings, so we need to convert it to bool
        recursive=expression_is_true(
            expression=input_dict.get("recursive", False)[0].decode("utf-8")
        ),
    )
    directory_bruteforce = DirectoryBruteforce(
        directory_bruteforce_input=directory_bruteforce_input,
        target=event.target,
    )

    # this is required because of 'join()' method aggregating results from all tasks
    # used inside '_run_with_celery()' method, without it 'join()' would block the task
    with allow_join_result():
        directory_bruteforce.run()


def run_email_scraper_task(event: StartModuleEvent):
    from modules.recon.email_scraper.email_scraper import (
        EmailScraper,
    )

    email_scraper = EmailScraper(
        target=event.target,
        # path for email scraper is a result (directory) from directory bruteforce module
        path=event.result if event.result else "",
    )

    # this is required because of 'join()' method aggregating results from all tasks
    # used inside '_run_with_celery()' method, without it 'join()' would block the task
    with allow_join_result():
        email_scraper.run()


def run_port_scan_task(event: StartModuleEvent) -> None:
    from modules.scan.port_scan.port_scan import PortScan

    input_dict = withdraw_input_from_db(module=PORT_SCAN)
    port_scan_input = PortScanInput(
        port_scan_type=input_dict.get("port_scan_type", "important")[0].decode("utf-8"),
        ports={
            int(port.decode("utf-8"))
            for port in input_dict.get("ports", set())
            if port.decode("utf-8").isdigit()
        },
    )
    port_scan = PortScan(
        port_scan_input=port_scan_input,
        target=event.target,
    )

    # this is required because of 'join()' method aggregating results from all tasks
    # used inside '_run_with_celery()' method, without it 'join()' would block the task
    with allow_join_result():
        port_scan.run()


def run_lfi_task(event: StartModuleEvent) -> None:
    from modules.gain_access.file_inclusion.lfi.local_file_inclusion import (
        LocalFileInclusion,
    )

    lfi = LocalFileInclusion(
        target=event.target,
    )

    # this is required because of 'delay()' method aggregating results from all tasks
    # used inside '_make_request()' method
    with allow_join_result():
        lfi.run()
