# -*- coding: utf-8 -*-
"""
A wrapper, and implementation of the the first window the user will normally see; Selecting a project, or to toggle
the experimental mode.
'Implements' the design in Project.ui, and wraps around src/resources/ui/Project_ui.py.
"""
from PyQt5.QtWidgets import *

from src.gui.state import State
from src.gui.wrappers.base_classes.dialogs import OkCancelDialog
from src.gui.wrappers.base_classes.getters.general import get_element
from src.gui.wrappers.base_classes.message_box import MessageBox
from src.gui.wrappers.main_window import MainWindow
from src.resources.ui.Project_ui import Ui_ProjectSelection
from src.utils.constants.non_qt import ProjectElements, HideOptions
from src.utils.constants.qt import MessageIcon
from src.utils.constants.defaults.non_qt import GeneralDefaults
from src.utils.constants.simple import OperationalMode
from src.utils.mappings import project_parameter_state_key_to_element_key
from src.utils.gui.getters import get_project_file
from src.utils.gui.update import toggle_elements


class Project(QMainWindow, Ui_ProjectSelection, OkCancelDialog):
    def __init__(self, parent=None):
        super(QMainWindow, self).__init__(parent=parent)
        self.setupUi(self)
        self.retranslateUi(self)

        self._state = State()
        self.default_mode = GeneralDefaults.OPERATION_MODE
        self.wire_up()

        self.main_window = None

    def wire_up(self, **kwargs) -> None:
        # TODO: Handle special ok, cancel
        # TODO: Make accessing elements more robust
        super(Project, self).wire_up(ok=self.open_gui, cancel=self.close)
        self.m_button_browse_project_file.clicked.connect(self.browse_files)
        self.m_rb_experimental_mode.clicked.connect(self.toggle_experimental_mode)
        self.m_rb_read_rms_project_file.clicked.connect(self.toggle_reading_mode)
        self.m_edit_browse_project.textChanged.connect(self.set_project_file_to_be_read)

        self.toggle_mode(mode=self.default_mode)

    def open_gui(self):
        data = self.read_parameters()
        self._state.set_project_parameters(data)
        if self._state.is_valid_state():
            self._state.read_project_model()
            # The state is consistent, and the main window can be opened
            self.main_window = MainWindow(state=self._state)
            self.main_window.show()
            self.close()
        else:
            error_message = self._state.get_error_message()
            dialog = MessageBox(error_message, icon=MessageIcon.WARNING_ICON, parent=self)
            dialog.show()

    def read_parameters(self) -> dict:
        mapping = project_parameter_state_key_to_element_key()
        data = {}
        for key in mapping.keys():
            m_edit = get_element(self, mapping[key])  # type: QLineEdit
            text = m_edit.text()
            if text:
                data[key] = text
        return data

    def set_project_file_to_be_read(self) -> None:
        path = get_element(self, ProjectElements.BROWSE_PROJECT_INPUT).text()
        self._state.set_project_path(path)

    def browse_files(self) -> None:
        path = get_project_file(self)
        self.m_edit_browse_project.setText(path)

    def activate_mode(self) -> None:
        toggle_read_project = True
        toggle_experimental = True
        if self._state.is_reading_mode():
            toggle_experimental = False
        elif self._state.is_experimental_mode():
            toggle_read_project = False
        self.m_rb_read_rms_project_file.setChecked(toggle_read_project)
        self.m_rb_experimental_mode.setChecked(toggle_experimental)

    def toggle_mode(self, mode: str) -> None:
        self._state.set_execution_mode(mode)
        self.activate_mode()
        if self._state.is_experimental_mode():
            self.show_file_reading(False)
        elif self._state.is_reading_mode():
            self.show_file_reading(True)

    def show_file_reading(self, enable: bool = True) -> None:
        elements = [self.m_button_browse_project_file, self.m_edit_browse_project, self.label_location_rms_project_file]
        toggle_elements(enable, elements, HideOptions.DISABLE)

    def toggle_experimental_mode(self) -> None:
        self.toggle_mode(mode=OperationalMode.EXPERIMENTAL_MODE)

    def toggle_reading_mode(self) -> None:
        self.toggle_mode(mode=OperationalMode.READING_MODE)
