# This module is used in FMU workflows to import gaussian field values from disk into APS. 
# Here we can assume that the project.current_realisation = 0 always since FMU ONLY run with one 
# realization in the RMS project and should have shared grid and shared parameters only.

import xtgeo

from aps.algorithms.APSModel import APSModel
from aps.utils.constants.simple import Debug


def get_grid_rotation(geometry):
    return geometry['avg_rotation']


def get_origin(geometry):
    keys = ['xori', 'yori', 'zori']
    return tuple(geometry[key] for key in keys)


def get_increments(geometry):
    return tuple(geometry[f'avg_d{axis}'] for axis in ('x', 'y', 'z'))


def run(
        *,
        project,
        aps_model:                APSModel,
        fmu_simulation_grid_name: str,
        max_fmu_grid_depth:       int,
        debug_level:              Debug,
        **kwargs,
):
    if project.current_realisation > 0:
        raise ValueError(f'In RMS models to be used with a FMU loop in ERT,'
                         'the grid and parameters should be shared and realisation = 1'
        )

    if debug_level >= Debug.ON:
        print(f'-- Creating ERT simulation box: {fmu_simulation_grid_name}')
    if debug_level >= Debug.VERBOSE:
        print(f'-- Using grid model: {aps_model.grid_model_name} as reference grid')
        print(f'-- Using realization number: {project.current_realisation} for reference grid') 
    reference_grid = xtgeo.grid_from_roxar(project, aps_model.grid_model_name, project.current_realisation)
    nx, ny, _ = reference_grid.dimensions
    dimension = nx, ny, max_fmu_grid_depth
    geometry = reference_grid.get_geometrics(return_dict=True)

    simulation_grid = xtgeo.Grid()
    simulation_grid.create_box(
        dimension,
        origin=get_origin(geometry),
        rotation=get_grid_rotation(geometry),
        increment=get_increments(geometry),
        flip=reference_grid.estimate_flip(),
    )
    simulation_grid.to_roxar(project, fmu_simulation_grid_name, project.current_realisation)
