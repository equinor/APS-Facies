#!/bin/env python
# -*- coding: utf-8 -*-
# Python3 script to update APS model file from global IPL include file

from src.algorithms.APSModel import APSModel
from src.utils.constants.simple import Debug
from src.utils.methods import get_run_parameters


def update_aps_model_from_fmu(
        global_ipl_file, input_aps_model_file, output_aps_model_file, debug_level=Debug.OFF,
        project=None, workflow_name=None,
  ):
    # Create empty APSModel object
    aps_model = APSModel()

    # Read model file and parameter file and update values in xml tree but no data
    # is put into APSModel data structure but instead an updated XML data tree is returned.
    tree = aps_model.updateXMLModelFile(
        modelFileName=input_aps_model_file, parameterFileName=global_ipl_file,
        project=project, workflow_name=workflow_name, debug_level=debug_level,
    )

    # Write the updated XML tree for the model parameters to a new file
    aps_model.writeModelFromXMLRoot(tree, output_aps_model_file)


# -------  Main ----------------
def run(roxar=None, project=None, **kwargs):
    params = get_run_parameters(**kwargs)
    input_aps_model_file = params['model_file']
    global_ipl_file = params['global_include_file']
    debug_level = params['debug_level']
    output_aps_model_file = params['output_model_file']
    workflow_name = params['workflow_name']
    update_aps_model_from_fmu(
        global_ipl_file, input_aps_model_file, output_aps_model_file, debug_level,
        project=project, workflow_name=workflow_name,
    )


if __name__ == '__main__':
    run(
        output_model_file='APS_modified.xml',
    )
