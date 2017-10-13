from PyQt5.Qt import QKeyEvent
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialogButtonBox

from src.gui.wrappers.base_classes.dialogs import GeneralDialog
from src.gui.wrappers.base_classes.getters.general import get_element
from src.resources.ui.AddFacies_ui import Ui_AddFacies
from src.utils.constants import Defaults, AddFaciesElements


class AddFacies(GeneralDialog, Ui_AddFacies):
    def __init__(self, state, parent=None, name_of_buttons=Defaults.NAME_OF_BUTTON_BOX):
        super(AddFacies, self).__init__(parent=parent, name_of_buttons=name_of_buttons)
        self.setupUi(self)
        self.retranslateUi(self)

        self.wire_up(save=self.save, cancel=self.close)
        self._state = state

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        if key == Qt.Key_Return:
            self.click_button(QDialogButtonBox.Save)
        elif key == Qt.Key_Escape:
            self.click_button(QDialogButtonBox.Cancel)

    def save(self):
        edit = get_element(self, AddFaciesElements.NEW_FACIES_NAME)
        facies_name = edit.text()
        self._state.add_facies(facies_name)
        self.close()
