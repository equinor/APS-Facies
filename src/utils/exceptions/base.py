class ApsException(Exception):
    def __init__(self, message, errors=None):
        super(ApsException, self).__init__(message)
        self.errors = errors
