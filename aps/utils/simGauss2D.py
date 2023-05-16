#!/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional

import gaussianfft
import numpy as np

from aps.utils.constants.simple import Debug, VariogramType


def simGaussField(
        iseed: int,
        nx: int,
        ny: int,
        xsize: float,
        ysize: float,
        variogram_type: VariogramType,
        range_major_axis: float,
        range_minor_axis: float,
        azimuth_angle: float,
        power: Optional[float] = None,
        debug_level: Debug = Debug.OFF
) -> np.ndarray:
    """
    Simulation of 2D Gaussian field for a grid with (nx,ny) grid cells and length and width (xsize, ysize).
    Correlation lengths are range1 in main direction and range2 in orthogonal direction.
    The angle is azimuth (angle clockwise measured from y -axis).
    variogramType is specified by an number, see heading of the file for variogram type
    :param iseed:
    :type iseed: int
    :param nx:
    :type nx: int
    :param ny:
    :type ny:int
    :param xsize:
    :type xsize: float
    :param ysize:
    :type ysize: float
    :param variogram_type:
    :type variogram_type: VariogramType
    :param range_major_axis:
    :type range_major_axis: float
    :param range_minor_axis:
    :type range_minor_axis: float
    :param azimuth_angle:
    :type azimuth_angle: float
    :param power:
    :type power: float
    :param debug_level:
    :type debug_level: Debug
    :return:
    :rtype: numpy 1D vector in F ordering representing 2D simulated field
    """
    # Residual gaussian fields
    if debug_level >= Debug.VERY_VERBOSE:
        print('Debug output:  Simulate  2D Gauss field using seed: ' + str(iseed))

    # Set startSeed
    gaussianfft.seed(iseed)

    # Have to define input to gaussianfft as 90-azimuth since it is based on
    # a right handed coordinate system and not a left handed as in RMS
    azimuth_angle = 90.0 - azimuth_angle

    # Define variogram
    variogram_name = variogram_type.name.upper()
    kwargs = {'main_range': range_major_axis, 'perp_range': range_minor_axis, 'azimuth': azimuth_angle}
    if variogram_type == VariogramType.GENERAL_EXPONENTIAL:
        assert power is not None
        kwargs['power'] = power
    sim_variogram = gaussianfft.variogram(variogram_name, **kwargs)

    dx = xsize / nx
    dy = ysize / ny
    dz = 1.0
    nz = 1

    # Simulate gauss field. Return numpy 1D vector in F order
    if debug_level >= Debug.VERY_VERBOSE:
        padding = gaussianfft.simulation_size(sim_variogram, nx, dx, ny, dy, nz, dz)
        coordinates = ['x', 'y', 'z']
        debug_info = 'Debug output: '
        for i in range(len(padding)):
            debug_info += 'n{coordinate}_padding: {value}     '.format(coordinate=coordinates[i], value=padding[i])
        print(debug_info.strip())

    # Have to remap the array to get it correct when plotting.
    # That is why switching nx by ny and so on and the remapping of the result vector.
    gauss_vector = gaussianfft.simulate(sim_variogram, nx, dx, ny, dy)
    a = np.reshape(gauss_vector, (nx, ny), 'F')
    gauss_vector = np.reshape(a, (nx * ny), 'F')
    return gauss_vector
