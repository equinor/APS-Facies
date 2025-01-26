#!/bin/env python
# -*- coding: utf-8 -*-

"""This module is used in FMU workflows to copy a continuous 3D parameter
from geomodel grid to ERTBOX grid and extrapolate values that are undefined
in ERTBOX grid. This functionality is used when the user wants to
use FIELD keywords for petrophysical properties in ERT in Assisted History Matching.
"""

# TODO: When the stubs are removed from the APS repository (deprecated), then this function here can be removed
# It will be replaced by fmu.tools.rms function copy_rms_param

from aps.toolbox import copy_rms_param_to_ertbox_grid
from aps.utils.constants.simple import ModelFileFormat
from aps.utils.methods import get_specification_file, SpecificationType


def run(project, **kwargs):
    """
    Read model file and copy the specified parameters for each zone
    from geomodel to ertbox model.
    The undefined grid cell values in ertbox grid is assigned values. The method
    for assigning values to undefined grid cell values is choosen by the user,
    and the implemented methods are the same as in copy_rms_param_trend_to_fmu_grid.py.
    """
    if project.current_realisation > 0:
        raise ValueError(
            'In RMS models to be used with a FMU loop in ERT,'
            'the grid and parameters should be shared and realisation = 1'
        )
    params = {
        'project': project,
        'model_file_name': get_specification_file(
            _type=SpecificationType.RESAMPLE, _format=ModelFileFormat.YML, **kwargs
        ),
        'debug_level': 2,
    }

    copy_rms_param_to_ertbox_grid.run(params)
