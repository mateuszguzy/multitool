import logging
from datetime import datetime

from pydantic import BaseModel

from config.settings import LOGGING_LEVEL, LOG_DIR, LOG_FORMAT
from utils.abstracts_classes import AbstractModule


class Logger(AbstractModule, BaseModel):
    module: str = str()
    logger: logging.Logger = object()
    formatter: logging.Formatter = object()

    # 'pydantic' required class - provide additional config to allow 'requests.Session' type check
    class Config:
        arbitrary_types_allowed = True

    def __init__(self, module: str):
        super().__init__()
        self.logger = logging.getLogger(module)
        self.logger.setLevel(LOGGING_LEVEL)
        self.module = module
        self.formatter = logging.Formatter(LOG_FORMAT)

    def run(self):
        timestamp = datetime.now().strftime("%Y%m%d")
        handler = logging.FileHandler(filename=f"{LOG_DIR}{timestamp}_{self.module}")
        handler.setFormatter(self.formatter)
        self.logger.addHandler(handler)

    def log_info(self, message: str):
        self.logger.info(message)

    def log_warning(self, message: str):
        self.logger.warning(message)

    def log_error(self, message: str):
        self.logger.error(message)

    def log_debug(self, message: str):
        self.logger.debug(message)
