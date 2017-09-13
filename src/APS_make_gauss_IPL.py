#!/bin/env python
# Python 3 script to make IPL script for simulation of Gauss fields.

import importlib

from src import APSGaussFieldJobs, APSMainFaciesTable, APSModel, APSZoneModel, Trend3D_linear_model_xml

importlib.reload(APSModel)
importlib.reload(APSZoneModel)
importlib.reload(APSMainFaciesTable)
importlib.reload(APSGaussFieldJobs)
importlib.reload(Trend3D_linear_model_xml)
# --------------- Start main script ------------------------------------------
print('Run: APS_make_gauss_IPL ')
modelFileName = 'APS.xml'

print('- Read file: ' + modelFileName)
apsModel = APSModel.APSModel(modelFileName)

apsModel.createSimGaussFieldIPL()

print('Finished APS_make_gauss_IPL.py')

