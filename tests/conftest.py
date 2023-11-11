import json
import os
from unittest import mock

import pytest
from redis import Redis

from config.settings import (
    TESTS_MOCKED_INPUT_DIR,
    BASE_DIR,
    REDIS_DB,
    REDIS_HOST,
    REDIS_PORT,
)
from modules.core.steering_module.steering_module import SteeringModule
from modules.network.socket_manager.socket_manager import SocketManager
from modules.recon.directory_bruteforce.directory_bruteforce import DirectoryBruteforce
from modules.scan.port_scan.port_scan import PortScan
from modules.task_queue.tasks import start_event_listeners
from modules.user_interface.cli.cli_interface import CliInterface
from utils.custom_dataclasses import (
    DirectoryBruteforceInput,
    ReconInput,
    UserInput,
    PortScanInput,
    ScanInput,
)

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
DIRECTORY_BRUTEFORCE_INPUT_NON_RECURSIVE = DirectoryBruteforceInput(
    list_size="small", recursive=False
)
DIRECTORY_BRUTEFORCE_INPUT_RECURSIVE = DirectoryBruteforceInput(
    list_size="small", recursive=True
)
TEST_PORTS = {80, 443}
TEST_PORT = 80
TASK_QUEUE_MODULE_PATH = "modules.task_queue.tasks"


###################################################
#                    UTILS                        #
###################################################
def convert_json_input_to_dict(path: str):
    user_input = open(path)
    return json.load(user_input)


def convert_user_input_to_dataclass(path: str) -> UserInput:
    user_input_dict = convert_json_input_to_dict(path=path)
    directory_bruteforce_input = DirectoryBruteforceInput(
        list_size=user_input_dict.get("recon")
        .get("directory_bruteforce")
        .get("list_size"),
        recursive=user_input_dict.get("recon")
        .get("directory_bruteforce")
        .get("recursive"),
    )
    port_scan_input = PortScanInput(
        ports=set(user_input_dict.get("scan").get("port_scan").get("ports")),
        port_scan_type=user_input_dict.get("scan")
        .get("port_scan")
        .get("port_scan_type"),
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


###################################################
#             INTEGRATION FIXTURES                #
###################################################
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


@pytest.fixture(scope="module")
def setup_event_listeners():
    start_event_listeners(output_after_every_finding=True)


###################################################
#                 UNIT FIXTURES                   #
###################################################
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


@pytest.fixture()
def cli_interface():
    return CliInterface()


@pytest.fixture(scope="function")
def directory_bruteforce_non_recursive():
    return DirectoryBruteforce(
        directory_bruteforce_input=DIRECTORY_BRUTEFORCE_INPUT_NON_RECURSIVE,
        target=TEST_TARGET,
    )


@pytest.fixture(scope="function")
def directory_bruteforce_recursive():
    return DirectoryBruteforce(
        directory_bruteforce_input=DIRECTORY_BRUTEFORCE_INPUT_RECURSIVE,
        target=TEST_TARGET,
    )


@pytest.fixture(scope="function")
def test_socket_manager():
    return SocketManager(target=TEST_PORT_SCAN_TARGET, port=TEST_PORT)


@pytest.fixture
def test_directory_bruteforce_input():
    return DirectoryBruteforceInput(list_size="small", recursive=False)


@pytest.fixture
def test_directory_bruteforce_input_empty():
    return DirectoryBruteforceInput(list_size=None, recursive=None)


@pytest.fixture
def test_recon_input(test_directory_bruteforce_input):
    return ReconInput(test_directory_bruteforce_input)


@pytest.fixture
def test_recon_input_empty(test_directory_bruteforce_input_empty):
    return ReconInput(test_directory_bruteforce_input_empty)


@pytest.fixture
def test_port_scan_input():
    return PortScanInput(
        port_scan_type="custom",
        ports=TEST_PORTS,
    )


@pytest.fixture
def test_port_scan_input_empty():
    return PortScanInput(
        port_scan_type="custom",
        ports=set(),
    )


@pytest.fixture
def test_scan_input(test_port_scan_input):
    return ScanInput(test_port_scan_input)


@pytest.fixture
def test_scan_input_empty(test_port_scan_input_empty):
    return ScanInput(test_port_scan_input_empty)


@pytest.fixture(scope="function")
def test_port_scan(test_port_scan_input):
    return PortScan(
        target=TEST_TARGET,
        port_scan_input=test_port_scan_input,
    )


###################################################
#                    MOCKS                        #
###################################################
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


@pytest.fixture(scope="function")
def mock_get_logger_function(mocker):
    return mocker.patch(f"{TASK_QUEUE_MODULE_PATH}.get_logger", return_value=mocker.Mock())


@pytest.fixture(scope="function")
def mock_get_logger_function_with_exception(mocker):
    return mocker.patch(f"{TASK_QUEUE_MODULE_PATH}.get_logger", side_effect=Exception)


@pytest.fixture(scope="function")
def mock_task_queue_logger_in_tasks(mocker):
    return mocker.patch(f"{TASK_QUEUE_MODULE_PATH}.logger", return_value=mocker.Mock())


@pytest.fixture(scope="function")
def mock_redis_in_tasks(mocker):
    return mocker.patch(f"{TASK_QUEUE_MODULE_PATH}.rc", return_value=mocker.Mock())


@pytest.fixture(scope="function")
def mock_redis_pubsub_subscribe_in_tasks(mocker):
    return mocker.patch(f"{TASK_QUEUE_MODULE_PATH}.pubsub.subscribe", return_value=mocker.Mock())


@pytest.fixture(scope="function")
def mock_redis_pubsub_listen_in_tasks(mocker):
    event = {"type": "message", "data": b"test_data_1"}
    return mocker.patch(f"{TASK_QUEUE_MODULE_PATH}.pubsub.listen", return_value=[event])


@pytest.fixture(scope="function")
def mock_redis_pubsub_listen_with_exception_in_tasks(mocker):
    return mocker.patch(f"{TASK_QUEUE_MODULE_PATH}.pubsub.listen", side_effect=Exception)


@pytest.fixture(scope="function")
def mock_log_results_task(mocker):
    return mocker.patch(f"{TASK_QUEUE_MODULE_PATH}.log_results", return_value=mocker.Mock())


@pytest.fixture(scope="function")
def mock_dispatcher_in_tasks(mocker):
    return mocker.patch(
        f"{TASK_QUEUE_MODULE_PATH}.Dispatcher", return_value=mocker.Mock()
    )


@pytest.fixture(scope="function")
def mock_event_listener_task(mocker):
    return mocker.patch(f"{TASK_QUEUE_MODULE_PATH}.event_listener_task")


@pytest.fixture(scope="function")
def mock_live_results_listener_task(mocker):
    return mocker.patch(f"{TASK_QUEUE_MODULE_PATH}.live_results_listener_task")


@pytest.fixture(scope="function")
def mock_pass_result_event(mocker):
    return mocker.patch(f"{TASK_QUEUE_MODULE_PATH}.pass_result_event")
