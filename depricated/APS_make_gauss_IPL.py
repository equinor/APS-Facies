#!/bin/env python
# -*- coding: utf-8 -*-
# Python 3 script to make IPL script for simulation of Gauss fields.
from warnings import warn

from src.algorithms.APSModel import APSModel
from src.utils.methods import get_specification_file


def run(roxar=None, project=None, **kwargs):
    warn("deprecated", DeprecationWarning)
    print('Run: APS_make_gauss_IPL')
    model_file_name = get_specification_file(**kwargs)

    print('- Read file: {}'.format(model_file_name))
    aps_model = APSModel(model_file_name)

    aps_model.createSimGaussFieldIPL()

    print('Finished APS_make_gauss_IPL.py')


# --------------- Start main script ------------------------------------------
if __name__ == '__main__':
    run()
