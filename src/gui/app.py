#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

from PyQt5.QtWidgets import QApplication

from src.gui.wrappers.main_window import MainWindow


def run():
    app = QApplication(sys.argv)
    # zone_parameter_name = QMainWindow()
    ui = MainWindow()
    # ui.setupUi(zone_parameter_name)
    ui.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    run()
