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

from src.utils.constants import ModeConstants
from src.utils.checks import is_experimental_mode


class MainWindow(QMainWindow, APS_prototype_ui.Ui_MainWindow):
    def __init__(self, parent=None, state=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.retranslateUi(self)

        self._state = state
        self._project_data = None
        if self._state:
            # TODO: Is project_data really necessary
            self._project_data = self._state.get_project_data()
        self.wire_up()
        self.probabilities = None

    def wire_up(self):
        self.m_button_assign_probability.clicked.connect(self.assign_probabilities)
        self.m_button_close.clicked.connect(self.close)
        self.initialize_project_data()

    def initialize_project_data(self):
        # TODO: Read from the project data
        if self._state:
            for key in self._state.keys():
                if key == ModeConstants.EXECUTION_MODE and is_experimental_mode(self._state[key]):
                    self.m_toggle_experimental_mode.setChecked(True)
                pass

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
        pass
