import re
from PyQt5.QtWidgets import QLineEdit

numeric_zero_regex = re.compile("^[+-]?[.,]?$")


def get_value_of_numeric_text_field(element: QLineEdit) -> float:
    assert isinstance(element, QLineEdit)
    value = element.text().replace(',', '.')  # type: str
    if numeric_zero_regex.match(value):
        value = 0
    return float(value)
