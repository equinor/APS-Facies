from typing import Dict, Iterator, List, Union

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMessageBox

ValueTypes = Union[str, int, float, QColor, QMessageBox.Icon]


# TODO: Implement automatic initialization, when accessing a constant
# Ex. ProjectConstants.PATH_OF_PROJECT_FIL (with, or without () at the end) will give a class instance having that value


class Constants(object):
    def __init__(self, constant=None):
        self.constant = None
        if constant in self.constants() or constant is None:
            self.constant = constant
        else:
            raise ValueError(
                "The given constant, {constant} is not valid for {class_name}"
                "".format(constant=constant, class_name=self.__class__.__name__)
            )

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            pass

    def get_value(self):
        pass

    def get_constant(self):
        pass

    def __eq__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return self.get_value() == other.get_value() and self.get_constant() == other.get_constant()
        return False

    @classmethod
    def constants(cls, local: bool = False, sort: bool = False) -> List[str]:
        """
         A method for getting the names of the constants defined in the class / category.
        :param local: A flag for getting the constants that are ONLY defined in the particular class, and NOT in in any
                      of its parents. Default is to give ALL constants.
        :type local: bool
        :param sort: A flag for having the constants sorted alphabetically.
        :type sort: bool
        :return: A (sorted) list of strings with the names of constants (only) defined in the class.
        :rtype: List[str]
        """
        all_constants = [name for name in dir(cls) if not cls._used_internally(name)]
        if local:
            if hasattr(cls.__base__, 'constants'):
                irrelevant_constants = set(cls.__base__.constants())
                all_constants = [constant for constant in all_constants if constant not in irrelevant_constants]
        if sort:
            all_constants.sort()
        return all_constants

    @classmethod
    def values(cls, local: bool = False, sort: bool = False) -> List[ValueTypes]:
        """
        Gets the values of the different constants.
        :param local: A flag for getting the constants that are ONLY defined in the particular class, and NOT in in any
                      of its parents. Default is to give ALL constants.
        :type local: bool
        :param sort: A flag for having the constants sorted alphabetically.
        :type sort: bool
        :return: A list of the definitions of the different constants
        :rtype: List[ValueType]
        """
        return [cls.__getattribute__(cls(), constant) for constant in cls.constants(local=local, sort=sort)]

    @classmethod
    def all(cls, local: bool = False) -> Dict[str, ValueTypes]:
        """
        Gets a dictionary of the constants where the key is the name of the constant, and the value of the constant
        :param local: A flag for getting the constants that are ONLY defined in the particular class, and NOT in in any
                      of its parents. Default is to give ALL constants.
        :type local: bool
        :return: A key, value pair of constants, and their value
        :rtype: Dict[str, ValueTypes]
        """
        return {constant: cls.__getattribute__(cls(), constant) for constant in cls.constants(local=local)}

    @classmethod
    def __contains__(cls, item) -> bool:
        return item in cls._standard_return_attribute()

    @classmethod
    def __iter__(cls) -> Iterator:
        return cls.all().__iter__()

    @classmethod
    def __len__(cls) -> int:
        return len(cls.constants())

    @classmethod
    def __getitem__(cls, item: str) -> ValueTypes:
        return cls.__getattribute__(cls(), item)

    @classmethod
    def _standard_return_attribute(cls) -> List[ValueTypes]:
        return cls.values()

    @staticmethod
    def is_key() -> bool:
        return False

    @staticmethod
    def is_value() -> bool:
        return False

    @staticmethod
    def is_icon() -> bool:
        return False

    @staticmethod
    def _used_internally(name: str) -> bool:
        # FIXME: Return true iff name is all uppercase?
        if name[0:2] == name[-2:] == '__':
            # These are 'magic' methods in Python, and thus used internally
            return True
        elif name[0] == '_':
            # Private methods
            return True
        elif name.islower():
            # These are methods in the base class, that are also used internally, and are therefore not constants
            return True
        else:
            return False

    @classmethod
    def __repr__(cls):
        return ''.join([cls.__name__, ': ', ', '.join(cls.constants())])


class Key(Constants):
    @staticmethod
    def is_key():
        return True


class Value(Constants):
    @staticmethod
    def is_value():
        return False


class Icon(Constants):
    @staticmethod
    def is_icon():
        return True


class DataBase(Value):
    NAME = 'state.db'


class DrawingLibrary(Value):
    LIBRARY_FOLDER = '/home/aps-gui/APS-GUI/libraries'  # Set automatically by make
    NAME = 'libdraw2D.so'
    LIBRARY_PATH = LIBRARY_FOLDER + '/' + NAME


class ModeConstants(Key):
    EXECUTION_MODE = 'execution mode'


class ModeOptions(Value):
    READING_MODE = 'reading'
    EXPERIMENTAL_MODE = 'experimental'


class ProjectConstants(Key):
    PATH_OF_PROJECT_FILE = 'path of project file'
    WORKFLOW_NAME = 'workflow name'
    FACIES_PARAMETER_NAME = 'facies parameter name'
    GAUSSIAN_PARAMETER_NAME = 'gaussian parameter name'
    GRID_MODEL_NAME = 'grid model name'
    ZONES_PARAMETER_NAME = 'zone parameter name'


class ProjectElements(Value):
    BROWSE_PROJECT_BUTTON = 'm_button_browse_project_file'
    BROWSE_PROJECT_INPUT = 'm_edit_browse_project'
    EXPERIMENTAL_BUTTON = 'm_rb_experimental_mode'
    FACIES_PARAMETER_NAME = 'm_edit_facies_parameter_name'
    GAUSSIAN_PARAMETER_NAME = 'm_edit_gaussian_parameter_name'
    GRID_MODEL_NAME = 'm_edit_grid_model_name'
    READ_PROJECT_FILE = 'm_rb_read_rms_project_file'
    WORKFLOW_NAME = 'm_edit_workflow_name'
    ZONES_PARAMETER_NAME = 'm_edit_zones_parameter_name'


class AddFaciesElements(Value):
    NEW_FACIES_NAME = 'm_edit_new_facies'


class MainWindowConstants(Key):
    pass


class MainWindowElements(Value):
    ASSIGN_PROBABILITY_CUBE = 'm_button_assign_probability'
    CLOSE = 'm_button_close'
    CONDITION_TO_WELL = 'm_toggle_condition_to_wells'
    EXPERIMENTAL_MODE = 'm_toggle_experimental_mode'
    RUN_PREVIEWER = 'm_button_previewer'
    SAVE = 'm_button_save'
    SAVE_AS = 'm_button_save_as'


class ZoneSelectionElements(MainWindowElements):
    # Button for making the elements interactive
    TOGGLE = 'm_toggle_separate_zone_models'
    # Lists for available and selected
    AVAILABLE = 'm_list_available_zones'
    SELECTED = 'm_list_selected_zones'
    # Buttons for moving items from 'selectable' to being 'selected'
    SELECT = 'm_button_add_zone'
    UNSELECT = 'm_button_remove_zone'

    # Labels
    LABEL_TITLE = 'label_zones_to_be_modeled'
    LABEL_AVAILABLE = 'label_available_zones'
    LABEL_SELECTED = 'label_selected_zones'


class RegionSelectionElements(MainWindowElements):
    pass


class FaciesSelectionElements(MainWindowElements):
    # Button for making the elements interactive
    TOGGLE = 'm_toggle_select_facies'
    # Lists for available and selected
    AVAILABLE = 'm_list_available_facies'
    SELECTED = 'm_list_selected_facies'
    # Buttons for moving items from 'selectable' to being 'selected'
    SELECT = 'm_button_add_facies'
    UNSELECT = 'm_button_remove_facies'
    # Buttons for adding, and removing additional facies
    ADD_FACIES = 'm_button_add_new_facies'
    REMOVE_FACIES = 'm_button_remove_selected'

    # Labels
    LABEL_TITLE = 'label_facies_to_be_modelled'
    LABEL_AVAILABLE = 'label_available_facies'
    LABEL_SELECTED = 'label_selected_facies'


class TruncationRuleLibraryElements(MainWindowElements):
    CUBIC_BUTTON = 'm_button_type_'
    NON_CUBIC_BUTTON = 'm_button_type_'
    BAYFILL_BUTTON = 'm_button_bayfill'
    CUSTOM_BUTTON = 'm_button_type_customized'


class GaussianRandomFieldElements(MainWindowElements):
    NUMBER_OF_ELEMENTS = 6
    PLOT_AREA = 'm_plot_area_'
    SETTINGS = 'm_button_settings_'
    APPLY = 'm_toggle_'


class DefineGaussianElements(Value):
    TOGGLE_TREND = 'm_toggle_apply_trend'


class VariogramModelElements(DefineGaussianElements):
    VARIOGRAM = 'm_choose_variogram_model'
    AZIMUTH = 'm_edit_azimuth'
    DIP = 'm_edit_dip'
    PARALLEL = 'm_edit_parallel_to_azimuth'
    NORMAL = 'm_edit_normal_to_azimuth'
    VERTICAL = 'm_edit_vertical_normal_to_dip'
    PLOT = 'm_plot_variogram'


class TrendSettingsElements(DefineGaussianElements):
    TREND = 'm_choose_select_trend'
    DEPOSITIONAL_DIRECTION = 'm_edit_depositional_direction'
    STACKING_PATTERN = 'm_choose_stacking_pattern'
    STACKING_ANGLE = 'm_edit_stacking_angle'
    RELATIVE_STANDARD_DEVIATION = 'm_edit_relative_standard_deviation'
    SIMULATION_BOX_THICKNESS = 'm_edit_simbox_thickness'
    PLOT = 'm_plot_trend'


class TrendSettingsLabelsElements(TrendSettingsElements):
    TITLE = 'label_trend_settings'
    SELECT_TREND = 'label_select_trend'
    DEPOSITIONAL_DIRECTION_LABEL = 'label_depositional_direction'
    STACKING_PATTERN_LABEL = 'label_stacking_pattern'
    STACKING_ANGLE_LABEL = 'label_stacking_angle'
    RELATIVE_STANDARD_DEVIATION_LABEL = 'label_relative_standard_deviation'
    SIMULATION_BOX_THICKNESS_LABEL = 'label_simbox_thickness'


class BaseNames(Value):
    ANGLES = 'basename_angles'
    COLOR_BUTTON = 'basename_color_button'
    DROP_DOWN = 'basename_drop_down'
    SLIDERS = 'basename_sliders'
    PROPORTIONS = 'basename_proportions'
    SLANT_FACTOR = 'basename_slanted_factor'


class TruncationLibrary(Key):
    pass


class TruncationLibraryKeys(TruncationLibrary):
    KEY = 'truncation rule type'
    # Keys for types of truncation rules
    CUBIC = 'cubic'
    NON_CUBIC = 'non-cubic'
    BAYFILL = 'bayfill'
    CUSTOM = 'custom'


class TruncationLibrarySubKeys(TruncationLibrary):
    # Keys used in the library mapping
    NUMBER_OF_FACIES_KEY = 'number of facies'
    BUTTON_NAME_KEY = 'button name, or prefix'


class TruncationLibraryButtonNameKeys(TruncationLibrary):
    # Keys used for handling the button name
    ACTUAL_NAME_OF_BUTTON = 'actual name of button'
    IS_PREFIX = 'is prefix'


class TruncationRuleElements(Value):
    pass


class CubicTruncationRuleElements(TruncationRuleElements):
    PROPORTIONS = 'm_edit_proportion_'
    SLIDERS = 'm_slider_'
    COLOR_BUTTON = 'm_color_button_'
    DROP_DOWN = 'm_choose_'
    TOGGLE_OVERLAY = 'm_toggle_apply_overlay_facies'
    CLICK_OVERLAY = 'm_button_apply_overlay_facies'


class NonCubicTruncationRuleElements(CubicTruncationRuleElements):
    ANGLES = 'm_edit_angle_'


class BayfillTruncationRuleElements(CubicTruncationRuleElements):
    SLANT_FACTOR = 'm_edit_factor_'


class TruncationRuleConstants(Key):
    TRUNCATION_RULES = 'truncation rules'


class CubicTruncationRuleConstants(TruncationRuleConstants):
    PROPORTION_INPUT = 'text_field'
    PROPORTION_SCALE = 'slider'
    COLOR = 'color'
    FACIES = 'chosen facies'


class NonCubicTruncationRuleConstants(CubicTruncationRuleConstants):
    ANGLES = 'angles'


class BayfillTruncationRuleConstants(CubicTruncationRuleConstants):
    SLANTED_FACTOR = 'slanted factor'


class FaciesLabels(Key):
    F1 = 'F1'
    F2 = 'F2'
    F3 = 'F3'
    F4 = 'F4'
    F5 = 'F5'


class FaciesBayfill(FaciesLabels):
    F1 = 'floodplain'
    F2 = 'subbay'
    F3 = 'WBF'
    F4 = 'BHD'
    F5 = 'lagoon'


class FaciesNameBayfill(Key):
    FLOODPLAIN = FaciesBayfill.F1
    SUBBAY = FaciesBayfill.F2
    WBF = FaciesBayfill.F3
    BHD = FaciesBayfill.F4
    LAGOON = FaciesBayfill.F5


class SlantFactorsBayfill(Key):
    SF = FaciesNameBayfill.FLOODPLAIN
    YSF = FaciesNameBayfill.SUBBAY
    SBHD = FaciesNameBayfill.BHD


class HideOptions(Value):
    DISABLE = 'disable'
    HIDE = 'hide'


class Debug(Value):
    OFF = 0
    ON = 1
    SOMEWHAT_VERBOSE = 1
    VERBOSE = 2
    VERY_VERBOSE = 3
    VERY_VERY_VERBOSE = 4


class Variogram(Value):
    SPHERICAL = 1
    EXPONENTIAL = 2
    GAUSSIAN = 3
    GENERAL_EXPONENTIAL = 4


class Defaults(Value):
    FILE_EXTENSION = 'xml'
    FILE_FILTER = 'XML files (*.xml)'
    NAME_OF_BUTTON_BOX = 'm_buttons_ok_cancel'
    NAME_OF_PROPORTIONS = CubicTruncationRuleElements.PROPORTIONS
    NAME_OF_SLIDERS = CubicTruncationRuleElements.SLIDERS
    NAME_OF_COLOR_BUTTON = CubicTruncationRuleElements.COLOR_BUTTON
    NAME_OF_DROP_DOWN = CubicTruncationRuleElements.DROP_DOWN
    NAME_OF_ANGLES = NonCubicTruncationRuleElements.ANGLES
    NAME_OF_SLANTED_FACTOR = BayfillTruncationRuleElements.SLANT_FACTOR
    OPERATION_MODE = ModeOptions.READING_MODE
    SEPARATE_ZONE_MODELS = Qt.Unchecked
    FACIES_MODELS = Qt.Unchecked
    GAUSSIAN_TREND = Qt.Unchecked
    CONDITION_TO_WELL = Qt.Unchecked
    HIDE = HideOptions.DISABLE
    DEBUG = Debug.OFF


class MessageIcon(Icon):
    NO_ICON = QMessageBox.NoIcon
    QUESTION_ICON = QMessageBox.Question
    INFORMATION_ICON = QMessageBox.Information
    WARNING_ICON = QMessageBox.Warning
    CRITICAL_ICON = QMessageBox.Critical


class Proportions(Value):
    BOTTOM = 0
    TOP = 1
    DECIMALS = 5
    MAXIMUM = TOP
    MINIMUM = BOTTOM


class Angles(Value):
    MINIMUM = -180.0
    MAXIMUM = +180.0
    DECIMALS = 2


class Ranges(Value):
    # Slider
    SLIDER_MAXIMUM = 99
    SLIDER_MINIMUM = 0
    # Proportion
    PROPORTION_MINIMUM = 0.0
    PROPORTION_MAXIMUM = 1.0


class Colors(Value):
    LAWN_GREEN = QColor('lawngreen')  # Hex code: #7CFC00
    GRAY = QColor('gray')  # Hex code: #808080
    DODGER_BLUE = QColor('dodgerblue')  # Hex code: #1E90FF
    GOLD = QColor('gold')  # Hex code: #D4AF37
    DARK_ORCHID = QColor('darkorchid')  # Hex code: #9932CC
    CYAN = QColor('cyan')  # Hex code: #00B7EB
    FIREBRICK = QColor('firebrick')  # Hex code: #B22222
    OLIVE_DRAB = QColor('olivedrab')  # Hex code: #6B8E23
    BLUE = QColor('blue')  # Hex code: #0000FF
    CRIMSON = QColor('crimson')  # Hex code: #DC143C
    DARK_ORANGE = QColor('darkorange')  # Hex code: #FF8C00
    RED = QColor('red')  # Hex code: #FF0000
    BACKGROUND = QColor('#EFEBE7')
