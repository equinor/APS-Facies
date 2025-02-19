#!/bin/env python
# -*- coding: utf-8 -*-
# Python3 script to update APS model file from global_variables (yml or IPL) file
from pathlib import Path

from aps.algorithms.APSModel import APSModel
from aps.utils.constants.simple import Debug
from aps.utils.methods import get_run_parameters, get_debug_level
from aps.utils.roxar.progress_bar import APSProgressBar


def update_aps_model_from_fmu(
    global_variables_file,
    input_aps_model_file,
    output_aps_model_file,
    debug_level=Debug.OFF,
    project=None,
    workflow_name=None,
    current_job_name=None,
):
    # Create empty APSModel object
    aps_model = APSModel()
    aps_model.debug_level = debug_level

    # Read model file and parameter file and update values in xml tree but no data
    # is put into APSModel data structure but instead an updated XML data tree is returned.
    tree = aps_model.update_model_file(
        model_file_name=Path(input_aps_model_file),
        parameter_file_name=Path(global_variables_file),
        project=project,
        workflow_name=workflow_name,
        current_job_name=current_job_name,
        debug_level=debug_level,
    )

    # Write the updated XML tree for the model parameters to a new file
    aps_model.write_model_from_xml_root(tree, output_aps_model_file)


# ------- Main ----------------
def run(project, **kwargs):
    params = get_run_parameters(**kwargs)
    input_aps_model_file = params['model_file']
    global_variables_file = params['global_variables_file']
    debug_level = get_debug_level(**kwargs)
    output_aps_model_file = params['output_model_file']
    workflow_name = params['workflow_name']
    current_job_name = params['current_job_name']

    if global_variables_file:
        print(f'\nUpdate APS model parameters from FMU parameters')
        if debug_level >= Debug.ON:
            print(
                f'- Read file with global variables from FMU: {global_variables_file}'
            )
        update_aps_model_from_fmu(
            global_variables_file,
            input_aps_model_file,
            output_aps_model_file,
            debug_level=debug_level,
            project=project,
            workflow_name=workflow_name,
            current_job_name=current_job_name,
        )
    else:
        if debug_level >= Debug.ON:
            print(
                'No global variables file was found. Check FMU project or aps_config.yml file if that is used.'
            )

    APSProgressBar.increment()
