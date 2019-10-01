#!/bin/env python
# -*- coding: utf-8 -*-
# Python3 script to update APS model file from global IPL include file

from src.algorithms.APSModel import APSModel
from src.utils.constants.simple import Debug
from src.utils.methods import get_run_parameters


def updateAPSModelFromFMU(globalIPLFile, inputAPSModelFile, outputAPSModelFile, debug_level=Debug.OFF):
    # Create empty APSModel object
    apsModel = APSModel()

    # Read model file and parameter file and update values in xml tree but no data
    # is put into APSModel data structure but instead an updated XML data tree is returned.
    eTree = apsModel.updateXMLModelFile(modelFileName=inputAPSModelFile, parameterFileName=globalIPLFile, debug_level=debug_level)

    # Write the updated XML tree for the model parameters to a new file
    apsModel.writeModelFromXMLRoot(eTree, outputAPSModelFile)


# -------  Main ----------------
def run(roxar=None, project=None, **kwargs):
    params = get_run_parameters(**kwargs)
    input_aps_model_file = params['model_file']
    global_ipl_file = params['global_include_file']
    debug_level = params['debug_level']
    output_aps_model_file = params['output_model_file']
    updateAPSModelFromFMU(global_ipl_file, input_aps_model_file, output_aps_model_file, debug_level)


if __name__ == '__main__':
    run(
        output_model_file='APS_modified.xml',
    )
