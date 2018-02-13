#!/bin/env python
# -*- coding: utf-8 -*-
from xml.etree.ElementTree import Element

import copy
import numpy as np

from src.utils.constants.simple import Debug
from src.utils.xml import getFloatCommand, getKeyword

"""
-----------------------------------------------------------------------
class Trunc2D_Base
Description: This class is used as a base class for class Trunc2D_Cubic_Multi_OverLay and Trunc2D_Angle_Multi_OverLay.
             It contains common data used by both and common functions related to common data.

 Public member functions:
 Constructor:
   def __init__(self, trRuleXML=None, mainFaciesTable=None, faciesInZone=None, gaussFieldsInZone=None, debug_level=Debug.OFF,
              modelFileName=None)

 Private functions:
   def __checkOverlayFacies(self)
   def __checkAlphaIndx(self)
   def __checkProbFrac(self)
   def __checkCenterTruncInterval(self)
   def __calcGroupIndxForBGFacies(self)
   def __addAlpha(self,alphaName,createErrorIfExist=False)
   def __interpretXMLTree_read_gauss_field_names(self,trRuleXML, gaussFieldsInZone, modelFileName)
   def __isFaciesInZone(self, fName)

 Protected functions (To be called from derived classes only, not public functions):
   def _setEmpty()
   def _setModelledFacies(mainFaciesTable, faciesInZone)
   def _setGaussFieldForEachAlphaDimension(gaussFieldsInZone, gaussFieldsInTruncRule)
   def _setOverlayFaciesDataStructure(overlayGroups)
   def _interpretXMLTree_overlay_facies(self, trRuleXML, modelFileName)
   def _isFaciesProbEqualOne(self, faciesProb)
   def _checkFaciesForZone(self)
   def _addFaciesToTruncRule(self, fName)
   def _setMinimumFaciesProb(self, faciesProb)
   def _modifyBackgroundFaciesArea(self, faciesProb)
   def _truncateOverlayFacies(self, indx, alphaCoord)
   def _XMLAddElement(self, parent)

 Public functions:
   def getAlphaIndexInZone(self, alphaName)
   def writeContentsInDataStructure(self)
   def getClassName(self)
   def getFaciesOrderIndexList(self)
   def getFaciesInTruncRule(self)
   def getFaciesInTruncRuleIndex(self, fName)
   def getBackgroundFaciesInTruncRuleIndex(self, fName)
   def getFaciesInZoneIndex(self, fName)

-------------------------------------------------------------
"""


class Trunc2D_Base:
    """
    This class implements common data structure and is a base class for
    Trunc2D_Cubic_Multi_OverLay and Trunc2D_Angle_Multi_OverLay.

    Data organization for data structure related to facies:
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

    4. gaussFieldsInZone.
    The specified list of gaussian fields for the zone.

    5. alphaIndxList.
    The truncation cube is defined by coordinates (alpha1, alpha2) for the background facies truncation map
    and is extended to more dimensions if overlay facies is  modelled. The index list alphaIndxList associate
    gauss field with alpha coordinates. j = alphaIndxList[i]  where i is alpha coordinate number
    and j is gauss field number.
    """

    def _setEmpty(self):
        """
        Initialize the data structure for empty object.
        Need to be called by initialization functions in derived classes.
        Common variables for the class Trunc2D_Cubic_Multi_OverLay and Trunc2D_Angle_Multi_OverLay
        Except for three lists, all common variables are defined by the model and initialized either by
        reading the model file or by calling initialize function.
        """

        # Tolerance used for probabilities
        self._epsFaciesProb = 0.0001

        # Global facies table
        self._mainFaciesTable = None
        self._nFaciesMain = 0

        # Facies to be modelled for the zone
        self._nFacies = 0
        self._faciesInZone = []

        # Facies code for faciesInZone. The facies code is defined in the global facies table.
        self._faciesCode = []

        # Facies to be modelled but ordered as it is defined in the truncation rule.
        # Note that facies ordering is important and defined in the truncation rule.
        self._faciesInTruncRule = []

        # Index list take as input index in faciesInTruncRule and return index in faciesInZone
        self._orderIndex = []

        # A logical (0/1) value per facies to be modelled. Input is index in faciesInZone
        # The value is 1 for a facies if this facies has probability close to 100%
        # and therefore is determined to be the facies. Is used to make the algorithm more robust.
        # This list is recalculated for each truncation map (for each new facies probability )
        self._faciesIsDetermined = []

        # Is set to a value from 0 to 3 and the lower the value, the less output is printed to screen
        # Value 3 result in output of debug info details.
        self._debug_level = Debug.OFF

        # Is used to check if truncation map is initialized or not. E.g. truncation map polygons
        # depends on having calculated truncation map.
        # This variable is set to True when truncation map is calculated.
        self._setTruncRuleIsCalled = False

        # Number of gauss fields used in background model
        self._nGaussFieldsInBackGroundModel = 0

        # Number of gauss fields used in the truncation rule (dimension of alpha space)
        self._nGaussFieldsInTruncationRule = 0

        # Gauss fields defined for the zone
        self._gaussFieldsInZone = []

        # Number of facies defined if no overlay facies is specified. These are also called background facies.
        self._nBackGroundFacies = 0

        # Gauss field index which define which gauss field number corresponds to alpha1,alpha2,...
        self._alphaIndxList = []

        # Variables containing specification of overlay facies model

        # Number of overlay facies groups
        self._nGroups = 0

        # A 1D array of indices to gauss fields. The input index to the list is facies index in faciesInTruncRule.
        self._groupIndxForBackGroundFaciesIndx = []

        # A 2D list where first index is group index (groupIndx) from 0 to self._nGroups
        # and second index i run from 0 to self._nAlphaPerGroup[groupIndx]. The value alphaIndx = alphaInGroup[groupIndx][i]
        # is an index in the list self._gaussFieldsInZone.
        self._alphaInGroup = []

        # A 2D list of center point for truncation intervals for the overlay facies defined in all groups for all alpha fields.
        # center = self._centerAlpha[groupIndx][i] where groupIndx refer to the overlay group and i refer to
        # the alpha field in the group.
        self._centerTruncIntervalInGroup = []

        # A 2D list with lower truncation value for overlay facies corresponding to specified
        # group index and alphaField number in group.
        # lowValue = self._lowAlpha[groupIndx][i] where groupIndx refer to the overlay group
        # and i refer to the alpha field in the group.
        # This list is recalculated for each truncation map (for each new facies probability )
        self._lowAlphaInGroup = []

        # A 2D list with upper truncation value for overlay facies corresponding to specified
        # group index and alphaField number in group.
        # highValue = self._highAlpha[groupIndx][i] where groupIndx refer to the overlay group
        # and i refer to the alpha field in the group.
        # This list is recalculated for each truncation map (for each new facies probability )
        self._highAlphaInGroup = []

        # A 2D list with indx to the overlay facies for a given groupindex (groupIndx) and alphaField (i).
        # indx = self._overlayFaciesIndx[groupIndx][i] Here indx is refereing to elements in the
        # self._faciesInTruncRule list for each overlay facies defined in the group.
        # Note that it is possible that the same overlay facies can correspond to different
        # alpha field indices i. This makes it possible
        # to create a geometry for the facies that is composed of geometry for different gaussian fields.
        # It is also possible that the same overlay facies can appear in different overlay facies groups.
        # This makes it possible to have some overlay facies which can appear to overprint many
        # different background facies while other overlay facies is limited to only a few background facies.
        self._overlayFaciesIndxInGroup = []

        # A 2D list with probability fractions for each overlay facies that is specified in any
        # group  (groupIndx) and for any alpha field (i) in the group.
        # The list elements are probFrac = self._probFracOverlayFacies[groupIndx][i]
        self._probFracOverlayFaciesInGroup = []

        # A 2D list with background facies indices for a given overlay facies group
        self._backgroundFaciesInGroup = []

        # Variables used to check optimization of algorithm
        self._nCalc = 0
        self._nLookup = 0
        self._useMemoization = True

        # Define disctionary to be used in memoization for optimalization
        # In this dictionary use key equal to faciesProb and save faciespolygon
        self._memo = {}

        # To make a lookup key from facies probability, round off input facies probability
        # to nearest value which is written like  n/resolution where n is an integer from 0 to resolution
        self._keyResolution = 100

    def __init__(self, trRuleXML=None, mainFaciesTable=None, faciesInZone=None, gaussFieldsInZone=None,
                 debug_level=Debug.OFF,
                 modelFileName=None, nGaussFieldsInBackGroundModel=2):
        """
        Base class constructor.
        """
        # Initialize data structure

        self._setEmpty()
        self._className = 'Trunc2D_Base'
        self._debug_level = debug_level
        self._nGaussFieldsInBackGroundModel = nGaussFieldsInBackGroundModel

        if trRuleXML is not None:
            if self._debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: Read data from model file in: ' + self._className)

            # Initialize common data for facies to be modelled (specified for the zone) and the
            # ordering of the facies in the truncation rule.
            self._setModelledFacies(mainFaciesTable, faciesInZone)

            # Read gauss field names for the background facies truncation rule and assign which gauss field
            # should correspond to each alpha coordinate for truncation rule for background facies (alpha1, alpha2)
            self.__interpretXMLTree_read_gauss_field_names(trRuleXML, gaussFieldsInZone, modelFileName)
        else:
            if self._debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: Create empty object for: ' + self._className)
                #  End of __init__

    def _setModelledFacies(self, mainFaciesTable, faciesInZone):
        """
        Initialize main facies table from input and which facies to model from input.
        """
        if mainFaciesTable is not None:
            self._mainFaciesTable = copy.copy(mainFaciesTable)
            self._nFaciesMain = len(self._mainFaciesTable)
        else:
            raise ValueError(
                'Error in {}\n'
                'Error: Inconsistency.'
                ''.format(self._className)
            )

        # Reference to facies in zone model using this truncation rule
        if faciesInZone is not None:
            self._faciesInZone = copy.copy(faciesInZone)
            self._nFacies = len(self._faciesInZone)
            self._faciesIsDetermined = np.zeros(self._nFacies, int)
        else:
            raise ValueError(
                'Error in ' + self._className + '\n'
                                                'Error: Inconsistency'
            )

        # Facies code for facies in zone
        self._faciesCode = []
        for fName in self._faciesInZone:
            fCode = self._mainFaciesTable.getFaciesCodeForFaciesName(fName)
            self._faciesCode.append(fCode)

    def _setGaussFieldForBackgroundFaciesTruncationMap(
            self, gaussFieldsInZone, alphaFieldNameForBackGroundFacies, nGaussFieldsInBackGroundModel
    ):
        """
        The lists: self._gaussFieldsInZone, self._alphaIndxList and the integer self._nGaussFieldsInTruncationRule
        are defined. The input names of the alphaFieldNamesForBackGroundFacies (gauss fields) corresponds
        to the alpha coordinate alpha1 and alpha2 and must exist in the self._gaussFieldsInZone list.
        The alphaIndxList define which alpha field corresponds to which specified gauss fields for the zone.
        j = self._alphaIndxList[i] is index in list self._gaussFieldsInZone
        and alpha1 = self._gaussFieldsInZone[self._alphaIndxList[0]]
            alpha2 = self._gaussFieldsInZone[self._alphaIndxList[1]] and so on.
        """
        # print(repr(gaussFieldsInZone))
        # print(repr(alphaFieldNameForBackGroundFacies))
        self._gaussFieldsInZone = copy.copy(gaussFieldsInZone)
        self._alphaIndxList = []
        self._nGaussFieldsInBackGroundModel = nGaussFieldsInBackGroundModel
        assert len(alphaFieldNameForBackGroundFacies) == nGaussFieldsInBackGroundModel
        self._nGaussFieldsInTruncationRule = nGaussFieldsInBackGroundModel
        for i in range(nGaussFieldsInBackGroundModel):
            self.__addAlpha(alphaFieldNameForBackGroundFacies[i], createErrorIfExist=False)

    def _setOverlayFaciesDataStructure(self, overlayGroups):
        """
        Initialize data structure from input list of lists.
        Fill the lists self._groupIndxForBackGroundFaciesIndx, self._alphaInGroup,
        self._centerTruncIntervalInGroup, self._overlayFaciesIndxInGroup,
        self._probFracOverlayFaciesInGroup, self._backgroundFaciesInGroup
        and variable self._nGroups
        """
        if overlayGroups is None:
            self._nGroups = 0
        else:
            self._nGroups = len(overlayGroups)
        # print('nGroups: ' + str(self._nGroups))

        # Before assigning overlay facies the number of facies in trunc rule list faciesInTruncRule
        # all facies are background facies.
        self._nBackGroundFacies = len(self._faciesInTruncRule)
        ALPHA_LIST_INDX = 0
        BACKGROUND_LIST_INDX = 1

        ALPHA_INDX = 0
        OVERLAY_INDX = 1
        PROBFRAC_INDX = 2
        CENTERINTERVAL_INDX = 3

        for groupIndx in range(self._nGroups):
            alphaFieldIndxListThisGroup = []
            overlayFaciesIndxListThisGroup = []
            probFracListThisGroup = []
            centerTruncIntervalThisGroup = []
            backGroundFaciesIndxListThisGroup = []
            groupItem = overlayGroups[groupIndx]
            alphaList = groupItem[ALPHA_LIST_INDX]
            nAlpha = len(alphaList)
            # print(repr(alphaList))
            for j in range(nAlpha):
                alphaItem = alphaList[j]
                # print('alphaItem:')
                # print(repr(alphaItem))
                alphaFieldName = alphaItem[ALPHA_INDX]
                overlayFaciesName = alphaItem[OVERLAY_INDX]
                probFrac = alphaItem[PROBFRAC_INDX]
                centerInterval = alphaItem[CENTERINTERVAL_INDX]
                # print('alphaFieldName: ' + alphaFieldName)
                # print(repr(self._gaussFieldsInZone))

                alphaIndx = self.__addAlpha(alphaFieldName, createErrorIfExist=False)
                alphaFieldIndxListThisGroup.append(alphaIndx)
                # print('alphaFieldName: ' + alphaFieldName + ' alphaIndx: ' + str(alphaIndx))

                nFaciesInTruncRule, indx, fIndx, isNew = self._addFaciesToTruncRule(overlayFaciesName)
                if isNew:
                    self._orderIndex.append(fIndx)

                overlayFaciesIndxListThisGroup.append(indx)
                # print('overlayFaciesName: ' + overlayFaciesName + ' indx for facies in truncation rule: ' + str(indx))

                probFracListThisGroup.append(probFrac)
                # print('probFrac: ' + str(probFrac))

                centerTruncIntervalThisGroup.append(centerInterval)
                # print('centerOfInterval: ' + str(centerInterval))

            bgFaciesListForGroup = groupItem[BACKGROUND_LIST_INDX]
            for bgFaciesName in bgFaciesListForGroup:
                indx = self.getFaciesInTruncRuleIndex(bgFaciesName)
                backGroundFaciesIndxListThisGroup.append(indx)
            # print('background facies: ')
            # print(repr(bgFaciesListForGroup))
            # print('background facies indx: ')
            # print(repr(backGroundFaciesIndxListThisGroup))

            self._alphaInGroup.append(alphaFieldIndxListThisGroup)
            self._overlayFaciesIndxInGroup.append(overlayFaciesIndxListThisGroup)
            self._probFracOverlayFaciesInGroup.append(probFracListThisGroup)
            self._centerTruncIntervalInGroup.append(centerTruncIntervalThisGroup)
            self._backgroundFaciesInGroup.append(backGroundFaciesIndxListThisGroup)

        self.__checkAlphaIndx()
        self.__checkOverlayFacies()
        self.__checkProbFrac()
        self.__checkCenterTruncInterval()

        self.__calcGroupIndxForBGFacies()

    def __checkOverlayFacies(self):
        nBackGroundFac = 0
        for groupIndx in range(self._nGroups):
            nBackGroundFac += len(self._backgroundFaciesInGroup[groupIndx])

        # Number of background facies for overlay facies can at maximum be all background facies
        assert nBackGroundFac <= self._nBackGroundFacies

        checkOverlapForBackGroundFacies = []
        for groupIndx in range(self._nGroups):
            nBackGroundFac = len(self._backgroundFaciesInGroup[groupIndx])
            checkIndx = []
            for i in range(nBackGroundFac):
                indx = self._backgroundFaciesInGroup[groupIndx][i]
                # Check that background facies index is legal
                if indx < 0 or indx >= self._nBackGroundFacies:
                    raise ValueError(
                        'Wrong index {0} for background facies.'
                        'Should be less than {1} and not negative'.format(str(indx), self._nBackGroundFacies)
                    )

                # Check that background facies for this group is not specified multiple times
                if indx in checkIndx:
                    fName = self._faciesInTruncRule[indx]
                    raise ValueError(
                        'Background facies {} is specified multiple times for the same group'
                        ''.format(fName)
                    )
                checkIndx.append(indx)

                # Check that background facies for this group is not used in other groups
                if indx in checkOverlapForBackGroundFacies:
                    fName = self._faciesInTruncRule[indx]
                    raise ValueError(
                        'Background facies {} is specified for more than one group'
                        ''.format(fName)
                    )
                checkOverlapForBackGroundFacies.append(indx)

            nAlpha = len(self._alphaInGroup[groupIndx])
            for i in range(nAlpha):
                indx = self._overlayFaciesIndxInGroup[groupIndx][i]

                # Check that overlay facies index is legal
                if indx < self._nBackGroundFacies or indx >= self._nFacies:
                    fName = self._faciesInTruncRule[indx]
                    raise ValueError(
                        'Overlay facies {} is not a valid facies name'
                        ''.format(fName)
                    )

    def __checkAlphaIndx(self):
        nGaussField = 2
        checkIndx = []
        for groupIndx in range(self._nGroups):
            nAlpha = len(self._alphaInGroup[groupIndx])
            for j in range(nAlpha):
                alphaIndx = self._alphaInGroup[groupIndx][j]
                # if this gauss field is not equal to any previous gauss field
                # count it and add it to the check list, if equal, ignore it
                if alphaIndx not in checkIndx:
                    checkIndx.append(alphaIndx)
                    # Check that this is consistent with self._alphaIndxList
                    assert alphaIndx == self._alphaIndxList[nGaussField]
                    nGaussField += 1

    def __checkProbFrac(self):
        sumProbFrac = np.zeros(self._nFacies, dtype=float)
        for groupIndx in range(self._nGroups):
            nAlpha = len(self._alphaInGroup[groupIndx])
            for j in range(nAlpha):
                indx = self._overlayFaciesIndxInGroup[groupIndx][j]
                probFrac = self._probFracOverlayFaciesInGroup[groupIndx][j]
                sumProbFrac[indx] += probFrac
                # print('nBackgroundfacies: ' + str(self._nBackGroundFacies))
                # print('nFacies: ' + str(self._nFacies))
                # print('faciesInTruncRule:')
                # print(repr(self._faciesInTruncRule))
        for indx in range(self._nBackGroundFacies, self._nFacies):
            fName = self._faciesInTruncRule[indx]
            # print(
            #    'Sum prob fraction for {} is {}'
            #    ''.format(fName, sumProbFrac[indx])
            # )
            assert abs(sumProbFrac[indx] - 1.0) <= self._epsFaciesProb

    def __checkCenterTruncInterval(self):
        for groupIndx in range(self._nGroups):
            nAlpha = len(self._alphaInGroup[groupIndx])
            for j in range(nAlpha):
                indx = self._overlayFaciesIndxInGroup[groupIndx][j]
                centerInterval = self._centerTruncIntervalInGroup[groupIndx][j]
                assert 0.0 <= centerInterval <= 1.0

    def __calcGroupIndxForBGFacies(self):
        self._groupIndxForBackGroundFaciesIndx = np.zeros(self._nBackGroundFacies, dtype=int)
        for i in range(self._nBackGroundFacies):
            self._groupIndxForBackGroundFaciesIndx[i] = -1

        for groupIndx in range(self._nGroups):
            nBackGroundFac = len(self._backgroundFaciesInGroup[groupIndx])
            for i in range(nBackGroundFac):
                indx = self._backgroundFaciesInGroup[groupIndx][i]
                self._groupIndxForBackGroundFaciesIndx[indx] = groupIndx

    def __addAlpha(self, alphaName, createErrorIfExist=False):
        """
        Check that alphaName is a valid name of a gauss field for the zone.
        If a valid name, add a new entry in the list self._alphaIndxList if the gauss field with name alphaName
        is not already used. If the alphaName gauss field is not already used and therefore added,
        the alpha space dimension is increased by one.
        The return value is the  alpha index (The index in the list gaussFieldsInZone for the gauss field
        with name alphaName).
        """
        indx = self.getAlphaIndexInZone(alphaName)
        if indx >= 0:
            # The alphaName exist in the zone
            if indx not in self._alphaIndxList:
                # Add only to the list if the alphaName is not used already
                self._alphaIndxList.append(indx)
                self._nGaussFieldsInTruncationRule = len(self._alphaIndxList)
            else:
                if createErrorIfExist:
                    raise ValueError(
                        'Cannot add gauss field name {} that is already used as alpha parameter'.format(alphaName)
                    )

        else:
            # print('indx: ' + str(indx))
            raise ValueError(
                'Error when initializing gauss field names for each alpha coordinate dimension\n'
                'Specified gauss field name {} in truncation rule is not defined for the zone.'
                ''.format(alphaName)
            )
        return indx

    def getAlphaIndexInZone(self, alphaName):
        indx = -1
        for j in range(len(self._gaussFieldsInZone)):
            gfName = self._gaussFieldsInZone[j]
            if alphaName == gfName:
                indx = j
                break
        return indx

    def __isFaciesInZone(self, fName):
        if fName in self._faciesInZone:
            return True
        else:
            return False

    def __interpretXMLTree_read_gauss_field_names(self, trRuleXML, gaussFieldsInZone, modelFileName):
        """
        Description: Read gauss field names for alpha1 and alpha2 which is used to create background facies
        """
        self._gaussFieldsInZone = copy.copy(gaussFieldsInZone)
        # print('gaussFieldsInZone: ')
        # print(repr(self._gaussFieldsInZone))
        bgmObj = getKeyword(trRuleXML, 'BackGroundModel', 'TruncationRule', modelFileName, required=True)

        alphaFieldsObj = getKeyword(bgmObj, 'AlphaFields', 'BackGroundModel', modelFileName, required=True)
        text = alphaFieldsObj.text
        alphaFieldNames = text.split()
        if len(alphaFieldNames) != self._nGaussFieldsInBackGroundModel:
            raise ValueError(
                'Error when reading model file: {}\n'
                'Error: Read truncation rule: {}\n'
                'Error: Number of specified gauss field names must be {} under keyword AlphaFields\n'
                ''.format(modelFileName, self._className, str(self._nGaussFieldsInBackGroundModel))
            )
        for i in range(self._nGaussFieldsInBackGroundModel):
            # Add gauss field
            indx = self.__addAlpha(alphaFieldNames[i], True)

        if self._debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: Background facies truncation rule use:')
            for i in range(self._nGaussFieldsInBackGroundModel):
                print('Alpha({}): {}'
                      ''.format(str(i), alphaFieldNames[i])
                      )

        self._nGaussFieldsInTruncationRule = len(self._alphaIndxList)
        assert self._nGaussFieldsInTruncationRule == self._nGaussFieldsInBackGroundModel

    def _interpretXMLTree_overlay_facies(self, trRuleXML, modelFileName, zoneNumber):
        """
        Description: Read specification of one or more overlay facies and which region (set of background facies)
                     the overlay facies is defined to be located. The background facies is defined by truncation rule
                     using the first two dimensions of the multidimensional unit cube (alpha1 and alpha2). The overlay
                     facies defined to 'overprint' a subset of the background facies. To be able to handle this,
                     the background facies are grouped into non-overlapping sets. No background facies can belong to two
                     different groups. For each group one can specify arbitrarily many overlay facies, but the sequence
                     they are specified define the internal truncation of the overlay facies. For each overlay facies
                     there are associated a gaussian field (alpha field) so that each overlay facies can have different geometry.
                     It is also possible to specify that one and the same overlay facies is associated with multiple alpha fields.
                     In this case one has to assign probability fractions for each of them such that the sum is 1.0.
                     It is also possible to define that an overlay facies can be defined for different groups. Also in this case
                     the sum of probability fractions over all occurrences of the overlay facies in the keyword OverLayModel
                     must sum to 1.0. It is also possible to let the same alpha field be used in different groups,
                     but it is a requirement that alpha fields related to facies in the same group must be different
                     (cannot have two different alpha dimensions related to the same alpha field at the same location
                     since this will create linear dependencies between alpha coordinates.)

        Input: trRuleXML - Pointer refering to XML tree where to find info about the truncation rule. All derived classes has a
               truncation rule containing the same keywords for overprint facies and associated background facies.
               modelFileName - Only used as a text string when printing error messages in order to make them more informative.
        """
        if self._debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: -- Start read overlay facies model in ' + self._className + ' from model file')

        # Number of background facies is the facies in truncation rule before overlay facies is added
        self._nBackGroundFacies = len(self._faciesInTruncRule)

        # Lookup array to find group indx (index in list groups) given background facies indx (index in list faciesInTruncRule)
        # Initialize the array to -1 since not all background facies that is modelled is necessarily used as
        # background for any overlay facies
        self._groupIndxForBackGroundFaciesIndx = np.zeros(self._nBackGroundFacies, dtype=int)
        for i in range(self._nBackGroundFacies):
            self._groupIndxForBackGroundFaciesIndx[i] = -1

        # Interpret model file for overlay facies
        kw = 'OverLayModel'
        overLayModelObj = getKeyword(trRuleXML, kw, 'TruncationRule', modelFileName, required=False)
        if overLayModelObj is not None:
            kw1 = 'Group'
            self._groups = []
            groupIndx = 0
            checkBGFaciesList = []
            for overLayGroupObj in overLayModelObj.findall(kw1):
                if overLayGroupObj is None:
                    raise ValueError('Missing keyword {} in keyword {} in zone {} in truncation rule in model file {}'
                                     ''.format(kw1, kw, str(zoneNumber), modelFileName))
                alphaList = []
                centerList = []
                probFracList = []
                overlayFaciesIndxInGroup = []
                kw2 = 'AlphaField'

                for alphaObj in overLayGroupObj.findall(kw2):

                    if alphaObj is None:
                        raise ValueError(
                            'Missing keyword {} in keyword {} in zone {} in truncation rule in model file {}'
                            ''.format(kw2, kw1, str(zoneNumber), modelFileName)
                        )
                    text = alphaObj.get('name')
                    alphaName = text.strip()

                    # First the gauss field alphaName is checked to be one of the gauss fields defined for the zone.
                    # Then add the gauss field alphaName to the alpha space and increase the alpha space dimension by one
                    # if the alphaName is not already added. The alphaIndxList is updated.
                    # In case the alphaName is already added, nothing will happen except that the index to the gauss field
                    # corresponding to the alpha variable is returned
                    alphaIndxInGroup = self.__addAlpha(alphaName)

                    # list of alpha indices for alpha fields for this group is updated
                    if alphaIndxInGroup not in alphaList:
                        alphaList.append(alphaIndxInGroup)
                    else:
                        raise ValueError(
                            'Cannot have two different overlay facies in same group with the same alpha field.'
                            'Alpha field name: {} is specified multiple times for group number {} in zone {}'
                            ''.format(alphaName, str(groupIndx + 1), str(zoneNumber))
                        )

                    kw3 = 'TruncIntervalCenter'
                    truncIntervalCenter = getFloatCommand(alphaObj, kw3, kw2, minValue=0.0, maxValue=1.0,
                                                          modelFile=modelFileName, required=True)
                    centerList.append(truncIntervalCenter)

                    kw4 = 'ProbFrac'
                    probFracObj = getKeyword(alphaObj, kw4, kw2, modelFile=modelFileName, required=True)
                    text = probFracObj.get('name')
                    fName = text.strip()
                    # Check that facies name is not a background facies and that it is defined for the zone
                    if fName not in self._faciesInZone:
                        raise ValueError(
                            'Specified overlay facies {} is not defined for zone {}'
                            ''.format(fName, str(zoneNumber))
                        )
                    indx = self.getBackgroundFaciesInTruncRuleIndex(fName)
                    if indx >= 0:
                        raise ValueError('Specified overlay facies {} is already defined as background facies.'
                                         ''.format(fName))

                    # Add the overlay facies to the list of facies for the truncation rule if not already added
                    nFacies, indx, fIndx, isNew = self._addFaciesToTruncRule(fName)
                    overlayFaciesIndxInGroup.append(indx)
                    if isNew == 1:
                        self._orderIndex.append(fIndx)

                    probFracValue = getFloatCommand(alphaObj, kw4, kw2, minValue=0.0, maxValue=1.0,
                                                    modelFile=modelFileName, required=True)
                    probFracList.append(probFracValue)

                if len(alphaList) == 0:
                    raise ValueError(
                        'Missing keyword {} in keyword {} in zone {} in truncation rule in model file {}'
                        ''.format(kw2, kw1, str(zoneNumber), modelFileName)
                    )

                self._alphaInGroup.append(alphaList)
                self._centerTruncIntervalInGroup.append(centerList)
                self._probFracOverlayFaciesInGroup.append(probFracList)
                self._overlayFaciesIndxInGroup.append(overlayFaciesIndxInGroup)
                kw2 = 'BackGround'
                bgFaciesIndxList = []
                for bgFaciesObj in overLayGroupObj.findall(kw2):
                    if bgFaciesObj is None:
                        raise ValueError(
                            'Missing keyword {} in keyword {} in zone {} in truncation rule in model file {}'
                            ''.format(kw2, kw1, str(zoneNumber), modelFileName)
                        )
                    text = bgFaciesObj.text
                    bgFaciesName = text.strip()
                    # Check that facies name is a valid facies for the zone
                    if not self.__isFaciesInZone(bgFaciesName):
                        raise ValueError(
                            'Error when reading model file {} for zone {} in truncation rule.\n'
                            'Error: Specified facies name: {} as background facies for overlay facies '
                            'in truncation rule is not defined in this zone.'
                            ''.format(modelFileName, str(zoneNumber), bgFaciesName)
                        )
                    # Check that the facies actually is a background facies in the truncation rule.
                    indx = self.getBackgroundFaciesInTruncRuleIndex(bgFaciesName)
                    if indx < 0:
                        raise ValueError(
                            'Error when reading model file {} for zone {} in truncation rule.\n'
                            'Error: Specified facies name: {} as background facies for overlay facies in truncation rule is not defined\n'
                            '       in the truncation rule in keyword BackGroundModel or it is used as overlay facies.'
                            ''.format(modelFileName, str(zoneNumber), bgFaciesName)
                        )
                    # Check that the facies name is not use previously in the list of background facies for this group
                    if indx in bgFaciesIndxList:
                        raise ValueError(
                            'Error when reading model file {} for zone {} in truncation rule.\n'
                            'The facies {} is specified multiple times as background facies in an overlay facies group'
                            ''.format(modelFileName, str(zoneNumber), bgFaciesName)
                        )
                    # Check that the facies is not specified in other groups.
                    if indx in checkBGFaciesList:
                        raise ValueError(
                            'Error when reading model file {} for zone {} in truncation rule.\n'
                            'The facies {} is specified as background facies in more than one of the overlay facies groups.'
                            ' The implemented method cannot handle this case.'.format(
                                modelFileName, str(zoneNumber), bgFaciesName
                            )
                        )
                    else:
                        checkBGFaciesList.append(indx)

                    # Facies name should be OK now
                    bgFaciesIndxList.append(indx)

                # Define group index for each background facies where facies is specified as index in faciesInTruncRule
                if len(bgFaciesIndxList) == 0:
                    raise ValueError(
                        'Missing keyword {} in keyword {} in zone {} in truncation rule in model file {}'
                        ''.format(kw2, kw1, str(zoneNumber), modelFileName)
                    )

                for indx in bgFaciesIndxList:
                    self._groupIndxForBackGroundFaciesIndx[indx] = groupIndx

                self._backgroundFaciesInGroup.append(bgFaciesIndxList)

                groupIndx += 1
            if groupIndx == 0:
                raise ValueError('Missing keyword {} in keyword {} for zone {} in truncation rule in model file {}'
                                 ''.format(kw1, kw, str(zoneNumber), modelFileName))

            self._nGroups = groupIndx
            self._nGaussFieldsInTruncationRule = len(self._alphaIndxList)

            # Check that sum of probability fractions is 1.0 for each overlay facies
            sumProbFrac = np.zeros(self._nFacies, dtype=float)
            for groupIndx in range(self._nGroups):
                nAlpha = len(self._alphaInGroup[groupIndx])
                for alphaInGroupIndx in range(nAlpha):
                    indx = self._overlayFaciesIndxInGroup[groupIndx][alphaInGroupIndx]
                    fName = self._faciesInTruncRule[indx]
                    probFrac = self._probFracOverlayFaciesInGroup[groupIndx][alphaInGroupIndx]
                    sumProbFrac[indx] += probFrac

            for indx in range(len(self._faciesInTruncRule)):
                fName = self._faciesInTruncRule[indx]
                sumPF = sumProbFrac[indx]
                indxBG = self.getBackgroundFaciesInTruncRuleIndex(fName)
                if indxBG < 0:
                    # This facies is overlay facies
                    if abs(sumPF - 1.0) > self._epsFaciesProb:
                        raise ValueError(
                            'Error in model file {} for zone {}\n'
                            ' Sum of probability fraction specified for overlay facies {} is {} and not 1.0'
                            ''.format(modelFileName, str(zoneNumber), fName, str(sumPF))
                        )

            nOverLayFacies = 0
            faciesFound = []
            for groupIndx in range(self._nGroups):
                nAlpha = len(self._alphaInGroup[groupIndx])
                for alphaInGroupIndx in range(nAlpha):
                    indx = self._overlayFaciesIndxInGroup[groupIndx][alphaInGroupIndx]
                    if indx not in faciesFound:
                        faciesFound.append(indx)
                        nOverLayFacies += 1
            self._nOverLayFacies = nOverLayFacies

            # Check that the number of facies specified in the zone (self._nFacies) is equal to the
            # specified number of facies in truncation rule
            if self._nFacies != (self._nBackGroundFacies + self._nOverLayFacies):
                raise ValueError(
                    'Number of facies specified for zone {} is: {}\n'
                    'Number of facies in background model is: {}\n'
                    'Number of overlay facies is: {}\n'
                    'The sum of number of background facies and overlay facies must match the number of facies for the zone'
                    ''.format(str(zoneNumber), str(self._nFacies), str(self._nOverLayFacies),
                              str(self._nBackGroundFacies))
                )

            if self._debug_level >= Debug.VERY_VERBOSE:
                print(
                    'Debug output: List of alpha fields used in the zone model. The sequence define the alpha coordinates'
                )
                for i in range(len(self._alphaIndxList)):
                    indx = self._alphaIndxList[i]
                    alphaName = self._gaussFieldsInZone[indx]
                    print(
                        'Debug output:  Alpha coordinate {}  corresponds to gauss field {}'.format(str(i + 1),
                                                                                                   alphaName)
                    )
                print('Debug output: Dimension of Alpha space is: ' + str(len(self._alphaIndxList)))
                print(' ')
                print('Debug output:   Number of overlay facies: ' + str(self._nOverLayFacies))
                print('Debug output: Group index for each background facies')
                for i in range(self._nBackGroundFacies):
                    fName = self._faciesInTruncRule[i]
                    groupIndx = self._groupIndxForBackGroundFaciesIndx[i]
                    if groupIndx >= 0:
                        print('Debug output:  {}  belongs to groupIndx= {}'.format(fName, str(groupIndx)))
                    else:
                        print('Debug output:  {} does not belong to any defined group'.format(fName))
                print(' ')
                print('Debug output: Alpha fields per group and overlay facies defined.')
                for groupIndx in range(self._nGroups):
                    nAlpha = len(self._alphaInGroup[groupIndx])
                    print(
                        'Debug output: For group with index: ' + str(groupIndx) + '  Number of alpha fields: ' + str(
                            nAlpha)
                    )
                    print('Debug output: Alpha    Facies   TruncIntervalCenter     ProbFrac:')
                    for alphaInGroupIndx in range(nAlpha):
                        alphaIndx = self._alphaInGroup[groupIndx][alphaInGroupIndx]
                        gfname = self._gaussFieldsInZone[alphaIndx]
                        indx = self._overlayFaciesIndxInGroup[groupIndx][alphaInGroupIndx]
                        fName = self._faciesInTruncRule[indx]
                        centerVal = self._centerTruncIntervalInGroup[groupIndx][alphaInGroupIndx]
                        probFrac = self._probFracOverlayFaciesInGroup[groupIndx][alphaInGroupIndx]
                        print(
                            'Debug output:   ' + gfname + '     ' + fName + '      ' + str(centerVal) + '     ' + str(
                                probFrac)
                        )

        if self._debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: -- End read overlay facies model in ' + self._className + ' from model file')

            # End read overlay facies

    def _isFaciesProbEqualOne(self, faciesProb):
        """
        Description: Check if facies probability is close to 1.0. Return True or False.
                     This function is used to check if it is necessary to calculate truncation map or not.
        """
        isDetermined = 0
        for fIndx in range(len(faciesProb)):
            self._faciesIsDetermined[fIndx] = 0
            if faciesProb[fIndx] > (1.0 - self._epsFaciesProb):
                self._faciesIsDetermined[fIndx] = 1
                isDetermined = 1
                break
        if isDetermined == 1:
            return True
        else:
            return False

    def _checkFaciesForZone(self):
        """
        Description: Check that the facies for the truncation rule is the same
                      as defined for the zone.
        """
        if len(self._faciesInTruncRule) != len(self._faciesInZone):
            raise ValueError(
                'Error: In truncation rule: {} Number of facies specified in truncation rule '
                'is {} which is different from number of facies specified for zone which is {}'
                ''.format(self._className, str(len(self._faciesInTruncRule)), str(len(self._faciesInZone)))
            )
        for fName in self._faciesInTruncRule:
            # print('fName in checkFaciesForZone: ')
            # print(fName)
            if fName not in self._faciesInZone:
                raise ValueError(
                    'Error: In truncation rule: {0} Facies name {1} is not defined for the current zone.\n'
                    '       No probability is defined for this facies for the current zone.'
                    ''.format(self._className, fName)
                )
        for fName in self._faciesInZone:
            if fName not in self._faciesInTruncRule:
                raise ValueError(
                    'Error: In truncation rule: {0} Facies name {1} which is defined for the current zone '
                    'is not defined in the truncation rule. Cannot have facies with specified '
                    'probability that is not used in the truncation rule.'
                    ''.format(self._className, fName)
                )

    def _addFaciesToTruncRule(self, fName):
        """
        Description: Check if facies already exist in list of facies for the truncation rule. If not, add it to
                     the truncation rule and return the index (indx) in faciesInTruncRule as well as index (fIndx)
                     in faciesInZone list.
        """
        found = 0
        isNew = 0
        nFaciesInTruncRule = len(self._faciesInTruncRule)
        indx = self.getFaciesInTruncRuleIndex(fName)
        if indx < 0:
            self._faciesInTruncRule.append(fName)
            indx = nFaciesInTruncRule
            nFaciesInTruncRule += 1
            isNew = 1

        fIndx = self.getFaciesInZoneIndex(fName)
        if fIndx < 0:
            raise ValueError('Error in {0}. Specified facies name {1} is not defined for this zone.'
                             ''.format(self._className, fName)
                             )
        self._nFaciesInTruncRule = nFaciesInTruncRule
        return nFaciesInTruncRule, indx, fIndx, isNew

    def writeContentsInDataStructure(self):
        """
        Description: Write contents of data structure for debug purpose.
        """
        print(self.__repr__())

    def __repr__(self):
        representation = """
************  Contents of the data structure common to several truncation algorithms  ***************
Eps for facies prob: {eps_facies_probability}
Main facies table:
{main_facies_table}
Number of facies in main facies table: {num_facies_main}
Facies to be modelled:
{facies_in_zone}
Facies code per facies to be modelled:
{facies_code}
Facies in truncation rule:
{facies_in_truncation_rule}
Number of facies to be modelled: {num_facies}'
Index array orderIndex:
{order_index}
Logical array with 0 for facies which is has probability 100% and 0 for facies with probability less than 100%
{is_facies_determined}
Print info level: {debug_level}'
Is function setTruncRule called?
{truncation_rule_called}
Background facies:
""".format(
            eps_facies_probability=self._epsFaciesProb, main_facies_table=repr(self._mainFaciesTable),
            num_facies_main=self._nFaciesMain, facies_in_zone=repr(self._faciesInZone),
            facies_code=repr(self._faciesCode), num_facies=self._nFacies, debug_level=self._debug_level,
            truncation_rule_called=self._setTruncRuleIsCalled, facies_in_truncation_rule=repr(self._faciesInTruncRule),
            order_index=self._orderIndex, is_facies_determined=self._faciesIsDetermined
        )
        for i in range(self._nBackGroundFacies):
            bgFaciesName = self._faciesInTruncRule[i]
            representation += '   {}'.format(bgFaciesName)
        representation += '\n'
        for i in range(self._nGroups):
            num_alpha = len(self._alphaInGroup[i])
            representation += '\nNumber of facies polygons in group number {i}  is {num_alpha}'.format(i=i,
                                                                                                       num_alpha=num_alpha)
            for j in range(num_alpha):
                alphaIndx = self._alphaInGroup[i][j]
                gfName = self._gaussFieldsInZone[alphaIndx]
                indx = self._overlayFaciesIndxInGroup[i][j]
                fName = self._faciesInTruncRule[indx]
                probFraction = self._probFracOverlayFaciesInGroup[i][j]
                low = self._lowAlphaInGroup[i][j]
                high = self._highAlphaInGroup[i][j]
                representation += (
                    'Overlay facies polygon number {j} in group {i} belongs to facies {facies_name}'
                    ' with prob fraction {probability_fraction} and defined by truncation of {gf_name}\n'
                    'Overlay facies polygon number {j} in group {i} belongs to facies {facies_name}'
                    ' and is truncated between {low} and {high}'.format(
                        j=j, i=i, facies_name=fName, probability_fraction=probFraction,
                        gf_name=gfName, low=low, high=high
                    )
                )

            for j in range(len(self._backgroundFaciesInGroup[i])):
                indx = self._backgroundFaciesInGroup[i][j]
                fName = self._faciesInTruncRule[indx]
                representation += 'Group number: {i}  Background facies: {facies_name}'.format(i=i, facies_name=fName)
        representation += '\nNumber of alpha variables (gauss fields) used in the truncation rule: {}'.format(
            self._nGaussFieldsInTruncationRule
        )
        for i in range(self._nGaussFieldsInTruncationRule):
            alphaIndx = self._alphaIndxList[i]
            gfName = self._gaussFieldsInZone[alphaIndx]
            representation += 'Alpha coordinate number {} corresponds to gauss field {}'.format(i + 1, gfName)
        return representation

    def getClassName(self):
        return copy.copy(self._className)

    def getFaciesOrderIndexList(self):
        return copy.copy(self._orderIndex)

    def getFaciesInTruncRule(self):
        return copy.copy(self._faciesInTruncRule)

    def getFaciesInTruncRuleIndex(self, fName):
        # Loop over all facies defined in the list faciesInTruncRule
        indx = -1
        for i in range(len(self._faciesInTruncRule)):
            fN = self._faciesInTruncRule[i]
            if fN == fName:
                indx = i
                break
        return indx

    def getBackgroundFaciesInTruncRuleIndex(self, fName):
        # Loop over only the facies defined as background facies
        indx = -1
        for i in range(self._nBackGroundFacies):
            fN = self._faciesInTruncRule[i]
            if fN == fName:
                indx = i
                break
        return indx

    def getFaciesInZoneIndex(self, fName):
        # Loop over all facies defined in the list faciesInZone
        indx = -1
        for i in range(self._nFacies):
            fN = self._faciesInZone[i]
            if fN == fName:
                indx = i
                break
        return indx

    def getNGaussFieldsInModel(self):
        return self._nGaussFieldsInTruncationRule

    def getEpsFaciesProb(self):
        return self._epsFaciesProb

    def setEpsFaciesProb(self, eps):
        if 0.0 < eps < 0.01:
            self._epsFaciesProb = eps
        else:
            raise ValueError(
                'Try to set tolerance for facies probabilities to {}.\n'
                'Can not set tolerance for facies probability greater than 0.01 or less than equal 0.0'
                ''.format(str(eps))
            )

    def _setMinimumFaciesProb(self, faciesProb):
        sumProb = 0.0
        eps = self._epsFaciesProb * 0.1
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

    # TODO: Sjekk ut robusthet av algoritmen i spesialtilfeller med 0 sannsynlighet for en eller flere facies eller hele grupper av facies
    def _modifyBackgroundFaciesArea(self, faciesProb):
        """
        Description: Calculate area in trunc map which has corrected for overlay facies.
                     This function will also set a minimum probability for robustness of truncation algorithms.
        """
        # The array faciesProb contain probability for all facies, a subset are background facies
        # NOTE: Only the entries in area corresponding to the background facies will be set
        # Set initially -1 into the list area.
        area = np.ones(self._nFacies, dtype=float)
        area = -1.0 * area
        for i in range(self._nBackGroundFacies):
            fIndx = self._orderIndex[i]
            area[fIndx] = faciesProb[fIndx]
        self._lowAlphaInGroup = []
        self._highAlphaInGroup = []

        # Probability of the N dimensional polygone in alpha space defined by background facies and overlay facies
        # for each group must be calculated.
        sumTotProb = 0.0
        sumProbBackGround = np.zeros(self._nGroups, dtype=float)
        sumProbOverlay = np.zeros(self._nGroups, dtype=float)
        sumProb = np.zeros(self._nGroups, dtype=float)
        if self._debug_level >= Debug.VERY_VERY_VERBOSE:
            print('\n')
            print('Debug output: Calculate modified area for background facies and threshold values for overlay facies:')

        for groupIndx in range(self._nGroups):
            # Sum over probability for background facies
            for j in range(len(self._backgroundFaciesInGroup[groupIndx])):
                indx = self._backgroundFaciesInGroup[groupIndx][j]
                fIndx = self._orderIndex[indx]
                prob = faciesProb[fIndx]
                sumProbBackGround[groupIndx] += prob

            # Sum over  overlay facies probability for this group
            nAlpha = len(self._alphaInGroup[groupIndx])
            for j in range(nAlpha):
                indx = self._overlayFaciesIndxInGroup[groupIndx][j]
                fIndx = self._orderIndex[indx]
                prob = faciesProb[fIndx]
                probFrac = self._probFracOverlayFaciesInGroup[groupIndx][j]
                assert probFrac > 0.0
                prob = prob * probFrac
                sumProbOverlay[groupIndx] += prob

            sumProb[groupIndx] = sumProbBackGround[groupIndx] + sumProbOverlay[groupIndx]
            if self._debug_level >= Debug.VERY_VERY_VERBOSE:
                print(
                    'Debug output: Group {group}: '
                    'Background facies prob={background}  Overlay facies prob={overlay}   Sum prob= {total}'
                    ''.format(
                        group=groupIndx,
                        background=sumProbBackGround[groupIndx],
                        overlay=sumProbOverlay[groupIndx],
                        total=sumProb[groupIndx])
                )

            sumTotProb += sumProb[groupIndx]

        # Calculate truncation intervals for each overlay facies
        # or overlay faciespolygon since the overlay facies can be defined in multiple polygons
        # in N dimensional unit cube in alpha space.
        # Calculate area the background facies should cover in alpha,alpha2 plane
        for groupIndx in range(self._nGroups):
            deltaAlphaThisGroup = []
            lowAlphaThisGroup = []
            highAlphaThisGroup = []
            nBackGroundFaciesInGroup = len(self._backgroundFaciesInGroup[groupIndx])
            nAlpha = len(self._alphaInGroup[groupIndx])
            D = sumProb[groupIndx]
            # print('D= ' + str(D))
            if abs(D) < self._epsFaciesProb:
                # Sum of background facies and overlay facies is 0 for this group. Set area to 0.0 for all background facies in this group
                # and set truncation interval to 0 for overlay facies in this group.
                for j in range(nBackGroundFaciesInGroup):
                    indx = self._backgroundFaciesInGroup[groupIndx][j]
                    fIndx = self._orderIndex[indx]
                    area[fIndx] = 0.0
                for j in range(nAlpha):
                    # print('groupIndx, nAlpha, indx j: ' + str(groupIndx) + ' ' + str(nAlpha) + ' ' + str(j))
                    indx = self._overlayFaciesIndxInGroup[groupIndx][j]
                    fIndx = self._orderIndex[indx]
                    lowAlphaThisGroup.append(0.0)
                    highAlphaThisGroup.append(0.0)
            else:
                B = 1.0
                # The sequence the overlay facies polygons are calculated is defined by the sequence it was specified
                # The first overlay facies polygon has truncation interval deltaAlpha1 = prob_of_facies1/sum_prob_group
                # The second overlay facies polygon has truncation interval deltaAlpha2 = prob_of_facies2/sum_prob_group*(1-deltaAlpha1)
                # The third overlay facies polygon has truncation interval deltaAlpha3 = prob_of_facies3/sum_prob_group*(1-deltaAlpha1):(1-deltaAlpha2)
                # and so on ... (This is because the second,third and so on overlay facies polygons are conditioned not to overlap the previous once.
                #nAlpha = len(self._alphaInGroup[groupIndx])
                for j in range(nAlpha):
                    indx = self._overlayFaciesIndxInGroup[groupIndx][j]
                    fIndx = self._orderIndex[indx]
                    prob = faciesProb[fIndx]
                    probFrac = self._probFracOverlayFaciesInGroup[groupIndx][j]
                    prob = prob * probFrac

                    if abs(D) < self._epsFaciesProb:
                        # This overlay facies probability is 0.0
                        delta = 0.0
                        B = 0.0
                        D = 0.0
                    else:
                        delta = prob / D
                        B = B * (1.0 - delta)
                        D = D * (1.0 - delta)
                    deltaAlphaThisGroup.append(delta)

                # If sum of probability for background facies for this group is 0.0, then assign area to the background facies
                # such that the som of area of the background facies is equal to the sum of probability of background and overlay facies
                # for this group and also ensure that truncation intervals for overlay facies is defined such that the overlay facies probability
                # sum up to the total facies probability for this group.
                if abs(sumProbBackGround[groupIndx]) < self._epsFaciesProb:
                    # Loop over all background facies in group and assign equal area to each background facies such that the sum is
                    # equal to the sum of probability for the group.
                    # NOTE: It is not unique how to split the area into the background facies in this case. This will have influence on the
                    # geometry of the realization, but the facies fraction is correct anyway.
                    for j in range(nBackGroundFaciesInGroup):
                        indx = self._backgroundFaciesInGroup[groupIndx][j]
                        fIndx = self._orderIndex[indx]
                        area[fIndx] = sumProb[groupIndx]/nBackGroundFaciesInGroup
                else:
                    # The sum of background facies probability is > 0
                    # Calculate area corresponding to background facies for the group in (alpha1, alpha2, 0, 0,..,0) plane of the truncation cube
                    for j in range(nBackGroundFaciesInGroup):
                        indx = self._backgroundFaciesInGroup[groupIndx][j]
                        fIndx = self._orderIndex[indx]
                        prob = faciesProb[fIndx]
                        if abs(B) < self._epsFaciesProb:
                            area[fIndx] = 0.0
                        else:
                            area[fIndx] = prob / B

                for j in range(nAlpha):
                    c = self._centerTruncIntervalInGroup[groupIndx][j]
                    delta = deltaAlphaThisGroup[j]
                    low = c - 0.5 * delta
                    high = c + 0.5 * delta
                    if low < 0.0:
                        low = 0.0
                        high = delta
                    elif high > 1.0:
                        high = 1.0
                        low = 1.0 - delta
                    lowAlphaThisGroup.append(low)
                    highAlphaThisGroup.append(high)
            # End if sumprob of group is 0
            self._lowAlphaInGroup.append(lowAlphaThisGroup)
            self._highAlphaInGroup.append(highAlphaThisGroup)
        if self._debug_level >= Debug.VERY_VERY_VERBOSE:
            if len(self._lowAlphaInGroup) > 0:
                print('Debug output: Low threshold values for overlay facies:')
                print(repr(self._lowAlphaInGroup))
                print('Debug output: High threshold values for overlay facies:')
                print(repr(self._highAlphaInGroup))
            print(
                'Debug output: Finished calculate modified area for background facies and threshold values for overlay facies')
            print(' ')
        return area

    def _truncateOverlayFacies(self, indx, alphaCoord):
        """
        Is used to truncate and find overlay facies. This function will be used in truncation calculations
        in derived classes when overlay facies is defined.
        The algorithm for overlay facies follows these rules:
            1. The background facies defined by the first two alpha dimensions (alpha1, alpha2) is grouped
               into one or more groups where each group has no background facies in common with other groups.
               There can be background facies that does not belong to any group. These are therefore never overlayed
               by any other facies.
            2. Within each group, there can be one or more overlay facies. Each overlay facies is defined by
               truncation of its own gaussian field (a dimension in the alpha space). Hence each overlay facies can
               have its own geometry since it is only one overlay facies defined per gaussian field.
               This can be extended later such that several overlay facies is defined by several threshold values
               for the same gaussian field.
               NOTE: There is a requirement that no two alpha variables (gauss fields) are equal within a group.
               However it is allowed to use the same alpha variable (gauss field) in different groups since
               different groups are independent of each other.
            3. The interval of the alpha parameter (the gaussian field) for an overlay facies is determined by
               an interval center and a width of the interval. In this way, the truncation interval does not have to be
               at one or the other end of the interval between 0 and 1 for the alpha coordinate corresponding
               to the gaussian field-
            4. The order of the Alpha fields define the truncation rule for overlay facies.
               The overlay facies specified first is independent of the other overlay facies in a given location.
               The second one depends on the first one, the third on both the first and second and so on.
            5. It is possible to define the same facies name for several different alpha fields. This means that the
               probability for the overlay facies is split into fractions associated with each alpha fields. This makes
               it possible to use multiple geometries (due to multiple alpha fields) for the same overlay facies.
               Note that each specification of overlay facies define a multidimensional polygon in the multidimensional
               truncation cube. This means that the same overlay facies is defined by multiple polygons similar to the
               functionality that is defined for truncation rule of background facies defined by (alpha1, alpha2).
            6. An ovelay facies can be specified in multiple groups, but with probability split into fractions
               such that the sum is 1.0 over all occurrences of the overlay facies in the multidimensional truncation cube.
        """

        # Lookup which overlay group the background facies faciesInTruncRule[indx] belongs to if any.
        groupIndx = self._groupIndxForBackGroundFaciesIndx[indx]
        if groupIndx >= 0:
            # The background facies is defined by the input variable 'indx' and the facies name is faciesInTruncRule[
            # indx]. This background facies belongs to the group with index groupIndx. The overlay facies in this
            # group may overprint the background facies. The sequence of overlay facies is determined by the sequence
            #  of alpha fields. So the sequence of alpha fields defined by the alphaInGroup and the corresponding
            # sequence of facies define the internal priority of which overlay facies is truncated or not by the
            # other overlay facies in this group. Note that overlay facies from different groups are independent of
            # each other. This code can be extended to have multiple overlay facies defined by the same alpha field,
            # by calculating threshold values for the alpha value for each facies, but so far only one overlay facies
            # is defined for each alpha field.
            nAlpha = len(self._alphaInGroup[groupIndx])
            for i in range(nAlpha):
                alphaIndx = self._alphaInGroup[groupIndx][i]
                alphaValue = alphaCoord[alphaIndx]
                # Check if value is within the interval which define the overlay facies.
                # Note that the loop over all alpha fields define the sequence in which the overlay facies is defined
                if self._lowAlphaInGroup[groupIndx][i] < alphaValue <= self._highAlphaInGroup[groupIndx][i]:
                    indx = self._overlayFaciesIndxInGroup[groupIndx][i]
                    break

        fIndx = self._orderIndex[indx]
        faciesCode = self._faciesCode[fIndx]
        return faciesCode, fIndx

    def _XMLAddElement(self, parent):
        """
        Description: Write to xml tree the keywords related to overlay facies
        """
        if self._debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: call XMLADDElement from Trunc2D_Base_xml')
        if self._nGroups == 0:
            return

        tag = 'OverLayModel'
        overlayModelElement = Element(tag)
        parent.append(overlayModelElement)

        for groupIndx in range(self._nGroups):
            tag = 'Group'
            groupElement = Element(tag)
            overlayModelElement.append(groupElement)
            nAlpha = len(self._alphaInGroup[groupIndx])
            for j in range(nAlpha):
                alphaIndx = self._alphaInGroup[groupIndx][j]
                gfName = self._gaussFieldsInZone[alphaIndx]
                tag = 'AlphaField'
                attribute = {'name': gfName}
                alphaElement = Element(tag, attribute)
                groupElement.append(alphaElement)

                tag = 'TruncIntervalCenter'
                trcElement = Element(tag)
                trcElement.text = ' ' + str(self._centerTruncIntervalInGroup[groupIndx][j]) + ' '
                alphaElement.append(trcElement)

                indx = self._overlayFaciesIndxInGroup[groupIndx][j]
                fName = self._faciesInTruncRule[indx]
                tag = 'ProbFrac'
                attribute = {'name': fName}
                probFracElement = Element(tag, attribute)
                probFracElement.text = ' ' + str(self._probFracOverlayFaciesInGroup[groupIndx][j]) + ' '
                alphaElement.append(probFracElement)

            nBackgroundFaciesInGroup = len(self._backgroundFaciesInGroup[groupIndx])
            for j in range(nBackgroundFaciesInGroup):
                indx = self._backgroundFaciesInGroup[groupIndx][j]
                fName = self._faciesInTruncRule[indx]
                tag = 'BackGround'
                bgElement = Element(tag)
                bgElement.text = ' ' + fName + ' '
                groupElement.append(bgElement)

    def getNCalcTruncMap(self):
        return self._nCalc

    def getNLookupTruncMap(self):
        return self._nLookup

    def getKeyResolution(self):
        return self._keyResolution

    @staticmethod
    def _makeKey(faciesProb, keyResolution):
        keyList = []
        key = None
        for p in faciesProb:
            # Round off the input values to nearest value of (0,0.01,0.02,..1.0)
            keyList.append(int(keyResolution * p + 0.5) / keyResolution)
            key = tuple(keyList)
        return key

    @staticmethod
    def _makeRoundOfFaciesProb(faciesProb, keyResolution):
        faciesProbNew = []
        sumProb = 0.0
        dValue = 1.0/keyResolution
        # minProb = 1.0
        maxProb = 0.0
        for i in range(len(faciesProb)):
            p = faciesProb[i]
            pNew = int(keyResolution * p + 0.5) / keyResolution
            sumProb += pNew
            # if minProb > pNew:
            #    minProb = pNew
            #    indxMin = i
            if maxProb < pNew:
                maxProb = pNew
                indxMax = i
            faciesProbNew.append(pNew)
        if sumProb > (0.9999 + dValue):
            # print('sumProb: ' + str(sumProb))
            faciesProbNew[indxMax] -= dValue
            sumProb -= dValue
            if sumProb > (0.9999 + dValue):
                faciesProbNew[indxMax] -= dValue
                sumProb -= dValue
            # print('sumProb oppdatert: ' + str(sumProb))
        elif sumProb < (1.0001 - dValue):
            # print('sumProb: ' + str(sumProb))
            faciesProbNew[indxMax] += dValue
            sumProb += dValue
            if sumProb < (1.0001- dValue):
                faciesProbNew[indxMax] += dValue
                sumProb += dValue
            # print('sumProb oppdatert: ' + str(sumProb))
        return faciesProbNew

    def getGaussFieldsInTruncationRule(self):
        # Return list of the gauss field names actually used in the truncation rule
        gfUsed = []
        for i in range(len(self._alphaIndxList)):
            gfName = self._gaussFieldsInZone[self._alphaIndxList[i]]
            gfUsed.append(gfName)
        return gfUsed

    def getGaussFieldIndexListInZone(self):
        return copy.copy(self._alphaIndxList)

    @staticmethod
    def _isInsidePolygon(polygon, xInput, yInput):
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
        num_intersections_found = 0
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
                    num_intersections_found += 1

        if (num_intersections_found // 2) * 2 != num_intersections_found:
            # Point pt is inside the closed polygon
            return True
        else:
            # Point pt is outside the closed polygon
            return False
