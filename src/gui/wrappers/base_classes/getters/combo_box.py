from PyQt5.QtWidgets import QComboBox


def get_choice(element: QComboBox) -> str:
    return element.currentText()
