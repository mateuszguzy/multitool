import re
import traceback
from typing import Set, List

from config.settings import (
    URL_CHECKING_REGEX_WITH_TLD,
    TRAILING_SLASH_REGEX,
    PROTOCOL_PREFIX_REGEX,
    LOGGING_DIVIDER,
    URL_CHECKING_REGEX_WITHOUT_TLD,
    steering_module_logger,
)
from modules.helper.redis_client import RedisClient


def clean_and_validate_input_targets(targets: str) -> Set[str]:
    """
    Check if provided targets are following one of below conventions:
        - <protocol>://<subdomain>.<domain_name>.<top_level_domain>:<port_number>
        - <protocol>://<subdomain>.<domain_name>.<top_level_domain>
        - <protocol>://<subdomain>.<domain_name>:<port_number>
        - <subdomain>.<domain_name>.<top_level_domain>:<port_number>
        - <subdomain>.<domain_name>.<top_level_domain>
        - <subdomain>.<domain_name>:<port_number>
        - <domain_name>.<top_level_domain>:<port_number>
        - <domain_name>.<top_level_domain>
        - <domain_name>:<port_number>
    """
    split_targets = {target.strip() for target in targets.split(",")}
    valid_targets = {target for target in split_targets if target_is_url(target)}

    targets_with_protocol = check_for_protocol_prefix_in_multiple_targets(valid_targets)
    final_targets = check_for_trailing_slash_in_multiple_targets(targets_with_protocol)

    return final_targets


def check_for_trailing_slash_in_multiple_targets(targets: Set[str]) -> Set[str]:
    """
    Check if given target has a trailing slash, if not, add one.
    """
    result: Set = set()

    for target in targets:
        if re.search(TRAILING_SLASH_REGEX, target) is None:
            result.add(target + "/")
        else:
            result.add(target)

    return result


def check_for_protocol_prefix_in_multiple_targets(targets: Set[str]) -> Set[str]:
    """
    Check if given target has a protocol defined, if not, add one.
    """
    result: Set = set()

    for target in targets:
        if re.search(PROTOCOL_PREFIX_REGEX, target) is None:
            result.add("http://" + target)
        else:
            result.add(target)

    return result


def format_exception_with_traceback_for_logging(exc: Exception) -> str:
    """
    Logger related function passing whole traceback info into log file.
    """
    tb = traceback.format_exc()
    try:
        message = f"Error:{exc.args[0]}{LOGGING_DIVIDER}TRACEBACK{LOGGING_DIVIDER}: {tb}"
    except IndexError:
        message = f"Error:{exc}{LOGGING_DIVIDER}TRACEBACK{LOGGING_DIVIDER}: {tb}"

    return message


def target_is_url(target: str) -> bool:
    """
    Verify if given target can be (with small changes) treated as a URL.
    """
    match: bool = False
    if re.search(URL_CHECKING_REGEX_WITH_TLD, target):
        match = True
    if re.search(URL_CHECKING_REGEX_WITHOUT_TLD, target):
        match = True
    return match


def prepare_final_results_dictionary() -> dict:
    """
    Pull all stored results from Redis and return in form of following dictionary:

    target_url: {
        module_producing_results: [ list_of_results ]
    }
    """
    results: dict = dict()

    with RedisClient() as rc:
        keys = rc.keys("modules|*")
        used_modules = rc.mget(keys)

        keys = rc.keys("targets|*")
        targets = rc.mget(keys)

        for target in targets:
            results[target.decode("utf-8")] = {}

            for module in used_modules:
                keys = rc.keys(f"{target.decode('utf-8')}|{module.decode('utf-8')}|*")
                results[target.decode("utf-8")][module.decode("utf-8")] = [
                    result.decode("utf-8") for result in rc.mget(keys)
                ]

        rc.flushall()

    return results


def store_module_results_in_database(target: str, results: dict, module: str) -> None:
    """
    Stare results in Redis in form of following dictionary:

    target_url: {
        module_producing_results: {
            id: result
        }
    }
    """
    with RedisClient() as rc:
        rc.mset({f"{target}|{module}|" + str(k): v for k, v in results.items()})


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
