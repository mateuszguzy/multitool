import json
import os

import pytest

from config.settings import TESTS_MOCKED_INPUT_DIR, BASE_DIR
from modules.core.steering_module.steering_module import SteeringModule
from modules.network.request_manager.request_manager import RequestManager


MOCK_USER_INPUT_SINGLE_MODULE_DIRECTORY_BRUTEFORCE = (
    f"{TESTS_MOCKED_INPUT_DIR}/mock_user_input_single_module_directory_bruteforce.json"
)
MOCK_USER_INPUT_SINGLE_PHASE_RECON = (
    f"{TESTS_MOCKED_INPUT_DIR}/mock_user_input_single_phase_recon.json"
)
MOCK_USER_INPUT_ALL = f"{TESTS_MOCKED_INPUT_DIR}/mock_user_input_all.json"


def convert_user_input_to_dict(path: str):
    user_input = open(path)
    return json.load(user_input)


def create_steering_module_instance_with_user_input(user_input):
    return SteeringModule(convert_user_input_to_dict(user_input))


# --- INTEGRATION
@pytest.fixture(scope="module")
def docker_compose_file(pytestconfig):
    return os.path.join(
        str(pytestconfig.rootpath), BASE_DIR, "docker-compose.tests.yaml"
    )


@pytest.fixture(scope="module")
def integration_steering_module_with_directory_bruteforce_test_input():
    return create_steering_module_instance_with_user_input(
        MOCK_USER_INPUT_SINGLE_MODULE_DIRECTORY_BRUTEFORCE
    )


# --- UNIT
@pytest.fixture(scope="module")
def steering_module_for_single_module_directory_bruteforce():
    return create_steering_module_instance_with_user_input(MOCK_USER_INPUT_SINGLE_MODULE_DIRECTORY_BRUTEFORCE)


@pytest.fixture(scope="module")
def steering_module_for_single_phase_recon():
    return create_steering_module_instance_with_user_input(MOCK_USER_INPUT_SINGLE_PHASE_RECON)


@pytest.fixture(scope="module")
def steering_module_for_all():
    return create_steering_module_instance_with_user_input(MOCK_USER_INPUT_ALL)


@pytest.fixture(
    scope="module",
    params=[
        "get",
        "GET",
        "post",
        "POST",
        "delete",
        "DELETE",
    ],
)
def request_manager(request):
    request_manager = RequestManager(
        method=request.param, url="https://www.example.com"
    )
    return request_manager
