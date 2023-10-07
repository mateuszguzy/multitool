import json
import os
from unittest import mock

import pytest

from config.settings import TESTS_MOCKED_INPUT_DIR, BASE_DIR
from modules.core.steering_module.steering_module import SteeringModule
from modules.network.request_manager.request_manager import RequestManager
from modules.network.socket_manager.socket_manager import SocketManager
from modules.recon.directory_bruteforce.directory_bruteforce import DirectoryBruteforce
from modules.recon.recon import Recon
from modules.scan.port_scan.port_scan import PortScan
from modules.scan.scan import Scan
from modules.user_interface.cli.cli_interface import CliInterface
from utils.custom_dataclasses import DirectoryBruteforceInput, ReconInput, UserInput, PortScanInput, ScanInput

MOCK_USER_INPUT_SINGLE_MODULE_DIRECTORY_BRUTEFORCE = (
    f"{TESTS_MOCKED_INPUT_DIR}/mock_user_input_single_module_directory_bruteforce.json"
)
MOCK_USER_INPUT_SINGLE_MODULE_PORT_SCAN = (
    f"{TESTS_MOCKED_INPUT_DIR}/mock_user_input_single_module_port_scan.json"
)
MOCK_USER_INPUT_SINGLE_PHASE_RECON = (
    f"{TESTS_MOCKED_INPUT_DIR}/mock_user_input_single_phase_recon.json"
)
MOCK_USER_INPUT_SINGLE_PHASE_SCAN = (
    f"{TESTS_MOCKED_INPUT_DIR}/mock_user_input_single_phase_scan.json"
)
MOCK_USER_INPUT_ALL = f"{TESTS_MOCKED_INPUT_DIR}/mock_user_input_all.json"
TEST_TARGET = "https://www.example.com"
TEST_PORT_SCAN_TARGET = "www.example.com"
DIRECTORY_BRUTEFORCE_WORDLIST_MOCK_INPUT = "word1\nword2\nword3"
BUILTINS_OPEN_PATH = "builtins.open"
DIRECTORY_BRUTEFORCE_INPUT = DirectoryBruteforceInput(list_size="small")
TEST_PORTS = {80, 443}
TEST_PORT = 80


def convert_json_input_to_dict(path: str):
    user_input = open(path)
    return json.load(user_input)


def convert_user_input_to_dataclass(path: str) -> UserInput:
    user_input_dict = convert_json_input_to_dict(path=path)
    directory_bruteforce_input = DirectoryBruteforceInput(
        user_input_dict.get("recon").get("directory_bruteforce").get("list_size")
    )
    port_scan_input = PortScanInput(
        ports=set(user_input_dict.get("scan").get("port_scan").get("ports"))
    )
    return UserInput(
        use_type=user_input_dict.get("use_type"),
        phase=user_input_dict.get("phase"),
        module=user_input_dict.get("module"),
        targets=set(user_input_dict.get("targets")),
        recon=ReconInput(directory_bruteforce_input),
        scan=ScanInput(port_scan_input),
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


# --- UNIT
@pytest.fixture(scope="module")
def steering_module_for_single_module_directory_bruteforce():
    return create_steering_module_instance_with_user_input(
        MOCK_USER_INPUT_SINGLE_MODULE_DIRECTORY_BRUTEFORCE
    )


@pytest.fixture(scope="module")
def steering_module_for_single_module_port_scan():
    return create_steering_module_instance_with_user_input(
        MOCK_USER_INPUT_SINGLE_MODULE_PORT_SCAN
    )


@pytest.fixture(scope="module")
def steering_module_for_single_phase_recon():
    return create_steering_module_instance_with_user_input(
        MOCK_USER_INPUT_SINGLE_PHASE_RECON
    )


@pytest.fixture(scope="module")
def steering_module_for_single_phase_scan():
    return create_steering_module_instance_with_user_input(
        MOCK_USER_INPUT_SINGLE_PHASE_SCAN
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
    request_manager = RequestManager(method=request.param, url=TEST_TARGET)
    return request_manager


@pytest.fixture(
    scope="module",
    params=[
        "post",
        "POST",
    ],
)
def request_manager_post_request(request):
    request_manager = RequestManager(method=request.param, url=TEST_TARGET)
    return request_manager


@pytest.fixture(
    scope="module",
    params=[
        "delete",
        "DELETE",
    ],
)
def request_manager_delete_request(request):
    request_manager = RequestManager(method=request.param, url=TEST_TARGET)
    return request_manager


@pytest.fixture()
def cli_interface():
    return CliInterface()


@pytest.fixture(scope="function")
def directory_bruteforce():
    return DirectoryBruteforce(
        directory_bruteforce_input=DIRECTORY_BRUTEFORCE_INPUT,
        target=TEST_TARGET,
    )


@pytest.fixture(scope="function")
def port_scan():
    return PortScan(
        target=TEST_TARGET,
        port_scan_input=PortScanInput(ports=TEST_PORTS),
    )


@pytest.fixture(scope="function")
def socket_manager():
    return SocketManager(target=TEST_PORT_SCAN_TARGET, port=TEST_PORT)


@pytest.fixture
def recon_whole_phase(directory_bruteforce):
    return Recon(
        recon_input=ReconInput(DIRECTORY_BRUTEFORCE_INPUT),
        target=TEST_TARGET,
        single_module=None,
    )


@pytest.fixture
def scan_whole_phase():
    return Scan(
        scan_input=ScanInput(PortScanInput(ports=TEST_PORTS)),
        target=TEST_TARGET,
        single_module=None,
    )


# MOCKS
@pytest.fixture
def mock_check_for_protocol_prefix_in_multiple_targets(mocker, expect):
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
def mock_celery_group():
    group_mock = mock.Mock()
    group_mock.apply_async.return_value.join.return_value = "mocked results"

    return group_mock


@pytest.fixture(scope="function")
def mock_socket_request_task():
    socket_request_mock = mock.Mock()
    socket_request_mock.s.return_value = socket_request_mock

    return socket_request_mock


@pytest.fixture(scope="function")
def mock_web_request_task():
    web_request_mock = mock.Mock()
    web_request_mock.s.return_value = web_request_mock

    return web_request_mock
