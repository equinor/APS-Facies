#!/bin/env python
# -*- coding: utf-8 -*-
from ctypes import CDLL, POINTER, c_double, c_float, c_int, c_uint

import numpy as np

from src.utils.constants.environment import DrawingLibrary
from src.utils.constants.simple import Debug, VariogramType

# Input angle for variogram is azimuth angle in degrees
# Input angle for linear trend direction is azimuth angle in degrees
#
# -----       Functions used to draw gaussian fields: -------------------------

# Global object with c/c++ code for simulation of gaussian fields
_draw2DLib = CDLL(DrawingLibrary.LIBRARY_PATH.value)

# Define input data types
_draw2DLib.draw2DGaussField.argtypes = (
    c_int, c_int,
    c_double, c_double,
    c_int, c_uint,
    c_double, c_double,
    c_double, c_double, c_int
)
# Define output data type
floatArrayPointer = POINTER(c_float)
_draw2DLib.draw2DGaussField.restype = floatArrayPointer


# Function simulating 2D gaussian field
def draw2D(
        nx, ny, xsize, ysize, variogram_type,
        iseed, range1, range2, angle, power, debug_level
):
    """

    :param nx:
    :type nx: int
    :param ny:
    :type ny: int
    :param xsize:
    :type xsize: flaot
    :param ysize:
    :type ysize: float
    :param variogram_type:
    :type variogram_type: VariogramType
    :param iseed:
    :type iseed: int
    :param range1:
    :type range1: float
    :param range2:
    :type range2: float
    :param angle:
    :type angle: float
    :param power:
    :type power: float
    :param debug_level:
    :type debug_level: Debug
    :return:
    :rtype:
    """
    if debug_level <= Debug.OFF:
        debug_level = Debug.OFF
    elif debug_level >= Debug.ON:
        debug_level = Debug.ON

    global _draw2DLib
    values = np.zeros(nx*ny,dtype=np.float32)

    # Call c/c++ function
    arrayPointer = _draw2DLib.draw2DGaussField(
        c_int(nx), c_int(ny),
        c_double(xsize), c_double(ysize),
        c_int(variogram_type.value), c_uint(iseed),
        c_double(range1), c_double(range2),
        c_double(angle), c_double(power), c_int(debug_level.value)
    )

    # Simulated values are in C index order.
    n = 0
    for i in range(nx):
        for j in range(ny):
            v = float(arrayPointer[n])
            indx = j + i*ny
            values[indx] = v
            n += 1
    return values


def simGaussFieldAddTrendAndTransform(
        iseed, nx, ny, xsize, ysize, variogramType, range1, range2,
        variogramAngle, pow, useTrend, trendAzimuth, relSigma, debug_level=Debug.OFF
):
    # Residual gaussian fields
    if debug_level >= Debug.VERY_VERBOSE:
        print('    - Simulate  2D Gauss field using seed: ' + str(iseed))
        # Variogram angle input should be azimuth angle in degrees, but angle in simulation algorithm should be
    # relative to first axis.
    variogramAngle = 90.0 - variogramAngle
    v1Residual = draw2D(
        nx, ny, xsize, ysize, variogramType, iseed,
        range1, range2, variogramAngle, pow, debug_level
    )

    # Trends for gaussian fields
    Trend1 = np.zeros(nx * ny, float)
    sigma1 = 1.0
    if useTrend:
        if debug_level >= Debug.VERY_VERBOSE:
            print('    - Add trend 2D Gauss field')
        dx = 1.0 / float(nx - 1)
        dy = 1.0 / float(ny - 1)
        ang1 = trendAzimuth * np.pi / 180.0
        sintheta = np.sin(ang1)
        costheta = np.cos(ang1)

        n = 0
        minV = 99999
        maxV = -99999
        for j in range(ny):
            y = float(j) * dy
            for i in range(nx):
                x = float(i) * dx
                x1 = x * sintheta + y * costheta
                Trend1[n] = x1  # Increasing from 0 to in x1 direction
                if x1 > maxV:
                    maxV = x1
                if x1 < minV:
                    minV = x1
                n = n + 1

        sigma1 = relSigma * (maxV - minV)
        # print( 'Sigma1: ' + str(sigma1))

    v1Trend = []
    for n in range(nx * ny):
        w = sigma1 * v1Residual[n]
        v1Trend.append(w + Trend1[n])

    # Transform into uniform distribution
    if debug_level >= Debug.VERY_VERBOSE:
        print('    - Transform 2D Gauss field')
        print('')
    transformedValues = np.zeros(nx * ny, float)
    sort_indx = np.argsort(v1Trend)
    for i in range(len(v1Trend)):
        indx = sort_indx[i]
        u = float(i) / float(nx * ny)
        transformedValues[indx] = u

    return transformedValues


def simGaussFieldAddTrendAndTransform2(
        iseed, nx, ny, xsize, ysize, variogramType, range1, range2,
        variogramAngle, pow, useTrend, trendAzimuth, relSigma, debug_level=Debug.OFF
):
    # Residual gaussian fields
    # Variogram angle input should be azimuth angle in degrees, but angle in simulation algorithm should be
    # relative to first axis.
    variogramAngle = 90.0 - variogramAngle
    v1Residual = draw2D(nx, ny, xsize, ysize, variogramType, iseed, range1, range2, variogramAngle, pow, debug_level)

    # Trends for gaussian fields
    Trend1 = np.zeros(nx * ny, float)
    sigma1 = 1.0
    if useTrend:
        print('    - Calculate trend for Gauss field')
        dx = 1.0 / float(nx - 1)
        dy = 1.0 / float(ny - 1)
        ang1 = trendAzimuth * np.pi / 180.0
        sintheta = np.sin(ang1)
        costheta = np.cos(ang1)

        n = 0
        minV = float('inf')
        maxV = -float('inf')
        for j in range(ny):
            y = float(j) * dy
            for i in range(nx):
                x = float(i) * dx
                x1 = x * sintheta + y * costheta
                Trend1[n] = x1  # Increasing from 0 to in x1 direction
                if x1 > maxV:
                    maxV = x1
                if x1 < minV:
                    minV = x1
                n = n + 1

        sigma1 = relSigma * (maxV - minV)
        # print( 'Sigma1: ' + str(sigma1))

    v1 = np.zeros(nx * ny, float)
    v1WithTrend = np.zeros(nx * ny, float)
    cumulativeX = np.zeros(nx * ny, float)
    cumulativeY = np.zeros(nx * ny, float)
    for n in range(nx * ny):
        w = sigma1 * v1Residual[n]
        v1WithTrend[n] = w + Trend1[n]
        v1[n] = w

    # Transform into uniform distribution
    print('    - Transform Gauss field')
    print('')
    transformedValues = np.zeros(nx * ny, float)
    sort_indx = np.argsort(v1WithTrend)
    for i in range(len(v1)):
        indx = sort_indx[i]
        u = float(i) / float(nx * ny)
        transformedValues[indx] = u
        cumulativeX[i] = v1WithTrend[indx]
        cumulativeY[i] = u

    return v1, v1WithTrend, transformedValues, cumulativeX, cumulativeY


def simGaussField(
        iseed: int, nx: int, ny: int, xsize: float, ysize: float, variogram_type: VariogramType,
        range_major_axis: float, range_minor_axis: float, azimuth_angle: float, power: float,
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
    :rtype:
    """
    # Residual gaussian fields
    if debug_level >= Debug.VERY_VERBOSE:
        print('    - Simulate  2D Gauss field using seed: ' + str(iseed))
    # Variogram angle input should be azimuth angle in degrees, but angle in simulation algorithm should be
    # relative to first axis.
    azimuth_angle = 90.0 - azimuth_angle

    residualField = draw2D(
        nx=nx, ny=ny, xsize=xsize, ysize=ysize, variogram_type=variogram_type, iseed=iseed,
        range1=range_major_axis, range2=range_minor_axis, angle=azimuth_angle, power=power,
        debug_level=debug_level
    )
    return residualField