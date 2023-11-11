import traceback
from logging import Logger
from typing import Set, List, Optional
from urllib.parse import urlparse

from config.settings import (
    steering_module_logger,
    directory_bruteforce_logger,
    port_scan_logger,
    REDIS_TARGETS_KEY,
    REDIS_MODULES_KEY,
    REDIS_USER_INPUT_KEY,
)
from modules.helper.redis_client import RedisClient

# Constants for module names
STEERING_MODULE_NAME = "__main__"
DIRECTORY_BRUTEFORCE_MODULE_NAME = (
    "modules.recon.directory_bruteforce.directory_bruteforce"
)
PORT_SCAN_MODULE_NAME = "modules.scan.port_scan.port_scan"

# Dictionary mapping module names to loggers
loggers = {
    STEERING_MODULE_NAME: steering_module_logger,
    DIRECTORY_BRUTEFORCE_MODULE_NAME: directory_bruteforce_logger,
    PORT_SCAN_MODULE_NAME: port_scan_logger,
}


def url_formatter(input_target: str, module: Optional[str] = None) -> str:
    """
    Format URL to be in form of http://target
    """
    final_url = ""
    url = urlparse(input_target)

    if not url.scheme and url.path:
        path = url.path
        url = url._replace(netloc=path, path="/", scheme="http")

    if not url.path:
        url = url._replace(path="/")

    if module == "port_scan":
        if url.scheme:
            url = url._replace(scheme="", path="")
            final_url = url.netloc + url.path
    else:
        final_url = url.geturl()

    return final_url


def clean_and_validate_input_ports(ports_to_scan: str) -> Set[int]:
    """
    Check if provided ports are following one of below conventions:
        - <port_number>
        - <port_number>,<port_number>,<port_number>
    """
    valid_ports = set()
    split_ports = {port.strip() for port in ports_to_scan.split(",")}

    for port in split_ports:
        try:
            port_number = int(port)
            if port_number in range(1, 65536):
                valid_ports.add(port_number)
        except ValueError:
            pass

    return valid_ports


def prepare_final_results_dictionary() -> dict:
    """
    Pull all stored results from Redis and return in form of following dictionary:

    target_url: {
        module_producing_results: [ list_of_results ]
    }
    """
    results: dict = dict()

    with RedisClient() as rc:
        keys = rc.keys(f"{REDIS_USER_INPUT_KEY}{REDIS_MODULES_KEY}*")
        used_modules = rc.mget(keys)

        keys = rc.keys(f"{REDIS_USER_INPUT_KEY}{REDIS_TARGETS_KEY}*")
        targets = rc.mget(keys)

        for target in targets:
            target = target.decode("utf-8")
            results[target] = {}

            for used_module in used_modules:
                used_module = used_module.decode("utf-8")
                phase = used_module.split("|")[0]
                module = used_module.split("|")[1]

                keys = rc.keys(f"{target}|{phase}|{module}|*")

                if not results[target].get(phase):
                    results[target][phase] = {}

                results[target][phase][module] = [
                    result.decode("utf-8") for result in rc.mget(keys)
                ]

        rc.flushall()

    return results


def store_module_results_in_database(
    target: str, results: dict, phase: str, module: str
) -> None:
    """
    Stare results in Redis in form of following dictionary:

    target_url: {
        module_producing_results: {
            id: result
        }
    }
    """
    if results:
        with RedisClient() as rc:
            rc.mset(
                {f"{target}|{phase}|{module}|" + str(k): v for k, v in results.items()}
            )


def convert_list_or_set_to_dict(list_of_items: List or Set) -> dict:  # type: ignore
    """
    Convert list of items into dictionary where key is a numerical ID.
    """
    middle_set = {item for item in list_of_items if item is not None}
    final_dict = {k: v for k, v in zip(range(len(middle_set)), middle_set)}

    return final_dict


def log_exception(exc_type, value, tb) -> None:
    exception_info = {
        "ExceptionType": exc_type.__name__,
        "Value": str(value),
        "Traceback": traceback.format_exception(exc_type, value, tb),
    }
    steering_module_logger.error(exception_info)


def get_logger(module: Optional[str]) -> Logger:
    """
    Returns the logger for the given module name.
    """
    if module in loggers:
        return loggers[module]
    else:
        return loggers[STEERING_MODULE_NAME]
