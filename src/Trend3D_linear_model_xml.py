#!/bin/env python
# Python 3 Calculate linear trend in 3D in RMS10 using roxapi

import math
import numpy as np
import importlib
from xml.etree.ElementTree import Element

import src.utils.xml

importlib.reload(src.utils.xml)

from src.utils.constants.simple import Debug
from src.utils.xml import getFloatCommand, getIntCommand


class Trend3D_linear_model:
    """
    This class keeps model parameter for linear 3D trend. The parameterization
    is azimuth angle for depositional direction and stacking angle. In addition a variable
    specifying whether the deposition is progradational or retrogradational is specified.

    Public member functions:
    Constructor:   def __init__(self, trendRuleXML=None, debug_level=Debug.OFF, modelFileName=None)

   Get functions:
    def getAzimuth(self)
    def getStackingAngle(self)
    def getStackingDirection(self)

   Set functions:
    def setAzimuth(self,angle)
    def setStackingAngle(self,stackingAngle)
    def setStackingDirection(self,direction)
    def initialize(self,azimuthAngle,stackingAngle,direction,debug_level=Debug.OFF)
    
   XmlTree update function:
    def XMLAddElement(self,parent)
    
   Private member functions:
    def __interpretXMLTree(self,trendRuleXML,debug_level,modelFileName)
"""

    def __init__(self, trendRuleXML, debug_level=Debug.OFF, modelFileName=None):
        """
        Create either empty object which have to be initialized
        later using the initialize function or create a full object
        by reading input parameters from XML input tree.
        :param trendRuleXML:
        :param debug_level:
        :param modelFileName:
        """
        self.__azimuth = 0.0
        self.__stackingAngle = 0.0
        self.__direction = 1
        self.__debug_level = debug_level
        self.__className = 'Trend3D_linear_model'
        self.type = 'Trend3D_linear'

        if trendRuleXML is not None:
            self.__interpretXMLTree(trendRuleXML, debug_level, modelFileName)
            if self.__debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: Trend:')
                print('Debug output: Azimuth:        ' + str(self.__azimuth))
                print('Debug output: Stacking angle: ' + str(self.__stackingAngle))
                print('Debug output: Stacking type:  ' + str(self.__direction))
        else:
            if self.__debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: Create empty object of ' + self.__className)

    def __interpretXMLTree(self, trendRuleXML, debug_level=Debug.OFF, modelFileName=None):
        # Initialize object form xml tree object trendRuleXML
        self.__azimuth = getFloatCommand(trendRuleXML, 'azimuth', modelFile=modelFileName)

        if not 0.0 < self.__azimuth < 360.0:
            raise ValueError(
                'Error: In {className}\n'
                'Error: Azimuth angle for linear trend ({angle}) is not within [0,360] degrees.'
                ''.format(className=self.__className, angle=self.__azimuth)
            )

        self.__direction = getIntCommand(trendRuleXML, 'directionStacking', modelFile=modelFileName)
        if self.__direction != -1 and self.__direction != 1:
            raise ValueError(
                'Error: In {}\n'
                'Error: Direction for linear trend is specified to be: {}\n'
                'Error: Direction for linear trend must be 1 if stacking angle is positive\n'
                '       when moving in positive azimuth direction and -1 if stacking angle\n'
                '       is positive when moving in negative azimuth direction.'
                ''.format(self.__className, self.__direction)
            )

        self.__stackingAngle = getFloatCommand(
            trendRuleXML, 'stackAngle', modelFile=modelFileName
        )

        if self.__stackingAngle < 0.0 or self.__stackingAngle > 90.0:
            raise ValueError(
                'Error: In {}\n'
                'Error: Stacking angle for linear trend is not within [0,90] degrees.'
                ''.format(self.__className)
            )

    def initialize(self, azimuthAngle, stackingAngle, direction, debug_level=Debug.OFF):
        if debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: Call the initialize function in ' + self.__className)

        self.__debug_level = debug_level
        if azimuthAngle < 0.0 or azimuthAngle > 360.0:
            raise ValueError(
                'Error: In {}\n'
                'Error: Cannot set azimuth angle for linear trend outside interval [0,360] degrees.'
                ''.format(self.__className)
            )
        if stackingAngle < 0.0 or stackingAngle > 90.0:
            raise ValueError(
                'Error in {}\n'
                'Error: Cannot set stacking angle to be outside interval [0,90] degrees.'
                ''.format(self.__className)
            )
        if direction != -1 and direction != 1:
            raise ValueError(
                'Error in {}\n'
                'Error: Cannot set stacking type to be a number different from -1 and 1.'
                ''.format(self.__className)
            )
        self.__azimuth = azimuthAngle
        self.__stackingAngle = stackingAngle
        self.__direction = direction
        self.__debug_level = debug_level
        if self.__debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: Trend:')
            print('Debug output: Azimuth:        ' + str(self.__azimuth))
            print('Debug output: Stacking angle: ' + str(self.__stackingAngle))
            print('Debug output: Stacking type:  ' + str(self.__direction))

    def getAzimuth(self):
        return self.__azimuth

    def getStackingAngle(self):
        return self.__stackingAngle

    def getStackingDirection(self):
        return self.__direction

    def setAzimuth(self, angle):
        if angle < 0.0 or angle > 360.0:
            raise ValueError(
                'Error: In {}\n'
                'Error: Cannot set azimuth angle for linear trend outside interval [0,360] degrees'
                ''.format(self.__className)
            )
        else:
            self.__azimuth = angle

    def setStackingAngle(self, stackingAngle):
        if stackingAngle < 0.0 or stackingAngle > 90.0:
            raise ValueError(
                'Error in {}\n'
                'Error: Cannot set stacking angle to be outside interval [0,90] degrees.'
                ''.format(self.__className)
            )
        else:
            self.__stackingAngle = stackingAngle

    def setStackingDirection(self, direction):
        if direction != -1 and direction != 1:
            raise ValueError(
                'Error in {}\n'
                'Error: Cannot set stacking type to be a number different from -1 and 1.'
                ''.format(self.__className)
            )
        else:
            self.__direction = direction

    def XMLAddElement(self, parent):
        # Add to the parent element a new element with specified tag and attributes.
        # The attributes are a dictionary with {name:value}
        # After this function is called, the parent element has got a new child element
        # for the current class.
        if self.__debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: call XMLADDElement from ' + self.__className)

        attribute = {'name': 'Linear3D'}
        tag = 'Trend'
        trendElement = Element(tag, attribute)
        # Put the xml commands for this truncation rule as the last child for the parent element
        parent.append(trendElement)

        tag = 'azimuth'
        obj = Element(tag)
        obj.text = ' ' + str(self.__azimuth) + ' '
        trendElement.append(obj)

        tag = 'directionStacking'
        obj = Element(tag)
        obj.text = ' ' + str(self.__direction) + ' '
        trendElement.append(obj)

        tag = 'stackAngle'
        obj = Element(tag)
        obj.text = ' ' + str(self.__stackingAngle) + ' '
        trendElement.append(obj)

    def __calcLinearTrendNormalVector(self, azimuthSimBox):
        """
        Calculate normal vector to iso-surfaces (planes) for constant trend values
        a*(x-x0)+b*(y-y0)+c*(z-z0) = K where K is a constant is such
        an iso surface and [a,b,c] is the normal vector to the plane.
        """
        # Calculate the 3D trend values

        alpha = (90.0 - self.__stackingAngle) * np.pi / 180.0
        if self.__direction == 1:
            theta = (self.__azimuth - azimuthSimBox) * np.pi / 180.0
        else:
            theta = (self.__azimuth - azimuthSimBox + 180.0) * np.pi / 180.0

        # Normal vector to a plane with constant trend value is [xComponent,yComponent,zComponent]
        xComponent = math.cos(alpha) * math.sin(theta)
        yComponent = math.cos(alpha) * math.cos(theta)
        zComponent = math.sin(alpha)
        return [xComponent, yComponent, zComponent]

    def createTrendFor2DProjection(self, simBoxXsize, simBoxYsize, simBoxZsize,
                                   azimuthSimBox,
                                   nxPreview, nyPreview, nzPreview, projectionType,
                                   crossSectionIndx):

        [xComponent, yComponent, zComponent] = self.__calcLinearTrendNormalVector(azimuthSimBox)
        xinc = simBoxXsize / nxPreview
        yinc = simBoxYsize / nyPreview
        zinc = simBoxZsize / nzPreview
        values = None
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

        #        minValue = np.min(values)
        #        maxValue = np.max(values)
        minmaxDifference = maxValue - minValue
        valuesRescaled = self.__direction * values / minmaxDifference

        minValue = minValue / minmaxDifference
        maxValue = maxValue / minmaxDifference
        minmaxDifference = maxValue - minValue
        minValueInCrossSection = min(valuesRescaled)
        maxValueInCrossSection = max(valuesRescaled)
        if self.__debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: Min value of trend within simBox: ' + str(minValue))
            print('Debug output: Max value of trend within simBox: ' + str(maxValue))
            print('Debug output: Difference between max and min value within simBox: ' + str(minmaxDifference))
            print('Debug output: Min value of trend within cross section: ' + str(minValueInCrossSection))
            print('Debug output: Max value of trend within cross section: ' + str(maxValueInCrossSection))

        return [minmaxDifference, valuesRescaled]
