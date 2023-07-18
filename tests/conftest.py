import pytest

from config.settings import TESTS_MOCKED_INPUT_DIR, BASE_DIR
from modules.network.request_manager.request_manager import RequestManager
from utils.utils import create_steering_module_instance_with_user_input


USER_INPUT_MOCK_SINGLE_MODULE_1 = (
    f"{TESTS_MOCKED_INPUT_DIR}/user_input_mock_single_module_1.json"
)
USER_INPUT_MOCK_SINGLE_MODULE_2 = (
    f"{TESTS_MOCKED_INPUT_DIR}/user_input_mock_single_module_2.json"
)
USER_INPUT_MOCK_SINGLE_MODULE_3 = (
    f"{TESTS_MOCKED_INPUT_DIR}/user_input_mock_single_module_3.json"
)
USER_INPUT_MOCK_SINGLE_PHASE_1 = (
    f"{TESTS_MOCKED_INPUT_DIR}/user_input_mock_single_phase_1.json"
)
USER_INPUT_MOCK_SINGLE_PHASE_2 = (
    f"{TESTS_MOCKED_INPUT_DIR}/user_input_mock_single_phase_2.json"
)
USER_INPUT_MOCK_RUN_ALL_1 = "tests/mocked_user_input/user_input_mock_run_all_1.json"


@pytest.fixture(
    scope="module",
    params=[
        USER_INPUT_MOCK_SINGLE_MODULE_1,
        USER_INPUT_MOCK_SINGLE_MODULE_2,
        USER_INPUT_MOCK_SINGLE_MODULE_3,
    ],
)
def test_input_1(request):
    return create_steering_module_instance_with_user_input(request.param)


@pytest.fixture(
    scope="module",
    params=[
        USER_INPUT_MOCK_SINGLE_PHASE_1,
        USER_INPUT_MOCK_SINGLE_PHASE_2,
    ],
)
def test_input_2(request):
    return create_steering_module_instance_with_user_input(request.param)


@pytest.fixture(
    scope="module",
    params=[
        USER_INPUT_MOCK_RUN_ALL_1,
    ],
)
def test_input_3(request):
    return create_steering_module_instance_with_user_input(request.param)


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
