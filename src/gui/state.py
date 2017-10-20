from src.APSModel import APSModel
from src.gui.wrappers.base_classes.truncation import BaseTruncation
from src.utils.checks import has_valid_extension, is_valid_path
from src.utils.constants import (
    CubicTruncationRuleConstants, CubicTruncationRuleElements, Debug, ModeConstants,
    ModeOptions, ProjectConstants, TruncationRuleConstants,
)


class State(dict):
    """
    A class that defines the state of the GUI application.
    """

    def __init__(self, **kwargs):
        super(State, self).__init__(**kwargs)

    def __setattr__(self, key, value):
        # TODO: Make pretty, and robust
        self.__dict__[key] = value

    def __getitem__(self, item):
        # TODO: Make pretty, and robust
        if item in self.__dict__:
            return self.__dict__[item]
        else:
            return None

    def __repr__(self):
        return repr(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __delitem__(self, key):
        #  TODO: Make pretty, and robust?
        del self.__dict__[key]

    def clear(self):
        # TODO: Should this be allowed?
        return self.__dict__.clear()

    def copy(self):
        return self.__dict__.copy()

    def __contains__(self, item):
        return item in self.__dict__

    def update(self, *args, **kwargs):
        # TODO: Should this be allowed?
        return self.__dict__.update(*args, **kwargs)

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()

    def pop(self, *args):
        # TODO: Should not be allowed
        return self.__dict__.pop(*args)

    def __iter__(self):
        return iter(self.__dict__)

    def get_project_data(self):
        return {key: self.__dict__[key] for key in ProjectConstants.values() if key in self.__dict__}

    def is_valid_state(self):
        if not self._is_valid_mode():
            return False
        # TODO: More checks
        return True

    def set_experimental_mode(self) -> None:
        self.set_execution_mode(ModeOptions.EXPERIMENTAL_MODE)

    def set_reading_mode(self) -> None:
        self.set_execution_mode(ModeOptions.READING_MODE)

    def set_execution_mode(self, mode: str) -> None:
        if mode not in ModeOptions():
            raise ValueError(
                "The mode '{mode}' is not a valid mode for execution. Please use one of {options}".format(
                    mode=mode,
                    options=', '.join(ModeOptions.values())
                )
            )
        self.__dict__[ModeConstants.EXECUTION_MODE] = mode

    def set_project_path(self, path: str) -> None:
        # TODO: Check if valid file
        if is_valid_path(path):
            self.__dict__[ProjectConstants.PATH_OF_PROJECT_FILE] = path
            self.set_reading_mode()
        else:
            # TODO: Error message?
            raise FileNotFoundError("The file {} was not found".format(path))

    def set_project_parameters(self, data: dict) -> None:
        # TODO: Use a better method
        self.update(**data)

    def set_truncation_rules(self, truncation: BaseTruncation):
        unnecessary_elements = [CubicTruncationRuleElements.SLIDERS]
        values = truncation.get_all_values(skip_elements=unnecessary_elements)
        self._ensure_normalization(values)
        self.__dict__[TruncationRuleConstants.TRUNCATION_RULES] = values

    def read_project_model(self):
        pass

    @staticmethod
    def _ensure_normalization(values):
        proportion_key = CubicTruncationRuleConstants.PROPORTION_INPUT
        total_sum = sum([values[label][proportion_key] for label in values.keys()])
        if total_sum != 1.0:
            for label in values.keys():
                value = values[label][proportion_key]
                values[label][proportion_key] = value / total_sum

    def _is_valid_mode(self):
        mode = self[ModeConstants.EXECUTION_MODE]
        if mode:
            # A mode is selected
            if self.is_reading_mode():
                return self._is_valid_reading_mode()
            elif self.is_experimental_mode():
                return self._is_valid_experimental_mode()

    def _is_valid_reading_mode(self):
        mode = self.get_mode()
        if mode != ModeOptions.READING_MODE:
            # The mode is invalid
            return False
        if not self.has_valid_path():
            # The is a file, and thus valid
            return False
        path_to_project_file = self.get_path()
        try:
            APSModel(path_to_project_file, debug_level=Debug.OFF)
            return True
        except:
            return False

    def _is_valid_experimental_mode(self):
        # TODO: Make better?
        # TODO: Is there any other requirements? Name, and such?
        return self.is_experimental_mode()

    def get_mode(self):
        mode = self[ModeConstants.EXECUTION_MODE]
        if mode:
            return mode
        else:
            return None

    def get_path(self) -> [str, None]:
        path = self[ProjectConstants.PATH_OF_PROJECT_FILE]
        if path:
            return path
        else:
            return None

    def is_reading_mode(self):
        return self.get_mode() == ModeOptions.READING_MODE

    def is_experimental_mode(self):
        return self.get_mode() == ModeOptions.EXPERIMENTAL_MODE

    def has_valid_path(self) -> bool:
        path = self.get_path()
        return is_valid_path(path)

    def _has_valid_extension(self) -> bool:
        path = self.get_path()
        return has_valid_extension(path)

    def get_error_message(self) -> str:
        error_message = ''
        if not self.is_valid_state():
            if self.is_reading_mode() and not self.has_valid_path():
                error_message = 'The mode is set to reading, but no valid path is given.'
            # TODO: Add more error messages
            else:
                error_message = 'There is an internal inconsistency error.'
        return error_message

    def add_facies(self, facies_name):
        # TODO: Implement!
        pass
