#!/bin/env python
# -*- coding: utf-8 -*-

import nrlib
import numpy as np

from src.utils.constants.simple import Debug, VariogramType


def simGaussField(iseed: int, nx: int, ny: int, xsize: float, ysize: float, variogram_type: VariogramType,
                  range_major_axis: float, range_minor_axis: float, azimuth_angle: float, power: float = None,
                  debug_level: Debug = Debug.OFF
                  ):
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
    nrlib.seed(iseed)

    # Have to define input to nrlib as 90-azimuth since it is based on
    # a right handed coordinate system and not a left handed as in RMS
    azimuth_angle = 90.0 - azimuth_angle

    # Define variogram
    variogram_name = variogram_type.name.upper()
    if variogram_name == 'GENERAL_EXPONENTIAL':
        assert power is not None
        simVariogram = nrlib.variogram(variogram_name, main_range=range_major_axis, perp_range=range_minor_axis, azimuth=azimuth_angle, power=power)
    else:
        simVariogram = nrlib.variogram(variogram_name, main_range=range_major_axis, perp_range=range_minor_axis, azimuth=azimuth_angle)

    dx = xsize / nx
    dy = ysize / ny
    dz = 1.0
    nz = 1

    # Simulate gauss field. Return numpy 1D vector in F order
    [nx_padding, ny_padding] = nrlib.simulation_size(simVariogram, nx, dx, ny, dy)
    if debug_level >= Debug.VERY_VERBOSE:
        print('Debug output: nx_padding: {}     ny_padding: {}'.format(str(nx_padding), str(ny_padding)))

    # Have to remap the array to get it correct when plotting. That is why switching nx by ny and so on and the remapping
    # of the result vector.
    gauss_vector = nrlib.simulate(simVariogram, nx, dx, ny, dy)
    a = np.reshape(gauss_vector, (nx, ny), 'F')
    gauss_vector = np.reshape(a, (nx * ny), 'F')
    return gauss_vector
