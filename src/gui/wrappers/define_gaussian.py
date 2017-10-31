from typing import List, Union

from PyQt5.QtWidgets import QComboBox, QLineEdit, QCheckBox

from src.gui.state import State
from src.gui.wrappers.base_classes.dialogs import OkCancelDialog
from src.gui.wrappers.base_classes.getters.general import get_element, get_elements
from src.resources.ui.Gaussian_ui import Ui_DefineGaussian
from src.utils.constants.constants import DefineGaussianElements, TrendSettingsLabelsElements, Defaults
from src.utils.methods import toggle_elements


class DefineGaussian(OkCancelDialog, Ui_DefineGaussian):
    def __init__(self, state: State, parent=None):
        super(OkCancelDialog, self).__init__(parent=parent)
        self.state = state

        self.setupUi(self)
        self.retranslateUi(self)

        self.wire_up()

    def wire_up(self):
        super(DefineGaussian, self).wire_up(ok=self.save)
        self.wire_up_apply_trend()

        self._initialize_state()

    def wire_up_apply_trend(self):
        apply_trend = self._get_apply_trend_checkbox()
        assert isinstance(apply_trend, QCheckBox)
        apply_trend.stateChanged.connect(self._toggle_trend)

    def save(self):
        raise NotImplemented

    def _initialize_state(self):
        apply_trend = self._get_apply_trend_checkbox()
        apply_trend.setCheckState(Defaults.GAUSSIAN_TREND)
        self._toggle_trend()

    def _toggle_trend(self):
        sender = self.sender()
        if sender is None:
            sender = self._get_apply_trend_checkbox()
        toggled = sender.isChecked()
        trend_settings_elements = self._get_trend_settings_elements()
        toggle_elements(toggled, trend_settings_elements)

    def _get_apply_trend_checkbox(self):
        return get_element(self, DefineGaussianElements.TOGGLE_TREND)

    def _get_trend_settings_elements(self) -> Union[List[QLineEdit], List[QComboBox]]:
        button_names = set(TrendSettingsLabelsElements.values()) - {TrendSettingsLabelsElements.TOGGLE_TREND}
        elements = get_elements(self, button_names)
        return elements
