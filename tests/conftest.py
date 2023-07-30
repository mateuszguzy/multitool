import json
import os

import pytest

from config.settings import TESTS_MOCKED_INPUT_DIR, BASE_DIR
from modules.core.steering_module.steering_module import SteeringModule
from modules.network.request_manager.request_manager import RequestManager
from modules.user_interface.cli.cli_interface import CliInterface

MOCK_USER_INPUT_SINGLE_MODULE_DIRECTORY_BRUTEFORCE = (
    f"{TESTS_MOCKED_INPUT_DIR}/mock_user_input_single_module_directory_bruteforce.json"
)
MOCK_USER_INPUT_SINGLE_PHASE_RECON = (
    f"{TESTS_MOCKED_INPUT_DIR}/mock_user_input_single_phase_recon.json"
)
MOCK_USER_INPUT_ALL = f"{TESTS_MOCKED_INPUT_DIR}/mock_user_input_all.json"
TEST_URL = "https://www.example.com"


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
    return create_steering_module_instance_with_user_input(
        MOCK_USER_INPUT_SINGLE_MODULE_DIRECTORY_BRUTEFORCE
    )


@pytest.fixture(scope="module")
def steering_module_for_single_phase_recon():
    return create_steering_module_instance_with_user_input(
        MOCK_USER_INPUT_SINGLE_PHASE_RECON
    )


@pytest.fixture(scope="module")
def steering_module_for_all():
    return create_steering_module_instance_with_user_input(MOCK_USER_INPUT_ALL)


@pytest.fixture(
    scope="module",
    params=[
        "get",
        "GET",
    ],
)
def request_manager_get_request(request):
    request_manager = RequestManager(
        method=request.param, url=TEST_URL
    )
    return request_manager


@pytest.fixture(
    scope="module",
    params=[
        "post",
        "POST",
    ],
)
def request_manager_post_request(request):
    request_manager = RequestManager(
        method=request.param, url=TEST_URL
    )
    return request_manager


@pytest.fixture(
    scope="module",
    params=[
        "delete",
        "DELETE",
    ],
)
def request_manager_delete_request(request):
    request_manager = RequestManager(
        method=request.param, url=TEST_URL
    )
    return request_manager


@pytest.fixture()
def cli_interface():
    return CliInterface()


@pytest.fixture
def mock_click_prompt(mocker, expect):
    mocker.patch(
        "modules.user_interface.cli.cli_interface.click.prompt", return_value=expect
    )


@pytest.fixture
def mock_directory_bruteforce_questions(mocker, expect):
    mocker.patch(
        "modules.user_interface.cli.cli_interface.CliInterface.directory_bruteforce_questions",
        return_value=expect,
    )


@pytest.fixture
def mock_clean_and_validate_input_targets(mocker, expect):
    mocker.patch("utils.utils.clean_and_validate_input_targets", return_value=expect)
