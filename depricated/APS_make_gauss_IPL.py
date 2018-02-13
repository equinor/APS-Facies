#!/bin/env python
# -*- coding: utf-8 -*-
# Python 3 script to make IPL script for simulation of Gauss fields.

from src.algorithms.APSModel import APSModel


def run(roxar=None, project=None):
    print('Run: APS_make_gauss_IPL ')
    modelFileName = 'APS.xml'

    print('- Read file: ' + modelFileName)
    apsModel = APSModel(modelFileName)

    apsModel.createSimGaussFieldIPL()

    print('Finished APS_make_gauss_IPL.py')


# --------------- Start main script ------------------------------------------
if __name__ == '__main__':
    run()
