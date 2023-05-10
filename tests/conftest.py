import pytest

from utils.utils import create_steering_module_instance_with_user_input

USER_INPUT_MOCK_SINGLE_MODULE_1 = (
    "tests/mocked_user_input/user_input_mock_single_module_1.json"
)
USER_INPUT_MOCK_SINGLE_MODULE_2 = (
    "tests/mocked_user_input/user_input_mock_single_module_2.json"
)
USER_INPUT_MOCK_SINGLE_MODULE_3 = (
    "tests/mocked_user_input/user_input_mock_single_module_3.json"
)
USER_INPUT_MOCK_SINGLE_PHASE_1 = (
    "tests/mocked_user_input/user_input_mock_single_phase_1.json"
)
USER_INPUT_MOCK_SINGLE_PHASE_2 = (
    "tests/mocked_user_input/user_input_mock_single_phase_2.json"
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
