from aps.utils.exceptions.base import ApsException


class InconsistencyError(ApsException):
    def __init__(self, class_name):
        super().__init__(f'Error in {class_name}\nError: Inconsistency')


def raise_error(function_name, text):
    raise ValueError(f'Error in {function_name}: {text}')
