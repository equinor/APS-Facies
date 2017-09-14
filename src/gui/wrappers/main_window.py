# -*- coding: utf-8 -*-
"""
A wrapper, and implementation of the main GUI window of the APS-GUI.
'Implements' the design in APS_prototype.ui, and wraps around src/resources/ui/APS_prototype_ui.py.
"""
import sys

from PyQt5.Qt import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from src.resources.ui import APS_prototype_ui

from src.gui.wrappers.assign_probabilities import AssignProbabilities


class MainWindow(QMainWindow, APS_prototype_ui.Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.retranslateUi(self)

        self.wire_up()
        self.probabilities = None

    def wire_up(self):
        self.m_button_assign_probability.clicked.connect(self.assign_probabilities)
        self.m_button_close.clicked.connect(self.close)

    def assign_probabilities(self, content_in_combo_boxes=None):
        # TODO: Read from file, and give that as input
        content_in_combo_boxes = [
            ['', 'yes', 'no'],
            [''],
            ['', 'birthday'],
            [''],
            [''],
        ]
        sender = self.sender()
        self.probabilities = AssignProbabilities(
            content_in_combo_boxes=content_in_combo_boxes,
            main_window=self,
            data=self.probabilities
        )
        self.probabilities.show()
        self.statusBar().showMessage("Clicked on button!")
        pass

    @pyqtSlot(dict, QWidget)
    def get_probabilities(self, data, source):
        print(data)
        pass
