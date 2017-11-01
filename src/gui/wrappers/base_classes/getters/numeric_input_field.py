import re

from PyQt5.QtWidgets import QLineEdit

numeric_zero_regex = re.compile("^[+-]?[.,]?$")
numeric_regex = re.compile("^[+-]?[0-9]+[.,]?[0-9]*$")
numeric_with_trailing_zero_regex = re.compile("^[+-]?[0-9]+\.[0-9]*$\.]")


def get_value_of_numeric_text_field(element: QLineEdit) -> str:
    assert isinstance(element, QLineEdit)
    # TODO: Rewrite to return str; allows 5.0 -> 5. -> 5.1 (backspace, and entering new)
    # TODO: Make sure the input is converted to a proper string when the time comes
    value = element.text().replace(',', '.')  # type: str
    if numeric_zero_regex.match(value):
        value = 0
    elif numeric_with_trailing_zero_regex.match(value):
        value = value[:-1]
    elif len(value) > 1 and value[0] == '0':
        value = value[1:]  # Remove non-trivial 0 prefix
    elif not numeric_regex.match(value):
        value = 0
    return str(value)


def get_number_from_numeric_text_field(element: QLineEdit) -> float:
    """
    Use this instead of `get_value_of_numeric_text_field`, when only the number is of interest.
    :param element: The input / text field from which we wish to get the value
    :type element: QLineEdit
    :return: The number written in the input field
    :rtype: float
    """
    return float(get_value_of_numeric_text_field(element))
