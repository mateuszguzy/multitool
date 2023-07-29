import re
import traceback
from typing import Set, List

from config.settings import (
    URL_CHECKING_REGEX_WITH_TLD,
    TRAILING_SLASH_REGEX,
    PROTOCOL_PREFIX_REGEX,
    LOGGING_DIVIDER,
    URL_CHECKING_REGEX_WITHOUT_TLD,
)


def clean_and_validate_input_targets(targets: str) -> Set[str]:
    split_targets = {target.strip() for target in targets.split(",")}
    valid_targets = {target for target in split_targets if target_is_url(target)}

    targets_with_protocol = check_for_protocol_prefix_in_multiple_targets(valid_targets)
    final_targets = check_for_trailing_slash_in_multiple_targets(targets_with_protocol)

    return final_targets


def check_for_trailing_slash_in_multiple_targets(targets: Set[str]) -> Set[str]:
    result: Set = set()

    for target in targets:
        if re.search(TRAILING_SLASH_REGEX, target) is None:
            result.add(target + "/")
        else:
            result.add(target)

    return result


def check_for_protocol_prefix_in_multiple_targets(targets: Set[str]) -> Set[str]:
    result: Set = set()

    for target in targets:
        if re.search(PROTOCOL_PREFIX_REGEX, target) is None:
            result.add("http://" + target)
        else:
            result.add(target)

    return result


def format_exception_with_traceback_for_logging(exc: Exception) -> str:
    tb = traceback.format_exc()
    message = f"Error:{exc.args[0]}{LOGGING_DIVIDER}TRACEBACK{LOGGING_DIVIDER}: {tb}"

    return message


def target_is_url(target: str) -> bool:
    match: bool = False
    if re.search(URL_CHECKING_REGEX_WITH_TLD, target):
        match = True
    if re.search(URL_CHECKING_REGEX_WITHOUT_TLD, target):
        match = True
    return match
