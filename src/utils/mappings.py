from functools import lru_cache
from typing import Dict, List, Set, Union

from PyQt5.QtWidgets import QWidget

from src.gui.wrappers.base_classes.getters.general import get_element
from src.utils.constants.constants import (
    BayfillTruncationRuleConstants, BayfillTruncationRuleElements,
    CubicTruncationRuleConstants, CubicTruncationRuleElements, Defaults, NonCubicTruncationRuleConstants,
    NonCubicTruncationRuleElements, ProjectConstants, ProjectElements, TruncationLibraryButtonNameKeys,
    TruncationLibraryKeys, TruncationLibrarySubKeys, TruncationRuleConstants,
    TruncationRuleLibraryElements,
)


@lru_cache()
def truncation_rule_element_key_to_state_key() -> Dict[TruncationRuleLibraryElements, TruncationRuleConstants]:
    return {
        CubicTruncationRuleElements.PROPORTIONS:    CubicTruncationRuleConstants.PROPORTION_INPUT,
        CubicTruncationRuleElements.SLIDERS:        CubicTruncationRuleConstants.PROPORTION_SCALE,
        CubicTruncationRuleElements.COLOR_BUTTON:   CubicTruncationRuleConstants.COLOR,
        CubicTruncationRuleElements.DROP_DOWN:      CubicTruncationRuleConstants.FACIES,
        NonCubicTruncationRuleElements.ANGLES:      NonCubicTruncationRuleConstants.ANGLES,
        BayfillTruncationRuleElements.SLANT_FACTOR: BayfillTruncationRuleConstants.SLANTED_FACTOR,
    }


@lru_cache()
def project_parameter_state_key_to_element_key() -> Dict[ProjectConstants, ProjectElements]:
    return {
        ProjectConstants.FACIES_PARAMETER_NAME:   ProjectElements.FACIES_PARAMETER_NAME,
        ProjectConstants.GAUSSIAN_PARAMETER_NAME: ProjectElements.GAUSSIAN_PARAMETER_NAME,
        ProjectConstants.GRID_MODEL_NAME:         ProjectElements.GRID_MODEL_NAME,
        ProjectConstants.WORKFLOW_NAME:           ProjectElements.WORKFLOW_NAME,
        ProjectConstants.ZONES_PARAMETER_NAME:    ProjectElements.ZONES_PARAMETER_NAME,
    }


@lru_cache()
def truncation_library_content() -> Dict[
    TruncationLibraryKeys, Dict[
        TruncationLibrarySubKeys,
        Union[
            Set[int],
            Dict[int, List[str]],
            Dict[TruncationLibraryButtonNameKeys, Union[TruncationRuleLibraryElements, bool]]
        ]
    ]
]:
    num_facies = TruncationLibrarySubKeys.NUMBER_OF_FACIES_KEY
    button_name = TruncationLibrarySubKeys.BUTTON_NAME_KEY
    actual_name_key = TruncationLibraryButtonNameKeys.ACTUAL_NAME_OF_BUTTON
    prefix_key = TruncationLibraryButtonNameKeys.IS_PREFIX
    return {
        TruncationLibraryKeys.CUBIC: {
            num_facies: {
                2: ['a', 'b', ],
                3: ['c', 'd', 'e', 'f', ],
                4: ['g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', ],
                5: ['o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', ],
            },
            button_name: {
                actual_name_key: TruncationRuleLibraryElements.CUBIC_BUTTON,
                prefix_key:      True,
            },
        },
        TruncationLibraryKeys.NON_CUBIC: {
            num_facies: {
                2: ['I', ],
                3: ['II', 'III', 'IV', ],
                4: ['V', 'VI', ],
                5: ['VII', ],
            },
            button_name: {
                actual_name_key: TruncationRuleLibraryElements.NON_CUBIC_BUTTON,
                prefix_key:      True,
            },
        },
        TruncationLibraryKeys.BAYFILL: {
            num_facies:  {5},
            button_name: {
                actual_name_key: TruncationRuleLibraryElements.BAYFILL_BUTTON,
                prefix_key:      False,
            },
        },
        TruncationLibraryKeys.CUSTOM: {
            num_facies:  {2, 3, 4, 5},
            button_name: {
                actual_name_key: TruncationRuleLibraryElements.CUSTOM_BUTTON,
                prefix_key:      False,
            },
        },
    }


@lru_cache()
def truncation_library_button_names() -> Dict[
    TruncationLibraryKeys, Union[
        Dict[TruncationLibrarySubKeys,
             Union[
                 str,
                 Union[int, Set[int]]
             ]
        ],
        List[
            Dict[TruncationLibrarySubKeys,
                 Union[
                     str,
                     Union[int, Set[int]]
                 ]
            ]
        ]
    ]
]:
    content = truncation_library_content()
    button_name_key = TruncationLibrarySubKeys.BUTTON_NAME_KEY
    num_facies_key = TruncationLibrarySubKeys.NUMBER_OF_FACIES_KEY
    library = {}
    for key in content.keys():
        button_info = content[key][TruncationLibrarySubKeys.BUTTON_NAME_KEY]
        button_name = button_info[TruncationLibraryButtonNameKeys.ACTUAL_NAME_OF_BUTTON]
        facies_information = content[key][TruncationLibrarySubKeys.NUMBER_OF_FACIES_KEY]
        if button_info[TruncationLibraryButtonNameKeys.IS_PREFIX]:
            names = []
            for number_of_facies in facies_information.keys():
                for name in facies_information[number_of_facies]:
                    names.append({button_name_key: button_name + name, num_facies_key: number_of_facies})
            library[key] = names
        else:
            if len(facies_information) == 1:
                facies_information = facies_information.pop()
            library[key] = {button_name_key: button_name, num_facies_key: facies_information}
    return library


def _get_truncation_rule_name(button_name: str) -> str:
    prefix = Defaults.PREFIX_NAME_OF_BUTTON
    truncation_rule = button_name[len(prefix):]
    # TODO: Do more?
    return truncation_rule


@lru_cache()
def truncation_library_elements(element: QWidget) -> Dict[
    TruncationLibraryKeys, Dict[TruncationLibrarySubKeys, Union[List[QWidget], QWidget, int]]
]:
    button_names = truncation_library_button_names()
    button_name_key = TruncationLibrarySubKeys.BUTTON_NAME_KEY
    num_facies_key = TruncationLibrarySubKeys.NUMBER_OF_FACIES_KEY
    truncation_rule_key = TruncationLibrarySubKeys.TRUNCATION_RULE_NAME
    return {
        key: [
            {
                button_name_key:     get_element(element, button_information[button_name_key]),
                num_facies_key:      button_information[num_facies_key],
                truncation_rule_key: _get_truncation_rule_name(button_information[button_name_key]),
            }
            for button_information in button_names[key]
        ]
        if isinstance(button_names[key], list)
        else
        {
            button_name_key:     get_element(element, button_names[key][button_name_key]),
            num_facies_key:      button_names[key][num_facies_key],
            truncation_rule_key: _get_truncation_rule_name(button_names[key][button_name_key]),
        }
        for key in button_names.keys()
    }


@lru_cache()
def truncation_library_button_to_kind_and_number_of_facies(element: QWidget) -> Dict[
    QWidget,
    Dict[
        Union[TruncationLibraryKeys, TruncationLibrarySubKeys],
        Union[TruncationLibraryKeys, int]
    ]
]:
    library = truncation_library_elements(element)
    data = {}
    for key in library.keys():
        if isinstance(library[key], list):
            for button_information in library[key]:
                _add_button_information(button_information, data, key)
        else:
            _add_button_information(library[key], data, key)
    return data


def _add_button_information(button_information, data, key):
    button = button_information[TruncationLibrarySubKeys.BUTTON_NAME_KEY]
    number_of_facies = button_information[TruncationLibrarySubKeys.NUMBER_OF_FACIES_KEY]
    truncation_rule_name = button_information[TruncationLibrarySubKeys.TRUNCATION_RULE_NAME]
    data[button] = {
        TruncationLibraryKeys.KEY:                     key,
        TruncationLibrarySubKeys.NUMBER_OF_FACIES_KEY: number_of_facies,
        TruncationLibrarySubKeys.TRUNCATION_RULE_NAME: truncation_rule_name,
    }


@lru_cache()
def get_cubic_truncation_maps():
    """
    :return:
    """
    # @formatter:off
    return {
        'a': ['H', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0]],
        'b': ['V', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0]],
        'c': ['H', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0], ['F3', 1.0, 3, 0, 0]],
        'd': ['V', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0], ['F3', 1.0, 3, 0, 0]],
        'e': ['H', ['F1', 1.0, 1, 1, 0], ['F2', 1.0, 1, 2, 0], ['F3', 1.0, 2, 0, 0]],
        'f': ['H', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 1, 0], ['F3', 1.0, 2, 2, 0]],
        'g': ['H', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0], ['F3', 1.0, 3, 0, 0], ['F4', 1.0, 4, 0, 0]],
        'h': ['V', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0], ['F3', 1.0, 3, 0, 0], ['F4', 1.0, 4, 0, 0]],
        'i': ['H', ['F1', 1.0, 1, 1, 0], ['F2', 1.0, 1, 2, 0], ['F3', 1.0, 1, 3, 0], ['F4', 1.0, 2, 0, 0]],
        'j': ['H', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 1, 0], ['F3', 1.0, 2, 2, 0], ['F4', 1.0, 2, 3, 0]],
        'k': ['H', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 1, 0], ['F3', 1.0, 2, 2, 1], ['F4', 1.0, 2, 2, 2]],
        'l': ['V', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 1, 0], ['F3', 1.0, 2, 2, 0], ['F4', 1.0, 2, 3, 0]],
        'm': ['V', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0], ['F3', 1.0, 3, 1, 0], ['F4', 1.0, 3, 2, 0]],
        'n': ['V', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 1, 1], ['F3', 1.0, 2, 1, 2], ['F4', 1.0, 2, 2, 0]],
        'o': ['H', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0], ['F3', 1.0, 3, 0, 0], ['F4', 1.0, 4, 0, 0], ['F5', 1.0, 5, 0, 0]],
        'p': ['V', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0], ['F3', 1.0, 3, 0, 0], ['F4', 1.0, 4, 0, 0], ['F5', 1.0, 5, 0, 0]],
        'q': ['V', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 1, 0], ['F3', 1.0, 2, 2, 1], ['F5', 0.5, 2, 2, 2], ['F4', 1.0, 2, 3, 1], ['F5', 0.5, 2, 3, 2]],
        'r': ['V', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0], ['F3', 1.0, 3, 1, 0], ['F4', 1.0, 3, 2, 0], ['F5', 1.0, 3, 3, 0]],
        's': ['V', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0], ['F3', 1.0, 3, 1, 0], ['F4', 1.0, 3, 2, 0], ['F5', 1.0, 4, 0, 0]],
        't': ['V', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0], ['F3', 1.0, 3, 1, 0], ['F4', 1.0, 3, 2, 0], ['F5', 1.0, 3, 3, 0]],
        'u': ['V', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0], ['F3', 1.0, 3, 1, 0], ['F4', 1.0, 3, 2, 0], ['F5', 1.0, 4, 0, 0]],
        'v': ['H', ['F1', 1.0, 1, 1, 0], ['F2', 1.0, 1, 2, 0], ['F3', 1.0, 1, 3, 0], ['F4', 1.0, 1, 4, 0], ['F5', 1.0, 2, 0, 0]],
        'w': ['H', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 1, 0], ['F3', 1.0, 2, 2, 0], ['F4', 1.0, 2, 3, 0], ['F5', 1.0, 2, 4, 0]],
    }
    # @formatter:on


@lru_cache()
def get_non_cubic_truncation_maps():
    """
    :return:
    """
    # @formatter:off
    return {
        'I':    [['F1', 45.0, 1.0], ['F2', 45.0, 1.0]],
        'II':   [['F1', 45.0, 1.0], ['F2', 0.0, 1.0],  ['F3', 0.0, 1.0]],
        'III':  [['F1', 45.0, 1.0], ['F2', 25.0, 1.0], ['F3', 0.0, 1.0]],
        'IV':   [['F1', 45.0, 1.0], ['F2', 0.0, 0.50], ['F3', 45.0, 1.0],  ['F2', 0.0, 0.5]],
        'V':    [['F1', 45.0, 1.0], ['F2', 0.0, 0.50], ['F3', 45.0, 1.0],  ['F2', 0.0, 0.5], ['F4', 0.0, 0.5]],
        'VI':   [['F1', 45.0, 1.0], ['F2', 25.0, 1.0], ['F3', 0.0, 0.5],   ['F4', 45.0, 0.5], ['F3', 0.0, 0.5]],
        'VII':  [['F1', 45.0, 1.0], ['F2', 25.0, 1.0], ['F3', 0.0, 0.5],   ['F4', 45.0, 1.0], ['F3', 0.0, 0.5], ['F5', 0.0, 1.0]],
        'VIII': [['F1', 90.0, 1.0], ['F2', 45.0, 1.0], ['F3', -45.0, 1.0], ['F4', 90.0, 1.0], ['F5', 0.0, 1.0]],
    }
    # @formatter:on
