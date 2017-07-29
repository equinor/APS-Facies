class APSException(Exception):
    def __init__(self, message, errors):
        super(APSException, self).__init__(message)
        self.errors = errors


class InconsistencyError(APSException):
    def __init__(self, class_name):
        super(InconsistencyError, self).__init__(
            "Error in {}\n"
            "Error: Inconsistency"
            "".format(class_name),
            errors=None
        )
