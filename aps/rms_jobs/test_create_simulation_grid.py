#!/bin/python
from aps.rms_jobs.create_simulation_grid import run as run_create_grid
from aps.utils.roxar.grid_model import GridSimBoxSize
from aps.algorithms.APSModel import APSModel
from aps.utils.constants.simple import Debug


def run_test(project, aps_model_name):
    aps_model = APSModel(aps_model_name)
    max_layers = 50
    debug_level = Debug.VERBOSE
    fmu_grid_name = 'ERTBOX_TEST'

    kwargs = {
        'aps_model': aps_model,
        'fmu_simulation_grid_name': fmu_grid_name,
        'max_fmu_grid_layers': max_layers,
        'debug_level': debug_level,
    }
    run_create_grid(project=project, **kwargs)


aps_model_name = 'aps.xml'
run_test(project, aps_model_name)
