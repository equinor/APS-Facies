from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QPushButton


def get_color(element: QPushButton) -> QColor:
    return element.palette().button().color()


def get_color_name(color: QColor, name_format: QColor.NameFormat = QColor.HexRgb) -> str:
    return color.name(name_format)
