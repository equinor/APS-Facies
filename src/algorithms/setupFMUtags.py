#!/bin/env python
# -*- coding: utf-8 -*-
from src.utils.methods import get_run_parameters
from src.utils.roxar.fmu_tags import (
    read_selected_fmu_variables,  set_all_as_fmu_updatable,  set_selected_as_fmu_updatable,
)
from src.utils.io import write_status_file


def run(roxar=None, project=None, **kwargs):
    params = get_run_parameters(**kwargs)
    model_file = params['model_file']
    input_selected_fmu_variable_file = params['fmu_variables_file']
    output_model_file = params['output_model_file']
    tagged_variable_file = params['tagged_variables_file']
    tag_all_variables = params['tag_all_variables']
    if tag_all_variables:
        # Set all APS model parameters as FMU updatable
        set_all_as_fmu_updatable(model_file, output_model_file, tagged_variable_file)
    else:
        # Read selected FMU variables
        fmu_variables = read_selected_fmu_variables(input_selected_fmu_variable_file)
        print(fmu_variables)
        set_selected_as_fmu_updatable(model_file, output_model_file, fmu_variables, tagged_variable_file)

    write_status_file(True, 'Test_Update_FMU_parameters')


if __name__ == '__main__':
    run(
        model_file='APS.xml',
        fmu_variables_file='examples/FMU_selected_variables.dat',
        output_model_file='APS_with_FMU_tags.xml',
        tagged_variable_file='FMU_tagged_variables.dat',
        tag_all_variables=True,
    )
