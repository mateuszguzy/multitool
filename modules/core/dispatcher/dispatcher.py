from typing import Union

from yaml import load, Loader

from config.settings import (
    dispatcher_logger,
    WORKFLOW_YAML_PATH,
    DIRECTORY_BRUTEFORCE,
    PORT_SCAN,
    EMAIL_SCRAPER,
    LFI,
)
from modules.task_queue.dispatcher_tasks import (
    run_directory_bruteforce_task,
    run_port_scan_task,
    run_email_scraper_task,
    run_lfi_task,
)
from utils.abstracts_classes import AbstractModule
from utils.custom_dataclasses import StartModuleEvent, ResultEvent

logger = dispatcher_logger

module_mapper = {
    DIRECTORY_BRUTEFORCE: run_directory_bruteforce_task,
    EMAIL_SCRAPER: run_email_scraper_task,
    PORT_SCAN: run_port_scan_task,
    LFI: run_lfi_task,
}


class Dispatcher(AbstractModule):
    workflow_yaml_path = WORKFLOW_YAML_PATH
    workflow: dict

    def __init__(self, event: Union[StartModuleEvent, ResultEvent]) -> None:
        super().__init__()
        self.event = event
        self.workflow = self._parse_workflow_yaml()

    def run(self) -> None:
        logger.debug(f"INTERPRETING::{self.event.id}")
        if isinstance(self.event, StartModuleEvent):
            self._interpret_start_module_event(event=self.event)

        if isinstance(self.event, ResultEvent):
            self._interpret_result_event(event=self.event)

    def _interpret_start_module_event(self, event: StartModuleEvent) -> None:
        for module in self.workflow["modules"]:
            if (
                module["name"] == event.destination_module
                and event.source_module.split(".")[-1] in module["accept_input_from"]
                and event.destination_module in module_mapper
            ):
                try:
                    logger.debug(f"START::{event.id}")
                    module_mapper[event.destination_module.split(".")[-1]].delay(
                        event=event
                    )

                except Exception as e:
                    logger.error(f"ERROR::{event.id}::{e}")

    def _interpret_result_event(self, event: ResultEvent) -> None:
        for module in self.workflow["modules"]:
            if (
                module["name"] == event.source_module.split(".")[-1]
                and module["pass_results_to"] is not None
            ):
                for destination_module in module["pass_results_to"]:
                    try:
                        logger.debug(f"START::{event.id}")
                        module_mapper[destination_module].delay(event=event)

                    except Exception as e:
                        logger.error(f"ERROR::{event.id}::{e}")

    def _parse_workflow_yaml(self) -> dict:
        with open(self.workflow_yaml_path, "r") as f:
            return load(f, Loader=Loader)["workflow"]
