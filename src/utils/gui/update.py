from typing import Union, List

from PyQt5.QtCore import QObject
from PyQt5.QtGui import QValidator
from PyQt5.QtWidgets import QWidget, QLineEdit

from src.gui.wrappers.base_classes.getters.numeric_input_field import get_value_of_numeric_text_field
from src.gui.wrappers.base_classes.setters.qt_element_widgets import set_value
from src.utils.constants.non_qt import HideOptions, Constraints
from src.utils.constants.defaults.non_qt import Hide
from src.utils.numeric import truncate_number


def toggle_elements(toggled: bool, elements: Union[List[QWidget], QWidget], deactivate_or_hide=Hide.HIDE) -> None:
    assert deactivate_or_hide in HideOptions()
    if isinstance(elements, list):
        for element in elements:
            toggle_elements(toggled, element)
    elif isinstance(elements, QWidget):
        if deactivate_or_hide == HideOptions.HIDE:
            elements.setVisible(toggled)
        elif deactivate_or_hide == HideOptions.DISABLE:
            elements.setEnabled(toggled)
        else:
            raise ValueError
    else:
        raise TypeError


def apply_method_to(items: Union[List[QObject], QObject], method) -> None:
    if isinstance(items, list):
        for item in items:
            apply_method_to(item, method)
    else:
        method(items)


def apply_validator(elements: Union[List[QObject], QObject], validator: QValidator):
    apply_method_to(elements, lambda x: x.setValidator(validator))


def update_numeric(
        element: QLineEdit,
        minimum_truncation: float,
        maximum_truncation: float,
        number_of_decimals: int = Constraints.DECIMALS
) -> None:
    value = get_value_of_numeric_text_field(element)
    value = truncate_number(minimum_truncation, value, maximum_truncation)
    set_value(element, value, normalize=False, skip_signals=True, force_change=True,
              number_of_decimals=number_of_decimals)
