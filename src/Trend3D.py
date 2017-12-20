#!/bin/env python
# Copyright 2017 Statoil ASA
#
# Class for Trends used in APS modelling
# Subclass for each trend type
#  - linear
#  - elliptic
#  - hyperbolic
#  - sinusoidal
#
####################################################################
# Kari B. Skjerve, karbor@statoil.com
# 2017
####################################################################

import math
import numpy as np
import importlib 
from xml.etree.ElementTree import Element
import src.utils.xml
importlib.reload(src.utils.xml)

from src.utils.constants.simple import Debug, OriginType, TrendType
from src.utils.xml import getFloatCommand, getIntCommand, getTextCommand


class Trend3D:
    """
    Description: Parent class for Trend3D
    """
    def __init__(self, trendRuleXML, modelFileName=None, debug_level=Debug.OFF):
        self._azimuth = 0.0
        self._stackingAngle = 0.0
        self._direction = 1
        self._debug_level = debug_level
        self.type = TrendType.NONE
        self._className = self.__class__.__name__

    def _interpretXMLTree(self, trendRuleXML, modelFileName, debug_level=Debug.OFF):
        # Initialize object form xml tree object trendRuleXML

        if self._debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: Trend3D:')
            print('Debug output: Azimuth:        ' + str(self._azimuth))
            print('Debug output: Stacking angle: ' + str(self._stackingAngle))
            print('Debug output: Stacking type:  ' + str(self._direction))

        self._azimuth = getFloatCommand(trendRuleXML, 'azimuth', modelFile=modelFileName)
        if self._azimuth < 0.0 or self._azimuth > 360.0:
            raise ValueError(
                'Error: In {}\n'
                'Error: Azimuth angle for linear trend is not within [0,360] degrees.'
                ''.format(self._className)
            )

        self._direction = getIntCommand(trendRuleXML, 'directionStacking', modelFile=modelFileName)
        if self._direction != -1 and self._direction != 1:
            raise ValueError(
                'Error: In {}\n'
                'Error: Direction for linear trend is specified to be: {}\n'
                'Error: Direction for linear trend must be 1 if stacking angle is positive\n'
                '       when moving in positive azimuth direction and -1 if stacking angle\n'
                '       is positive when moving in negative azimuth direction.'
                ''.format(self._className, self._direction)
            )

        self._stackingAngle = getFloatCommand(
            trendRuleXML, 'stackAngle', modelFile=modelFileName
        )

        if self._stackingAngle < 0.0 or self._stackingAngle > 90.0:
            raise ValueError(
                'Error: In {}\n'
                'Error: Stacking angle for linear trend is not within [0,90] degrees.'
                ''.format(self._className)
            )

    def _XMLAddElementTag(self, trendElement):
        tag = 'azimuth'
        obj = Element(tag)
        obj.text = ' ' + str(self._azimuth) + ' '
        trendElement.append(obj)

        tag = 'directionStacking'
        obj = Element(tag)
        obj.text = ' ' + str(self._direction) + ' '
        trendElement.append(obj)

        tag = 'stackAngle'
        obj = Element(tag)
        obj.text = ' ' + str(self._stackingAngle) + ' '
        trendElement.append(obj)

    def initialize(self, azimuthAngle, stackingAngle, direction, debug_level=Debug.OFF):
        if debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: Call the initialize function in ' + self._className)

        if azimuthAngle < 0.0 or azimuthAngle > 360.0:
            raise ValueError(
                'Error: In {}\n'
                'Error: Cannot set azimuth angle for linear trend outside interval [0,360] degrees.'
                ''.format(self._className)
            )
        if stackingAngle < 0.0 or stackingAngle > 90.0:
            raise ValueError(
                'Error in {}\n'
                'Error: Cannot set stacking angle to be outside interval [0,90] degrees.'
                ''.format(self._className)
            )
        if direction != -1 and direction != 1:
            raise ValueError(
                'Error in {}\n'
                'Error: Cannot set stacking type to be a number different from -1 and 1.'
                ''.format(self._className)
            )
        self._azimuth = azimuthAngle
        self._stackingAngle = stackingAngle
        self._direction = direction
        self._debug_level = debug_level
        if self._debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: Trend:')
            print('Debug output: Azimuth:        ' + str(self._azimuth))
            print('Debug output: Stacking angle: ' + str(self._stackingAngle))
            print('Debug output:Stacking type:   ' + str(self._direction))

    def getAzimuth(self):
        return self._azimuth

    def getStackingAngle(self):
        return self._stackingAngle

    def getStackingDirection(self):
        return self._direction

    def setAzimuth(self, angle):
        if angle < 0.0 or angle > 360.0:
            raise ValueError(
                'Error: In {}\n'
                'Error: Cannot set azimuth angle for linear trend outside interval [0,360] degrees'
                ''.format(self._className)
            )
        else:
            self._azimuth = angle

    def setStackingAngle(self, stackingAngle):
        if stackingAngle < 0.0 or stackingAngle > 90.0:
            raise ValueError(
                'Error in {}\n'
                'Error: Cannot set stacking angle to be outside interval [0,90] degrees.'
                ''.format(self._className)
            )
        else:
            self._stackingAngle = stackingAngle

    def setStackingDirection(self, direction):
        if direction != -1 and direction != 1:
            raise ValueError(
                'Error in {}\n'
                'Error: Cannot set stacking type to be a number different from -1 and 1.'
                ''.format(self._className)
            )
        else:
            self._direction = direction

    def _trendCenter(self, x0, y0, azimuthAngle, simBoxXLength, simBoxYLength, origin_type=None, origin=None):
        if origin is None or origin_type is None:
            x_center, y_center = x0, y0
        elif origin_type == OriginType.RELATIVE:
            aA = azimuthAngle * math.pi / 180
            x_center = (
                x0
                + origin[0] * simBoxXLength * math.cos(aA)
                + origin[1] * simBoxYLength * math.sin(aA)
            )
            y_center = (
                y0
                - origin[0] * simBoxXLength * math.sin(aA)
                + origin[1] * simBoxYLength * math.cos(aA)
            )
        elif origin_type == OriginType.ABSOLUTE:
            x_center, y_center = origin[0], origin[1]
        else:
            raise ValueError(
                'Error: In {}\n'
                'Error: Origin type must be Relative or Absolute.'
                ''.format(self._className)
            )
        return x_center, y_center

    def createTrend(self, gridModel, realNumber, nDefinedCells, cellIndexDefined, zoneNumber, simBoxThickness):
        """
        Description: Create trend values for 3D grid zone using Roxar API.
        """
        import src.generalFunctionsUsingRoxAPI as gr
        # Check if specified grid model exists and is not empty
        if gridModel.is_empty():
            text = 'Error: Specified grid model: ' + gridModel.name + ' is empty.'
            print(text)
            values = None
        else:
            grid3D = gridModel.get_grid(realNumber)
            gridIndexer = grid3D.simbox_indexer
            (nx, ny, nz) = gridIndexer.dimensions

            simBoxXLength, simBoxYLength, azimuthAngle, x0, y0 = gr.getGridSimBoxSize(grid3D, self._debug_level)

            xcenter, ycenter = self._trendCenter(x0, y0, azimuthAngle, simBoxXLength, simBoxYLength)

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
            if self._debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: In ' + self._className)
                print('Debug output:  Zone name: ' + zoneName)
                print('Debug output:  SimboxThickness: ' + str(simBoxThickness))
                print('Debug output:  Zinc: ' + str(zinc))
                print('Debug output:  nx, ny, nz: ' + str(nx) + ', ' + str(ny) + ', ' + str(nz))
                print('Debug output:  Number of layers in zone: ' + str(nLayersInZone))

            # Create an empty array with 0 values with correct length
            # corresponding to all active cells in the grid
            # values = grid3D.generate_values(np.float32)
            valuesInSelectedCells = np.zeros(nDefinedCells, np.float32)

            # Calculate the 3D trend values
            alpha, theta = self._AlphaTheta()
            # TODO: Kari - make functions

            trendValueInputParams = self._trendValueInputParams()
            # TODO: Kari - make functions

            kCenter = (cellIndices.max(axis=0)[2] - cellIndices.min(axis=0)[2]) / 2

            for indx in range(nDefinedCells):
                x = cellCenterPoints[indx, 0]
                y = cellCenterPoints[indx, 1]
                z = cellCenterPoints[indx, 2]

                i = cellIndices[indx, 0]
                j = cellIndices[indx, 1]
                k = cellIndices[indx, 2]

                # Coordinates relative to a local origo (xmin,ymin) for x,y
                # The depth coordinate zSimBox is relative to simulation box
                xRel = x - xcenter
                yRel = y - ycenter
                zSimBox = (k - kCenter + 0.5) * zinc

                trendValue = self._trendValue(*trendValueInputParams)
                # TODO: Kari - make functions

                valuesInSelectedCells[indx] = trendValue
            minValue = valuesInSelectedCells.min()
            maxValue = valuesInSelectedCells.max()
            minmaxDifference = maxValue - minValue
            valuesRescaled = (valuesInSelectedCells - minValue) / minmaxDifference

            minValue = valuesRescaled.min()
            maxValue = valuesRescaled.max()
            minmaxDifference = maxValue - minValue
        return minmaxDifference, valuesRescaled

    def get_origin_type_from_model_file(self, model_file_name, trendRuleXML):
        origin_type = getTextCommand(
            trendRuleXML, 'origintype', modelFile=model_file_name, required=False, defaultText="Relative"
        )
        origin_type = origin_type.strip('\"\'')
        if origin_type.lower() == 'relative':
            return OriginType.RELATIVE
        elif origin_type.lower() == 'absolute':
            return OriginType.ABSOLUTE
        else:
            raise ValueError(
                'Error: In {}\n'
                'Error: Origin type must be Relative or Absolute.'
                ''.format(self._className)
            )


class Trend3D_linear(Trend3D):
    """
        Description: Create a linear trend 3D object
        Input is model parameters.
    """

    def __init__(self, trendRuleXML, modelFileName=None, debug_level=Debug.OFF):
        super().__init__(trendRuleXML, modelFileName, debug_level)
        self.type = 'Trend3D_linear'
        self._className = 'Trend3D_linear'

        if trendRuleXML is not None:
            self._interpretXMLTree(trendRuleXML, modelFileName, debug_level)
        else:
            if self._debug_level >= Debug.VERY_VERBOSE:
                print('Debug info: Create empty object of ' + self._className)

    def _interpretXMLTree(self, trendRuleXML, modelFileName, debug_level=Debug.OFF):
        super()._interpretXMLTree(trendRuleXML, modelFileName, debug_level)
        # Additional input parameters comes here (for other Trend3D-types)

    def XMLAddElement(self, parent):
        # Add to the parent element a new element with specified tag and attributes.
        # The attributes are a dictionary with {name:value}
        # After this function is called, the parent element has got a new child element
        # for the current class.
        if self._debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: call XMLADDElement from ' + self._className)

        attribute = {'name': 'Linear3D'}
        tag = 'Trend'
        trendElement = Element(tag, attribute)
        # Put the xml commands for this truncation rule as the last child for the parent element
        parent.append(trendElement)

        super()._XMLAddElementTag(trendElement)

        ## Additional tags dependent on trend type to be added here
        # tag = 'azimuth'
        # obj = Element(tag)
        # obj.text = ' ' + str(self._azimuth) + ' '
        # trendElement.append(obj)

    def initialize(self, azimuthAngle, stackingAngle, direction, debug_level=Debug.OFF):
        super().initialize(azimuthAngle, stackingAngle, direction, debug_level)
        # Add additional for current trend type here

    def _calcLinearTrendNormalVector(self, azimuthSimBox):
        """
            Calculate normal vector to iso-surfaces (planes) for constant trend values
            a*(x-x0)+b*(y-y0)+c*(z-z0) = K where K is a constant is such
            an iso surface and [a,b,c] is the normal vector to the plane.
        """
        # Calculate the 3D trend values

        alpha = (90.0 - self._stackingAngle) * np.pi / 180.0
        if self._direction == 1:
            theta = (self._azimuth - azimuthSimBox) * np.pi / 180.0
        else:
            theta = (self._azimuth - azimuthSimBox + 180.0) * np.pi / 180.0

        # Normal vector to a plane with constant trend value is [xComponent,yComponent,zComponent]
        xComponent = math.cos(alpha) * math.sin(theta)
        yComponent = math.cos(alpha) * math.cos(theta)
        zComponent = math.sin(alpha)
        return xComponent, yComponent, zComponent

    def createTrendFor2DProjection(
            self, simBoxXsize, simBoxYsize, simBoxZsize, azimuthSimBox,
            nxPreview, nyPreview, nzPreview, projectionType, crossSectionIndx
    ):

        xComponent, yComponent, zComponent = self._calcLinearTrendNormalVector(azimuthSimBox)
        xinc = simBoxXsize / nxPreview
        yinc = simBoxYsize / nyPreview
        zinc = simBoxZsize / nzPreview

        if projectionType == 'IJ':
            zRel = (crossSectionIndx + 0.5) * zinc
            values = np.zeros(nxPreview * nyPreview, float)
            for i in range(nxPreview):
                xRel = (i + 0.5) * xinc
                for j in range(nyPreview):
                    indx = i + j * nxPreview
                    yRel = (j + 0.5) * yinc
                    trendValue = xComponent * xRel + yComponent * yRel + zComponent * zRel
                    values[indx] = trendValue
        elif projectionType == 'IK':
            yRel = (crossSectionIndx + 0.5) * yinc
            values = np.zeros(nxPreview * nzPreview, float)
            for i in range(nxPreview):
                xRel = (i + 0.5) * xinc
                for k in range(nzPreview):
                    indx = i + k * nxPreview
                    zRel = (k + 0.5) * zinc
                    trendValue = xComponent * xRel + yComponent * yRel + zComponent * zRel
                    values[indx] = trendValue
        elif projectionType == 'JK':
            xRel = (crossSectionIndx + 0.5) * xinc
            values = np.zeros(nyPreview * nzPreview, float)
            for j in range(nyPreview):
                yRel = (j + 0.5) * yinc
                for k in range(nzPreview):
                    indx = j + k * nyPreview
                    zRel = (k + 0.5) * zinc
                    trendValue = xComponent * xRel + yComponent * yRel + zComponent * zRel
                    values[indx] = trendValue
        else:
            raise ValueError("Invalid projection type. Must be one of 'IJ', 'IK', 'JK'")

        v1 = 0.0
        v2 = xComponent * simBoxXsize
        v3 = yComponent * simBoxYsize
        v4 = xComponent * simBoxXsize + yComponent * simBoxYsize

        v5 = v1 + zComponent * simBoxZsize
        v6 = v2 + zComponent * simBoxZsize
        v7 = v3 + zComponent * simBoxZsize
        v8 = v4 + zComponent * simBoxZsize
        w = [v1, v2, v3, v4, v5, v6, v7, v8]
        minValue = min(w)
        maxValue = max(w)

        minmaxDifference = maxValue - minValue
        valuesRescaled = self._direction * values / minmaxDifference

        minValue = minValue / minmaxDifference
        maxValue = maxValue / minmaxDifference
        minmaxDifference = maxValue - minValue
        minValueInCrossSection = min(valuesRescaled)
        maxValueInCrossSection = max(valuesRescaled)
        if self._debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: Min value of trend within simBox: ' + str(minValue))
            print('Debug output: Max value of trend within simBox: ' + str(maxValue))
            print('Debug output: Difference between max and min value within simBox: ' + str(minmaxDifference))
            print('Debug output: Min value of trend within cross section: ' + str(minValueInCrossSection))
            print('Debug output: Max value of trend within cross section: ' + str(maxValueInCrossSection))

        return minmaxDifference, valuesRescaled

    def _trendCenter(
            self, x0, y0, azimuthAngle=None, simBoxXLength=None, simBoxYLength=None, origin_type=None, origin=None
    ):
        return x0, y0

    def _AlphaTheta(self):
        alpha = (90.0 - self._stackingAngle) * np.pi / 180.0
        if self._direction == 1:
            theta = self._azimuth * np.pi / 180.0
        else:
            theta = (self._azimuth + 180.0) * np.pi / 180.0
        return alpha, theta

    def createTrend(self, gridModel, realNumber, nDefinedCells, cellIndexDefined, zoneNumber, simBoxThickness):
        """
        Description: Create trend values for 3D grid zone using Roxar API.
        """
        import src.generalFunctionsUsingRoxAPI as gr
        # Check if specified grid model exists and is not empty
        if gridModel.is_empty():
            text = 'Error: Specified grid model: ' + gridModel.name + ' is empty.'
            print(text)
            values = None
        else:
            grid3D = gridModel.get_grid(realNumber)
            gridIndexer = grid3D.simbox_indexer
            (nx, ny, nz) = gridIndexer.dimensions

            simBoxXLength, simBoxYLength, azimuthAngle, x0, y0 = gr.getGridSimBoxSize(grid3D, self._debug_level)

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
            if self._debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: In ' + self._className)
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

            alpha = (90.0 - self._stackingAngle) * np.pi / 180.0
            if self._direction == 1:
                theta = self._azimuth * np.pi / 180.0
            else:
                theta = (self._azimuth + 180.0) * np.pi / 180.0

            # Normal vector to a plane with constant trend value is [xComponent,yComponent,zComponent]
            xComponent = math.cos(alpha) * math.sin(theta)
            yComponent = math.cos(alpha) * math.cos(theta)
            zComponent = math.sin(alpha)

            if self._debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: In ' + self._className)
                print('Debug output: normal vector: ({x}, {y}, {z})'.format(x=xComponent, y=yComponent, z=zComponent))

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
            valuesRescaled = self._direction * valuesInSelectedCells / minmaxDifference

            minValue = valuesRescaled.min()
            maxValue = valuesRescaled.max()
            minmaxDifference = maxValue - minValue
        return minmaxDifference, valuesRescaled


class Trend3D_elliptic(Trend3D):
    """
        Description: Create an elliptic trend 3D object
        Input is model parameters.
    """

    def __init__(self, trendRuleXML, modelFileName=None, debug_level=Debug.OFF):
        super().__init__(trendRuleXML, modelFileName, debug_level)
        self._curvature = 1.0
        self._origin = [0, 0]
        self._origin_type = OriginType.RELATIVE
        self.type = TrendType.ELLIPTIC
        self._className = self.__class__.__name__

        if trendRuleXML is not None:
            self._interpretXMLTree(trendRuleXML, modelFileName, debug_level)
        else:
            if self._debug_level >= Debug.VERY_VERBOSE:
                print('Debug info: Create empty object of ' + self._className)

    def _interpretXMLTree(self, trendRuleXML, modelFileName, debug_level=Debug.OFF):
        super()._interpretXMLTree(trendRuleXML, modelFileName, debug_level)
        # Additional input parameters comes here (for other Trend3D-types)
        self._curvature = getFloatCommand(trendRuleXML, 'curvature', modelFile=modelFileName, required=False,
                                          defaultValue=1)
        if self._curvature < 0.0:
            raise ValueError(
                'Error: In {}\n'
                'Error: Curvature for elliptic trend is below 0.'
                ''.format(self._className)
            )
        origin_x = getFloatCommand(trendRuleXML, 'origin_x', modelFile=modelFileName, required=False, defaultValue=0)
        origin_y = getFloatCommand(trendRuleXML, 'origin_y', modelFile=modelFileName, required=False, defaultValue=0)
        self._origin = [origin_x, origin_y]
        self._origin_type = self.get_origin_type_from_model_file(modelFileName, trendRuleXML)

    def XMLAddElement(self, parent):
        """
            Add to the parent element a new element with specified tag and attributes.
            The attributes are a dictionary with {name:value}
            After this function is called, the parent element has got a new child element
            for the current class.
        """
        if self._debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: call XMLADDElement from ' + self._className)

        attribute = {'name': 'Elliptic3D'}
        tag = 'Trend'
        trendElement = Element(tag, attribute)
        # Put the xml commands for this truncation rule as the last child for the parent element
        parent.append(trendElement)

        super()._XMLAddElementTag(trendElement)

        tag = 'curvature'
        obj = Element(tag)
        obj.text = ' ' + str(self._curvature) + ' '
        trendElement.append(obj)

    def initialize(
            self, azimuthAngle, stackingAngle, direction, curvature=1.0,
            origin=None, origin_type=OriginType.RELATIVE, debug_level=Debug.OFF
    ):
        super().initialize(azimuthAngle, stackingAngle, direction, debug_level)
        # Add additional for current trend type here
        if curvature < 0.0:
            raise ValueError(
                'Error: In {}\n'
                'Error: Cannot set curvature less than 0'
                ''.format(self._className)
            )
        if origin is None:
            origin = [0, 0]
        if not (isinstance(origin, list) or isinstance(origin, tuple)):
            raise ValueError(
                'Error: In {}\n'
                'Error: Origin must be of type array or tuple.'
                ''.format(self._className)
            )
        if not len(origin) == 3:
            raise ValueError(
                'Error: In {}\n'
                'Error: Origin must have length 3'
                ''.format(self._className)
            )
        for val in origin:
            if type(val) is int:
                val = float(val)
            if type(val) is not float:
                raise ValueError(
                    'Error: In {}\n'
                    'Error: Origin must contain float values'
                    ''.format(self._className)
                )
        if origin_type not in OriginType:
            raise ValueError(
                'Error: In {}\n'
                "Error: Origintype must be either 'Relative' or 'Absolute' "
                ''.format(self._className)
            )

        self._curvature = curvature
        self._origin = origin
        self._origin_type = origin_type

    def _trendCenter(self, x0, y0, azimuthAngle, simBoxXLength, simBoxYLength, origin_type=None, origin=None):
        return super()._trendCenter(x0, y0, azimuthAngle, simBoxXLength, simBoxYLength, self._origin_type, self._origin)

    def _AlphaTheta(self):
        alpha = self._direction * (90.0 - self._stackingAngle) * np.pi / 180.0
        theta = self._azimuth * np.pi / 180.0
        return alpha, theta

    def createTrend(self, gridModel, realNumber, nDefinedCells, cellIndexDefined, zoneNumber, simBoxThickness):
        """
        Description: Create trend values for 3D grid zone using Roxar API.
        """
        import src.generalFunctionsUsingRoxAPI as gr
        # Check if specified grid model exists and is not empty
        if gridModel.is_empty():
            text = 'Error: Specified grid model: ' + gridModel.name + ' is empty.'
            print(text)
            values = None
        else:
            grid3D = gridModel.get_grid(realNumber)
            gridIndexer = grid3D.simbox_indexer
            (nx, ny, nz) = gridIndexer.dimensions

            simBoxXLength, simBoxYLength, azimuthAngle, x0, y0 = gr.getGridSimBoxSize(grid3D, self._debug_level)

            xcenter, ycenter = self._trendCenter(x0, y0, azimuthAngle, simBoxXLength, simBoxYLength)

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
            if self._debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: In ' + self._className)
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
            alpha = self._direction * (90.0 - self._stackingAngle) * np.pi / 180.0
            theta = self._azimuth * np.pi / 180.0

            # Elliptic
            a = 1
            b = self._curvature
            xC = math.sin(theta)
            yC = math.cos(theta)
            u1 = np.array([xC, yC, 0])
            u2 = np.array([-yC, xC, 0])
            u3 = np.array([0, 0, 1])
            # Basis change matrix
            M = np.concatenate((u1, u2, u3))
            M = np.matrix(np.reshape(M, (3, 3)))

            for indx in range(nDefinedCells):
                x = cellCenterPoints[indx, 0]
                y = cellCenterPoints[indx, 1]
                z = cellCenterPoints[indx, 2]

                i = cellIndices[indx, 0]
                j = cellIndices[indx, 1]
                k = cellIndices[indx, 2]

                # Coordinates relative to a local origo (xmin, ymin) for x,y
                # The depth coordinate zSimBox is relative to simulation box
                xRel = x - xcenter
                yRel = y - ycenter
                zSimBox = (k + 0.5) * zinc

                # Elliptic
                xorg = np.array([xRel, yRel, zSimBox])
                X = np.array(M.dot(xorg))[0]
                trendValue = (
                    np.sqrt(np.square(X[0] / a) + np.square(X[1] / b)) * math.cos(alpha)
                    + X[2] * math.sin(alpha)
                )

                ## For spheroid
                ## Change basis to a coordinate system where z is the major axis of ellipse
                # xorg = np.array([xRel, yRel, zSimBox])
                # X = np.array(M.dot(xorg))[0]
                # trendValue = (np.square(X[0])+np.square(X[1]))/a+np.square(X[2])/b

                valuesInSelectedCells[indx] = trendValue
            minValue = valuesInSelectedCells.min()
            maxValue = valuesInSelectedCells.max()
            minmaxDifference = maxValue - minValue
            valuesRescaled = (valuesInSelectedCells - minValue) / minmaxDifference
            # valuesRescaled = self._direction * valuesInSelectedCells / minmaxDifference
            # valuesRescaled = valuesInSelectedCells / minmaxDifference

            minValue = valuesRescaled.min()
            maxValue = valuesRescaled.max()
            minmaxDifference = maxValue - minValue
        return minmaxDifference, valuesRescaled


class Trend3D_hyperbolic(Trend3D):
    """
        Description: Create a hyperbolic trend 3D object
        Input is model parameters.
    """
    def __init__(self, trendRuleXML, modelFileName=None, debug_level=Debug.OFF):
        super().__init__(trendRuleXML, modelFileName, debug_level)
        self._curvature = 1.0
        self._origin = [0, 0, 0]  # Center point of hyperbola
        self._origin_type = OriginType.RELATIVE
        self._migrationAngle = 0  # 0 for no migration
        self.type = TrendType.HYPERBOLIC
        self._className = self.__class__.__name__

        if trendRuleXML is not None:
            self._interpretXMLTree(trendRuleXML, modelFileName, debug_level)
        else:
            if self._debug_level >= Debug.VERY_VERBOSE:
                print('Debug info: Create empty object of ' + self._className)

    def _interpretXMLTree(self, trendRuleXML, modelFileName, debug_level=Debug.OFF):
        super()._interpretXMLTree(trendRuleXML, modelFileName, debug_level)
        # Additional input parameters comes here (for other Trend3D-types)
        self._curvature = getFloatCommand(
            trendRuleXML, 'curvature', modelFile=modelFileName, required=False, defaultValue=1
        )
        if self._curvature < 0.0:
            raise ValueError(
                'Error: In {}\n'
                'Error: Curvature for elliptic trend is below 0.'
                ''.format(self._className)
            )
        self._migrationAngle = getFloatCommand(
            trendRuleXML, 'migrationAngle', modelFile=modelFileName, required=False, defaultValue=0
        )
        origin_x = getFloatCommand(trendRuleXML, 'origin_x', modelFile=modelFileName, required=False, defaultValue=0)
        origin_y = getFloatCommand(trendRuleXML, 'origin_y', modelFile=modelFileName, required=False, defaultValue=0)
        self._origin = [origin_x, origin_y]
        self._origin_type = self.get_origin_type_from_model_file(modelFileName, trendRuleXML)

    def _trendCenter(self, x0, y0, azimuthAngle, simBoxXLength, simBoxYLength, origin_type=None, origin=None):
        return super()._trendCenter(x0, y0, azimuthAngle, simBoxXLength, simBoxYLength, self._origin_type, self._origin)

    def _AlphaTheta(self):
        alpha = self._direction * (90.0 - self._stackingAngle) * np.pi / 180.0
        theta = self._azimuth * np.pi / 180.0
        return alpha, theta

    def createTrend(self, gridModel, realNumber, nDefinedCells, cellIndexDefined, zoneNumber, simBoxThickness):
        """
        Description: Create trend values for 3D grid zone using Roxar API.
        """
        import src.generalFunctionsUsingRoxAPI as gr
        importlib.reload(gr)
        # Check if specified grid model exists and is not empty
        if gridModel.is_empty():
            text = 'Error: Specified grid model: ' + gridModel.name + ' is empty.'
            print(text)
            values = None
        else:
            grid3D = gridModel.get_grid(realNumber)
            gridIndexer = grid3D.simbox_indexer
            (nx, ny, nz) = gridIndexer.dimensions

            simBoxXLength, simBoxYLength, azimuthAngle, x0, y0 = gr.getGridSimBoxSize(grid3D, self._debug_level)

            xcenter, ycenter = self._trendCenter(x0, y0, azimuthAngle, simBoxXLength, simBoxYLength)

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
            if self._debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: In ' + self._className)
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
            alpha = self._direction * (90.0 - self._stackingAngle) * np.pi / 180.0
            theta = self._azimuth * np.pi / 180.0

            # Hyperbolic
            b = 1
            a = self._curvature
            xC = math.sin(theta) * math.cos(alpha)
            yC = math.cos(theta) * math.cos(alpha)
            zC = math.sin(alpha)
            # Basis change matrix
            u2 = np.array([xC, yC, zC])  # Unit vector along hyperbola major axis
            u1 = np.array([yC, -xC, 0])  # Unit vector perpendicular to u1, in the x-y-plane
            u3 = np.cross(u1, u2)  # Unit vector perpendicular to u1, u2
            M = np.concatenate((u1, u2, u3))
            M = np.matrix(np.reshape(M, (3, 3)))

            imax, jmax, kmax = cellCenterPoints.argmax(axis=0)
            imin, jmin, kmin = cellCenterPoints.argmin(axis=0)

            xmaxRel = cellCenterPoints[imax, :] - np.array([xcenter, ycenter, 0])
            xmax = np.array(M.dot(xmaxRel))[0]
            xminRel = cellCenterPoints[imin, :] - np.array([xcenter, ycenter, 0])
            xmin = np.array(M.dot(xminRel))[0]

            ymaxRel = cellCenterPoints[jmax, :] - np.array([xcenter, ycenter, 0])
            ymax = np.array(M.dot(ymaxRel))[0]
            yminRel = cellCenterPoints[jmin, :] - np.array([xcenter, ycenter, 0])
            ymin = np.array(M.dot(yminRel))[0]

            xinc = max(abs(xmin[0]), abs(xmax[0]))
            yinc = max(abs(ymin[1]), abs(ymax[1]))
            a = xinc
            b = yinc / np.sqrt(np.square(self._curvature) - 1)
            kCenter = (cellIndices.max(axis=0)[2] - cellIndices.min(axis=0)[2]) / 2

            for indx in range(nDefinedCells):
                x = cellCenterPoints[indx, 0]
                y = cellCenterPoints[indx, 1]
                z = cellCenterPoints[indx, 2]

                i = cellIndices[indx, 0]
                j = cellIndices[indx, 1]
                k = cellIndices[indx, 2]

                # Coordinates relative to a local origo (xmin,ymin) for x,y
                # The depth coordinate zSimBox is relative to simulation box
                xRel = x - xcenter
                yRel = y - ycenter
                zSimBox = (k - kCenter + 0.5) * zinc

                # Hyperbolic

                xorg = np.array([xRel, yRel, zSimBox])
                X = np.array(M.dot(xorg))[0]

                dX = -zSimBox / math.sin(alpha) * math.tan(self._migrationAngle * math.pi / 180)
                xp = X[0] - dX

                # Stretch
                if dX * xp > 0:
                    zeroPoint = a * np.sqrt(1 + np.square(X[1] / b)) - dX
                else:
                    zeroPoint = a * np.sqrt(1 + np.square(X[1] / b)) + dX

                ## Move - use either move or stretch
                # zeroPoint=(a-dX)*np.sqrt(1+np.square(X[1]/b))

                trendValue = 1 - abs(xp) / zeroPoint

                valuesInSelectedCells[indx] = trendValue
            minValue = valuesInSelectedCells.min()
            maxValue = valuesInSelectedCells.max()
            minmaxDifference = maxValue - minValue
            valuesRescaled = (valuesInSelectedCells - minValue) / minmaxDifference

            minValue = valuesRescaled.min()
            maxValue = valuesRescaled.max()
            minmaxDifference = maxValue - minValue
        return minmaxDifference, valuesRescaled
