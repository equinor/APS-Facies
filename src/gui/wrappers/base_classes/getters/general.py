from typing import Union, List, Iterable

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QComboBox, QLineEdit, QPushButton, QSlider, QCheckBox, QListWidget

from src.gui.wrappers.base_classes.getters.color import get_color
from src.gui.wrappers.base_classes.getters.combo_box import get_choice
from src.gui.wrappers.base_classes.getters.numeric_input_field import get_value_of_numeric_text_field
from src.gui.wrappers.base_classes.getters.slider import get_value_of_slider
from src.utils.constants.non_qt import BaseNames, TruncationRuleLibraryElements, FaciesLabels


def get_value_of_element(element: Union[QLineEdit, QSlider, QPushButton, QComboBox]) -> Union[float, int, QColor, str]:
    # TODO
    if isinstance(element, QSlider):
        return get_value_of_slider(element)
    elif isinstance(element, QLineEdit):
        return get_value_of_numeric_text_field(element)
    elif isinstance(element, QPushButton):
        return get_color(element)
    elif isinstance(element, QComboBox):
        return get_choice(element)
    else:
        raise TypeError


def get_elements_from_base_name(
        obj: object,
        property_name: BaseNames,
        facies_names: List[FaciesLabels],
) -> Union[List[QPushButton], List[QLineEdit], List[QSlider]]:
    names = []
    if hasattr(obj, property_name):
        element_type = get_element(obj, property_name)
        if isinstance(facies_names, list) and all(isinstance(name, str) for name in facies_names):
            names = [element_type + name for name in facies_names]
        else:
            names = facies_names
        return get_elements(obj, names)
    return names


def get_elements(
        obj: object,
        names: Iterable[str]
) -> Union[List[QPushButton], List[QLineEdit], List[QSlider]]:
    elements = []
    if isinstance(names, Iterable) and len(names) > 1:
        for name in names:
            element = get_element(obj, name)
            if element is not None:
                elements.append(element)
    return elements


def get_element(
        obj: object,
        name: str
) -> Union[QPushButton, QLineEdit, QSlider, QCheckBox, TruncationRuleLibraryElements, QListWidget, QComboBox, None]:
    # TODO: Make more robust
    if hasattr(obj, name):
        return obj.__getattribute__(name)
    return None
