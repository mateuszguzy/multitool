from celery.result import allow_join_result  # type: ignore

from config.settings import task_queue_logger
from modules.task_queue.celery import app
from utils.custom_dataclasses import DirectoryBruteforceInput, PortScanInput

logger = task_queue_logger


@app.task()
def run_directory_bruteforce_task(target: str):
    from modules.recon.directory_bruteforce.directory_bruteforce import (
        DirectoryBruteforce,
    )

    # TODO: change hardcoded values after Redis temporary storage is implemented
    directory_bruteforce_input = DirectoryBruteforceInput(
        list_size="small",
        recursive=False,
    )
    directory_bruteforce = DirectoryBruteforce(
        directory_bruteforce_input=directory_bruteforce_input,
        target=target,
    )

    # this is required because of 'join()' method aggregating results from all tasks
    # used inside '_run_with_celery()' method, without it 'join()' would block the task
    with allow_join_result():
        directory_bruteforce.run()


@app.task
def run_port_scan_task(target: str) -> None:
    from modules.scan.port_scan.port_scan import PortScan

    # TODO: change hardcoded values after Redis temporary storage is implemented
    port_scan_input = PortScanInput(
        port_scan_type="important",
        ports=set(),
    )
    port_scan = PortScan(
        port_scan_input=port_scan_input,
        target=target,
    )

    with allow_join_result():
        port_scan.run()
