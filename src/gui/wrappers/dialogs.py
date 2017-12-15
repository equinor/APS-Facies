from PyQt5.Qt import QKeyEvent
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialogButtonBox

from src.gui.wrappers.base_classes.dialogs import GeneralDialog
from src.gui.wrappers.base_classes.getters.general import get_element
from src.resources.ui.AddFacies_ui import Ui_AddFacies
from src.utils.constants.non_qt import AddFaciesElements
from src.utils.constants.defaults.non_qt import DatabaseDefaults, UI


class AddFacies(GeneralDialog, Ui_AddFacies):
    def __init__(self, state, sender, parent=None, name_of_buttons=UI.NAME_OF_BUTTON_BOX):
        super(AddFacies, self).__init__(parent=parent, name_of_buttons=name_of_buttons)
        self.setupUi(self)
        self.retranslateUi(self)

        self.wire_up(save=self.save, close=self.close)
        self._state = state
        self._sender = sender

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        if key in [Qt.Key_Return, Qt.Key_Enter]:
            self.click_button(QDialogButtonBox.Save)
        elif key == Qt.Key_Escape:
            self.click_button(QDialogButtonBox.Close)

    def save(self):
        edit = get_element(self, AddFaciesElements.NEW_FACIES_NAME)
        facies_name = edit.text()
        max_facies = DatabaseDefaults.MAXIMUM_NUMBER_OF_FACIES
        if facies_name:
            success = self._state.add_facies(facies_name, max_facies=max_facies)
            if success:
                self._sender.update_facies()
                edit.clear()
            else:
                ok = get_element(self, self.name_of_buttons)  # type: QDialogButtonBox
                ok.button(QDialogButtonBox.Save).setEnabled(False)
                ok.setToolTip("The maximum number of facies have been reached ({}).".format(max_facies))
        else:
            # For your convenience; nothing entered, so we assume we are done entering facies.
            self.close()
