import json
import os

import pytest
from redis import Redis

from config.settings import TESTS_MOCKED_INPUT_DIR, BASE_DIR, REDIS_DB, REDIS_HOST, REDIS_PORT
from modules.core.steering_module.steering_module import SteeringModule
from modules.network.request_manager.request_manager import RequestManager
from modules.recon.directory_bruteforce.directory_bruteforce import DirectoryBruteforce
from modules.recon.recon import Recon
from modules.user_interface.cli.cli_interface import CliInterface
from utils.custom_dataclasses import DirectoryBruteforceInput, ReconInput, UserInput

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
DIRECTORY_BRUTEFORCE_INPUT = DirectoryBruteforceInput(list_size="small")


def convert_json_input_to_dict(path: str):
    user_input = open(path)
    return json.load(user_input)


def convert_user_input_to_dataclass(path: str) -> UserInput:
    user_input_dict = convert_json_input_to_dict(path=path)
    directory_bruteforce_input = DirectoryBruteforceInput(
        user_input_dict.get("recon").get("directory_bruteforce").get("list_size")
    )
    return UserInput(
        use_type=user_input_dict.get("use_type"),
        phase=user_input_dict.get("phase"),
        module=user_input_dict.get("module"),
        targets=set(user_input_dict.get("targets")),
        recon=ReconInput(directory_bruteforce_input),
        output_after_every_phase=False,
        output_after_every_finding=True,
    )


def create_steering_module_instance_with_user_input(user_input):
    return SteeringModule(convert_user_input_to_dataclass(user_input))


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


@pytest.fixture(scope="class")
def test_redis_client():
    return Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)


@pytest.fixture(scope="function")
def test_redis_db_results_complete(test_redis_client):
    rc = test_redis_client

    rc.set("modules|0", "phase1|module1")
    rc.set("modules|1", "phase1|module2")

    rc.set("targets|0", "target1")
    rc.set("targets|1", "target2")

    rc.set("target1|phase1|module1|0", "result1")
    rc.set("target1|phase1|module1|1", "result2")
    rc.set("target1|phase1|module2|2", "result3")
    rc.set("target2|phase1|module1|3", "result4")

    yield

    rc.flushall()


@pytest.fixture(scope="function")
def test_redis_db_results_only_targets(test_redis_client):
    rc = test_redis_client

    rc.set("targets|0", "target1")
    rc.set("targets|1", "target2")

    yield

    rc.flushall()


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


@pytest.fixture(scope="function")
def directory_bruteforce():
    return DirectoryBruteforce(
        directory_bruteforce_input=DIRECTORY_BRUTEFORCE_INPUT,
        target=TEST_URL,
    )


@pytest.fixture
def recon_whole_phase(directory_bruteforce):
    return Recon(
        recon_input=ReconInput(DIRECTORY_BRUTEFORCE_INPUT),
        target=TEST_URL,
        single_module=None,
    )


# MOCKS
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
