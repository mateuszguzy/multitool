import inspect
import json
import os
import uuid
from unittest import mock

import pytest
from redis import Redis

import modules.task_queue.tasks as celery_tasks
from config.settings import (
    TESTS_MOCKED_INPUT_DIR,
    BASE_DIR,
    REDIS_DB,
    REDIS_HOST,
    REDIS_PORT,
    REDIS_MODULES_KEY,
    REDIS_TARGETS_KEY,
    REDIS_USER_INPUT_KEY,
    STEERING_MODULE,
    DIRECTORY_BRUTEFORCE,
    PORT_SCAN,
    EMAIL_SCRAPER,
)
from modules.core.dispatcher.dispatcher import Dispatcher
from modules.core.steering_module.steering_module import SteeringModule
from modules.network.request_manager.request_manager import RequestManager
from modules.network.socket_manager.socket_manager import SocketManager
from modules.recon.directory_bruteforce.directory_bruteforce import DirectoryBruteforce
from modules.recon.email_scraper.email_scraper import EmailScraper
from modules.scan.port_scan.port_scan import PortScan
from modules.task_queue.tasks import start_event_listeners
from modules.user_interface.cli.cli_interface import CliInterface
from utils.custom_dataclasses import (
    DirectoryBruteforceInput,
    ReconInput,
    UserInput,
    PortScanInput,
    ScanInput,
    StartModuleEvent,
    ResultEvent,
)

# --- MOCKED INPUT PATHS
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

# --- TEST DATA
TEST_TARGET = "https://www.example.com"
TEST_PATH = "/path"
TEST_PORT_SCAN_TARGET = "www.example.com"
TEST_RESULT = "test_result"
DIRECTORY_BRUTEFORCE_WORDLIST_MOCK_INPUT = "word1\nword2\nword3"
BUILTINS_OPEN_PATH = "builtins.open"
DIRECTORY_BRUTEFORCE_INPUT_NON_RECURSIVE = DirectoryBruteforceInput(
    list_size="small", recursive=False
)
DIRECTORY_BRUTEFORCE_INPUT_RECURSIVE = DirectoryBruteforceInput(
    list_size="small", recursive=True
)
TEST_TARGETS_SET = {"http://dvwa/", "https://www.example.com"}
TEST_PORTS = {80, 443}
TEST_PORT = 80
TEST_REQUEST_MANAGER_METHOD = "GET"
MOCKED_WORKFLOW = {
    "version": "1.0",
    "modules": [
        {
            "name": "directory_bruteforce",
            "accept_input_from": ["steering_module"],
            "pass_results_to": ["email_scraper"],
        },
        {
            "name": "port_scan",
            "accept_input_from": ["steering_module"],
            "pass_results_to": None,
        },
        {
            "name": "email_scraper",
            "accept_input_from": ["steering_module", "directory_bruteforce"],
            "pass_results_to": None,
        },
    ],
}

# --- MODULE PATHS
DIRECTORY_BRUTEFORCE_MODULE_PATH = inspect.getmodule(DirectoryBruteforce).__name__  # type: ignore
PORT_SCAN_MODULE_PATH = inspect.getmodule(PortScan).__name__  # type: ignore
EMAIL_SCRAPER_MODULE_PATH = inspect.getmodule(EmailScraper).__name__  # type: ignore
REQUEST_MANAGER_MODULE_PATH = inspect.getmodule(RequestManager).__name__  # type: ignore
CELERY_TASKS_MODULE_PATH = inspect.getmodule(celery_tasks).__name__  # type: ignore
DISPATCHER_MODULE_PATH = inspect.getmodule(Dispatcher).__name__  # type: ignore


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
        output_after_every_finding=True,
    )


def create_steering_module_instance_with_user_input(user_input):
    return SteeringModule(convert_user_input_to_dataclass(user_input))


###################################################
#           INTEGRATION TESTS FIXTURES            #
###################################################
@pytest.fixture(scope="class")
def docker_compose_file_for_running_tests(pytestconfig):
    return os.path.join(
        str(pytestconfig.rootpath), BASE_DIR, "docker-compose.tests.yaml"
    )


@pytest.fixture(scope="class")
def steering_module_with_directory_bruteforce_test_input_integration_fixture():
    return create_steering_module_instance_with_user_input(
        MOCK_USER_INPUT_SINGLE_MODULE_DIRECTORY_BRUTEFORCE
    )


@pytest.fixture(scope="class")
def redis_client_fixture():
    return Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)


@pytest.fixture(scope="class")
def redis_db_results_complete_fixture(redis_client_fixture):
    rc = redis_client_fixture

    rc.set(f"{REDIS_USER_INPUT_KEY}{REDIS_MODULES_KEY}|0", "phase1|module1")
    rc.set(f"{REDIS_USER_INPUT_KEY}{REDIS_MODULES_KEY}|1", "phase1|module2")

    rc.set(f"{REDIS_USER_INPUT_KEY}{REDIS_TARGETS_KEY}0", "target1")
    rc.set(f"{REDIS_USER_INPUT_KEY}{REDIS_TARGETS_KEY}1", "target2")

    rc.set("target1|phase1|module1|0", "result1")
    rc.set("target1|phase1|module1|1", "result2")
    rc.set("target1|phase1|module2|2", "result3")
    rc.set("target2|phase1|module1|3", "result4")

    yield

    rc.flushall()


@pytest.fixture(scope="class")
def redis_db_results_only_targets_fixture(redis_client_fixture):
    rc = redis_client_fixture

    rc.set(f"{REDIS_USER_INPUT_KEY}{REDIS_TARGETS_KEY}0", "target1")
    rc.set(f"{REDIS_USER_INPUT_KEY}{REDIS_TARGETS_KEY}1", "target2")

    yield

    rc.flushall()


@pytest.fixture(scope="class")
def setup_event_listeners_fixture():
    start_event_listeners(output_after_every_finding=True)


###################################################
#                UNIT TESTS FIXTURES              #
###################################################
##########################
#     STEERING MODULE    #
##########################
# used by 'lazy_fixture' that why 'usages' are not counted
@pytest.fixture(scope="class")
def steering_module_for_single_module_directory_bruteforce_fixture():
    return create_steering_module_instance_with_user_input(
        MOCK_USER_INPUT_SINGLE_MODULE_DIRECTORY_BRUTEFORCE
    )


# used by 'lazy_fixture' that why 'usages' are not counted
@pytest.fixture(scope="class")
def steering_module_for_single_module_port_scan_fixture():
    return create_steering_module_instance_with_user_input(
        MOCK_USER_INPUT_SINGLE_MODULE_PORT_SCAN
    )


# used by 'lazy_fixture' that why 'usages' are not counted
@pytest.fixture(scope="class")
def steering_module_for_single_phase_recon_fixture():
    return create_steering_module_instance_with_user_input(
        MOCK_USER_INPUT_SINGLE_PHASE_RECON
    )


# used by 'lazy_fixture' that why 'usages' are not counted
@pytest.fixture(scope="class")
def steering_module_for_single_phase_scan_fixture():
    return create_steering_module_instance_with_user_input(
        MOCK_USER_INPUT_SINGLE_PHASE_SCAN
    )


# used by 'lazy_fixture' that why 'usages' are not counted
@pytest.fixture(scope="class")
def steering_module_for_all_fixture():
    return create_steering_module_instance_with_user_input(MOCK_USER_INPUT_ALL)


##########################
#        DISPATCHER      #
##########################
# used by 'lazy_fixture' that why 'usages' are not counted
@pytest.fixture(scope="class")
def start_directory_bruteforce_module_event_fixture():
    return StartModuleEvent(
        id=uuid.uuid4(),
        source_module=STEERING_MODULE,
        target=TEST_TARGET,
        destination_module=DIRECTORY_BRUTEFORCE,
        result=TEST_RESULT,
    )


# used by 'lazy_fixture' that why 'usages' are not counted
@pytest.fixture(scope="class")
def start_port_scan_module_event_fixture():
    return StartModuleEvent(
        id=uuid.uuid4(),
        source_module=STEERING_MODULE,
        target=TEST_TARGET,
        destination_module=PORT_SCAN,
        result=TEST_RESULT,
    )


# used by 'lazy_fixture' that why 'usages' are not counted
@pytest.fixture(scope="class")
def start_email_scraper_module_event_fixture():
    return StartModuleEvent(
        id=uuid.uuid4(),
        source_module=STEERING_MODULE,
        target=TEST_TARGET,
        destination_module=EMAIL_SCRAPER,
        result=TEST_RESULT,
    )


# used by 'lazy_fixture' that why 'usages' are not counted
@pytest.fixture(scope="class")
def directory_bruteforce_result_event_fixture():
    return ResultEvent(
        id=uuid.uuid4(),
        source_module=DIRECTORY_BRUTEFORCE,
        target=TEST_TARGET,
        result=TEST_RESULT,
    )


# used by 'lazy_fixture' that why 'usages' are not counted
@pytest.fixture(scope="class")
def email_scraper_result_event_fixture():
    return ResultEvent(
        id=uuid.uuid4(),
        source_module=EMAIL_SCRAPER,
        target=TEST_TARGET,
        result=TEST_RESULT,
    )


# used by 'lazy_fixture' that why 'usages' are not counted
@pytest.fixture(scope="class")
def port_scan_result_event_fixture():
    return ResultEvent(
        id=uuid.uuid4(),
        source_module=PORT_SCAN,
        target=TEST_TARGET,
        result=TEST_RESULT,
    )


##########################
#      CLI INTERFACE     #
##########################
@pytest.fixture(scope="class")
def cli_interface_fixture():
    return CliInterface()


##########################
#  DIRECTORY BRUTEFORCE  #
##########################
@pytest.fixture(scope="function")
def directory_bruteforce_non_recursive_fixture():
    return DirectoryBruteforce(
        directory_bruteforce_input=DIRECTORY_BRUTEFORCE_INPUT_NON_RECURSIVE,
        target=TEST_TARGET,
    )


# used by 'lazy_fixture' that why 'usages' are not counted
@pytest.fixture(scope="function")
def directory_bruteforce_recursive_fixture():
    return DirectoryBruteforce(
        directory_bruteforce_input=DIRECTORY_BRUTEFORCE_INPUT_RECURSIVE,
        target=TEST_TARGET,
    )


##########################
#         MANAGERS       #
##########################
@pytest.fixture(scope="class")
def socket_manager_fixture():
    return SocketManager(target=TEST_PORT_SCAN_TARGET, port=TEST_PORT)


@pytest.fixture(scope="function")
def request_manager_fixture():
    return RequestManager(method=TEST_REQUEST_MANAGER_METHOD)


##########################
#           SCAN         #
##########################
# used by 'lazy_fixture' that why 'usages' are not counted
@pytest.fixture(scope="class")
def scan_input_fixture(port_scan_input_fixture):
    return ScanInput(port_scan_input_fixture)


# used by 'lazy_fixture' that why 'usages' are not counted
@pytest.fixture(scope="class")
def scan_input_empty_fixture(port_scan_input_empty_fixture):
    return ScanInput(port_scan_input_empty_fixture)


##########################
#        PORT SCAN       #
##########################
@pytest.fixture(scope="class")
def port_scan_input_fixture():
    return PortScanInput(
        port_scan_type="custom",
        ports=TEST_PORTS,
    )


@pytest.fixture(scope="class")
def port_scan_input_empty_fixture():
    return PortScanInput(
        port_scan_type="custom",
        ports=set(),
    )


@pytest.fixture(scope="class")
def port_scan_fixture(port_scan_input_fixture):
    return PortScan(
        target=TEST_TARGET,
        port_scan_input=port_scan_input_fixture,
    )


###################################################
#                    MOCKS                        #
###################################################
##########################
#        BUILTINS        #
##########################
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


##########################
#        DISPATCHER      #
##########################
@pytest.fixture(scope="function")
def mock_dispatcher_parse_workflow_yaml_function(mocker):
    return mocker.patch(f"{DISPATCHER_MODULE_PATH}.Dispatcher._parse_workflow_yaml")


@pytest.fixture(scope="function")
def mock_dispatcher_interpret_start_module_event_function(mocker):
    return mocker.patch(
        f"{DISPATCHER_MODULE_PATH}.Dispatcher._interpret_start_module_event"
    )


@pytest.fixture(scope="function")
def mock_dispatcher_interpret_result_event_function(mocker):
    return mocker.patch(f"{DISPATCHER_MODULE_PATH}.Dispatcher._interpret_result_event")


@pytest.fixture(scope="function")
def mock_dispatcher_directory_bruteforce_task(mocker):
    return mocker.patch(f"{DISPATCHER_MODULE_PATH}.run_directory_bruteforce_task.delay")


@pytest.fixture(scope="function")
def mock_dispatcher_email_scraper_task(mocker):
    return mocker.patch(f"{DISPATCHER_MODULE_PATH}.run_email_scraper_task.delay")


@pytest.fixture(scope="function")
def mock_dispatcher_port_scan_task(mocker):
    return mocker.patch(f"{DISPATCHER_MODULE_PATH}.run_port_scan_task.delay")


@pytest.fixture(scope="function")
def mock_dispatcher_workflow(mocker):
    return mocker.patch(
        f"{DISPATCHER_MODULE_PATH}.Dispatcher._parse_workflow_yaml",
        return_value=MOCKED_WORKFLOW,
    )


##########################
#  DIRECTORY BRUTEFORCE  #
##########################
@pytest.fixture(scope="function")
def mock_directory_bruteforce_read_wordlist(mocker):
    return mocker.patch(
        f"{DIRECTORY_BRUTEFORCE_MODULE_PATH}.DirectoryBruteforce._read_wordlist"
    )


@pytest.fixture(scope="function")
def mock_directory_bruteforce_run_recursively(mocker):
    return mocker.patch(
        f"{DIRECTORY_BRUTEFORCE_MODULE_PATH}.DirectoryBruteforce._run_recursively"
    )


@pytest.fixture(scope="function")
def mock_directory_bruteforce_save_results(mocker):
    return mocker.patch(
        f"{DIRECTORY_BRUTEFORCE_MODULE_PATH}.DirectoryBruteforce._save_results"
    )


##########################
#       PORT SCAN        #
##########################
@pytest.fixture(scope="function")
def mock_port_scan_convert_list_or_set_to_dict(mocker):
    return mocker.patch(f"{PORT_SCAN_MODULE_PATH}.convert_list_or_set_to_dict")


@pytest.fixture(scope="function")
def mock_port_scan_store_module_results_in_database(mocker):
    return mocker.patch(f"{PORT_SCAN_MODULE_PATH}.store_module_results_in_database")


##########################
#        TASK QUEUE      #
##########################
@pytest.fixture(scope="function")
def mock_get_logger_function(mocker):
    return mocker.patch(
        f"{CELERY_TASKS_MODULE_PATH}.get_logger", return_value=mocker.Mock()
    )


@pytest.fixture(scope="function")
def mock_get_logger_function_with_exception(mocker):
    return mocker.patch(f"{CELERY_TASKS_MODULE_PATH}.get_logger", side_effect=Exception)


@pytest.fixture(scope="function")
def mock_task_queue_logger_in_tasks(mocker):
    return mocker.patch(
        f"{CELERY_TASKS_MODULE_PATH}.logger", return_value=mocker.Mock()
    )


@pytest.fixture(scope="function")
def mock_redis_in_tasks(mocker):
    return mocker.patch(f"{CELERY_TASKS_MODULE_PATH}.rc", return_value=mocker.Mock())


@pytest.fixture(scope="function")
def mock_redis_pubsub_subscribe_in_tasks(mocker):
    return mocker.patch(
        f"{CELERY_TASKS_MODULE_PATH}.pubsub.subscribe", return_value=mocker.Mock()
    )


@pytest.fixture(scope="function")
def mock_redis_pubsub_listen_in_tasks(mocker):
    event = {"type": "message", "data": b"test_data_1"}
    return mocker.patch(
        f"{CELERY_TASKS_MODULE_PATH}.pubsub.listen", return_value=[event]
    )


@pytest.fixture(scope="function")
def mock_redis_pubsub_listen_with_exception_in_tasks(mocker):
    return mocker.patch(
        f"{CELERY_TASKS_MODULE_PATH}.pubsub.listen", side_effect=Exception
    )


@pytest.fixture(scope="function")
def mock_log_results_task(mocker):
    return mocker.patch(
        f"{CELERY_TASKS_MODULE_PATH}.log_results", return_value=mocker.Mock()
    )


@pytest.fixture(scope="function")
def mock_dispatcher_in_tasks(mocker):
    return mocker.patch(
        f"{CELERY_TASKS_MODULE_PATH}.Dispatcher", return_value=mocker.Mock()
    )


@pytest.fixture(scope="function")
def mock_event_listener_task(mocker):
    return mocker.patch(f"{CELERY_TASKS_MODULE_PATH}.event_listener_task")


@pytest.fixture(scope="function")
def mock_live_results_listener_task(mocker):
    return mocker.patch(f"{CELERY_TASKS_MODULE_PATH}.live_results_listener_task")


@pytest.fixture(scope="function")
def mock_pass_result_event(mocker):
    return mocker.patch(f"{CELERY_TASKS_MODULE_PATH}.pass_result_event")


##########################
#      EMAIL SCRAPER     #
##########################
@pytest.fixture(scope="function")
def mock_email_scraper_module(mocker):
    mocker.patch(
        f"{EMAIL_SCRAPER_MODULE_PATH}.urlunparse",
        return_value=mocker.MagicMock(),
    )
    return EmailScraper(target=TEST_TARGET, path=TEST_PATH)


@pytest.fixture(scope="function")
def mock_email_scraper_web_request_task(mocker):
    return mocker.patch(
        f"{EMAIL_SCRAPER_MODULE_PATH}.email_scraper_web_request",
        return_value=mocker.Mock(),
    )


@pytest.fixture(scope="function")
def mock_email_scraper_web_request_task_with_exception(mocker):
    return mocker.patch(
        f"{EMAIL_SCRAPER_MODULE_PATH}.email_scraper_web_request.delay",
        side_effect=Exception,
    )


@pytest.fixture(scope="function")
def mock_email_scraper_save_results_method(mocker):
    return mocker.patch(f"{EMAIL_SCRAPER_MODULE_PATH}.EmailScraper._save_results")


@pytest.fixture(scope="function")
def mock_store_module_results_in_database(mocker):
    return mocker.patch(f"{EMAIL_SCRAPER_MODULE_PATH}.store_module_results_in_database")


@pytest.fixture(scope="function")
def mock_log_results(mocker):
    return mocker.patch(f"{EMAIL_SCRAPER_MODULE_PATH}.log_results.delay")


##########################
#          CELERY        #
##########################
@pytest.fixture(scope="class")
def mock_celery_group():
    group_mock = mock.Mock()
    group_mock.apply_async.return_value.join.return_value = "mocked results"

    return group_mock


@pytest.fixture(scope="class")
def mock_socket_request_task():
    socket_request_mock = mock.Mock()
    socket_request_mock.s.return_value = socket_request_mock

    return socket_request_mock


@pytest.fixture(scope="class")
def mock_web_request_task():
    web_request_mock = mock.Mock()
    web_request_mock.s.return_value = web_request_mock

    return web_request_mock
