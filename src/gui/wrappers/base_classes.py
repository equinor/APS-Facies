from typing import List, Union, Callable

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from src.utils.constants import MessageIcon, Defaults


class MessageBox(QMessageBox):
    def __init__(self, text: str, icon: QMessageBox.Icon = None, parent=None) -> None:
        super(MessageBox, self).__init__(parent=parent)
        self.setText(text)
        if icon and icon in MessageIcon():
            self.setIcon(icon)


class Dialog(QDialogButtonBox):
    def __init__(self, parent=None, name_of_buttons=Defaults.NAME_OF_BUTTON_BOX):
        # TODO: Make name_of_buttons into a constant
        super(Dialog, self).__init__(parent=parent)
        self.name_of_buttons = name_of_buttons

    def connect_button(self, button: QDialogButtonBox.StandardButton, fun: Callable) -> None:
        self.__getattribute__(self.name_of_buttons).button(button).clicked.connect(fun)

    def click_button(self, button: QDialogButtonBox.StandardButton) -> None:
        self.__getattribute__(self.name_of_buttons).button(button).click()

    def wire_up(self, ok: Callable = lambda _: _) -> None:
        self.connect_button(QDialogButtonBox.Ok, ok)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Return:
            self.click_button(QDialogButtonBox.Ok)


class OkCancelDialog(Dialog):
    def __init__(self, parent=None):
        super(OkCancelDialog, self).__init__(parent=parent)

    def wire_up(self, ok: Callable = lambda _: _, cancel: Callable = lambda _: _) -> None:
        super(OkCancelDialog, self).wire_up(ok=ok)
        self.connect_button(QDialogButtonBox.Cancel, cancel)

    def keyPressEvent(self, event: QKeyEvent):
        super(OkCancelDialog, self).keyPressEvent(event)
        if event.key() == Qt.Key_Escape:
            self.click_button(QDialogButtonBox.Cancel)


class BaseTruncation(OkCancelDialog):
    def __init__(self, parent=None):
        super(BaseTruncation, self).__init__(parent=parent)
        self.names = ['F1', 'F2', 'F3', 'F4', 'F5']

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
            value = self._normalize(value, maximum_in=99, minimum_in=0, minimum_out=0, maximum_out=1)
            item_that_should_changed.setText(str(value))
            sender.blockSignals(True)
        elif isinstance(item_that_should_changed, QSlider):
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
