from functools import lru_cache
from typing import Dict, List, Set, Union

from PyQt5.QtWidgets import QWidget

from src.gui.wrappers.base_classes.getters.general import get_element
from src.utils.constants.constants import (
    BayfillTruncationRuleConstants, BayfillTruncationRuleElements,
    CubicTruncationRuleConstants, CubicTruncationRuleElements, NonCubicTruncationRuleConstants,
    NonCubicTruncationRuleElements, ProjectConstants, ProjectElements, TruncationLibraryButtonNameKeys,
    TruncationLibraryKeys, TruncationLibrarySubKeys, TruncationRuleConstants,
    TruncationRuleLibraryElements,
)


@lru_cache()
def truncation_rule_element_key_to_state_key() -> Dict[TruncationRuleLibraryElements, TruncationRuleConstants]:
    return {
        CubicTruncationRuleElements.PROPORTIONS: CubicTruncationRuleConstants.PROPORTION_INPUT,
        CubicTruncationRuleElements.SLIDERS: CubicTruncationRuleConstants.PROPORTION_SCALE,
        CubicTruncationRuleElements.COLOR_BUTTON: CubicTruncationRuleConstants.COLOR,
        CubicTruncationRuleElements.DROP_DOWN: CubicTruncationRuleConstants.FACIES,
        NonCubicTruncationRuleElements.ANGLES: NonCubicTruncationRuleConstants.ANGLES,
        BayfillTruncationRuleElements.SLANT_FACTOR: BayfillTruncationRuleConstants.SLANTED_FACTOR,
    }


@lru_cache()
def project_parameter_state_key_to_element_key() -> Dict[ProjectConstants, ProjectElements]:
    return {
        ProjectConstants.FACIES_PARAMETER_NAME: ProjectElements.FACIES_PARAMETER_NAME,
        ProjectConstants.GAUSSIAN_PARAMETER_NAME: ProjectElements.GAUSSIAN_PARAMETER_NAME,
        ProjectConstants.GRID_MODEL_NAME: ProjectElements.GRID_MODEL_NAME,
        ProjectConstants.WORKFLOW_NAME: ProjectElements.WORKFLOW_NAME,
        ProjectConstants.ZONES_PARAMETER_NAME: ProjectElements.ZONES_PARAMETER_NAME,
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
                prefix_key: True,
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
                prefix_key: True,
            },
        },
        TruncationLibraryKeys.BAYFILL: {
            num_facies: {5},
            button_name: {
                actual_name_key: TruncationRuleLibraryElements.BAYFILL_BUTTON,
                prefix_key: False,
            },
        },
        TruncationLibraryKeys.CUSTOM: {
            num_facies: {2, 3, 4, 5},
            button_name: {
                actual_name_key: TruncationRuleLibraryElements.CUSTOM_BUTTON,
                prefix_key: False,
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


@lru_cache()
def truncation_library_elements(element: QWidget) -> Dict[
    TruncationLibraryKeys, Dict[TruncationLibrarySubKeys, Union[List[QWidget], QWidget, int]]
]:
    button_names = truncation_library_button_names()
    button_name_key = TruncationLibrarySubKeys.BUTTON_NAME_KEY
    num_facies_key = TruncationLibrarySubKeys.NUMBER_OF_FACIES_KEY
    return {
        key: [
            {
                button_name_key: get_element(element, button_information[button_name_key]),
                num_facies_key: button_information[num_facies_key]
            }
            for button_information in button_names[key]
        ]
        if isinstance(button_names[key], list)
        else
        {
            button_name_key: get_element(element, button_names[key][button_name_key]),
            num_facies_key: button_names[key][num_facies_key],
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
    data[button] = {
        TruncationLibraryKeys.KEY: key,
        TruncationLibrarySubKeys.NUMBER_OF_FACIES_KEY: number_of_facies
    }
