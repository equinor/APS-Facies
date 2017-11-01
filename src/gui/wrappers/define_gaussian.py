from functools import lru_cache
from typing import Dict, List, Union

from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QCheckBox, QComboBox, QLineEdit

from src.gui.state import State
from src.gui.wrappers.base_classes.dialogs import OkCancelDialog
from src.gui.wrappers.base_classes.getters.general import get_element, get_elements
from src.gui.wrappers.base_classes.getters.numeric_input_field import get_number_from_numeric_text_field
from src.resources.ui.Gaussian_ui import Ui_DefineGaussian
from src.utils.constants.constants import (
    AzimuthAngle, Constraints, Defaults, DefineGaussianElements, DipAngle,
    MainRange, PerpRange, Power, TrendSettingsLabelsElements, VariogramModelConstants, VariogramModelElements,
    VerticalRange,
)
from src.utils.constants.simple import VariogramType
from src.utils.methods import apply_validator, toggle_elements, update_numeric


class DefineGaussian(OkCancelDialog, Ui_DefineGaussian):
    def __init__(self, state: State, parent=None):
        super(OkCancelDialog, self).__init__(parent=parent)
        self.state = state

        self.setupUi(self)
        self.retranslateUi(self)

        self.wire_up()

    def wire_up(self):
        super(DefineGaussian, self).wire_up(ok=self.save)
        self.wire_up_validators()
        self.wire_up_variogram_model()

        self.wire_up_apply_trend()

        self._initialize_state()

    def wire_up_validators(self):
        input_fields = self.get_variogram_elements_and_constraints()
        for input_field, constraints in input_fields.items():
            validator = QDoubleValidator(
                top=constraints.MAXIMUM, bottom=constraints.MINIMUM, decimals=constraints.DECIMALS
            )
            apply_validator(input_field, validator)
            input_field.textChanged.connect(self._update_numeric_element)

    @lru_cache()
    def get_variogram_elements_and_constraints(self) -> Dict[QLineEdit, Constraints]:
        input_fields = self.get_variogram_element_names_and_constants()
        return {get_element(self, key): constraint for key, constraint in input_fields.items()}

    @lru_cache()
    def get_variogram_elements_to_keys(self):
        input_fields = self.get_variogram_element_names_and_keys()
        return {get_element(self, name): key for name, key in input_fields.items()}

    @staticmethod
    @lru_cache()
    def get_variogram_element_names_and_constants():
        return {
            VariogramModelElements.AZIMUTH:  AzimuthAngle,
            VariogramModelElements.DIP:      DipAngle,
            VariogramModelElements.PARALLEL: MainRange,
            VariogramModelElements.NORMAL:   PerpRange,
            VariogramModelElements.VERTICAL: VerticalRange,
            VariogramModelElements.POWER:    Power,
        }

    @staticmethod
    @lru_cache()
    def get_variogram_element_names_and_keys():
        input_fields = {
            VariogramModelElements.AZIMUTH:  VariogramModelConstants.AZIMUTH,
            VariogramModelElements.DIP:      VariogramModelConstants.DIP,
            VariogramModelElements.PARALLEL: VariogramModelConstants.PARALLEL,
            VariogramModelElements.NORMAL:   VariogramModelConstants.NORMAL,
            VariogramModelElements.VERTICAL: VariogramModelConstants.VERTICAL,
            VariogramModelElements.POWER:    VariogramModelConstants.POWER,
        }
        return input_fields

    def wire_up_variogram_model(self):
        choose_model = self.get_variogram_model_element()
        choose_model.currentIndexChanged.connect(self._update_variogram)

        self._initialize_variogram_model_selection(choose_model)

    def get_variogram_model(self):
        choose_model = self.get_variogram_model_element()
        model = choose_model.currentText()
        return self.state.convert_variogram_name_to_enum(model)

    def get_variogram_model_element(self) -> QComboBox:
        return get_element(self, VariogramModelElements.VARIOGRAM)

    def _initialize_variogram_model_selection(self, choose_model):
        model_names = self.state.get_variogram_model_names()
        choose_model.addItems(model_names)

    def wire_up_apply_trend(self):
        apply_trend = self._get_apply_trend_checkbox()
        assert isinstance(apply_trend, QCheckBox)
        apply_trend.stateChanged.connect(self._toggle_trend)

    def save(self):
        self.state.set_gaussian_field_settings(self)
        self.close()

    def get_values(self):
        values = {VariogramModelConstants.VARIOGRAM: self.get_variogram_model()}
        is_general_exponential = values[VariogramModelConstants.VARIOGRAM] == VariogramType.GENERAL_EXPONENTIAL
        elements = self.get_variogram_elements_to_keys()
        for element, key in elements.items():
            if key == VariogramModelConstants.POWER and not is_general_exponential:
                continue
            values[key] = get_number_from_numeric_text_field(element)
        return values

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

    def _update_variogram(self):
        sender = self.sender()  # type: QComboBox
        variogram_model = self.state.convert_variogram_name_to_enum(sender.currentText())
        self._update_display_settings(variogram_model)

    def _update_display_settings(self, variogram: VariogramType):
        power_elements = get_elements(self, [VariogramModelElements.POWER, VariogramModelElements.LABEL_POWER])
        if variogram == VariogramType.GENERAL_EXPONENTIAL:
            toggle = True
        else:
            toggle = False
        toggle_elements(toggle, power_elements)

    def _update_numeric_element(self):
        sender = self.sender()
        assert isinstance(sender, QLineEdit)
        constraints = self.get_constraints(sender)
        update_numeric(
            sender,
            minimum_truncation=constraints.MINIMUM,
            maximum_truncation=constraints.MAXIMUM,
            number_of_decimals=constraints.DECIMALS
        )

    def get_constraints(self, sender: QLineEdit) -> Constraints:
        constraint_library = self.get_variogram_elements_and_constraints()
        if sender in constraint_library:
            constraints = constraint_library[sender]
        else:
            constraints = Constraints
        return constraints
