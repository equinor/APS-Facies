from functools import lru_cache
from typing import Dict, List, Union

from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QCheckBox, QComboBox, QLineEdit, QPushButton, QSlider, QWidget

from src.gui.wrappers.base_classes.chekkers.values import should_change
from src.gui.wrappers.base_classes.dialogs import OkCancelDialog
from src.gui.wrappers.base_classes.getters.color import get_color
from src.gui.wrappers.base_classes.getters.general import get_element, get_elements_from_base_name, get_value_of_element
from src.gui.wrappers.base_classes.getters.numeric_input_field import get_number_from_numeric_text_field
from src.gui.wrappers.base_classes.pickers.color_picker import ColorPicker
from src.gui.wrappers.base_classes.setters.color import set_color
from src.gui.wrappers.base_classes.setters.qt_element_widgets import set_value
from src.utils.constants.non_qt import (
    Angles, BaseNames, CubicTruncationRuleConstants, CubicTruncationRuleElements, FaciesLabels, Proportions,
    TruncationRuleConstants, TruncationRuleLibraryElements,
)
from src.utils.constants.defaults.non_qt import UI
from src.utils.gui.getters import get_attributes, get_elements_with_prefix
from src.utils.gui.update import apply_validator, toggle_elements, update_numeric
from src.utils.mappings import truncation_rule_element_key_to_state_key
from src.utils.numeric import normalize_number


class BaseTruncation(OkCancelDialog):
    def __init__(
            self,
            state,
            truncation_type: str,
            parent=None,
            name_of_buttons=UI.NAME_OF_BUTTON_BOX,
            basename_sliders=UI.NAME_OF_SLIDERS,
            basename_proportions=UI.NAME_OF_PROPORTIONS,
            basename_color_button=UI.NAME_OF_COLOR_BUTTON,
            basename_drop_down=UI.NAME_OF_DROP_DOWN,
            facies_options=None,
            color_options=None,
            names=None,
            active=None
    ):
        """
        The base class of all truncation rule widgets (or, at the very least for Cubic, and Non-Cubic)
        :param parent:
        :type parent:
        :param state:
        :type state: State
        :param truncation_type: The truncation rule to be used (from the truncation library)
        :type truncation_type: str  TODO: Make more precise / list in Constants
        :param name_of_buttons: The name of the variable that holds an object of type QDialogButtonBox
        :type name_of_buttons: TruncationRuleLibraryElements
        :param basename_sliders: The prefix of every slider
        :type basename_sliders: TruncationRuleLibraryElements
        :param basename_proportions: The prefix of every text input box
        :type basename_proportions: TruncationRuleLibraryElements
        :param basename_color_button: The prefix for every button to choose a color
        :type basename_color_button: TruncationRuleLibraryElements
        :param basename_drop_down: The prefix for every drop-down menu
        :type basename_drop_down: TruncationRuleLibraryElements
        :param facies_options: A (named) list of lists that contains the valid options for the drop-down menues for the
                               different facies.
        :type facies_options: Union[List[List[str]], Dict[str, List[str]]]
        :param color_options: A list of the colors the buttons have by default. This may also be a 'named list' (a dict)
                              where the key is the name / label of the facies. If only a list, then the colors are
                              assigned in order (F1, ..., F5)
        :type color_options: Union[List[QColor], Dict[str, QColor]]
        :param names: A list of (default) names / labels for the different facies
        :type names: List[str]
        :param active: A list, or set of 'elements' that are active
        :type active: Union[List[str], Set[str], int]
        """
        super(BaseTruncation, self).__init__(parent=parent, name_of_buttons=name_of_buttons)
        self.state = state
        if names is None:
            self.names = ['F1', 'F2', 'F3', 'F4', 'F5']  # TODO: Make dynamic
        else:
            self.names = names

        # TODO: Validate
        self.color_options = color_options

        # TODO: Validate
        self.facies_options = facies_options

        # TODO: Validate
        self.truncation_type = truncation_type

        if isinstance(active, int):
            # Use only the 'active' / n first elements / labels
            active = self.names[:active]
        assert set(active) <= set(self.names)
        self.active = active
        self._set_base_names(BaseNames.SLIDERS, basename_sliders)
        self._set_base_names(BaseNames.PROPORTIONS, basename_proportions)
        self._set_base_names(BaseNames.COLOR_BUTTON, basename_color_button)
        self._set_base_names(BaseNames.DROP_DOWN, basename_drop_down)

    def wire_up(self):
        super(BaseTruncation, self).wire_up(ok=self.save, cancel=self.close)
        # TODO: Wire up connections to the display / preview
        self.wire_up_proportions_and_sliders()

        self.wire_up_color_buttons()

        self.wire_up_drop_downs()

        self.wire_up_angles()

        self.wire_up_slated_factor()

        self.wire_up_overlay_facies()

        self.deactivate_inactive_elements()

    def wire_up_slated_factor(self):
        validator = QDoubleValidator(top=Proportions.MAXIMUM, bottom=Proportions.MINIMUM, decimals=Proportions.DECIMALS)
        text_fields = self._get_slant_factors()
        apply_validator(text_fields, validator)
        for text_field in text_fields:
            text_field.textChanged.connect(self.update_slanted_factor)
            text_field.textChanged.connect(self.update_state)

    def wire_up_overlay_facies(self):
        toggle_overlay = CubicTruncationRuleElements.TOGGLE_OVERLAY
        click_overlay = CubicTruncationRuleElements.CLICK_OVERLAY
        if hasattr(self, toggle_overlay) and hasattr(self, click_overlay):
            toggle_apply_overlay_facies = get_element(self, toggle_overlay)
            button_apply_overlay_facies = get_element(self, click_overlay)
            toggle_apply_overlay_facies.clicked.connect(self.toggle_apply_overlay_facies)
            button_apply_overlay_facies.clicked.connect(self.apply_overlay_facies)

    def wire_up_angles(self):
        validator = QDoubleValidator(bottom=Angles.MINIMUM, top=Angles.MAXIMUM, decimals=Angles.DECIMALS)
        angle_inputs = self._get_angle_inputs()
        if len(angle_inputs) == len(self.names) and len(self.names) > 0:
            apply_validator(angle_inputs, validator)
            for angle_input in angle_inputs:
                angle_input.textChanged.connect(self.update_angle)
                angle_input.textChanged.connect(self.update_state)

    def wire_up_drop_downs(self):
        # TODO: Add different 'labels' / facies names to the different facies (F1, F2, ...)
        selected_facies = ['']
        selected_facies.extend(self.state.get_selected_facies().keys())
        for facies in self.active:
            drop_down = get_element(self, self.basename_drop_down + facies)  # type: QComboBox
            drop_down.addItems(selected_facies)

    def wire_up_color_buttons(self):
        # Wire up the color buttons
        color_buttons = self._get_color_buttons()
        # TODO: Set default colors
        for color_button in color_buttons:
            color_button.clicked.connect(self.select_color)
            color_button.clicked.connect(self.update_state)

    def _get_color_buttons(self) -> List[QPushButton]:
        return get_elements_from_base_name(self, BaseNames.COLOR_BUTTON, self.names)

    def _get_sliders(self) -> List[QSlider]:
        return get_elements_from_base_name(self, BaseNames.SLIDERS, self.names)

    def _get_proportion_inputs(self) -> List[QLineEdit]:
        return get_elements_from_base_name(self, BaseNames.PROPORTIONS, self.names)

    def _get_angle_inputs(self) -> List[QLineEdit]:
        return get_elements_from_base_name(self, BaseNames.ANGLES, self.names)

    def _get_slant_factors(self) -> List[QLineEdit]:
        return get_elements_from_base_name(self, BaseNames.SLANT_FACTOR, self.names)

    def wire_up_proportions_and_sliders(self):
        validator = QDoubleValidator(bottom=Proportions.MINIMUM, top=Proportions.MAXIMUM, decimals=Proportions.DECIMALS)
        proportion_inputs = self._get_proportion_inputs()
        sliders = self._get_sliders()
        if len(proportion_inputs) == len(sliders) == len(self.names) and len(self.names) > 0:
            # Set edits fields to be numbers only
            apply_validator(proportion_inputs, validator)
            # Connect sliders to text boxes
            for i in range(len(self.names)):
                slider = sliders[i]  # type: QSlider
                line_edit = proportion_inputs[i]  # type: QLineEdit
                self.connect_slider_and_text(slider, line_edit)
                line_edit.textChanged.connect(self.update_state)

            # Set default values
            self._initialize_proportion_values()

    def update_slanted_factor(self):
        update_numeric(self.sender(), minimum_truncation=Proportions.MINIMUM, maximum_truncation=Proportions.MAXIMUM)

    def update_state(self):
        # TODO
        pass

    def apply_overlay_facies(self):
        # TODO
        raise NotImplemented

    def toggle_apply_overlay_facies(self):
        sender = self.sender()  # type: QCheckBox
        toggle_overlay = CubicTruncationRuleElements.TOGGLE_OVERLAY
        button_overlay = CubicTruncationRuleElements.CLICK_OVERLAY
        if sender is None and hasattr(self, toggle_overlay):
            sender = self.__getattribute__(toggle_overlay)
        toggled = sender.isChecked()
        if hasattr(self, button_overlay):
            toggle_elements(toggled, self.__getattribute__(button_overlay))

    def save(self):
        # TODO: Implement
        self._ensure_proportions_are_between_0_1()
        self.ensure_normalization()
        self.state.set_truncation_rules(self)
        # TODO: Overprint facies
        self.close(unset_truncation_rule=False)

    def close(self, unset_truncation_rule=True):
        # TODO: Ugly hack, should only be set when saving
        if unset_truncation_rule:
            self.state.set_current_truncation_rule(None)
        super().close()

    def deactivate_inactive_elements(self):
        # TODO: Make more general?
        if self.active is None:
            to_be_deactivated = set(self.names)
        else:
            to_be_deactivated = set(self.names) - set(self.active)
        elements = get_attributes(
            self,
            [base_name + element for base_name in self.get_basename_of_elements() for element in to_be_deactivated]
        )
        # TODO?: Add toggle_overlay_facies (button)
        toggle_elements(toggled=False, elements=elements)
        self.toggle_apply_overlay_facies()

    def get_total_sum(self) -> float:
        content = [self._get_text_field_by_name(key) for key in self.active]
        return sum([get_number_from_numeric_text_field(cell) for cell in content])

    def get_value(self, element_type: TruncationRuleLibraryElements, element_label: FaciesLabels):
        assert element_type in self.get_basename_of_elements()
        assert element_label in self.active
        element = self._get_corresponding_element(element_label, element_type)
        if element is None:
            return None
        value = get_value_of_element(element)
        if isinstance(element, QLineEdit):
            value = float(value)
        return value

    def get_values(
            self,
            element_label: FaciesLabels,
            skip_elements: List[TruncationRuleLibraryElements] = None
    ) -> Dict[FaciesLabels, object]:  # TODO: Be more specific on the return values
        storage = {}
        key_mapping = truncation_rule_element_key_to_state_key()
        for element_type in self.get_basename_of_elements():
            if skip_elements and element_type in skip_elements:
                continue
            storage_key = key_mapping[element_type]
            storage[storage_key] = self.get_value(element_type, element_label)
        return storage

    def get_all_values(
            self,
            skip_labels: List[FaciesLabels] = None,
            skip_elements: List[TruncationRuleLibraryElements] = None):
        storage = {}
        for element_label in self.active:
            if skip_labels and element_label in skip_labels:
                continue
            storage[element_label] = self.get_values(element_label, skip_elements)
        return storage

    def get_truncation_rule(self):
        # TODO: Make proper, and return a proper class for Truncation rules
        return self.truncation_type

    def connect_slider_and_text(self, slider: QSlider, line_edit: QLineEdit) -> None:
        slider.valueChanged[int].connect(self.update_text)
        line_edit.textChanged.connect(self.update_slider)
        line_edit.textChanged.connect(self.ensure_normalization)

    def update_text(self):
        # TODO: Do not move the lower slider
        slider = self.sender()  # type: QSlider
        if self._slider_can_move():
            value = normalize_number(slider.value(), minimum_in=0, maximum_in=100, minimum_out=0, maximum_out=1)
            text_filed = self.get_corresponding_text_field(slider)
            if should_change(value, text_filed):
                text_filed.setText(str(value))

    def _update_slider(self, text_field: QLineEdit, skip_signals: bool = False) -> None:
        corresponding_slider = self.get_corresponding_slider(text_field)
        value = get_value_of_element(text_field)

        value = int(normalize_number(value, maximum_in=1, minimum_in=0, maximum_out=100, minimum_out=0))
        if should_change(value, corresponding_slider):
            set_value(corresponding_slider, value, normalize=False, skip_signals=skip_signals)

    def update_slider(self):
        sender = self.sender()
        assert isinstance(sender, QLineEdit)
        self._update_slider(sender)

    def update_sliders(self):
        for facies_label in self.active:
            slider = self._get_text_field_by_name(facies_label)
            self._update_slider(slider, skip_signals=True)

    def get_corresponding_text_field(self, sender: Union[QSlider, str]) -> QLineEdit:
        text_filed = self._get_corresponding_element(sender, self.basename_proportions)  # type: QLineEdit
        return text_filed

    def get_corresponding_slider(self, sender: QLineEdit) -> QSlider:
        slider = self._get_corresponding_element(sender, self.basename_sliders)
        return slider

    def _get_corresponding_element(
            self,
            sender: Union[QWidget, FaciesLabels],
            element_name: Union[TruncationRuleLibraryElements, TruncationRuleConstants],
    ) -> Union[QLineEdit, QSlider, None]:
        if isinstance(sender, str) or isinstance(sender, FaciesLabels):
            sender = self._get_element_lookup_table()[sender][element_name]
        facies_label = self._get_facies_label_lookup_table()[sender]
        if element_name in self.get_basename_of_elements():
            element = element_name
        elif element_name in self.get_mapping_for_element_names():
            element = self.get_mapping_for_element_names()[element_name]
        else:
            raise ValueError("The given element name, '{}' is invalid".format(element_name))
        if facies_label is None or element is None:
            return None
        return self._get_element_lookup_table()[facies_label][element]

    @lru_cache()
    def get_mapping_for_element_names(self) -> Dict[TruncationRuleConstants, TruncationRuleLibraryElements]:
        return {
            CubicTruncationRuleConstants.PROPORTION_SCALE: self.basename_sliders,
            CubicTruncationRuleConstants.PROPORTION_INPUT: self.basename_proportions,
            CubicTruncationRuleConstants.COLOR: self.basename_color_button,
            CubicTruncationRuleConstants.FACIES: self.basename_drop_down,
        }

    def ensure_normalization(self):
        sender = self.sender()
        if isinstance(sender, QSlider) or isinstance(sender, QLineEdit):
            to_be_changed = self.get_elements_from_base_name_to_be_changed(sender)
        elif isinstance(sender, QPushButton):
            to_be_changed = self.active
        else:
            raise TypeError
        sender.blockSignals(True)
        total_sum = self.get_total_sum()
        self._ensure_proportions_are_between_0_1()
        if sender is None and total_sum == 0:
            self._initialize_proportion_values()
        elif len(to_be_changed) == 0:
            # TODO: Deal with increasing/decreasing of the LAST facies
            pass
        elif total_sum == 1.0:
            # It sums to one, and there are nothing to be done, except ot 'clean up'
            pass
        else:
            # TODO: General normalization
            diff = (1 - total_sum) / len(to_be_changed)
            for facies_label in to_be_changed:
                # TODO: Deal with negative numbers
                text_field = self.get_corresponding_text_field(facies_label)
                self.add_difference_to_proportion_value(diff, text_field)
            pass

        # Clean up
        self.update_sliders()
        sender.blockSignals(False)

    def _slider_can_move(self) -> bool:
        # TODO: Implement properly
        sender = self.sender()
        assert isinstance(sender, QSlider)
        facies_label = self.get_facies_label_of_element(sender)
        if self.active[-1] == facies_label:
            # This is the last (active) slider, and should there fore not be allowed to move upward
            return False
        return True

    def _initialize_proportion_values(self):
        mean = 1 / len(self.active)
        for name in self.active:
            text_field = self._get_text_field_by_name(name)
            text_field.blockSignals(True)
            text_field.setText(str(mean))
            text_field.blockSignals(False)
        self.update_sliders()

    def _ensure_proportions_are_between_0_1(self):
        for name in self.active:
            text_field = self._get_text_field_by_name(name)  # type: QLineEdit
            value = get_number_from_numeric_text_field(text_field)
            if value < 0:
                text_field.setText('0')
            elif value > 1:
                text_field.setText('1')

    def add_difference_to_proportion_value(self, difference: float, name: Union[QLineEdit, FaciesLabels]) -> None:
        if isinstance(name, str):
            element = self._get_text_field_by_name(name)
        elif isinstance(name, QLineEdit):
            element = name
        else:
            raise TypeError(
                "The element to be updated must be a 'QLineEdit', or 'str', and not '{}'".format(type(name))
            )
        value = max(float(get_value_of_element(element)) + difference, 0)
        set_value(element, value, normalize=False, skip_signals=True)

    def get_elements_from_base_name_to_be_changed(self, sender: QWidget) -> List[str]:
        if sender is None:
            return self.active
        lookup_table = self._get_facies_label_lookup_table()
        index_beyond_which_sliders_may_change = self.names.index(lookup_table[sender])
        to_be_changed = [
            name for name in self.names[index_beyond_which_sliders_may_change + 1:]
            if name in self.active
        ]
        return to_be_changed

    @lru_cache()
    def get_facies_label_of_element(self, element: Union[QSlider, QLineEdit, QComboBox, QPushButton]) -> FaciesLabels:
        return self._get_facies_label_lookup_table()[element]

    @lru_cache()
    def get_basename_of_elements(self) -> List[TruncationRuleLibraryElements]:
        prefix = 'basename'
        element_variable_names = get_elements_with_prefix(self, prefix)
        return [self.__getattribute__(name) for name in element_variable_names]

    @lru_cache()
    def _get_element_lookup_table(
            self
    ) -> Dict[FaciesLabels, Dict[TruncationRuleLibraryElements, Union[QLineEdit, QSlider, QPushButton, QComboBox]]]:
        base_elements = self.get_basename_of_elements()
        return {
            facies_label: {
                base_name: self.__getattribute__(base_name + facies_label)
                if hasattr(self, base_name + facies_label) else None for base_name in base_elements
            } for facies_label in self.names
        }

    @lru_cache()
    def _get_facies_label_lookup_table(self) -> Dict[QWidget, FaciesLabels]:
        element_lookup_table = self._get_element_lookup_table()
        return {
            element: facies_label if element is not None else None
            for facies_label in element_lookup_table
            for element in element_lookup_table[facies_label].values()
        }

    def _get_element_by_name(
            self,
            facies_label: FaciesLabels,
            element_type: TruncationRuleLibraryElements
    ) -> Union[QSlider, QLineEdit, QComboBox, QPushButton]:
        return self._get_element_lookup_table()[facies_label][element_type]

    def _get_text_field_by_name(self, name: FaciesLabels) -> QLineEdit:
        return self._get_element_by_name(name, self.basename_proportions)

    def select_color(self):
        sender = self.sender()
        previous_color = get_color(sender)
        color = ColorPicker(parent=self, initial_color=previous_color).get_color()
        if color.value():
            set_color(sender, color)
        # TODO: Store the color in the state (or button)
        return color

    def update_angle(self):
        update_numeric(self.sender(), minimum_truncation=Angles.MINIMUM, maximum_truncation=Angles.MAXIMUM)

    def _set_base_names(self, basename_key: BaseNames, basename_value: TruncationRuleLibraryElements) -> None:
        self.__setattr__(basename_key, basename_value)
