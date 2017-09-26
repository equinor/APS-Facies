from typing import Callable, List, Union, Dict

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from src.utils.constants import Defaults, MessageIcon


class MessageBox(QMessageBox):
    def __init__(self, text: str, icon: QMessageBox.Icon = None, parent=None) -> None:
        super(MessageBox, self).__init__(parent=parent)
        self.setText(text)
        if icon and icon in MessageIcon():
            self.setIcon(icon)


class GeneralDialog(QDialogButtonBox):
    def __init__(self, parent=None, name_of_buttons=Defaults.NAME_OF_BUTTON_BOX, **kwargs):
        # TODO: Make name_of_buttons into a constant
        super(GeneralDialog, self).__init__(parent=parent)
        self.valid_buttons = self._get_valid_buttons()

        self.name_of_buttons = name_of_buttons
        if kwargs:
            self.wire_up(**kwargs)

    def connect_button(self, button: QDialogButtonBox.StandardButton, fun: Callable) -> None:
        self.__getattribute__(self.name_of_buttons).button(button).clicked.connect(fun)

    def click_button(self, button: QDialogButtonBox.StandardButton) -> None:
        self.__getattribute__(self.name_of_buttons).button(button).click()

    def wire_up(self, **kwargs) -> None:
        if not self._has_valid_keys(**kwargs):
            raise ValueError("The keys, {} are not valid".format(kwargs.keys()))
        for key in kwargs:
            button = self.valid_buttons[key]
            fun = kwargs[key]
            self.connect_button(button, fun)

    def keyPressEvent(self, event: QKeyEvent):
        pass

    @staticmethod
    def _get_valid_buttons() -> Dict[str, QDialogButtonBox.StandardButton]:
        return {
            'ok':               QDialogButtonBox.Ok,
            'open':             QDialogButtonBox.Open,
            'save':             QDialogButtonBox.Save,
            'cancel':           QDialogButtonBox.Cancel,
            'close':            QDialogButtonBox.Close,
            'discard':          QDialogButtonBox.Discard,
            'apply':            QDialogButtonBox.Apply,
            'reset':            QDialogButtonBox.Reset,
            'restore_defaults': QDialogButtonBox.RestoreDefaults,
            'help':             QDialogButtonBox.Help,
            'save_all':         QDialogButtonBox.SaveAll,
            'yes':              QDialogButtonBox.Yes,
            'yes_to_all':       QDialogButtonBox.YesToAll,
            'no':               QDialogButtonBox.No,
            'no_to_all':        QDialogButtonBox.NoToAll,
            'abort':            QDialogButtonBox.Abort,
            'retry':            QDialogButtonBox.Retry,
            'ignore':           QDialogButtonBox.Ignore,
        }

    @staticmethod
    def _has_valid_keys(**kwargs):
        buttons = GeneralDialog._get_valid_buttons()
        valid_keys = buttons.keys()
        for key in kwargs.keys():
            if key not in valid_keys:
                return False
            # TODO: Check for valid function in kwargs?
        return True


class OkDialog(GeneralDialog):
    def __init__(self, parent=None, name_of_buttons=Defaults.NAME_OF_BUTTON_BOX):
        # TODO: Make name_of_buttons into a constant
        super(OkDialog, self).__init__(parent=parent, name_of_buttons=name_of_buttons)

    def wire_up(self, ok=None):
        if ok is None:
            ok = self.save
        super(OkDialog, self).wire_up(ok=ok)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Return:
            self.click_button(QDialogButtonBox.Ok)

    def save(self):
        pass


class OkCancelDialog(OkDialog):
    def __init__(self, parent=None, name_of_buttons=Defaults.NAME_OF_BUTTON_BOX):
        super(OkCancelDialog, self).__init__(parent=parent, name_of_buttons=name_of_buttons)

    def wire_up(self, ok: Callable = None, cancel: Callable = None) -> None:
        super(OkCancelDialog, self).wire_up(ok=ok)
        if cancel is None:
            cancel = self.close
        super(OkDialog, self).wire_up(cancel=cancel)

    def keyPressEvent(self, event: QKeyEvent):
        super(OkCancelDialog, self).keyPressEvent(event)
        if event.key() == Qt.Key_Escape:
            self.click_button(QDialogButtonBox.Cancel)


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
