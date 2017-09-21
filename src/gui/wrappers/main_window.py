# -*- coding: utf-8 -*-
"""
A wrapper, and implementation of the main GUI window of the APS-GUI.
'Implements' the design in APS_prototype.ui, and wraps around src/resources/ui/APS_prototype_ui.py.
"""
import sys
from typing import List

from PyQt5.Qt import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from src.gui.state import State
from src.resources.ui.APS_prototype_ui import Ui_MainWindow
from src.gui.wrappers.base_classes import MessageBox

from src.gui.wrappers.assign_probabilities import AssignProbabilities
from src.utils.checks import is_valid_path

from src.utils.constants import ModeConstants, Defaults
from src.utils.methods import toggle_elements, get_project_file


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None, state: State=None):
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
        self.m_toggle_seperate_zone_models.stateChanged.connect(self._toggle_separate_zone_models)
        self.m_toggle_select_facies.stateChanged.connect(self._toggle_select_facies)
        self.m_toggle_experimental_mode.clicked.connect(self._toggle_experimental_mode)
        self.m_toggle_condition_to_wells.clicked.connect(self._condition_to_wells)

        self.initialize_truncation_rules()
        self.initialize_project_data()

        self._set_checkboxes_to_defaults()

    def initialize_project_data(self):
        # TODO: Read from the project data
        if self._state:
            for key in self._state.keys():
                if key == ModeConstants.EXECUTION_MODE and self._state.is_experimental_mode():
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

    def initialize_truncation_rules(self):
        library = {
            'cubic': {key: self.__getattribute__('m_button_type_' + key) for key in 'abcdefghijklmnopqrstuvw'},
            'num-cubic': {key: self.__getattribute__('m_button_type_' + key) for key in ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII']},
            'bayfill': self.m_button_bayfill,
            'custom': self.m_button_type_customized,
        }
        pass

    def _toggle_separate_zone_models(self):
        checkbox = self.m_toggle_seperate_zone_models
        elements = [
            self.label_available_zones, self.label_selected_zones, self.label_zones_to_be_modeled,
            self.m_list_available_zones, self.m_list_selected_zones, self.m_button_add_zone, self.m_button_remove_zone
        ]
        toggle_elements(checkbox, elements)

    def _toggle_select_facies(self):
        checkbox = self.m_toggle_select_facies
        elements = [
            self.label_available_facies, self.label_facies_to_be_modelled, self.label_selected_facies,
            self.m_list_available_facies, self.m_list_selected_facies, self.m_button_add_facies,
            self.m_button_remove_facies, self.m_button_add_new_facies, self.m_button_remove_selected,
        ]
        toggle_elements(checkbox, elements)

    def _set_checkboxes_to_defaults(self):
        self.m_toggle_seperate_zone_models.setCheckState(Defaults.SEPARATE_ZONE_MODELS)
        self.m_toggle_select_facies.setCheckState(Defaults.FACIES_MODELS)
        self._toggle_separate_zone_models()
        self._toggle_select_facies()

    def _toggle_experimental_mode(self):
        use_experimental_mode = self.m_toggle_experimental_mode.isChecked()
        if not use_experimental_mode and not self._state.has_valid_path():
            # The state is invalid, and the user must choose a project file

            # The user will get a dialog, asking them to choose a model file
            MessageBox(text="Please give a model file.", parent=self).exec()
            path = get_project_file(parent=self)
            if is_valid_path(path):
                self._state.set_project_path(path)
            else:
                self._state.set_experimental_mode()
                self.m_toggle_experimental_mode.setChecked(True)
        elif use_experimental_mode:
            # TODO:
            pass

    def _condition_to_wells(self):
        # TODO: Implement
        pass
