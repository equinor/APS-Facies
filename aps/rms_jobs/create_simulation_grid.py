''' This module is used in FMU workflows to import gaussian field values from 
    disk into APS. Here we can assume that the project.current_realisation = 0 
    always since FMU ONLY run with one realization in the RMS project and 
    should have shared grid and shared parameters only. The grid model to be
    created here should have same lateral grid size and grid increments and
    same rotation. The number of layers is use defined, and the vertical
    z increment can be arbitary. The purpose of the grid is to be a 3D array
    to save the GRF values to be exchanged between ERT and APS.
'''

import xtgeo

from numpy import pi
from roxar import Direction

from aps.algorithms.APSModel import APSModel
from aps.utils.constants.simple import Debug
from aps.utils.roxar.grid_model import GridSimBoxSize
from aps.utils.roxar.progress_bar import APSProgressBar
from aps.utils.constants.simple import FlipDirectionXtgeo

def get_grid_rotation(geometry):
    return geometry['avg_rotation']


def get_origin(geometry):
    keys = ['xori', 'yori', 'zori']
    return tuple(geometry[key] for key in keys)


def get_increments(geometry):
    return tuple(geometry[f'avg_d{axis}'] for axis in ('x', 'y', 'z'))

def create_ertbox_grid_model(project, geo_grid_model_name: str,
    fmu_simulation_grid_name: str, max_fmu_grid_layers: int, debug_level: Debug = Debug.OFF):
    if project.current_realisation > 0:
        raise ValueError(f'In RMS models to be used with a FMU loop in ERT,'
                         'the grid and parameters should be shared and realisation = 1'
        )

    print(f'-- Creating ERT simulation box: {fmu_simulation_grid_name}')
    if debug_level >= Debug.VERBOSE:
        print(f'-- Using grid model: {geo_grid_model_name} as reference grid')

    grid_model = project.grid_models[geo_grid_model_name]
    grid = grid_model.get_grid(project.current_realisation)

    attributes = GridSimBoxSize(grid, debug_level=debug_level)
    # The number of cells is defined by the simbox grid dimensions.
    # The physical size of the simulation box grid defined below is defined such that
    # the grid increments match the average grid increments of the physical 3D grid.
    # The thickness and depth of the grid are arbitrarily choosen.

    simbox_nx = attributes.simbox_nx
    simbox_ny = attributes.simbox_ny
    xinc = attributes.x_length / attributes.nx
    yinc = attributes.y_length / attributes.ny
    x_length = xinc * simbox_nx
    y_length = yinc * simbox_ny
    z_length = 100.0
    simbox_nz = max_fmu_grid_layers
    zinc = z_length / simbox_nz

    # The origo for simbox grid is defined from the 3D grid with real geometry.
    # It is not identical since the sim box may have larger number of grid cells
    # than the geo grid due to reverse stair step faults.
    # The origo is calculated by first calculating the midpoint of the four
    # corner points of the geogrid and use that as origo for a rotation
    # of a rectangle with length and width estimated from the geogrid and with
    # the centerpoint of the rectangle in the same location as the centerpoint
    # from the geo grid. The orientation will be the same as the orientation
    # estimated from the geo grid. There are no practical consequences that
    # there are small differences in xy layout of the simbox grid and the
    # geo grid since the simbox grids main purpose is to be a 3D array keeping
    # property values to be exchanged with ERT. Since it simplifies correct
    # handling of variogram parameters and anisotropy directions the orientation
    # should be as close to the geo grid as possible and the grid increments
    # should also be as close as possible with the geo grid.

    rotation_anticlockwise_degrees = -attributes.azimuth_angle

    # Origo is upper left if flip is UPPER_LEFT_CORNER 
    # and lower left if flip = LOWER_LEFT_CORNER

    flip = FlipDirectionXtgeo.LOWER_LEFT_CORNER
    if attributes.handedness == Direction.right:
        flip = FlipDirectionXtgeo.UPPER_LEFT_CORNER

    x0, y0 = attributes.estimated_origo(flip=flip)
    z0 = 0.0
    if debug_level >= Debug.VERY_VERBOSE:
      print(f'--- Simbox rotation origo: ({x0}, {y0})')
   
    dimension = (simbox_nx, simbox_ny, simbox_nz)
    origin =(x0, y0, z0)

    increment = (xinc, yinc, zinc)

    # xtgeo create_box assume counter clockwise rotation in contrast to RMS
    try:
        simulation_grid = xtgeo.create_box_grid(
            dimension,
            origin=origin,
            rotation=rotation_anticlockwise_degrees,
            increment=increment,
            flip=flip,
        )
        simulation_grid.to_roxar(project, fmu_simulation_grid_name, project.current_realisation)
    except:
        print(f'Error when creating grid model: {fmu_simulation_grid_name}')
        return False
    return True

def run(
        *,
        project,
        aps_model:                APSModel,
        fmu_simulation_grid_name: str,
        max_fmu_grid_layers:       int,
        debug_level:              Debug,
        **kwargs,
):
    create_ertbox_grid_model(project,
        aps_model.grid_model_name,
        fmu_simulation_grid_name,
        max_fmu_grid_layers,
        debug_level=debug_level)

    APSProgressBar.increment()

