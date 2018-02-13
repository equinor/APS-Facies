#!/bin/env python
# -*- coding: utf-8 -*-
import copy
from xml.etree.ElementTree import Element

import numpy as np

from src.algorithms.Trunc2D_Base_xml import Trunc2D_Base
from src.utils.constants.simple import Debug
from src.utils.numeric import isNumber
from src.utils.xml import getFloatCommand, getKeyword, getTextCommand


class Trunc2D_Angle(Trunc2D_Base):
    """
    This class implements adaptive plurigaussian field truncation
    using two simulated gaussian fields (with trend).

    This class is derived from Trunc2D_Base which contain common data structure for
    truncation algorithms with overlay facies.

    Truncation map consists of polygons defined by linear sloping boundaries.
    Each facies boundary has a normal vector with specified direction.
    The direction is specified as anticlockwise rotation relative to first axis.
    The angle is in degrees. So an angle of 0.0 means that the normal vector points
    in the first axis direction ('x'-direction).
    An angle of 90.0 degrees means that the normal vector points in
    the second axis direction ('y' direction) while angle of 45.0 degrees means a
    45 degree rotation of the vector relative to the first axis direction anticlockwise.
    It is possible to specify that a facies can be associated with multiple polygons
    in the truncation map.

    Overlay facies can be defined and follow the rule defined in the Trunc2D_Base class.

     Constructor:
        def __init__(self, trRuleXML=None, mainFaciesTable=None, faciesInZone=None,
                     nGaussFieldInModel=None, debug_level=Debug.OFF, modelFileName=None)

     Public member functions:
     def initialize(self, mainFaciesTable, faciesInZone, truncStructure,
                    backGroundFaciesGroups, overlayFacies, overlayTruncCenter,
                    useConstTruncParam, debug_level)
     def getTruncationParam(self, get3DParamFunction, gridModel, realNumber)
     def setTruncRule(self, faciesProb, cellIndx=0)
     def defineFaciesByTruncRule(self, alphaCoord)
     def getClassName(self)
     def useConstTruncModelParam(self)
     def getNCountShiftAlpha(self)
     def truncMapPolygons(self)
     def faciesIndxPerPolygon(self)
     def setAngle(self, polygonNumber, angle)
     def setAngleTrend(self, polygonNumber, angleParamName)
     def setUseTrendForAngles(self, useConstTrend)
     def XMLAddElement(self, parent)
     def writeContentsInDataStructure(self)
     def getNCalcTruncMap(self)
     def getNLookupTruncMap(self)

     Private member functions:
     def __setEmpty(self)
     def __interpretXMLTree(self, trRuleXML, modelFileName)
     def __setUnitSquarePolygon(self)
     def __setZeroPolygon(self)
     def __setFaciesLines(self, cellIndx)
     def __subdividePolygonByLine(self, polygonPts, vx, vy, x0, y0)
     def __polyArea(self, polygon)
     def __findSminSmaxForPolygon(self, polygon, vx, vy, vxNormal, vyNormal, x0Normal, y0Normal)
     def __defineIntersectionFromProb(self, polygon, vx, vy, vxNormal, vyNormal, x0Normal, y0Normal, faciesProb)
     def __isInsidePolygon(self, polygon, xInput, yInput)
     def __calculateFaciesPolygons(self,cellIndx,area)
    """

    def __setEmpty(self):
        """Initialize values for empty data structure"""

        # Specific variables for class Trunc2D_Angle
        self._className = 'Trunc2D_Angle'

        # Variables containing truncations for the 2D truncation map
        # The input direction angles can be file names in case trend parameters for these are specified
        self.__faciesBoundaryOrientationName = []

        # List of angles in case no trend of truncation parameter is used
        # and in case trend parameters are used for truncation parameters,
        # each element in the list is a 3D parameter with values.
        self.__faciesBoundaryOrientation = []

        self.__probFracPerPolygon = []
        self.__nPolygons = 0

        # Variables for the internal data structure
        self.__vxLine = []
        self.__vyLine = []
        self.__vxNormal = []
        self.__vyNormal = []
        self.__x0Normal = []
        self.__y0Normal = []
        self.__fNrLine = []
        self.__faciesPolygons = []
        self.__faciesIndxPerPolygon = []
        self.__shiftTolerance = 0.01
        self.__nCountShiftBoundaryOrientation = 0
        # Define if truncation parameter (angles) are constant for all grid cells or
        # vary from cell to cell.
        self.__useConstTruncModelParam = True

        # Define dictionary to be used in memoization for optimization
        # In this dictionary use key equal to faciesProb and save faciespolygon
        self.__memo = {}
        self.__nCalc = 0
        self.__nLookup = 0
        self.__useMemoization = 1
        # To make a lookup key from facies probability, round off input facies probability
        # to nearest value which is written like  n/resolution where n is an integer from 0 to resolution
        self.__keyResolution = 100

    def __init__(self, trRuleXML=None, mainFaciesTable=None, faciesInZone=None, gaussFieldsInZone=None,
                 keyResolution=100, debug_level=Debug.OFF, modelFileName=None, zoneNumber=None):
        """
        This constructor can either create a new object by reading the information
        from an XML tree or it can create an empty data structure for such an object.
        If an empty data structure is created, the initialize function must be used.

        About data structure:
        All information related to common data which is used by more than one truncation algorithm
        is saved in the base class Trunc2D_Base. This includes lists and data related to facies tables
        and data structure for modelling of overlya facies.
        """
        nGaussFieldsInBackGroundModel = 2
        super().__init__(trRuleXML, mainFaciesTable, faciesInZone, gaussFieldsInZone,
                         debug_level, modelFileName, nGaussFieldsInBackGroundModel)
        self.__setEmpty()

        if keyResolution == 0:
            self.__useMemoization = False
        else:
            self.__useMemoization = True
            self.__keyResolution = keyResolution

        if trRuleXML is not None:
            if debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: Read data from model file for: ' + self._className)

            # Read truncation rule for background facies from xml tree.
            # Here the hierarchy of polygons in the 2D truncation map defined by the two
            # first transformed gaussian fields is defined. This is specific for the non cubic truncations.
            self.__interpretXMLTree(trRuleXML, modelFileName)

            # Call base class method to read truncation rule for overlay facies.
            # Overlay facies truncation rules are read here. The overlay facies does not
            # have to know anything about how the 2D truncation map defined by the two first
            # transformed gaussian fields looks like. It only need to know which facies in the 2D map
            # is "background" for each overlay facies. Therefore data structure and methods
            # related to overprint facies is common to several different truncation algorithms.
            self._interpretXMLTree_overlay_facies(trRuleXML, modelFileName, zoneNumber)

            # Call base class method to check that facies in truncation rule is
            # consistent with facies in zone.
            self._checkFaciesForZone()

            if self._debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: Facies names in truncation rule:')
                print(repr(self._faciesInTruncRule))
                print('Debug output: Facies ordering (relative to facies in zone):')
                print(repr(self._orderIndex))
                print('Debug output: Facies code for facies in zone')
                print(repr(self._faciesCode))
                print(' ')
                print('Debug output: Gauss fields in zone:')
                print(repr(self._gaussFieldsInZone))
                print('Debug output: Gauss fields for each alpha coordinate:')
                for i in range(len(self._alphaIndxList)):
                    j = self._alphaIndxList[i]
                    gfName = self._gaussFieldsInZone[j]
                    print(' {} {}'.format(str(i + 1), gfName))

        else:
            if debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: Create empty object for: ' + self._className)
                #  End of __init__

    def __interpretXMLTree(self, trRuleXML, modelFileName):
        """
        Initialize object from xml tree object trRuleXML.
        This function read Angle truncation rules.
        It does however NOT read any Overlay facies.
        This is done by methods from base class which handle overlay facies.
        """
        self._className = 'Trunc2D_Angle'

        # Keyword BackGroundModel
        bgmObj = getKeyword(trRuleXML, 'BackGroundModel', 'TruncationRule', modelFileName, required=True)

        # Keyword UseConstTruncParam
        useParamObj = getKeyword(bgmObj, 'UseConstTruncParam', 'BackGroundModel', modelFileName, required=True)
        if useParamObj is None:
            self.__useConstTruncModelParam = True
        else:
            text = useParamObj.text
            val = int(text.strip())
            if val == 0:
                self.__useConstTruncModelParam = False
            else:
                self.__useConstTruncModelParam = True

        kw = 'Facies'
        nPolygons = 0
        probFracPerPolygon = []
        sumProbFrac = []
        nFacies = 0
        # Keyword Facies
        for faciesObj in bgmObj.findall(kw):
            if faciesObj is None:
                raise IOError(
                    'Error when reading model file: {}\n'
                    'Error: Read truncation rule: {}\n'
                    'Error: Missing keyword {} under keyword BackGroundModel under keyword TruncationRule'
                    ''.format(modelFileName, self._className, kw, )
                )
            fName = faciesObj.get('name')
            nFacies, indx, fIndx, isNewFacies = self._addFaciesToTruncRule(fName)
            self.__faciesIndxPerPolygon.append(indx)

            kw2 = 'Angle'
            # Input angle is anticlockwise rotation from first axis and in degrees.
            text = getTextCommand(faciesObj, kw2, 'Facies', modelFile=modelFileName, required=True)
            if self.__useConstTruncModelParam:
                if isNumber(text):
                    value = float(text.strip())
                    self.__faciesBoundaryOrientation.append(value)
                else:
                    raise ValueError(
                        'Error: when reading model file: {}\n'
                        'Error: Read truncation rule: {}\n'
                        'Error: Expecting a floating point number, but got {} in keyword {} under keyword Facies '
                        'under keyword TruncationRule\n'
                        'Change keyword UseConstTruncParam to 0'
                        ''.format(modelFileName, self._className, text, kw2)
                    )
            else:
                paramNameAlpha = copy.copy(text.strip())
                self.__faciesBoundaryOrientationName.append([fName, paramNameAlpha])

            kw3 = 'ProbFrac'
            # Input prob fraction must be in interval [0,1] and for each facies this fraction must
            # sum up to 1.0 when summing over all polygons with the same facies.
            probFrac = getFloatCommand(faciesObj, kw3, 'Facies', modelFile=modelFileName, required=True)
            if probFrac < 0.0 or probFrac > 1.0:
                raise IOError(
                    'Error when reading model file: {}\n'
                    'Error: Read truncation rule: {}\n'
                    'Error: Probability fraction specified for {} in keyword {}\n'
                    ' under keyword Facies under keyword TruncationRule is: {} which is outside [0,1]'
                    ''.format(modelFileName, self._className, fName, kw3, probFrac)
                )

            item = [indx, probFrac]

            probFracPerPolygon.append(item)
            nPolygons += 1
            if isNewFacies == 0:
                sumProbFrac[indx] += probFrac
            else:
                # New facies
                sumProbFrac.append(probFrac)
                self._orderIndex.append(fIndx)
        # End read Facies
        self._nBackGroundFacies = nFacies
        self.__probFracPerPolygon = probFracPerPolygon
        self.__nPolygons = nPolygons

        # Check the sum over background facies for probfrac
        # Note that overlay facies is not a part of this calculations.
        for i in range(self._nBackGroundFacies):
            if self._debug_level >= Debug.VERY_VERBOSE:
                fName = self._faciesInTruncRule[i]
                print('Debug output: Sum prob frac for facies {0} is: {1}'.format(fName, str(sumProbFrac[i])))

            if abs(sumProbFrac[i] - 1.0) > 0.001:
                fName = self._faciesInTruncRule[i]
                raise ValueError(
                    'Error in: {0}\n'
                    '         Sum of probability fractions over all polygons for facies {1} is not 1.0\n'
                    '         The sum is: {2}'
                    ''.format(self._className, fName, str(sumProbFrac[i]))
                )

    def initialize(self, mainFaciesTable, faciesInZone, gaussFieldsInZone, alphaFieldNameForBackGroundFacies,
                   truncStructure, overlayGroups=None, useConstTruncParam=False, debug_level=Debug.OFF):
        """
        Initialize the truncation object from input variables.
                  debug_level - an integer number from 0 to 3 defining how much to be printed to screen during runs.
        :param mainFaciesTable: object of class APSMainFaciesTable
        :param faciesInZone: list of facies names to be modelled for the zone. Example: ['F1','F2','F3']
        :param gaussFieldsInZone: List of gauss fields defined for the zone.
        :param alphaFieldNameForBackGroundFacies: Name of the gauss fields corresponding to alpha1 and
                                                  alpha2 that define background facies truncation map.
        :param truncStructure: list of tuples [facies name, angle, probfraction],
                               one per polygon in the truncation map.
                               Example: [['F1',90.0,0.4],['F2',-45.0, 1.0],['F1',-135.0,0.6]].
                               This example show that there are two facies,
                               but three polygons since one facies is
                               associated with two different polygons with
                               probability fraction split into 0.4 and 0.6.
                               The second value in the tuple is the angle
                               specified by the user for the normal vector
                               to the facies polygon line in the truncation map.
        :param overlayGroups: List of overlay facies with associated alphaFields and probability fractions.
        :param useConstTruncParam: Is a boolean variable and must be True if the angles specified are specified as
                                   constants (not spatially dependent, not varlying from grid cell to grid cell in the
                                   modelling grid). If it is set to 1, the angle numbers specified in truncStructure
                                   must be replaced by name of RMS parameters containing the angles.
                                   In this case it is possible to specify spatial trends for these parameters.
        :param debug_level:
        :return:
        """
        # Initialize data structure
        if debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: Call the initialize function in ' + self._className)

        # Initialize base class variables
        super()._setEmpty()

        # Initialize this class variables
        self.__setEmpty()
        self._debug_level = debug_level

        # Call base class method to set modelled facies
        self._setModelledFacies(mainFaciesTable, faciesInZone)

        # Call base class method to associate gauss fields with alpha coordinates
        self._setGaussFieldForBackgroundFaciesTruncationMap(gaussFieldsInZone, alphaFieldNameForBackGroundFacies, 2)

        # Set data structure for truncation rule
        # Loop over all polygons in truncation map
        self.__useConstTruncModelParam = useConstTruncParam
        self.__nPolygons = 0
        for item in truncStructure:
            fName = item[0]
            probFrac = item[2]
            if self.__useConstTruncModelParam:
                angle = float(item[1])
                self.__faciesBoundaryOrientation.append(angle)
            else:
                angleTrendParamName = copy.copy(item[1])
                self.__faciesBoundaryOrientationName.append(angleTrendParamName)

            nFaciesInTruncRule, indx, fIndx, isNewFacies = self._addFaciesToTruncRule(fName)
            self.__faciesIndxPerPolygon.append(indx)
            self.__probFracPerPolygon.append([indx, probFrac])
            if isNewFacies == 1:
                self._orderIndex.append(fIndx)
            self.__nPolygons += 1

        if self._debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: Background facies defined: ')
            print(repr(self._faciesInTruncRule))

        # Call base class function to fill data structure with overlay facies
        self._setOverlayFaciesDataStructure(overlayGroups)

        # Check that facies in truncation rule is consistent with facies in zone
        self._checkFaciesForZone()

    def getTruncationParam(self, gridModel, realNumber):
        """
        Description: This function is used if trends are specified for the angle parameters for this truncation rule.
                     The function will call ROXAPI functions to get grids with values for the angles.
                     The function requires knowledge of which RMS grid and realization
                     to use in this operation.
        """
        # Read truncation parameters
        import src.utils.roxar.generalFunctionsUsingRoxAPI as gr
        self.__faciesBoundaryOrientation = []
        if not self.__useConstTruncModelParam:
            for k in range(self._nFacies):
                item = self.__faciesBoundaryOrientationName[k]
                fName = item[0]
                paramName = item[1]
                # Check consistency
                if fName == self._faciesInTruncRule[k]:
                    # Get param values
                    if self._debug_level >= Debug.VERBOSE:
                        print('--- Get RMS parameter: ' + paramName + ' for facies ' + fName)
                    values = gr.getContinuous3DParameterValues(gridModel, paramName, realNumber, self._debug_level)
                    self.__faciesBoundaryOrientation.append(values)
                else:
                    raise ValueError(
                        'Error in {}\n'
                        'Error: Inconsistency in data structure. Programming error.'
                        ''.format(self._className)
                    )

    @staticmethod
    def __setUnitSquarePolygon():
        """
        Description: Function related to this truncation rule.
                     Create a polygon for the unit square
        """
        poly = [[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]
        return poly

    @staticmethod
    def __setZeroPolygon():
        """
        Description: Function related to this truncation rule.
                     Create a dummy 0 size polygon.
        """
        poly = [[0, 0], [0, 0.0001], [0.0001, 0.0001], [0, 0.0001], [0, 0]]
        return poly

    def __setFaciesLines(self, cellIndx):
        """
        Description:
        Input: Facies names and direction angles
              (measured in anticlockwise direction relative to x-axis)
              for the normal to the facies boundary lines in the truncation map.

        Output: Arrays with direction  vector components for boundary lines
               (tangent vector components) (vx,vy).
               Arrays with normal vector components to boundary lines (vxnormal,vyNormal).
               A reference point for a line with the normal vector as its direction vector.
               The arrays have indices which are the same as facies number.
        Algorithm:
         Direction vectors [vx,vy] of normal to each facies border line
         Direction vectors [vy,-vx] of facies border line  since dot product [vy,-vx]*[vx,vy] = 0
         Lines are parameterized as:
            x(t) = x0 + vy*t
            y(t) = y0 - vx*t
         The point (x0,y0) will vary and creates alternative parallell facies border lines

         These lines are parameterized like:
         for  0<= alpha < 90
            xref(s) = 0.0 + a1*vx*s
            yref(s) = 0.0 + a1*vy*s
         for  90 <= alpha < 180
            xref(s) = 1.0 + a2*vx*s
            yref(s) = 0.0 + a2*vy*s
         for  -90<= alpha < 0
            xref(s) = 0.0 + a3*vx*s
            yref(s) = 1.0 + a3*vy*s
         for  -180 <= alpha < 90
            xref(s) = 1.0 + a4*vx*s
            yref(s) = 1.0 + a4*vy*s
         where a1,a2,a3,a4 is defined such that when 0<= s <=1 the
         line defined by
            x(t) = xref(s) + vy*t
            y(t) = yref(s) - vx*t
         run through  (0,0) for s=0 and (1,1) for s=1 when 0<= alpha <= 90
         run through  (1,0) for s=0 and (0,1) for s=1 when 0<= alpha <= 90
         run through  (0,1) for s=0 and (1,0) for s=1 when -90<= alpha <= 0
         run through  (1,1) for s=0 and (0,0) for s=1 when -180 <= alpha <= -90

        """
        vxLine = []
        vyLine = []
        vxNormal = []
        vyNormal = []
        x0Normal = []
        y0Normal = []
        fNrLine = []

        faciesAlpha = []
        if self.__useConstTruncModelParam:
            # The angle is constant, not varying from cell to cell
            # The list self.__faciesBoundaryOrientation is one angle per polygon specified.
            faciesAlpha = self.__faciesBoundaryOrientation
        else:
            # The angle is constant, not varying from cell to cell
            # The list self.__faciesBoundaryOrientation is a list of arrays.
            # Look up the value for the specified grid cell with index cellIndx
            for i in range(self.__nPolygons):
                values = self.__faciesBoundaryOrientation[i]
                faciesAlpha.append(values[cellIndx])

        for i in range(self.__nPolygons):
            alpha = faciesAlpha[i]
            alpha = alpha * 3.14159265 / 180.0
            vx = np.cos(alpha)
            vy = np.sin(alpha)
            vxLine.append(vy)
            vyLine.append(-vx)
            if vx >= 0.0 and vy >= 0.0:
                # 0<= alpha <= 90
                a = (vx + vy)
                vxNormal.append(vx * a)
                vyNormal.append(vy * a)
                x0Normal.append(0.0)
                y0Normal.append(0.0)
            if vx < 0.0 <= vy:
                # 90< alpha <= 180
                a = (vy - vx)
                vxNormal.append(vx * a)
                vyNormal.append(vy * a)
                x0Normal.append(1.0)
                y0Normal.append(0.0)
            if vx >= 0.0 > vy:
                # -90<= alpha < 0
                a = (vx - vy)
                vxNormal.append(vx * a)
                vyNormal.append(vy * a)
                x0Normal.append(0.0)
                y0Normal.append(1.0)
            if vx < 0.0 and vy < 0.0:
                # -180< alpha < -900
                a = -(vx + vy)
                vxNormal.append(vx * a)
                vyNormal.append(vy * a)
                x0Normal.append(1.0)
                y0Normal.append(1.0)

            fNrLine.append(i)
            # The sequence defines which facies (facies index)
        self.__vxLine = vxLine
        self.__vyLine = vyLine
        self.__vxNormal = vxNormal
        self.__vyNormal = vyNormal
        self.__x0Normal = x0Normal
        self.__y0Normal = y0Normal
        self.__fNrLine = fNrLine
        return

    @staticmethod
    def __subdividePolygonByLine(polygonPts, vx, vy, x0, y0):
        """
        Description:
            Input: Polygon and a straight line defined by its direction
                   vector (vx,vy) and reference point (x0,y0).

            Output: A variable telling if the polygon is split into two polygons
                    and the two new polygons if the original polygon was
                    split into two by the input line.
        """

        outputPolyA = []
        outputPolyB = []
        # Find intersection between input line defined by x(t) = x0 + vx*t  y(t) = y0 + vy*t
        # and polygon lines for the closed input polygon
        pt1 = polygonPts[0]
        pt1x = pt1[0]
        pt1y = pt1[1]

        n = len(polygonPts)
        intersectPt1x = -1
        intersectPt2x = -1
        intersectPt1y = -1
        intersectPt2y = -1
        indx1 = -1
        indx2 = -1
        #        print(repr(polygonPts))
        #        print('vx: {}, vy:{}, x0:{}, y0:{}'.format(str(vx), str(vy), str(x0), str(y0)))
        for i in range(1, n):
            pt0x = pt1x
            pt0y = pt1y
            pt1 = polygonPts[i]
            pt1x = pt1[0]
            pt1y = pt1[1]

            vxp = pt1x - pt0x
            vyp = pt1y - pt0y

            u0x = (pt0x - x0)
            u0y = (pt0y - y0)

            d = vy * vxp - vx * vyp
            if d == 0:
                # No intersection the input line and polygon line are parallell
                t = 1000  # greather than 1
            else:
                s = (u0y * vxp - u0x * vyp) / d
                t = (u0y * vx - u0x * vy) / d
                x = pt0x + vxp * t
                y = pt0y + vyp * t
            #            print('i= {} t= {} d={}'.format(str(i), str(t), str(d)))
            if 0 < t < 1:
                # intersection with line segment between polygon point i-1 and point i.
                # Add point inbetween the two points defining the edge where the intersection appears
                # Either 0 or 2 intersection points with the closed convex polygon exists
                if indx1 == -1:
                    intersectPt1x = x
                    intersectPt1y = y
                    indx1 = i
                else:
                    intersectPt2x = x
                    intersectPt2y = y
                    indx2 = i
        isSplit = 0
        if indx1 == -1:
            # No intersection, return the input polygon as both the left polygon and right polygon
            outputPolyA = copy.copy(polygonPts)
            outputPolyB = copy.copy(polygonPts)
        else:
            isSplit = 1
            pt1 = [intersectPt1x, intersectPt1y]
            pt2 = [intersectPt2x, intersectPt2y]
            # Split the original polygon into two by the new line

            # The A-polygon is defined to be the points (0,1,..,indx1-1,intersectPt1,intersectPt2,indx2,..,n-1,0)
            for i in range(indx1):
                p1 = copy.copy(polygonPts[i])
                outputPolyA.append(p1)

            outputPolyA.append(pt1)
            outputPolyA.append(pt2)
            for i in range(indx2, n - 1):
                p1 = copy.copy(polygonPts[i])
                outputPolyA.append(p1)

            p1 = copy.copy(polygonPts[n - 1])
            outputPolyA.append(p1)

            # The B-polygon is defined to be the points (intersectPt1,indx1,..,indx2-1,intersectPt2,intersectPt1)
            outputPolyB.append(pt1)
            for i in range(indx1, indx2):
                p1 = copy.copy(polygonPts[i])
                outputPolyB.append(p1)

            outputPolyB.append(pt2)
            outputPolyB.append(pt1)

        return isSplit, outputPolyA, outputPolyB

    @staticmethod
    def __polyArea(polygon):
        """
        Description:
            Input: Polygon
            Output: Area of the input polygon.
        """
        pt = polygon[0]
        x2 = pt[0]
        y2 = pt[1]
        area = 0.0
        for i in range(1, len(polygon)):
            x1 = x2
            y1 = y2
            pt = polygon[i]
            x2 = pt[0]
            y2 = pt[1]
            area = area + (x1 + x2) * (y1 - y2)
        area = -0.5 * area
        return area

    @staticmethod
    def __findSminSmaxForPolygon(polygon, vx, vy, vxNormal, vyNormal, x0Normal, y0Normal):
        """
        Description:
            Is used to calculate interval for a parameter s.
        """
        # First calculate the min and max value of s
        # for the parametric curve
        # x(s) = x0Normal + vxNormal*s
        # y(s) = y0Normal + vyNormal*s
        # by checking all the corner points of the input polygon
        n = len(polygon)
        smin = 2  # Initialize to a value above the maximum legal value of 1.0
        smax = -2  # Initialize to a value below the minimum legal value of 0.0
        epsMinMax = 0.01
        for i in range(n):
            pt1 = polygon[i]
            x0 = pt1[0]
            y0 = pt1[1]
            # Define a line parallell to the line defined by direction [vx,vy] and point [x0Normal,y0Normal]
            # This new parallell line should run through a polygon corner point (x0,y0), hence defined by
            # x2(t) = x0 + vx*t
            # y2(t) = y0 + vy*t
            # Calculate the intersection with the normal line
            # x(s) = x0Normal + vxNormal*s
            # y(s) = y0Normal + vyNormal*s
            # and determine the value of s
            d = vx * vyNormal - vy * vxNormal
            # This number must be value such that     0 <= s <= 1
            s = (-vy * (x0 - x0Normal) + vx * (y0 - y0Normal)) / d
            if s < smin:
                smin = s
            if s > smax:
                smax = s
        smin = smin - epsMinMax
        smax = smax + epsMinMax
        return smin, smax

    def __defineIntersectionFromProb(self, polygon, vx, vy, vxNormal, vyNormal, x0Normal, y0Normal, faciesProb):
        """
        Description:
            Intersection between a straight line and a closed polygon is calculated such that
            the area of one of the two polygons that are a result of the split matches as
            specified value (faciesProb).
            A bi-section algorithm is used to find the correct location of the line that splits the polygon.
        """
        # First calculate the min and max value of s
        # for the parametric curve
        # x(s) = x0Normal + vxNormal*s
        # y(s) = y0Normal + vyNormal*s
        # by checking all the corner points of the input polygon
        if faciesProb < self._epsFaciesProb:
            # The polygon area is 0.0. Define output polygons to be a 0 area polygon as the
            # closest polygon and the original as the one to be further divided.

            smin = 0.0
            smax = 0.05
        elif faciesProb > (1 - 0 - self._epsFaciesProb):
            smin = 0.95
            smax = 1.0
        else:
            [smin, smax] = self.__findSminSmaxForPolygon(polygon, vx, vy, vxNormal, vyNormal, x0Normal, y0Normal)

        sHigh = smax
        sLow = smin
        nmax = 20
        tolerance = 0.0025
        tolerance2 = 0.005
        converged = 0
        closestPolygon = 0
        isSplit = 0
        outputPolyA = None
        outputPolyB = None
        area = self.__polyArea(polygon)
        for i in range(nmax):
            s = 0.5 * (sHigh + sLow)
            x0 = x0Normal + vxNormal * s
            y0 = y0Normal + vyNormal * s
            # Split polygon
            isSplit, outputPolyA, outputPolyB = self.__subdividePolygonByLine(polygon, vx, vy, x0, y0)
            if isSplit:
                sminA, smaxA = self.__findSminSmaxForPolygon(
                    outputPolyA, vx, vy, vxNormal, vyNormal, x0Normal, y0Normal
                )
                sminB, smaxB = self.__findSminSmaxForPolygon(
                    outputPolyB, vx, vy, vxNormal, vyNormal, x0Normal, y0Normal
                )

                # Find the polygon closest to (x0Normal,y0Normal)
                if smaxA < smaxB:
                    area = self.__polyArea(outputPolyA)
                    closestPolygon = 1
                else:
                    area = self.__polyArea(outputPolyB)
                    closestPolygon = 2

            if self._debug_level >= Debug.VERY_VERY_VERBOSE:
                print('FaciesProb: {}  Iteration number: {}  Area: {} S: {} SLow: {}  SHigh {}'
                      ''.format(str(faciesProb), str(i), str(area), str(s), str(sLow), str(sHigh))
                      )

            if np.abs(area - faciesProb) > tolerance:
                if area > faciesProb:
                    sHigh = s
                else:
                    sLow = s
            else:
                converged = 1
                break
        # End for
        if converged == 0:
            print('area, prob: ' + str(area) + ' ' + str(faciesProb))
            if np.abs(area - faciesProb) > tolerance2:
                print('Warning message: Not converged')
                print('area, prob: ' + str(area) + ' ' + str(faciesProb))

                print(repr(outputPolyA))
                print(repr(outputPolyB))
                print(' ')

        return outputPolyA, outputPolyB, closestPolygon

    def setTruncRule(self, faciesProb, cellIndx=0):
        """
        Description:
        Input: Facies names, direction angles for facies boundary lines and facies probabilities.
        Output: A set of polygons that define the area for each facies
                within the truncation map.
        """
        # Call common functions from base class
        # Check if facies probability is close to 1.0. In this case do not calculate truncation map.
        # Take care of overprint facies to get correct probability (volume in truncation cube)
        self._setTruncRuleIsCalled = True
        faciesProbRoundOff = self._makeRoundOfFaciesProb(faciesProb, self._keyResolution)
        if self._isFaciesProbEqualOne(faciesProbRoundOff):
            return
        area = self._modifyBackgroundFaciesArea(faciesProbRoundOff)
        if self.__useMemoization:
            key = self._makeKey(faciesProb, self.__keyResolution)

            if key not in self.__memo:
                self.__nCalc += 1

                # Call methods specific for this truncation rule with corrected area due to overprint facies
                # Calculate polygons the truncation map is divided into
                polygons = self.__calculateFaciesPolygons(cellIndx, area)
                self.__memo[key] = polygons
                self.__faciesPolygons = polygons
            else:
                self.__nLookup += 1
                self.__faciesPolygons = self.__memo[key]
        else:
            # Call methods specific for this truncation rule with corrected area due to overprint facies
            # Calculate polygons the truncation map is divided into
            polygons = self.__calculateFaciesPolygons(cellIndx, area)
            self.__faciesPolygons = polygons

    def __calculateFaciesPolygons(self, cellIndx, area):
        """
        Description:  Calculate polygons in truncation map for given facies fraction (area)
        The result is saved in the internal variable self.__faciesPolygons
        """

        # Call methods specific for this truncation rule with corrected area due to overprint facies
        self.__setFaciesLines(cellIndx)
        initialPolygon = self.__setUnitSquarePolygon()
        polygon = copy.copy(initialPolygon)
        nPolygons = self.__nPolygons
        faciesPolygons = []
        for i in range(nPolygons - 1):
            vx = self.__vxLine[i]
            vy = self.__vyLine[i]
            vxN = self.__vxNormal[i]
            vyN = self.__vyNormal[i]
            x0N = self.__x0Normal[i]
            y0N = self.__y0Normal[i]
            item = self.__probFracPerPolygon[i]

            indx = item[0]
            probFrac = item[1]
            fIndx = self._orderIndex[indx]
            fProb = area[fIndx] * probFrac
            # If area = 0 for a facies, define a 0 area polygon as the one that is split off the input polygon
            if abs(area[fIndx]) < self._epsFaciesProb:
                outPolyA = [[0.0, 0.0], [1.0,0.0], [1.0, 0.000001], [0.0, 0.000001], [0.0,0.0]]
                faciesPolygons.append(outPolyA)
                if i == nPolygons - 2:
                    faciesPolygons.append(polygon)
            else:
                outPolyA, outPolyB, closestPolygon = self.__defineIntersectionFromProb(polygon, vx, vy, vxN, vyN, x0N, y0N, fProb)
                # Save facies polygons that are complete
                if closestPolygon == 1:
                    faciesPolygons.append(outPolyA)
                    if i == nPolygons - 2:
                        # add the last polygon to the last facies
                        faciesPolygons.append(outPolyB)

                    polygon = outPolyB
                else:
                    faciesPolygons.append(outPolyB)
                    if i == nPolygons - 2:
                        # add the last polygon to the last facies
                        faciesPolygons.append(outPolyA)

                    polygon = outPolyA
        return faciesPolygons

    def getNCalcTruncMap(self):
        return self.__nCalc

    def getNLookupTruncMap(self):
        return self.__nLookup

    def defineFaciesByTruncRule(self, alphaCoord):
        """
        Description: Apply the truncation rule to find facies.
        """
        x = alphaCoord[self._alphaIndxList[0]]
        y = alphaCoord[self._alphaIndxList[1]]
        # Check if the facies is deterministic (100% probability)
        for fIndx in range(len(self._faciesInZone)):
            if self._faciesIsDetermined[fIndx] == 1:
                faciesCode = self._faciesCode[fIndx]
                return faciesCode, fIndx

        # Input is facies polygons for truncation rules and two values between 0 and 1
        # Check in which polygon the point is located and thereby the facies
        inside = 0
        faciesCode = -999
        fIndx = -999
        for i in range(self.__nPolygons):
            polygon = self.__faciesPolygons[i]
            inside = self._isInsidePolygon(polygon, x, y)
            if inside == 0:
                continue
            else:
                item = self.__probFracPerPolygon[i]
                indx = item[0]
                assert indx >= 0
                # Check truncations for overlay facies (call function from base class)
                faciesCode, fIndx = self._truncateOverlayFacies(indx, alphaCoord)
                break

        if inside == 0:
            # Problem to identify which polygon in truncation map the point is within.
            # Try once more but now by minor shift of the input point.

            # Count the number of times in total for all cells this proble appears.
            self.__nCountShiftBoundaryOrientation += 1

            # Shift the point slightly and check again
            xNew = x + self.__shiftTolerance
            if xNew >= 1.0:
                xNew = x - self.__shiftTolerance
            yNew = y + self.__shiftTolerance
            if yNew >= 1.0:
                yNew = y - self.__shiftTolerance

            for i in range(self.__nPolygons):
                polygon = self.__faciesPolygons[i]
                inside = self._isInsidePolygon(polygon, xNew, yNew)
                if inside == 0:
                    continue
                else:
                    item = self.__probFracPerPolygon[i]
                    indx = item[0]
                    assert indx >= 0
                    # Check truncations for overlay facies (call function from base class)
                    faciesCode, fIndx = self._truncateOverlayFacies(indx, alphaCoord)
                    break

            assert inside == 1

        return faciesCode, fIndx

    def getClassName(self):
        return copy.copy(self._className)

    def useConstTruncModelParam(self):
        return self.__useConstTruncModelParam

    def getNCountShiftAlpha(self):
        return self.__nCountShiftBoundaryOrientation

    def truncMapPolygons(self):
        """
        Description: Return a lost of the polygons the truncation maps is divided into.
        """
        isDetermined = False
        for fIndx in range(len(self._faciesInZone)):
            if self._faciesIsDetermined[fIndx] == 1:
                isDetermined = True
                break

        if isDetermined:
            # One facies has 100% facies probability
            # Make a polygon equal to the complete unit square for this facies
            # and dummy 0 area polygons for all other facies
            self.__faciesPolygons = []
            for i in range(self.__nPolygons):
                indx = self.__faciesIndxPerPolygon[i]
                fIndx = self._orderIndex[indx]
                if self._faciesIsDetermined[fIndx] == 1:
                    poly = self._setUnitSquarePolygon()
                    self.__faciesPolygons.append(poly)
                else:
                    poly = self.__setZeroPolygon()
                    self.__faciesPolygons.append(poly)

        polygons = copy.copy(self.__faciesPolygons)

        return polygons

    def faciesIndxPerPolygon(self):
        faciesIndxPerPoly = copy.copy(self.__faciesIndxPerPolygon)
        return faciesIndxPerPoly

    def setAngle(self, polygonNumber, angle):
        err = 0
        if not self.__useConstTruncModelParam:
            err = 1
        else:
            if angle < -180.0:
                angle = angle + 360.0
            if angle > 180.0:
                angle = angle - 360.0
            self.__faciesBoundaryOrientation[polygonNumber] = angle
            item = self.__probFracPerPolygon[polygonNumber]
            indx = item[0]
            fName = self._faciesInTruncRule[indx]
            if self._debug_level >= Debug.VERY_VERBOSE:
                text = 'Debug output: Set new angle for polygon number: ' + str(polygonNumber)
                text = text + ' with facies ' + fName + ' : ' + str(angle)
                print(text)
        return err

    def setAngleTrend(self, polygonNumber, angleParamName):
        if self.__useConstTruncModelParam:
            raise ValueError("Error: Using a constant truncation model is incompatible with setting an angle trend.")
        else:
            item = self.__probFracPerPolygon[polygonNumber]
            indx = item[0]
            fName = self._faciesInTruncRule[indx]
            self.__faciesBoundaryOrientationName[polygonNumber] = [fName, angleParamName]
            if self._debug_level >= Debug.VERY_VERBOSE:
                text = 'Debug output: Set new angle trend for polygon number: ' + str(polygonNumber)
                text = text + ' with facies ' + fName + ' : ' + angleParamName
                print(text)

    def setUseTrendForAngles(self, useConstTrend):
        if useConstTrend == 1:
            if not self.__useConstTruncModelParam:
                self.__faciesBoundaryOrientationName = []
                self.__faciesBoundaryOrientation = []
                # set default values of faciesAlpha
                for i in range(self.__nPolygons):
                    self.__faciesBoundaryOrientation.append(0.0)
                self.__useConstTruncModelParam = True
        else:
            if self.__useConstTruncModelParam:
                self.__faciesBoundaryOrientationName = []
                self.__faciesBoundaryOrientation = []
                # set default values of faciesAlphaName
                for i in range(self.__nPolygons):
                    self.__faciesBoundaryOrientationName.append([' ', ' '])
                self.__useConstTruncModelParam = False

    def XMLAddElement(self, parent):
        """
        Description:
         Add to the parent element a new element with specified tag and attributes.
         The attributes are a dictionary with {name:value}
         After this function is called, the parent element has got a new child element
         for the current class.
        """
        if self._debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: call XMLADDElement from ' + self._className)

        nGF = self._nGaussFieldsInTruncationRule
        attribute = {
            'name': 'Trunc2D_Angle',
            'nGFields': str(nGF)
        }
        tag = 'TruncationRule'
        trRuleElement = Element(tag, attribute)
        # Put the xml commands for this truncation rule as the last child for the parent element
        parent.append(trRuleElement)

        tag = 'BackGroundModel'
        bgModelElement = Element(tag)
        trRuleElement.append(bgModelElement)

        tag = 'AlphaFields'
        alphaFieldsElement = Element(tag)
        alphaIndx1 = self._alphaIndxList[0]
        gfName1 = self._gaussFieldsInZone[alphaIndx1]
        alphaIndx2 = self._alphaIndxList[1]
        gfName2 = self._gaussFieldsInZone[alphaIndx2]
        alphaFieldsElement.text = ' ' + gfName1 + ' ' + gfName2 + ' '
        bgModelElement.append(alphaFieldsElement)

        tag = 'UseConstTruncParam'
        useConstElement = Element(tag)
        if self.__useConstTruncModelParam:
            useConstElement.text = ' 1 '
        else:
            useConstElement.text = ' 0 '
        bgModelElement.append(useConstElement)

        for k in range(self.__nPolygons):
            item = self.__probFracPerPolygon[k]
            indx = item[0]
            probFrac = item[1]
            fName = self._faciesInTruncRule[indx]

            tag = 'Facies'
            attribute = {'name': fName}
            fElement = Element(tag, attribute)

            tag = 'Angle'
            angleElement = Element(tag)
            if self.__useConstTruncModelParam:
                angleElement.text = ' ' + str(self.__faciesBoundaryOrientation[k]) + ' '
            else:
                item = self.__faciesBoundaryOrientationName[k]
                angleParamName = copy.copy(item[1])
                angleElement.text = ' ' + angleParamName + ' '
            fElement.append(angleElement)

            tag = 'ProbFrac'
            probFracElement = Element(tag)
            probFracElement.text = ' ' + str(probFrac) + ' '
            fElement.append(probFracElement)

            bgModelElement.append(fElement)

        # Read overlay facies keywords
        super()._XMLAddElement(trRuleElement)

    def writeContentsInDataStructure(self):
        # Write common contents from base class
        super().writeContentsInDataStructure()

        print(' ')
        print('************  Contents specific to the "Angle algorithm" *****************')
        print('Orientation angles for normal vectors for facies polygon border lines in truncation map:')
        if not self._setTruncRuleIsCalled:
            print('Truncation rule polygons are not calculated yet')
            return

        print('Number of polygons: ' + str(self.__nPolygons))
        if self.__useConstTruncModelParam:
            for i in range(self.__nPolygons):
                fAngle = self.__faciesBoundaryOrientation[i]
                indx = self.__faciesIndxPerPolygon[i]
                fName = self._faciesInTruncRule[indx]
                poly = self.__faciesPolygons[i]
                probFrac = self.__probFracPerPolygon[i][1]
                assert indx == self.__probFracPerPolygon[i][0]
                print('Polygon: {0} Angle: {1} Facies: {2} Prob frac: {3}'.format(str(i), str(fAngle), fName, probFrac))
                for j in range(len(poly)):
                    print(repr(poly[j]))
        else:
            for i in range(self.__nPolygons):
                fAngleParamName = self.__faciesBoundaryOrientationName[i]
                indx = self.__faciesIndxPerPolygon[i]
                fName = self._faciesInTruncRule[indx]
                poly = self.__faciesPolygons[i]
                probFrac = self.__probFracPerPolygon[i][1]
                assert indx == self.__probFracPerPolygon[i][0]
                print('Polygon: {0} Angle param name: {1} Facies: {2} Prob frac: {3}'.format(str(i), fAngleParamName,
                                                                                             fName, probFrac))
                for j in range(len(poly)):
                    print(repr(poly[j]))

        print('Facies index for polygons:')
        faciesIndxPerPoly = self.faciesIndxPerPolygon()
        print(repr(faciesIndxPerPoly))
