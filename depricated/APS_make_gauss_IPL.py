#!/bin/env python
# Python 3 script to make IPL script for simulation of Gauss fields.
import importlib

import src.algorithms.APSModel

importlib.reload(src.algorithms.APSModel)

from src.algorithms.APSModel import APSModel


# --------------- Start main script ------------------------------------------
if __name__ == '__main__':
    print('Run: APS_make_gauss_IPL ')
    modelFileName = 'APS.xml'

    print('- Read file: ' + modelFileName)
    apsModel = APSModel(modelFileName)

    apsModel.createSimGaussFieldIPL()

    print('Finished APS_make_gauss_IPL.py')
