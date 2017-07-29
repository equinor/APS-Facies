#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

from PyQt5.Qt import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from src.ui import APS_prototype_ui


class APSGUI(QMainWindow, APS_prototype_ui.Ui_ZoneParameterName):
    def __init__(self):
        QMainWindow.__init__(self)


def run():
    # app = QApplication(sys.argv)
    app = QApplication(sys.argv)
    zone_parameter_name = QMainWindow()
    ui = APSGUI()
    ui.setupUi(zone_parameter_name)
    zone_parameter_name.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    run()
