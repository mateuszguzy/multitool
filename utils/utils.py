import re
import traceback
from typing import List

from config.settings import (
    URL_CHECKING_REGEX_WITH_TLD,
    TRAILING_SLASH_REGEX,
    PROTOCOL_PREFIX_REGEX,
    LOGGING_DIVIDER,
    URL_CHECKING_REGEX_WITHOUT_TLD,
)


def clean_and_validate_input_targets(targets: str) -> List[str]:
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
    split_targets = [target.strip() for target in targets.split(",")]
    valid_targets = [target for target in split_targets if target_is_url(target)]

    targets_with_protocol = check_for_protocol_prefix_in_multiple_targets(valid_targets)
    final_targets = check_for_trailing_slash_in_multiple_targets(targets_with_protocol)

    return final_targets


def check_for_trailing_slash_in_multiple_targets(targets: List[str]) -> List[str]:
    """
    Check if given target has a trailing slash, if not, add one.
    """
    result = []

    for target in targets:
        if re.search(TRAILING_SLASH_REGEX, target) is None:
            result.append(target + "/")
        else:
            result.append(target)

    return result


def check_for_protocol_prefix_in_multiple_targets(targets: List[str]) -> List[str]:
    """
    Check if given target has a protocol defined, if not, add one.
    """
    result = []

    for target in targets:
        if re.search(PROTOCOL_PREFIX_REGEX, target) is None:
            result.append("http://" + target)
        else:
            result.append(target)

    return result


def format_exception_with_traceback_for_logging(exc: Exception) -> str:
    """
    Logger related function passing whole traceback info into log file.
    """
    tb = traceback.format_exc()
    message = f"Error:{exc.args[0]}{LOGGING_DIVIDER}TRACEBACK{LOGGING_DIVIDER}: {tb}"

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
