from PyQt5.QtWidgets import *

from src.utils.constants import MessageIcon


class MessageBox(QMessageBox):
    def __init__(self, text: str, icon: QMessageBox.Icon = None, parent=None) -> None:
        super(MessageBox, self).__init__(parent=parent)
        self.setText(text)
        if icon and icon in MessageIcon():
            self.setIcon(icon)
