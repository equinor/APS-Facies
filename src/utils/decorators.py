from functools import wraps

from src.utils.constants.simple import Debug
from src.utils.debug import dump_debug_information


def cached(func):
    @wraps(func)
    def wrapper(self):
        name = '_' + func.__name__
        if not hasattr(self, name):
            result = func(self)
            setattr(self, name, result)
        return getattr(self, name)

    return wrapper


def loggable(func):
    @wraps(func)
    def wrapper(config):
        if config.error_message:
            return func(config)
        try:
            return func(config)
        except Exception as e:
            if config.debug_level >= Debug.ON:
                dump_debug_information(config)
            raise e

    return wrapper
