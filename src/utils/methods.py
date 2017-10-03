import xml.etree.ElementTree as ET
from typing import Dict, List, TypeVar, Union
from xml.dom import minidom

import numpy as np
from PyQt5.QtCore import QObject
from PyQt5.QtGui import QValidator
from PyQt5.QtWidgets import QWidget, QFileDialog, QCheckBox, QWidget

from src.utils.constants import Defaults, HideOptions

T = TypeVar('T')
U = TypeVar('U')


def prettify(elem):
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ", newl="\n")


def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def writeFile(fileName, a, nx, ny, printInfo=0):
    with open(fileName, 'w') as file:
        # Choose an arbitrary heading
        outstring = '-996  ' + str(ny) + '  50.000000     50.000000\n'
        outstring += '637943.187500   678043.187500  4334008.000000  4375108.000000\n'
        outstring += ' ' + str(nx) + ' ' + ' 0.000000   637943.187500  4334008.000000\n'
        outstring += '0     0     0     0     0     0     0\n'
        count = 0
        text = ''
        if printInfo >= 1:
            print('len(a): ' + str(len(a)))
        for j in range(len(a)):
            text = text + str(a[j]) + '  '
            count += 1
            if count >= 5:
                text += '\n'
                outstring += text
                count = 0
                text = ''
        if count > 0:
            outstring += text + '\n'
        file.write(outstring)
    print('Write file: ' + fileName)


def readFile(fileName, printInfo=0):
    print('Read file: ' + fileName)
    with open(fileName, 'r') as file:
        inString = file.read()
        words = inString.split()
        ny = int(words[1])
        nx = int(words[8])
        if printInfo >= 1:
            n = len(words)
            print('Number of words: ' + str(n))
            print('nx,ny: ' + str(nx) + ' ' + str(ny))
            print('Number of values: ' + str(len(words) - 19))
        a = np.zeros(nx * ny, float)
        for i in range(19, len(words)):
            a[i - 19] = float(words[i])
    return [a, nx, ny]


def toggle_elements(toggled: bool, elements: Union[List[QWidget], QWidget], deactivate_or_hide=Defaults.HIDE) -> None:
    assert deactivate_or_hide in HideOptions()
    if isinstance(elements, list):
        for element in elements:
            toggle_elements(toggled, element)
    elif isinstance(elements, QWidget):
        if deactivate_or_hide == HideOptions.HIDE:
            elements.setVisible(toggled)
        elif deactivate_or_hide == HideOptions.DISABLE:
            elements.setEnabled(toggled)
        else:
            raise ValueError
    else:
        raise TypeError


def get_project_file(parent=None):
    openfile = QFileDialog.getOpenFileName(parent=parent, filter=Defaults.FILE_FILTER)
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


def invert_dict(to_be_inverted: Dict[T, U]) -> Dict[U, T]:
    return {
        to_be_inverted[key]: key for key in to_be_inverted.keys()
    }


def apply_method_to(items: Union[List[QObject], QObject], method) -> None:
    if isinstance(items, list):
        for item in items:
            apply_method_to(item, method)
    else:
        method(items)


def apply_validator(elements: Union[List[QObject], QObject], validator: QValidator):
    apply_method_to(elements, lambda x: x.setValidator(validator))
