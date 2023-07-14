import json
import re
from typing import List

from config.settings import (
    URL_CHECKING_REGEX,
    TRAILING_SLASH_REGEX,
    PROTOCOL_PREFIX_REGEX,
)
from modules.core.steering_module.steering_module import SteeringModule


def create_steering_module_instance_with_user_input(path: str):
    test_input = open(path)
    steering_module = SteeringModule(json.load(test_input))

    return steering_module


def clean_and_validate_input_targets(targets: str) -> List[str]:
    split_targets = [target.strip() for target in targets.split(",")]
    valid_targets = [
        target
        for target in split_targets
        if re.search(URL_CHECKING_REGEX, target) is not None
    ]

    targets_with_protocol = check_for_protocol_prefix_in_multiple_targets(valid_targets)
    final_targets = check_for_trailing_slash_in_multiple_targets(targets_with_protocol)

    return final_targets


def check_for_trailing_slash_in_multiple_targets(targets: List[str]) -> List[str]:
    result = []

    for target in targets:
        if re.search(TRAILING_SLASH_REGEX, target) is None:
            result.append(target + "/")
        else:
            result.append(target)

    return result


def check_for_protocol_prefix_in_multiple_targets(targets: List[str]) -> List[str]:
    result = []

    for target in targets:
        if re.search(PROTOCOL_PREFIX_REGEX, target) is None:
            result.append("http://" + target)
        else:
            result.append(target)

    return result
