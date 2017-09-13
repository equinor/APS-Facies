#!/bin/env python
from xml.etree.ElementTree import Element

import copy
import numpy as np


class Trunc2D_Angle_Overlay:
    """
    class Trunc2D_Angle_Overlay
    Description: This class implements adaptive plurigaussian field truncation using two simulated
                 gaussian fields (with trend).
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

     Member function with common name for all truncation type classes
       name                     =  getClassName()
       indexList                =  getFaciesOrderIndexList()
       faciesList               =  getFaciesInTruncRule()
       useConstTruncModelParam  =  useConstTruncModelParam()
                                   setTruncRule(faciesProb,cellIndx = 0)
       [faciesCode,fIndx]       =  defineFaciesByTruncRule(alphaCoord)
       [polygons]               =  truncMapPolygons()
                                   XMLAddElement(parent)

     Public member functions specific for class Trunc2D_Angle_Overlay

     Constructor:
                  __init__(self,trRuleXML=None, mainFaciesTable=None, faciesInZone=None,
                           printInfo = 0,modelFileName=None)

     def initialize(self,mainFaciesTable,faciesInZone,truncStructure,
                      backgroundFacies, overlayFacies, overlayTruncCenter,
                      useConstTruncParam,printInfo)

     getTruncationParam(gridModel,realNumber)
    --------------------------------------------------------

     Internal member functions specific for class Trunc2D_B
       isOK                =  __checkFaciesForZone()
        polygon            =  __setUnitSquarePolygon()
                              __setFaciesLines(cellIndx)
    [isSplit,outputPolyA, outputPolyB] = __subdividePolygonByLine(polygonPts, vx,vy,x0,y0)
       area                =  __polyArea(polygon)
      [smin,smax]          =  __findSminSmaxForPolygon(polygon,vx,vy,vxNormal,vyNormal,x0Normal,y0Normal)
      inside               =  __isInsidePolygon(polygon, xInput,yInput)
     [outputPolyA,outputPolyB,closestPolygon] = __defineIntersectionFromProb(self,polygon,vx,vy,
                                                           vxNormal,vyNormal,x0Normal,y0Normal,faciesProb)
    """

    def __init__(self, trRuleXML=None, mainFaciesTable=None, faciesInZone=None, nGaussFieldInModel=None,
                 printInfo=0, modelFileName=None):
        """
           Description: Create either an empty object which have to be initialized
                        later using the initialize function or create a full object
                        by reading the values from an input XML tree representing the
                        model file input.
        """
        # Data organization:
        # There are three facies lists:
        # 1. mainFaciesTable.
        #    Main facies list which is common for all zones, All other facies lists must check
        #    against the main facies list that the facies is defined. Main facies list also contain
        #    the facies code for each facies.
        #
        # 2. faciesInZone.
        #    For each zone there is a specific subset of facies that is modelled. For each of these
        #    facies a probability is specified. This list is must be consistent with the facies
        #    used in the truncation rule.
        #
        # 3. faciesInTrucRule.
        #    The truncation rule specify the facies in a particular sequence. This sequence define the facies
        #    ordering and neigbourhood relation between the facies.

        # Tolerance used for probabilities
        self.__eps = 0.001

        # Global facies table
        self.__mainFaciesTable = None
        self.__nFaciesMain = 0

        # Facies to be modelled
        self.__faciesInZone = []
        self.__faciesCode = []
        self.__faciesInTruncRule = []
        self.__nFacies = 0
        self.__orderIndex = []
        self.__faciesIsDetermined = []
        self.__printInfo = printInfo
        self.__className = 'Trunc2D_Angle_Overlay'

        self.__modelFileName = modelFileName

        # Variables containing truncations for the 2D truncation map
        # The input direction angles can be file names in case trend parameters for these are specified
        self.__faciesAlphaName = []

        # List of angles in case no trend of truncation parameter is used
        # and in case trend parameters are used for truncation parameters,
        # each element in the list is a 3D parameter with values.
        self.__faciesAlpha = []

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

        # Define if truncation parameter (angles) are constant for all grid cells or
        # vary from cell to cell.
        self.__useConstTruncModelParam = True
        self.__overLayTruncIntervalCenter = 0.0
        self.__isBackgroundFacies = None
        self.__backGroundFaciesIndx = []
        self.__overlayFaciesIndx = 0
        self.__useOverLay = 0
        self.__deltaH = 1.0
        self.__lowH = 0
        self.__highH = 1

        # assert trRuleXML is not None
        if trRuleXML is not None:
            # This method require exactly 3 transformed gauss fields
            assert (nGaussFieldInModel == 3)
            # Fill the object from an xml model file
            self.__interpretXMLTree(trRuleXML, mainFaciesTable, faciesInZone, printInfo, modelFileName)
        else:
            if self.__printInfo >= 3:
                # Create an empty object. The object will be initialized by set functions later
                print('Debug info: Create empty object of: ' + self.__className)

    def __interpretXMLTree(self, trRuleXML, mainFaciesTable, faciesInZone, printInfo, modelFileName):
        # Initialize object from xml tree object trRuleXML
        self.__printInfo = printInfo

        # Reference to main facies table which is global for the whole model
        if mainFaciesTable is not None:
            self.__mainFaciesTable = mainFaciesTable
            self.__nFaciesMain = self.__mainFaciesTable.getNFacies()
        else:
            raise ValueError(
                'Error in {}'
                'Error: Inconsistency.'
                ''.format(self.__className)
            )

        # Reference to facies in zone mode using this truncation rule
        if faciesInZone is not None:
            self.__faciesInZone = copy.copy(faciesInZone)
            self.__nFacies = len(self.__faciesInZone)
            self.__faciesIsDetermined = np.zeros(self.__nFacies, int)
        else:
            raise ValueError(
                'Error in {}\n'
                'Error: Inconsistency'
                ''.format(self.__className)
            )

        if self.__printInfo >= 3:
            print('Debug output: Call Trunc2D_Angle_Overlay init')

        # Facies code for facies in zone
        for fName in self.__faciesInZone:
            fCode = self.__mainFaciesTable.getFaciesCodeForFaciesName(fName)
            self.__faciesCode.append(fCode)

        # Get info from the XML model file tree for this truncation rule
        kw = 'UseConstTruncParam'
        useParamObj = trRuleXML.find(kw)
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
        for faciesObj in trRuleXML.findall(kw):
            if faciesObj is None:
                raise IOError(
                    'Error when reading model file: {}\n'
                    'Error: Read truncation rule: {}\n'
                    'Error: Missing keyword {} under keyword TruncationRule.'
                    ''.format(modelFileName, self.__className, kw)
                )
            fName = faciesObj.get('name')
            [nFacies, indx, fIndx, isNewFacies] = self.__addFaciesToTruncRule(fName)

            kw2 = 'Angle'
            # Input angle is anticlockwise rotation from first axis and in degrees.
            angleObj = faciesObj.find(kw2)
            if angleObj is None:
                raise IOError(
                    'Error when reading model file: {}\n'
                    'Error: Read truncation rule: {}\n'
                    'Error: Missing keyword {} under keyword Facies under keyword TruncationRule'
                    ''.format(modelFileName, self.__className, kw2)
                )
            text = angleObj.text
            if self.__useConstTruncModelParam:
                value = float(text.strip())
                self.__faciesAlpha.append(value)
            else:
                paramNameAlpha = copy.copy(text.strip())
                self.__faciesAlphaName.append([fName, paramNameAlpha])

            kw3 = 'ProbFrac'
            # Input prob fraction must be in interval [0,1] and for each facies this fraction must
            # sum up to 1.0 when summing over all polygons with the same facies.
            pFracObj = faciesObj.find(kw3)
            if pFracObj is None:
                raise IOError(
                    'Error when reading model file: {}\n'
                    'Error: Read truncation rule: {}\n'
                    'Error: Missing keyword {} under keyword Facies under keyword TruncationRule'
                    ''.format(modelFileName, self.__className, kw3)
                )
            probFrac = float(pFracObj.text)
            if probFrac < 0.0 or probFrac > 1.0:
                raise IOError(
                    'Error when reading model file: {}\n'
                    'Error: Read truncation rule: {}\n'
                    'Error: Probability fraction specified for {} in keyword {}\n'
                    ' under keyword Facies under keyword TruncationRule is: {} which is outside [0,1]'
                    ''.format(modelFileName, self.__className, fName, kw3, probFrac)
                )

            item = [indx, probFrac]

            probFracPerPolygon.append(item)
            nPolygons += 1
            if isNewFacies == 0:
                sumProbFrac[indx] += probFrac
            else:
                # New facies
                sumProbFrac.append(probFrac)
                self.__orderIndex.append(fIndx)
        # End read Facies

        kw = 'OverLayFacies'
        overLayObj = trRuleXML.find(kw)
        if overLayObj is not None:
            self.__useOverLay = 1
            text = overLayObj.get('name')
            fNameOverLayFacies = text.strip()
            if fNameOverLayFacies not in self.__faciesInZone:
                raise IOError(
                    'Error when reading model file: {}\n'
                    'Error: Read truncation rule: {}\n'
                    'Error: Specified facies name in truncation rule: {} is not defined for this zone.'
                    ''.format(modelFileName, self.__className, fNameOverLayFacies)
                )

            kw1 = 'TruncIntervalCenter'
            ticObj = overLayObj.find(kw1)
            if ticObj is not None:
                text = ticObj.text
                center = float(text.strip())
                if center < 0.0:
                    center = 0.0
                if center > 1.0:
                    center = 1.0
                self.__overLayTruncIntervalCenter = center

            kw2 = 'Background'
            self.__isBackgroundFacies = np.zeros(len(self.__faciesInZone), int)
            for bgObj in overLayObj.findall(kw2):
                text = bgObj.text
                bgFaciesName = text.strip()
                if fName not in self.__faciesInTruncRule:
                    raise IOError(
                        'Error when reading model file: {}\n'
                        'Error: Read truncation rule: {}\n'
                        'Error: Specified facies name as background facies in truncation rule: {} is not defined.'
                        ''.format(modelFileName, self.__className, bfFaciesIane)
                    )
                for i in range(len(self.__faciesInTruncRule)):
                    fN = self.__faciesInTruncRule[i]
                    if fN == bgFaciesName:
                        indx = i
                        break
                self.__backGroundFaciesIndx.append(indx)
                self.__isBackgroundFacies[indx] = 1

            [nFacies, indx, fIndx, isNewFacies] = self.__addFaciesToTruncRule(fNameOverLayFacies)
            if isNewFacies == 1:
                self.__overlayFaciesIndx = indx
                self.__orderIndex.append(fIndx)
            else:
                raise ValueError(
                    'Error in {}\n'
                    'Error: Specified overlay facies is already used as background facies.'
                    ''.format(self.__className)
                )
        else:
            raise ValueError(
                'Error in {}\n'
                'Error: Missing keyword {} in truncation rule.'
                ''.format(self.__className, kw)
            )
        self.__nFacies = nFacies
        # End read overlay facies

        self.__probFracPerPolygon = probFracPerPolygon
        self.__nPolygons = nPolygons

        # Check that specified facies is defined for the zone
        if len(self.__faciesInTruncRule) != self.__nFacies:
            raise IOError(
                'Error when reading model file: {}\n'
                'Error: Read truncation rule: {}\n'
                'Error: Different number of facies in truncation rule and in zone.'
                ''.format(modelFileName, self.__className)
            )
        elif not self.__checkFaciesForZone():
            raise IOError(
                'Error when reading model file: {}\n'
                'Error: Mismatch between facies for truncation rule and facies for the zone.'
                ''.format(modelFileName)
            )

        # Check that probability fractions summed over all polygons for each facies is 1.0
        for i in range(nFacies - 1):
            if self.__printInfo >= 3:
                fName = self.__faciesInTruncRule[i]
                print('Debug output: Sum prob frac for facies ' + fName + ' is: ' + str(sumProbFrac[i]))

            if abs(sumProbFrac[i] - 1.0) > 0.001:
                fName = self.__faciesInTruncRule[i]
                raise ValueError(
                    'Error in {}\n'
                    'Error: Sum of probability fractions over all polygons for facies {} is not 1.0\n'
                    'Error: The sum is: {}'
                    ''.format(self.__className, fName, sumProbFrac[i])
                )

        if self.__printInfo >= 3:
            print('Debug output: Facies names in truncation rule:')
            print(repr(self.__faciesInTruncRule))
            print('Debug output: Facies ordering:')
            print(repr(self.__orderIndex))
            print('Debug output: Facies code for facies in truncation rule')
            print(repr(self.__faciesCode))
            print('Debug output: Probability fractions for facies for each polygons in truncation rule')
            print(repr(self.__probFracPerPolygon))

    def __addFaciesToTruncRule(self, fName):
        found = 0
        isNew = 0
        nFaciesInTruncRule = len(self.__faciesInTruncRule)
        for i in range(nFaciesInTruncRule):
            fN = self.__faciesInTruncRule[i]
            if fN == fName:
                found = 1
                indx = i
                break
        if found == 0:
            self.__faciesInTruncRule.append(fName)
            indx = nFaciesInTruncRule
            nFaciesInTruncRule += 1
            isNew = 1
        fIndx = -999
        for j in range(self.__nFacies):
            fN = self.__faciesInZone[j]
            if fN == fName:
                fIndx = j
                break
        if fIndx == -999:
            raise ValueError(
                'Error in {}\n'
                'Error: Specified facies name in truncation rule is not defined for the zone.'
                ''.format(self.__className)
            )
        return [nFaciesInTruncRule, indx, fIndx, isNew]

    def initialize(self, mainFaciesTable, faciesInZone, truncStructure,
                   backgroundFacies, overlayFacies, overlayTruncCenter,
                   useConstTruncParam, printInfo):
        """
           Description: Initialize the truncation object from input variables.
        """
        self.__printInfo = printInfo
        self.__mainFaciesTable = copy.copy(
            mainFaciesTable)  # Main facies table
        self.__nFaciesMain = self.__mainFaciesTable.getNFacies()

        # Facies with defined probabilities for the zone
        self.__faciesInZone = copy.copy(faciesInZone)
        self.__nFacies = len(self.__faciesInZone)
        self.__faciesIsDetermined = np.zeros(self.__nFacies, int)

        # Facies code for facies in zone
        self.__faciesCode = []
        for fName in self.__faciesInZone:
            fCode = self.__mainFaciesTable.getFaciesCodeForFaciesName(fName)
            self.__faciesCode.append(fCode)

        self.__useConstTruncModelParam = useConstTruncParam
        self.__faciesAlphaName = []
        self.__faciesAlpha = []
        self.__probFracPerPolygon = []
        self.__nPolygons = 0
        # Set data structure for truncation rule
        # Loop over all polygons in truncation map
        for item in truncStructure:
            fName = item[0]
            probFrac = item[2]
            if self.__useConstTruncModelParam == 1:
                angle = float(item[1])
                self.__faciesAlpha.append(angle)
            else:
                angleTrendParamName = copy.copy(item[1])
                self.__faciesAlphaName.append(angleTrendParamName)

            [nFaciesInTruncRule, indx, fIndx, isNewFacies] = self.__addFaciesToTruncRule(fName)
            self.__probFracPerPolygon.append([indx, probFrac])
            if isNewFacies == 1:
                self.__orderIndex.append(fIndx)
            self.__nPolygons += 1

        # Check if overlay facies is to be used
        if len(backgroundFacies) > 0:
            self.__useOverLay = 1
            self.__overLayTruncIntervalCenter = overlayTruncCenter
            # Set data structure for background facies for the overlay facies
            self.__isBackgroundFacies = np.zeros(len(self.__faciesInZone), int)
            for bgFaciesName in backgroundFacies:
                for i in range(len(self.__faciesInTruncRule)):
                    fN = self.__faciesInTruncRule[i]
                    if fN == bgFaciesName:
                        indx = i
                        break

                self.__backGroundFaciesIndx.append(indx)
                self.__isBackgroundFacies[indx] = 1

            # Set data structure for overlay facies
            [nFaciesInTruncRule, indx, fIndx, isNewFacies] = self.__addFaciesToTruncRule(overlayFacies)
            if isNewFacies == 1:
                self.__overlayFaciesIndx = indx
                self.__orderIndex.append(fIndx)
            else:
                raise ValueError(
                    'Error in {}\n'
                    'Error: Wrong name of overlay facies. '
                    'This facies name is already used in truncation rule as a possible background facies.'
                    ''.format(self.__className)
                )
        # End if use overlay

        if not self.__checkFaciesForZone():
            raise ValueError(
                'Error when reading model file: {}\n'
                'Error: Mismatch between facies for truncation rule and facies for the zone.'
                ''.format(self.__modelFileName)
            )

    def getTruncationParam(self, get3DParamFunction, gridModel, realNumber):
        # Read truncation parameters
        self.__faciesAlpha = []
        if not self.__useConstTruncModelParam:
            for k in range(self.__nFacies):
                item = self.__faciesAlphaName[k]
                fName = item[0]
                paramName = item[1]
                # Check consistency
                if fName == self.__faciesInTruncRule[k]:
                    # Get param values
                    if self.__printInfo >= 2:
                        print('--- Get RMS parameter: ' + paramName + ' for facies ' + fName)
                    [values] = get3DParamFunction(
                        gridModel, paramName, realNumber, self.__printInfo)
                    #                    [values] = getContinuous3DParameterValues(gridModel,paramName,realNumber,self.__printInfo)
                    self.__faciesAlpha.append(values)
                else:
                    raise ValueError(
                        'Error in {}\n'
                        'Error: Inconsistency in data structure. Programming error.'
                        ''.format(self.__className)
                    )

    def __checkFaciesForZone(self):
        # Check that the facies for the truncation rule is the same
        # as defined for the zone with specified probabilities.
        try:
            for fName in self.__faciesInTruncRule:
                if fName not in self.__faciesInZone:
                    raise ValueError(
                        'Error: In truncation rule: {}\n'
                        'Error: Facies name {} is not defined for the current zone.\n'
                        'Error: No probability is defined for this facies for the current zone.\n'
                        ''.format(self.__className, fName)
                    )
            for fName in self.__faciesInZone:
                if fName not in self.__faciesInTruncRule:
                    raise ValueError(
                        'Error: In truncation rule: {}\n'
                        'Error: Facies name {} which is defined for the current zone'
                        ' is not defined in the truncation rule.\n'
                        'Error: Cannot have facies with specified probability that'
                        ' is not used in the truncation rule.\n'
                        ''.format(self.__className, fName)
                    )
            return True
        except ValueError as e:
            print(e)
            return False

    def __setUnitSquarePolygon(self):
        """ Function related to LBL (Linear Boundary Line) truncation rule.
        Create a polygon for the unit square
        """
        poly = [[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]
        return poly

    def __setZeroPolygon(self):
        """ Function related to LBL (Linear Boundary Line) truncation rule.
        Create a polygon for the unit square
        """
        poly = [[0, 0], [0, 0.0001], [0.0001, 0.0001], [0, 0.0001], [0, 0]]
        return poly

    def __setFaciesLines(self, cellIndx):
        """ Function related to the LBL (Linear Boundary Lines) truncation rule.
        Input: Facies names and direction angles
              (measured in anticlockwise direction relative to x-axis)
              for the normal to the facies boundary lines in the truncation map.

        Output: Arrays with direction  vector components for boundary lines
               (tangent vector components) (vx,vy).
               Arrays with normal vector components to boundary lines (vxnormal,vyNormal).
               A reference point for a line with the normal vector as its direction vector.
               The arrays have indices which are the same as facies number.
        """
        vxLine = []
        vyLine = []
        vxNormal = []
        vyNormal = []
        x0Normal = []
        y0Normal = []
        fNrLine = []
        #        print( 'i,alpha,vx,vy: ' + str(i) + ' ' + str(alpha) + ' ' + str(vx) + ' '  + str(vy))

        # Direction vectors [vx,vy] of normal to each facies border line
        # Direction vectors [vy,-vx] of facies border line  since dot product [vy,-vx]*[vx,vy] = 0
        # Lines are parameterized as:
        #    x(t) = x0 + vy*t
        #    y(t) = y0 - vx*t
        # The point (x0,y0) will vary and creates alternative parallell facies border lines

        # These lines are parameterized like:
        # for  0<= alpha < 90
        #    xref(s) = 0.0 + a1*vx*s
        #    yref(s) = 0.0 + a1*vy*s
        # for  90 <= alpha < 180
        #    xref(s) = 1.0 + a2*vx*s
        #    yref(s) = 0.0 + a2*vy*s
        # for  -90<= alpha < 0
        #    xref(s) = 0.0 + a3*vx*s
        #    yref(s) = 1.0 + a3*vy*s
        # for  -180 <= alpha < 90
        #    xref(s) = 1.0 + a4*vx*s
        #    yref(s) = 1.0 + a4*vy*s
        # where a1,a2,a3,a4 is defined such that when 0<= s <=1 the
        # line defined by
        #    x(t) = xref(s) + vy*t
        #    y(t) = yref(s) - vx*t
        # run through  (0,0) for s=0 and (1,1) for s=1 when 0<= alpha <= 90
        # run through  (1,0) for s=0 and (0,1) for s=1 when 0<= alpha <= 90
        # run through  (0,1) for s=0 and (1,0) for s=1 when -90<= alpha <= 0
        # run through  (1,1) for s=0 and (0,0) for s=1 when -180 <= alpha <= -90
        #

        faciesAlpha = []
        if self.__useConstTruncModelParam:
            faciesAlpha = self.__faciesAlpha
        else:
            for i in range(self.__nFacies):
                values = self.__faciesAlpha[i]
                faciesAlpha.append(values[cellIndx])

            #        for i in range(self.__nFacies):
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

    def __subdividePolygonByLine(self, polygonPts, vx, vy, x0, y0):
        """ Function related to the LBL (Linear Boundary Lines) truncation rule.
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
                #        print( 't,s: ' + str(t) + ' ' + str(s))
                #        print( 'intersection: ' + '(' + str(x) + ',' + str(y) + ')')
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

        return [isSplit, outputPolyA, outputPolyB]

    def __polyArea(self, polygon):
        """ Function related to the LBL (Linear Boundary Lines) truncation rule.
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

    def __findSminSmaxForPolygon(self, polygon, vx, vy, vxNormal, vyNormal, x0Normal, y0Normal):
        """ Function related to the LBL (Linear Boundary Lines) truncation rule.
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

        return [smin, smax]

    def __defineIntersectionFromProb(self, polygon, vx, vy, vxNormal, vyNormal, x0Normal, y0Normal, faciesProb):
        """ Function related to the LBL (Linear Boundary Lines) truncation rule.
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
        [smin, smax] = self.__findSminSmaxForPolygon(polygon, vx, vy, vxNormal, vyNormal, x0Normal, y0Normal)

        #    print( ' smin,smax: ' + str(smin) + ' '  + str(smax))
        sHigh = smax
        sLow = smin
        nmax = 15
        tolerance = 0.01
        tolerance2 = 0.02
        converged = 0
        closestPolygon = 0
        isSplit = 0
        for i in range(nmax):
            s = 0.5 * (sHigh + sLow)
            x0 = x0Normal + vxNormal * s
            y0 = y0Normal + vyNormal * s
            # Split polygon
            [isSplit, outputPolyA, outputPolyB] = self.__subdividePolygonByLine(polygon, vx, vy, x0, y0)
            if isSplit:
                #            print( ' Polygon A:')
                #            print( repr(outputPolyA))
                #            print( ' Polygon B:')
                #            print( repr(outputPolyB))
                [sminA, smaxA] = self.__findSminSmaxForPolygon(outputPolyA, vx, vy, vxNormal, vyNormal, x0Normal,
                                                               y0Normal)
                [sminB, smaxB] = self.__findSminSmaxForPolygon(outputPolyB, vx, vy, vxNormal, vyNormal, x0Normal,
                                                               y0Normal)
                #            print( ' sminA,smaxA: ' + str(sminA) + ' ' + str(smaxA))
                #            print( ' sminB,smaxB: ' + str(sminB) + ' ' + str(smaxB))
                # Find the polygon closest to (x0Normal,y0Normal)
                if smaxA < smaxB:
                    area = self.__polyArea(outputPolyA)
                    closestPolygon = 1
                else:
                    area = self.__polyArea(outputPolyB)
                    closestPolygon = 2

                    #            print( ' s,area: ' + str(s) + ' ' + str(area))

            else:
                raise ValueError(
                    'Error in {}\n'
                    'Error: When calculating a split of the polygon.'
                    ''.format(self.__className)
                )

            if np.abs(area - faciesProb) > tolerance:
                if area > faciesProb:
                    sHigh = s
                else:
                    sLow = s
                    continue
            else:
                converged = 1
                #            print( 'area, prob: ' + str(area) + ' '  + str(faciesProb))
                break

        # End for
        if converged == 0:
            print('area, prob: ' + str(area) + ' ' + str(faciesProb))
            if np.abs(area - faciesProb) > tolerance2:
                print('Not converged')
                print('area, prob: ' + str(area) + ' ' + str(faciesProb))

                print(repr(outputPolyA))
                print(repr(outputPolyB))
                print(' ')

        return [outputPolyA, outputPolyB, closestPolygon]

    def __isInsidePolygon(self, polygon, xInput, yInput):
        """ Function related to the LBL (Linear Boundary Lines) truncation rule.
            Take as input a polygon and a point and return 0 or 1 depending on
            whether the point is inside or outside of the polygon.
        """
        # Calculate intersection between a straight line through the input point pt and the closed polygon
        # in one direction from the point. If the number of intersections are odd number (1,3,5,..),
        # the point is inside, if the number of intersections are even (0,2,4,..) the point is outside.
        n = len(polygon)
        p = polygon[0]
        x1 = p[0]
        y1 = p[1]
        nIntersectionsFound = 0
        for i in range(1, n):
            x0 = x1
            y0 = y1
            p = polygon[i]
            x1 = p[0]
            y1 = p[1]
            vyp = y1 - y0
            vxp = x1 - x0
            if vyp != 0.0:
                s = (yInput - y0) / vyp
                x = x0 + s * vxp
                t = x - xInput
                if 0.0 <= s <= 1.0 and t > 0:
                    # intersection between the line y = pt[1] and the polygon line
                    # between the points polygon[i-1] and polygon[i] in one direction
                    # from the point pt
                    nIntersectionsFound += 1
        if (nIntersectionsFound // 2) * 2 != nIntersectionsFound:
            # Point pt is inside the closed polygon
            return 1
        else:
            # Point pt is outside the closed polygon
            return 0

    def __modifyBackgroundFaciesArea(self, faciesProb):
        sumProb = 0.0
        area = copy.copy(faciesProb)
        for i in range(len(self.__backGroundFaciesIndx)):
            indx = self.__backGroundFaciesIndx[i]
            fIndx = self.__orderIndex[indx]
            fProb = faciesProb[fIndx]
            if fProb < 0.0005:
                fProb = 0.0005
                area[fIndx] = fProb
            sumProb += fProb
        #            print('i,sumProb: ' + str(i) + ' ' + str(sumProb))
        fIndx = self.__orderIndex[self.__overlayFaciesIndx]
        overLayProb = faciesProb[fIndx]
        #        print('overLayProb: ' + str(overLayProb))

        sumTot = sumProb + overLayProb
        deltaH = 1.0
        lowAlpha = 0.0
        highAlpha = 0.0
        if sumTot > 0.0005:
            deltaH = sumProb / (sumTot)
            #            print('deltaH: ' + str(deltaH))
            for i in range(len(self.__backGroundFaciesIndx)):
                indx = self.__backGroundFaciesIndx[i]
                fIndx = self.__orderIndex[indx]
                p = area[fIndx]
                area[fIndx] = p / deltaH
            #                print('faciesProb, area: ' + str(p) + ' ' + str(area[fIndx]))
            lowAlpha = self.__overLayTruncIntervalCenter - 0.5 * (1.0 - deltaH)
            highAlpha = self.__overLayTruncIntervalCenter + 0.5 * (1.0 - deltaH)
            if lowAlpha < 0.0:
                lowAlpha = 0.0
                highAlpha = 1.0 - deltaH
            if highAlpha > 1.0:
                highAlpha = 1.0
                lowAlpha = deltaH

        return [area, deltaH, lowAlpha, highAlpha]

    def __setMinimumFaciesProb(self, faciesProb):
        sumProb = 0.0
        eps = self.__eps * 0.1
        for i in range(len(faciesProb)):
            p = faciesProb[i]
            if p < eps:
                p = eps
                faciesProb[i] = p
            if p >= 1.0:
                p = 1.0 - eps
                faciesProb[i] = p
            sumProb += p

        for i in range(len(faciesProb)):
            p = faciesProb[i]
            faciesProb[i] = p / sumProb
        return faciesProb

    def setTruncRule(self, faciesProb, cellIndx=0):
        """
        Function related to the LBL (Linear Boundary Lines) truncation rule.
        Input: Facies names, direction angles for facies boundary lines and facies probabilities.
        Output: A set of polygons that define the area for each facies
                within the truncation map for the LBL truncation.
        """
        faciesProb = self.__setMinimumFaciesProb(faciesProb)
        isDetermined = 0
        for indx in range(len(faciesProb)):
            fIndx = self.__orderIndex[indx]
            self.__faciesIsDetermined[indx] = 0
            if faciesProb[fIndx] > (1.0 - self.__eps):
                self.__faciesIsDetermined[indx] = 1
                isDetermined = 1
        if isDetermined == 1:
            return

        if self.__useOverLay == 1:
            [area, deltaH, lowH, highH] = self.__modifyBackgroundFaciesArea(faciesProb)
            self.__deltaH = deltaH
            self.__lowH = lowH
            self.__highH = highH
        #            print('deltaH: ' + str(deltaH))
        #            print('lowH: ' + str(lowH))
        #            print('highH: ' + str(highH))
        #            print('Facies prob:')
        #            print(repr(faciesProb))
        #            print('Adjusted area: ')
        #            print(repr(area))
        #            for i in range(len(faciesProb)-1):
        #                faciesProb[i] = area[i]

        self.__setFaciesLines(cellIndx)
        initialPolygon = self.__setUnitSquarePolygon()
        polygon = copy.copy(initialPolygon)
        #        nFacies = self.__nFacies
        nPolygons = self.__nPolygons
        faciesPolygons = []
        #        for i in range(nFacies-1):
        for i in range(nPolygons - 1):
            # print('i: '+ str(i))
            vx = self.__vxLine[i]
            vy = self.__vyLine[i]
            vxN = self.__vxNormal[i]
            vyN = self.__vyNormal[i]
            x0N = self.__x0Normal[i]
            y0N = self.__y0Normal[i]
            item = self.__probFracPerPolygon[i]
            # print('item: ' + repr(item))
            # print('orderIndex: ' + repr(self.__orderIndex))
            indx = item[0]
            probFrac = item[1]
            fIndx = self.__orderIndex[indx]
            fProb = area[fIndx] * probFrac

            [outPolyA, outPolyB, closestPolygon] = self.__defineIntersectionFromProb(polygon, vx, vy, vxN, vyN, x0N,
                                                                                     y0N, fProb)

            # Save facies polygons that are complete
            if closestPolygon == 1:
                #            print( ' Valgt polygon for facies nummer ' + str(i+1) + ': A' )
                faciesPolygons.append(outPolyA)
                if i == nPolygons - 2:
                    # add the last polygon to the last facies
                    faciesPolygons.append(outPolyB)

                polygon = outPolyB
            else:
                faciesPolygons.append(outPolyB)
                #            print( ' Valgt polygon for facies nummer ' + str(i+1) + ': B' )
                #                if i == nFacies-2:
                if i == nPolygons - 2:
                    # add the last polygon to the last facies
                    faciesPolygons.append(outPolyA)

                polygon = outPolyA
        self.__faciesPolygons = faciesPolygons

    #    def defineFaciesByTruncRule(self,x,y):
    #        """
    #        Function related to the LBL (Linear Boundary Lines) truncation rule.
    #        Input: polygons with definition of areas in the truncation map for each facies and a point in the truncation map.
    #        Output: Facies number for the facies in location (x,y) in the truncation map.
    #        """
    #        # Input is facies polygons for truncation rules and two values between 0 and 1
    #        # Check in which polygon the point is located and thereby the facies
    #        fIndx = -999
    #        print('Use overlay facies: No')
    #        for i in range(self.__nPolygons):
    #            polygon = self.__faciesPolygons[i]
    #            inside = self.__isInsidePolygon(polygon, x,y)
    #            if inside == 0:
    #                continue
    #            else:
    #                item = self.__probFracPerPolygon[i]
    #                indx = item[0]
    #                fIndx = self.__orderIndex[indx]
    #                faciesCode = self.__faciesCode[fIndx]
    #                break
    #        if fIndx == -999:
    #            print('Error: Point ('+ str(x) + ',' + str(y) + ')' + ' is not inside any polygon.')
    #
    #
    #        return [faciesCode,fIndx]

    def defineFaciesByTruncRule(self, alphaCoord):
        """
        Function related to the LBL (Linear Boundary Lines) truncation rule.
        Input: polygons with definition of areas in the truncation map for each facies and a point in the truncation map.
               Interval of allowed values for the third gaussian field for the overlay facies
               and which background facies to apply the overlay facies to.
        Output: Facies number for the facies in location (x,y,z) in the truncation map.
        """
        x = alphaCoord[0]
        y = alphaCoord[1]
        z = alphaCoord[2]
        # Check if facies is defined (has probability 1)
        for indx in range(len(self.__faciesInTruncRule)):
            if self.__faciesIsDetermined[indx] == 1:
                fIndx = self.__orderIndex[indx]
                faciesCode = self.__faciesCode[fIndx]
                return [faciesCode, fIndx]

        # Input is facies polygons for truncation rules and two values between 0 and 1
        # Check in which polygon the point is located and thereby the facies
        fIndx = -1
        if self.__useOverLay == 1:
            #            print('Use overlay facies: Yes')
            for i in range(self.__nPolygons):
                polygon = self.__faciesPolygons[i]
                inside = self.__isInsidePolygon(polygon, x, y)
                if inside == 0:
                    continue
                else:
                    # Check truncation of third GF
                    item = self.__probFracPerPolygon[i]
                    indx = item[0]
                    if self.__isBackgroundFacies[indx] == 1:
                        if self.__lowH < z < self.__highH:
                            indx = self.__overlayFaciesIndx
                    fIndx = self.__orderIndex[indx]
                    faciesCode = self.__faciesCode[fIndx]
                    break
        else:
            #            print('Use overlay facies: No')
            for i in range(self.__nPolygons):
                polygon = self.__faciesPolygons[i]
                inside = self.__isInsidePolygon(polygon, x, y)
                if inside == 0:
                    continue
                else:
                    item = self.__probFracPerPolygon[i]
                    indx = item[0]
                    fIndx = self.__orderIndex[indx]
                    faciesCode = self.__faciesCode[fIndx]
                    break
            if fIndx < 0:
                raise ValueError(
                    'Error: Point ({}, {}) is not inside any polygon.'.format(x, y)
                )

        return [faciesCode, fIndx]

    def getClassName(self):
        return copy.copy(self.__className)

    def getFaciesOrderIndexList(self):
        return copy.copy(self.__orderIndex)

    def getFaciesInTruncRule(self):
        return copy.copy(self.__faciesInTruncRule)

    def useConstTruncModelParam(self):
        return self.__useConstTruncModelParam

    def truncMapPolygons(self):
        isDetermined = 0
        for indx in range(len(self.__faciesInTruncRule)):
            if self.__faciesIsDetermined[indx] == 1:
                isDetermined = 1
                break
        if isDetermined == 1:
            self.__faciesPolygons = []
            for indx in range(len(self.__faciesInTruncRule)):
                if self.__faciesIsDetermined[indx] == 1:
                    poly = self.__setUnitSquarePolygon()
                    self.__faciesPolygons.append(poly)
                else:
                    poly = self.__setZeroPolygon()
                    self.__faciesPolygons.append(poly)

        polygons = copy.copy(self.__faciesPolygons)
        return [polygons]

    def faciesIndxPerPolygon(self):
        isDetermined = 0
        for indx in range(len(self.__faciesInTruncRule)):
            if self.__faciesIsDetermined[indx] == 1:
                isDetermined = 1
                break

        if isDetermined == 1:
            self.__faciesPolygons = []
            fIndxList = []
            for indx in range(len(self.__faciesInTruncRule)):
                if self.__faciesIsDetermined[indx] == 1:
                    poly = self.__setUnitSquarePolygon()
                    self.__faciesPolygons.append(poly)
                    fIndxList.append(indx)
                else:
                    poly = self.__setZeroPolygon()
                    self.__faciesPolygons.append(poly)
                    fIndxList.append(indx)
        else:
            fIndxList = []
            for i in range(self.__nPolygons):
                item = self.__probFracPerPolygon[i]
                indx = item[0]
                fIndxList.append(indx)
        return fIndxList

    def setAngle(self, polygonNumber, angle):
        err = 0
        if not self.__useConstTruncModelParam:
            err = 1
        else:
            if angle < -180.0:
                angle = angle + 360.0
            if angle > 180.0:
                angle = angle - 360.0
            self.__faciesAlpha[polygonNumber] = angle
            item = self.__probFracPerPolygon[polygonNumber]
            indx = item[0]
            fName = self.__faciesInTruncRule[indx]
            if self.__printInfo >= 3:
                text = 'Debug output: ' + \
                       'Set new angle for polygon number: ' + str(polygonNumber)
                text = text + ' with facies ' + fName + ' : ' + str(angle)
                print(text)
        return err

    def setAngleTrend(self, polygonNumber, angleParamName):
        if self.__useConstTruncModelParam:
            raise ValueError("Error: Using a constant truncation model is incompatible with setting an angle trend.")
        else:
            item = self.__probFracPerPolygon[polygonNumber]
            indx = item[0]
            fName = self.__faciesInTruncRule[indx]
            self.__faciesAlphaName[polygonNumber] = [fName, angleParamName]
            if self.__printInfo >= 3:
                text = 'Debug output: ' + 'Set new angle trend for polygon number: ' + str(polygonNumber)
                text = text + ' with facies ' + fName + ' : ' + str(angleParamName)
                print(text)

    def setUseTrendForAngles(self, useConstTrend):
        if useConstTrend == 1:
            if not self.__useConstTruncModelParam:
                self.__faciesAlphaName = []
                self.__faciesAlpha = []
                # set default values of faciesAlpha
                for i in range(self.__nPolygons):
                    self.__faciesAlpha.append(0.0)
                self.__useConstTruncModelParam = True
        else:
            if self.__useConstTruncModelParam:
                self.__faciesAlphaName = []
                self.__faciesAlpha = []
                # set default values of faciesAlphaName
                for i in range(self.__nPolygons):
                    self.__faciesAlphaName.append([' ', ' '])
                self.__useConstTruncModelParam = False

    def XMLAddElement(self, parent):
        # Add to the parent element a new element with specified tag and attributes.
        # The attributes are a dictionary with {name:value}
        # After this function is called, the parent element has got a new child element
        # for the current class.
        attribute = {
            'name': 'Trunc2D_Angle_Overlay',
            'nGFields': '3'
        }
        tag = 'TruncationRule'
        trRuleElement = Element(tag, attribute)
        # Put the xml commands for this truncation rule as the last child for the parent element
        parent.append(trRuleElement)
        tag = 'UseConstTruncParam'
        useConstElement = Element(tag)
        if self.__useConstTruncModelParam:
            useConstElement.text = '1'
        else:
            useConstElement.text = '0'
        trRuleElement.append(useConstElement)
        for k in range(self.__nPolygons):
            item = self.__probFracPerPolygon[k]
            indx = item[0]
            probFrac = item[1]
            fName = self.__faciesInTruncRule[indx]
            tag = 'Facies'
            attribute = {'name': fName}
            fElement = Element(tag, attribute)
            tag = 'Angle'
            angleElement = Element(tag)
            if self.__useConstTruncModelParam:
                angleElement.text = ' ' + str(self.__faciesAlpha[k]) + ' '
            else:
                item = self.__faciesAlphaName[k]
                angleParamName = copy.copy(item[1])
                angleElement.text = ' ' + angleParamName + ' '
            fElement.append(angleElement)

            tag = 'ProbFrac'
            probFracElement = Element(tag)
            probFracElement.text = ' ' + str(probFrac) + ' '
            fElement.append(probFracElement)
            trRuleElement.append(fElement)

        if self.__useOverLay == 1:
            indx = self.__overlayFaciesIndx
            fName = self.__faciesInTruncRule[indx]
            tag = 'OverLayFacies'
            attribute = {'name': fName}
            overLayElement = Element(tag, attribute)
            trRuleElement.append(overLayElement)
            tag = 'TruncIntervalCenter'
            ticElement = Element(tag)
            ticElement.text = ' ' + str(self.__overLayTruncIntervalCenter) + ' '
            overLayElement.append(ticElement)
            tag = 'Background'
            for i in range(len(self.__backGroundFaciesIndx)):
                indx = self.__backGroundFaciesIndx[i]
                fName = self.__faciesInTruncRule[indx]
                bElement = Element(tag)
                bElement.text = ' ' + fName + ' '
                overLayElement.append(bElement)

    def writeContentsInDataStructure(self):
        print(' ')
        print('************  Contents specific to the "Angle algorithm" *****************')
        print('Orientation angles for normal vectors for facies polygon border lines in truncation map:')
        for i in range(len(self.__faciesAlpha)):
            print(repr(self.__faciesAlpha))
        for i in range(len(self.__faciesAlphaName)):
            print(repr(self.__faciesAlphaName))

        print('Number of polygons: ' + str(self.__nPolygons))
        for i in range(len(self.__faciesPolygons)):
            poly = self.__faciesPolygons[i]
            print('Polygon number: ' + str(i))
            for j in range(len(poly)):
                print(repr(poly[j]))
        print('Prob frac per polygon: ')
        print(repr(self.__probFracPerPolygon))
        print('Facies index for polygons:')
        faciesIndxPerPoly = self.faciesIndxPerPolygon()
        print(repr(faciesIndxPerPoly))
