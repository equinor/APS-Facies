from PyQt5.QtWidgets import QMessageBox

from src.utils.constants.qt import MessageIcon


class MessageBox(QMessageBox):
    def __init__(self, text: str, icon: QMessageBox.Icon = None, parent=None) -> None:
        super(MessageBox, self).__init__(parent=parent)
        self.setText(text)
        if icon and icon in MessageIcon():
            self.setIcon(icon)
