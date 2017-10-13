from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QColorDialog

from src.gui.wrappers.base_classes.dialogs import OkCancelDialog
from src.utils.constants import Colors


class ColorPicker(QColorDialog, OkCancelDialog):
    def __init__(self, parent=None, initial_color=None, color_options=Colors.values()):
        super(ColorPicker, self).__init__(parent=parent)
        self.color_options = color_options
        # TODO: Implement selected color

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Escape:
            return None

    def get_color(self):
        # TODO: Catch the case of canceling
        color = self.getColor()
        return color
