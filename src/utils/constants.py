from typing import Dict, Iterator, List

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMessageBox


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
    def constants(cls) -> List[str]:
        """
        A method for getting the names of the constants defined in the class / category
        :return: A list of strings with the names of constants defined in the class
        :rtype: List[str]
        """
        return [name for name in dir(cls) if not cls._used_internally(name)]

    @classmethod
    def values(cls) -> List[object]:
        """
        Gets the values of the different constants
        :return: A list of the definitions of the different constants
        :rtype: List[object]
        """
        return [cls.__getattribute__(cls(), constant) for constant in cls.constants()]

    @classmethod
    def all(cls) -> Dict[str, object]:
        """
        Gets a dictionary of the constants where the key is the name of the constant, and the value of the constant
        :return: A key, value pair of constants, and their value
        :rtype: Dict[str, str]
        """
        return {constant: cls.__getattribute__(cls(), constant) for constant in cls.constants()}

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
    def __getitem__(cls, item: str) -> object:
        return cls.__getattribute__(cls(), item)

    @classmethod
    def _standard_return_attribute(cls) -> List[object]:
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
        elif name in ['constants', 'values', 'all', 'is_key', 'is_value', 'is_icon', 'get_value', 'get_constant']:
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
    FACIES_PARAMETER_NAME = 'm_edit_facies_parameter_name'
    GAUSSIAN_PARAMETER_NAME = 'm_edit_gaussian_parameter_name'
    GRID_MODEL_NAME = 'm_edit_grid_model_name'
    WORKFLOW_NAME = 'm_edit_workflow_name'
    ZONES_PARAMETER_NAME = 'm_edit_zones_parameter_name'


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


class TruncationRuleConstants(Key):
    TRUNCATION_RULES = 'truncation rules'
    pass


class CubicTruncationRuleConstants(TruncationRuleConstants):
    PROPORTION_INPUT = 'text_field'
    PROPORTION_SCALE = 'slider'
    COLOR = 'color'
    FACIES = 'chosen facies'


class NonCubicTruncationRuleConstants(CubicTruncationRuleConstants):
    ANGLES = 'angles'


class FaciesLabels(Key):
    F1 = 'F1'
    F2 = 'F2'
    F3 = 'F3'
    F4 = 'F4'
    F5 = 'F5'


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
    OPERATION_MODE = ModeOptions.READING_MODE
    SEPARATE_ZONE_MODELS = Qt.Unchecked
    FACIES_MODELS = Qt.Unchecked
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
