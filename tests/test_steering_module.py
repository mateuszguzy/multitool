from unittest.mock import patch

from modules.core.steering_module import SteeringModule


def test_run_single_module(test_input_1):
    """
    Test function for running single module.
    """
    mocked_output = f"Running: {test_input_1.module}"
    output_to_check = str()

    with patch.object(
        SteeringModule, f"_{test_input_1.module}", return_value=mocked_output
    ):
        returned_generator = test_input_1._run_module(module=test_input_1.module)
        for value in returned_generator:
            output_to_check += value

    assert output_to_check == mocked_output


def test_run_single_phase(test_input_2):
    """
    Test function for running single phase.
    """
    mocked_output = f"Running: all {test_input_2.phase} modules"
    output_to_check = str()

    with patch.object(
        SteeringModule, f"_run_{test_input_2.phase}", return_value=mocked_output
    ):
        returned_generator = test_input_2._run_phase(phase=test_input_2.phase)
        for value in returned_generator:
            output_to_check += value

    assert output_to_check == mocked_output
