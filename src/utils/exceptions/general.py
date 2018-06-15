from src.utils.exceptions.base import ApsException


class InconsistencyError(ApsException):
    def __init__(self, class_name):
        super().__init__(
            "Error in {class_name}\n"
            "Error: Inconsistency"
            "".format(class_name=class_name)
        )


def raise_error(function_name, text):
    raise ValueError(
        'Error in {function_name}: {text}'
        ''.format(function_name=function_name, text=text)
    )
