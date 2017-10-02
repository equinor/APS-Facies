from PyQt5.QtWidgets import QLineEdit, QSlider

from src.gui.wrappers.base_classes.getters.general import get_value_of_element


def should_change(value: float, item_that_should_changed: [QSlider, QLineEdit], esp: float = 0.01) -> bool:
    old_value = get_value_of_element(item_that_should_changed)
    # TODO: Check if they are sufficiently different
    return abs(old_value - value) > esp
