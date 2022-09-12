#!/bin/env python
# -*- coding: utf-8 -*-
''' This module is used in FMU workflows to copy a continuous 3D parameter
    from geomodel grid to ERTBOX grid and extrapolate values that are undefined
    in ERTBOX grid. This functionality is used when the user wants to
    use FIELD keywords for petrophysical properties in ERT in Assisted History Matching.
'''

from aps.toolbox.copy_rms_param_to_ertbox_grid import run as run_copy_rms_param_to_ertbox
from aps.utils.constants.simple import Debug
from aps.utils.methods import get_debug_level, get_specification_file, SpecificationType



def run(project, **kwargs):
    """
    Read model file and copy the specified parameters for each zone
    from geomodel to ertbox model.
    The undefined grid cell values in ertbox grid is assigned values. The method
    for assigning values to undefined grid cell values is choosen by the user,
    and the implemented methods are the same as in copy_rms_param_trend_to_fmu_grid.py.
    """

    if project.current_realisation > 0:
        raise ValueError(f'In RMS models to be used with a FMU loop in ERT,'
                         'the grid and parameters should be shared and realisation = 1'
        )
    model_file_name = get_specification_file(_type=SpecificationType.RESAMPLE, **kwargs)
    debug_level = get_debug_level(**kwargs)
    params = {
        'project': project,
        'model_file_name': model_file_name,
        'debug_level': debug_level,
    }
    run_copy_rms_param_to_ertbox(params)


if __name__ == "__main__":
    run(project,debug_level=Debug.VERBOSE)

