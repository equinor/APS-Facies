#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import argparse
from PyQt5.QtWidgets import QApplication

from src.gui.state import State
from src.gui.wrappers.project import Project
from src.gui.wrappers.truncation_rule import CubicTruncationRule, NonCubicTruncationRule, BayfillTruncationRule
from src.gui.wrappers.main_window import MainWindow
from src.gui.wrappers.define_gaussian import DefineGaussian

parser = argparse.ArgumentParser(
    prog="APS-GUI",
    description="A GUI for setting parameters to plurigaussian simulations."
)
parser.add_argument('--project', help="Starts the GUI with the given project file")
parser.add_argument('--version', action='version', version='%(prog)s 0.0.1')
parser.add_argument(
    '--verbosity',
    help="Sets the verbosity level. 0 is off, while 4 is the highest",
    type=int,
    choices=[0, 1, 2, 3, 4]
)
args = parser.parse_args()


def run():
    app = QApplication(sys.argv)
    ui = Project()
    # ui = CubicTruncationRule(State(), active=['F1', 'F2', 'F3', 'F4'])
    ui.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    run()
