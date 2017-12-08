from typing import List

from PyQt5.QtWidgets import QFileDialog, QWidget

from src.utils.constants.defaults.non_qt import APSModelFile


def get_project_file(parent=None):
    openfile = QFileDialog.getOpenFileName(parent=parent, filter=APSModelFile.FILE_FILTER)
    path = openfile[0]
    return path


def get_attributes(obj: QWidget, names: List[str]) -> List[QWidget]:
    elements = []
    for name in names:
        if hasattr(obj, name):
            elements.append(obj.__getattribute__(name))
    return elements


def get_elements_with_prefix(obj: object, prefix: str) -> List[str]:
    return [item for item in dir(obj) if prefix == item[:len(prefix)]]
