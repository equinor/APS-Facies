#!/bin/env python
# Python 3 Calculate linear trend in 3D in RMS10 using roxapi
import math

import numpy as np

import src.generalFunctionsUsingRoxAPI as gr
from src.utils.constants.simple import Debug


class Trend3D_linear:
    """
    Description: Calculate linear 3D trend for specified grid cells.
    """

    def __init__(self, trendRuleModel, debug_level=Debug.OFF):
        """
        Description: Create a trend object which is used to create 3D trends using ROXAPI. 
                     Input is model parameters.
        """
        self.__className = 'Trend3D_linear'
        if trendRuleModel is None:
            print('Error in ' + self.__className)
            print('Error: Programming error. Empty trendRuleModel object')
            return

        self.__azimuth = trendRuleModel.getAzimuth()
        self.__stackingAngle = trendRuleModel.getStackingAngle()
        self.__direction = trendRuleModel.getStackingDirection()
        self.__debug_level = debug_level

    def createTrend(self, gridModel, realNumber, nDefinedCells, cellIndexDefined, zoneNumber, simBoxThickness):
        """
        Description: Create trend values for 3D grid zone using Roxar API.
        """
        # Check if specified grid model exists and is not empty
        if gridModel.is_empty():
            text = 'Error: Specified grid model: ' + gridModel.name + ' is empty.'
            raise IOError(text)
        else:
            grid3D = gridModel.get_grid(realNumber)
            gridIndexer = grid3D.simbox_indexer
            (nx, ny, nz) = gridIndexer.dimensions
            [simBoxXLength, simBoxYLength, azimuthAngle, x0, y0] = gr.getGridSimBoxSize(grid3D, self.__debug_level)

            cellCenterPoints = grid3D.get_cell_centers(cellIndexDefined)
            cellIndices = gridIndexer.get_indices(cellIndexDefined)

            zoneName = grid3D.zone_names[zoneNumber - 1]
            zonation = gridIndexer.zonation
            layerRanges = zonation[zoneNumber - 1]
            n = 0
            for layer in layerRanges:
                for k in layer:
                    n += 1
            nLayersInZone = n
            zinc = simBoxThickness / nLayersInZone
            if self.__debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: In ' + self.__className)
                print('Debug output:  Zone name: ' + zoneName)
                print('Debug output:  SimboxThickness: ' + str(simBoxThickness))
                print('Debug output:  Zinc: ' + str(zinc))
                print('Debug output:  nx,ny,nz: ' + str(nx) + ' ' + str(ny) + ' ' + str(nz))
                print('Debug output:  Number of layers in zone: ' + str(nLayersInZone))

                # Create an empty array with 0 values with correct length
                # corresponding to all active cells in the grid
            # values = grid3D.generate_values(np.float32)
            valuesInSelectedCells = np.zeros(nDefinedCells, np.float32)

            # Calculate the 3D trend values

            alpha = (90.0 - self.__stackingAngle) * np.pi / 180.0
            if self.__direction == 1:
                theta = self.__azimuth * np.pi / 180.0
            else:
                theta = (self.__azimuth + 180.0) * np.pi / 180.0

            # Normal vector to a plane with constant trend value is [xComponent,yComponent,zComponent]
            xComponent = math.cos(alpha) * math.sin(theta)
            yComponent = math.cos(alpha) * math.cos(theta)
            zComponent = math.sin(alpha)

            if self.__debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: In ' + self.__className)
                print(
                    'Debug output: normal vector: ' + '(' + str(xComponent) + ', ' + str(yComponent) + ', ' + str(
                        zComponent) + ')'
                )

            for indx in range(nDefinedCells):
                x = cellCenterPoints[indx, 0]
                y = cellCenterPoints[indx, 1]
                z = cellCenterPoints[indx, 2]

                i = cellIndices[indx, 0]
                j = cellIndices[indx, 1]
                k = cellIndices[indx, 2]

                # Coordinates relative to a local origo (xmin,ymin) for x,y
                # The depth coordinate zSimBox is relative to simulation box
                xRel = x - x0
                yRel = y - y0
                zSimBox = (k + 0.5) * zinc
                trendValue = xComponent * xRel + yComponent * yRel + zComponent * zSimBox
                valuesInSelectedCells[indx] = trendValue
            minValue = valuesInSelectedCells.min()
            maxValue = valuesInSelectedCells.max()
            minmaxDifference = maxValue - minValue
            valuesRescaled = self.__direction * valuesInSelectedCells / minmaxDifference

            minValue = valuesRescaled.min()
            maxValue = valuesRescaled.max()
            minmaxDifference = maxValue - minValue
        return [minmaxDifference, valuesRescaled]

    def getAzimuth(self):
        return self.__azimuth

    def getStackingAngle(self):
        return self.__stackingAngle

    def getStackingDirection(self):
        return self.__direction
