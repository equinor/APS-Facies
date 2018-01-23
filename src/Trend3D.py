#!/bin/env python
# Copyright 2017 Statoil ASA
#
# Class for Trends used in APS modelling
# Subclass for each trend type
#  - linear
#  - elliptic
#  - hyperbolic
#  - RMSParameter
#
####################################################################
# Kari B. Skjerve, karbor@statoil.com
# Oddvar Lia 
# 2017/2018
####################################################################

import math
import copy
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
    The following functions must be specified for the sub classes:
    _calcParam(self)
    _writeTrendSpecificParam(self)
    _trendValueCalculation(self, parametersForTrendCalc, x, y, k, zinc)
    """
    def __init__(self, trendRuleXML, modelFileName=None, debug_level=Debug.OFF):
        """
        Initialize common parameters for all methods implemented in sub classes.
        These parameters will be defined in sub classes

        """
        # Depositional direction
        self._azimuth = 0.0

        # Angle between facies
        self._stackingAngle = 0.0001

        # Direction of stacking (prograding/retrograding)
        self._direction = 1

        self._debug_level = debug_level
        self.type = TrendType.NONE

        # Position of a reference point for the trend function. 
        # This is in global coordinates for (x,y) and relative to simulation box for the zone for z coordinate.
        self._xCenter = 0.0
        self._yCenter = 0.0
        self._zCenter = 0.0
        self._xSimBox = 0.0
        self._ySimBox = 0.0
        self._zSimBox = 0.0
        self._startLayer = -1
        self._endLayer = -1

        self._className = self.__class__.__name__

    def _interpretXMLTree(self, trendRuleXML, modelFileName):
        """
        Read common parameters from xml tree for all trend types
        """
        self._azimuth = getFloatCommand(trendRuleXML, 'azimuth', modelFile=modelFileName)
        if not 0.0 <= self._azimuth <= 360.0:
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
        if self._debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: Trend parameters:')
            print('Debug output:   Azimuth:        ' + str(self._azimuth))
            print('Debug output:   Stacking angle: ' + str(self._stackingAngle))
            print('Debug output:   Stacking type:  ' + str(self._direction))

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

    def initialize(self, azimuthAngle=0.0, stackingAngle=0.01, direction=1, debug_level=Debug.OFF):
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

    def _setTrendCenter(self, x0, y0, azimuthAngle, simBoxXLength, simBoxYLength, simBoxThickness, 
                        origin_type=None, origin=None):
        if origin is None or origin_type is None:
            x_center, y_center = x0, y0
            z_center = 0.0 # Top of zone
        elif origin_type == OriginType.RELATIVE:
            aA = azimuthAngle * math.pi / 180.0
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
            z_center = origin[2] * simBoxThickness
        elif origin_type == OriginType.ABSOLUTE:
            x_center, y_center = origin[0], origin[1]
            z_center = origin[2] * simBoxThickness
        else:
            raise ValueError(
                'In {}\n'
                'Origin type must be either {} or {}.'
                ''.format(self._className, str(OriginType.RELATIVE.name), str(OriginType.ABSOLUTE.name))
                )
        self._xCenter = x_center
        self._yCenter = y_center
        self._zCenter = z_center
        self._xSimBox = simBoxXLength
        self._ySimBox = simBoxYLength
        self._zSimBox = simBoxThickness
        

    def _calculateTrendModelParam(self):
        raise NotImplementedError('Can not use: {} object as a trend object. Use sub classes of this as trend'
                         ''.format(self.__className))

    def _writeTrendSpecificParam(self):
        raise NotImplementedError('Can not use: {} object as a trend object. Use sub classes of this as trend'
                         ''.format(self.__className))

    def _trendValueCalculation(self, parametersForTrendCalc, x, y, k, zinc):
        raise NotImplementedError('Can not use: {} object as a trend object. Use sub classes of this as trend'
                         ''.format(self.__className))

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
            # Define self._xCenter, self._yCenter for the trend
            self._setTrendCenter(x0, y0, azimuthAngle, simBoxXLength, simBoxYLength, simBoxThickness)

            cellCenterPoints = grid3D.get_cell_centers(cellIndexDefined)
            cellIndices = gridIndexer.get_indices(cellIndexDefined)

            zoneName = grid3D.zone_names[zoneNumber - 1]
            zonation = gridIndexer.zonation
            layerRanges = zonation[zoneNumber - 1]
            n = 0
            startLayer = 99999999
            endLayer = -1
            for layer in layerRanges:
                if startLayer > layer[0]:
                    startLayer = layer[0]
                if endLayer < layer[-1]:
                    endLayer = layer[-1]

                for k in layer:
                    n += 1
            nLayersInZone = n

            # Set start and end layer for this zone
            self._startLayer = startLayer
            self._endLayer = endLayer
            zinc = simBoxThickness / nLayersInZone
            if self._debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: In ' + self._className)
                print('Debug output:  Zone name: ' + zoneName)
                print('Debug output:  SimboxThickness: ' + str(simBoxThickness))
                print('Debug output:  Zinc: ' + str(zinc))
                print('Debug output:  nx,ny,nz: ' + str(nx) + ' ' + str(ny) + ' ' + str(nz))
                print('Debug output:  Number of layers in zone: ' + str(nLayersInZone))
                print('Debug output:  Start layer in zone: ' + str(startLayer+1))
                print('Debug output:  End layer in zone: ' + str(endLayer+1))
                print('Debug output:  Trend type: {}'.format(self.type.name))
                if self.type != TrendType.RMS_PARAM:
                    print('Debug output:  Trend azimuth: {}'.format(self._azimuth))
                    print('Debug output:  StackingAngle: {}'.format(self._stackingAngle)) 
                    print('Debug output:  Direction: {}'.format(str(self._direction)))
                    print('Debug output:  x_center: {}'.format(str(self._xCenter)))
                    print('Debug output:  y_center: {}'.format(str(self._yCenter)))
                    print('Debug output:  z_center (sim box): {}'.format(str(self._zCenter)))
                self._writeTrendSpecificParam()

                # Create an empty array with 0 values with correct length
                # corresponding to all active cells in the grid

            if self.type == TrendType.RMS_PARAM:
                print(self.type)
                # Values for all active cells
                valuesInActiveCells = gr.getContinuous3DParameterValues(gridModel, self._rmsParamName, 
                                                                        realNumber, debug_level=self._debug_level)
                # Values for selected cells (using numpy vectors)
                valuesInSelectedCells = valuesInActiveCells[cellIndexDefined]

            else:
                valuesInSelectedCells = np.zeros(nDefinedCells, np.float32)
                parametersForTrendCalc = self._calculateTrendModelParam()
                for indx in range(nDefinedCells):
                    x = cellCenterPoints[indx, 0]
                    y = cellCenterPoints[indx, 1]
                    z = cellCenterPoints[indx, 2]
                    
                    i = cellIndices[indx, 0]
                    j = cellIndices[indx, 1]
                    k = cellIndices[indx, 2]
                    
                    trendValue =self._trendValueCalculation(parametersForTrendCalc, x, y, k, zinc)
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

# ----------------------------------------------------------------------------------------------------------

class Trend3D_linear(Trend3D):
    """
        Description: Create a linear trend 3D object
        Input is model parameters.
    """

    def __init__(self, trendRuleXML, modelFileName=None, debug_level=Debug.OFF):
        super().__init__(trendRuleXML, modelFileName, debug_level)
        self.type = TrendType.LINEAR
        self._className = self.__class__.__name__

        if trendRuleXML is not None:
            if self._debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: Trend type: {}'.format(self.type))
            self._interpretXMLTree(trendRuleXML, modelFileName)
        else:
            if self._debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: Create empty object of ' + self._className)

    def _interpretXMLTree(self, trendRuleXML, modelFileName):
        super()._interpretXMLTree(trendRuleXML, modelFileName)
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
        parent.append(trendElement)

        super()._XMLAddElementTag(trendElement)

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

    def _setTrendCenter(self, x0, y0, azimuthAngle, simBoxXLength, simBoxYLength, simBoxThickness, origin_type=None, origin=None):
        self._xCenter = x0
        self._yCenter = y0
        self._zCenter = 0.0

    def _AlphaTheta(self):
        alpha = (90.0 - self._stackingAngle) * np.pi / 180.0
        if self._direction == 1:
            theta = self._azimuth * np.pi / 180.0
        else:
            theta = (self._azimuth + 180.0) * np.pi / 180.0
        return alpha, theta

    def _calculateTrendModelParam(self):
        # Calculate the 3D linear trend parameters
        alpha, theta = self._AlphaTheta()

        # Normal vector to a plane with constant trend value is [xComponent,yComponent,zComponent]
        if abs(self._stackingAngle) < 0.0000001:
            xComponent = 0.0
            yComponent = 0.0
            zComponent = 1.0
        else:
            xComponent = math.cos(alpha) * math.sin(theta)
            yComponent = math.cos(alpha) * math.cos(theta)
            zComponent = math.sin(alpha)
        parameterForTrendCalculation = [xComponent, yComponent, zComponent]
        return parameterForTrendCalculation

    def _writeTrendSpecificParam(self):
        print('')

    def _trendValueCalculation(self, parametersForTrendCalc,x, y, k, zinc):
        xComponent =  parametersForTrendCalc[0]
        yComponent =  parametersForTrendCalc[1]
        zComponent =  parametersForTrendCalc[2]

        # Transform the point(0,0,zRel) into a point (x_center, y_center, zRel)
        zRel = (k - self._startLayer + 0.5) * zinc - self._zCenter 
        xRel = x - self._xCenter
        yRel = y - self._yCenter
        trendValue = xComponent * xRel + yComponent * yRel + zComponent * zRel
        return trendValue

# ----------------------------------------------------------------------------------------------------------

class Trend3D_elliptic(Trend3D):
    """
        Description: Create an elliptic trend 3D object
        Input is model parameters.
    """

    def __init__(self, trendRuleXML, modelFileName=None, debug_level=Debug.OFF):
        super().__init__(trendRuleXML, modelFileName, debug_level)
        self._curvature = 1.0
        self._origin = [0.0, 0.0, 0.0]
        self._origin_type = OriginType.RELATIVE
        self.type = TrendType.ELLIPTIC
        self._className = self.__class__.__name__

        if trendRuleXML is not None:
            if self._debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: Trend type: {}'.format(self.type))
            self._interpretXMLTree(trendRuleXML, modelFileName)
        else:
            if self._debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: Create empty object of ' + self._className)

    def _interpretXMLTree(self, trendRuleXML, modelFileName):
        super()._interpretXMLTree(trendRuleXML, modelFileName)
        # Stacking angle must be > 0.
        if abs(self._stackingAngle) < 0.00001:
            self._stackingAngle = 0.00001

        # Additional input parameters comes here (for other Trend3D-types)
        self._curvature = getFloatCommand(trendRuleXML, 'curvature', modelFile=modelFileName, required=False,
                                          defaultValue=1)
        if self._curvature <= 0.0:
            raise ValueError(
                'Error: In {}\n'
                'Error: Curvature for elliptic trend is not positive.'
                ''.format(self._className)
            )
        origin_x = getFloatCommand(trendRuleXML, 'origin_x', modelFile=modelFileName, required=False, defaultValue=0.0)
        origin_y = getFloatCommand(trendRuleXML, 'origin_y', modelFile=modelFileName, required=False, defaultValue=0.0)
        origin_z = getFloatCommand(trendRuleXML, 'origin_z_simbox', modelFile=modelFileName, required=False, defaultValue=0.0)
        self._origin = [origin_x, origin_y, origin_z]
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
        parent.append(trendElement)

        super()._XMLAddElementTag(trendElement)

        tag = 'curvature'
        obj = Element(tag)
        obj.text = ' ' + str(self._curvature) + ' '
        trendElement.append(obj)

        tag = 'origin_x'
        obj = Element(tag)
        obj.text = ' ' + str(self._origin[0]) + ' '
        trendElement.append(obj)

        tag = 'origin_y'
        obj = Element(tag)
        obj.text = ' ' + str(self._origin[1]) + ' '
        trendElement.append(obj)

        tag = 'origin_z_simbox'
        obj = Element(tag)
        obj.text = ' ' + str(self._origin[2]) + ' '
        trendElement.append(obj)

        tag = 'origintype'
        obj = Element(tag)
        if self._origin_type == OriginType.RELATIVE:
            obj.text = ' Relative '
        elif self._origin_type == OriginType.ABSOLUTE:
            obj.text = ' Absolute '
        trendElement.append(obj)



    def initialize(
            self, azimuthAngle, stackingAngle, direction, curvature=1.0,
            origin=None, origin_type=OriginType.RELATIVE, debug_level=Debug.OFF
    ):
        super().initialize(azimuthAngle, stackingAngle, direction, debug_level)
        # Add additional for current trend type here
        if curvature <= 0.0:
            raise ValueError(
                'Error: In {}\n'
                'Error: Cannot set curvature less than or equal to 0'
                ''.format(self._className)
            )
        if origin is None:
            origin = [0.0, 0.0, 0.0]
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

    def setCurvature(self, curvature):
        if curvature <= 0.0:
            raise ValueError(
                'Error: In {}\n'
                'Error: Curvature for elliptic trend is not positive.'
                ''.format(self._className)
                )
        self._curvature = curvature

    def setOrigin(self, origin):
        self._origin = origin

    def setOriginType(self, originType):
        if originType not in OriginType:
            raise ValueError(
                'Error: In {}\n'
                "Error: Origintype must be either 'Relative' or 'Absolute' "
                ''.format(self._className)
            )
        self._origin_type = originType

    def getCurvature(self):
        return self._curvature

    def getOrigin(self):
        return self._origin

    def getOriginType(self):
        return self._origin_type


    def _setTrendCenter(self, x0, y0, azimuthAngle, simBoxXLength, simBoxYLength, simBoxThickness, origin_type=None, origin=None):
        super()._setTrendCenter(x0, y0, azimuthAngle, simBoxXLength, simBoxYLength,simBoxThickness, 
                                self._origin_type, self._origin)

    def _trendValueCalculation(self, parametersForTrendCalc, x, y, k, zinc):
        # Elliptic
        sinTheta = parametersForTrendCalc[0]
        cosTheta = parametersForTrendCalc[1]
        tanAlpha = parametersForTrendCalc[2]
        a = parametersForTrendCalc[3]
        b = parametersForTrendCalc[4]

        # Transform the point(0,0,zRel) into a point (x_center, y_center, zRel)
        zRel = (k - self._startLayer + 0.5) * zinc - self._zCenter
        if zRel != 0.0:
            L = zRel * tanAlpha
            x_center = -L * sinTheta + self._xCenter
            y_center = -L * cosTheta + self._yCenter
        else:
            x_center = self._xCenter
            y_center = self._yCenter

        xRel = x - x_center
        yRel = y - y_center
        xRotated = xRel * cosTheta - yRel * sinTheta
        yRotated = xRel * sinTheta + yRel * cosTheta
        value = np.sqrt(np.square(xRotated / a) + np.square(yRotated / b))
        return value

    def _calculateTrendModelParam(self):
        # Calculate the 3D trend values for Elliptic
        alpha = self._direction * (90.0 - self._stackingAngle) * np.pi / 180.0
        theta = self._azimuth * np.pi / 180.0

        # Elliptic
        a = 1
        b = self._curvature
        sinTheta = math.sin(theta)
        cosTheta = math.cos(theta)
        tanAlpha = math.tan(alpha)
        parametersForTrendCalc = [sinTheta, cosTheta, tanAlpha, a, b]
        return parametersForTrendCalc


    def _writeTrendSpecificParam(self):
        # Elliptic
        print('Debug output:  Curvature: {}'.format(str(self._curvature)))
        print('Debug output:  Origin: ({},{}, {})'.format(str(self._origin[0]), str(self._origin[1]), str(self._origin[2])))
        print('Debug output:  Origin type: {}'.format(self._origin_type.name))


    def createTrendFor2DProjection(
            self, simBoxXsize, simBoxYsize, simBoxZsize, azimuthSimBox,
            nxPreview, nyPreview, nzPreview, projectionType, crossSectionIndx
    ):

        xinc = simBoxXsize / nxPreview
        yinc = simBoxYsize / nyPreview
        zinc = simBoxZsize / nzPreview

        parametersForTrendCalc = self._calculateTrendModelParam() 

        if projectionType == 'IJ':
            zRel = (crossSectionIndx + 0.5) * zinc
            values = np.zeros(nxPreview * nyPreview, float)
            for i in range(nxPreview):
                ii = i-nxPreview
                xRel = (ii + 0.5) * xinc
                for j in range(nyPreview):
                    indx = i + j * nxPreview
                    jj = j-nyPreview
                    yRel = (jj + 0.5) * yinc
                    # Elliptic
                    trendValue = self._trendValueCalculation(parametersForTrendCalc,xRel, yRel, zRel)
                    values[indx] = trendValue
        elif projectionType == 'IK':
            yRel = (crossSectionIndx + 0.5) * yinc
            values = np.zeros(nxPreview * nzPreview, float)
            for i in range(nxPreview):
                ii = i-nxPreview
                xRel = (ii + 0.5) * xinc
                for k in range(nzPreview):
                    indx = i + k * nxPreview
                    kk = k-nzPreview
                    zRel = (kk + 0.5) * zinc
                    trendValue = self._trendValueCalculation(parametersForTrendCalc,xRel, yRel, zRel)
                    values[indx] = trendValue
        elif projectionType == 'JK':
            xRel = (crossSectionIndx + 0.5) * xinc
            values = np.zeros(nyPreview * nzPreview, float)
            for j in range(nyPreview):
                jj = j-nxPreview
                yRel = (jj + 0.5) * yinc
                for k in range(nzPreview):
                    indx = j + k * nyPreview
                    kk = k-nzPreview
                    zRel = (kk + 0.5) * zinc
                    trendValue = self._trendValueCalculation(parametersForTrendCalc,xRel, yRel, zRel)
                    values[indx] = trendValue
        else:
            raise ValueError("Invalid projection type. Must be one of 'IJ', 'IK', 'JK'")
        minValue = values.min()
        maxValue = values.max()

        minmaxDifference = maxValue - minValue
        valuesRescaled = (values - minValue) / minmaxDifference

        minValue = valuesRescaled.min()
        maxValue = valuesRescaled.max()
        minmaxDifference = maxValue - minValue
        minValueInCrossSection = minValue
        maxValueInCrossSection = maxValue
        if self._debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: Min value of trend within cross section: ' + str(minValueInCrossSection))
            print('Debug output: Max value of trend within cross section: ' + str(maxValueInCrossSection))

        return minmaxDifference, valuesRescaled

# ----------------------------------------------------------------------------------------------------------

class Trend3D_hyperbolic(Trend3D):
    """
        Description: Create a hyperbolic trend 3D object
        Input is model parameters.
    """
    def __init__(self, trendRuleXML, modelFileName=None, debug_level=Debug.OFF):
        super().__init__(trendRuleXML, modelFileName, debug_level)
        self._curvature = 1.1
        self._origin = [0.0, 0.0, 0.0]
        self._origin_type = OriginType.RELATIVE
        self._migrationAngle = 0  # 0 for no migration
        self.type = TrendType.HYPERBOLIC
        self._className = self.__class__.__name__

        if trendRuleXML is not None:
            if self._debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: Trend type: {}'.format(self.type))
            self._interpretXMLTree(trendRuleXML, modelFileName)
        else:
            if self._debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: Create empty object of ' + self._className)

    def _interpretXMLTree(self, trendRuleXML, modelFileName):
        super()._interpretXMLTree(trendRuleXML, modelFileName)
        # Additional input parameters comes here (for other Trend3D-types)
        self._curvature = getFloatCommand(
            trendRuleXML, 'curvature', modelFile=modelFileName, required=False, defaultValue=1
        )
        if self._curvature <= 1.0:
            raise ValueError(
                'Error: In {}\n'
                'Error: Curvature for hyperbolic trend is not greater than 1.0'
                ''.format(self._className)
            )
        self._migrationAngle = getFloatCommand(
            trendRuleXML, 'migrationAngle', modelFile=modelFileName, required=False, defaultValue=0
        )
        if self._migrationAngle <= -90.0 or self._migrationAngle >= 90.0:
            raise ValueError(
                'Error: In {}\n'
                'Error: Migration angle must be between -90.0 and +90.0 degrees.'
                ''.format(self._className)
                )

        origin_x = getFloatCommand(trendRuleXML, 'origin_x', modelFile=modelFileName, required=False, defaultValue=0.0)
        origin_y = getFloatCommand(trendRuleXML, 'origin_y', modelFile=modelFileName, required=False, defaultValue=0.0)
        origin_z = getFloatCommand(trendRuleXML, 'origin_z_simbox', modelFile=modelFileName, required=False, defaultValue=0.0)
        self._origin = [origin_x, origin_y, origin_z]
        self._origin_type = self.get_origin_type_from_model_file(modelFileName, trendRuleXML)

    def setCurvature(self, curvature):
        if curvature <= 0.0:
            raise ValueError(
                'Error: In {}\n'
                'Error: Curvature for elliptic trend is not positive.'
                ''.format(self._className)
                )
        self._curvature = curvature

    def setMigrationAngle(self, migrationAngle):
        if migrationAngle <= -90.0 or migrationAngle >= 90.0:
            raise ValueError(
                'Error: In {}\n'
                'Error: Migration angle must be between -90.0 and +90.0 degrees.'
                ''.format(self._className)
                )
        self._migrationAngle = migrationAngle

    def setOrigin(self, origin):
        self._origin = origin

    def setOriginType(self, originType):
        if originType not in OriginType:
            raise ValueError(
                'Error: In {}\n'
                "Error: Origintype must be either 'Relative' or 'Absolute' "
                ''.format(self._className)
            )
        self._origin_type = originType

    def getCurvature(self):
        return self._curvature

    def getMigrationAngle(self):
        return self._migrationAngle

    def getOrigin(self):
        return self._origin

    def getOriginType(self):
        return self._origin_type


    def initialize( 
            self, azimuthAngle, stackingAngle, direction, migrationAngle, curvature,
            origin=None, origin_type=OriginType.RELATIVE, debug_level=Debug.OFF
    ):
        super().initialize(azimuthAngle, stackingAngle, direction, debug_level)
        # Add additional for current trend type here
        if curvature <= 1.0:
            raise ValueError(
                'Error: In {}\n'
                'Error: Cannot set curvature less than or equal to 1'
                ''.format(self._className)
            )
        if migrationAngle <= -90.0 or migrationAngle >= 90.0:
            raise ValueError(
                'Error: In {}\n'
                'Error: Migration angle must be between -90.0 and +90.0 degrees.'
                ''.format(self._className)
                )
        if origin is None:
            origin = [0.0, 0.0, 0.0]
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
        self._migrationAngle = migrationAngle
        self._origin = origin
        self._origin_type = origin_type


    def _setTrendCenter(self, x0, y0, azimuthAngle, simBoxXLength, simBoxYLength, simBoxThickness, origin_type=None, origin=None):
        super()._setTrendCenter(x0, y0, azimuthAngle, simBoxXLength, simBoxYLength, simBoxThickness,
                                self._origin_type, self._origin)

    def _trendValueCalculation(self, parametersForTrendCalc, x, y, k, zinc):
        # Hyperbolic
        sinTheta = parametersForTrendCalc[0]
        cosTheta = parametersForTrendCalc[1]
        tanAlpha = parametersForTrendCalc[2]
        tanBeta = parametersForTrendCalc[3]
        a = parametersForTrendCalc[4]
        b = parametersForTrendCalc[5]

        zRel = (k -self._startLayer + 0.5) * zinc - self._zCenter

        # The center point is changed by depth. There are two angles that can specify this
        # The angle alpha (which is 90 -stacking angle) will shift the center point along azimuth direction.
        # The angle beta (migration angle) will shift the center point orthogonal to azimuth direction.
        # First shift the center point in azimuth direction
        L = -zRel * tanAlpha
        x_center = L * sinTheta + self._xCenter
        y_center = L * cosTheta + self._yCenter

        # Secondly, shift the center point further, but now orthogonal to azimuth direction.
        L = -zRel * tanBeta
        x_center = L * cosTheta + x_center
        y_center = -L * sinTheta + y_center

        xRel = x - x_center
        yRel = y - y_center
        xRotatedByTheta = xRel * cosTheta - yRel * sinTheta
        yRotatedByTheta = xRel * sinTheta + yRel * cosTheta

        if xRotatedByTheta > 0:
            zeroPoint = a * np.sqrt(1 + np.square(yRotatedByTheta / b))
        else:
            zeroPoint = -a * np.sqrt(1 + np.square(yRotatedByTheta / b))

        trendValue = (1.0  - abs(xRotatedByTheta / zeroPoint)) 
        return trendValue

    def _calculateTrendModelParam(self):
        # Calculate the 3D trend values
        assert self._curvature > 1.0
        assert abs(self._migrationAngle) < 90.0
        assert abs(self._stackingAngle) > 0.0

        theta = self._azimuth * np.pi / 180.0
        beta  = self._migrationAngle * np.pi / 180.0
        alpha = self._direction * (90.0 - self._stackingAngle) * np.pi / 180.0

        # Hyperbolic
        sinTheta = math.sin(theta)
        cosTheta = math.cos(theta)
        tanBeta  = math.tan(beta)
        tanAlpha = math.tan(alpha)

        a = self._xSimBox
        b = self._ySimBox / np.sqrt(np.square(self._curvature) - 1.0)

        parametersForTrendCalc = [sinTheta, cosTheta, tanAlpha, tanBeta, a, b]

        if self._debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: Calculated parameters for Hyperbolic trend:')
            print('Debug output:   sinTheta = {}'.format(str(sinTheta)))
            print('Debug output:   cosTheta = {}'.format(str(cosTheta)))
            print('Debug output:   tanAlpha = {}'.format(str(tanAlpha)))
            print('Debug output:   tanBeta  = {}'.format(str(tanBeta)))
            print('Debug output:   a = {}'.format(str(a)))
            print('Debug output:   b = {}'.format(str(b)))
            print('')
        return  parametersForTrendCalc




    def _writeTrendSpecificParam(self):
        print('Debug output:  Curvature: {}'.format(str(self._curvature)))
        print('Debug output:  Origin: ({},{}, {})'.format(str(self._origin[0]), str(self._origin[1]), str(self._origin[2])))
        print('Debug output:  Origin type: {}'.format(self._origin_type.name))
        print('Debug output:  Migration angle: {}'.format(str(self._migrationAngle)))


    def XMLAddElement(self, parent):
        """
        Add to the parent element a new element with specified tag and attributes.
            The attributes are a dictionary with {name:value}
            After this function is called, the parent element has got a new child element
            for the current class.
        """
        if self._debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: call XMLADDElement from ' + self._className)

        attribute = {'name': 'Hyperbolic3D'}
        tag = 'Trend'
        trendElement = Element(tag, attribute)
        parent.append(trendElement)

        super()._XMLAddElementTag(trendElement)

        tag = 'curvature'
        obj = Element(tag)
        obj.text = ' ' + str(self._curvature) + ' '
        trendElement.append(obj)

        tag = 'migrationAngle'
        obj = Element(tag)
        obj.text = ' ' + str(self._migrationAngle) + ' '
        trendElement.append(obj)

        tag = 'origin_x'
        obj = Element(tag)
        obj.text = ' ' + str(self._origin[0]) + ' '
        trendElement.append(obj)

        tag = 'origin_y'
        obj = Element(tag)
        obj.text = ' ' + str(self._origin[1]) + ' '
        trendElement.append(obj)

        tag = 'origin_z_simbox'
        obj = Element(tag)
        obj.text = ' ' + str(self._origin[2]) + ' '
        trendElement.append(obj)

        tag = 'origintype'
        obj = Element(tag)
        if self._origin_type == OriginType.RELATIVE:
            obj.text = ' Relative '
        elif self._origin_type == OriginType.ABSOLUTE:
            obj.text = ' Absolute '
        trendElement.append(obj)

# ----------------------------------------------------------------------------------------------------------

class Trend3D_rms_param(Trend3D):
    """
        Description: Create a trend 3D object using a specified RMS 3D continuous parameter
        Input is model parameters.
    """
    def __init__(self, trendRuleXML, modelFileName=None, debug_level=Debug.OFF):
        self._rmsParamName =None
        self.type = TrendType.RMS_PARAM
        self._debug_level = debug_level
        self._className = self.__class__.__name__

        if trendRuleXML is not None:
            if self._debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: Trend type: {}'.format(self.type))
            self._interpretXMLTree(trendRuleXML, modelFileName)
        else:
            if self._debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: Create empty object of ' + self._className)

    def _interpretXMLTree(self, trendRuleXML, modelFileName):
        text = getTextCommand(trendRuleXML, 'TrendParamName', 'Trend', defaultText=None, modelFile=modelFileName, required=True)
        self._rmsParamName=copy.copy(text.strip())

    def initialize(self, rmsParamName, debug_level=Debug.OFF):
        self._rmsParamName=rmsParamName
        self._debug_level = debug_level

    def _writeTrendSpecificParam(self):
        print('Debug output:  RMS parameter name for trend values: {}'.format(str(self._rmsParamName)))

    def getTrendParamName(self):
        return self._rmsParamName

    def setTrendParamName(self, paramName):
        self._rmsParamName = paramName

    def XMLAddElement(self, parent):
        """
        Add to the parent element a new element with specified tag and attributes.
            The attributes are a dictionary with {name:value}
            After this function is called, the parent element has got a new child element
            for the current class.
        """
        if self._debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: call XMLADDElement from ' + self._className)

        attribute = {'name': 'RMSParameter'}
        tag = 'Trend'
        trendElement = Element(tag, attribute)
        parent.append(trendElement)

        tag = 'TrendParamName'
        obj = Element(tag)
        obj.text = ' ' + self._rmsParamName + ' '
        trendElement.append(obj)

