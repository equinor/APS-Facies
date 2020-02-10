#!/bin/env python
# -*- coding: utf-8 -*-
import copy
import math
import numpy as np
from warnings import warn
from xml.etree.ElementTree import Element

from src.algorithms.Trunc2D_Base_xml import Trunc2D_Base
from src.utils.constants.simple import Debug
from src.utils.xmlUtils import getKeyword, isFMUUpdatable, createFMUvariableNameForBayfillTruncation

"""
------------ Truncation map for Bayfill ----------------------------------
 Developed by: Kari Skjerve and Tone-Berit Ornskar
 Date: 2016
 Adapted to new data structure by: O.Lia
 Date: 2017

class Trunc3D_bayfill
Description: This truncation rule was the first truncation rule developed in this project.
             It was designed mainly for bayfill reservoirs and should be used with a
             lateral trend for the first of the three gaussian fields.
             The method use 5 facies. Documentation of the truncation rule is found in
             document: APS_truncmap_bayfill_final.pdf with title:
            "APS truncation map for bayfill version: April 2016 by Kari B. Skjerve with updates by O.Lia.
            The method was documented in report:
            "Test the Adaptive Plurigaussian Simulation method for facies modelling on Bay fill deposits"
            by Tone Berit Ornskar and O.Lia (2016).
--------------------------------------------------------------------------------------------

 Public member functions specific for class Trunc3D_bayfill

   Constructor:           __init__(trRuleXML=None, mainFaciesTable=None, faciesInZone=None,
                                   debug_level=Debug.OFF, modelFileName=None)

   def initialize(self,mainFaciesTable,faciesInZone,faciesInTruncRule,
                  sf_value, sf_name, ysf,sbhd, useConstTruncParam, debug_level=Debug.OFF)


   --- Common get functions  for all Truncation classes ---
   def getClassName(self)
   def getFaciesOrderIndexList(self)
   def getFaciesInTruncRule(self)
   def getNGaussFieldsInModel(self)
   def getUseZ(self)
   def getZTruncationValue(self)

  --- Set functions ---
   def setParamSF(self, paramName)
   def setParamSFConst(self, value)
   def setParamYSFConst(self, value)
   def setParamSBHDConst(self, value)

  --- Common functions for all Truncation classes ---
   def useConstTruncModelParam(self)
   def setTruncRule(self,faciesProb, cellIndx=0)
   def defineFaciesByTruncRule(self, alphaCoord)
   def truncMapPolygons(self)
   def faciesIndxPerPolygon(self)
   def XMLAddElement(self, parent)

   --- Other get functions specific for this class ---
   def getTruncationParam(self, get3DParamFunction, gridModel, realNumber)


 Local functions

   def __interpretXMLTree(self, trRuleXML, mainFaciesTable, faciesInZone, modelFileName, debug_level=Debug.OFF)
   def __checkFaciesForZone(self)
   def __isInsidePolygon(self,polygon, xInput,yInput)
   def __setUnitSquarePolygon(self)
   def __setZeroPolygon(self)

----------------------------------------------------------------------------
"""


class Trunc3D_bayfill(Trunc2D_Base):
    """
    This class implements adaptive pluri-gaussian field
    truncation for the Bayfill model. (Three transformed gaussian fields)
    """

    def __init__(self, trRuleXML=None, mainFaciesTable=None, faciesInZone=None, gaussFieldsInZone=None,
                 debug_level=Debug.OFF, modelFileName=None):
        """
        Create either an empty object which have to be initialized
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
        # Initialize data structure to empty if trRule is None and call up the base class function setEmpty as well.
        # If the trRule is not none, the base class data structure is initialized.
        super().__init__(
            trRuleXML, mainFaciesTable, faciesInZone, gaussFieldsInZone, debug_level, modelFileName,
            nGaussFieldsInBackGroundModel=3,
        )
        # Specific variables for class Trunc3D_bayfill
        self.__fIndxPerPolygon = np.arange(5, dtype=np.int32)

        # Internal data structure
        self.__param_sf = []
        self._is_param_sf_fmuupdatable = False
        self.__param_ysf = 0
        self._is_param_ysf_fmuupdatable = False
        self.__param_sbhd = 0
        self._is_param_sbhd_fmuupdatable = False
        self.__param_sf_name = ''

        self.__polygons = []
        self.__useZ = False
        self.__Zm = 0

        # Tolerance used for probabilities
        self.__eps = 0.5 * self._epsFaciesProb

        # Define if truncation parameters are constant for all grid cells or
        # vary from cell to cell.
        self.__useConstTruncModelParam = True

        if trRuleXML is not None:
            # Require exactly 3 transformed gauss fields
            nGaussFieldInZone = len(self._gaussFieldsInZone)
            assert nGaussFieldInZone >= 3
            self.__interpretXMLTree(trRuleXML[0], modelFileName)

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
                print('')
                print('Debug output: Gauss fields in zone:')
                print(repr(self._gaussFieldsInZone))
                print('Debug output: Gauss fields for each alpha coordinate:')
                for i in range(len(self._alphaIndxList)):
                    j = self._alphaIndxList[i]
                    gfName = self._gaussFieldsInZone[j]
                    print(' {} {}'.format(str(i + 1), gfName))

        else:
            if debug_level >= Debug.VERY_VERBOSE:
                # Create an empty object which will be initialized by set functions
                print('Debug output: Create empty object of ' + self._className)

    def __interpretXMLTree(self, trRuleXML, modelFileName):
        # Initialize object from xml tree object trRuleXML
        # Reference to main facies table which is global for the whole model
        if self._debug_level >= Debug.VERY_VERBOSE:
            print('Call Trunc3D_bayfill init')

        # Get info from the XML model file tree for this truncation rule
        # Keyword BackGroundModel
        bgmObj = getKeyword(trRuleXML, 'BackGroundModel', 'TruncationRule', modelFileName, required=True)

        kw = 'UseConstTruncParam'
        useParamObj = bgmObj.find(kw)
        if useParamObj is None:
            self.__useConstTruncModelParam = True
        else:
            text = useParamObj.text
            self.__useConstTruncModelParam = bool(text.strip())
        kw = 'Floodplain'
        fpObj = bgmObj.find(kw)
        if fpObj is None:
            raise ValueError(
                f'Error in {self._className}\n'
                f'Error: Floodplain facies is not specified.'
            )
        else:
            text = fpObj.text
            self._faciesInTruncRule.append(text.strip())

        kw = 'Subbay'
        sbObj = bgmObj.find(kw)
        if sbObj is None:
            raise ValueError(
                f'Error in {self._className}\n'
                f'Error: Subbay facies is not specified.'
            )
        else:
            text = sbObj.text
            self._faciesInTruncRule.append(text.strip())

        kw = 'WBF'
        wbfObj = bgmObj.find(kw)
        if wbfObj is None:
            raise ValueError(
                f'Error in {self._className}\n'
                f'Error: Wave influenced bayfill facies (WBF) is not specified.'
            )
        else:
            text = wbfObj.text
            self._faciesInTruncRule.append(text.strip())

        kw = 'BHD'
        bhdObj = bgmObj.find(kw)
        if bhdObj is None:
            raise ValueError(
                f'Error in {self._className}\n'
                f'Error: Bayhead delta facies (BHD) is not specified.'
            )
        else:
            text = bhdObj.text
            self._faciesInTruncRule.append(text.strip())

        kw = 'Lagoon'
        lgObj = bgmObj.find(kw)
        if lgObj is None:
            raise ValueError(
                f'Error in {self._className}\n'
                f'Error: Lagoon facies is not specified.'
            )
        else:
            text = lgObj.text
            self._faciesInTruncRule.append(text.strip())

        kw = 'SF'
        SFObj = bgmObj.find(kw)
        if SFObj is None:
            self.__param_sf = 0.0
            print(
                f'Warning in {self._className}\n'
                f'Warning: Truncation parameter SF is not specified. Using default = {self.__param_sf}'
            )
        else:
            text = SFObj.text
            if self.__useConstTruncModelParam:
                self.__param_sf = float(text.strip())
                self._is_param_sf_fmuupdatable = isFMUUpdatable(bgmObj, kw)
            else:
                self.__param_sf_name = text.strip()

        kw = 'YSF'
        YSFObj = bgmObj.find(kw)
        if YSFObj is None:
            self.__param_ysf = 1.0
            warn(
                f'Warning in {self._className}\n'
                f'Warning: Truncation parameter YSF is not specified. Using default = {self.__param_ysf}'
            )
        else:
            text = YSFObj.text
            self.__param_ysf = float(text.strip())
            self._is_param_ysf_fmuupdatable = isFMUUpdatable(bgmObj, kw)

        kw = 'SBHD'
        SBHDObj = bgmObj.find(kw)
        if SBHDObj is None:
            self.__param_sbhd = 0.0
            warn(
                f'Warning in {self._className}\n'
                f'Warning: Truncation parameter SBHD is not specified. Use default = {self.__param_sbhd}'
            )
        else:
            text = SBHDObj.text
            self.__param_sbhd = float(text.strip())
            self._is_param_sbhd_fmuupdatable = isFMUUpdatable(bgmObj, kw)

        # Check that 5 facies is defined and find the orderIndex
        if self.num_facies_in_zone != 5:
            raise ValueError(
                f'Error when reading model file: {modelFileName}\n'
                f'Error: Read truncation rule: {self._className}\n'
                f'Error: Different number of facies in truncation rule and in zone.'
            )

        # Check that specified facies is defined for the zone
        self._checkFaciesForZone()

        for item in self._faciesInTruncRule:
            fName = item
            fIndx = -1
            for k in range(len(self._faciesInZone)):
                fN = self._faciesInZone[k]
                if fN == fName:
                    fIndx = k
                    break
            if fIndx < 0:
                raise ValueError('Error in Trunc3D_Bayfill.  Programming error.')
            self._orderIndex.append(fIndx)

        if self._debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: Facies names in truncation rule:')
            print(repr(self._faciesInTruncRule))
            print('Debug output: Facies ordering:')
            print(repr(self._orderIndex))
            print('Debug output: Facies code for facies in truncation rule')
            print(repr(self._faciesCode))

    def initialize(
        self, mainFaciesTable, faciesInZone, faciesInTruncRule,
        gaussFieldsInZone, alphaFieldNameForBackGroundFacies,
        sf_value, sf_name, sf_fmu_updatable, ysf, ysf_fmu_updatable, sbhd, sbhd_fmu_updatable,
        useConstTruncParam, debug_level=Debug.OFF
    ):
        """
        Initialize the truncation object from input variables.
        """
        # Initialize data structure
        self.__init__(debug_level=debug_level)
        if self._debug_level >= Debug.VERY_VERBOSE:
            print(f'Debug output: Call the initialize function in {self._className}')

        # Call base class method to set modelled facies
        self._setModelledFacies(mainFaciesTable, faciesInZone)

        # Call base class method to associate gauss fields with alpha coordinates
        self._setGaussFieldForBackgroundFaciesTruncationMap(gaussFieldsInZone, alphaFieldNameForBackGroundFacies, 3)
        # Set facies in truncation rule
        self._faciesInTruncRule = copy.copy(faciesInTruncRule)

        # Set truncation parameters
        self.__useConstTruncModelParam = useConstTruncParam
        if self.__useConstTruncModelParam:
            self.__param_sf = sf_value
            self.__param_sf_name = ''
            self._is_param_sf_fmuupdatable = sf_fmu_updatable
        else:
            self.__param_sf = 0
            self.__param_sf_name = copy.copy(sf_name)

        self.__param_ysf = float(ysf)
        self._is_param_ysf_fmuupdatable = ysf_fmu_updatable

        self.__param_sbhd = float(sbhd)
        self._is_param_sbhd_fmuupdatable = sbhd_fmu_updatable

        # Check that facies in truncation rule is consistent with facies in zone
        self._checkFaciesForZone()

        # Set orderIndex
        for fName in self._faciesInTruncRule:
            fIndx = -1
            for k in range(len(self._faciesInZone)):
                fN = self._faciesInZone[k]
                if fN == fName:
                    fIndx = k
                    break
            if fIndx < 0:
                raise ValueError('Error in Trunc3D_bayfill.  Programming error.')
            self._orderIndex.append(fIndx)

    def writeContentsInDataStructure(self):
        print('')
        print('************  Contents of the data structure for class: ' + self._className + ' ***************')
        print('Eps: ' + str(self.__eps))
        print('Main facies table:')
        print(repr(self._mainFaciesTable))
        print('Number of facies in main facies table: ' + str(self.num_global_facies))
        print('Facies to be modelled:')
        print(repr(self._faciesInZone))
        print('Facies code per facies to be modelled:')
        print(repr(self._faciesCode))
        print('Facies in truncation rule:')
        print(repr(self._faciesInTruncRule))
        print('Number of facies to be modelled:' + str(self.num_facies_in_zone))
        print('Index array orderIndex:')
        print(repr(self._orderIndex))
        print('Index in faciesInZone for facies which has 100% probability')
        print(repr(self._faciesIsDetermined))
        print('Print info level: ' + str(self._debug_level))
        print('Is function setTruncRule called?')
        print(repr(self._setTruncRuleIsCalled))
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
        for idx, poly in enumerate(self.__polygons):
            print('Polygon number: ' + str(idx))
            for p in poly:
                print(repr(p))
        print('Facies index for polygons:')
        print(repr(self.__fIndxPerPolygon))

    def getClassName(self):
        return self._className

    def getFaciesOrderIndexList(self):
        return copy.copy(self._orderIndex)

    def getFaciesInTruncRule(self):
        return copy.copy(self._faciesInTruncRule)

    def getNGaussFieldsInModel(self):
        return 3

    def getUseZ(self):
        return self.__useZ

    def getZTruncationValue(self):
        return self.__Zm

    def useConstTruncModelParam(self):
        return self.__useConstTruncModelParam

    def truncMapPolygons(self):
        assert self._setTruncRuleIsCalled
        isDetermined = any(
            self._faciesIsDetermined[self._orderIndex[index]]
            for index in range(self.num_facies_in_truncation_rule)
        )
        if isDetermined:
            self.__polygons = []
            for indx in range(self.num_facies_in_truncation_rule):
                fIndx = self._orderIndex[indx]
                if self._faciesIsDetermined[fIndx] == 1:
                    poly = self.__unitSquarePolygon()
                else:
                    poly = self.__zeroPolygon()
                self.__polygons.append(poly)
        return copy.copy(self.__polygons)

    def getTruncationParam(self, gridModel, realNumber):
        # Read truncation parameters
        from src.utils.roxar.grid_model import getContinuous3DParameterValues
        paramName = self.__param_sf_name
        if self._debug_level >= Debug.VERBOSE:
            print('--- Use spatially varying truncation rule parameter SF for truncation rule: ' + self._className)
            print('--- Read RMS parameter: ' + paramName)

        values = getContinuous3DParameterValues(gridModel, paramName, realNumber, self._debug_level)
        self.__param_sf = values

    def faciesIndxPerPolygon(self):
        return copy.copy(self.__fIndxPerPolygon)

    def XMLAddElement(self, parent, zone_number, region_number, fmu_attributes):
        if self._debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: call XMLADDElement from ' + self._className)

        # Add to the parent element a new element with specified tag and attributes.
        # The attributes are a dictionary with {name:value}
        # After this function is called, the parent element has got a new child element
        # for the current class.
        nGF = self.getNGaussFieldsInModel()

        trRuleElement = Element('TruncationRule')
        parent.append(trRuleElement)

        attribute = {
            'nGFields': str(nGF)
        }
        trRuleTypeElement = Element('Trunc3D_Bayfill', attribute)
        trRuleElement.append(trRuleTypeElement)

        tag = 'BackGroundModel'
        bgModelElement = Element(tag)
        trRuleTypeElement.append(bgModelElement)

        tag = 'AlphaFields'
        alphaFieldsElement = Element(tag)
        alphaIndx1 = self._alphaIndxList[0]
        gfName1 = self._gaussFieldsInZone[alphaIndx1]
        alphaIndx2 = self._alphaIndxList[1]
        gfName2 = self._gaussFieldsInZone[alphaIndx2]
        alphaIndx3 = self._alphaIndxList[2]
        gfName3 = self._gaussFieldsInZone[alphaIndx3]
        alphaFieldsElement.text = ' ' + gfName1 + ' ' + gfName2 + ' ' + gfName3 + ' '
        bgModelElement.append(alphaFieldsElement)

        tag = 'UseConstTruncParam'
        useConstElement = Element(tag)
        useConstElement.text = ' 1 ' if self.__useConstTruncModelParam else ' 0 '
        bgModelElement.append(useConstElement)

        tag = 'Floodplain'
        obj = Element(tag)
        obj.text = ' ' + str(self._faciesInTruncRule[0]) + ' '
        bgModelElement.append(obj)

        tag = 'Subbay'
        obj = Element(tag)
        obj.text = ' ' + str(self._faciesInTruncRule[1]) + ' '
        bgModelElement.append(obj)

        tag = 'WBF'
        obj = Element(tag)
        obj.text = ' ' + str(self._faciesInTruncRule[2]) + ' '
        bgModelElement.append(obj)

        tag = 'BHD'
        obj = Element(tag)
        obj.text = ' ' + str(self._faciesInTruncRule[3]) + ' '
        bgModelElement.append(obj)

        tag = 'Lagoon'
        obj = Element(tag)
        obj.text = ' ' + str(self._faciesInTruncRule[4]) + ' '
        bgModelElement.append(obj)

        tag = 'SF'
        obj = Element(tag)
        if self._is_param_sf_fmuupdatable:
            fmu_attribute = createFMUvariableNameForBayfillTruncation(tag, zone_number, region_number)
            fmu_attributes.append(fmu_attribute)
            obj.attrib = dict(kw=fmu_attribute)
        if self.__useConstTruncModelParam:
            obj.text = ' ' + str(self.__param_sf) + ' '
        else:
            obj.text = ' ' + self.__param_sf_name + ' '
        bgModelElement.append(obj)

        tag = 'YSF'
        obj = Element(tag)
        obj.text = ' ' + ' ' + str(self.__param_ysf) + ' '
        if self._is_param_ysf_fmuupdatable:
            fmu_attribute = createFMUvariableNameForBayfillTruncation(tag, zone_number, region_number)
            fmu_attributes.append(fmu_attribute)
            obj.attrib = dict(kw=fmu_attribute)
        bgModelElement.append(obj)

        tag = 'SBHD'
        obj = Element(tag)
        obj.text = ' ' + ' ' + str(self.__param_sbhd) + ' '
        if self._is_param_sbhd_fmuupdatable:
            fmu_attribute = createFMUvariableNameForBayfillTruncation(tag, zone_number, region_number)
            fmu_attributes.append(fmu_attribute)
            obj.attrib = dict(kw=fmu_attribute)
        bgModelElement.append(obj)

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

    @staticmethod
    def __unitSquarePolygon():
        """  Create a polygon for the unit square
        """
        return [[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]

    @staticmethod
    def __zeroPolygon():
        """ Create a small polygon
        """
        return [[0, 0], [0, 0.0001], [0.0001, 0.0001], [0, 0.0001], [0, 0]]

    def setSFParam(self, sfValue):
        if 0 <= sfValue <= 1.0:
            self.__param_sf = sfValue
        else:
            raise ValueError('SF parameter for Bayfill truncation rule must be between 0.0 and 1.0')

    def setSFParamFmuUpdatable(self, value):
        self._is_param_sf_fmuupdatable = value

    def setYSFParam(self, ysfValue):
        if 0 <= ysfValue <= 1.0:
            self.__param_ysf = ysfValue
        else:
            raise ValueError('YSF parameter for Bayfill truncation rule must be between 0.0 and 1.0')

    def setYSFParamFmuUpdatable(self, value):
        self._is_param_ysf_fmuupdatable = value

    def setSBHDParam(self, sbhdValue):
        if 0 <= sbhdValue <= 1.0:
            self.__param_sbhd = sbhdValue
        else:
            raise ValueError('SBHD parameter for Bayfill truncation rule must be between 0.0 and 1.0')

    def setSBHDParamFmuUpdatable(self, value):
        self._is_param_sbhd_fmuupdatable = value

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

        self._setTruncRuleIsCalled = True
        self.__setMinimumFaciesProb(faciesProb)
        isDetermined = False
        for indx in range(self.num_facies_in_truncation_rule):
            fIndx = self._orderIndex[indx]
            self._faciesIsDetermined[fIndx] = 0
            if faciesProb[fIndx] > (1.0 - self.__eps):
                self._faciesIsDetermined[fIndx] = 1
                isDetermined = True
        if isDetermined:
            return

        if self.__useConstTruncModelParam:
            sf = self.__param_sf
        else:
            sf = self.__param_sf[cellIndx]

        ysf = self.__param_ysf
        sbhd = self.__param_sbhd

        fIndx = self._orderIndex[0]
        P1 = faciesProb[fIndx]

        fIndx = self._orderIndex[1]
        P2 = faciesProb[fIndx]

        fIndx = self._orderIndex[2]
        P3 = faciesProb[fIndx]

        fIndx = self._orderIndex[3]
        P4 = faciesProb[fIndx]

        fIndx = self._orderIndex[4]
        P5 = faciesProb[fIndx]
        if self._debug_level >= Debug.VERY_VERY_VERBOSE and cellIndx == 0:
            print('Debug output: P1,P2,P3,P4,P5: {} {} {} {} {}'.format(P1, P2, P3, P4, P5))
        if sbhd > 0.999:
            sbhd = 0.999
        elif sbhd < 0.001:
            sbhd = 0.001
        if sf < 0.0001:
            sf = 0.0001

        # Tolerance when comparing two float values
        eps = self.__eps
        YWIB = 1.0
        Ym = 0.0
        Ym2 = 0.0
        Xm = 0.0
        Xm2 = 0.0

        if P1 < 0.0 or P2 < 0.0 or P3 < 0.0 or P4 < 0.0 or P5 < 0.0:
            warn(' Warning: Negative probabilities as input. Is set to 0.')
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
            raise ValueError('Error: All input probabilities are <= 0.0')

        if not (1.0 + 2.0 * eps) >= sumProb >= (1.0 - 2.0 * eps):
            print(
                f' Warning: In truncation rule type: bayfill.\n'
                f'          Sum of input probabilities is {sumProb} and not within 1.0 +/- {2.0 * eps}\n'
                f'          Adjust all probabilities by normalizing the probabilities.'
            )

        # Very small adjustments if abs(sumProb) < eps
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
            # No BHD in shared polygon shared by WBF
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
            Amax = XL - X4
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
                        ((XL - X2) * (XL - X2) / (sf * sf)) + (c / (sf * (c - sf))) * (
                            (XL - X2) * (XL - X2) / c + 2.0 * AmP4sqrt)
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
                elif AmP4sqrt <= (
                    (0.5 / c) * (XL - X4) * (XL - X4)
                    - 0.5 * (X2 - X4) * YS + (XL - X4) * (1.0 - (XL - X4) / c)
                ):
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

        if self._debug_level >= Debug.VERY_VERY_VERBOSE and cellIndx == 0:
            print('Internal variables in ' + self._className + ' for cell index = ' + str(cellIndx) + ' :')
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
            if bhdsit < 4:
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
            useZ = True
        else:
            useZ = False

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
            if P1 > 0.0:
                polyFP.extend([
                    [0.0, 0.0],
                    [1.0, 0.0],
                    [X2, YF2],
                    [X1, YF],
                    [0.0, YF],
                    [0.0, 0.0]
                ])
            else:
                polyFP.extend([[0, 0], [0, 0], [0, 0], [0, 0]])

            polygons.append(polyFP)

            # polygon = Polygon([(X4,YS),(X3,YF),(X1,YF)],True) #SB
            if P2 > 0.0:
                polySB.extend([
                    [X4, YS],
                    [X3, YF],
                    [X1, YF],
                    [X4, YS]
                ])
            else:
                polySB.extend([[0, 0], [0, 0], [0, 0], [0, 0]])

            polygons.append(polySB)

        elif fssit == 2:
            # polygon = Polygon([(0.0,0.0),(X2,YS),(X1,YF),(0.0,YF)],True) #FP
            if P1 > 0:
                polyFP.extend([
                    [0.0, 0.0],
                    [X2, YS],
                    [X1, YF],
                    [0.0, YF],
                    [0.0, 0.0]
                ])
            else:
                polyFP.extend([[0, 0], [0, 0], [0, 0], [0, 0]])

            polygons.append(polyFP)

            # polygon = Polygon([(X4,YS),(X3,YF),(X1,YF),(X2,YS)],True) #SB
            if P2 > 0:
                polySB.extend([
                    [X4, YS],
                    [X3, YF],
                    [X1, YF],
                    [X2, YS],
                    [X4, YS]
                ])
            else:
                polySB.extend([[0, 0], [0, 0], [0, 0], [0, 0]])

            polygons.append(polySB)

        elif fssit == 3:
            # polygon = Polygon([(0.0,0.0),(X2,YF2),(X1,YF),(0.0,YF)],True) #FP
            if P1 > 0:
                polyFP.extend([
                    [0.0, 0.0],
                    [X2, YF2],
                    [X1, YF],
                    [0.0, YF],
                    [0.0, 0.0]
                ])
            else:
                polyFP.extend([[0, 0], [0, 0], [0, 0], [0, 0]])

            polygons.append(polyFP)

            # polygon = Polygon([(X4,YS),(X3,YF),(X1,YF)],True) #SB
            if P2 > 0:
                polySB.extend([
                    [X4, YS],
                    [X3, YF],
                    [X1, YF],
                    [X4, YS]
                ])
            else:
                polySB.extend([[0, 0], [0, 0], [0, 0], [0, 0]])

            polygons.append(polySB)

        elif fssit == 4:
            # polygon = Polygon([(0.0,0.0),(X2,YS),(X1,YF)],True) #FP
            if P1 > 0:
                polyFP.extend([
                    [0.0, 0.0],
                    [X2, YS],
                    [X1, YF],
                    [0.0, 0.0]
                ])
            else:
                polyFP.extend([[0, 0], [0, 0], [0, 0], [0, 0]])

            polygons.append(polyFP)

            # polygon = Polygon([(X4,YS),(X3,1.0),(X1,1.0),(X1,YF),(X2,YS)],True) #SB
            if P2 > 0:
                polySB.extend([
                    [X4, YS],
                    [X3, 1.0],
                    [X1, 1.0],
                    [X1, YF],
                    [X2, YS],
                    [X4, YS]
                ])
            else:
                polySB.extend([[0, 0], [0, 0], [0, 0], [0, 0]])

            polygons.append(polySB)

        elif fssit == 5:
            # polygon = Polygon([(0.0,0.0),(X2,YF2),(X1,YF)],True) #FP
            if P1 > 0:
                polyFP.extend([
                    [0.0, 0.0],
                    [X2, YF2],
                    [X1, YF],
                    [0.0, 0.0],
                ])
            else:
                polyFP.extend([[0, 0], [0, 0], [0, 0], [0, 0]])

            polygons.append(polyFP)

            # polygon = Polygon([(X4,YS),(X3,1.0),(X1,1.0),(X1,YF)],True) #SB
            if P2 > 0:
                polySB.extend([
                    [X4, YS],
                    [X3, 1.0],
                    [X1, 1.0],
                    [X1, YF],
                    [X4, YS]
                ])
            else:
                polySB.extend([[0, 0], [0, 0], [0, 0], [0, 0]])

            polygons.append(polySB)

        else:
            # polygon = Polygon([(0.0,0.0),(X2,YF2),(X1,YF)],True) #FP
            if P1 > 0:
                polyFP.extend([
                    [0.0, 0.0],
                    [X2, YF2],
                    [X1, YF],
                    [0.0, 0.0]
                ])
            else:
                polyFP.extend([[0, 0], [0, 0], [0, 0], [0, 0]])

            polygons.append(polyFP)

            # polygon = Polygon([(X4,YS),(X1,YS2),(X1,YF)],True) #SB
            if P2 > 0:
                polySB.extend([
                    [X4, YS],
                    [X1, YS2],
                    [X1, YF],
                    [X4, YS]
                ])
            else:
                polySB.extend([[0, 0], [0, 0], [0, 0], [0, 0]])

            polygons.append(polySB)

        # ------ Lagoon ------------------

        y2 = 0.0
        # Intersection between Floodplain line and Lagoon line
        if X2 >= XL:
            y2 = (YF2 - YF) * (XL - X1) / (X2 - X1) + YF

        if bhdsit == 1:
            # polygon = Polygon([(1.0,0.0),(1.0,1.0),(XL,1.0),(XL,0.0)],True) #LG
            if P5 > 0:
                polyLG.extend([
                    [1.0, 0.0],
                    [1.0, 1.0],
                    [XL, 1.0],
                    [XL, 0.0],
                    [1.0, 0.0]
                ])
            else:
                polyLG.extend([[0, 0], [0, 0], [0, 0], [0, 0]])

            polygons.append(polyLG)

        else:
            if X2 > XL:
                # polygon = Polygon([(X2,YF2),(1.0,0.0),(1.0,1.0),(XL,1.0),(XL,y2)],True) #LG
                if P5 > 0:
                    polyLG.extend([
                        [X2, YF2],
                        [1.0, 0.0],
                        [1.0, 1.0],
                        [XL, 1.0],
                        [XL, y2],
                        [X2, YF2]
                    ])
                else:
                    polyLG.extend([[0, 0], [0, 0], [0, 0], [0, 0]])

                polygons.append(polyLG)

            else:
                # polygon = Polygon([(XL,0.0),(1.0,0.0),(1.0,1.0),(XL,1.0)],True) #LG
                if P5 > 0:
                    polyLG.extend([
                        [XL, 0.0],
                        [1.0, 0.0],
                        [1.0, 1.0],
                        [XL, 1.0],
                        [XL, 0.0]
                    ])
                else:
                    polyLG.extend([[0, 0], [0, 0], [0, 0], [0, 0]])

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
            if bhdsit == 1:
                if Xm2 > X4:
                    # polygon = Polygon([(Xm,Ym2),(Xm2,Ym),(X4,1.0),(X4,0.0),(Xm,0.0)],True) #BHD
                    if P4 > 0:
                        polyBHD.extend([
                            [Xm, Ym2],
                            [Xm2, Ym],
                            [X4, 1.0],
                            [X4, 0.0],
                            [Xm, 0.0],
                            [Xm, Ym2]
                        ])
                    else:
                        polyBHD.extend([[0, 0], [0, 0], [0, 0], [0, 0]])

                    polygons.insert(2, polyBHD)

                    # polygon = Polygon([(Xm,Ym2),(Xm2,Ym),(XL,1.0),(XL,Ym2)],True) #WBF
                    if P3 > 0:
                        polyWBF.extend([
                            [Xm, Ym2],
                            [Xm2, Ym],
                            [XL, 1.0],
                            [XL, Ym2],
                            [Xm, Ym2]
                        ])
                    else:
                        polyWBF.extend([[0, 0], [0, 0], [0, 0], [0, 0]])

                    polygons.insert(2, polyWBF)

                else:
                    # polygon = Polygon([(Xm,Ym2),(Xm2,Ym),(Xm2,0.0),(Xm,0.0)],True) #BHD
                    if P4 > 0:
                        polyBHD.extend([
                            [Xm, Ym2],
                            [Xm2, Ym],
                            [Xm2, 0.0],
                            [Xm, 0.0],
                            [Xm, Ym2]
                        ])
                    else:
                        polyBHD.extend([[0, 0], [0, 0], [0, 0], [0, 0]])

                    polygons.insert(2, polyBHD)

                    # polygon = Polygon([(Xm,Ym2),(Xm2,Ym),(Xm2,1.0),(XL,1.0),(XL,YL)],True) #WBF
                    if P3 > 0:
                        polyWBF.extend([
                            [Xm, Ym2],
                            [Xm2, Ym],
                            [Xm2, 1.0],
                            [XL, 1.0],
                            [XL, YL],
                            [Xm, Ym2]
                        ])
                    else:
                        polyWBF.extend([[0, 0], [0, 0], [0, 0], [0, 0]])

                    polygons.insert(2, polyWBF)

            elif bhdsit == 2:
                if Xm2 > X4:
                    if Ym < YS:
                        # polygon = Polygon([(Xm,Ym2),(Xm2,Ym),(X2,0.0),(XL,0.0)],True) #BHD
                        if P4 > 0:
                            polyBHD.extend([
                                [Xm, Ym2],
                                [Xm2, Ym],
                                [X2, 0.0],
                                [XL, 0.0],
                                [Xm, Ym2]
                            ])
                        else:
                            polyBHD.extend([[0, 0], [0, 0], [0, 0], [0, 0]])

                        polygons.insert(2, polyBHD)

                        # polygon =
                        # Polygon([(Xm,Ym2),(Xm2,Ym),(X4,YS),(X3,YS2),(X3,1.0),(X4,1.0),(XL,1.0),(XL,0.0)],True)
                        # #WBF
                        if P3 > 0:
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
                        else:
                            polyWBF.extend([[0, 0], [0, 0], [0, 0], [0, 0]])

                        polygons.insert(2, polyWBF)

                    elif Ym == 1.0:
                        # polygon =
                        # Polygon([(Xm,Ym2),(Xm2,Ym),(X4,1.0),(X4,YS),(X2,YF2),(XL,0.0)],True)
                        # #BHD
                        if P4 > 0:
                            polyBHD.extend([
                                [Xm, Ym2],
                                [Xm2, Ym],
                                [X4, 1.0],
                                [X4, YS],
                                [X2, YF2],
                                [XL, 0.0],
                                [Xm, Ym2]
                            ])
                        else:
                            polyBHD.extend([[0, 0], [0, 0], [0, 0], [0, 0]])

                        polygons.insert(2, polyBHD)

                        # polygon =
                        # Polygon([(X4,1.0),(X3,1.0),(X3,YS2),(X4,YS),(X4,1.0),(Xm2,1.0),(XL,1.0),(XL,0.0),(Xm,Ym2),(Xm2,Ym)],False)
                        # #WBF
                        if P3 > 0:
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
                        else:
                            polyWBF.extend([[0, 0], [0, 0], [0, 0], [0, 0]])

                        polygons.insert(2, polyWBF)
                else:
                    if Ym == 0.0 and Ym2 == 0.0:
                        # polygon = Polygon([(Xm,Ym2),(X4,Ym)],True) #BHD
                        if P4 > 0:
                            polyBHD.extend([
                                [Xm, Ym2],
                                [X4, Ym],
                                [Xm, Ym2]
                            ])
                        else:
                            polyBHD.extend([[0, 0], [0, 0], [0, 0], [0, 0]])

                        polygons.insert(2, polyBHD)

                        # polygon =
                        # Polygon([(X4,YS),(X3,YS2),(X3,1.0),(X4,1.0),(XL,1.0),(XL,0.0),(X2,0.0)],True)
                        # #WBF
                        if P3 > 0:
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
                        else:
                            polyWBF.extend([[0, 0], [0, 0], [0, 0], [0, 0]])
                        polygons.insert(2, polyWBF)

                    else:
                        # polygon = Polygon([(Xm,Ym2),(X4,Ym),(X4,YS),(X2,0.0),(Xm,0.0)],True) #BHD
                        if P4 > 0:
                            polyBHD.extend([
                                [Xm, Ym2],
                                [X4, Ym],
                                [X4, YS],
                                [X2, 0.0],
                                [Xm, 0.0],
                                [Xm, Ym2]
                            ])
                        else:
                            polyBHD.extend([[0, 0], [0, 0], [0, 0], [0, 0]])

                        polygons.insert(2, polyBHD)

                        # polygon =
                        # Polygon([(Xm,Ym2),(X4,Ym),(X4,YS),(X3,YS2),(X3,1.0),(X4,1.0),(XL,1.0),(XL,0.0)],True)
                        # #WBF
                        if P3 > 0:
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
                        else:
                            polyWBF.extend([[0, 0], [0, 0], [0, 0], [0, 0]])

                        polygons.insert(2, polyWBF)

            elif bhdsit == 3:
                if Xm2 > X4:
                    if Ym < YS:
                        # polygon = Polygon([(Xm,Ym2),(Xm2,Ym),(XL,YL)],True) #BHD
                        if P4 > 0:
                            polyBHD.extend([
                                [Xm, Ym2],
                                [Xm2, Ym],
                                [XL, YL],
                                [Xm, Ym2]
                            ])
                        else:
                            polyBHD.extend([[0, 0], [0, 0], [0, 0], [0, 0]])

                        polygons.insert(2, polyBHD)

                        # polygon =
                        # Polygon([(Xm,Ym2),(Xm2,Ym),(X4,YS),(X3,1.0),(X4,1.0),(XL,1.0),(XL,Ym2)],True)
                        # #WBF
                        if P3 > 0:
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
                        else:
                            polyWBF.extend([[0, 0], [0, 0], [0, 0], [0, 0]])

                        polygons.insert(2, polyWBF)

                    elif Ym == 1.0:
                        # polygon = Polygon([(Xm,Ym2),(Xm2,Ym),(X4,1.0),(X4,YS),(XL,YL)],True) #BHD
                        if P4 > 0:
                            polyBHD.extend([
                                [Xm, Ym2],
                                [Xm2, Ym],
                                [X4, 1.0],
                                [X4, YS],
                                [XL, YL],
                                [Xm, Ym2]
                            ])
                        else:
                            polyBHD.extend([[0, 0], [0, 0], [0, 0], [0, 0]])

                        polygons.insert(2, polyBHD)

                        # polygon =
                        # Polygon([(X4,1.0),(X3,1.0),(X4,YS),(X4,1.0),(Xm2,1.0),(XL,1.0),(Xm,Ym2),(Xm2,Ym)],False)
                        # #WBF
                        if P3 > 0:
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
                        else:
                            polyWBF.extend([[0, 0], [0, 0], [0, 0], [0, 0]])

                        polygons.insert(2, polyWBF)
                else:
                    # polygon = Polygon([(Xm,Ym2),(X4,Ym),(X4,YS),(XL,YL)],True) #BHD
                    if P4 > 0:
                        polyBHD.extend([
                            [Xm, Ym2],
                            [X4, Ym],
                            [X4, YS],
                            [XL, YL],
                            [Xm, Ym2]
                        ])
                    else:
                        polyBHD.extend([[0, 0], [0, 0], [0, 0], [0, 0]])

                    polygons.insert(2, polyBHD)

                    # polygon = Polygon([(Xm,Ym2),(X4,Ym),(X4,YS),(X3,1.0),(X4,1.0),(XL,1.0)],True) #WBF
                    if P3 > 0:
                        if P4 > 0:
                            polyWBF.extend([
                                [Xm, Ym2],
                                [X4, Ym],
                                [X4, YS],
                                [X3, 1.0],
                                [X4, 1.0],
                                [XL, 1.0],
                                [Xm, Ym2]
                            ])
                        else:
                            polyWBF.extend([
                                [XL, YL],
                                [X4, YS],
                                [X3, 1.0],
                                [X4, 1.0],
                                [XL, 1.0],
                                [XL, YL]
                            ])
                    else:
                        polyWBF.extend([[0, 0], [0, 0], [0, 0], [0, 0]])
                    polygons.insert(2, polyWBF)

        else:
            # Subbay line
            x1 = X3
            x2 = X4
            y1 = YS2
            y2 = YS

            # Intersection between y = YWIB and the line for boundary between Subbay and WFB
            x2 = x1 + (YWIB - y1) * (x2 - x1) / (y2 - y1)

            if bhdsit == 4:
                if X2 > XL:
                    # polygon =
                    # Polygon([(X4,1.0),(X4,YWIB),(x2,YWIB),(X4,YS),(XL,YL),(XL,1.0)],True)
                    # #BHD
                    if P4 > 0:
                        polyBHD.extend([
                            [X4, 1.0],
                            [X4, YWIB],
                            [x2, YWIB],
                            [X4, YS],
                            [XL, YL],
                            [XL, 1.0],
                            [X4, 1.0]
                        ])
                    else:
                        polyBHD.extend([[0, 0], [0, 0], [0, 0], [0, 0]])

                    polygons.insert(2, polyBHD)

                    # polygon = Polygon([(X4,1.0),(X4,YWIB),(x2,YWIB),(X3,YS2)],True) #WBF
                    if P3 > 0:
                        polyWBF.extend([
                            [X4, 1.0],
                            [X4, YWIB],
                            [x2, YWIB],
                            [X3, YS2],
                            [X4, 1.0]
                        ])
                    else:
                        polyWBF.extend([[0, 0], [0, 0], [0, 0], [0, 0]])

                    polygons.insert(2, polyWBF)

                else:
                    # polygon =
                    # Polygon([(X4,1.0),(X4,YWIB),(x2,YWIB),(X4,YS),(X2,YF2),(XL,0.0),(XL,1.0)],True)
                    # #BHD
                    if P4 > 0:
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
                    else:
                        polyBHD.extend([[0, 0], [0, 0], [0, 0], [0, 0]])

                    polygons.insert(2, polyBHD)

                    # polygon = Polygon([(X4,1.0),(X4,YWIB),(x2,YWIB),(X3,YS2)],True) #WBF
                    if P3 > 0:
                        polyWBF.extend([
                            [X4, 1.0],
                            [X4, YWIB],
                            [x2, YWIB],
                            [X3, YS2],
                            [X4, 1.0]
                        ])
                    else:
                        polyWBF.extend([[0, 0], [0, 0], [0, 0], [0, 0]])

                    polygons.insert(2, polyWBF)

            if bhdsit == 5 or bhdsit == 6:
                if YWIB > YS2:
                    # polygon =
                    # Polygon([(X4,1.0),(X4,YWIB),(0.0,YWIB),(0.0,YS2),(X4,YS),(X2,YF2),(XL,YL),(XL,1.0)],True)
                    # #BHD
                    if P4 > 0:
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
                    else:
                        polyBHD.extend([[0, 0], [0, 0], [0, 0], [0, 0]])

                    polygons.insert(2, polyBHD)

                    # polygon = Polygon([(X4,1.0),(X4,YWIB),(0.0,YWIB),(0.0,1.0)],True) #WBF
                    if P3 > 0:
                        polyWBF.extend([
                            [X4, 1.0],
                            [X4, YWIB],
                            [0.0, YWIB],
                            [0.0, 1.0],
                            [X4, 1.0]
                        ])
                    else:
                        polyWBF.extend([[0, 0], [0, 0], [0, 0], [0, 0]])

                    polygons.insert(2, polyWBF)

                else:
                    # polygon =
                    # Polygon([(X4,1.0),(X4,YWIB),(x2,YWIB),(X4,YS),(X2,YF2),(XL,YL),(XL,1.0)],True)
                    # #BHD
                    if P4 > 0:
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
                    else:
                        polyBHD.extend([[0, 0], [0, 0], [0, 0], [0, 0]])

                    polygons.insert(2, polyBHD)

                    # polygon = Polygon([(X4,1.0),(X4,YWIB),(x2,YWIB),(X3,YS2),(X3,1.0)],True) #WBF
                    if P3 > 0:
                        polyWBF.extend([
                            [X4, 1.0],
                            [X4, YWIB],
                            [x2, YWIB],
                            [X3, YS2],
                            [X3, 1.0],
                            [X4, 1.0]
                        ])
                    else:
                        polyWBF.extend([[0, 0], [0, 0], [0, 0], [0, 0]])

                    polygons.insert(2, polyWBF)

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
                WBF_area = (X4 - X3) * (1.0 - 0.5 * (YS2 + YS)) - 0.5 * (X4 - X3) * (YWIB - YS) * (YWIB - YS) / (
                    YS2 - YS)
                BHD_vol = 1.0 - WBF_area - LG_area - FP_area - SB_area
        elif bhdsit == 6:
            WBF_area = 0.5 * ((X4 - X3) * (1.0 - YS) - (X4 - X3) * (YWIB - YS) * (YWIB - YS) / (1.0 - YS))
            BHD_vol = 1.0 - WBF_area - LG_area - FP_area - SB_area

        if self._debug_level >= Debug.VERY_VERY_VERBOSE and cellIndx == 0:
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
        # Set base class facies polygons
        self._faciesPolygons = copy.copy(self.__polygons)
        self.num_polygons = len(self._faciesPolygons)

    def defineFaciesByTruncRule_old(self, alphaCoord):
        """defineFaciesByTruncRule: Calculate facies by applying the truncation rule.

           Input:
                      x,y,z      - The values of the uniformly distributed fields to be used.
           Output:    facies     - facies code.

           Internal variables to be used:
                     self.__polygons
                     self.__useZ
                     self.__Zm
        """
        x = alphaCoord[self._alphaIndxList[0]]
        y = alphaCoord[self._alphaIndxList[1]]
        z = alphaCoord[self._alphaIndxList[2]]
        for indx in range(self.num_facies_in_truncation_rule):
            fIndx = self._orderIndex[indx]
            if self._faciesIsDetermined[fIndx] == 1:
                faciesCode = self._faciesCode[fIndx]
                return faciesCode, fIndx

        faciesCode = -1
        indx = -1
        for i in range(len(self.__polygons)):
            polygon = self.__polygons[i]
            inside = self._isInsidePolygon(polygon, x, y)
            if inside == 0:
                continue
            else:
                if i in [0, 1, 4]:
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

        fIndx = self._orderIndex[indx]
        faciesCode = self._faciesCode[fIndx]

        return faciesCode, fIndx

    def facies_index_in_truncation_rule_for_polygon(self, polygon_index):
        indx = self.__fIndxPerPolygon[polygon_index]
        if indx < 0:
            print('indx: {} polygon number: {}'.format(indx, polygon_index))
            assert indx >= 0
        return indx

    def get_background_index_in_truncaction_rule(self):
        return self.__fIndxPerPolygon

    def setParamSFConst(self, value):
        if not (0 <= value <= 1):
            raise ValueError("Error: The value must be between 0 and 1 (inclusive)")
        else:
            self.__param_sf = value

    def setParamSF(self, paramName):
        self.__param_sf = 0
        self.__param_sf_name = copy.copy(paramName)

    def setParamYSFConst(self, value):
        if value < 0 or value > 1:
            raise ValueError("Error: The value must be between 0 and 1 (inclusive)")
        else:
            self.__param_ysf = value

    def setParamSBHDConst(self, value):
        if value < 0 or value > 1:
            raise ValueError("Error: The value must be between 0 and 1 (inclusive)")
        else:
            self.__param_sbhd = value
