#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from src.utils.simGauss2D_nrlib import simGaussField
from src.utils.constants.simple import Debug, VariogramType
from src.utils.io import writeFileRTF


def run():
    nx = 150
    ny = 150
    xLength = 10000.0
    yLength = 10.0
    dx = xLength / nx
    dy = yLength / ny
    variogramType = VariogramType.GENERAL_EXPONENTIAL
    mainRange = 2000.0
    perpRange = 1.0
    azimuth = 90.0
    power = 1.0
    debug_level = Debug.VERY_VERBOSE
    iseed = 829292922888
    iseed = 9829292922888
    fileName = 'test1.dat'
    if variogramType == VariogramType.GENERAL_EXPONENTIAL:
        gaussVector = simGaussField(iseed, nx, ny, xLength, yLength, variogramType, mainRange, perpRange, (90.0 - azimuth), power, debug_level)
    else:
        gaussVector = simGaussField(iseed, nx, ny, xLength, yLength, variogramType, mainRange, perpRange, (90.0 - azimuth), debug_level=debug_level)
    x0 = 0.0
    y0 = 0.0
    writeFileRTF(fileName, gaussVector, nx, ny, dx, dy, x0, y0, debug_level)


if __name__ == '__main__':
    run()
