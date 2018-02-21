from src.utils.exceptions.base import ApsException


class InconsistencyError(ApsException):
    def __init__(self, class_name):
        super().__init__(
            "Error in {class_name}\n"
            "Error: Inconsistency"
            "".format(class_name=class_name)
        )
