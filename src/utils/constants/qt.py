from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMessageBox

from src.utils.constants.base import Icon, Value


class MessageIcon(Icon):
    NO_ICON = QMessageBox.NoIcon
    QUESTION_ICON = QMessageBox.Question
    INFORMATION_ICON = QMessageBox.Information
    WARNING_ICON = QMessageBox.Warning
    CRITICAL_ICON = QMessageBox.Critical


class Colors(Value):
    LAWN_GREEN = QColor('lawngreen')  # Hex code: #7CFC00
    GRAY = QColor('gray')  # Hex code: #808080
    DODGER_BLUE = QColor('dodgerblue')  # Hex code: #1E90FF
    GOLD = QColor('gold')  # Hex code: #D4AF37
    DARK_ORCHID = QColor('darkorchid')  # Hex code: #9932CC
    CYAN = QColor('cyan')  # Hex code: #00B7EB
    FIREBRICK = QColor('firebrick')  # Hex code: #B22222
    OLIVE_DRAB = QColor('olivedrab')  # Hex code: #6B8E23
    BLUE = QColor('blue')  # Hex code: #0000FF
    CRIMSON = QColor('crimson')  # Hex code: #DC143C
    DARK_ORANGE = QColor('darkorange')  # Hex code: #FF8C00
    RED = QColor('red')  # Hex code: #FF0000
    BACKGROUND = QColor('#EFEBE7')
