from utils.utils import (
    print_generator_values,
    create_steering_module_instance_with_user_input,
)

USER_INPUT_MOCK = "tests/mocked_user_input/user_input_mock_single_phase_1.json"
# USER_INPUT_MOCK = "tests/mocked_user_input/user_input_mock_single_module_1.json"


def main():
    steering_module = create_steering_module_instance_with_user_input(USER_INPUT_MOCK)
    print_generator_values(steering_module.run())


if __name__ == "__main__":
    main()
