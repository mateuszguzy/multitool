import json
import os

import pytest

from config.settings import TESTS_MOCKED_INPUT_DIR, BASE_DIR
from modules.core.steering_module.steering_module import SteeringModule
from modules.network.request_manager.request_manager import RequestManager
from modules.recon.directory_bruteforce.directory_bruteforce import DirectoryBruteforce
from modules.recon.recon import Recon
from modules.user_interface.cli.cli_interface import CliInterface
from utils.custom_dataclasses import DirectoryBruteforceInput

MOCK_USER_INPUT_SINGLE_MODULE_DIRECTORY_BRUTEFORCE = (
    f"{TESTS_MOCKED_INPUT_DIR}/mock_user_input_single_module_directory_bruteforce.json"
)
MOCK_USER_INPUT_SINGLE_PHASE_RECON = (
    f"{TESTS_MOCKED_INPUT_DIR}/mock_user_input_single_phase_recon.json"
)
MOCK_USER_INPUT_ALL = f"{TESTS_MOCKED_INPUT_DIR}/mock_user_input_all.json"
TEST_URL = "https://www.example.com"
DIRECTORY_BRUTEFORCE_WORDLIST_MOCK_INPUT = "word1\nword2\nword3"
BUILTINS_OPEN_PATH = "builtins.open"


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
    request_manager = RequestManager(method=request.param, url=TEST_URL)
    return request_manager


@pytest.fixture(
    scope="module",
    params=[
        "post",
        "POST",
    ],
)
def request_manager_post_request(request):
    request_manager = RequestManager(method=request.param, url=TEST_URL)
    return request_manager


@pytest.fixture(
    scope="module",
    params=[
        "delete",
        "DELETE",
    ],
)
def request_manager_delete_request(request):
    request_manager = RequestManager(method=request.param, url=TEST_URL)
    return request_manager


@pytest.fixture()
def cli_interface():
    return CliInterface()


@pytest.fixture
def recon():
    return Recon(directory_bruteforce_list_size="small", target="example.com")


@pytest.fixture(scope="function")
def directory_bruteforce():
    return DirectoryBruteforce(
        directory_bruteforce_input=DirectoryBruteforceInput(list_size="small"),
        target=TEST_URL,
    )


# MOCKS
@pytest.fixture
def mock_click_prompt_without_return_value(mocker):
    mocker.patch(
        "modules.user_interface.cli.cli_interface.click.prompt"
    )


@pytest.fixture
def mock_click_prompt_with_return_value(mocker, expect):
    mocker.patch(
        "modules.user_interface.cli.cli_interface.click.prompt", return_value=expect
    )


@pytest.fixture
def mock_translate_abbreviations(mocker, expect):
    mocker.patch(
        "modules.user_interface.cli.cli_interface.CliInterface._translate_abbreviations", return_value=expect
    )


@pytest.fixture
def mock_directory_bruteforce_questions(mocker):
    mocker.patch(
        "modules.user_interface.cli.cli_interface.CliInterface.directory_bruteforce_questions",
    )


@pytest.fixture
def mock_directory_bruteforce_list_size_question(mocker):
    mocker.patch(
        "modules.user_interface.cli.cli_interface.CliInterface.directory_bruteforce_list_size_question",
    )


@pytest.fixture
def mock_clean_and_validate_input_targets(mocker, expect):
    mocker.patch("modules.user_interface.cli.cli_interface.clean_and_validate_input_targets", return_value=expect)


@pytest.fixture
def mock_check_for_protocol_prefix_in_multiple_targets(mocker, expect):
    mocker.patch(
        "utils.utils.check_for_protocol_prefix_in_multiple_targets", return_value=expect
    )


@pytest.fixture
def mock_check_for_trailing_slash_in_multiple_targets(mocker, expect):
    mocker.patch(
        "utils.utils.check_for_protocol_prefix_in_multiple_targets", return_value=expect
    )


@pytest.fixture(scope="function")
def mock_open_with_data(mocker):
    return mocker.patch(
        BUILTINS_OPEN_PATH,
        mocker.mock_open(read_data=DIRECTORY_BRUTEFORCE_WORDLIST_MOCK_INPUT),
    )


@pytest.fixture(scope="function")
def mock_open_without_data(mocker):
    return mocker.patch(BUILTINS_OPEN_PATH, mocker.mock_open(read_data=""))


@pytest.fixture(scope="function")
def mock_open_with_file_not_found_error(mocker):
    return mocker.patch(BUILTINS_OPEN_PATH, side_effect=FileNotFoundError)


@pytest.fixture(scope="function")
def mock_celery_group(mocker):
    return mocker.patch("celery.group")
