from src.utils.exceptions.base import ApsException


class InconsistencyError(ApsException):
    def __init__(self, class_name):
        super(InconsistencyError, self).__init__(
            "Error in {}\n"
            "Error: Inconsistency"
            "".format(class_name)
        )
