from typing import List, Dict, Iterator

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox


class Constants(object):
    def __init__(self, constant=None):
        self._constant = None
        if constant in self.constants() or constant is None:
            self._constant = constant
        else:
            raise ValueError(
                "The given constant, {constant} is not valid for {class_name}"
                "".format(constant=constant, class_name=self.__class__.__name__)
            )

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


class Ranges(Value):
    # Slider
    SLIDER_MAXIMUM = 99
    SLIDER_MINIMUM = 0
    # Proportion
    PROPORTION_MINIMUM = 0.0
    PROPORTION_MAXIMUM = 1.0
