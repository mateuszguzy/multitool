import time
import traceback
from hashlib import blake2b
from logging import Logger
from typing import Set, List, Optional
from urllib.parse import urlparse

from config.settings import (
    steering_module_logger,
    REDIS_TARGETS_KEY,
    REDIS_MODULES_KEY,
    REDIS_USER_INPUT_KEY,
    DB_INPUT_MODULE_MAPPER,
    LOGGERS_MAPPER,
    PUBSUB_LAST_MESSAGE_TIME_KEY,
    ZAP_SPIDER,
    BLACK2B_DIGEST_SIZE,
)
from modules.helper.redis_client import RedisClient
from modules.zap.zap import zap


def url_formatter(input_target: str, module: Optional[str] = None) -> str:
    """
    Format URL to be in form of http://target
    """
    final_url = ""
    url = urlparse(input_target)

    if not url.scheme and url.path:
        path = url.path
        url = url._replace(netloc=path, path="", scheme="http")

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

                keys = rc.keys(f"{target}*|{phase}|{module}|*")

                if not results[target].get(phase):
                    results[target][phase] = {}

                if module == ZAP_SPIDER:
                    results[target][phase][module] = zap.spider.all_urls
                else:
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


def get_logger(module: str) -> Logger:
    """
    Returns the logger for the given module name.
    """
    for key in LOGGERS_MAPPER.keys():
        if key in module:
            return LOGGERS_MAPPER[key]

    # if no logger is found, return the default logger
    return LOGGERS_MAPPER["__main__"]


def expression_is_true(expression) -> bool:
    """
    Check if expression is True.
    """
    if expression in [
        "True",
        "true",
        True,
    ]:
        return True
    else:
        return False


def withdraw_input_from_db(module: str) -> dict:
    input_dict: dict = dict()

    if module in DB_INPUT_MODULE_MAPPER:
        with RedisClient() as rc:
            # cannot decode results from Redis directly here because some results are
            # single values and some are lists e.g. port_scan::ports, so it's done while
            # creating input class
            input_dict = {
                k: rc.mget(rc.keys(f"{DB_INPUT_MODULE_MAPPER[module]['path']}{v}*"))
                for k, v in DB_INPUT_MODULE_MAPPER[module]["keys"].items()
            }

    return input_dict


def extract_passwd_file_content_from_web_response(response: str) -> List[str]:
    """
    Extracts the content of the passwd file from the response.
    """
    return response.split("<!DOCTYPE")[0].strip().split()


def put_single_value_in_db(key: str, value: str) -> None:
    """
    Puts single key data in the database.
    """
    with RedisClient() as rc:
        rc.set(name=key, value=value)


def pull_single_value_from_db(key: str) -> str:
    """
    Pulls single key data from the database.
    """
    with RedisClient() as rc:
        return rc.get(key).decode("utf-8")


def save_message_time():
    """
    Saves the time of the last message received from the broker.
    Used to check if the broker is still alive.
    """
    put_single_value_in_db(key=PUBSUB_LAST_MESSAGE_TIME_KEY, value=str(time.time()))


def hash_target_name(target: str) -> str:
    """
    Hashes the target name with black2b algorithm.
    """
    return blake2b(target.encode("utf-8"), digest_size=BLACK2B_DIGEST_SIZE).hexdigest()


def transform_regexs_into_urls(targets: List[str]) -> Set[str]:
    """
    Function responsible for transforming regexs into urls.
    """
    result_targets = set()

    for target in targets:
        target = target.replace(".*", "")
        result_targets.add(target)

    return result_targets
