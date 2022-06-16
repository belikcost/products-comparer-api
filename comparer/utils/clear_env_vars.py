import os
from typing import Callable


def clear_env_vars(rule: Callable):
    for name in filter(rule, tuple(os.environ)):
        os.environ.pop(name)
