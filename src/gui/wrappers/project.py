# -*- coding: utf-8 -*-
"""
A wrapper, and implementation of the the first window the user will normally see; Selecting a project, or to toggle
the experimental mode.
'Implements' the design in Project.ui, and wraps around src/resources/ui/Project_ui.py.
"""
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from src.gui.wrappers.message_box import MessageBox
from src.resources.ui.Project_ui import Ui_project_selection
from src.gui.wrappers.main_window import MainWindow
from src.gui.state import State

from src.utils.constants import ProjectConstants, ModeConstants, ModeOptions, Defaults, MessageIcon


class Project(QMainWindow, Ui_project_selection):
    def __init__(self):
        super(QMainWindow, self).__init__()
        self.setupUi(self)
        self.retranslateUi(self)

        self._state = State()
        self.default_mode = Defaults.OPERATION_MODE
        self.wire_up()

        self.main_window = None

    def wire_up(self) -> None:
        ok = QDialogButtonBox.Ok
        cancel = QDialogButtonBox.Cancel

        self.m_buttons_ok_cancel_project.button(ok).clicked.connect(self.open_gui)
        self.m_buttons_ok_cancel_project.button(cancel).clicked.connect(self.close)
        self.m_button_browse_project_file.clicked.connect(self.browse_files)
        self.m_rb_experimental_mode.clicked.connect(self.toggle_experimental_mode)
        self.m_rb_read_rms_project_file.clicked.connect(self.toggle_reading_mode)
        self.m_edit_browse_project.textChanged.connect(self.set_project_file_to_be_read)

        self.toggle_mode(mode=self.default_mode)

    def open_gui(self):
        data = self.read_parameters()
        self._state.update(**data)  # TODO: Use a better method
        if self._state.is_valid_state():
            # The state is consistent, and the main window can be opened
            self.main_window = MainWindow(state=self._state)
            self.main_window.show()
            self.close()
        else:
            error_message = self._state.get_error_message()
            dialog = MessageBox(error_message, icon=MessageIcon.WARNING_ICON, parent=self)
            dialog.show()

    def read_parameters(self) -> dict:
        mapping = {
            ProjectConstants.FACIES_PARAMETER_NAME: self.m_edit_facies_parameter_name,
            ProjectConstants.GAUSSIAN_PARAMETER_NAME: self.m_edit_gaussian_parameter_name,
            ProjectConstants.GRID_MODEL_NAME: self.m_edit_grid_model_name,
            ProjectConstants.WORKFLOW_NAME: self.m_edit_workflow_name,
            ProjectConstants.ZONES_PARAMETER_NAME: self.m_edit_zones_parameter_name,
        }
        data = {}
        for key in mapping.keys():
            m_edit = mapping[key]  # type: QLineEdit
            text = m_edit.text()
            if text:
                data[key] = text
        return data

    def set_project_file_to_be_read(self) -> None:
        path = self.m_edit_browse_project.text()
        self._state.set_project_path(path)

    def browse_files(self) -> None:
        openfile = QFileDialog.getOpenFileName(self)
        path = openfile[0]
        self.m_edit_browse_project.setText(path)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Return:
            self.m_buttons_ok_cancel_project.button(QDialogButtonBox.Ok).click()
        elif event.key() == Qt.Key_Escape:
            self.m_buttons_ok_cancel_project.button(QDialogButtonBox.Cancel).click()

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

    def show_file_reading(self, enable: bool=True) -> None:
        self.m_button_browse_project_file.setEnabled(enable)
        self.m_edit_browse_project.setEnabled(enable)
        self.label_location_rms_project_file.setEnabled(enable)

    def toggle_experimental_mode(self) -> None:
        self.toggle_mode(mode=ModeOptions.EXPERIMENTAL_MODE)

    def toggle_reading_mode(self) -> None:
        self.toggle_mode(mode=ModeOptions.READING_MODE)
