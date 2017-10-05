#!/bin/env python
# Python 3 script to make IPL script for simulation of Gauss fields.

import importlib

from src import APSModel

importlib.reload(APSModel)
# --------------- Start main script ------------------------------------------
print('Run: APS_make_gauss_IPL ')
modelFileName = 'APS.xml'

print('- Read file: ' + modelFileName)
apsModel = APSModel.APSModel(modelFileName)

apsModel.createSimGaussFieldIPL()

print('Finished APS_make_gauss_IPL.py')
