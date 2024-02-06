import datetime
import json
from hashlib import blake2b
from typing import Set, List, Dict, Any

from config.settings import (
    BLACK2B_DIGEST_SIZE,
    RESULTS_DIR,
    REDIS_ZAP_CONTEXT_NAME_KEY,
    CURRENT_DATE,
    steering_module_logger,
)
from utils.redis_utils import pull_single_value_from_db


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


def convert_list_or_set_to_dict(list_of_items: List or Set) -> dict:  # type: ignore
    """
    Convert list of items into dictionary where key is a numerical ID.
    """
    middle_set = {item for item in list_of_items if item is not None}
    final_dict = {k: v for k, v in zip(range(len(middle_set)), middle_set)}

    return final_dict


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


def extract_passwd_file_content_from_web_response(response: str) -> List[str]:
    """
    Extracts the content of the passwd file from the response.
    """
    return response.split("<!DOCTYPE")[0].strip().split()


def hash_target_name(target: str) -> str:
    """
    Hashes the target name with black2b algorithm.
    """
    return blake2b(target.encode("utf-8"), digest_size=BLACK2B_DIGEST_SIZE).hexdigest()


def save_results_to_file(results: Dict[str, Any]) -> None:
    """
    Save results to file.
    """
    current_time = datetime.datetime.now().strftime("%H%M")
    context_name = pull_single_value_from_db(key=REDIS_ZAP_CONTEXT_NAME_KEY).split("_")[
        -1
    ]
    steering_module_logger.info(
        f"{RESULTS_DIR}/{CURRENT_DATE}_{current_time}_{context_name}.json"
    )

    with open(
        f"{RESULTS_DIR}/{CURRENT_DATE}_{current_time}_{context_name}.json", mode="w"
    ) as file:
        json.dump(results, file)
