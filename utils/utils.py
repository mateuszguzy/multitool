import json
from collections.abc import Generator

from modules.core.steering_module import SteeringModule


def print_generator_values(generator: Generator) -> None:
    for value in generator:
        print(value)


def create_steering_module_instance_with_user_input(path: str):
    test_input = open(path)
    steering_module = SteeringModule(json.load(test_input))

    return steering_module
