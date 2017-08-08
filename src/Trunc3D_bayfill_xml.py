#!/bin/env python
import sys
import copy
import numpy as np
import math

from APSMainFaciesTable import APSMainFaciesTable
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, dump
from utils.APSExceptions import InconsistencyError


# ------------ Truncation map for Bayfill ----------------------------------
#  Developed by: Kari Skjerve and Tone-Berit Ornskar
#  Date: 2016
#  Adapted to new data structure by: O.Lia
#  Date: 2017
#
# class Trunc3D_bayfill
# Description: This truncation rule was the first truncation rule developed in this project.
#              It was designed mainly for bayfill reservoirs and should be used with a
#              lateral trend for the first of the three gaussian fields.
#              The method use 5 facies. Documentation of the truncation rule is found in
#              document: APS_truncmap_bayfill_final.pdf with title:
#             "APS truncation map for bayfill version: April 2016 by Kari B. Skjerve with updates by O.Lia.
#             The method was documented in report:
#             "Test the Adaptive Plurigaussian Simulation method for facies modelling on Bay fill deposits"
#             by Tone Berit Ornskar and O.Lia (2016).
# --------------------------------------------------------------------------------------------
#
#  Public member functions specific for class Trunc3D_bayfill
#
#    Constructor:           __init__(trRuleXML=None, mainFaciesTable=None, faciesInZone=None,
#                                    printInfo = 0,modelFileName=None)
#
#    def initialize(self,mainFaciesTable,faciesInZone,faciesInTruncRule,
#                   sf_value, sf_name, ysf,sbhd, useConstTruncParam,printInfo)
#
#
#    --- Common get functions  for all Truncation classes ---
#    def getClassName(self)
#    def getFaciesOrderIndexList(self)
#    def getFaciesInTruncRule(self)
#    def getNGaussFieldsInModel(self)
#
#   --- Set functions ---
#    def setParamSF(self,paramName)
#    def setParamSFConst(self,value)
#    def setParamYSFConst(self,value)
#    def setParamSBHDConst(self,value)

#   --- Common functions for all Truncation classes ---
#    def useConstTruncModelParam(self)
#    def setTruncRule(self,faciesProb,cellIndx=0)
#    def defineFaciesByTruncRule(self,alphaCoord)
#    def truncMapPolygons(self)
#    def faciesIndxPerPolygon(self)
#    def XMLAddElement(self,parent)
#
#    --- Other get functions specific for this class ---
#    def getTruncationParam(self,get3DParamFunction,gridModel,realNumber)
#
#
#  Local functions
#
#    def __interpretXMLTree(self,,trRuleXML,mainFaciesTable,faciesInZone,printInfo,modelFileName)
#    def __checkFaciesForZone(self)
#    def __isInsidePolygon(self,polygon, xInput,yInput)
#    def __setUnitSquarePolygon(self)
#    def __setZeroPolygon(self)
#
# ----------------------------------------------------------------------------


class Trunc3D_bayfill:
    """
        Description: This class implements adaptive pluri-gaussian field
        trucation for the Bayfill model. (Three transformed gaussian fields)
    """
    def __setEmpty(self):
        # Global facies table
        self.__mainFaciesTable = None
        self.__nFaciesMain = 0

        # Facies to be modelled
        self.__faciesInZone = []
        self.__faciesCode = []
        self.__faciesInTruncRule = []
        self.__orderIndex = []
        self.__nFacies = 0

        self.__fIndxPerPolygon = [0, 1, 2, 3, 4]
        self.__printInfo = 0
        self.__className = 'Trunc3D_Bayfill'

        # Internal data structure
        self.__param_sf = []
        self.__param_ysf = 0
        self.__param_sbhd = 0
        self.__param_sf_name = ''

        self.__setTruncRuleIsCalled = False
        self.__polygons = []
        self.__useZ = 0
        self.__Zm = 0

        # Tolerance used for probabilities
        self.__eps = 0.001
        self.__faciesIsDetermined = []

        # Define if truncation parameters are constant for all grid cells or
        # vary from cell to cell.
        self.__useConstTruncModelParam = True

    def __init__(self, trRuleXML=None, mainFaciesTable=None, faciesInZone=None, nGaussFieldInModel=None,
                 printInfo=0, modelFileName=None):
        """
           Description: Create either an empty object which have to be initialized
                        later using the initialize function or create a full object
                        by reading the values from an input XML tree representing the
                        model file input.
        Data organization:
        There are three facies lists:
        1. mainFaciesTable.
           Main facies list which is common for all zones, All other facies lists must check
           against the main facies list that the facies is defined. Main facies list also contain
           the facies code for each facies.

        2. faciesInZone.
           For each zone there is a specific subset of facies that is modelled. For each of these
           facies a probability is specified. This list is must be consistent with the facies
           used in the truncation rule.

        3. faciesInTrucRule.
           The truncation rule specify the facies in a particular sequence. This sequence define the facies
           ordering and neigbourhood relation between the facies.
        """

        #assert trRuleXML is not None
        if trRuleXML is not None:
            # Require extactly 3 transformed gauss fields
            assert(nGaussFieldInModel == 3)
            self.__interpretXMLTree(trRuleXML, mainFaciesTable, faciesInZone, printInfo, modelFileName)
        else:
            if printInfo >= 3:
                # Create an empty object which will be initialized by set functions
                print('Debug info: Create empty object of ' + self.__className)
        #  End of __init__

    def __interpretXMLTree(self, trRuleXML, mainFaciesTable, faciesInZone, printInfo, modelFileName):
        # Initialize object from xml tree object trRuleXML
        # Reference to main facies table which is global for the whole model
        self.__setEmpty()
        self.__printInfo = printInfo
        if printInfo >= 3:
            print('Call Trunc3D_bayfill init')

        if mainFaciesTable is not None:
            self.__mainFaciesTable = mainFaciesTable
            self.__nFaciesMain = self.__mainFaciesTable.getNFacies()
        else:
            raise InconsistencyError(self.__class__.__name__)

        # Reference to facies in zone mode using this truncation rule
        if faciesInZone is not None:
            self.__faciesInZone = copy.copy(faciesInZone)
            self.__nFacies = len(self.__faciesInZone)
            self.__faciesIsDetermined = np.zeros(self.__nFacies, int)
        else:
            raise InconsistencyError(self.__className)

        if printInfo >= 3:
            print('Debug output: Call Trunc2D_B init')

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

        kw = 'Floodplain'
        fpObj = trRuleXML.find(kw)
        if fpObj is None:
            raise ValueError(
                'Error in {}\n'
                'Error: Floodplain facies is not specified.'
                ''.format(self.__className)
            )
        else:
            text = fpObj.text
            self.__faciesInTruncRule.append(text.strip())

        kw = 'Subbay'
        sbObj = trRuleXML.find(kw)
        if sbObj is None:
            raise ValueError(
                'Error in {}\n'
                'Error: Subbay facies is not specified.'
                ''.format(self.__className)
            )
        else:
            text = sbObj.text
            self.__faciesInTruncRule.append(text.strip())

        kw = 'WBF'
        wbfObj = trRuleXML.find(kw)
        if wbfObj is None:
            raise ValueError(
                'Error in {}\n'
                'Error: Wave influenced bayfill facies (WBF) is not specified.'
                ''.format(self.__className)
            )
        else:
            text = wbfObj.text
            self.__faciesInTruncRule.append(text.strip())

        kw = 'BHD'
        bhdObj = trRuleXML.find(kw)
        if bhdObj is None:
            raise ValueError(
                'Error in {}\n'
                'Error: Bayhead delta facies (BHD) is not specified.'
                ''.format(self.__className)
            )
        else:
            text = bhdObj.text
            self.__faciesInTruncRule.append(text.strip())

        kw = 'Lagoon'
        lgObj = trRuleXML.find(kw)
        if lgObj is None:
            raise ValueError(
                'Error in {}\n'
                'Error: Lagoon facies is not specified.'
                ''.format(self.__className)
            )
        else:
            text = lgObj.text
            self.__faciesInTruncRule.append(text.strip())

        kw = 'SF'
        SFObj = trRuleXML.find(kw)
        if SFObj is None:
            self.__param_sf = 0.0
            print(
                'Warning in {}\n'
                'Warning: Truncation parameter SF is not specified. Using default = {}'
                ''.format(self.__className, self.__param_sf)
            )
        else:
            text = SFObj.text
            if self.__useConstTruncModelParam:
                self.__param_sf = float(text.strip())
            else:
                self.__param_sf_name = copy.copy(text.strip())

        kw = 'YSF'
        YSFObj = trRuleXML.find(kw)
        if YSFObj is None:
            self.__param_ysf = 1.0
            print(
                'Warning in {}\n'
                'Warning: Truncation parameter YSF is not specified. Using default = {}'
                ''.format(self.__className, self.__param_ysf)
            )
        else:
            text = YSFObj.text
            self.__param_ysf = float(text.strip())

        kw = 'SBHD'
        SBHDObj = trRuleXML.find(kw)
        if SBHDObj is None:
            self.__param_sbhd = 0.0
            print(
                'Warning in {}\n'
                'Warning: Truncation parameter SBHD is not specified. Use default = {}'
                ''.format(self.__className, self.__param_sbhd)
            )
        else:
            text = SBHDObj.text
            self.__param_sbhd = float(text.strip())

        # Check that 5 facies is defined and find the orderIndex
        if self.__nFacies != 5:
            raise ValueError(
                'Error when reading model file: {}\n'
                'Error: Read truncation rule: {}\n'
                'Error: Different number of facies in truncation rule and in zone.'
                ''.format(modelFileName, self.__className)
            )

        # Check that specified facies is defined for the zone
        if not self.__checkFaciesForZone():
            raise ValueError(
                'Error when reading model file: {}\n'
                'Error: Mismatch between facies for truncation rule and facies for the zone.'
                ''.format(modelFileName)
            )

        for j in range(len(self.__faciesInTruncRule)):
            fName = self.__faciesInTruncRule[j]
            fIndx = -1
            for k in range(len(self.__faciesInZone)):
                fN = self.__faciesInZone[k]
                if fN == fName:
                    fIndx = k
                    break
            if fIndx < 0:
                raise ValueError('Error in Trunc3D_Bayfill.  Programming error.')
            self.__orderIndex.append(fIndx)

        if printInfo >= 3:
            print('Debug output: Facies names in truncation rule:')
            print(repr(self.__faciesInTruncRule))
            print('Debug output: Facies ordering:')
            print(repr(self.__orderIndex))
            print('Debug output: Facies code for facies in truncation rule')
            print(repr(self.__faciesCode))

    def initialize(self, mainFaciesTable, faciesInZone, faciesInTruncRule,
                   sf_value, sf_name, ysf, sbhd, useConstTruncParam, printInfo):
        """
           Description: Initialize the truncation object from input variables.
        """
        self.__setEmpty()
        
        # Main facies table i set
        self.__mainFaciesTable = copy.copy(mainFaciesTable)
        self.__nFaciesMain = self.__mainFaciesTable.getNFacies()

        # Facies in zone are set
        self.__faciesInZone = copy.copy(faciesInZone)


        # Facies in truncation rule
        self.__faciesInTruncRule = copy.copy(faciesInTruncRule)
        self.__nFacies = len(faciesInTruncRule)
        self.__faciesIsDetermined = np.zeros(self.__nFacies, int)

        # Facies code for facies in zone
        self.__faciesCode = []
        for fName in self.__faciesInZone:
            fCode = self.__mainFaciesTable.getFaciesCodeForFaciesName(fName)
            self.__faciesCode.append(fCode)

        self.__printInfo = printInfo

        # Set truncation parameters
        self.__useConstTruncModelParam = useConstTruncParam
        if self.__useConstTruncModelParam:
            self.__param_sf = sf_value
            self.__param_sf_name = ''
        else:
            self.__param_sf = 0
            self.__param_sf_name = copy.copy(sf_name)

        self.__param_ysf = float(ysf)
        self.__param_sbhd = float(sbhd)

        # Check that facies in truncation rule is consistent with facies in zone
        if not self.__checkFaciesForZone():
            raise ValueError(
                'Error: Mismatch between facies for truncation rule and facies for the zone.'
            )

        # Set orderIndex
        for j in range(len(self.__faciesInTruncRule)):
            fName = self.__faciesInTruncRule[j]
            fIndx = -1
            for k in range(len(self.__faciesInZone)):
                fN = self.__faciesInZone[k]
                if fN == fName:
                    fIndx = k
                    break
            if fIndx < 0:
                raise ValueError('Error in Trunc3D_bayfill.  Programming error.')
            self.__orderIndex.append(fIndx)

        return


    def writeContentsInDataStructure(self):
        print(' ')
        print('************  Contents of the data structure for class: ' + self.__className + ' ***************')
        print('Eps: ' + str(self.__eps))
        print('Main facies table:')
        print(repr(self.__mainFaciesTable))
        print('Number of facies in main facies table: ' + str(self.__nFaciesMain))
        print('Facies to be modelled: ')
        print(repr(self.__faciesInZone))
        print('Facies code per facies to be modelled:')
        print(repr(self.__faciesCode))
        print('Facies in truncation rule:')
        print(repr(self.__faciesInTruncRule))
        print('Number of facies to be modelled:' + str(self.__nFacies))
        print('Index array orderIndex: ')
        print(repr(self.__orderIndex))
        print('Facies index for facies which has 100% probability')
        print(repr(self.__faciesIsDetermined))
        print('Print info level: ' + str(self.__printInfo))
        print('Is function setTruncRule called? ')
        print(repr(self.__setTruncRuleIsCalled))
        print('Number of Gauss fields in model: ' + str(3))
        if self.__useConstTruncModelParam:
            print('Parameter SF: ' + str(self.__param_sf))
            print('Parameter YSF: ' + str(self.__param_ysf))
            print('Parameter SBHD: ' + str(self.__param_sbhd))
        else:
            print('Parameter SF: ' + self.__param_sf_name)
        print('UseZ: ' + str(self.__useZ))
        print('Zm: ' + str(self.__Zm))
        print('Number of polygons: ' + str(len(self.__polygons)))
        for i in range(len(self.__polygons)):
            poly = self.__polygons[i]
            print('Polygon number: ' + str(i))
            for j in range(len(poly)):
                print(repr(poly[j]))
        print('Facies index for polygons:')
        print(repr(self.__fIndxPerPolygon))




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
                        'Error: In truncation rule: {}'
                        'Error: Facies name {} which is defined for the current'
                        ' zone is not defined in the truncation rule.\n'
                        'Error: Cannot have facies with specified probability that is not used in the truncation rule.\n'
                        ''.format(self.__className, fName)
                    )
            return True
        except ValueError as e:
            print(e)
            return False

    def getClassName(self):
        return copy.copy(self.__className)

    def getFaciesOrderIndexList(self):
        return copy.copy(self.__orderIndex)

    def getFaciesInTruncRule(self):
        return copy.copy(self.__faciesInTruncRule)

    def getNGaussFieldsInModel(self):
        return 3

    def useConstTruncModelParam(self):
        return self.__useConstTruncModelParam

    def truncMapPolygons(self):
        assert self.__setTruncRuleIsCalled
        isDetermined = 0
        for indx in range(len(self.__faciesInTruncRule)):
            if self.__faciesIsDetermined[indx] == 1:
                isDetermined = 1
                break
        if isDetermined == 1:
            self.__polygons = []
            for indx in range(len(self.__faciesInTruncRule)):
                if self.__faciesIsDetermined[indx] == 1:
                    poly = self.__setUnitSquarePolygon()
                    self.__polygons.append(poly)
                else:
                    poly = self.__setZeroPolygon()
                    self.__polygons.append(poly)

        polygons = copy.copy(self.__polygons)
        return [polygons]

    def getTruncationParam(self, get3DParamFunction, gridModel, realNumber):
        # Input: get3DParamFunction - Pointer to a function to read 3D parameter from RMS
        #        gridModel - Pointer to grid model in RMS

        # This function should only be called if the truncation parameter sf is to be spatially varying
        assert self.__useConstTruncModelParam
        
        # Read truncation parameters
        paramName = self.__param_sf_name
        if self.__printInfo >= 2:
            print('--- Use spatially varying truncation rule parameter SF for truncation rule: ' + self.__className)
            print('--- Read RMS parameter: ' + paramName)
        # Expect that the function points to the function:
        #  getContinuous3DParameterValues with input: (gridModel,paramName,realNumber,self.__printInfo)
        [values] = get3DParamFunction(gridModel, paramName, realNumber, self.__printInfo)
        self.__param_sf = values
        
    def faciesIndxPerPolygon(self):
        fIndxList = copy.copy(self.__fIndxPerPolygon)
        return fIndxList


    def XMLAddElement(self, parent):
        # Add to the parent element a new element with specified tag and attributes.
        # The attributes are a dictionary with {name:value}
        # After this function is called, the parent element has got a new child element
        # for the current class.
        attribute = {
            'name': 'Trunc3D_Bayfill',
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

        tag = 'Floodplain'
        obj = Element(tag)
        obj.text = ' ' + str(self.__faciesInTruncRule[0]) + ' '
        trRuleElement.append(obj)

        tag = 'Subbay'
        obj = Element(tag)
        obj.text = ' ' + str(self.__faciesInTruncRule[1]) + ' '
        trRuleElement.append(obj)

        tag = 'WBF'
        obj = Element(tag)
        obj.text = ' ' + str(self.__faciesInTruncRule[2]) + ' '
        trRuleElement.append(obj)

        tag = 'BHD'
        obj = Element(tag)
        obj.text = ' ' + str(self.__faciesInTruncRule[3]) + ' '
        trRuleElement.append(obj)

        tag = 'Lagoon'
        obj = Element(tag)
        obj.text = ' ' + str(self.__faciesInTruncRule[4]) + ' '
        trRuleElement.append(obj)

        tag = 'SF'
        obj = Element(tag)
        if self.__useConstTruncModelParam:
            obj.text = ' ' + str(self.__param_sf) + ' '
        else:
            obj.text = ' ' + self.__param_sf_name + ' '
        trRuleElement.append(obj)

        tag = 'YSF'
        obj = Element(tag)
        obj.text = ' ' + ' ' + str(self.__param_ysf) + ' '
        trRuleElement.append(obj)

        tag = 'SBHD'
        obj = Element(tag)
        obj.text = ' ' + ' ' + str(self.__param_sbhd) + ' '
        trRuleElement.append(obj)

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
        return

    def __setUnitSquarePolygon(self):
        """  Create a polygon for the unit square
        """
        poly = [[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]
        return poly

    def __setZeroPolygon(self):
        """ Create a small polygon
        """
        poly = [[0, 0], [0, 0.0001], [0.0001, 0.0001], [0, 0.0001], [0, 0]]
        return poly

    def setTruncRule(self, faciesProb, cellIndx=0):
        """setTruncRule: Calculate internal parameters and polygons that define the truncation rule.
           Input:  faciesProb - Probability for each facies.
           Model parameters:
                 sf  - Floodplain slant line. Bigger value=more slant
                 ysf - Define where subbay polygon in the truncation cube should start. Value 0 means that
                       Subbay is neighbour to Floodplain along the whole border between
                       Floodplain and other facies. Value 1 means that Subbay is neigbour to only the upper part,
                       but this also depends on facies probabilities.
                       Low value moves subbay closer to peat protrusion (and mouthbar).
                sbhd - Slant factor for BHD, low value means BHD are close to floodplain/subbay,
                       high value means BHD will be longer into the bay/WIB but slimmer. 0<sbhd<1
        """
        # Internally in this python code:
        #  Floodplain is 1 with probability P1
        #  Subbay     is 2 with probability P2
        #  WBF        is 3 with probability P3
        #  BHD        is 4 with probability P4
        #  Lagoon     is 5 with probability P5

        self.__setTruncRuleIsCalled = True
        self.__setMinimumFaciesProb(faciesProb)
        isDetermined = 0
        for indx in range(len(faciesProb)):
            fIndx = self.__orderIndex[indx]
            self.__faciesIsDetermined[indx] = 0
            if faciesProb[fIndx] > (1.0 - self.__eps):
                self.__faciesIsDetermined[indx] = 1
                isDetermined = 1
        if isDetermined == 1:
            return

        if self.__useConstTruncModelParam:
            sf = self.__param_sf
        else:
            sf = self.__param_sf[cellIndx]

        ysf = self.__param_ysf
        sbhd = self.__param_sbhd

        fIndx = self.__orderIndex[0]
        P1 = faciesProb[fIndx]

        fIndx = self.__orderIndex[1]
        P2 = faciesProb[fIndx]

        fIndx = self.__orderIndex[2]
        P3 = faciesProb[fIndx]

        fIndx = self.__orderIndex[3]
        P4 = faciesProb[fIndx]

        fIndx = self.__orderIndex[4]
        P5 = faciesProb[fIndx]
        if self.__printInfo >= 3 and cellIndx == 0:
            print('Debug output: P1,P2,P3,P4,P5: {} {} {} {} {}'.format(P1, P2, P3, P4, P5))
        if sbhd > 0.999:
            sbhd = 0.999
        elif sbhd < 0.001:
            sbhd = 0.001
        if sf < 0.0001:
            sf = 0.0001

        # Tolerance when comparing two float values
        eps = 0.0001
        YWIB = 1.0
        Ym = 0.0
        Ym2 = 0.0
        Xm = 0.0
        Xm2 = 0.0

        if P1 < 0.0 or P2 < 0.0 or P3 < 0.0 or P4 < 0.0 or P5 < 0.0:
            print(' Warning: Negative probabilities as input. Is set to 0.')
            if P1 < 0.0:
                P1 = 0.0
            if P2 < 0.0:
                P2 = 0.0
            if P3 < 0.0:
                P3 = 0.0
            if P4 < 0.0:
                P4 = 0.0
            if P5 < 0.0:
                P5 = 0.0

        if abs(P1) < eps:
            P1 = 0.0
        if abs(P2) < eps:
            P2 = 0.0
        if abs(P3) < eps:
            P3 = 0.0
        if abs(P4) < eps:
            P4 = 0.0
        if abs(P5) < eps:
            P5 = 0.0

        sumProb = P1 + P2 + P3 + P4 + P5
        if sumProb == 0.0:
            raise ValueError('Error: All input probabilites are <= 0.0')

        if sumProb > (1.0 + eps) or sumProb < (1.0 - eps):
            print(' Warning: Sum of input probabilities is not equal to 1.0')
            print('          Adjust all probabilities by normalizing the probabilities.')

        #   Very small adjustments if abs(sumProb) < eps
        P1 = P1 / sumProb
        P2 = P2 / sumProb
        P3 = P3 / sumProb
        P4 = P4 / sumProb
        P5 = P5 / sumProb

        # Compute limits for Floodplain, Subbay and Lagoon
        if P1 > 1 - sf / 2.0:
            fssit = 1
        elif P1 > sf / 2.0:
            if P2 > sf / 2.0:
                fssit = 2
            else:
                fssit = 3
        elif P1 + P2 > math.sqrt(2.0 * sf * P1):
            fssit = 4
        else:
            fssit = 0  # This will be set to either 5 or 6 later, depending on the value of X4

        if fssit == 1:
            YF2 = 1.0 - math.sqrt(2.0 / sf * (1.0 - P1))
            YF = 1.0
            X1 = 1.0 - sf * (1.0 - YF2)
            X2 = 1.0
            YL = 1.0 - math.sqrt(max([0, 1.0 - 2.0 * ((1.0 - 0.5 * YF2) * YF2 + P5 / sf)]))
            XL = 1.0 - sf * (YL - YF2)
            YS = YL + ysf * (1 - math.sqrt(2.0 * P2 / sf) - YL)
            YS2 = 1.0
            if YS < 1:
                X3 = X1 + 2.0 * P2 / (1.0 - YS)
            else:
                X3 = X1
            X4 = X2 - sf * (YS - YF2)
            if P3 < 0.5 * (X4 - X3) * (1.0 - YS):
                bhdsit = 4
            else:
                bhdsit = 3
        elif fssit == 2:
            YF = 1.0
            YF2 = 0.0
            X1 = P1 - 0.5 * sf
            X2 = P1 + 0.5 * sf
            X3 = P1 + P2
            X4 = X3
            YS = 0.0
            YS2 = 1.0
            XL = P1 + P2 + P3 + P4
            YL = 0.0
            bhdsit = 1
        elif fssit == 3:
            YF = 1.0
            YF2 = 0.0
            X1 = P1 - 0.5 * sf
            X2 = P1 + 0.5 * sf
            if P5 <= 1 - X2:
                XL = 1.0 - P5
                YL = 0.0
            else:
                YL = 1.0 - math.sqrt(max([0, 1.0 - (2.0 / sf) * (P5 - 1 + X2)]))
                XL = X2 - sf * YL
            YS = YL + ysf * (1 - math.sqrt(2.0 * P2 / sf) - YL)
            YS2 = 1
            if abs(P2) < eps:
                X3 = X1
            else:
                X3 = X1 + 2.0 * P2 / (1.0 - YS)
            X4 = X2 - sf * YS

            if P5 <= 1 - X2:
                if P3 < 0.5 * (X4 - X3) * (1.0 - YS):
                    bhdsit = 4
                else:
                    bhdsit = 2
            else:
                if P3 < 0.5 * (X4 - X3) * (1.0 - YS):
                    bhdsit = 6
                else:
                    bhdsit = 3

        elif fssit == 4:
            X1 = 0.0
            YF2 = 0.0
            YF = math.sqrt(2.0 * P1 / sf)
            X2 = sf * YF
            X3 = P1 + P2
            X4 = X3
            YS = 0.0
            YS2 = 1.0
            XL = P1 + P2 + P3 + P4
            YL = 0.0
            bhdsit = 1
        else:
            X1 = 0
            YF2 = 0
            YF = math.sqrt(2.0 * P1 / sf)
            X2 = sf * YF
            if P5 <= 1 - X2:
                XL = 1.0 - P5
                YL = 0.0
            else:
                YL = 1.0 - math.sqrt(max([0, 1.0 - (2.0 / sf) * (P5 - 1.0 + X2)]))
                XL = X2 - sf * YL
            YS = YL + ysf * (1 - math.sqrt(max([0, (1.0 - YF) * (1.0 - YF) + 2.0 * P2 / sf])) - YL)
            X4 = sf * (YF - YS)
            if P2 >= 0.5 * X4 * (1.0 - YF):  # fssit=5
                fssit = 5
                X3 = (2.0 * P2 - X4 * (1.0 - YF)) / (1.0 - YS)
                YS2 = 1.0
                if P5 <= 1 - X2:
                    if P3 < 0.5 * (X4 - X3) * (1.0 - YS):
                        bhdsit = 4
                    else:
                        bhdsit = 2
                else:
                    if P3 < 0.5 * (X4 - X3) * (1.0 - YS):
                        bhdsit = 6
                    else:
                        bhdsit = 3
            else:  # fssit=6
                fssit = 6
                YS2 = YF + 2.0 * P2 / X4
                X3 = 0
                if P5 <= 1 - X2:
                    if P3 < 0.5 * (X4 - X3) * (1.0 - YS):
                        bhdsit = 5
                    else:
                        bhdsit = 2
                else:
                    if P3 < 0.5 * (X4 - X3) * (1.0 - YS):
                        bhdsit = 6
                    else:
                        bhdsit = 3

        # Compute limits for Wave influenced bayfill and Bay head delta
        caseT = 0
        caseA = 0
        c = math.tan(0.5 * math.pi * sbhd)
        Amax = 0
        if c == 0:
            c = 0.00001
        if bhdsit > 1 and c < sf:
            c = sf + 0.00001

        if P4 == 0:
            Xm = X4
            Xm2 = X4
            Ym = 0.0
            Ym2 = 0.0
            Amax = 0
        elif P3 == 0:
            Xm = XL
            Xm2 = XL
            Ym = 1.0
            Ym2 = 1.0
            Amax = 0
        elif bhdsit == 1:
            Amax = XL - X4
            AmP4sqrt = math.sqrt(P4 * Amax)
            if Amax == 0:
                Xm = X4
                Xm2 = X4
                Ym = 0.0
                Ym2 = 0.0
            elif (XL - X4) / c <= 1.0:  # T1
                caseT = 1
                if AmP4sqrt <= 0.5 * (XL - X4) * (XL - X4) / c:  # AmP4sqrt<=A1
                    Ym = math.sqrt(2.0 * AmP4sqrt / c)
                    Ym2 = 0
                    Xm = X4 + c * Ym
                    Xm2 = X4
                    caseA = 1
                elif AmP4sqrt <= (XL - X4) - 0.5 * (XL - X4) * (XL - X4) / c:  # A1<AmP4sqrt<=A2
                    Ym = (AmP4sqrt - 0.5 * (XL - X4) * (XL - X4) / c + (XL - X4) * (XL - X4) / c) / (XL - X4)
                    Ym2 = Ym - (XL - X4) / c
                    Xm = XL
                    Xm2 = X4
                    caseA = 2
                else:  # A2<AmP4sqrt
                    Xm2 = XL - math.sqrt(max([0, 2.0 * c * ((XL - X4) - AmP4sqrt)]))
                    Xm = XL
                    Ym2 = 1.0 - (XL - Xm2) / c
                    Ym = 1.0
                    caseA = 3
            else:  # T2
                caseT = 2
                if AmP4sqrt <= 0.5 * c:  # AmP4sqrt<=A1
                    Ym = math.sqrt(2.0 * AmP4sqrt / c)
                    Ym2 = 0
                    Xm = X4 + c * Ym
                    Xm2 = X4
                    caseA = 1
                elif AmP4sqrt <= (XL - X4) - 0.5 * c:  # A1<AmP4sqrt<=A2
                    Xm2 = X4 + AmP4sqrt - 0.5 * c
                    Xm = Xm2 + c
                    Ym2 = 0.0
                    Ym = 1.0
                    caseA = 2
                else:  # A2<AmP4sqrt
                    Ym2 = 1.0 - math.sqrt(max([0, 2.0 * (XL - X4 - AmP4sqrt) / c]))
                    Ym = 1.0
                    Xm2 = XL - c * (1.0 - Ym2)
                    Xm = XL
                    caseA = 3
        elif bhdsit == 2:
            Amax = (XL - X4) - 0.5 * (X2 - X4) * YS
            AmP4sqrt = math.sqrt(P4 * Amax)
            if Amax == 0:
                Xm = X4
                Xm2 = X4
                Ym = 0.0
                Ym2 = 0.0
            elif (XL - X4) / c <= YS:  # T2
                caseT = 2
                if AmP4sqrt <= 0.5 * (XL - X2) * (XL - X2) / (c - sf):  # AmP4sqrt<=A1
                    Ym = math.sqrt(2.0 * AmP4sqrt / (c - sf))
                    Ym2 = 0.0
                    Xm = X2 + 2.0 * AmP4sqrt / Ym
                    Xm2 = Xm - c * Ym
                    caseA = 1
                # A1<AmP4sqrt<=A2
                elif AmP4sqrt <= (XL - X4) * YS - 0.5 * (XL - X4) * (XL - X4) / c - 0.5 * (X2 - X4) * YS:
                    Ym = math.sqrt(max([
                        0,
                        ((XL - X2) * (XL - X2) / (sf * sf)) + (c / (sf * (c - sf))) * ((XL - X2) * (XL - X2) / c + 2.0 * AmP4sqrt)
                    ])) - (XL - X2) / sf
                    Ym2 = (1.0 - sf / c) * Ym - (XL - X2) / c
                    Xm = XL
                    Xm2 = X2 - sf * Ym
                    caseA = 2
                # A2<AmP4sqrt<=A3
                elif AmP4sqrt <= (XL - X4) - 0.5 * (X2 - X4) * YS - 0.5 * (XL - X4) * (XL - X4) / c:
                    Ym2 = (AmP4sqrt + 0.5 * (X2 - X4) * YS - 0.5 * (XL - X4) * (XL - X4) / c) / (XL - X4)
                    Ym = Ym2 + (XL - X4) / c
                    Xm = XL
                    Xm2 = X4
                    caseA = 3
                else:  # A3<AmP4sqrt
                    Ym2 = 1.0 - math.sqrt(max([0, (2.0 / c) * (XL - X4 - 0.5 * (X2 - X4) * YS - AmP4sqrt)]))
                    Ym = 1.0
                    Xm = XL
                    Xm2 = XL - c * (1.0 - Ym2)
                    caseA = 4
            elif (XL - X4) / c >= 1:  # T3
                caseT = 3
                # AmP4sqrt<=A1
                if AmP4sqrt <= 0.5 * c * YS * YS - 0.5 * (X2 - X4) * YS:
                    Ym = math.sqrt(2.0 * AmP4sqrt / (c - sf))
                    Ym2 = 0.0
                    Xm = X2 + 2.0 * AmP4sqrt / Ym
                    Xm2 = Xm - c * Ym
                    caseA = 1
                # A1<AmP4sqrt<=A2
                elif AmP4sqrt <= 0.5 * c - 0.5 * (X2 - X4) * YS:
                    Ym = math.sqrt(2.0 * (AmP4sqrt + 0.5 * (X2 - X4) * YS) / c)
                    Ym2 = 0.0
                    Xm = X4 + c * Ym
                    Xm2 = X4
                    caseA = 2
                # A2<AmP4sqrt<=A3
                elif AmP4sqrt <= 0.5 * c - 0.5 * (X2 - X4) * YS + (XL - X4 - c):
                    Xm = AmP4sqrt - (0.5 * c - 0.5 * (X2 - X4) * YS) + X4 + c
                    Xm2 = Xm - c
                    Ym = 1.0
                    Ym2 = 0.0
                    caseA = 3
                else:  # A3<AmP4sqrt
                    Ym2 = 1.0 - math.sqrt(max([0, (2.0 / c) * (XL - X4 - 0.5 * (X2 - X4) * YS - AmP4sqrt)]))
                    Ym = 1.0
                    Xm = XL
                    Xm2 = XL - c * (1.0 - Ym2)
                    caseA = 4
            else:  # T1
                caseT = 1
                # AmP4sqrt<=A1
                if AmP4sqrt <= 0.5 * c * YS * YS - 0.5 * (X2 - X4) * YS:
                    Ym = math.sqrt(2.0 * AmP4sqrt / (c - sf))
                    Ym2 = 0.0
                    Xm = X2 + 2.0 * AmP4sqrt / Ym
                    Xm2 = Xm - c * Ym
                    caseA = 1
                # A1<AmP4sqrt<=A2
                elif AmP4sqrt <= (0.5 / c) * (XL - X4) * (XL - X4) - 0.5 * (X2 - X4) * YS:
                    Ym = math.sqrt(2.0 * (AmP4sqrt + 0.5 * (X2 - X4) * YS) / c)
                    Ym2 = 0.0
                    Xm = X4 + c * Ym
                    Xm2 = X4
                    caseA = 2
                # A2<AmP4sqrt<=A3
                elif AmP4sqrt <= (0.5 / c) * (XL - X4) * (XL - X4) - 0.5 * (X2 - X4) * YS + (XL - X4) * (1.0 - (XL - X4) / c):
                    Ym2 = (AmP4sqrt + 0.5 * (X2 - X4) * YS - 0.5 *
                           (XL - X4) * (XL - X4) / c) / (XL - X4)
                    Ym = Ym2 + (XL - X4) / c
                    Xm = XL
                    Xm2 = X4
                    caseA = 3
                else:  # A3<AmP4sqrt
                    Ym2 = 1.0 - math.sqrt(max([0, (2.0 / c) * (XL - X4 - 0.5 * (X2 - X4) * YS - AmP4sqrt)]))
                    Ym = 1.0
                    Xm = XL
                    Xm2 = XL - c * (1.0 - Ym2)
                    caseA = 4
        elif bhdsit == 3:
            Amax = (XL - X4) * ((1.0 - YS) + 0.5 * (YS - YL))
            AmP4sqrt = math.sqrt(P4 * Amax)
            if AmP4sqrt <= 0.5 * (XL - X4) * (YS - YL - (XL - X4) / c):  # AmP4sqrt<=A1
                Ym = YL + math.sqrt(2.0 * AmP4sqrt / (sf * (1.0 - sf / c)))
                Xm2 = XL - sf * (Ym - YL)
                Ym2 = Ym - (XL - Xm2) / c
                Xm = XL
                caseA = 1
            # A1<AmP4sqrt<=A2
            elif AmP4sqrt <= 0.5 * (XL - X4) * (YS - YL - (XL - X4) / c) + (XL - X4) * (1.0 - YS):
                Ym = YS + (AmP4sqrt - 0.5 * (XL - X4) * (YS - YL - (XL - X4) / c)) / (XL - X4)
                Ym2 = Ym - (XL - X4) / c
                Xm = XL
                Xm2 = X4
                caseA = 2
            else:  # A2<AmP4sqrt
                Ym2 = 1.0 - math.sqrt(max([0, 2.0 / c * (Amax - AmP4sqrt)]))
                Ym = 1.0
                Xm = XL
                Xm2 = XL - c * (1.0 - Ym2)
                caseA = 3
        elif bhdsit == 4:
            if P3 == 0.0:
                YWIB = YS + math.sqrt((YS2 - YS) * (YS2 - YS))
            else:
                YWIB = YS + math.sqrt(max([0, (YS2 - YS) * (YS2 - YS) - 2.0 * P3 * (YS2 - YS) / (X4 - X3)]))
        elif bhdsit == 5:
            if P3 < (X4 - X3) * (1.0 - YS2):
                YWIB = 1.0 - P3 / (X4 - X3)
            else:
                YWIB = YS + math.sqrt(2.0 * ((YS2 - YS) * (1.0 - 0.5 * (YS2 + YS)) - (YS2 - YS) / (X4 - X3) * P3))
        elif bhdsit == 6:
            YWIB = YS + math.sqrt(max([0, (1.0 - YS) * (1.0 - YS) - 2.0 * P3 * (1.0 - YS) / (X4 - X3)]))

        if Amax > 0:
            Zm = 1.0 - math.sqrt(P4 / Amax)
        else:
            Zm = 1.0

        if self.__printInfo >= 3 and cellIndx == 0:
            print('Internal variables in ' + self.__className + ' for cell index = ' + str(cellIndx) + ' :')
            print('FSsit= ' + str(fssit))
            print('BHDsit= ' + str(bhdsit))
            print('CaseT= ' + str(caseT))
            print('CaseA= ' + str(caseA))
            print('Sf=    ' + str(sf))
            print('Ysf=   ' + str(ysf))
            print('Sbhd=  ' + str(sbhd))
            print('c=     ' + str(c))
            print('-------------------')
            print('P1(Floodplain)=  ' + str(P1))
            print('P2(Subbay)    =  ' + str(P2))
            print('P3(WBF)       =  ' + str(P3))
            print('P4(BHD)       =  ' + str(P4))
            print('P5(Lagoon)    =  ' + str(P5))
            print('-------------------')
            print('X1=  ' + str(X1))
            print('X2=  ' + str(X2))
            print('X3=  ' + str(X3))
            print('X4=  ' + str(X4))
            print('XL=  ' + str(XL))
            print('YF=  ' + str(YF))
            print('YF2= ' + str(YF2))
            print('YL=  ' + str(YL))
            print('YS=  ' + str(YS))
            print('YS2= ' + str(YS2))
            print('Zm=  ' + str(Zm))
            print('-------------------')
            if(bhdsit < 4):
                print('Xm=  ' + str(Xm))
                print('Xm2= ' + str(Xm2))
                print('Ym=  ' + str(Ym))
                print('Ym2= ' + str(Ym2))
                print('Zm=  ' + str(Zm))
                if abs(Ym - Ym2) > eps:
                    print(' (Xm - Xm2)/(Ym-Ym2) = ' + str((Xm - Xm2) / (Ym - Ym2)))
                    print(' c =                   ' + str(c))
                else:
                    print(' (Xm - Xm2)/(Ym-Ym2)= ' + str(c))
                print('-------------------')
            if bhdsit >= 4:
                print('YWIB = ' + str(YWIB))

        # Truncation rule depends on 3rd field if bhdsit <= 3
        if bhdsit <= 3:
            useZ = 1
        else:
            useZ = 0

        # Calculate polygons for each facies in the plane defined by the first and second field
        polygons = []
        polyFP = []
        polySB = []
        polyLG = []
        polyBHD = []
        polyWBF = []

        # ------ Floodplain  and subbay   ------------

        # Area Floodplain
        A = 0.0
        if X1 > 0.0:
            A = A + X1 * 1.0
        if YF2 > 0.0:
            A = A + YF2 * 1.0
        if X1 > 0.0 and YF2 > 0.0:
            A = A - X1 * YF2
        A = A + (X2 - X1) * (YF - YF2) * 0.5
        FP_area = A

        # Area Subbay
        # TODO: A is always set / defined
        A = 0.0
        if fssit == 1 or fssit == 3:
            A = (X3 - X1) * (1.0 - YS) * 0.5
        elif fssit == 2:
            A = 0.5 * ((X3 - X1) + (X3 - X2)) * 1.0
        elif fssit == 4:
            A = 0.5 * ((X3 - X1) + (X3 - X2)) * YF
            A = A + (X3 - X1) * (1.0 - YF)
        elif fssit == 5:
            A = 0.5 * ((1.0 - YF) + (1.0 - YS)) * (X4 - X1)
            A = A - (X4 - X3) * (1.0 - YS) * 0.5
        else:
            A = (YS2 - YF) * X4 * 0.5
        SB_area = A

        if fssit == 1:
            # polygon = Polygon([(0.0,0.0),(1.0,0.0),(X2,YF2),(X1,YF),(0.0,YF)],True) #FP
            polyFP.extend([
                [0.0, 0.0],
                [1.0, 0.0],
                [X2, YF2],
                [X1, YF],
                [0.0, YF],
                [0.0, 0.0]
            ])
            polygons.append(polyFP)

            # polygon = Polygon([(X4,YS),(X3,YF),(X1,YF)],True) #SB
            polySB.extend([
                [X4, YS],
                [X3, YF],
                [X1, YF],
                [X4, YS]
            ])
            polygons.append(polySB)

        elif fssit == 2:
            # polygon = Polygon([(0.0,0.0),(X2,YS),(X1,YF),(0.0,YF)],True) #FP
            polyFP.extend([
                [0.0, 0.0],
                [X2, YS],
                [X1, YF],
                [0.0, YF],
                [0.0, 0.0]
            ])
            polygons.append(polyFP)

            # polygon = Polygon([(X4,YS),(X3,YF),(X1,YF),(X2,YS)],True) #SB
            polySB.extend([
                [X4, YS],
                [X3, YF],
                [X1, YF],
                [X2, YS],
                [X4, YS]
            ])
            polygons.append(polySB)

        elif fssit == 3:
            # polygon = Polygon([(0.0,0.0),(X2,YF2),(X1,YF),(0.0,YF)],True) #FP
            polyFP.extend([
                [0.0, 0.0],
                [X2, YF2],
                [X1, YF],
                [0.0, YF],
                [0.0, 0.0]
            ])
            polygons.append(polyFP)

            # polygon = Polygon([(X4,YS),(X3,YF),(X1,YF)],True) #SB
            polySB.extend([
                [X4, YS],
                [X3, YF],
                [X1, YF],
                [X4, YS]
            ])
            polygons.append(polySB)

        elif fssit == 4:
            # polygon = Polygon([(0.0,0.0),(X2,YS),(X1,YF)],True) #FP
            polyFP.extend([
                [0.0, 0.0],
                [X2, YS],
                [X1, YF],
                [0.0, 0.0]
            ])
            polygons.append(polyFP)

            # polygon = Polygon([(X4,YS),(X3,1.0),(X1,1.0),(X1,YF),(X2,YS)],True) #SB
            polySB.extend([
                [X4, YS],
                [X3, 1.0],
                [X1, 1.0],
                [X1, YF],
                [X2, YS],
                [X4, YS]
            ])
            polygons.append(polySB)

        elif fssit == 5:
            # polygon = Polygon([(0.0,0.0),(X2,YF2),(X1,YF)],True) #FP
            polyFP.append([0.0, 0.0])
            polyFP.append([X2, YF2])
            polyFP.append([X1, YF])
            polyFP.append([0.0, 0.0])
            polygons.append(polyFP)

            # polygon = Polygon([(X4,YS),(X3,1.0),(X1,1.0),(X1,YF)],True) #SB
            polySB.extend([
                [X4, YS],
                [X3, 1.0],
                [X1, 1.0],
                [X1, YF],
                [X4, YS]
            ])
            polygons.append(polySB)

        else:
            # polygon = Polygon([(0.0,0.0),(X2,YF2),(X1,YF)],True) #FP
            polyFP.extend([
                [0.0, 0.0],
                [X2, YF2],
                [X1, YF],
                [0.0, 0.0]
            ])
            polygons.append(polyFP)

            # polygon = Polygon([(X4,YS),(X1,YS2),(X1,YF)],True) #SB
            polySB.extend([
                [X4, YS],
                [X1, YS2],
                [X1, YF],
                [X4, YS]
            ])
            polygons.append(polySB)

        # ------ Lagoon ------------------

        x1 = XL
        x2 = XL
        y1 = 1.0
        y2 = 0.0
        # Intersection between Floodplain line and Lagoon line
        if X2 >= XL:
            x2 = XL  # TODO: Unused
            y2 = (YF2 - YF) * (XL - X1) / (X2 - X1) + YF

        if bhdsit == 1:
            # polygon = Polygon([(1.0,0.0),(1.0,1.0),(XL,1.0),(XL,0.0)],True) #LG
            polyLG.extend([
                [1.0, 0.0],
                [1.0, 1.0],
                [XL, 1.0],
                [XL, 0.0],
                [1.0, 0.0]
            ])
            polygons.append(polyLG)

        else:
            if X2 > XL:
                # polygon = Polygon([(X2,YF2),(1.0,0.0),(1.0,1.0),(XL,1.0),(XL,y2)],True) #LG
                polyLG.extend([
                    [X2, YF2],
                    [1.0, 0.0],
                    [1.0, 1.0],
                    [XL, 1.0],
                    [XL, y2],
                    [X2, YF2]
                ])
                polygons.append(polyLG)

            else:
                # polygon = Polygon([(XL,0.0),(1.0,0.0),(1.0,1.0),(XL,1.0)],True) #LG
                polyLG.extend([
                    [XL, 0.0],
                    [1.0, 0.0],
                    [1.0, 1.0],
                    [XL, 1.0],
                    [XL, 0.0]
                ])
                polygons.append(polyLG)

        # Area Lagoon
        A = (1.0 - XL) * 1.0
        if YF2 > 0:
            A -= 0.5 * (YL - YF2) * (1.0 - XL)
            A -= YF2 * (1.0 - XL)
        else:
            A -= 0.5 * YL * (X2 - XL)

        LG_area = A

        # -----------  WBF  and   BHD ------------------

        # BHD polygons should be inserted into the list before Lagoon which is at the end of the list so far
        # WBF
        if bhdsit < 4:
            # TODO: Unused
            x1 = Xm2
            x2 = Xm
            y1 = Ym
            y2 = Ym2

            if bhdsit == 1:
                if Xm2 > X4:
                    # polygon = Polygon([(Xm,Ym2),(Xm2,Ym),(X4,1.0),(X4,0.0),(Xm,0.0)],True) #BHD
                    polyBHD.extend([
                        [Xm, Ym2],
                        [Xm2, Ym],
                        [X4, 1.0],
                        [X4, 0.0],
                        [Xm, 0.0],
                        [Xm, Ym2]
                    ])
                    polygons.insert(2, polyBHD)

                    # polygon = Polygon([(Xm,Ym2),(Xm2,Ym),(XL,1.0),(XL,Ym2)],True) #WBF
                    polyWBF.extend([
                        [Xm, Ym2],
                        [Xm2, Ym],
                        [XL, 1.0],
                        [XL, Ym2],
                        [Xm, Ym2]
                    ])
                    polygons.insert(2, polyWBF)

                else:
                    # polygon = Polygon([(Xm,Ym2),(Xm2,Ym),(Xm2,0.0),(Xm,0.0)],True) #BHD
                    polyBHD.extend([
                        [Xm, Ym2],
                        [Xm2, Ym],
                        [Xm2, 0.0],
                        [Xm, 0.0],
                        [Xm, Ym2]
                    ])
                    polygons.insert(2, polyBHD)

                    # polygon = Polygon([(Xm,Ym2),(Xm2,Ym),(Xm2,1.0),(XL,1.0),(XL,YL)],True) #WBF
                    polyWBF.extend([
                        [Xm, Ym2],
                        [Xm2, Ym],
                        [Xm2, 1.0],
                        [XL, 1.0],
                        [XL, YL],
                        [Xm, Ym2]
                    ])
                    polygons.insert(2, polyWBF)

            elif bhdsit == 2:
                if Xm2 > X4:
                    if Ym < YS:
                        # polygon = Polygon([(Xm,Ym2),(Xm2,Ym),(X2,0.0),(XL,0.0)],True) #BHD
                        polyBHD.extend([
                            [Xm, Ym2],
                            [Xm2, Ym],
                            [X2, 0.0],
                            [XL, 0.0],
                            [Xm, Ym2]
                        ])
                        polygons.insert(2, polyBHD)

                        # polygon =
                        # Polygon([(Xm,Ym2),(Xm2,Ym),(X4,YS),(X3,YS2),(X3,1.0),(X4,1.0),(XL,1.0),(XL,0.0)],True)
                        # #WBF
                        polyWBF.extend([
                            [Xm, Ym2],
                            [Xm2, Ym],
                            [X4, YS],
                            [X3, YS2],
                            [X3, 1.0],
                            [X4, 1.0],
                            [XL, 1.0],
                            [XL, 0.0],
                            [Xm, Ym2]
                        ])
                        polygons.insert(2, polyWBF)

                    elif Ym == 1.0:
                        # polygon =
                        # Polygon([(Xm,Ym2),(Xm2,Ym),(X4,1.0),(X4,YS),(X2,YF2),(XL,0.0)],True)
                        # #BHD
                        polyBHD.extend([
                            [Xm, Ym2],
                            [Xm2, Ym],
                            [X4, 1.0],
                            [X4, YS],
                            [X2, YF2],
                            [XL, 0.0],
                            [Xm, Ym2]
                        ])
                        polygons.insert(2, polyBHD)

                        # polygon =
                        # Polygon([(X4,1.0),(X3,1.0),(X3,YS2),(X4,YS),(X4,1.0),(Xm2,1.0),(XL,1.0),(XL,0.0),(Xm,Ym2),(Xm2,Ym)],False)
                        # #WBF
                        polyWBF.extend([
                            [X4, 1.0],
                            [X3, 1.0],
                            [X3, YS2],
                            [X4, YS],
                            [X4, 1.0],
                            [Xm2, 1.0],
                            [XL, 1.0],
                            [XL, 0.0],
                            [Xm, Ym2],
                            [Xm2, Ym],
                            [X4, 1.0]
                        ])
                        polygons.insert(2, polyWBF)
                else:
                    if Ym == 0.0 and Ym2 == 0.0:
                        # polygon = Polygon([(Xm,Ym2),(X4,Ym)],True) #BHD
                        polyBHD.extend([
                            [Xm, Ym2],
                            [X4, Ym],
                            [Xm, Ym2]
                        ])
                        polygons.insert(2, polyBHD)

                        # polygon =
                        # Polygon([(X4,YS),(X3,YS2),(X3,1.0),(X4,1.0),(XL,1.0),(XL,0.0),(X2,0.0)],True)
                        # #WBF
                        polyWBF.extend([
                            [X4, YS],
                            [X3, YS2],
                            [X3, 1.0],
                            [X4, 1.0],
                            [XL, 1.0],
                            [XL, 0.0],
                            [X2, 0.0],
                            [X4, YS]
                        ])
                        polygons.insert(2, polyWBF)

                    else:
                        # polygon = Polygon([(Xm,Ym2),(X4,Ym),(X4,YS),(X2,0.0),(Xm,0.0)],True) #BHD
                        polyBHD.extend([
                            [Xm, Ym2],
                            [X4, Ym],
                            [X4, YS],
                            [X2, 0.0],
                            [Xm, 0.0],
                            [Xm, Ym2]
                        ])
                        polygons.insert(2, polyBHD)

                        # polygon =
                        # Polygon([(Xm,Ym2),(X4,Ym),(X4,YS),(X3,YS2),(X3,1.0),(X4,1.0),(XL,1.0),(XL,0.0)],True)
                        # #WBF
                        polyWBF.extend([
                            [Xm, Ym2],
                            [X4, Ym],
                            [X4, YS],
                            [X3, YS2],
                            [X3, 1.0],
                            [X4, 1.0],
                            [XL, 1.0],
                            [XL, 0.0],
                            [Xm, Ym2]
                        ])
                        polygons.insert(2, polyWBF)

            elif bhdsit == 3:
                if Xm2 > X4:
                    if Ym < YS:
                        # polygon = Polygon([(Xm,Ym2),(Xm2,Ym),(XL,YL)],True) #BHD
                        polyBHD.extend([
                            [Xm, Ym2],
                            [Xm2, Ym],
                            [XL, YL],
                            [Xm, Ym2]
                        ])
                        polygons.insert(2, polyBHD)

                        # polygon =
                        # Polygon([(Xm,Ym2),(Xm2,Ym),(X4,YS),(X3,1.0),(X4,1.0),(XL,1.0),(XL,Ym2)],True)
                        # #WBF
                        polyWBF.extend([
                            [Xm, Ym2],
                            [Xm2, Ym],
                            [X4, YS],
                            [X3, 1.0],
                            [X4, 1.0],
                            [XL, 1.0],
                            [XL, Ym2],
                            [Xm, Ym2]
                        ])
                        polygons.insert(2, polyWBF)

                    elif Ym == 1.0:
                        # polygon = Polygon([(Xm,Ym2),(Xm2,Ym),(X4,1.0),(X4,YS),(XL,YL)],True) #BHD
                        polyBHD.extend([
                            [Xm, Ym2],
                            [Xm2, Ym],
                            [X4, 1.0],
                            [X4, YS],
                            [XL, YL],
                            [Xm, Ym2]
                        ])
                        polygons.insert(2, polyBHD)

                        # polygon =
                        # Polygon([(X4,1.0),(X3,1.0),(X4,YS),(X4,1.0),(Xm2,1.0),(XL,1.0),(Xm,Ym2),(Xm2,Ym)],False)
                        # #WBF
                        polyWBF.extend([
                            [X4, 1.0],
                            [X3, 1.0],
                            [X4, YS],
                            [X4, 1.0],
                            [Xm2, 1.0],
                            [XL, 1.0],
                            [Xm, Ym2],
                            [Xm2, Ym],
                            [X4, 1.0]
                        ])
                        polygons.insert(2, polyWBF)
                else:
                    # polygon = Polygon([(Xm,Ym2),(X4,Ym),(X4,YS),(XL,YL)],True) #BHD
                    polyBHD.extend([
                        [Xm, Ym2],
                        [X4, Ym],
                        [X4, YS],
                        [XL, YL],
                        [Xm, Ym2]
                    ])
                    polygons.insert(2, polyBHD)

                    # polygon = Polygon([(Xm,Ym2),(X4,Ym),(X4,YS),(X3,1.0),(X4,1.0),(XL,1.0)],True) #WBF
                    polyWBF.extend([
                        [Xm, Ym2],
                        [X4, Ym],
                        [X4, YS],
                        [X3, 1.0],
                        [X4, 1.0],
                        [XL, 1.0],
                        [Xm, Ym2]
                    ])
                    polygons.insert(2, polyWBF)

        else:
            # Subbay line
            x1 = X3
            x2 = X4
            y1 = YS2
            y2 = YS

            # Intersection between y = YWIB and the line for boundary between Subbay and WFB
            x2 = x1 + (YWIB - y1) * (x2 - x1) / (y2 - y1)
            x1 = X4
            y1 = YWIB
            y2 = YWIB

            if bhdsit == 4:
                if X2 > XL:
                    # polygon =
                    # Polygon([(X4,1.0),(X4,YWIB),(x2,YWIB),(X4,YS),(XL,YL),(XL,1.0)],True)
                    # #BHD
                    polyBHD.extend([
                        [X4, 1.0],
                        [X4, YWIB],
                        [x2, YWIB],
                        [X4, YS],
                        [XL, YL],
                        [XL, 1.0],
                        [X4, 1.0]
                    ])
                    polygons.insert(2, polyBHD)

                    # polygon = Polygon([(X4,1.0),(X4,YWIB),(x2,YWIB),(X3,YS2)],True) #WBF
                    polyWBF.extend([
                        [X4, 1.0],
                        [X4, YWIB],
                        [x2, YWIB],
                        [X3, YS2],
                        [X4, 1.0]
                    ])
                    polygons.insert(2, polyWBF)

                else:
                    # polygon =
                    # Polygon([(X4,1.0),(X4,YWIB),(x2,YWIB),(X4,YS),(X2,YF2),(XL,0.0),(XL,1.0)],True)
                    # #BHD
                    polyBHD.extend([
                        [X4, 1.0],
                        [X4, YWIB],
                        [x2, YWIB],
                        [X4, YS],
                        [X2, YF2],
                        [XL, 0.0],
                        [XL, 1.0],
                        [X4, 1.0]
                    ])
                    polygons.insert(2, polyBHD)

                    # polygon = Polygon([(X4,1.0),(X4,YWIB),(x2,YWIB),(X3,YS2)],True) #WBF
                    polyWBF.extend([
                        [X4, 1.0],
                        [X4, YWIB],
                        [x2, YWIB],
                        [X3, YS2],
                        [X4, 1.0]
                    ])
                    polygons.insert(2, polyWBF)

            if bhdsit == 5 or bhdsit == 6:
                if YWIB > YS2:
                    # polygon =
                    # Polygon([(X4,1.0),(X4,YWIB),(0.0,YWIB),(0.0,YS2),(X4,YS),(X2,YF2),(XL,YL),(XL,1.0)],True)
                    # #BHD
                    polyBHD.extend([
                        [X4, 1.0],
                        [X4, YWIB],
                        [0.0, YWIB],
                        [0.0, YS2],
                        [X4, YS],
                        [X2, YF2],
                        [XL, YL],
                        [XL, 1.0],
                        [X4, 1.0]
                    ])
                    polygons.insert(2, polyBHD)

                #                polygon = Polygon([(X4,1.0),(X4,YWIB),(0.0,YWIB),(0.0,1.0)],True) #WBF
                    polyWBF.extend([
                        [X4, 1.0],
                        [X4, YWIB],
                        [0.0, YWIB],
                        [0.0, 1.0],
                        [X4, 1.0]
                    ])
                    polygons.insert(2, polyWBF)

                else:
                    # polygon =
                    # Polygon([(X4,1.0),(X4,YWIB),(x2,YWIB),(X4,YS),(X2,YF2),(XL,YL),(XL,1.0)],True)
                    # #BHD
                    polyBHD.extend([
                        [X4, 1.0],
                        [X4, YWIB],
                        [x2, YWIB],
                        [X4, YS],
                        [X2, YF2],
                        [XL, YL],
                        [XL, 1.0],
                        [X4, 1.0]
                    ])
                    polygons.insert(2, polyBHD)

                    # polygon = Polygon([(X4,1.0),(X4,YWIB),(x2,YWIB),(X3,YS2),(X3,1.0)],True) #WBF
                    polyWBF.extend([
                        [X4, 1.0],
                        [X4, YWIB],
                        [x2, YWIB],
                        [X3, YS2],
                        [X3, 1.0],
                        [X4, 1.0]
                    ])
                    polygons.insert(2, polyWBF)

            x1 = X4
            x2 = X4
            y1 = 1.0
            y2 = YWIB

        # Area BHD and WBF
        WBF_area = 0.0
        BHD_vol = 0.0
        if bhdsit == 1:
            A = (Xm2 - X4) * 1.0
            A = A + 0.5 * (Ym2 + Ym) * (Xm - Xm2)
            BHD_vol = A * (1.0 - Zm)
            WBF_area = 1.0 - BHD_vol - LG_area - FP_area - SB_area
        elif bhdsit == 2:
            if Ym < YS:
                A = 0.5 * (Ym2 + Ym) * (Xm - Xm2) - 0.5 * (X2 - Xm2) * Ym
            elif Ym < 1.0:
                A = 0.5 * (Ym2 + Ym) * (Xm - Xm2) - 0.5 * (X2 - X4) * YS
            else:
                A = 0.5 * (Ym2 + 1.0) * (Xm - X4) + 0.5 * (Xm2 - X4) * (1.0 - Ym2) - 0.5 * (X2 - X4) * YS
            BHD_vol = A * (1.0 - Zm)
            WBF_area = 1.0 - BHD_vol - LG_area - FP_area - SB_area
        elif bhdsit == 3:
            A = 0.5 * (Ym + Ym2) * (Xm - Xm2)
            if Ym > YS:
                A = A - (YL + YS) * (Xm - Xm2) * 0.5
            else:
                A = A - (YL + Ym) * (Xm - Xm2) * 0.5
            BHD_vol = A * (1.0 - Zm)
            WBF_area = 1.0 - BHD_vol - LG_area - FP_area - SB_area
        elif bhdsit == 4:
            WBF_area = 0.5 * ((X4 - X3) * (YS2 - YS) - (X4 - X3) * (YWIB - YS) * (YWIB - YS) / (YS2 - YS))
            BHD_vol = 1.0 - WBF_area - LG_area - FP_area - SB_area
        elif bhdsit == 5:
            if P3 < (X4 - X3) * (1.0 - YS2):
                WBF_area = (X4 - X3) * (1.0 - YWIB)
                BHD_vol = 1.0 - WBF_area - LG_area - FP_area - SB_area
            else:
                WBF_area = (X4 - X3) * (1.0 - 0.5 * (YS2 + YS)) - 0.5 * (X4 - X3) * (YWIB - YS) * (YWIB - YS) / (YS2 - YS)
                BHD_vol = 1.0 - WBF_area - LG_area - FP_area - SB_area
        elif bhdsit == 6:
            WBF_area = 0.5 * ((X4 - X3) * (1.0 - YS) - (X4 - X3) * (YWIB - YS) * (YWIB - YS) / (1.0 - YS))
            BHD_vol = 1.0 - WBF_area - LG_area - FP_area - SB_area

        if self.__printInfo >= 3 and cellIndx == 0:
            print('Calculated probabilities for Bayfill truncation rule:')
            print('Prob FP = ' + str(FP_area))
            print('Prob SB = ' + str(SB_area))
            print('Prob WBF = ' + str(WBF_area))
            print('Prob BHD = ' + str(BHD_vol))
            print('Prob LG = ' + str(LG_area))
            print('-------------------')
            print('\n')
        self.__polygons = polygons
        self.__useZ = useZ
        self.__Zm = Zm

    def defineFaciesByTruncRule(self, alphaCoord):
        """defineFaciesByTruncRule: Calculate facies by applying the truncation rule.

           Input:
                      x,y,z      - The values of the uniformly distributed fields to be used.
           Output:    facies     - facies code.

           Internal variables to be used:
                     self.__polygons
                     self.__useZ
                     self.__Zm
        """
        x = alphaCoord[0]
        y = alphaCoord[1]
        z = alphaCoord[2]
        for indx in range(len(self.__faciesInTruncRule)):
            if self.__faciesIsDetermined[indx] == 1:
                fIndx = self.__orderIndex[indx]
                faciesCode = self.__faciesCode[fIndx]
                return [faciesCode, fIndx]

        faciesCode = -1
        indx = -1
        for i in range(len(self.__polygons)):
            polygon = self.__polygons[i]
            inside = self.__isInsidePolygon(polygon, x, y)
            if inside == 0:
                continue
            else:
                if i == 0 or i == 1 or i == 4:
                    # Facies is Floodplain, Subbay or Lagoon
                    indx = i
                elif i == 3:
                    # Facies is BHD or WBF
                    if self.__useZ:
                        if z >= self.__Zm:
                            # Facies is BHD
                            indx = 3
                        else:
                            # Facies is WBF
                            indx = 2
                    else:
                        indx = 3
                elif i == 2:
                    indx = 2
                break

        fIndx = self.__orderIndex[indx]
        faciesCode = self.__faciesCode[fIndx]

        return [faciesCode, fIndx]

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
        # TODO: Rewrite: check if not even
        if (nIntersectionsFound // 2) * 2 != nIntersectionsFound:
            # Point pt is inside the closed polygon
            return 1
        else:
            # Point pt is outside the closed polygon
            return 0

        # TODO: Unused!
        def setParamSFConst(self, value):
            if value < 0 or value > 1:
                raise ValueError("Error: The value must be between 0 and 1 (inclusive)")
            else:
                self.__sf = value

        def setParamSF(self, paramName):
            self.__param_sf = 0
            self.__param_sf_name = copy.copy(paramName)
            return

        def setParamYSFConst(self, value):
            if value < 0 or value > 1:
                raise ValueError("Error: The value must be between 0 and 1 (inclusive)")
            else:
                self.__ysf = value

        def setParamSBHDConst(self, value):
            if value < 0 or value > 1:
                raise ValueError("Error: The value must be between 0 and 1 (inclusive)")
            else:
                self.__sbhd = value
