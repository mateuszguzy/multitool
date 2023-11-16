from config.settings import dispatcher_logger
from modules.task_queue.dispatcher_tasks import (
    run_directory_bruteforce_task,
    run_port_scan_task,
    run_email_scraper_task,
)
from utils.abstracts_classes import AbstractModule
from utils.custom_dataclasses import StartModuleEvent

logger = dispatcher_logger


class Dispatcher(AbstractModule):
    event: StartModuleEvent

    def __init__(self, event: StartModuleEvent):
        super().__init__()
        self.event = event

    def run(self) -> None:
        logger.debug(f"START::{self.event.id}")
        # TODO: add "smart" event interpreter
        self.interpret_event()

    def interpret_event(self):
        if self.event.destination_module == "directory_bruteforce":
            logger.debug("RUN::Directory bruteforce module")
            run_directory_bruteforce_task.delay(self.event.target)

        elif self.event.destination_module == "email_scraper":
            logger.debug(
                f"RUN::Email scraper module {self.event.target} {self.event.result}"
            )
            run_email_scraper_task.delay(
                target=self.event.target, path=self.event.result
            )

        elif self.event.destination_module == "port_scan":
            logger.debug("RUN::Directory bruteforce module")
            run_port_scan_task.delay(self.event.target)
