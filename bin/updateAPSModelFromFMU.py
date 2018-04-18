#!/bin/env python
# -*- coding: utf-8 -*-
# Python3 script to update APS model file from global IPL include file

from src.algorithms.APSModel import APSModel
from src.utils.constants.simple import Debug


def updateAPSModelFromFMU(globalIPLFile, inputAPSModelFile, outputAPSModelFile, debug_level=Debug.OFF):
    # Create empty APSModel object
    apsModel = APSModel()

    # Read model file and parameter file and update values in xml tree but no data
    # is put into APSModel data structure but instead an updated XML data tree is returned.
    eTree = apsModel.updateXMLModelFile(inputAPSModelFile, globalIPLFile, debug_level)

    # Write the updated XML tree for the model parameters to a new file
    apsModel.writeModelFromXMLRoot(eTree, outputAPSModelFile)


# -------  Main ----------------
def run(roxar=None, project=None):
    globalIPLFile = "test_global_include.ipl"
    inputAPSModelFile = "APS.xml"
    outputAPSModelFile = "APS_modified.xml"
    debug_level = Debug.VERY_VERBOSE
    updateAPSModelFromFMU(globalIPLFile, inputAPSModelFile, outputAPSModelFile, debug_level)


if __name__ == '__main__':
    run()
