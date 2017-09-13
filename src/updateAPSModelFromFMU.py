#!/bin/env python
# Python3 script to update APS model file from global IPL include file

from src import APSModel
import importlib

importlib.reload(APSModel)


def updateAPSModelFromFMU(globalIPLFile,inputAPSModelFile,outputAPSModelFile,printInfo):
    # Create empty APSModel object
    apsModel = APSModel.APSModel()

    # Read model file and parameter file and update values in xml tree but no data 
    # is put into APSModel data structure but instead an updated XML data tree is returned.
    eTree = apsModel.updateXMLModelFile(inputAPSModelFile,globalIPLFile,printInfo)

    # Write the updated XML tree for the model parameters to a new file
    apsModel.writeModelFromXMLRoot(eTree,outputAPSModelFile)
    return
# -------  Main ----------------
globalIPLFile      = "test_global_include.ipl"
inputAPSModelFile  = "APS.xml"
outputAPSModelFile = "APS_modified.xml"
printInfo = 3
updateAPSModelFromFMU(globalIPLFile,inputAPSModelFile,outputAPSModelFile,printInfo)
