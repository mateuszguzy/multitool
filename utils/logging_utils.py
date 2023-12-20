import traceback
from logging import Logger

from config.settings import steering_module_logger, LOGGERS_MAPPER


def log_exception(exc_type, value, tb) -> None:
    exception_info = {
        "ExceptionType": exc_type.__name__,
        "Value": str(value),
        "Traceback": traceback.format_exception(exc_type, value, tb),
    }
    steering_module_logger.error(exception_info)


def get_logger(module: str) -> Logger:
    """
    Returns the logger for the given module name.
    """
    for key in LOGGERS_MAPPER.keys():
        if key in module:
            return LOGGERS_MAPPER[key]

    # if no logger is found, return the default logger
    return LOGGERS_MAPPER["__main__"]
