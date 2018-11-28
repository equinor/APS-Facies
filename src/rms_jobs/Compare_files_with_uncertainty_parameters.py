# -*- coding: utf-8 -*-
from src.utils.roxar.compare_files import run

run(
    file_name1='examples/reference_uncertainty_parameter_list.dat',
    file_name2='tmp_Test_APS_uncertainty_workflow.dat',
    workflow_name='Test_Update_FMU_parameters',
)
