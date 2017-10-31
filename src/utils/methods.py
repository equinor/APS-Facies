from typing import Dict, List, TypeVar, Union

from PyQt5.QtCore import QObject
from PyQt5.QtGui import QValidator
from PyQt5.QtWidgets import QFileDialog, QWidget

from src.utils.constants.constants import Defaults, HideOptions

T = TypeVar('T')
U = TypeVar('U')


def toggle_elements(toggled: bool, elements: Union[List[QWidget], QWidget], deactivate_or_hide=Defaults.HIDE) -> None:
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


def get_project_file(parent=None):
    openfile = QFileDialog.getOpenFileName(parent=parent, filter=Defaults.FILE_FILTER)
    path = openfile[0]
    return path


def get_attributes(obj: QWidget, names: List[str]) -> List[QWidget]:
    elements = []
    for name in names:
        if hasattr(obj, name):
            elements.append(obj.__getattribute__(name))
    return elements


def get_elements_with_prefix(obj: object, prefix: str) -> List[str]:
    return [item for item in dir(obj) if prefix == item[:len(prefix)]]


def invert_dict(to_be_inverted: Dict[T, U]) -> Dict[U, T]:
    return {
        to_be_inverted[key]: key for key in to_be_inverted.keys()
    }


def apply_method_to(items: Union[List[QObject], QObject], method) -> None:
    if isinstance(items, list):
        for item in items:
            apply_method_to(item, method)
    else:
        method(items)


def apply_validator(elements: Union[List[QObject], QObject], validator: QValidator):
    apply_method_to(elements, lambda x: x.setValidator(validator))
