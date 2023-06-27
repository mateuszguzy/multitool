import logging
from datetime import datetime

from config.settings import LOGGING_LEVEL, LOG_DIR, LOG_FORMAT
from utils.abstracts_classes import AbstractModule


class Logger(AbstractModule):
    logger: logging.Logger = object()
    formatter: logging.Formatter = object()
    handler: logging.Handler = object()

    # 'pydantic' required class - provide additional config to allow 'requests.Session' type check
    class Config:
        arbitrary_types_allowed = True

    def __init__(self, module: str):
        super().__init__()
        self.logger = logging.getLogger(module)
        self.logger.setLevel(LOGGING_LEVEL)
        self.formatter = logging.Formatter(LOG_FORMAT)
        filename_date = datetime.now().strftime("%Y%m%d")
        self.handler = logging.FileHandler(
            filename=f"{LOG_DIR}{filename_date}_{module.split('.')[-1]}"
        )
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)

    def run(self, mode: str, message: str):
        if mode.lower() == "info":
            self.log_info(message=message)
        elif mode.lower() == "warning":
            self.log_warning(message=message)
        elif mode.lower() == "error":
            self.log_error(message=message)
        elif mode.lower() == "debug":
            self.log_debug(message=message)

    def exit(self):
        self.logger.removeHandler(self.handler)

    def log_info(self, message: str):
        self.logger.info(message)

    def log_warning(self, message: str):
        self.logger.warning(message)

    def log_error(self, message: str):
        self.logger.error(message)

    def log_debug(self, message: str):
        self.logger.debug(message)
