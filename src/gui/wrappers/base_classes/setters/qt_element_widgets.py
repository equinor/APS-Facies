from PyQt5.QtWidgets import QLineEdit, QSlider

from src.gui.wrappers.base_classes.chekkers.values import should_change
from src.utils.numeric import normalize_number, strip_trailing_decimals
from src.utils.constants import Constraints


def set_value(
        item_that_should_changed: [QLineEdit, QSlider],
        value: float,
        normalize: bool = True,
        skip_signals: bool = False,
        force_change: bool = False,
        number_of_decimals: int = Constraints.DECIMALS
) -> None:
    if normalize:
        if isinstance(item_that_should_changed, QLineEdit):
            value = normalize_number(value, maximum_in=100, minimum_in=0, minimum_out=0, maximum_out=1)
        elif isinstance(item_that_should_changed, QSlider):
            value = normalize_number(value, maximum_in=1, minimum_in=0, minimum_out=0, maximum_out=100)
    _set_value(item_that_should_changed, value, skip_signals, force_change, number_of_decimals)


def _set_value(
        item_that_should_changed: [QLineEdit, QSlider],
        value: float,
        skip_signals: bool = False,
        force_change: bool = False,
        number_of_decimals: int = Constraints.DECIMALS
) -> None:
    assert isinstance(item_that_should_changed, QLineEdit) or isinstance(item_that_should_changed, QSlider)
    if force_change or should_change(value, item_that_should_changed):
        if skip_signals:
            item_that_should_changed.blockSignals(True)
        if isinstance(item_that_should_changed, QLineEdit):
            item_that_should_changed.setText(strip_trailing_decimals(value, number_of_decimals))
        elif isinstance(item_that_should_changed, QSlider):
            item_that_should_changed.setValue(int(value))
        if skip_signals:
            item_that_should_changed.blockSignals(False)
