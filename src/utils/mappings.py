from typing import Dict

from src.utils.constants import (
    CubicTruncationRuleConstants, CubicTruncationRuleElements,
    NonCubicTruncationRuleConstants, NonCubicTruncationRuleElements, ProjectConstants, ProjectElements,
    TruncationRuleConstants, TruncationRuleElements,
)


def truncation_rule_element_key_to_state_key() -> Dict[TruncationRuleElements, TruncationRuleConstants]:
    return {
        CubicTruncationRuleElements.PROPORTIONS:  CubicTruncationRuleConstants.PROPORTION_INPUT,
        CubicTruncationRuleElements.SLIDERS:      CubicTruncationRuleConstants.PROPORTION_SCALE,
        CubicTruncationRuleElements.COLOR_BUTTON: CubicTruncationRuleConstants.COLOR,
        CubicTruncationRuleElements.DROP_DOWN:    CubicTruncationRuleConstants.FACIES,
        NonCubicTruncationRuleElements.ANGLES:    NonCubicTruncationRuleConstants.ANGLES,
    }


def project_parameter_state_key_to_element_key() -> Dict[ProjectConstants, ProjectElements]:
    return {
        ProjectConstants.FACIES_PARAMETER_NAME:   ProjectElements.FACIES_PARAMETER_NAME,
        ProjectConstants.GAUSSIAN_PARAMETER_NAME: ProjectElements.GAUSSIAN_PARAMETER_NAME,
        ProjectConstants.GRID_MODEL_NAME:         ProjectElements.GRID_MODEL_NAME,
        ProjectConstants.WORKFLOW_NAME:           ProjectElements.WORKFLOW_NAME,
        ProjectConstants.ZONES_PARAMETER_NAME:    ProjectElements.ZONES_PARAMETER_NAME,
    }
