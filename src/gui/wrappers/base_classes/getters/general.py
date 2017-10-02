from typing import Union

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QComboBox, QLineEdit, QPushButton, QSlider

from src.gui.wrappers.base_classes.getters.color import get_color
from src.gui.wrappers.base_classes.getters.combo_box import get_choice
from src.gui.wrappers.base_classes.getters.numeric_input_field import get_value_of_numeric_text_field
from src.gui.wrappers.base_classes.getters.slider import get_value_of_slider


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
