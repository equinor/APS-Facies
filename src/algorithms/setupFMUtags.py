#!/bin/env python
# -*- coding: utf-8 -*-
from src.algorithms.APSModel import APSModel
from src.utils.constants.simple import Debug, VariogramType, TrendType
from src.utils.roxar.fmu_tags import read_selected_fmu_variables,  set_all_as_fmu_updatable,  set_selected_as_fmu_updatable


if __name__ == '__main__':
    input_model_file = 'APS.xml'
    input_selected_FMU_variable_file = 'FMU_selected_variables.dat'
    output_model_file = 'APS_with_FMU_tags.xml'
    tagged_variable_file = 'FMU_tagged_variables.dat'
    tag_all_variables = True

    if tag_all_variables:
        # Set all APS model parameters as FMU updatable
        set_all_as_fmu_updatable(input_model_file, output_model_file, tagged_variable_file)
    else:
        # Read selected FMU variables
        fmu_variables = read_selected_fmu_variables(input_selected_FMU_variable_file)
        print(fmu_variables)
        set_selected_as_fmu_updatable(input_model_file, output_model_file, fmu_variables, tagged_variable_file)
