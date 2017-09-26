from typing import Callable, Union, List

from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QLineEdit, QSlider

from src.gui.wrappers.base_classes.dialogs import OkCancelDialog
from utils.constants import Defaults


class BaseTruncation(OkCancelDialog):
    def __init__(self, parent=None, name_of_buttons=Defaults.NAME_OF_BUTTON_BOX):
        super(BaseTruncation, self).__init__(parent=parent, name_of_buttons=name_of_buttons)
        self.names = ['F1', 'F2', 'F3', 'F4', 'F5']

    def wire_up(self):
        super(BaseTruncation, self).wire_up(ok=self.save, cancel=self.close)

    def save(self):
        # TODO: Implement
        pass

    def calculate_sums(self):
        total_sum = [float(self.__getattribute__('m_edit_proportion_' + key).text()) for key in self.names]
        pass

    def _proportion_value_changed(
            self,
            item_that_should_changed: [QLineEdit, QSlider]
    ) -> Callable[[QLineEdit, QSlider], None]:
        return lambda _: self._update_proportions(item_that_should_changed)

    def _update_proportions(self, item_that_should_changed: [QLineEdit, QSlider]) -> None:
        # TODO: Mapping
        sender = self.sender()
        value = self._get_value(sender)
        if isinstance(item_that_should_changed, QLineEdit):
            value = self._normalize(value, maximum_in=100, minimum_in=0, minimum_out=0, maximum_out=1)
            if self.should_change(value, item_that_should_changed):
                item_that_should_changed.setText(str(value))
        elif isinstance(item_that_should_changed, QSlider):
            value = self._normalize(value, maximum_in=1, minimum_in=0, minimum_out=0, maximum_out=100)
            if self.should_change(value, item_that_should_changed):
                item_that_should_changed.setValue(int(value))
            pass
        pass

    def connect_slider_and_text(self, slider, line_edit):
        slider.valueChanged[int].connect(self._proportion_value_changed(line_edit))
        line_edit.textChanged.connect(self._proportion_value_changed(slider))
        pass

    @staticmethod
    def _get_value(sender: [QLineEdit, QSlider]) -> Union[float, int]:
        # TODO
        if isinstance(sender, QSlider):
            return sender.value()
            pass
        elif isinstance(sender, QLineEdit):
            value = sender.text()
            # TODO: Make more robust. Alt. borrow from similar method in CRIS
            if value == '':
                return 0
            elif ',' in value:
                value = value.replace(',', '.')
            if value == '.':
                value = 0
            return float(value)
        return -1
        pass

    @staticmethod
    def _normalize(value: float, minimum_in: float, maximum_in: float, minimum_out: float, maximum_out: float) -> float:
        # TODO: Write unit test(s)
        assert minimum_in < maximum_in
        assert minimum_out < maximum_out
        normalized = (value - minimum_in) / (maximum_in - minimum_in)
        return normalized * (maximum_out - minimum_out) + minimum_out

    @staticmethod
    def apply_method_to(items: [List[QObject], QObject], method) -> None:
        if isinstance(items, list):
            for item in items:
                BaseTruncation.apply_method_to(item, method)
        else:
            method(items)

    @staticmethod
    def should_change(value: float, item_that_should_changed: [QSlider, QLineEdit], esp=0.01) -> bool:
        old_value = BaseTruncation._get_value(item_that_should_changed)
        # TODO: Check if they are sufficiently different
        return abs(old_value - value) > esp
