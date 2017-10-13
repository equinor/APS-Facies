class ApsException(Exception):
    def __init__(self, message, errors=None):
        super(ApsException, self).__init__(message)
        self.errors = errors


class InconsistencyError(ApsException):
    def __init__(self, class_name):
        super(InconsistencyError, self).__init__(
            "Error in {}\n"
            "Error: Inconsistency"
            "".format(class_name)
        )


class ApsXmlError(ApsException, IOError):
    def __init__(self, message, errors=None):
        super(ApsXmlError, self).__init__(message=message, errors=errors)


class ReadingXmlError(ApsXmlError, IOError):
    def __init__(self, keyword, parent_keyword=None, model_file_name=None):
        message = self.get_keyword_error_message(keyword, parent_keyword, model_file_name)
        super(ReadingXmlError, self).__init__(message=message)

    @staticmethod
    def get_keyword_error_message(keyword, parent_keyword=None, model_file_name=None):
        if model_file_name:
            message = "The model file, '{file}', is missing the keyword '{keyword}'".format(
                file=model_file_name,
                keyword=keyword
            )
        else:
            message = "The keyword '{keyword}' is missing".format(keyword=keyword)
        if parent_keyword:
            message += " underneath the parent keyword '{keyword}'.".format(keyword=parent_keyword)
        else:
            message += '.'
        return message


class ValueOutsideExpectedRange(ApsXmlError):
    def __init__(self, message, errors=None):
        super(ValueOutsideExpectedRange, self).__init__(message=message, errors=errors)
        pass

    @staticmethod
    def get_value_specified_error_message(keyword, parent_keyword=None, model_file_name=None, end_with_period=True):
        message = "The value specified in the keyword '{keyword}'".format(keyword=keyword)
        if parent_keyword:
            message += ", underneath the parent keyword '{keyword}'".format(keyword=parent_keyword)
        if model_file_name:
            message += ", in the model file '{file_name}'".format(file_name=model_file_name)
        if end_with_period:
            message += '.'
        return message


class LessThanExpected(ValueOutsideExpectedRange):
    def __init__(self, keyword, value, minimum, parent_keyword=None, model_file_name=None):
        base_message = self.get_value_specified_error_message(
            keyword=keyword,
            parent_keyword=parent_keyword,
            model_file_name=model_file_name,
            end_with_period=False
        )
        message = base_message + ', is LESS than the minimum value ({value} < {minimum})'.format(
            value=value,
            minimum=minimum
        )
        super(LessThanExpected, self).__init__(message)


class MoreThanExpected(ValueOutsideExpectedRange):
    def __init__(self, keyword, value, maximum, parent_keyword=None, model_file_name=None):
        base_message = self.get_value_specified_error_message(
            keyword=keyword,
            parent_keyword=parent_keyword,
            model_file_name=model_file_name,
            end_with_period=False
        )
        message = base_message + ', is GREATER than the maximum value ({value} > {maximum})'.format(
            value=value,
            maximum=maximum
        )
        super(MoreThanExpected, self).__init__(message)
