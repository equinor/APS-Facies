#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

from PyQt5.QtWidgets import QApplication

from src.gui.wrappers.project import Project


def run():
    app = QApplication(sys.argv)
    ui = Project()
    ui.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    run()
