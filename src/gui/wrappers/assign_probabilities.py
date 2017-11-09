# -*- coding: utf-8 -*-
"""
A wrapper, and implementation of the window that lets the user assign probabilities
'Implements' the design in Assign_Probs.ui, and wraps around src/resources/ui/Assign_Probs_ui.py.
"""
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from src.resources.ui.Assign_Probs_ui import Ui_AssignProbabilities


class AssignProbabilities(QWidget, Ui_AssignProbabilities):
    def __init__(self, parent=None, content_in_combo_boxes=None, main_window=None, data=None):
        super(AssignProbabilities, self).__init__(parent)
        self.setupUi(self)
        self.retranslateUi(self)

        self.main_window = main_window

        # TODO: Make dynamic
        self.facies = 'facies'
        self.probability_cube = 'probability cube'
        self.keys = ['F1', 'F2', 'F3', 'F4', 'F5', ]
        self.choices_of_probability_cubes = [self.__getattribute__('m_choose_' + key) for key in self.keys]
        self.edit_facies = [self.__getattribute__('m_edit_' + key) for key in self.keys]
        self.inputs = {
            self.keys[i]: {
                self.facies: self.edit_facies[i],
                self.probability_cube: self.choices_of_probability_cubes[i]
            } for i in range(len(self.keys))
        }

        self.wire_up()
        self.set_content_in_combo_boxes(content_in_combo_boxes, data)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Escape:
            self.cancel()
        elif event.key() == Qt.Key_Return:
            self.send_probabilities()

    def wire_up(self):
        ok = QDialogButtonBox.Ok
        cancel = QDialogButtonBox.Cancel

        self.m_buttons_ok_cancel.button(ok).clicked.connect(self.send_probabilities)
        self.m_buttons_ok_cancel.button(cancel).clicked.connect(self.cancel)

    def set_content_in_combo_boxes(self, content_in_combo_boxes: dict = None, data: dict = None) -> None:
        if content_in_combo_boxes:
            assert len(content_in_combo_boxes) == len(self.choices_of_probability_cubes)
            for i in range(len(content_in_combo_boxes)):
                choices = self.choices_of_probability_cubes[i]
                content = content_in_combo_boxes[i]
                choices.addItems(content)
        if data:
            for key in data.keys():
                if self.facies in data[key]:
                    m_edit = self.inputs[key][self.facies]  # type: QLineEdit
                    m_edit.setText(data[key][self.facies])

                if self.probability_cube in data[key]:
                    m_choose = self.inputs[key][self.probability_cube]  # type: QComboBox
                    m_choose.setCurrentText(data[key][self.probability_cube])

    def send_probabilities(self):
        self.main_window.probabilities = self.get_facies()
        self.close()

    def cancel(self):
        # TODO: Remove everything from te dialog?
        self.close()

    def get_facies(self):
        data = {}
        for key in self.inputs.keys():
            data_point = self.inputs[key]
            text = data_point[self.facies].text()
            probability_cube = data_point[self.probability_cube].currentText()
            if key not in data:
                data[key] = {}
            if text:
                data[key][self.facies] = text
            if probability_cube:
                data[key][self.probability_cube] = probability_cube
        return data
