#!/bin/env python
# Python 3 Calculate linear trend in 3D in RMS10 using roxapi

import math
from xml.etree.ElementTree import Element
from src.utils.constants import Debug

import numpy as np

from src.xmlFunctions import getFloatCommand, getIntCommand


class Trend3D_linear_model:
    """
    Description: This class keeps model parameter for linear 3D trend. The parameterization
             is azimuth angle for depositional direction and stacking angle. In addition a variable
             specifying whether the deposition is progradational or retrogradational is specified.
    Description: Create either empty object which have to be initialized
                     later using the initialize function or create a full object
                     by reading input parameters from XML input tree.

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
        Description: Create either empty object which have to be initialized
                     later using the initialize function or create a full object
                     by reading input parameters from XML input tree.
        """

        self.__azimuth = 0.0
        self.__stackingAngle = 0.0
        self.__direction = 1
        self.__debug_level = debug_level
        self.__className = 'Trend3D_linear_model'
        self.type = 'Trend3D_linear'

        if trendRuleXML is not None:
            self.__interpretXMLTree(trendRuleXML, modelFileName, debug_level)
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
