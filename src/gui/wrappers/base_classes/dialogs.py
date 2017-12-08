from typing import Callable, Dict

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QDialogButtonBox, QDialog

from src.utils.constants.defaults.non_qt import UI


class GeneralDialog(QDialogButtonBox, QDialog):
    def __init__(self, parent=None, name_of_buttons=UI.NAME_OF_BUTTON_BOX, **kwargs):
        # TODO: Make name_of_buttons into a constant
        super(GeneralDialog, self).__init__(parent=parent)
        self.valid_buttons = self._get_valid_buttons()

        self.name_of_buttons = name_of_buttons
        self.setWindowModality(Qt.ApplicationModal)
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
        # TODO: Make Constants
        return {
            'ok': QDialogButtonBox.Ok,
            'open': QDialogButtonBox.Open,
            'save': QDialogButtonBox.Save,
            'cancel': QDialogButtonBox.Cancel,
            'close': QDialogButtonBox.Close,
            'discard': QDialogButtonBox.Discard,
            'apply': QDialogButtonBox.Apply,
            'reset': QDialogButtonBox.Reset,
            'restore_defaults': QDialogButtonBox.RestoreDefaults,
            'help': QDialogButtonBox.Help,
            'save_all': QDialogButtonBox.SaveAll,
            'yes': QDialogButtonBox.Yes,
            'yes_to_all': QDialogButtonBox.YesToAll,
            'no': QDialogButtonBox.No,
            'no_to_all': QDialogButtonBox.NoToAll,
            'abort': QDialogButtonBox.Abort,
            'retry': QDialogButtonBox.Retry,
            'ignore': QDialogButtonBox.Ignore,
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
    def __init__(self, parent=None, name_of_buttons=UI.NAME_OF_BUTTON_BOX):
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
    def __init__(self, parent=None, name_of_buttons=UI.NAME_OF_BUTTON_BOX):
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
