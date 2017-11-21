#!/bin/env python
# Python 3 script to make IPL script for simulation of Gauss fields.
import sys
import importlib

import src.APSModel

importlib.reload(src.APSModel)

from src.APSModel import APSModel

# --------------- Start main script ------------------------------------------
print('Run: APS_make_gauss_IPL ')
modelFileName = 'APS.xml'

print('- Read file: ' + modelFileName)
apsModel = APSModel(modelFileName)

apsModel.createSimGaussFieldIPL()

print('Finished APS_make_gauss_IPL.py')
