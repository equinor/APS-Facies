from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QWidget


def set_color(element: QWidget, color: QColor) -> None:
    pallet = element.palette()
    pallet.setColor(QPalette.Button, color)
    element.setAutoFillBackground(True)
    element.setPalette(pallet)
    element.update()
