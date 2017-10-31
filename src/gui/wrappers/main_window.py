# -*- coding: utf-8 -*-
"""
A wrapper, and implementation of the main GUI window of the APS-GUI.
'Implements' the design in APS_prototype.ui, and wraps around src/resources/ui/APS_prototype_ui.py.
"""
from typing import Callable, Dict, Union

from PyQt5.QtWidgets import *

from src.gui.state import State
from src.gui.wrappers.assign_probabilities import AssignProbabilities
from src.gui.wrappers.base_classes.getters.general import get_element, get_elements
from src.gui.wrappers.base_classes.message_box import MessageBox
from src.gui.wrappers.define_gaussian import DefineGaussian
from src.gui.wrappers.dialogs import AddFacies
from src.gui.wrappers.truncation_rule import (
    BayfillTruncationRule, CubicTruncationRule, CustomTruncationRule,
    NonCubicTruncationRule,
)
from src.resources.ui.APS_prototype_ui import Ui_MainWindow
from src.utils.checks import is_valid_path
from src.utils.constants.constants import (
    Defaults, FaciesSelectionElements, GaussianRandomFieldElements, MainWindowElements,
    ModeConstants, TruncationLibraryKeys, TruncationLibrarySubKeys, ZoneSelectionElements,
)
from src.utils.mappings import truncation_library_button_to_kind_and_number_of_facies, truncation_library_elements
from src.utils.methods import get_project_file, toggle_elements


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None, state: State = None):
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
        self.gaussian_settings = None
        self.new_facies_dialog = None

    def wire_up(self):
        self.wire_up_navigation()
        self.wire_up_selections()

        self.initialize_truncation_rules()
        self.initialize_project_data()

        self.wire_up_gaussian_random_fields()
        self.initialize_gaussian_random_field_clickability()

        self._set_checkboxes_to_defaults()

    def wire_up_selections(self):
        buttons = {
            ZoneSelectionElements.TOGGLE: self._toggle_separate_zone_models,
            FaciesSelectionElements.TOGGLE: self._toggle_select_facies,
        }
        self._connect_buttons_to_functions_on_event(buttons, 'stateChanged')

    def _connect_buttons_to_functions_on_event(self, buttons: Dict[str, Callable], event: str):
        for key, fun in buttons.items():
            button = get_element(self, key)
            button.__getattribute__(event).connect(fun)

    def wire_up_navigation(self):
        buttons = {
            MainWindowElements.ASSIGN_PROBABILITY_CUBE: self.assign_probabilities,
            MainWindowElements.CLOSE: self.close,
            MainWindowElements.EXPERIMENTAL_MODE: self._toggle_experimental_mode,
            MainWindowElements.CONDITION_TO_WELL: self._condition_to_wells,
            FaciesSelectionElements.ADD_FACIES: self.add_facies,
        }
        self._connect_buttons_to_functions_on_event(buttons, 'clicked')

    def initialize_gaussian_random_field_clickability(self):
        # TODO: Read how many facies are available, and make sure that no more than that can be clicked.
        # TODO: Do this for the different zones
        pass

    def wire_up_gaussian_random_fields(self):
        settings_prefix = GaussianRandomFieldElements.SETTINGS
        for i in range(GaussianRandomFieldElements.NUMBER_OF_ELEMENTS):
            name = 'GRF' + str(i + 1)  # GRFs are 1 indexed
            button = get_element(self, settings_prefix + name)
            button.clicked.connect(self.define_gaussian_field)

    def define_gaussian_field(self):
        # TODO: Pass information on which button this came from
        sender = self.sender()
        self.gaussian_settings = DefineGaussian(self._state)
        self.gaussian_settings.show()
        pass

    def initialize_project_data(self):
        # TODO: Read from the project data
        if self._state:
            for key in self._state.keys():
                if key == ModeConstants.EXECUTION_MODE and self._state.is_experimental_mode():
                    check_box = get_element(self, MainWindowElements.EXPERIMENTAL_MODE)
                    check_box.setChecked(True)
                pass

    def add_facies(self):
        self.new_facies_dialog = AddFacies(self._state)
        self.new_facies_dialog.show()

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
        library = truncation_library_elements(self)
        for key in library.keys():
            if isinstance(library[key], list):
                for button_information in library[key]:
                    self._connect_truncation_button(button_information)
            else:
                self._connect_truncation_button(library[key])

    def _connect_truncation_button(
            self,
            button_information: Dict[TruncationLibrarySubKeys, Union[QWidget, int]]
    ) -> None:
        button = button_information[TruncationLibrarySubKeys.BUTTON_NAME_KEY]  # type: QPushButton
        button.clicked.connect(self._generate_truncation_dialog)

    def _generate_truncation_dialog(self):
        sender = self.sender()
        library = truncation_library_button_to_kind_and_number_of_facies(self)
        button_information = library[sender]
        truncation_rule = button_information[TruncationLibraryKeys.KEY]
        number_of_facies = button_information[TruncationLibrarySubKeys.NUMBER_OF_FACIES_KEY]
        parent = None
        if truncation_rule == TruncationLibraryKeys.CUBIC:
            dialog = CubicTruncationRule(parent=parent, state=self._state, active=number_of_facies)
        elif truncation_rule == TruncationLibraryKeys.NON_CUBIC:
            dialog = NonCubicTruncationRule(parent=parent, state=self._state, active=number_of_facies)
        elif truncation_rule == TruncationLibraryKeys.BAYFILL:
            dialog = BayfillTruncationRule(parent=parent, state=self._state)
        elif truncation_rule == TruncationLibraryKeys.CUSTOM:
            # TODO
            dialog = CustomTruncationRule(parent=parent, state=self._state)
        else:
            raise ValueError
        dialog.show()

    def _toggle_separate_zone_models(self):
        self._toggle_elements_in_selection_area(ZoneSelectionElements)

    def _toggle_select_facies(self):
        self._toggle_elements_in_selection_area(FaciesSelectionElements)

    def _toggle_elements_in_selection_area(self, constants):
        check_box = get_element(self, constants.TOGGLE)
        toggled = check_box.isChecked()
        elements = get_elements(self, constants.values(local=True))
        elements.remove(check_box)
        toggle_elements(toggled, elements)

    def _set_checkboxes_to_defaults(self):
        buttons = {
            ZoneSelectionElements.TOGGLE: Defaults.SEPARATE_ZONE_MODELS,
            FaciesSelectionElements.TOGGLE: Defaults.FACIES_MODELS,
            MainWindowElements.CONDITION_TO_WELL: Defaults.CONDITION_TO_WELL,
        }
        for key, default in buttons.items():
            check_box = get_element(self, key)
            check_box.setCheckState(default)
        self._toggle_experimental_mode()
        self._toggle_separate_zone_models()
        self._toggle_select_facies()
        self._condition_to_wells()

    def _toggle_experimental_mode(self):
        experimental_check_box = get_element(self, MainWindowElements.EXPERIMENTAL_MODE)
        use_experimental_mode = experimental_check_box.isChecked()
        if not use_experimental_mode and not self._state.has_valid_path():
            # The state is invalid, and the user must choose a project file

            # The user will get a dialog, asking them to choose a model file
            MessageBox(text="Please give a model file.", parent=self).exec()
            path = get_project_file(parent=self)
            if is_valid_path(path):
                self._state.set_project_path(path)
            else:
                self._state.set_experimental_mode()
                experimental_check_box.setChecked(True)
        elif use_experimental_mode:
            # TODO:
            pass
        condition_to_wells = get_element(self, MainWindowElements.CONDITION_TO_WELL)
        toggle_elements(not use_experimental_mode, condition_to_wells)

    def _condition_to_wells(self):
        check_box = get_element(self, MainWindowElements.CONDITION_TO_WELL)
        toggled = check_box.isChecked()
        assign_probability_cube = get_element(self, MainWindowElements.ASSIGN_PROBABILITY_CUBE)
        toggle_elements(toggled, assign_probability_cube)
        # TODO: Implement
        pass
