#!/bin/env python
# -*- coding: utf-8 -*-
from typing import List, Optional, Tuple, Union, Sized
from warnings import warn
from xml.etree.ElementTree import Element

import copy
import numpy as np

from aps.algorithms.APSMainFaciesTable import APSMainFaciesTable
from aps.utils.constants.simple import Debug
from aps.utils.xmlUtils import getFloatCommand, getKeyword
from aps.algorithms.Memoization import RoundOffConstant

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
   def _setModelledFacies(mainFaciesTable, faciesInZone)
   def _setGaussFieldForEachAlphaDimension(gaussFieldsInZone, gaussFieldsInTruncRule)
   def _setOverlayFaciesDataStructure(overlayGroups)
   def _interpretXMLTree_overlay_facies(self, trRuleXML, modelFileName)
   def _isFaciesProbEqualOne(self, faciesProb)
   def _checkFaciesForZone(self)
   def _addFaciesToTruncRule(self, facies_name)
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

    def __init__(
        self,
        trRuleXML: Optional[Element] = None,
        mainFaciesTable: Optional[APSMainFaciesTable] = None,
        faciesInZone: Optional[List[str]] = None,
        gaussFieldsInZone: Optional[List[str]] = None,
        debug_level: Debug = Debug.OFF,
        modelFileName: Optional[str] = None,
        nGaussFieldsInBackGroundModel: int = 2,
        keyResolution: int = 100,
    ) -> None:
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

        # Facies to be modelled for the zone
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
        # and second index i run from 0 to self._nAlphaPerGroup[groupIndx].
        # The value alphaIndx = alphaInGroup[groupIndx][i]
        # is an index in the list self._gaussFieldsInZone.
        self._alphaInGroup = []

        # A 2D list of center point for truncation intervals for the overlay facies defined in all groups for all alpha
        # fields. center = self._centerAlpha[groupIndx][i] where groupIndx refer to the overlay group and i refer to
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

        # Truncation map polygons calculated by sub classes. The polygons subdivide the unit square into non-overlapping
        # areas. They are used in the algorithm that look up which facies that is associated with a point in the
        # truncation map/cube. They are also used for the purpose to plot/visualize the truncation map.
        self._faciesPolygons = []

        # Counter for how many lookup of facies in truncation maps had to be modified by slightly shifting the alpha
        # coordinates. This happens if the alpha coordinate for the lookup point is located exactly on the boundary
        # between two polygons and the algorithm is not able to define in which polygon the point is located.
        self._nCountShiftBoundary = 0

        # The key resolution is a resolution of how to round off facies probability.
        # The facies probability rounded off is used as key to classify which grid cells have the same facies
        # probability and can be treated simultaneously when looking up facies in the truncation cubes.
        self._keyResolution = 100

        self._className = self.__class__.__name__
        self._gaussFieldsInZone = []
        self._debug_level = debug_level
        self._keyResolution = keyResolution
        self._nGaussFieldsInBackGroundModel = nGaussFieldsInBackGroundModel

        if trRuleXML is not None:
            if self._debug_level >= Debug.VERY_VERBOSE:
                print(f'--- Read data from model file in: {self._className}')

            if any(
                arg is None
                for arg in [mainFaciesTable, faciesInZone, gaussFieldsInZone]
            ):
                raise ValueError(
                    f'Insufficient arguments; when a truncation rule is given ({trRuleXML}), these arguments are '
                    f'mandatory: "mainFaciesTable", "faciesInZone", and "gaussFieldsInZone"'
                )
            # Initialize common data for facies to be modelled (specified for the zone) and the
            # ordering of the facies in the truncation rule.
            self._setModelledFacies(mainFaciesTable, faciesInZone)

            # Read gauss field names for the background facies truncation rule and assign which gauss field
            # should correspond to each alpha coordinate for truncation rule for background facies (alpha1, alpha2)
            self.__interpretXMLTree_read_gauss_field_names(
                trRuleXML, gaussFieldsInZone, modelFileName
            )
        else:
            if self._debug_level >= Debug.VERY_VERBOSE:
                print(f'--- Create empty object for: {self._className}')
                #  End of __init__

    @property
    def __eps(self) -> float:
        return self._epsFaciesProb

    @property
    def num_facies_in_zone(self) -> int:
        return self._length_of_property(self._faciesInZone)

    @property
    def num_global_facies(self) -> int:
        return self._length_of_property(self._mainFaciesTable)

    @property
    def num_facies_in_truncation_rule(self) -> int:
        return self._length_of_property(self._faciesInTruncRule)

    @staticmethod
    def _length_of_property(prop: Optional[Sized]) -> int:
        return len(prop) if prop else 0

    def _setModelledFacies(
        self, mainFaciesTable: APSMainFaciesTable, faciesInZone: List[str]
    ) -> None:
        """
        Initialize main facies table from input and which facies to model from input.
        """
        if mainFaciesTable is not None:
            self._mainFaciesTable = copy.copy(mainFaciesTable)
        else:
            raise ValueError(f'Error in {self._className}\nError: Inconsistency.')

        # Reference to facies in zone model using this truncation rule
        if faciesInZone is not None:
            self._faciesInZone = copy.copy(faciesInZone)
            self._faciesIsDetermined = np.zeros(self.num_facies_in_zone, dtype=bool)
        else:
            raise ValueError(f'Error in {self._className}\nError: Inconsistency')

        # Facies code for facies in zone
        self._faciesCode = []
        for fName in self._faciesInZone:
            fCode = self._mainFaciesTable.getFaciesCodeForFaciesName(fName)
            self._faciesCode.append(fCode)

    def _setGaussFieldForBackgroundFaciesTruncationMap(
        self,
        gaussFieldsInZone: List[str],
        alphaFieldNameForBackGroundFacies: List[str],
        nGaussFieldsInBackGroundModel: int,
    ) -> None:
        """
        The lists: self._gaussFieldsInZone, self._alphaIndxList and the integer self.getNGaussFieldsInModel()
        are defined. The input names of the alphaFieldNamesForBackGroundFacies (gauss fields) corresponds
        to the alpha coordinate alpha1 and alpha2 and must exist in the self._gaussFieldsInZone list.
        The alphaIndxList define which alpha field corresponds to which specified gauss fields for the zone.
        j = self._alphaIndxList[i] is index in list self._gaussFieldsInZone
        and alpha1 = self._gaussFieldsInZone[self._alphaIndxList[0]]
            alpha2 = self._gaussFieldsInZone[self._alphaIndxList[1]] and so on.
        """
        self._gaussFieldsInZone = copy.copy(gaussFieldsInZone)
        self._alphaIndxList = []
        self._nGaussFieldsInBackGroundModel = nGaussFieldsInBackGroundModel
        assert len(alphaFieldNameForBackGroundFacies) == nGaussFieldsInBackGroundModel
        for i in range(nGaussFieldsInBackGroundModel):
            self.__addAlpha(
                alphaFieldNameForBackGroundFacies[i], createErrorIfExist=False
            )

    def _setOverlayFaciesDataStructure(
        self,
        overlayGroups: Optional[
            List[List[Union[List[List[Union[str, float]]], List[str]]]]
        ],
    ) -> None:
        """
        Initialize data structure from input list of lists.
        Fill the lists self._groupIndxForBackGroundFaciesIndx, self._alphaInGroup,
        self._centerTruncIntervalInGroup, self._overlayFaciesIndxInGroup,
        self._probFracOverlayFaciesInGroup, self._backgroundFaciesInGroup
        and variable self._nGroups
        """
        self._nGroups = 0 if overlayGroups is None else len(overlayGroups)
        # Before assigning overlay facies the number of facies in trunc rule list faciesInTruncRule
        # all facies are background facies.
        self._nBackGroundFacies = self.num_facies_in_truncation_rule
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
            for j in range(nAlpha):
                alphaItem = alphaList[j]
                alphaFieldName = alphaItem[ALPHA_INDX]
                overlayFaciesName = alphaItem[OVERLAY_INDX]
                probFrac = alphaItem[PROBFRAC_INDX]
                centerInterval = alphaItem[CENTERINTERVAL_INDX]

                alphaIndx = self.__addAlpha(alphaFieldName, createErrorIfExist=False)
                alphaFieldIndxListThisGroup.append(alphaIndx)

                nFaciesInTruncRule, indx, fIndx, isNew = self._addFaciesToTruncRule(
                    overlayFaciesName
                )
                if isNew:
                    self._orderIndex.append(fIndx)

                overlayFaciesIndxListThisGroup.append(indx)
                probFracListThisGroup.append(probFrac)
                centerTruncIntervalThisGroup.append(centerInterval)

            bgFaciesListForGroup = groupItem[BACKGROUND_LIST_INDX]
            for bgFaciesName in bgFaciesListForGroup:
                indx = self.getFaciesInTruncRuleIndex(bgFaciesName)
                backGroundFaciesIndxListThisGroup.append(indx)

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
        nBackGroundFac = sum(
            len(self._backgroundFaciesInGroup[groupIndx])
            for groupIndx in range(self._nGroups)
        )
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
                        'Should be less than {1} and not negative'.format(
                            indx, self._nBackGroundFacies
                        )
                    )

                # Check that background facies for this group is not specified multiple times
                if indx in checkIndx:
                    fName = self._faciesInTruncRule[indx]
                    raise ValueError(
                        f'Background facies {fName} is specified multiple times for the same group'
                    )
                checkIndx.append(indx)

                # Check that background facies for this group is not used in other groups
                if indx in checkOverlapForBackGroundFacies:
                    fName = self._faciesInTruncRule[indx]
                    raise ValueError(
                        f'Background facies {fName} is specified for more than one group'
                    )
                checkOverlapForBackGroundFacies.append(indx)

            nAlpha = len(self._alphaInGroup[groupIndx])
            for i in range(nAlpha):
                indx = self._overlayFaciesIndxInGroup[groupIndx][i]

                # Check that overlay facies index is legal
                if indx < self._nBackGroundFacies or indx >= self.num_facies_in_zone:
                    fName = self._faciesInTruncRule[indx]
                    raise ValueError(
                        f'Overlay facies {fName} is not a valid facies name'
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
        sumProbFrac = np.zeros(self.num_facies_in_zone, dtype=float)
        for groupIndx in range(self._nGroups):
            nAlpha = len(self._alphaInGroup[groupIndx])
            for j in range(nAlpha):
                indx = self._overlayFaciesIndxInGroup[groupIndx][j]
                probFrac = self._probFracOverlayFaciesInGroup[groupIndx][j]
                sumProbFrac[indx] += probFrac
                # print('nBackgroundfacies: ' + str(self._nBackGroundFacies))
                # print('nFacies: ' + str(self.num_facies_in_zone))
                # print('faciesInTruncRule:')
                # print(repr(self._faciesInTruncRule))
        for indx in range(self._nBackGroundFacies, self.num_facies_in_zone):
            assert abs(sumProbFrac[indx] - 1.0) <= self._epsFaciesProb

    def __checkCenterTruncInterval(self):
        for groupIndx in range(self._nGroups):
            nAlpha = len(self._alphaInGroup[groupIndx])
            for j in range(nAlpha):
                indx = self._overlayFaciesIndxInGroup[groupIndx][j]
                centerInterval = self._centerTruncIntervalInGroup[groupIndx][j]
                assert 0.0 <= centerInterval <= 1.0

    def __calcGroupIndxForBGFacies(self):
        self._groupIndxForBackGroundFaciesIndx = np.zeros(
            self._nBackGroundFacies, dtype=int
        )
        for i in range(self._nBackGroundFacies):
            self._groupIndxForBackGroundFaciesIndx[i] = -1

        for groupIndx in range(self._nGroups):
            nBackGroundFac = len(self._backgroundFaciesInGroup[groupIndx])
            for i in range(nBackGroundFac):
                indx = self._backgroundFaciesInGroup[groupIndx][i]
                self._groupIndxForBackGroundFaciesIndx[indx] = groupIndx

    def __addAlpha(self, alphaName: str, createErrorIfExist: bool = False) -> int:
        """
        Check that alphaName is a valid name of a gauss field for the zone.
        If a valid name, add a new entry in the list self._alphaIndxList if the gauss field with name alphaName
        is not already used. If the alphaName gauss field is not already used and therefore added,
        the alpha space dimension is increased by one.
        The return value is the  alpha index (The index in the list gaussFieldsInZone for the gauss field
        with name alphaName).
        """
        index = self.getAlphaIndexInZone(alphaName)
        if index >= 0:
            # The alphaName exist in the zone
            if index not in self._alphaIndxList:
                # Add only to the list if the alphaName is not used already
                self._alphaIndxList.append(index)
            else:
                if createErrorIfExist:
                    raise ValueError(
                        'Cannot add gauss field name {} that is already used as alpha parameter'.format(
                            alphaName
                        )
                    )

        else:
            raise ValueError(
                'Error when initializing gauss field names for each alpha coordinate dimension\n'
                'Specified gauss field name {} in truncation rule is not defined for the zone.'
                ''.format(alphaName)
            )
        return index

    def getAlphaIndexInZone(self, alphaName: str) -> int:
        try:
            index = self._gaussFieldsInZone.index(alphaName)
        except ValueError:
            index = -1
        return index

    def __isFaciesInZone(self, fName):
        return fName in self._faciesInZone

    def __interpretXMLTree_read_gauss_field_names(
        self, trRuleXML, gaussFieldsInZone, modelFileName
    ):
        """
        Description: Read gauss field names for alpha1 and alpha2 which is used to create background facies
        """
        self._gaussFieldsInZone = copy.copy(gaussFieldsInZone)
        trRuleTypeXML = trRuleXML[0]
        bgmObj = getKeyword(
            trRuleXML[0],
            'BackGroundModel',
            trRuleTypeXML.tag,
            modelFileName,
            required=True,
        )

        alphaFieldsObj = getKeyword(
            bgmObj, 'AlphaFields', 'BackGroundModel', modelFileName, required=True
        )
        alphaFieldNames = alphaFieldsObj.text.split()
        if len(alphaFieldNames) != self._nGaussFieldsInBackGroundModel:
            raise ValueError(
                f'Error when reading model file: {modelFileName}\n'
                f'Error: Read truncation rule: {self._className}\n'
                f'Error: Number of specified gauss field names must be '
                f'{self._nGaussFieldsInBackGroundModel} under keyword AlphaFields\n'
            )
        for i in range(self._nGaussFieldsInBackGroundModel):
            # Add gauss field
            self.__addAlpha(alphaFieldNames[i], True)

        if self._debug_level >= Debug.VERY_VERBOSE:
            print('--- Background facies truncation rule use:')
            for i in range(self._nGaussFieldsInBackGroundModel):
                print(f'--- Alpha({i}): {alphaFieldNames[i]}')

        assert self.getNGaussFieldsInModel() == self._nGaussFieldsInBackGroundModel

    def _interpretXMLTree_overlay_facies(
        self, trRuleXML: Element, modelFileName: str, zoneNumber: Optional[int]
    ) -> None:
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
            print(
                f'--- Start read overlay facies model in {self._className} from model file'
            )

        # Number of background facies is the facies in truncation rule before overlay facies is added
        self._nBackGroundFacies = self.num_facies_in_truncation_rule

        # Lookup array to find group indx (index in list groups) given background facies indx (index in list faciesInTruncRule)
        # Initialize the array to -1 since not all background facies that is modelled is necessarily used as
        # background for any overlay facies
        self._groupIndxForBackGroundFaciesIndx = np.zeros(
            self._nBackGroundFacies, dtype=int
        )
        for i in range(self._nBackGroundFacies):
            self._groupIndxForBackGroundFaciesIndx[i] = -1

        # Interpret model file for overlay facies
        kw = 'OverLayModel'
        overLayModelObj = getKeyword(
            trRuleXML, kw, 'TruncationRule', modelFileName, required=False
        )
        if overLayModelObj is not None:
            kw1 = 'Group'
            self._groups = []
            groupIndx = 0
            checkBGFaciesList = []
            for overLayGroupObj in overLayModelObj.findall(kw1):
                if overLayGroupObj is None:
                    raise ValueError(
                        f'Missing keyword {kw1} in keyword {kw} in zone {zoneNumber},'
                        f' in truncation rule in model file {modelFileName}'
                    )
                alphaList = []
                centerList = []
                probFracList = []
                overlayFaciesIndxInGroup = []
                kw2 = 'AlphaField'

                for alphaObj in overLayGroupObj.findall(kw2):
                    if alphaObj is None:
                        raise ValueError(
                            f'Missing keyword {kw2} in keyword {kw1} in zone {zoneNumber},'
                            f' in truncation rule in model file {modelFileName}'
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
                            f'Alpha field name: {alphaName} is specified multiple times for'
                            f' group number {groupIndx + 1} in zone {zoneNumber}'
                        )

                    kw3 = 'TruncIntervalCenter'
                    truncIntervalCenter = getFloatCommand(
                        alphaObj,
                        kw3,
                        kw2,
                        minValue=0.0,
                        maxValue=1.0,
                        modelFile=modelFileName,
                        required=True,
                    )
                    centerList.append(truncIntervalCenter)

                    kw4 = 'ProbFrac'
                    probFracObj = getKeyword(
                        alphaObj, kw4, kw2, modelFile=modelFileName, required=True
                    )
                    text = probFracObj.get('name')
                    fName = text.strip()
                    # Check that facies name is not a background facies and that it is defined for the zone
                    if fName not in self._faciesInZone:
                        raise ValueError(
                            f'Specified overlay facies {fName} is not defined for zone {zoneNumber}'
                        )
                    indx = self.getBackgroundFaciesInTruncRuleIndex(fName)
                    if indx >= 0:
                        raise ValueError(
                            f'Specified overlay facies {fName} is already defined as background facies.'
                        )

                    # Add the overlay facies to the list of facies for the truncation rule if not already added
                    nFacies, indx, fIndx, isNew = self._addFaciesToTruncRule(fName)
                    overlayFaciesIndxInGroup.append(indx)
                    if isNew == 1:
                        self._orderIndex.append(fIndx)

                    probFracValue = getFloatCommand(
                        alphaObj,
                        kw4,
                        kw2,
                        minValue=0.0,
                        maxValue=1.0,
                        modelFile=modelFileName,
                        required=True,
                    )
                    probFracList.append(probFracValue)

                if not alphaList:
                    raise ValueError(
                        f'Missing keyword {kw2} in keyword {kw1} in zone {zoneNumber},'
                        f' in truncation rule in model file {modelFileName}'
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
                            f'Missing keyword {kw2} in keyword {kw1} '
                            f'in zone {zoneNumber} in truncation rule in model file {modelFileName}'
                        )
                    text = bgFaciesObj.text
                    bgFaciesName = text.strip()
                    # Check that facies name is a valid facies for the zone
                    if not self.__isFaciesInZone(bgFaciesName):
                        raise ValueError(
                            f'Error when reading model file {modelFileName} for zone {zoneNumber} in truncation rule.\n'
                            f'Error: Specified facies name: {bgFaciesName} as background facies for overlay facies '
                            f'in truncation rule is not defined in this zone.'
                        )
                    # Check that the facies actually is a background facies in the truncation rule.
                    indx = self.getBackgroundFaciesInTruncRuleIndex(bgFaciesName)
                    if indx < 0:
                        raise ValueError(
                            f'Error when reading model file {modelFileName} for zone {zoneNumber} in truncation rule.\n'
                            f'Error: Specified facies name: {bgFaciesName} as background facies for overlay facies in truncation rule is not defined\n'
                            '       in the truncation rule in keyword BackGroundModel or it is used as overlay facies.'
                        )
                    # Check that the facies name is not use previously in the list of background facies for this group
                    if indx in bgFaciesIndxList:
                        raise ValueError(
                            f'Error when reading model file {modelFileName} for zone {zoneNumber} in truncation rule.\n'
                            f'The facies {bgFaciesName} is specified multiple times as background facies in an overlay facies group'
                        )
                    # Check that the facies is not specified in other groups.
                    if indx in checkBGFaciesList:
                        raise ValueError(
                            f'Error when reading model file {modelFileName} for zone {zoneNumber} in truncation rule.\n'
                            f'The facies {bgFaciesName} is specified as background facies in more than one of the overlay facies groups.'
                            ' The implemented method cannot handle this case.'
                        )
                    else:
                        checkBGFaciesList.append(indx)

                    # Facies name should be OK now
                    bgFaciesIndxList.append(indx)

                if not bgFaciesIndxList:
                    raise ValueError(
                        f'Missing keyword {kw2} in keyword {kw1} in zone {zoneNumber},'
                        f' in truncation rule in model file {modelFileName}'
                    )

                for indx in bgFaciesIndxList:
                    self._groupIndxForBackGroundFaciesIndx[indx] = groupIndx

                self._backgroundFaciesInGroup.append(bgFaciesIndxList)

                groupIndx += 1
            if groupIndx == 0:
                raise ValueError(
                    f'Missing keyword {kw1} in keyword {kw} for zone {zoneNumber},'
                    f' in truncation rule in model file {modelFileName}'
                )

            self._nGroups = groupIndx

            # Check that sum of probability fractions is 1.0 for each overlay facies
            sumProbFrac = np.zeros(self.num_facies_in_zone, dtype=float)
            for groupIndx in range(self._nGroups):
                nAlpha = len(self._alphaInGroup[groupIndx])
                for alphaInGroupIndx in range(nAlpha):
                    indx = self._overlayFaciesIndxInGroup[groupIndx][alphaInGroupIndx]
                    probFrac = self._probFracOverlayFaciesInGroup[groupIndx][
                        alphaInGroupIndx
                    ]
                    sumProbFrac[indx] += probFrac

            for indx in range(self.num_facies_in_truncation_rule):
                fName = self._faciesInTruncRule[indx]
                sumPF = sumProbFrac[indx]
                indxBG = self.getBackgroundFaciesInTruncRuleIndex(fName)
                if indxBG < 0 and abs(sumPF - 1.0) > self._epsFaciesProb:
                    raise ValueError(
                        f'Error in model file {modelFileName} for zone {zoneNumber}\n'
                        f' Sum of probability fraction specified for overlay facies {fName} is {sumPF} and not 1.0'
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

            # Check that the number of facies specified in the zone (self.num_facies_in_zone) is equal to the
            # specified number of facies in truncation rule
            if self.num_facies_in_zone != (
                self._nBackGroundFacies + self._nOverLayFacies
            ):
                raise ValueError(
                    f'Number of facies specified for zone {zoneNumber} is: {self.num_facies_in_zone}\n'
                    f'Number of facies in background model is: {self._nOverLayFacies}\n'
                    f'Number of overlay facies is: {self._nBackGroundFacies}\n'
                    f'The sum of number of background facies and overlay facies must match the number of facies for the zone'
                )

            if self._debug_level >= Debug.VERY_VERBOSE:
                print(
                    '--- List of alpha fields used in the zone model. The sequence define the alpha coordinates'
                )
                for i in range(len(self._alphaIndxList)):
                    indx = self._alphaIndxList[i]
                    alphaName = self._gaussFieldsInZone[indx]
                    print(
                        f'--- Alpha coordinate {i + 1} corresponds to gauss field {alphaName}'
                    )
                print(f'--- Dimension of Alpha space is: {len(self._alphaIndxList)}')
                print('')
                print(f'--- Number of overlay facies: {self._nOverLayFacies}')
                print('--- Group index for each background facies')
                for i in range(self._nBackGroundFacies):
                    fName = self._faciesInTruncRule[i]
                    groupIndx = self._groupIndxForBackGroundFaciesIndx[i]
                    if groupIndx >= 0:
                        print(f'---  {fName}  belongs to groupIndx= {groupIndx}')
                    else:
                        print(f'---  {fName} does not belong to any defined group')
                print('')
                print('--- Alpha fields per group and overlay facies defined.')
                for groupIndx in range(self._nGroups):
                    nAlpha = len(self._alphaInGroup[groupIndx])
                    print(
                        f'--- For group with index: {groupIndx}  Number of alpha fields: {nAlpha}'
                    )
                    print('--- Alpha    Facies   TruncIntervalCenter     ProbFrac:')
                    for alphaInGroupIndx in range(nAlpha):
                        alphaIndx = self._alphaInGroup[groupIndx][alphaInGroupIndx]
                        gfname = self._gaussFieldsInZone[alphaIndx]
                        indx = self._overlayFaciesIndxInGroup[groupIndx][
                            alphaInGroupIndx
                        ]
                        fName = self._faciesInTruncRule[indx]
                        centerVal = self._centerTruncIntervalInGroup[groupIndx][
                            alphaInGroupIndx
                        ]
                        probFrac = self._probFracOverlayFaciesInGroup[groupIndx][
                            alphaInGroupIndx
                        ]
                        print(
                            f'---   {gfname}     {fName}      {centerVal}     {probFrac}'
                        )

        if self._debug_level >= Debug.VERY_VERBOSE:
            print(
                f'--- End read overlay facies model in {self._className} from model file'
            )

            # End read overlay facies

    def _isFaciesProbEqualOne(self, faciesProb: List[float]) -> bool:
        """
        Description: Check if facies probability is close to 1.0. Return True or False.
                     This function is used to check if it is necessary to calculate truncation map or not.
        """
        for fIndx in range(len(faciesProb)):
            self._faciesIsDetermined[fIndx] = False
            if faciesProb[fIndx] > (1.0 - self._epsFaciesProb):
                self._faciesIsDetermined[fIndx] = True
                return True
        return False

    def _checkFaciesForZone(self) -> None:
        """
        Description: Check that the facies for the truncation rule is the same
                      as defined for the zone.
        """
        if self.num_facies_in_truncation_rule != self.num_facies_in_zone:
            raise ValueError(
                f'Error: In truncation rule: {self._className} Number of facies specified in truncation rule '
                f'is {self.num_facies_in_truncation_rule} which is different from number'
                f' of facies specified for zone which is {self.num_facies_in_zone}'
            )
        for fName in self._faciesInTruncRule:
            # print('fName in checkFaciesForZone:')
            # print(fName)
            if fName not in self._faciesInZone:
                raise ValueError(
                    f'Error: In truncation rule: {self._className} Facies name {fName} is not defined for the current zone.\n'
                    f'       No probability is defined for this facies for the current zone.'
                )
        for fName in self._faciesInZone:
            if fName not in self._faciesInTruncRule:
                raise ValueError(
                    f'Error: In truncation rule: {self._className} Facies name {fName} which is defined for the current zone '
                    'is not defined in the truncation rule. Cannot have facies with specified '
                    'probability that is not used in the truncation rule.'
                )

    def _addFaciesToTruncRule(self, facies_name: str) -> Tuple[int, int, int, int]:
        """
        Description: Check if facies already exist in list of facies for the truncation rule. If not, add it to
                     the truncation rule and return the index (indx) in faciesInTruncRule as well as index (fIndx)
                     in faciesInZone list.
        """
        isNew = False
        nFaciesInTruncRule = len(self._faciesInTruncRule)
        index = self.getFaciesInTruncRuleIndex(facies_name)
        if index < 0:
            self._faciesInTruncRule.append(facies_name)
            index = nFaciesInTruncRule
            nFaciesInTruncRule += 1
            isNew = True

        fIndx = self.getFaciesInZoneIndex(facies_name)
        if fIndx < 0:
            raise ValueError(
                f'Error in {self._className}. Specified facies name {facies_name} is not defined for this zone.'
            )
        self._nFaciesInTruncRule = nFaciesInTruncRule
        return nFaciesInTruncRule, index, fIndx, isNew

    def writeContentsInDataStructure(self):
        """
        Description: Write contents of data structure for debug purpose.
        """
        print(self.__repr__())

    def __repr__(self) -> str:
        representation = f"""
************  Contents of the data structure common to several truncation algorithms  ***************
Eps for facies prob: {self._epsFaciesProb}
Main facies table:
{self._mainFaciesTable!r}
Number of facies in main facies table: {self.num_global_facies}
Facies to be modelled:
{self._faciesInZone!r}
Facies code per facies to be modelled:
{self._faciesCode!r}
Facies in truncation rule:
{self._faciesInTruncRule!r}
Number of facies to be modelled: {self.num_facies_in_zone}'
Index array orderIndex:
{self._orderIndex}
Logical array with 0 for facies which is has probability 100% and 0 for facies with probability less than 100%
{self._faciesIsDetermined}
Print info level: {self._debug_level}'
Is function setTruncRule called?
{self._setTruncRuleIsCalled}
Background facies:
"""
        for i in range(self._nBackGroundFacies):
            bgFaciesName = self._faciesInTruncRule[i]
            representation += '   {}'.format(bgFaciesName)
        representation += '\n'
        for i in range(self._nGroups):
            num_alpha = len(self._alphaInGroup[i])
            representation += (
                f'\nNumber of facies polygons in group number {i}  is {num_alpha}'
            )
            for j in range(num_alpha):
                alphaIndx = self._alphaInGroup[i][j]
                gfName = self._gaussFieldsInZone[alphaIndx]
                indx = self._overlayFaciesIndxInGroup[i][j]
                fName = self._faciesInTruncRule[indx]
                probFraction = self._probFracOverlayFaciesInGroup[i][j]
                low = self._lowAlphaInGroup[i][j]
                high = self._highAlphaInGroup[i][j]
                representation += (
                    f'Overlay facies polygon number {j} in group {i} belongs to facies {fName}'
                    f' with prob fraction {probFraction} and defined by truncation of {gfName}\n'
                    f'Overlay facies polygon number {j} in group {i} belongs to facies {fName}'
                    f' and is truncated between {low} and {high}'
                )

            for j in range(len(self._backgroundFaciesInGroup[i])):
                indx = self._backgroundFaciesInGroup[i][j]
                fName = self._faciesInTruncRule[indx]
                representation += f'Group number: {i}  Background facies: {fName}'
        representation += f'\nNumber of alpha variables (gauss fields) used in the truncation rule: {self.getNGaussFieldsInModel()}'
        for i in range(self.getNGaussFieldsInModel()):
            alphaIndx = self._alphaIndxList[i]
            gfName = self._gaussFieldsInZone[alphaIndx]
            representation += (
                f'\nAlpha coordinate number {i + 1} corresponds to gauss field {gfName}'
            )
        return representation

    @property
    def names_of_gaussian_fields(self) -> List[str]:
        return self._gaussFieldsInZone

    @names_of_gaussian_fields.setter
    def names_of_gaussian_fields(self, names):
        self._gaussFieldsInZone = names

    def getClassName(self):
        return copy.copy(self._className)

    def getFaciesOrderIndexList(self) -> List[int]:
        return copy.copy(self._orderIndex)

    def getFaciesInTruncRule(self) -> List[str]:
        return copy.copy(self._faciesInTruncRule)

    def getFaciesInTruncRuleIndex(self, fName: str) -> int:
        # Loop over all facies defined in the list faciesInTruncRule
        indx = -1
        for i in range(len(self._faciesInTruncRule)):
            fN = self._faciesInTruncRule[i]
            if fN == fName:
                indx = i
                break
        return indx

    def getBackgroundFaciesInTruncRuleIndex(self, fName: str) -> int:
        # Loop over only the facies defined as background facies
        indx = -1
        for i in range(self._nBackGroundFacies):
            fN = self._faciesInTruncRule[i]
            if fN == fName:
                indx = i
                break
        return indx

    def getFaciesInZoneIndex(self, facies_name: str) -> int:
        # Loop over all facies defined in the list faciesInZone
        try:
            return self._faciesInZone.index(facies_name)
        except ValueError:
            return -1

    def getNGaussFieldsInModel(self) -> int:
        # Number of gauss fields used in the truncation rule (dimension of alpha space)
        return len(self._alphaIndxList)

    def getEpsFaciesProb(self) -> float:
        return self._epsFaciesProb

    def setEpsFaciesProb(self, eps: float):
        if 0.0 < eps < 0.01:
            self._epsFaciesProb = eps
        else:
            raise ValueError(
                f'Try to set tolerance for facies probabilities to {eps}.\n'
                f'Can not set tolerance for facies probability greater than 0.01 or less than equal 0.0'
            )

    def _setMinimumFaciesProb(self, faciesProb):
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

    # TODO: Sjekk ut robusthet av algoritmen i spesialtilfeller med 0 sannsynlighet for en eller flere facies eller hele grupper av facies
    def _modifyBackgroundFaciesArea(self, faciesProb: List[float]) -> np.ndarray:
        """
        Description: Calculate area in trunc map which has corrected for overlay facies.
                     It also calculates truncation intervals for overlay facies for alpha3, alpha4, .., alphaN.
                     This function will also set a minimum probability for robustness of truncation algorithms.
        """
        if self._nGroups == 0:
            return faciesProb

        # The array faciesProb contain probability for all facies, a subset are background facies
        # NOTE: Only the entries in area corresponding to the background facies will be set
        # Set initially -1 into the list area.
        area = np.ones(self.num_facies_in_zone, dtype=float)
        area = -1.0 * area
        for i in range(self._nBackGroundFacies):
            fIndx = self._orderIndex[i]
            area[fIndx] = faciesProb[fIndx]
        self._lowAlphaInGroup = []
        self._highAlphaInGroup = []

        # Probability of the N dimensional polygon in alpha space defined by background facies and overlay facies
        # for each group must be calculated.
        sumTotProb = 0.0
        sumProbBackGround = np.zeros(self._nGroups, dtype=float)
        sumProbOverlay = np.zeros(self._nGroups, dtype=float)
        sumProb = np.zeros(self._nGroups, dtype=float)
        if self._debug_level >= Debug.VERY_VERY_VERBOSE:
            print('\n')
            print(
                '--- Calculate modified area for background facies and threshold values for overlay facies:'
            )

        for groupIndx in range(self._nGroups):
            # Sum over probability for background facies
            for indx in self._backgroundFaciesInGroup[groupIndx]:
                fIndx = self._orderIndex[indx]
                prob = faciesProb[fIndx]
                sumProbBackGround[groupIndx] += prob

            # Sum over overlay facies probability for this group
            nAlpha = len(self._alphaInGroup[groupIndx])
            for j in range(nAlpha):
                indx = self._overlayFaciesIndxInGroup[groupIndx][j]
                fIndx = self._orderIndex[indx]
                prob = faciesProb[fIndx]
                probFrac = self._probFracOverlayFaciesInGroup[groupIndx][j]
                if not probFrac > 0.0:
                    raise ValueError(
                        f'Found a probability fraction {probFrac} which is not positive.'
                    )
                prob = prob * probFrac
                sumProbOverlay[groupIndx] += prob

            sumProb[groupIndx] = (
                sumProbBackGround[groupIndx] + sumProbOverlay[groupIndx]
            )
            if self._debug_level >= Debug.VERY_VERY_VERBOSE:
                print(
                    f'--- Group {groupIndx}: '
                    f'Background facies prob={sumProbBackGround[groupIndx]} '
                    f'Overlay facies prob={sumProbOverlay[groupIndx]}   '
                    f'Sum prob= {sumProb[groupIndx]}'
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
                # Sum of background facies and overlay facies is 0 for this group. Set area to 0.0 for all
                # background facies in this group and set truncation interval to 0 for overlay facies in this group.
                for j in range(nBackGroundFaciesInGroup):
                    indx = self._backgroundFaciesInGroup[groupIndx][j]
                    fIndx = self._orderIndex[indx]
                    area[fIndx] = 0.0
                for j in range(nAlpha):
                    # print('groupIndx, nAlpha, indx j: ' + str(groupIndx) + ' ' + str(nAlpha) + ' ' + str(j))
                    indx = self._overlayFaciesIndxInGroup[groupIndx][j]
                    lowAlphaThisGroup.append(0.0)
                    highAlphaThisGroup.append(0.0)
            else:
                B = 1.0
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
                        B *= 1.0 - delta
                        D = D * (1.0 - delta)
                    deltaAlphaThisGroup.append(delta)

                if abs(sumProbBackGround[groupIndx]) < self._epsFaciesProb:
                    # Loop over all background facies in group and assign equal area to each background facies
                    # such that the sum is equal to the sum of probability for the group.
                    # NOTE: It is not unique how to split the area into the background facies in this case. This will
                    # have influence on the geometry of the realization, but the facies fraction is correct anyway.
                    for j in range(nBackGroundFaciesInGroup):
                        indx = self._backgroundFaciesInGroup[groupIndx][j]
                        fIndx = self._orderIndex[indx]
                        area[fIndx] = sumProb[groupIndx] / nBackGroundFaciesInGroup
                else:
                    for j in range(nBackGroundFaciesInGroup):
                        indx = self._backgroundFaciesInGroup[groupIndx][j]
                        fIndx = self._orderIndex[indx]
                        prob = faciesProb[fIndx]
                        area[fIndx] = 0.0 if abs(B) < self._epsFaciesProb else prob / B
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
            if self._lowAlphaInGroup:
                print('--- Low threshold values for overlay facies:')
                print(repr(self._lowAlphaInGroup))
                print('--- High threshold values for overlay facies:')
                print(repr(self._highAlphaInGroup))
            print(
                '--- Finished calculate modified area for background facies and threshold values for overlay facies'
            )
            print('')
        return area

    def _truncateOverlayFacies(
        self, indx: int, alphaCoord: np.ndarray
    ) -> Tuple[int, int]:
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
        if len(self._groupIndxForBackGroundFaciesIndx) == 0:
            groupIndx = -1
        else:
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
                if (
                    self._lowAlphaInGroup[groupIndx][i]
                    < alphaValue
                    <= self._highAlphaInGroup[groupIndx][i]
                ):
                    indx = self._overlayFaciesIndxInGroup[groupIndx][i]
                    break

        fIndx = self._orderIndex[indx]
        faciesCode = self._faciesCode[fIndx]
        return faciesCode, fIndx

    def _truncateOverlayFacies_vectorized(
        self, bg_index_in_trunc_rule, alpha_coord_vectors
    ):
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
        order_index = np.asarray(self._orderIndex)
        facies_codes = np.asarray(self._faciesCode)
        index_vector = bg_index_in_trunc_rule
        num_index_values = index_vector.max() + 1
        group_index_for_bg_facies_index = np.asarray(
            self._groupIndxForBackGroundFaciesIndx
        )
        groupIndx_vector = group_index_for_bg_facies_index[index_vector]
        for m in range(num_index_values):
            # Lookup which overlay group the background facies faciesInTruncRule[indx] belongs to if any.

            groupIndx = self._groupIndxForBackGroundFaciesIndx[m]
            if groupIndx >= 0:
                index_selected = index_vector == m
                num_selected = index_selected.sum()
                # The background facies is defined by the input variable 'indx' and the facies name is
                # faciesInTruncRule[indx]. This background facies belongs to the group with index groupIndx.
                # The overlay facies in this group may overprint the background facies.
                # The sequence of overlay facies is determined by the sequence
                #  of alpha fields. So the sequence of alpha fields defined by the alphaInGroup and the corresponding
                # sequence of facies define the internal priority of which overlay facies is truncated or not by the
                # other overlay facies in this group. Note that overlay facies from different groups are independent of
                # each other. This code can be extended to have multiple overlay facies defined by the same alpha field,
                # by calculating threshold values for the alpha value for each facies, but so far only one overlay facies
                # is defined for each alpha field.
                set_overlay_facies_index = np.zeros(len(index_vector), dtype=int)
                nAlpha = len(self._alphaInGroup[groupIndx])
                for i in range(nAlpha):
                    alphaIndx = self._alphaInGroup[groupIndx][i]
                    alphaValue = alpha_coord_vectors[:, alphaIndx]

                    # Check if value is within the interval which define the overlay facies.
                    # Note that the loop over all alpha fields define the sequence in which the overlay facies is defined
                    inside_truncation_interval = (
                        index_selected
                        & (alphaValue > self._lowAlphaInGroup[groupIndx][i])
                        & (alphaValue <= self._highAlphaInGroup[groupIndx][i])
                    )
                    set_overlay_facies_index = (
                        set_overlay_facies_index == False
                    ) & inside_truncation_interval
                    index_vector[set_overlay_facies_index] = (
                        self._overlayFaciesIndxInGroup[groupIndx][i]
                    )

        fIndx_vector = order_index[index_vector]
        faciesCode_vector = facies_codes[fIndx_vector]
        return faciesCode_vector, fIndx_vector

    def _XMLAddElement(self, parent: Element) -> None:
        """
        Description: Write to xml tree the keywords related to overlay facies
        """
        if self._debug_level >= Debug.VERY_VERBOSE:
            print('--- call XMLADDElement from Trunc2D_Base_xml')
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
                trcElement.text = f' {self._centerTruncIntervalInGroup[groupIndx][j]} '
                alphaElement.append(trcElement)

                indx = self._overlayFaciesIndxInGroup[groupIndx][j]
                fName = self._faciesInTruncRule[indx]
                tag = 'ProbFrac'
                attribute = {'name': fName}
                probFracElement = Element(tag, attribute)
                probFracElement.text = (
                    f' {self._probFracOverlayFaciesInGroup[groupIndx][j]} '
                )
                alphaElement.append(probFracElement)

            nBackgroundFaciesInGroup = len(self._backgroundFaciesInGroup[groupIndx])
            for j in range(nBackgroundFaciesInGroup):
                indx = self._backgroundFaciesInGroup[groupIndx][j]
                fName = self._faciesInTruncRule[indx]
                tag = 'BackGround'
                bgElement = Element(tag)
                bgElement.text = ' ' + fName + ' '
                groupElement.append(bgElement)

    @staticmethod
    def _makeKey(faciesProbRoundOff) -> Tuple[float, ...]:
        """Use round off of facies probability as key in dictionary. Make a tuple from the facies probability array."""
        key = tuple(faciesProbRoundOff)
        return key

    def _makeRoundOffFaciesProb(self, facies_prob):
        """Calculate round off of facies probabilities and adjusted
        so that the round off values also are close to normalised
        Resolution is set to 100 if input is not positive. The case that memoization is turned off
        corresponds to input resolution = 0 and in this case 100 is always used.
        """
        if len(facies_prob) == 0:
            warn('The facies probabilities are empty')
            return facies_prob
        # A value of 0 or negative indicates that memoization is turned off.
        # Anyway the probabilities will be rounded off to nearest 1/100.
        resolution = 100 if self._keyResolution <= 0 else self._keyResolution
        delta = 1.0 / resolution
        facies_prob = (facies_prob * resolution + 0.5).astype(int) * delta
        sum_prob = facies_prob.sum()
        index_max = facies_prob.argmax()
        if sum_prob > (RoundOffConstant.low + delta):
            facies_prob[index_max] -= delta
            sum_prob -= delta
            if sum_prob > (RoundOffConstant.low + delta):
                facies_prob[index_max] -= delta
                sum_prob -= delta
        elif sum_prob < (RoundOffConstant.high - delta):
            facies_prob[index_max] += delta
            sum_prob += delta
            if sum_prob < (RoundOffConstant.high - delta):
                facies_prob[index_max] += delta
                sum_prob += delta
        return facies_prob

    @property
    def gaussian_fields_in_truncation_rule(self) -> List[str]:
        return self.getGaussFieldsInTruncationRule()

    def getGaussFieldsInTruncationRule(self) -> List[str]:
        # Return list of the gauss field names actually used in the truncation rule
        gfUsed = []
        for index in self._alphaIndxList:
            gfName = self._gaussFieldsInZone[index]
            gfUsed.append(gfName)
        return gfUsed

    def getGaussFieldIndexListInZone(self) -> List[int]:
        return copy.copy(self._alphaIndxList)

    @staticmethod
    def _isInsidePolygon(
        polygon: Union[List[List[float]], List[Union[List[int], List[np.float64]]]],
        xInput: Union[np.float32, np.float64],
        yInput: Union[np.float32, np.float64],
    ) -> bool:
        """Function related to the LBL (Linear Boundary Lines) truncation rule.
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
            if vyp != 0.0:
                s = (yInput - y0) / vyp
                vxp = x1 - x0
                x = x0 + s * vxp
                t = x - xInput
                if 0.0 <= s <= 1.0 and t > 0:
                    # intersection between the line y = pt[1] and the polygon line
                    # between the points polygon[i-1] and polygon[i] in one direction
                    # from the point pt
                    num_intersections_found += 1

        # Point pt is inside the closed polygon iff there is an odd number of intersections
        return num_intersections_found % 2 != 0

    @staticmethod
    def _isInsidePolygon_vectorized(polygon, x_coordinates, y_coordinates, poly_number):
        """Take as input a polygon and x and y vectors of the coordinates to many points
        and return a vector with True/False whether the points are inside or outside the polygon.
        """
        # Calculate intersection between a straight line through the input point pt and the closed polygon
        # in one direction from the point. If the number of intersections are odd number (1,3,5,..),
        # the point is inside, if the number of intersections are even (0,2,4,..) the point is outside.
        n = len(polygon)
        p = polygon[0]
        x1 = p[0]
        y1 = p[1]
        num_intersections_found = np.zeros(len(x_coordinates), dtype=int)
        polygon_numbers = np.ones(len(x_coordinates), dtype=int) * (-1)
        for i in range(1, n):
            x0 = x1
            y0 = y1
            p = polygon[i]
            x1 = p[0]
            y1 = p[1]
            vyp = y1 - y0
            vxp = x1 - x0
            if vyp != 0.0:
                s = (y_coordinates - y0) / vyp
                x = s * vxp + x0
                t = x - x_coordinates
                intersections = (s >= 0.0) & (s <= 1.0) & (t > 0)
                # intersection between the line y = pt[1] and the polygon line
                # between the points polygon[i-1] and polygon[i] in one direction
                # from the point pt
                num_intersections_found[intersections] += 1

        # Value of check is 0 if number of intersections is even which means outside polygon
        # and the value is  not equal to 0 if number of intersections is uneven which means inside polygon
        check = num_intersections_found % 2
        polygon_numbers[check != 0] = poly_number
        return polygon_numbers

    def getOrderIndex(self):
        return self._orderIndex

    def defineFaciesByTruncRule(
        self, alphaCoord: Union[np.ndarray, List[float]]
    ) -> Tuple[int, int]:
        """
        Description: Apply the truncation rule to find facies.
        """
        x = alphaCoord[self._alphaIndxList[0]]
        y = alphaCoord[self._alphaIndxList[1]]
        # Check if the facies is deterministic (100% probability)
        for fIndx in range(len(self._faciesInZone)):
            if self._faciesIsDetermined[fIndx]:
                faciesCode = self._faciesCode[fIndx]
                return faciesCode, fIndx

        # Input is facies polygons for truncation rules and two values between 0 and 1
        # Check in which polygon the point is located and thereby the facies
        inside = False
        faciesCode = -999
        fIndx = -999
        for i in range(self.num_polygons):
            polygon = self._faciesPolygons[i]
            inside = self._isInsidePolygon(polygon, x, y)
            if not inside:
                continue
            else:
                if self._className == 'Trunc3D_bayfill':
                    indx = self.facies_index_in_truncation_rule_for_polygon(i)
                    z = alphaCoord[self._alphaIndxList[2]]
                    useZ = self.getUseZ()
                    z_truncation_value = self.getZTruncationValue()
                    if useZ and indx == 3 and z < z_truncation_value:
                        indx = 2

                else:
                    indx = self.facies_index_in_truncation_rule_for_polygon(i)

                # For bayfill rule this function only calculates facies code and fIndx given indx
                faciesCode, fIndx = self._truncateOverlayFacies(indx, alphaCoord)
                break
        if not inside:
            # Problem to identify which polygon in truncation map the point is within.
            # Try once more but now by minor shift of the input point.

            # Count the number of times in total for all cells this problem appears.
            self._nCountShiftBoundary += 1

            # Shift the point slightly and check again
            xNew = x + RoundOffConstant.shift_tolerance
            if xNew >= 1.0:
                xNew = x - RoundOffConstant.shift_tolerance
            yNew = y + RoundOffConstant.shift_tolerance
            if yNew >= 1.0:
                yNew = y - RoundOffConstant.shift_tolerance

            for i in range(self.num_polygons):
                polygon = self._faciesPolygons[i]
                inside = self._isInsidePolygon(polygon, xNew, yNew)
                if not inside:
                    continue
                else:
                    if self._className == 'Trunc3D_bayfill':
                        indx = self.facies_index_in_truncation_rule_for_polygon(i)
                        z = alphaCoord[self._alphaIndxList[2]]
                        useZ = self.getUseZ()
                        z_truncation_value = self.getZTruncationValue()
                        if useZ and indx == 3 and z < z_truncation_value:
                            indx = 2
                    else:
                        indx = self.facies_index_in_truncation_rule_for_polygon(i)

                    # For bayfill rule this function only calculates facies code and fIndx given indx
                    faciesCode, fIndx = self._truncateOverlayFacies(indx, alphaCoord)
                    break
            if not inside:
                print(f'Not inside any polygons, x,y: {x} {y}')
                for i in range(self.num_polygons):
                    polygon = self._faciesPolygons[i]
                    print(f'poly number {i}')
                    for point in polygon:
                        print(f'point ({point[0]}, {point[1]})')

            assert inside is True

        return faciesCode, fIndx

    def defineFaciesByTruncRule_vectorized(self, alpha_coord_vectors):
        """
        Description: Apply the truncation rule to find facies.
        """
        # Check if the facies is deterministic (100% probability)
        for fIndx in range(len(self._faciesInZone)):
            if self._faciesIsDetermined[fIndx]:
                facies_code = self._faciesCode[fIndx]
                fIndx_vector = (
                    np.ones(
                        len(alpha_coord_vectors[:, self._alphaIndxList[0]]), dtype=int
                    )
                    * fIndx
                )
                faciesCode_vector = (
                    np.ones(
                        len(alpha_coord_vectors[:, self._alphaIndxList[0]]),
                        dtype=np.uint8,
                    )
                    * facies_code
                )
                return faciesCode_vector, fIndx_vector

        x_coordinates = alpha_coord_vectors[:, self._alphaIndxList[0]]
        y_coordinates = alpha_coord_vectors[:, self._alphaIndxList[1]]
        polygon_number_all_vector = np.ones(len(x_coordinates), dtype=int) * (-1)
        # Input is facies polygons for truncation rules and coordinates in alpha space for
        # for a set of points saved in vectors of length equal to the set of points.
        # Check in which polygon the points are located and thereby the facies
        faciesCode_vector = np.ones(len(x_coordinates), dtype=np.uint8) * (-1)
        for poly_number in range(self.num_polygons):
            polygon = self._faciesPolygons[poly_number]
            selected = polygon_number_all_vector == -1
            x_coordinates_selected = x_coordinates[selected]
            y_coordinates_selected = y_coordinates[selected]

            # Assign polygon number to those points that are inside the current polygon
            # All other points in the selection will still be unassigned and have value -1.
            polygon_number_selected = self._isInsidePolygon_vectorized(
                polygon,
                x_coordinates_selected,
                y_coordinates_selected,
                poly_number,
            )

            # The array with all points are updated for the selected points that are not previously assigned
            polygon_number_all_vector[selected] = polygon_number_selected

        if polygon_number_all_vector.min() == -1:
            selected = polygon_number_all_vector == -1
            # There are still some points which is not assigned to any polygon for numerical reasons
            # Shift slightly the points which is not assigned to any polygon and re-calculate
            for poly_number in range(self.num_polygons):
                polygon = self._faciesPolygons[poly_number]
                selected = polygon_number_all_vector == -1
                # Shift the point slightly and check again
                if polygon_number_all_vector.min() == -1:
                    x_coordinates_selected = (
                        x_coordinates[selected] + RoundOffConstant.shift_tolerance
                    )
                    x_coordinates_selected[x_coordinates_selected >= 1.0] = (
                        x_coordinates_selected[x_coordinates_selected >= 1.0]
                        - 2.0 * RoundOffConstant.shift_tolerance
                    )
                    y_coordinates_selected = (
                        y_coordinates[selected] + RoundOffConstant.shift_tolerance
                    )
                    y_coordinates_selected[y_coordinates_selected >= 1.0] = (
                        y_coordinates_selected[y_coordinates_selected >= 1.0]
                        - 2.0 * RoundOffConstant.shift_tolerance
                    )
                    polygon_number_selected = self._isInsidePolygon_vectorized(
                        polygon,
                        x_coordinates_selected,
                        y_coordinates_selected,
                        poly_number,
                    )
                    polygon_number_all_vector[selected] = polygon_number_selected

            selected = polygon_number_all_vector == -1
            num_points_not_in_polygons = len(polygon_number_all_vector[selected])
            if num_points_not_in_polygons > 0:
                raise ValueError(
                    f'Internal error: Number of points with alpha coordinates outside unit square is: {num_points_not_in_polygons}'
                )

        # Get background facies index and background facies for each point
        assert polygon_number_all_vector.min() >= 0
        bg_index_in_trunc_rule = self.get_background_index_in_truncaction_rule()

        # This vector contains for each point the index in the list of facies in truncation rule table self._faciesInTruncRule
        # It means that self._faciesInTruncRule[index] is the name of the facies used in the truncation rule.
        bg_index_vector = bg_index_in_trunc_rule[polygon_number_all_vector]
        if self._className == 'Trunc3D_bayfill':
            # Special case for handling of the alpha3 coordinate to determine facies
            z_coordinates = alpha_coord_vectors[:, self._alphaIndxList[2]]
            useZ = self.getUseZ()
            z_truncation_value = self.getZTruncationValue()
            if useZ:
                selected = (bg_index_vector == 3) & (z_coordinates < z_truncation_value)
                bg_index_vector[selected] = 2
            order_index = np.asarray(self._orderIndex)
            facies_codes = np.asarray(self._faciesCode)
            fIndx_vector = order_index[bg_index_vector]
            faciesCode_vector = facies_codes[fIndx_vector]
        else:
            # The overlay facies is determined for the other truncation algorithms
            if self._nGroups == 0:
                # No overlay facies
                order_index = np.asarray(self._orderIndex)
                facies_codes = np.asarray(self._faciesCode)
                fIndx_vector = order_index[bg_index_vector]
                faciesCode_vector = facies_codes[fIndx_vector]
            else:
                # Calculate facies for the case that overlay facies is possible
                faciesCode_vector, fIndx_vector = (
                    self._truncateOverlayFacies_vectorized(
                        bg_index_vector, alpha_coord_vectors
                    )
                )
        return faciesCode_vector, fIndx_vector

    def facies_index_in_truncation_rule_for_polygon(self, polygon_number):
        # Is only implemented in sub classes
        raise NotImplementedError

    def get_background_index_in_truncaction_rule(self):
        # Is only implemented in sub classed
        raise NotImplementedError
