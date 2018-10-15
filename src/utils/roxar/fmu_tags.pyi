# -*- coding: utf-8 -*-
from typing import Optional, List, Tuple


FmuParameter = Tuple[str, int, int, str, str]


def get_list_of_aps_uncertainty_parameters(
        project,
        workflow_name
): ...
def read_selected_fmu_variables(
        input_selected_fmu_variable_file: str
) -> List[FmuParameter]: ...
def set_all_as_fmu_updatable(
        input_model_file:                 str,
        output_model_file:                str,
        tagged_variable_file:             Optional[str]       = None
) -> None: ...
def set_selected_as_fmu_updatable(
        input_model_file:                 str,
        output_model_file:                str,
        selected_variables:               List[FmuParameter],
        tagged_variable_file:             Optional[str]       = None,
) -> None: ...
