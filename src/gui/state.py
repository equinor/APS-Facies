from typing import List, Union

from PyQt5.QtWidgets import QListWidgetItem

from src.APSModel import APSModel
from src.gui.wrappers.base_classes.truncation import BaseTruncation
from src.utils.checks import has_valid_extension, is_valid_path
from src.utils.constants.non_qt import (
    CubicTruncationRuleConstants, CubicTruncationRuleElements, FaciesSelectionConstants, GaussianRandomFieldConstants,
    ModeConstants, ProjectConstants, TruncationRuleConstants,
)
from src.utils.constants.defaults.non_qt import DatabaseDefaults
from src.utils.constants.simple import Debug, OperationalMode, VariogramType
# TODO: Rewrite, and split up into several files / folders?
# TODO: Use SQLite
from src.utils.methods import get_printable_legal_values_of_enum


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

    def get_workflow_name(self) -> str:
        return self._get_simple_value(key=ProjectConstants.WORKFLOW_NAME)

    def get_grid_model_name(self):
        return self._get_simple_value(ProjectConstants.GRID_MODEL_NAME)

    def get_facies_parameter_name(self):
        return self._get_simple_value(ProjectConstants.FACIES_PARAMETER_NAME)

    def get_zone_parameter_name(self):
        return self._get_simple_value(ProjectConstants.ZONES_PARAMETER_NAME)

    def _get_simple_value(self, key) -> str:
        project_data = self.get_project_data()
        if key in self.__dict__:
            return project_data[key]
        else:
            return ''

    def is_valid_state(self):
        if not self._is_valid_mode():
            return False
        # TODO: More checks
        return True

    def set_experimental_mode(self) -> None:
        self.set_execution_mode(OperationalMode.EXPERIMENTAL)

    def set_reading_mode(self) -> None:
        self.set_execution_mode(OperationalMode.NORMAL)

    def set_execution_mode(self, mode: OperationalMode) -> None:
        if mode not in OperationalMode:
            raise ValueError(
                "The mode '{mode}' is not a valid mode for execution. Please use one of {options}".format(
                    mode=mode,
                    options=', '.join(get_printable_legal_values_of_enum(OperationalMode))
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
        self.__dict__[TruncationRuleConstants.SELECTED] = truncation.get_truncation_rule()

    def set_gaussian_field_settings(self, gaussian_settings):
        values = gaussian_settings.get_values()
        if GaussianRandomFieldConstants.SELECTED not in self.__dict__:
            raise ValueError("No Gaussian Random Field selected")
        current_gaussian_random_field = self.get_currently_selected_gaussian_field()
        self.__dict__[GaussianRandomFieldConstants.AVAILABLE][current_gaussian_random_field] = values

    def set_current_gaussian_random_field(self, name: str) -> None:
        key = GaussianRandomFieldConstants.CURRENT
        # Set currently selected
        if key not in self.__dict__:
            self.__dict__[key] = ''
        self.__dict__[key] = name
        # Add to set of sel
        self.update_toggled_gaussian_random_fields(name, True)

    def set_available_gaussian_random_fields(self, names: List[Union[str, None]]):
        key = GaussianRandomFieldConstants.AVAILABLE
        if key not in self.__dict__:
            self.__dict__[key] = {}
        for name in names:
            if name:
                self.__dict__[key][name] = {}

    def update_toggled_gaussian_random_fields(self, name: str, toggled: bool) -> None:
        key = GaussianRandomFieldConstants.SELECTED
        if key not in self.__dict__:
            self.__dict__[key] = set()
        if toggled:
            self.__dict__[key].add(name)
        elif name in self.__dict__[key]:
            self.__dict__[key].remove(name)
        else:
            # Nothing to do
            pass

    def get_currently_selected_gaussian_field(self) -> str:
        key = GaussianRandomFieldConstants.CURRENT
        if key in self.__dict__:
            return self.__dict__[key]
        else:
            return ''

    def get_aps_model(self):
        return APSModel(
            rmsWorkflowName=self.get_workflow_name(),
            rmsGridModelName=self.get_grid_model_name(),
            rmsFaciesParameterName=self.get_facies_parameter_name(),
            rmsZoneParameterName=self.get_zone_parameter_name(),

            previewZone=1,
        )

    def read_project_model(self):
        # TODO: Implement
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
        if mode != OperationalMode.NORMAL:
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
        return self.get_mode() == OperationalMode.NORMAL

    def is_experimental_mode(self):
        return self.get_mode() == OperationalMode.EXPERIMENTAL

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

    def select_facies(self, facies: Union[List[str], List[QListWidgetItem], str, QListWidgetItem]) -> None:
        if isinstance(facies, list):
            for f in facies:
                self.add_facies(f, key=FaciesSelectionConstants.SELECTED)
        else:
            self.add_facies(facies, key=FaciesSelectionConstants.SELECTED)

    def remove_select_facies(
            self,
            facies: Union[List[str], List[int], List[QListWidgetItem], str, int, QListWidgetItem]
    ) -> None:
        self.remove_facies(facies, key=FaciesSelectionConstants.SELECTED)

    def add_facies(
            self,
            facies_name: Union[str, QListWidgetItem],
            key: FaciesSelectionConstants = FaciesSelectionConstants.AVAILABLE,
            max_facies=DatabaseDefaults.MAXIMUM_NUMBER_OF_FACIES
    ) -> bool:
        """
        Adds the given name, og list object to the list of (available/selected) facies. The method also reads from the
        :param facies_name: The name of the facies to be added
        :type facies_name: Union[str, QListWidgetItem]
        :param key: The name of the list the name is added to. May be either available, or selected.
                    These are defined in FaciesSelectionConstants (AVAILABLE, and SELECTED)
        :type key: FaciesSelectionConstants
        :param max_facies: The maximum number of facies that are allowed to be added
        :type max_facies: int
        :return:
        :rtype: bool
        """
        assert key in [FaciesSelectionConstants.AVAILABLE, FaciesSelectionConstants.SELECTED]
        assert max_facies <= DatabaseDefaults.MAXIMUM_NUMBER_OF_FACIES
        if key not in self.__dict__:
            self.__dict__[key] = {}
        if isinstance(facies_name, QListWidgetItem):
            facies_name = facies_name.text()
        if facies_name not in self.__dict__[key]:
            # This check is as it is because the user may try to add an item that already exists, and that's OK
            if 0 <= max_facies <= len(self.__dict__[key]):
                # I.e. max_facies have been enabled (> 0), and the we will exceed the threshold if another item is added
                return False
            else:
                self.__dict__[key][facies_name] = {}
        return True

    def remove_facies(
            self,
            facies: Union[List[int], List[str], List[QListWidgetItem], int, str, QListWidgetItem],
            key: FaciesSelectionConstants = FaciesSelectionConstants.AVAILABLE
    ) -> None:
        if isinstance(facies, list):
            for f in facies:
                self.remove_facies(f, key=key)
        elif isinstance(facies, int):
            self.remove_facies_by_index(facies, key=key)
        elif isinstance(facies, str):
            self.remove_facies_by_name(facies, key=key)
        elif isinstance(facies, QListWidgetItem):
            self.remove_facies_by_name(facies.text(), key=key)
        else:
            # TODO: Raise exception?
            pass

    def remove_facies_by_index(
            self,
            indices: Union[List[int], int],
            key: FaciesSelectionConstants = FaciesSelectionConstants.AVAILABLE
    ) -> None:
        # TODO: very duplicated (comp. remove_facies_by_name)
        if isinstance(indices, list):
            for i in indices:
                self.remove_facies_by_index(i)
        elif isinstance(indices, int) and key in self.__dict__:
            self._remove_item(indices, key)
        else:
            # TODO: Give warning / raise exception?
            pass

    def _remove_item(self, item: str, key):
        def remove(collection: dict, item: str):
            if item in collection:
                collection.pop(item, None)
            else:
                # TODO: raise an exception?
                pass

        available_key = FaciesSelectionConstants.AVAILABLE
        selected_key = FaciesSelectionConstants.SELECTED

        if key == FaciesSelectionConstants.AVAILABLE:
            remove_from_available = True
        else:
            remove_from_available = False

        if remove_from_available and available_key in self.__dict__:
            remove(self.__dict__[available_key], item)
        if selected_key in self.__dict__:
            remove(self.__dict__[selected_key], item)

    def remove_facies_by_name(
            self,
            facies_names: Union[List[str], str],
            key: FaciesSelectionConstants = FaciesSelectionConstants.AVAILABLE
    ) -> None:
        # TODO: very duplicated (comp. remove_facies_by_index)
        if key in self.__dict__:
            if isinstance(facies_names, list):
                for facies_name in facies_names:
                    self.remove_facies_by_name(facies_name)
            elif isinstance(facies_names, str) and facies_names in self.__dict__[key]:
                self._remove_item(facies_names, key)

    def get_available_facies(self) -> List[str]:
        return self._get_list_items(FaciesSelectionConstants.AVAILABLE)

    def _get_list_items(self, key: str) -> List[str]:
        if key in self.__dict__:
            return self.__dict__[key]
        else:
            return []

    def get_selected_facies(self) -> List[str]:
        return self._get_list_items(FaciesSelectionConstants.SELECTED)

    @staticmethod
    def get_variogram_models() -> List[VariogramType]:
        return [model for model in VariogramType]

    @staticmethod
    def get_variogram_model_names() -> List[str]:
        models = State.get_variogram_models()
        names = [model.name for model in models]
        return [name.replace('_', ' ').capitalize() for name in names]

    @staticmethod
    def convert_variogram_name_to_enum(variogram_name: str) -> Union[VariogramType, None]:
        variogram_name = variogram_name.replace(' ', '_').upper()
        for variogram in VariogramType:
            if variogram.name == variogram_name:
                return variogram
        return None
