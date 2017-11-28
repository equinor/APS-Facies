from src.utils.exceptions.base import ApsException


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

    @staticmethod
    def get_value_specified_error_message(keyword, parent_keyword=None, model_file_name=None, end_with_period=True):
        message = "The value specified in the keyword '{keyword}'".format(keyword=keyword)
        if parent_keyword:
            message += ", underneath the parent keyword '{parent_keyword}'".format(parent_keyword=parent_keyword)
        if model_file_name:
            message += ", in the model file '{model_file_name}'".format(model_file_name=model_file_name)
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
        message = base_message + ', is LESS than the minimum value ({value} < {minimum})'.format(
            value=value,
            minimum=minimum
        )
        if end_with_period:
            message += '.'
        super(LessThanExpected, self).__init__(message)


class MoreThanExpected(ValueOutsideExpectedRange):
    def __init__(self, keyword, value, maximum, parent_keyword=None, model_file_name=None, end_with_period=True):
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
        if end_with_period:
            message += '.'
        super(MoreThanExpected, self).__init__(message)


class UndefinedZoneError(NameError):
    def __init__(self, zone_number: int):
        super(UndefinedZoneError, self).__init__(
            'Error: Zone number: {zone_number} is not defined'.format(zone_number=zone_number)
        )


class MissingAttributeInKeyword(KeyError):
    def __init__(self, keyword, attribute_name):
        super(MissingAttributeInKeyword, self).__init__(
            "The attribute '{attribute_name}' is required for the keyword '{keyword}'".format(
                attribute_name=attribute_name,
                keyword=keyword
            )
        )


class CrossSectionOutsideRange(ValueError):
    def __init__(self, cross_section_name, cross_section_index, upper_bound):
        super(CrossSectionOutsideRange, self).__init__(
            'Cross section index is specified to be: {cross_section_index} for {cross_section_name} cross section, '
            'but must be in interval [0, {upper_bound}]'.format(
                cross_section_index=cross_section_index,
                cross_section_name=cross_section_name,
                upper_bound=upper_bound
            )
        )
