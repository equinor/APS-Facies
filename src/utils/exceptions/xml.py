from src.utils.exceptions.base import ApsException


class ApsXmlError(ApsException, IOError):
    def __init__(self, message, errors=None):
        super().__init__(message=message, errors=errors)


class ReadingXmlError(ApsXmlError, IOError):
    def __init__(self, keyword, parent_keyword=None, model_file_name=None):
        message = self.get_keyword_error_message(keyword, parent_keyword, model_file_name)
        super().__init__(message=message)

    @staticmethod
    def get_keyword_error_message(keyword, parent_keyword=None, model_file_name=None):
        if model_file_name:
            message = f"The model file, '{model_file_name}', is missing the keyword '{keyword}'"
        else:
            message = f"The keyword '{keyword}' is missing"
        if parent_keyword:
            message += f" underneath the parent keyword '{parent_keyword}'."
        else:
            message += '.'
        return message


class MissingRequiredValue(ReadingXmlError):
    @staticmethod
    def get_keyword_error_message(keyword, parent_keyword=None, model_file_name=None):
        if model_file_name:
            message = f"The model file, '{model_file_name}', has no value for the keyword '{keyword}'"
        else:
            message = f"No value for keyword '{keyword}'"
        if parent_keyword:
            message += f" underneath the parent keyword '{parent_keyword}'."
        else:
            message += '.'
        return message



class ValueOutsideExpectedRange(ApsXmlError):
    def __init__(self, message, errors=None):
        super().__init__(message=message, errors=errors)

    @staticmethod
    def get_value_specified_error_message(keyword, parent_keyword=None, model_file_name=None, end_with_period=True):
        message = f"The value specified in the keyword '{keyword}'"
        if parent_keyword:
            message += f", underneath the parent keyword '{parent_keyword}'"
        if model_file_name:
            message += f", in the model file '{model_file_name}'"
        if end_with_period:
            message += '.'
        return message


class LessThanExpected(ValueOutsideExpectedRange):
    def __init__(self, keyword, value, minimum, parent_keyword=None, model_file_name=None, end_with_period=True):
        base_message = self.get_value_specified_error_message(
            keyword=keyword,
            parent_keyword=parent_keyword,
            model_file_name=model_file_name,
            end_with_period=False
        )
        message = base_message + f', is LESS than the minimum value ({value} < {minimum})'
        if end_with_period:
            message += '.'
        super().__init__(message)


class MoreThanExpected(ValueOutsideExpectedRange):
    def __init__(self, keyword, value, maximum, parent_keyword=None, model_file_name=None, end_with_period=True):
        base_message = self.get_value_specified_error_message(
            keyword=keyword,
            parent_keyword=parent_keyword,
            model_file_name=model_file_name,
            end_with_period=False
        )
        message = base_message + f', is GREATER than the maximum value ({value} > {maximum})'
        if end_with_period:
            message += '.'
        super().__init__(message)


class UndefinedZoneError(NameError):
    def __init__(self, zone_number: int):
        super().__init__(f'Error: Zone number: {zone_number} is not defined')


class MissingAttributeInKeyword(KeyError):
    def __init__(self, keyword, attribute_name):
        super().__init__(f"The attribute '{attribute_name}' is required for the keyword '{keyword}'")


class CrossSectionOutsideRange(ValueError):
    def __init__(self, cross_section_name, cross_section_index, upper_bound):
        super().__init__(
            f'Cross section index is specified to be: {cross_section_index} for {cross_section_name} cross section, '
            f'but must be in the interval [0, {upper_bound}]'
        )


class MissingKeyword(IOError):
    def __init__(self, keyword, model_file=None):
        message = ''
        if model_file:
            message = f'Error reading {model_file}\n'
        message += f'Error missing command: {keyword}'
        super().__init__(message)
