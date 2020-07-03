import xtgeo

from src.algorithms.APSModel import APSModel
from src.utils.constants.simple import Debug


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
    if debug_level >= Debug.ON:
        print(f'Creating ERT simulation box; {fmu_simulation_grid_name}')
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
