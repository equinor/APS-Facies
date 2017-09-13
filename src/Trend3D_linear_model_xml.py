#!/bin/env python
# Python 3 Calculate linear trend in 3D in RMS10 using roxapi

from xml.etree.ElementTree import Element


class Trend3D_linear_model:
    """
    -------------------------------------------------------------------
    class Trend3D_linear_model
    Description: Calculate linear 3D trend for specified grid cells. This class keeps model parameter for
                 linear 3D trend. The parameterization is asimuth angle for depositional direction and stacking angle.
                 In addition a variable specifying whether the deposition is progradational or
                retrogradational is specified.

     Public member functions:
     Constructor:   def __init__(self,trendRuleXML=None,printInfo=0,modelFileName=None)

     Get functions:
      def getAsimuth(self)
      def getStackingAngle(self)
      def getStackingDirection(self)

     Set functions:
      def setAsimuth(self,angle)
      def setStackingAngle(self,stackingAngle)
      def setStackingDirection(self,direction)
      def initialize(self,asimuthAngle,stackingAngle,direction,printInfo)

     XmlTree update function:
      def XMLAddElement(self,parent)

     Private member functions:
      def __interpretXMLTree(self,trendRuleXML,printInfo,modelFileName)


    --------------------------------------------------------------------------------------
    """

    def __init__(self, trendRuleXML, printInfo=0, modelFileName=None):
        """
        Description: Create either empty object which have to be initialized
                     later using the initialize function or create a full object
                     by reading input parameters from XML input tree.
        """

        self.__azimuth = 0.0
        self.__stackingAngle = 0.0
        self.__direction = 1
        self.__printInfo = printInfo
        self.__className = 'Trend3D_linear_model'
        self.type = 'Trend3D_linear'

        if trendRuleXML is not None:
            self.__interpretXMLTree(trendRuleXML, printInfo, modelFileName)
            if self.__printInfo >= 3:
                print('Debug output: Trend:')
                print('Debug output: Asimuth:        ' + str(self.__azimuth))
                print('Debug output: Stacking angle: ' + str(self.__stackingAngle))
                print('Debug output: Stacking type:  ' + str(self.__direction))
        else:
            if self.__printInfo >= 3:
                print('Debug info: Create empty object of ' + self.__className )

    def __interpretXMLTree(self, trendRuleXML, printInfo, modelFileName):
        # Initialize object form xml tree object trendRuleXML
        kw = 'asimuth'
        obj = trendRuleXML.find(kw)
        if obj is not None:
            text = obj.text
            self.__azimuth = float(text.strip())
        else:
            raise ValueError(
                'Error in {}\n'
                'Error missing keyword {} in keyword Trend'
                ''.format(self.__className, kw)
            )

        if self.__azimuth < 0.0 or self.__azimuth > 360.0:
            raise ValueError(
                'Error: In {}\n'
                'Error: Asimuth angle for linear trend is not within [0,360] degrees.'
                ''.format(self.__className)
            )

        kw = 'directionStacking'
        obj = trendRuleXML.find(kw)
        if obj is not None:
            text = obj.text
            self.__direction = int(text.strip())
            if self.__direction != -1 and self.__direction != 1:
                raise ValueError(
                    'Error: In {}\n'
                    'Error: Direction for linear trend is specified to be: {}\n'
                    'Error: Direction for linear trend must be 1 if stacking angle is positive\n'
                    '       when moving in positive asimuth direction and -1 if stacking angle\n'
                    '       is positive when moving in negative asimuth direction.'
                    ''.format(self.__className, self.__direction)
                )

        kw = 'stackAngle'
        obj = trendRuleXML.find(kw)
        if obj is not None:
            text = obj.text
            self.__stackingAngle = float(text.strip())
        else:
            raise ValueError(
                'Error in {}\n'
                'Error: Missing keyword {} in keyword Trend'
                ''.format(self.__className, kw)
            )

        if self.__stackingAngle < 0.0 or self.__stackingAngle > 90.0:
            raise ValueError(
                'Error: In {}\n'
                'Error: Stacking angle for linear trend is not within [0,90] degrees.'
                ''.format(self.__className)
            )

    def initialize(self, asimuthAngle, stackingAngle, direction, printInfo):
        self.__printInfo = printInfo
        if asimuthAngle < 0.0 or asimuthAngle > 360.0:
            raise ValueError(
                'Error: In {}\n'
                'Error: Cannot set asimuth angle for linear trend outside interval [0,360] degrees.'
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
        self.__azimuth = asimuthAngle
        self.__stackingAngle = stackingAngle
        self.__direction = direction
        self.__printInfo = printInfo
        if self.__printInfo >= 3:
            print('Trend:')
            print('Asimuth:        ' + str(self.__azimuth))
            print('Stacking angle: ' + str(self.__stackingAngle))
            print('Stacking type:  ' + str(self.__direction))

    def getAsimuth(self):
        return self.__azimuth

    def getStackingAngle(self):
        return self.__stackingAngle

    def getStackingDirection(self):
        return self.__direction

    def setAsimuth(self, angle):
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
        attribute = {'name': 'Linear3D'}
        tag = 'Trend'
        trendElement = Element(tag, attribute)
        # Put the xml commands for this truncation rule as the last child for the parent element
        parent.append(trendElement)

        tag = 'asimuth'
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
