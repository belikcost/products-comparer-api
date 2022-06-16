from argparse import ArgumentTypeError
from typing import Callable


def validate(expected_type: Callable, constraint: Callable):
    def wrapper(value):
        value = expected_type(value)
        if not constraint(value):
            raise ArgumentTypeError


positive_int = validate(int, lambda x: x > 0)
