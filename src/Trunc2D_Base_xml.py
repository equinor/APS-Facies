#!/bin/env python
import copy
import numpy as np

from xml.etree.ElementTree import Element


"""
-----------------------------------------------------------------------
class Trunc2D_Base
Description: This class is used as a base class for class Trunc2D_Cubic_Multi_OverLay and Trunc2D_Angle_Multi_OverLay.
             It contains common data used by both and common functions related to common data.
  
 Public member functions:
 Constructor:    def __init__(self)



 Protected functions (To be called from derived classes only, not public functions):
 def __setEmpty()
 def _setModelledFacies(mainFaciesTable, faciesInZone)
 def _isFaciesInZone(fName)
 def _interpretXMLTree_overlay_facies(trRuleXML, modelFileName)
 def _isFaciesProbEqualOne(faciesProb)
 def _checkFaciesForZone()
 def _addFaciesToTruncRule(fName)
 def _defineBackgroundFaciesAndOverLayFacies(backGroundFaciesGroups=None, 
                                             overlayFacies=None, 
                                             overlayTruncCenter=None)
 def _setMinimumFaciesProb(faciesProb)
 def _modifyBackgroundFaciesArea(faciesProb)
 def _truncateOverlayFacies(indx,alphaCoord)
 def _XMLAddElement(self, parent)


 Public functions:
 def writeContentsInDataStructure()
 def getClassName()
 def getFaciesOrderIndexList()
 def getFaciesInTruncRule()
 def getNGaussFieldsInModel()
-------------------------------------------------------------
"""


class Trunc2D_Base:
    """
    Description: This class implements common data structure and is a base class for 
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

                 Data organization related to overlay/overprint facies and associated background facies:

                 TODO: Beskriv her mer om data strukturen relatert til overlay facies.
    """
    def __setEmpty(self):
        """
        Description: Initialize the data structure for empty object. 
                     Need to be called by initialization functions in derived classes.
        """
        # Common variables for the class Trunc2D_Cubic_Multi_OverLay and Trunc2D_Angle_Multi_OverLay
        # Tolerance used for probabilities
        self._eps = 0.0001

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
        self._faciesIsDetermined = []

        # Is set to a value from 0 to 3 and the lower the value, the less output is printed to screen
        # Value 3 result in output of debug info details.
        self._printInfo = 0

        # Is used to check if truncation map is initialized or not. E.g. truncation map polygons
        # depends on having calculated truncation map.
        self._setTruncRuleIsCalled = False

        # This variable will contain number of Gauss fields required by the specification of the
        # truncation rule. If no overlay facies is specified, it is 2.
        self._nGaussFieldInModel = 2


        # Variables containing specification of overlay facies model
        
        # Number of facies defined if no overlay facies is specified. These are also called background facies.
        self._nBackGroundFacies = 0

        # Number of overlay facies.
        self._nOverLayFacies = 0

        # 2D Index list. First index is index from 0 to nOverLayFacies-1 (called group index) 
        # Second index go from 0 to number of background facies for this overlay facies.
        self._backGroundFaciesIndx = []

        # 2D Logical (0/1) index list. First index is index from 0 to nOverLayFacies-1 (called group index)
        # Second index go from 0 to nFacies-1 and is the index used in faciesInTruncRule.
        # The values are 1 if the facies is a member of the group of background facies corresponding
        # to the overlay facies (defined by the group index) and 0 if not.
        self._isBackGroundFacies = None

        # This list will take as input an index from 0 to nOverLayFacies-1 (group index) and return index for the overlay facies
        # in the faciesInTruncRule list
        self._overlayFaciesIndx = []

        # A list with lower truncation value for overlay facies. The index is overlay facies index (group index).
        self._lowAlpha = []

        # A list with upper truncation value for overlay facies. The index is overlay facies index (group index).
        self._highAlpha = []

        # A list with value for the center point of the interval between low and high truncation value.
        # The index is overlay facies index (group index)
        self._overLayTruncIntervalCenter = []

    def __init__(self):
        """
           Description: Base class constructor. 
        """
        # Initialize data structure
        self.__setEmpty()
        self._className = 'Trunc2D_Base'
        #  End of __init__

    def _setModelledFacies(self, mainFaciesTable, faciesInZone):
        """
        Description:  Initialize main facies table from input and which facies to model from input.
        """
        if mainFaciesTable is not None:
            self._mainFaciesTable = copy.copy(mainFaciesTable)
            self._nFaciesMain = self._mainFaciesTable.getNFacies()
        else:
            raise ValueError(
                'Error in {}\n'
                'Error: Inconsistency.'
                ''.format(self._className)
            )

        # Reference to facies in zone mode using this truncation rule
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

    def _isFaciesInZone(self,fName):
        if fName in self._faciesInZone:
            return True
        else:
            return False
    
    def _interpretXMLTree_overlay_facies(self, trRuleXML, modelFileName):
        """
        Description: Read specification of one or more overlay facies and which region (set of background facies)
                     the overlay facies is defined to be located. A requirement is that the background facies 
                     for each overlay facies is not overlapping. It is not allowed to specify the same facies 
                     as background facies for two different overlay facies.
        Input: trRuleXML - Pointer refering to XML tree where to find info about the truncation rule. All derived classes has a
               truncation rule containing the same keywords for overprint facies and associated background facies.
               modelFileName - Only used as a text string when printing error messages in order to make them more informative.
        """

        kw = 'OverLayFacies'
        self._nBackGroundFacies = len(self._faciesInTruncRule)
        nOverLayFacies = 0
        self._backGroundFaciesIndx = []
        for overLayObj in trRuleXML.findall(kw):
            if overLayObj is not None:
                nOverLayFacies += 1
                bgFaciesIndxList = []
                self._backGroundFaciesIndx.append(bgFaciesIndxList)
        if nOverLayFacies == 0:
            return

        if self._printInfo >= 3:
            print('Debug output: Number of overlay facies is : ' + str(nOverLayFacies))

        # Check that number of gauss fields in model match the required number in this model
        if self._nGaussFieldInModel != (nOverLayFacies + 2):
            raise ValueError('Mismatch in specification of truncation rule: {0} in model file: {1} regarding number of gaussian fields'
                             ''.format(self._className, modelFileName)
                             )

        self._isBackGroundFacies = np.zeros((nOverLayFacies,len(self._faciesInZone)), dtype=int)
        groupIndx = 0
        for overLayObj in trRuleXML.findall(kw):
            if overLayObj is not None:
                text = overLayObj.get('name')
                fNameOverLayFacies = text.strip()
                if fNameOverLayFacies not in self._faciesInZone:
                    raise ValueError(
                        'Error when reading truncation rule: {0} in model file: {1} \n'
                        'Specified facies name {2} is not defined.'
                        ''.format(self._className, modelFileName, fNameOverLayFacies)
                        )

                kw1 = 'TruncIntervalCenter'
                ticObj = overLayObj.find(kw1)
                # Set default value 
                center = 0.0 
                if ticObj is not None:
                    text = ticObj.text
                    center = float(text.strip())
                    if center < 0.0:
                        center = 0.0
                    if center > 1.0:
                        center = 1.0
                    self._overLayTruncIntervalCenter.append(center)

                kw2 = 'Background'
                bgFaciesIndxList = self._backGroundFaciesIndx[groupIndx]
                for bgObj in overLayObj.findall(kw2):
                    text = bgObj.text
                    bgFaciesName = text.strip()
                    # Check that background facies is defined and if defined, add to list
                    indx = self._getBackgroundFaciesInTruncRuleIndex(bgFaciesName)
                    if indx < 0:
                        raise ValueError(
                            'Error when reading model file: {}\n'
                            'Error: Read truncation rule: {}\n'
                            'Error: Specified facies name as background facies in truncation rule: {} is not defined\n'
                            '       or is defined as overlay facies.'
                            ''.format(modelFileName, self._className, bgFaciesName)
                            )
                    bgFaciesIndxList.append(indx)
                    self._isBackGroundFacies[groupIndx,indx] = 1
                groupIndx += 1

                [nFacies, indx, fIndx, isNew] = self._addFaciesToTruncRule(fNameOverLayFacies)
                if isNew == 1:
                    self._overlayFaciesIndx.append(indx)
                    self._orderIndex.append(fIndx)
                else:
                    raise ValueError(
                        'Error in {0}. Specified overlay facies {1} '
                        'is already used as background facies or overlay facies.'
                        ''.format(self._className,fNameOverLayFacies)
                        )

            else:
                raise ValueError(
                    'Error in {0}. Missing keyword {1} in truncation rule.'
                    ''.format(self._className, kw)
                    )

        # Check that background facies regions for different overlay facies does not have
        # common facies.
        for groupIndx1 in range(len(self._overlayFaciesIndx)):
            bgFaciesIndxList1 = self._backGroundFaciesIndx[groupIndx1]
            for groupIndx2 in range(groupIndx1+1,len(self._overlayFaciesIndx)):
                bgFaciesIndxList2 = self._backGroundFaciesIndx[groupIndx2]
                for indx1 in bgFaciesIndxList1:
                    if indx1 in bgFaciesIndxList2:
                        raise ValueError(
                            'Error in {0}. Facies name: {1} is specified as background facies '
                            'for more than one overlay facies.'
                            ''.format(self._className, self._faciesInTruncRule[indx1]) 
                            )
        self._nOverLayFacies = len(self._overlayFaciesIndx)

        if len(self._faciesInTruncRule) != self._nFacies:
            raise ValueError(
                'Error when reading model file: {0}\n'
                'Error: Read truncation rule: {1}\n'
                'Error: Mismatch in number of facies specified in truncation rule: {2}\n'
                '       and number of facies to be modelled for the zone: {3}.'
                ''.format(modelFileName, self._className,str(len(self._faciesInTruncRule)),str(self._nFacies))
            )
        # End read overlay facies

    def _isFaciesProbEqualOne(self,faciesProb):
        """
        Description: Check if facies probability is close to 1.0. Return True or False.
                     This function is used to check if it is necessary to calculate truncation map or not.
        """
        isDetermined = 0
        for fIndx in range(len(faciesProb)):
            self._faciesIsDetermined[fIndx] = 0
            if faciesProb[fIndx] > (1.0 - self._eps):
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
                'is different from number of facies specified for zone'
                ''.format(self._className)
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
        indx = self._getFaciesInTruncRuleIndex(fName)
        if indx < 0:
            self._faciesInTruncRule.append(fName)
            indx = nFaciesInTruncRule
            nFaciesInTruncRule += 1
            isNew = 1

        fIndx = self._getFaciesInZoneIndex(fName)
        if fIndx < 0:
            raise ValueError('Error in {0}. Specified facies name {1} is not defined for this zone.'
                             ''.format(self._className,fName)
                             )
        self._nFaciesInTruncRule = nFaciesInTruncRule
        return [nFaciesInTruncRule, indx, fIndx, isNew]

    def writeContentsInDataStructure(self):
        """
        Description: Write contents of data structure for debug purpose.
        """
        print(' ')
        print('************  Contents of the data structure common to several truncation algorithms  ***************')
        print('Eps: ' + str(self._eps))
        print('Main facies table:')
        print(repr(self._mainFaciesTable))
        print('Number of facies in main facies table: ' + str(self._nFaciesMain))
        print('Facies to be modelled: ')
        print(repr(self._faciesInZone))
        print('Facies code per facies to be modelled:')
        print(repr(self._faciesCode))
        print('Facies in truncation rule:')
        print(repr(self._faciesInTruncRule))
        print('Number of facies to be modelled:' + str(self._nFacies))
        print('Index array orderIndex: ')
        print(repr(self._orderIndex))
        print('Facies index for facies which has 100% probability')
        print(repr(self._faciesIsDetermined))
        print('Print info level: ' + str(self._printInfo))
        print('Is function setTruncRule called? ')
        print(repr(self._setTruncRuleIsCalled))
        print('Number of Gauss fields in model: ' + str(self._nGaussFieldInModel))
        print('Background facies index for each overlay facies:')
        for i in range(len(self._backGroundFaciesIndx)):
            list = self._backGroundFaciesIndx[i]
            print('Group number: ' + str(i))
            for j in range(len(self._backGroundFaciesIndx[i])):
                indx = self._backGroundFaciesIndx[i][j]
                print('Indx: ' + str(indx) + ' Facies: ' + self._faciesInTruncRule[indx])
        print('Is the facies a background facies: ')
        print(repr(self._isBackGroundFacies))
        print('Number of overlay facies: ' + str(self._nOverLayFacies))
        print('Overlay facies index:')
        print(repr(self._overlayFaciesIndx))
        print('Low Alpha: ')
        print(repr(self._lowAlpha))
        print('High Alpha: ')
        print(repr(self._highAlpha))
        print('Overlay parameter for truncation interval center: ')
        print(repr(self._overLayTruncIntervalCenter))

    def _defineBackgroundFaciesAndOverLayFacies(self, backGroundFaciesGroups=None, 
                                                overlayFacies=None, overlayTruncCenter=None):
        """
        Define the class member variables that is used to handle overlay facies.
               This function is used when initializing truncation rule data structure for derived classed
               and when the initializing is not done by reading xml tree, but initialized from input variables.

        Input: backGroundFacies - A list of lists of background facies per overlay facies
               overlayFacies    - A list of overlay facies
               overlayTruncCenter - A list of a float number between 0 and 1 defining the center of the truncation interval.
        """
        nOverLayFacies = len(overlayFacies)
        self._nOverLayFacies =  nOverLayFacies

        if backGroundFaciesGroups!= None:
            # Number of overlay facies and number of groups of background facies must be equal
            assert len(backGroundFaciesGroups) == len(overlayFacies)

            # Number of background facies and overlay facies must match number of facies in zone
            assert self._nBackGroundFacies + self._nOverLayFacies == self._nFacies

        if self._nOverLayFacies == 0:
            return

        # Parameter for overlay facies truncation interval
        self._overLayTruncIntervalCenter = copy.copy(overlayTruncCenter)

        self._isBackGroundFacies = np.zeros((nOverLayFacies,self._nFacies), int)
        self._backGroundFaciesIndx = []
        for groupIndx in range(nOverLayFacies):
            bgFaciesGroup = backGroundFaciesGroups[groupIndx]
            bgFaciesIndxList = []
            self._backGroundFaciesIndx.append(bgFaciesIndxList)
            indx = -1
            for bgFaciesName in bgFaciesGroup:
                for i in range(self._nBackGroundFacies):
                    fN = self._faciesInTruncRule[i]
                    if fN == bgFaciesName:
                        indx = i
                        break
                if indx < 0:
                    raise ValueError(
                        'Error in {}'
                        'Error: Inconsistent facies names as input for background facies. Programming error'
                        ''.format(self._className)
                        )
                else:
                    bgFaciesIndxList.append(indx)
                    self._isBackGroundFacies[groupIndx,indx] = 1
            overlayFaciesName = overlayFacies[groupIndx]
#            print('Overlay facies name......: ' + overlayFaciesName)
            [nFacies, indx, fIndx, isNew] = self._addFaciesToTruncRule(overlayFaciesName)
            if isNew == 1:
                self._overlayFaciesIndx.append(indx)
                self._orderIndex.append(fIndx)
            else:
                raise ValueError(
                    'Error in {0}'
                    'Error: Specified overlay facies {1} is already used as background facies.'
                    ''.format(self._className,overlayFaciesName)
                    )

        assert self._nFacies == nFacies

    def getClassName(self):
        return copy.copy(self._className)

    def getFaciesOrderIndexList(self):
        return copy.copy(self._orderIndex)

    def getFaciesInTruncRule(self):
        return copy.copy(self._faciesInTruncRule)

    def getNGaussFieldsInModel(self):
        return self._nGaussFieldInModel

    def _getFaciesInTruncRuleIndex(self,fName):
        # Loop over all facies defined in the list faciesInTruncRule
        indx = -1
        for i in range(len(self._faciesInTruncRule)):
            fN = self._faciesInTruncRule[i]
            if fN == fName:
                indx = i
                break
        return indx

    def _getBackgroundFaciesInTruncRuleIndex(self,fName):
        # Loop over only the facies defined as background facies
        indx = -1
        for i in range(self._nBackGroundFacies):
            fN = self._faciesInTruncRule[i]
            if fN == fName:
                indx = i
                break
        return indx

    def _getFaciesInZoneIndex(self,fName):
        # Loop over all facies defined in the list faciesInZone
        indx = -1
        for i in range(self._nFacies):
            fN = self._faciesInZone[i]
            if fN == fName:
                indx = i
                break
        return indx

    def _setMinimumFaciesProb(self, faciesProb):
        sumProb = 0.0
        eps = self._eps * 0.1
        for i in range(len(faciesProb)):
            p = faciesProb[i]
            if p < eps:
                p = eps
                faciesProb[i] = p
            if p >= 1.0:
                p = 1.0 - eps
                faciesProb[i] = p
            sumProb += p
        return faciesProb

        for i in range(len(faciesProb)):
            p = faciesProb[i]
            faciesProb[i] = p / sumProb
        return

    def _modifyBackgroundFaciesArea(self, faciesProb):
        """
        Description: Calculate area in trunc map which has corrected for overlay facies. 
                     This function will also set a minimum probability for robustness of truncation algorithms.
        """
        area = copy.copy(faciesProb)
        sumProbBGFacies = []
        overLayProb = []
        for groupIndx in range(self._nOverLayFacies):
#            print('Overlay facies group: ' + str(groupIndx))
            sumProb = 0.0
            bgFaciesIndxList = self._backGroundFaciesIndx[groupIndx]
            for i in range(len(bgFaciesIndxList)):
                indx = bgFaciesIndxList[i]
                fIndx = self._orderIndex[indx]
                fProb = faciesProb[fIndx]
                if fProb < 0.0005:
                    fProb = 0.0005
                area[fIndx] = fProb
                sumProb += fProb
#            print('  sumProb background facies: ' + str(sumProb))
            sumProbBGFacies.append(sumProb)
            fIndx = self._orderIndex[self._overlayFaciesIndx[groupIndx]]
#            print('fIndx: ' + str(fIndx))
#            print('len(faciesProb): ')
#            print(repr(faciesProb))
#            print('orderindx: ')
#            print(repr(self._orderIndex))
            overLayProbability = faciesProb[fIndx]
            overLayProb.append(overLayProbability)
#            print('  overLayProb: ' + str(overLayProbability))

        # Renormalize again the probability since it might have changed slightly in previous step
        sumAll = 0.0
        for indx in range(len(self._orderIndex)):
            fIndx = self._orderIndex[indx]
            fProb = area[fIndx]
            sumAll += fProb
        for indx in range(len(self._orderIndex)):
            fIndx = self._orderIndex[indx]
            fProb = area[fIndx] / sumAll
            area[fIndx] = fProb

        lowAlpha = []
        highAlpha = []
#        deltaH = []
        for groupIndx in range(self._nOverLayFacies):
#            print('groupIndx: ' + str(groupIndx))
            bgFaciesIndxList = self._backGroundFaciesIndx[groupIndx]
            sumProb = sumProbBGFacies[groupIndx]
            sumTot = sumProb + overLayProb[groupIndx]
            dH = 1.0
            lAlpha = 0.0
            hAlpha = 0.0
            if sumTot > 0.0005:
                dH = sumProb / sumTot
#                print('Overlay facies group: ' + str(groupIndx) + ' deltaH: ' + str(dH))
                for i in range(len(bgFaciesIndxList)):
                    indx = bgFaciesIndxList[i]
                    fIndx = self._orderIndex[indx]
                    p = area[fIndx]
                    area[fIndx] = p / dH
#                    print('  faciesProb, area: ' + str(p) + ' ' + str(area[fIndx]))
#                print('overLayTruncIntervalCenter: ')
#                print(repr(self._overLayTruncIntervalCenter))
                lAlpha = self._overLayTruncIntervalCenter[groupIndx] - 0.5 * (1.0 - dH)
                hAlpha = self._overLayTruncIntervalCenter[groupIndx] + 0.5 * (1.0 - dH)
                if lAlpha < 0.0:
                    lAlpha = 0.0
                    hAlpha = 1.0 - dH
                if hAlpha > 1.0:
                    hAlpha = 1.0
                    lAlpha = dH
                lowAlpha.append(lAlpha)
                highAlpha.append(hAlpha)
        
        self._lowAlpha = lowAlpha
        self._highAlpha = highAlpha
        return area

    def _truncateOverlayFacies(self,indx,alphaCoord):
        """
        Description: Is used to truncate and find overlay facies. This function will be used
                     in truncation calculations in derived classes when overlay facies is defined.
        """
        
        # Loop over all groups 
        # The indx will be updated only if overlay facies should be used
        # The fIndx and faciesCode will be looked up and returned

        for groupIndx in range(self._nOverLayFacies):
            if self._isBackGroundFacies[groupIndx][indx] == 1:
                # This background facies can be overprinted by the overLay facies
                z = alphaCoord[groupIndx+2]
                if self._lowAlpha[groupIndx] < z <= self._highAlpha[groupIndx]:
                    # The alpha is within the specified truncation interval
                    # Set indx to overlay facies
                    indx = self._overlayFaciesIndx[groupIndx]
                    break

        fIndx = self._orderIndex[indx]
        faciesCode = self._faciesCode[fIndx]
        return [faciesCode, fIndx]

    def _XMLAddElement(self, parent):
        """
        Description: Write to xml tree the keywords related to overlay facies
        """
        if self._printInfo >= 3:
            print('Debug output: call XMLADDElement from Trunc2D_Base_xml')
        for groupIndx in range(self._nOverLayFacies):
            indx = self._overlayFaciesIndx[groupIndx]
            fName = self._faciesInTruncRule[indx]
            tag = 'OverLayFacies'
            attribute = {'name': fName}
            overLayElement = Element(tag, attribute)
            parent.append(overLayElement)
            tag = 'TruncIntervalCenter'
            ticElement = Element(tag)
            ticElement.text = ' ' + str(self._overLayTruncIntervalCenter[groupIndx]) + ' '
            overLayElement.append(ticElement)
            tag = 'Background'
            for i in range(len(self._backGroundFaciesIndx[groupIndx])):
                indx = self._backGroundFaciesIndx[groupIndx][i]
                fName = self._faciesInTruncRule[indx]
                bElement = Element(tag)
                bElement.text = ' ' + fName + ' '
                overLayElement.append(bElement)
