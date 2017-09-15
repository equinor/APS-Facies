#!/bin/env python
from xml.etree.ElementTree import Element

import copy
import numpy as np

"""
-----------------------------------------------------------------------
class Trunc2D_Cubic_Multi_Overlay
Description: A general truncation rule using rectangular polygons for the truncation map
             It is specified in a hierarchical way with 3 levels of subdivision of the truncation
             unit square into rectangles.
             In addition to the facies specified for the 2D truncation map, it is possible
             to specify additional facies using additional gaussian fields. These facies are specified
             to overprint or "overlay" the "background" facies which was specified for the 2D truncation map.
             Note that for each overprint facies a subset of the facies defined by the two first
             Gaussian fields must be defined. The algoritm also requires that there can be only one
             overprint facies that can "overprint" a background facies. So if e.g. 3 background facies
             are modelled like F1,F2,F3 and 2 overprint facies are specified like F4,F5, then the background facies
             must be divided into 2 groups like e.g. (F1,F3) and (F2) where one group is overprinted by F4 
             and the other by F5. It is not possible to the same background facies in two or more groups. 
             It is also possible to define different rectangular polygons from the truncation map
             to belong to the same facies in order to generate truncation rule with non-neigbour
             polygons in the truncation map.

 Public member functions:
 Constructor:    def __init__(self,trRuleXML=None, mainFaciesTable=None, faciesInZone=None,
                printInfo = 0,modelFileName=None)
  def initialize(self,mainFaciesTable,faciesInZone,truncStructureList,
                 backGroundFacies=None,overlayFacies=None,overlayTruncCenter=None,printInfo=0)


  --- Common get functions for all Truncation classes ---
  def getClassName(self)
  def getFaciesOrderIndexList(self)
  def getFaciesInTruncRule(self)
  def getNGaussFieldsInModel(self)
  --- Set functions ---


  --- Common functions for all Truncation classes ---
  def useConstTruncModelParam(self)
  def setTruncRule(self,faciesProb,cellIndx = 0)
  def defineFaciesByTruncRule(self,alphaCoord)
  def truncMapPolygons(self)
  def faciesIndxPerPolygon(self)
  def XMLAddElement(self,parent)

 Private member functions:
   def __interpretXMLTree(trRuleXML,mainFaciesTable,faciesInZone,printInfo,modelFileName)
   def __checkFaciesForZone(self)
   def __addFaciesToTruncRule(self,fName)
   def __modifyBackgroundFaciesArea(self,faciesProb)
   def __calcProbForEachNode(self,faciesProb)
   def __calcThresholdValues(self)
   def __calcFaciesLevel1V(self,nodeListL1,alphaCoord)
   def __calcFaciesLevel1H(self,nodeListL1,alphaCoord)
   def __calcFaciesLevel2H(self,nodeListL2,alphaCoord)
   def __calcFaciesLevel2V(self,nodeListL2,alphaCoord)
   def __calcFaciesLevel3H(self,nodeListL3,alphaCoord)
   def __calcFaciesLevel3V(self,nodeListL3,alphaCoord)
   def __calcPolyLevel(self,direction,nodeList,polyLevelAbove,levelNumber)
   def __writeDataForTruncRule(self)
   def __getPolygonAndFaciesList(self)
   def __setMinimumFaciesProb(self,faciesProb)
   def __setTruncStructure(self,truncStructureList)
   def __defineBackgroundFaciesAndOverLayFacies(self,backGroundFacies,overlayFacies)

-------------------------------------------------------------
"""


class Trunc2D_Cubic_Multi_Overlay:
    """
    Description: This class implements adaptive plurigaussian field truncation
                 using two simulated gaussian fields (with trend).

    """

    def __setEmpty(self):
        # Tolerance used for probabilities
        self.__eps = 0.0001

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
        self.__printInfo = 0
        self.__className = 'Trunc2D_Cubic_Multi_Overlay'

        # Variables containing truncations for the 2D truncation map
        self.__setTruncRuleIsCalled = False
        self.__nGaussFieldInModel = 2
        self.__truncStructure = []
        self.__useLevel2 = 0
        self.__useLevel3 = 0
        self.__backGroundFaciesIndx = []
        self.__isBackGroundFacies = None
        self.__overlayFaciesIndx = []
        self.__nOverLayFacies = 0
        self.__lowAlpha = []
        self.__highAlpha = []
        # self.__deltaH = 0
        self.__overLayTruncIntervalCenter = []
        # nodeData is either of the form  ['N',direction,nodeList,prob,polygon,xmin,xmax,ymin.ymax]  or
        # of the form ['F',indx,     probFrac,prob,polygon,xmin,xmax,ymin,ymax]
        self.__node_index = {
            'type': 0,
            'direction': 1,
            'list of nodes': 2,
            'probability': 3,
            'polygon': 4,
            'index': 1,
            'probability fraction': 2,
            'x min': 5,
            'x max': 6,
            'y min': 7,
            'y max': 8
        }

        self.__nPoly = 0
        self.__polygons = []
        self.__fIndxPerPolygon = []

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
        print('Number of Gauss fields in model: ' + str(self.__nGaussFieldInModel))
        print('Truncation structure:')
        for i in range(len(self.__truncStructure)):
            item = self.__truncStructure[i]
            print(repr(item))
        print('Use level 2: ' + str(self.__useLevel2))
        print('Use level 3: ' + str(self.__useLevel3))
        print('Background facies index for each overlay facies:')
        for i in range(len(self.__backGroundFaciesIndx)):
            list = self.__backGroundFaciesIndx[i]
            print('Group number: ' + str(i))
            print(repr(list))
        print('Is the facies a background facies: ')
        print(repr(self.__backGroundFaciesIndx))
        print('Number of overlay facies: ' + str(self.__nOverLayFacies))
        print('Overlay facies index:')
        print(repr(self.__overlayFaciesIndx))
        print('Low Alpha: ')
        print(repr(self.__lowAlpha))
        print('High Alpha: ')
        print(repr(self.__highAlpha))
        print('Overlay parameter for truncation interval center: ')
        print(repr(self.__overLayTruncIntervalCenter))
        print('Internal indices in data structure (node_index):')
        print(self.__node_index)
        print('Number of polygons: ' + str(self.__nPoly))
        for i in range(len(self.__polygons)):
            poly = self.__polygons[i]
            print('Polygon number: ' + str(i))
            for j in range(len(poly)):
                print(repr(poly[j]))
        print('Facies index for polygons:')
        print(repr(self.__fIndxPerPolygon))

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
        # Initialize data structure
        self.__setEmpty()

        if trRuleXML is not None:
            if printInfo >= 3:
                print('Debug info: Read data from model file for: ' + self.__className)
            self.__nGaussFieldInModel = nGaussFieldInModel
            self.__interpretXMLTree(trRuleXML, mainFaciesTable, faciesInZone, printInfo, modelFileName)
        else:
            if printInfo >= 3:
                print('Debug info: Create empty object for: ' + self.__className)
        #  End of __init__

    def __interpretXMLTree(self, trRuleXML, mainFaciesTable, faciesInZone, printInfo, modelFileName):
        # Initialize object from xml tree object trRuleXML
        self.__printInfo = printInfo
        # Reference to main facies table which is global for the whole model
        if mainFaciesTable is not None:
            self.__mainFaciesTable = mainFaciesTable
            self.__nFaciesMain = self.__mainFaciesTable.getNFacies()
        else:
            raise ValueError(
                'Error in {}\n'
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
                'Error in ' + self.__className + '\n'
                'Error: Inconsistency'
            )

        # Facies code for facies in zone
        for fName in self.__faciesInZone:
            fCode = self.__mainFaciesTable.getFaciesCodeForFaciesName(fName)
            self.__faciesCode.append(fCode)

        # Get info from the XML model file tree for this truncation rule
        TYPE = self.__node_index['type']
        # DIR = self.__node_index['direction']
        NLIST = self.__node_index['list of nodes']
        # PROB = self.__node_index['probability']
        # POLY = self.__node_index['polygon']
        INDX = self.__node_index['index']
        PFRAC = self.__node_index['probability fraction']

        truncStructure = []
        nFacies = 0
        nPoly = 0
        kw1 = 'L1'
        L1Obj = trRuleXML.find(kw1)
        if L1Obj is None:
            raise ValueError(
                'Error when reading model file: {}\n'
                'Error: Read truncation rule: {}\n'
                'Error: Missing keyword {} under keyword  TruncationRule\n'
                ''.format(modelFileName, self.__className, kw1)
            )

        text = L1Obj.get('direction')
        directionL1 = text.strip()
        if directionL1 != 'H' and directionL1 != 'V':
            raise ValueError(
                'Error when reading model file: {}\n'
                'Error: Read truncation rule: {}\n'
                'Error: Specified attribute "direction" must be H or V.'
                ''.format(modelFileName, self.__className)
            )

        nodeList = []
        poly = []
        # nodeData = ['N',direction,nodeList,prob,polygon,xmin,xmax,ymin.ymax]
        truncStructure = ['N', directionL1, nodeList, 0.0, poly, 0.0, 1.0, 0.0, 1.0]

        # Loop over all child elements directly under L1 level
        nodeListLevel1 = []
        truncStructure[NLIST] = nodeListLevel1
        kw2 = 'ProbFrac'
        kw3 = 'L2'
        kw4 = 'L3'
        for childL1 in L1Obj:
            # print('Child L1 tag and attribute: ')
            # print(childL1.tag,childL1.attrib)
            if childL1.tag == kw2:
                text = childL1.get('name')
                fName = text.strip()
                text = childL1.text
                probFrac = float(text.strip())
                if fName not in self.__faciesInZone:
                    raise ValueError(
                        'Error when reading model file: {0}\n'
                        'Error: Read truncation rule: {1}\n'
                        'Error: Specified facies name in truncation rule: {2} is not defined for this zone.'
                        ''.format(modelFileName, self.__className, fName)
                    )
                if probFrac < 0.0 or probFrac > 1.0:
                    raise ValueError(
                        'Error when reading model file: {}\n'
                        'Error: Read truncation rule: {}\n'
                        'Error: Specified probability fraction in truncation rule is outside [0,1].'
                        ''.format(modelFileName, self.__className)
                    )

                [nFacies, indx, fIndx, isNew] = self.__addFaciesToTruncRule(fName)
                nPoly += 1

                poly = []
                # nodeData = ['F',indx,probFrac,prob,polygon,xmin,xmax,ymin,ymax]
                nodeData = ['F', indx, probFrac, 0.0, poly, 0.0, 0.0, 0.0, 0.0]
                nodeListLevel1.append(nodeData)
                if isNew == 1:
                    self.__orderIndex.append(fIndx)
            elif childL1.tag == kw3:
                if directionL1 == 'H':
                    directionL2 = 'V'
                else:
                    directionL2 = 'H'
                self.__useLevel2 = 1

                nodeListLevel2 = []
                poly = []
                # nodeData = ['N',direction,nodeList,prob,polygon,xmin,xmax,ymin,ymax]
                nodeData = ['N', directionL2, nodeListLevel2, 0.0, poly, 0.0, 0.0, 0.0, 0.0]
                nodeListLevel1.append(nodeData)

                # Loop over all child elements directly under L2 level
                for childL2 in childL1:
                    # print('Child L2 tag and attribute: ')
                    # print(childL2.tag,childL2.attrib)
                    if childL2.tag == kw2:
                        text = childL2.get('name')
                        fName = text.strip()
                        text = childL2.text
                        probFrac = float(text.strip())
                        if fName not in self.__faciesInZone:
                            raise ValueError(
                                'Error when reading model file: ' + modelFileName + '\n'
                                'Error: Read truncation rule: ' + self.__className + '\n'
                                'Error: Specified facies name in truncation rule: ' + fName
                                + ' is not defined for this zone.'
                            )
                        elif probFrac < 0.0 or probFrac > 1.0:
                            raise ValueError(
                                'Error when reading model file: ' + modelFileName + '\n'
                                'Error: Read truncation rule: ' + self.__className + '\n'
                                'Error: Specified probability fraction in truncation rule is outside [0,1]'
                            )

                        [nFacies, indx, fIndx, isNew] = self.__addFaciesToTruncRule(fName)
                        nPoly += 1

                        poly = []
                        # nodeData = ['F',indx,probFrac,prob,polygon,xmin,xmax,ymin,ymax]
                        nodeData = ['F', indx, probFrac, 0.0, poly, 0.0, 0.0, 0.0, 0.0]
                        nodeListLevel2.append(nodeData)
                        if isNew == 1:
                            self.__orderIndex.append(fIndx)
                    elif childL2.tag == kw4:
                        directionL3 = directionL1
                        self.__useLevel3 = 1
                        nodeListLevel3 = []
                        poly = []
                        # nodeData = ['N',direction,nodeList,prob,polygon,xmin,xmax,ymin,ymax]
                        nodeData = ['N', directionL3, nodeListLevel3, 0.0, poly, 0.0, 0.0, 0.0, 0.0]
                        nodeListLevel2.append(nodeData)

                        # Loop over all child elements directly under L3 level
                        for childL3 in childL2:
                            # print('Child L3 tag and attribute: ')
                            # print(childL3.tag,childL3.attrib)
                            if childL3.tag == kw2:
                                text = childL3.get('name')
                                fName = text.strip()
                                text = childL3.text
                                probFrac = float(text.strip())
                                if not (fName in self.__faciesInZone):
                                    raise ValueError(
                                        'Error when reading model file: ' + modelFileName + '\n'
                                        'Error: Read truncation rule: ' + self.__className + '\n'
                                        'Error: Specified facies name in truncation rule: ' + fName
                                        + ' is not defined for this zone.'
                                    )
                                if probFrac < 0.0 or probFrac > 1.0:
                                    raise ValueError(
                                        'Error when reading model file: ' + modelFileName + '\n'
                                        'Error: Read truncation rule: ' + self.__className + '\n'
                                        'Error: Specified probability fraction in truncation rule is outside [0,1]'
                                    )

                                [nFacies, indx, fIndx, isNew] = self.__addFaciesToTruncRule(fName)
                                nPoly += 1

                                poly = []
                                # nodeData = ['F',indx,probFrac,prob,polygon,xmin,xmax,ymin,ymax]
                                nodeData = ['F', indx, probFrac, 0.0, poly, 0.0, 0.0, 0.0, 0.0]
                                nodeListLevel3.append(nodeData)
                                if isNew == 1:
                                    self.__orderIndex.append(fIndx)

        # End loop over L1 children

        # Read specification of one or more overlay facies and which region (set of background facies)
        # the overlay facies is defined to be located.
        # A requirement is that the background facies for each overlay facies is not overlapping.
        # It is not allowed to specify the same facies as background facies for two different overlya facies.
        kw = 'OverLayFacies'
        nBackGroundFacies = nFacies
        nOverLayFacies = 0
        self.__backGroundFaciesIndx = []
        for overLayObj in trRuleXML.findall(kw):
            if overLayObj is not None:
                nOverLayFacies += 1
                bgFaciesIndxList = []
                self.__backGroundFaciesIndx.append(bgFaciesIndxList)
        if self.__printInfo >= 3:
            print('Debug info: Number of overlay facies is : ' + str(nOverLayFacies))

        # Check that number of gauss fields in model match the required number in this model
        if self.__nGaussFieldInModel != (nOverLayFacies + 2):
            raise ValueError(
                'Mismatch in specification of model file regarding number of gaussian fields and truncation rule'
            )

        self.__isBackGroundFacies = np.zeros((nOverLayFacies, len(self.__faciesInZone)), dtype=int)
        groupIndx = 0
        for overLayObj in trRuleXML.findall(kw):
            if overLayObj is not None:
                text = overLayObj.get('name')
                fNameOverLayFacies = text.strip()
                if fNameOverLayFacies not in self.__faciesInZone:
                    raise ValueError(
                        'Error when reading model file: ' + modelFileName + '\n'
                        'Error: Read truncation rule: ' + self.__className + '\n'
                        'Error: Specified facies name in truncation rule: ' + fNameOverLayFacies
                        + ' is not defined for this zone.'
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
                    self.__overLayTruncIntervalCenter.append(center)

                kw2 = 'Background'
                bgFaciesIndxList = self.__backGroundFaciesIndx[groupIndx]
                for bgObj in overLayObj.findall(kw2):
                    text = bgObj.text
                    bgFaciesName = text.strip()
                    # Check that background facies is defined and if defined, add to list
                    indx = -999
                    for i in range(nBackGroundFacies):
                        fN = self.__faciesInTruncRule[i]
                        if fN == bgFaciesName:
                            indx = i
                            break
                    if indx < 0:
                        raise ValueError(
                            'Error when reading model file: {}\n'
                            'Error: Read truncation rule: {}\n'
                            'Error: Specified facies name as background facies in truncation rule: {} is not defined\n'
                            '       or is defined as overlay facies.'
                            ''.format(modelFileName, self.__className, bgFaciesName)
                        )
                    bgFaciesIndxList.append(indx)
                    self.__isBackGroundFacies[groupIndx, indx] = 1
                groupIndx += 1

                [nFacies, indx, fIndx, isNew] = self.__addFaciesToTruncRule(fNameOverLayFacies)
                if isNew == 1:
                    self.__overlayFaciesIndx.append(indx)
                    self.__orderIndex.append(fIndx)
                else:
                    raise ValueError(
                        'Error in {}\n'
                        'Error: Specified overlay facies ' + fNameOverLayFacies +
                        ' is already used as background facies or overlay facies.'
                        ''.format(self.__className)
                    )

            else:
                raise ValueError(
                    'Error in {}\n'
                    'Error: Missing keyword {} in truncation rule.'
                    ''.format(self.__className, kw)
                )
        # Check that background facies regions for different overlay facies does not have
        # common facies.
        for groupIndx1 in range(len(self.__overlayFaciesIndx)):
            bgFaciesIndxList1 = self.__backGroundFaciesIndx[groupIndx1]
            for groupIndx2 in range(groupIndx1 + 1, len(self.__overlayFaciesIndx)):
                bgFaciesIndxList2 = self.__backGroundFaciesIndx[groupIndx2]
                for indx1 in bgFaciesIndxList1:
                    if indx1 in bgFaciesIndxList2:
                        raise ValueError(
                            'Error in ' + self.__className +'\n'
                            'Facies name ' + self.__faciesInTruncRule[indx1] +
                            ' is specified as background facies for more than one overlay facies'
                        )
        self.__nOverLayFacies = len(self.__overlayFaciesIndx)
        # End read overlay facies

        # print('nFacies,self__nFacies: ' + str(nFacies) + ' ' + str(self.__nFacies))
        if nFacies != self.__nFacies:
            raise ValueError(
                'Error when reading model file: {0}\n'
                'Error: Read truncation rule: {1}\n'
                'Error: Mismatch in number of facies specified in truncation rule: {2}\n'
                '       and number of facies to be modelled for the zone: {3}.'
                ''.format(modelFileName, self.__className, str(nFacies), str(self.__nFacies))
            )

        # Check that specified probability fractions for each facies when summing over all polygons
        # for a facies is 1.0
        # This sum should not include overlay facies which is the last facies in the faciesInTruncRule list
        sumProbFrac = np.zeros(nFacies - self.__nOverLayFacies, np.float32)
        nodeListL1 = truncStructure[NLIST]
        for i in range(len(nodeListL1)):
            item = nodeListL1[i]
            if item[TYPE] == 'F':
                indx = item[INDX]
                probFrac = item[PFRAC]
                sumProbFrac[indx] += probFrac
            else:
                nodeListL2 = item[NLIST]
                for j in range(len(nodeListL2)):
                    item = nodeListL2[j]
                    if item[TYPE] == 'F':
                        indx = item[INDX]
                        probFrac = item[PFRAC]
                        sumProbFrac[indx] += probFrac
                    else:
                        nodeListL3 = item[NLIST]
                        for k in range(len(nodeListL3)):
                            item = nodeListL3[k]
                            indx = item[INDX]
                            probFrac = item[PFRAC]
                            sumProbFrac[indx] += probFrac
        # Number of background facies (not overLay facies)
        nBackGroundFacies = nFacies - nOverLayFacies
        for i in range(nBackGroundFacies):
            if self.__printInfo >= 3:
                fName = self.__faciesInTruncRule[i]
                print('Debug output: Sum prob frac for facies {0} is: {1}'.format(
                    fName, str(sumProbFrac[i])))

            if abs(sumProbFrac[i] - 1.0) > 0.001:
                fName = self.__faciesInTruncRule[i]
                raise ValueError(
                    'Error in {0}\n'
                    'Error: Sum of probability fractions over all polygons for facies {1} is not 1.0\n'
                    'Error: The sum is: {2}'.format(
                        self.__className, fName, str(sumProbFrac[i]))
                )

        self.__truncStructure = truncStructure

        self.__checkFaciesForZone()

        if self.__printInfo >= 3:
            print('Debug output: Facies names in truncation rule:')
            print(repr(self.__faciesInTruncRule))
            print('Debug output: Facies ordering (relative to facies in zone):')
            print(repr(self.__orderIndex))
            print('Debug output: Facies code for facies in zone')
            print(repr(self.__faciesCode))
            for i in range(len(self.__overlayFaciesIndx)):
                print('Debug output: Overlay facies for group ' + str(i + 1) + ': '
                      + self.__faciesInTruncRule[self.__overlayFaciesIndx[i]])
                print('Debug output: Background facies index in trunc rule for this group: ')
                print(repr(self.__backGroundFaciesIndx[i]))

    def __checkFaciesForZone(self):
        # Check that the facies for the truncation rule is the same
        # as defined for the zone with specified probabilities.
        for fName in self.__faciesInTruncRule:
            # print('fName in checkFaciesForZone: ')
            # print(fName)
            if fName not in self.__faciesInZone:
                raise ValueError(
                    'Error: In truncation rule: {}\n'
                    'Error: Facies name {} is not defined for the current zone.\n'
                    'Error: No probability is defined for this facies for the current zone.'
                    ''.format(self.__className, fName)
                )
        for fName in self.__faciesInZone:
            if fName not in self.__faciesInTruncRule:
                raise ValueError(
                    'Error: In truncation rule: {}\n'
                    'Error: Facies name {} which is defined for the current zone is not defined in the truncation rule.\n'
                    'Error: Cannot have facies with specified probability that is not used in the truncation rule.'
                    ''.format(self.__className, fName)
                )
        return True

    def __addFaciesToTruncRule(self, fName):
        found = 0
        isNew = 0
        indx = -1
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
        if indx < 0:
            raise ValueError("An error occured. Programming error.")
        if fIndx < 0:
            assert self.__nFacies == len(self.__faciesInZone)
            raise ValueError(
                'Error in {}. Specified facies name {} is not defined for this zone.'.format(self.__className, fName)
            )
        return [nFaciesInTruncRule, indx, fIndx, isNew]

    def getClassName(self):
        return copy.copy(self.__className)

    def getFaciesOrderIndexList(self):
        return copy.copy(self.__orderIndex)

    def getFaciesInTruncRule(self):
        return copy.copy(self.__faciesInTruncRule)

    def getNGaussFieldsInModel(self):
        return self.__nGaussFieldInModel

    def useConstTruncModelParam(self):
        # This is a function returning True if there are no truncation model
        # parameter that is spatially dependent. In the truncation rule here
        # there are no model parameters for the truncation model (except facies probability)
        return True

    def setTruncRule(self, faciesProb, cellIndx=0):
        """
           Description: Calculate threshold values from probabilities per layer or column in truncation map.
           Input:
               faciesProb - Probability for each facies.
               cellIndx   - Is not used here , but may be used in case there are 3D parameters for
                            truncation rule model parameters that are not facies probabilities.
        """
        self.__setTruncRuleIsCalled = True
        self.__setMinimumFaciesProb(faciesProb)
        isDetermined = 0
        for fIndx in range(len(faciesProb)):
            self.__faciesIsDetermined[fIndx] = 0
            if faciesProb[fIndx] > (1.0 - self.__eps):
                self.__faciesIsDetermined[fIndx] = 1
                isDetermined = 1

        if isDetermined == 1:
            return

        [area, lowAlpha, highAlpha] = self.__modifyBackgroundFaciesArea(faciesProb)
        self.__calcProbForEachNode(area)
        # self.__deltaH = deltaH
        self.__lowAlpha = lowAlpha
        self.__highAlpha = highAlpha

        self.__calcThresholdValues()

        self.__writeDataForTruncRule()
        return

    def __setMinimumFaciesProb(self, faciesProb):
        sumProb = 0.0
        eps = self.__eps * 0.5
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

    def __modifyBackgroundFaciesArea(self, faciesProb):

        area = copy.copy(faciesProb)
        sumProbBGFacies = []
        overLayProb = []
        for groupIndx in range(self.__nOverLayFacies):
            # print('Overlay facies group: ' + str(groupIndx))
            sumProb = 0.0
            bgFaciesIndxList = self.__backGroundFaciesIndx[groupIndx]
            for i in range(len(bgFaciesIndxList)):
                indx = bgFaciesIndxList[i]
                fIndx = self.__orderIndex[indx]
                fProb = faciesProb[fIndx]
                if fProb < 0.0005:
                    fProb = 0.0005
                area[fIndx] = fProb
                sumProb += fProb
            # print('  sumProb background facies: ' + str(sumProb))
            sumProbBGFacies.append(sumProb)
            fIndx = self.__orderIndex[self.__overlayFaciesIndx[groupIndx]]
            overLayProbability = faciesProb[fIndx]
            overLayProb.append(overLayProbability)
            # print('  overLayProb: ' + str(overLayProbability))

        # Renormalize again the probability since it might have changed slightly in previous step
        sumAll = 0.0
        for indx in range(len(self.__orderIndex)):
            fIndx = self.__orderIndex[indx]
            fProb = area[fIndx]
            sumAll += fProb
        for indx in range(len(self.__orderIndex)):
            fIndx = self.__orderIndex[indx]
            fProb = area[fIndx] / sumAll
            area[fIndx] = fProb

        lowAlpha = []
        highAlpha = []
        # deltaH = []
        for groupIndx in range(self.__nOverLayFacies):
            # print('groupIndx: ' + str(groupIndx))
            bgFaciesIndxList = self.__backGroundFaciesIndx[groupIndx]
            sumProb = sumProbBGFacies[groupIndx]
            sumTot = sumProb + overLayProb[groupIndx]
            dH = 1.0
            lAlpha = 0.0
            hAlpha = 0.0
            if sumTot > 0.0005:
                dH = sumProb / sumTot
                # print('Overlay facies group: ' + str(groupIndx) + ' deltaH: ' + str(dH))
                for i in range(len(bgFaciesIndxList)):
                    indx = bgFaciesIndxList[i]
                    fIndx = self.__orderIndex[indx]
                    p = area[fIndx]
                    area[fIndx] = p / dH
                    # print('  faciesProb, area: ' + str(p) + ' ' + str(area[fIndx]))
                # print('overLayTruncIntervalCenter: ')
                # print(repr(self.__overLayTruncIntervalCenter))
                lAlpha = self.__overLayTruncIntervalCenter[groupIndx] - 0.5 * (1.0 - dH)
                hAlpha = self.__overLayTruncIntervalCenter[groupIndx] + 0.5 * (1.0 - dH)
                if lAlpha < 0.0:
                    lAlpha = 0.0
                    hAlpha = 1.0 - dH
                if hAlpha > 1.0:
                    hAlpha = 1.0
                    lAlpha = dH
                lowAlpha.append(lAlpha)
                highAlpha.append(hAlpha)
        return [area, lowAlpha, highAlpha]

    def __calcProbForEachNode(self, faciesProb):
        TYPE = self.__node_index['type']
        NLIST = self.__node_index['list of nodes']
        PROB = self.__node_index['probability']
        INDX = self.__node_index['index']
        PFRAC = self.__node_index['probability fraction']
        # eps = self.__eps
        nodeListL1 = self.__truncStructure[NLIST]
        cumProbL1 = 0.0
        for i in range(len(nodeListL1)):
            itemL1 = nodeListL1[i]
            if itemL1[TYPE] == 'F':
                indx = itemL1[INDX]
                fIndx = self.__orderIndex[indx]
                probFrac = itemL1[PFRAC]
                p = faciesProb[fIndx] * probFrac
                itemL1[PROB] = p
                cumProbL1 += p
            else:
                nodeListL2 = itemL1[NLIST]
                cumProbL2 = 0
                for j in range(len(nodeListL2)):
                    itemL2 = nodeListL2[j]
                    if itemL2[TYPE] == 'F':
                        indx = itemL2[INDX]
                        fIndx = self.__orderIndex[indx]
                        probFrac = itemL2[PFRAC]
                        p = faciesProb[fIndx] * probFrac
                        itemL2[PROB] = p  # prob
                        cumProbL2 += p
                    else:
                        nodeListL3 = itemL2[NLIST]
                        cumProbL3 = 0

                        for k in range(len(nodeListL3)):
                            itemL3 = nodeListL3[k]
                            indx = itemL3[INDX]
                            fIndx = self.__orderIndex[indx]
                            probFrac = itemL3[PFRAC]
                            p = faciesProb[fIndx] * probFrac
                            itemL3[PROB] = p  # prob
                            cumProbL3 += p

                        itemL2[PROB] = cumProbL3  # prob
                        cumProbL2 += cumProbL3

                itemL1[PROB] = cumProbL2  # prob
                cumProbL1 += cumProbL2

                # Check that total sum of probabilities is =  1.0
        if abs(cumProbL1 - 1.0) > 0.001:
            raise ValueError(
                'Error in {0}\n'
                'Error: Internal program error. Sum of probabilities is not 1.0\n'
                'Error: cumProbL1 = {1}'.format(self.__className, str(cumProbL1))
            )

    def __calcThresholdValues(self):
        TYPE = self.__node_index['type']
        NLIST = self.__node_index['list of nodes']
        DIR = self.__node_index['direction']
        PROB = self.__node_index['probability']
        XMIN = self.__node_index['x min']
        XMAX = self.__node_index['x max']
        YMIN = self.__node_index['y min']
        YMAX = self.__node_index['y max']
        eps = self.__eps
        nodeListL1 = self.__truncStructure[NLIST]
        directionL1 = self.__truncStructure[DIR]

        # Level L1 threshold values
        if directionL1 == 'H':
            # directionL1 = 'H'
            yminL1 = 0.0
            ymaxL1 = 0.0
            for i in range(len(nodeListL1)):
                itemL1 = nodeListL1[i]
                p = itemL1[PROB]
                yminL1 = ymaxL1
                ymaxL1 = yminL1 + p
                itemL1[XMIN] = 0.0
                itemL1[XMAX] = 1.0
                itemL1[YMIN] = yminL1
                itemL1[YMAX] = ymaxL1
        else:
            # directionL1 = 'V'
            xminL1 = 0.0
            xmaxL1 = 0.0
            for i in range(len(nodeListL1)):
                itemL1 = nodeListL1[i]
                p = itemL1[PROB]
                xminL1 = xmaxL1
                xmaxL1 = xminL1 + p
                itemL1[XMIN] = xminL1
                itemL1[XMAX] = xmaxL1
                itemL1[YMIN] = 0.0
                itemL1[YMAX] = 1.0

        # Level L2 threshold values
        if self.__useLevel2 == 1:
            if directionL1 == 'H':
                # directionL2 = 'V'
                for i in range(len(nodeListL1)):
                    itemL1 = nodeListL1[i]
                    if itemL1[TYPE] == 'N':
                        probL1 = itemL1[PROB]
                        if probL1 > eps:
                            nodeListL2 = itemL1[NLIST]
                            xminL2 = 0.0
                            xmaxL2 = 0.0
                            for j in range(len(nodeListL2)):
                                itemL2 = nodeListL2[j]
                                p = itemL2[PROB] / probL1
                                xminL2 = xmaxL2
                                xmaxL2 = xminL2 + p
                                itemL2[XMIN] = xminL2
                                itemL2[XMAX] = xmaxL2
                                itemL2[YMIN] = itemL1[YMIN]
                                itemL2[YMAX] = itemL1[YMAX]

            else:
                # directionL2 = 'H'
                for i in range(len(nodeListL1)):
                    itemL1 = nodeListL1[i]
                    if itemL1[TYPE] == 'N':
                        probL1 = itemL1[PROB]
                        if probL1 > eps:
                            nodeListL2 = itemL1[NLIST]
                            yminL2 = 0.0
                            ymaxL2 = 0.0
                            for j in range(len(nodeListL2)):
                                itemL2 = nodeListL2[j]
                                p = itemL2[PROB] / probL1
                                yminL2 = ymaxL2
                                ymaxL2 = yminL2 + p
                                itemL2[YMIN] = yminL2
                                itemL2[YMAX] = ymaxL2
                                itemL2[XMIN] = itemL1[XMIN]
                                itemL2[XMAX] = itemL1[XMAX]
        # end if use level 2

        # Level L3 threshold values
        if self.__useLevel3 == 1:
            if directionL1 == 'V':
                # directionL3 = 'V'
                for i in range(len(nodeListL1)):
                    itemL1 = nodeListL1[i]
                    if itemL1[TYPE] == 'N':
                        probL1 = itemL1[PROB]
                        if probL1 > eps:
                            nodeListL2 = itemL1[NLIST]
                            for j in range(len(nodeListL2)):
                                itemL2 = nodeListL2[j]
                                if itemL2[TYPE] == 'N':
                                    probL2 = itemL2[PROB]
                                    if probL2 > eps:
                                        nodeListL3 = itemL2[NLIST]
                                        xminL2 = itemL2[XMIN]
                                        xmaxL2 = itemL2[XMAX]
                                        xLength = xmaxL2 - xminL2
                                        xmaxL3 = xminL2
                                        yminL2 = itemL2[YMIN]
                                        ymaxL2 = itemL2[YMAX]
                                        for k in range(len(nodeListL3)):
                                            itemL3 = nodeListL3[k]
                                            p = itemL3[PROB] / probL2
                                            xminL3 = xmaxL3
                                            xmaxL3 = xminL3 + p * xLength
                                            itemL3[XMIN] = xminL3
                                            itemL3[XMAX] = xmaxL3
                                            itemL3[YMIN] = yminL2
                                            itemL3[YMAX] = ymaxL2
            else:
                # directionL3 = 'H'
                for i in range(len(nodeListL1)):
                    itemL1 = nodeListL1[i]
                    if itemL1[TYPE] == 'N':
                        probL1 = itemL1[PROB]
                        if probL1 > eps:
                            nodeListL2 = itemL1[NLIST]
                            for j in range(len(nodeListL2)):
                                itemL2 = nodeListL2[j]
                                if itemL2[TYPE] == 'N':
                                    probL2 = itemL2[PROB]
                                    if probL2 > eps:
                                        nodeListL3 = itemL2[NLIST]
                                        yminL2 = itemL2[YMIN]
                                        ymaxL2 = itemL2[YMAX]
                                        yLength = ymaxL2 - yminL2
                                        ymaxL3 = yminL2
                                        xminL2 = itemL2[XMIN]
                                        xmaxL2 = itemL2[XMAX]
                                        for k in range(len(nodeListL3)):
                                            itemL3 = nodeListL3[k]
                                            p = itemL3[PROB] / probL2
                                            yminL3 = ymaxL3
                                            ymaxL3 = yminL3 + p * yLength
                                            itemL3[XMIN] = xminL2
                                            itemL3[XMAX] = xmaxL2
                                            itemL3[YMIN] = yminL3
                                            itemL3[YMAX] = ymaxL3
        # end if use level 3

    def defineFaciesByTruncRule(self, alphaCoord):
        for fIndx in range(len(self.__faciesInZone)):
            if self.__faciesIsDetermined[fIndx] == 1:
                faciesCode = self.__faciesCode[fIndx]
                return [faciesCode, fIndx]

        directionL1 = self.__truncStructure[self.__node_index['direction']]
        nodeListL1 = self.__truncStructure[self.__node_index['list of nodes']]
        if directionL1 == 'H':
            [faciesCode, fIndx] = self.__calcFaciesLevel1H(nodeListL1, alphaCoord)
        else:
            [faciesCode, fIndx] = self.__calcFaciesLevel1V(nodeListL1, alphaCoord)
        return [faciesCode, fIndx]

    def __calcFaciesLevel1V(self, nodeListL1, alphaCoord):
        faciesCode = -1
        fIndx = -1
        x = alphaCoord[0]
        y = alphaCoord[1]
        for i in range(len(nodeListL1)):
            itemL1 = nodeListL1[i]
            typeNode = itemL1[self.__node_index['type']]
            if typeNode == 'F':
                if x <= itemL1[self.__node_index['x max']]:
                    indx = itemL1[self.__node_index['index']]
                    found = 0
                    for groupIndx in range(self.__nOverLayFacies):
                        if self.__isBackGroundFacies[groupIndx][indx] == 1:
                            z = alphaCoord[groupIndx + 2]
                            if self.__lowAlpha[groupIndx] < z <= self.__highAlpha[groupIndx]:
                                fIndx = self.__orderIndex[self.__overlayFaciesIndx[groupIndx]]
                                faciesCode = self.__faciesCode[fIndx]
                                found = 1
                                break
                    if found:
                        break
                    fIndx = self.__orderIndex[indx]
                    faciesCode = self.__faciesCode[fIndx]
                    break
            else:
                if x <= itemL1[self.__node_index['x max']]:
                    directionL2 = itemL1[self.__node_index['direction']]
                    nodeListL2 = itemL1[self.__node_index['list of nodes']]
                    if directionL2 == 'H':
                        [faciesCode, fIndx] = self.__calcFaciesLevel2H(nodeListL2, alphaCoord)
                    else:
                        [faciesCode, fIndx] = self.__calcFaciesLevel2V(nodeListL2, alphaCoord)
                    break
        if faciesCode < 0 or fIndx < 0:
            # TODO: Proper error message
            raise ValueError("Something happened")
        return [faciesCode, fIndx]

    def __calcFaciesLevel1H(self, nodeListL1, alphaCoord):
        faciesCode = -1
        fIndx = -1
        x = alphaCoord[0]
        y = alphaCoord[1]
        for i in range(len(nodeListL1)):
            itemL1 = nodeListL1[i]
            typeNode = itemL1[self.__node_index['type']]
            if typeNode == 'F':
                if y <= itemL1[self.__node_index['y max']]:
                    indx = itemL1[self.__node_index['index']]
                    found = 0
                    for groupIndx in range(self.__nOverLayFacies):
                        if self.__isBackGroundFacies[groupIndx][indx] == 1:
                            z = alphaCoord[groupIndx + 2]
                            if self.__lowAlpha[groupIndx] < z <= self.__highAlpha[groupIndx]:
                                fIndx = self.__orderIndex[self.__overlayFaciesIndx[groupIndx]]
                                faciesCode = self.__faciesCode[fIndx]
                                found = 1
                                break

                    if found:
                        break
                    fIndx = self.__orderIndex[indx]
                    faciesCode = self.__faciesCode[fIndx]
                    break

            else:
                if y <= itemL1[self.__node_index['y max']]:
                    directionL2 = itemL1[self.__node_index['direction']]
                    nodeListL2 = itemL1[self.__node_index['list of nodes']]
                    if directionL2 == 'H':
                        [faciesCode, fIndx] = self.__calcFaciesLevel2H(nodeListL2, alphaCoord)
                    else:
                        [faciesCode, fIndx] = self.__calcFaciesLevel2V(nodeListL2, alphaCoord)
                    break
        if faciesCode < 0 or fIndx < 0:
            # TODO: Proper error message
            raise ValueError("Something happened")
        return [faciesCode, fIndx]

    def __calcFaciesLevel2H(self, nodeListL2, alphaCoord):
        faciesCode = -1
        fIndx = -1
        x = alphaCoord[0]
        y = alphaCoord[1]
        for j in range(len(nodeListL2)):
            itemL2 = nodeListL2[j]
            typeNode = itemL2[self.__node_index['type']]
            if typeNode == 'F':
                if y <= itemL2[self.__node_index['y max']]:
                    indx = itemL2[self.__node_index['index']]
                    found = 0
                    for groupIndx in range(self.__nOverLayFacies):
                        if self.__isBackGroundFacies[groupIndx][indx] == 1:
                            z = alphaCoord[groupIndx + 2]
                            if self.__lowAlpha[groupIndx] < z <= self.__highAlpha[groupIndx]:
                                fIndx = self.__orderIndex[self.__overlayFaciesIndx[groupIndx]]
                                faciesCode = self.__faciesCode[fIndx]
                                found = 1
                                break
                    if found:
                        break
                    fIndx = self.__orderIndex[indx]
                    faciesCode = self.__faciesCode[fIndx]
                    break
            else:
                if y <= itemL2[self.__node_index['y max']]:
                    directionL3 = itemL2[self.__node_index['direction']]
                    nodeListL3 = itemL2[self.__node_index['list of nodes']]
                    if directionL3 == 'H':
                        # [faciesCode, fIndx] = self.__calcFaciesLevel3H(nodeListL3, y, z)
                        [faciesCode, fIndx] = self.__calcFaciesLevel3H(nodeListL3, alphaCoord)
                    else:
                        # [faciesCode, fIndx] = self.__calcFaciesLevel3V(nodeListL3, x, z)
                        [faciesCode, fIndx] = self.__calcFaciesLevel3V(nodeListL3, alphaCoord)
                    break
        if faciesCode < 0 or fIndx < 0:
            # TODO: Proper error message
            raise ValueError("Something happened")
        return [faciesCode, fIndx]

    def __calcFaciesLevel2V(self, nodeListL2, alphaCoord):
        faciesCode = -1
        fIndx = -1
        x = alphaCoord[0]
        y = alphaCoord[1]
        for j in range(len(nodeListL2)):
            itemL2 = nodeListL2[j]
            typeNode = itemL2[self.__node_index['type']]
            if typeNode == 'F':
                if x <= itemL2[self.__node_index['x max']]:
                    indx = itemL2[self.__node_index['index']]
                    found = 0
                    for groupIndx in range(self.__nOverLayFacies):
                        if self.__isBackGroundFacies[groupIndx][indx] == 1:
                            z = alphaCoord[groupIndx + 2]
                            if self.__lowAlpha[groupIndx] < z <= self.__highAlpha[groupIndx]:
                                fIndx = self.__orderIndex[self.__overlayFaciesIndx[groupIndx]]
                                faciesCode = self.__faciesCode[fIndx]
                                found = 1
                                break
                    if found:
                        break
                    fIndx = self.__orderIndex[indx]
                    faciesCode = self.__faciesCode[fIndx]
                    break
            else:
                if x <= itemL2[self.__node_index['x max']]:
                    directionL3 = itemL2[self.__node_index['direction']]
                    nodeListL3 = itemL2[self.__node_index['list of nodes']]
                    if directionL3 == 'H':
                        [faciesCode, fIndx] = self.__calcFaciesLevel3H(nodeListL3, alphaCoord)
                    else:
                        [faciesCode, fIndx] = self.__calcFaciesLevel3V(nodeListL3, alphaCoord)
                    break
        if faciesCode < 0 or fIndx < 0:
            # TODO: Proper error message
            raise ValueError("Something happened")
        return [faciesCode, fIndx]

    def __calcFaciesLevel3H(self, nodeListL3, alphaCoord):
        faciesCode = -1
        fIndx = -1
        y = alphaCoord[1]
        for k in range(len(nodeListL3)):
            itemL3 = nodeListL3[k]
            typeNode = itemL3[self.__node_index['type']]
            if typeNode != 'F':
                raise ValueError(
                    'Error in {}\n'
                    'Error: Programming error. Mismatch type. Expect F type.'
                    ''.format(self.__class__.__name__)
                )

            if y <= itemL3[self.__node_index['y max']]:
                indx = itemL3[self.__node_index['index']]
                found = 0
                for groupIndx in range(self.__nOverLayFacies):
                    if self.__isBackGroundFacies[groupIndx][indx] == 1:
                        z = alphaCoord[groupIndx + 2]
                        if self.__lowAlpha[groupIndx] < z <= self.__highAlpha[groupIndx]:
                            fIndx = self.__orderIndex[self.__overlayFaciesIndx[groupIndx]]
                            faciesCode = self.__faciesCode[fIndx]
                            found = 1
                            break
                if found:
                    break

                fIndx = self.__orderIndex[indx]
                faciesCode = self.__faciesCode[fIndx]
                break
        if faciesCode < 0 or fIndx < 0:
            # TODO: Proper error message
            raise ValueError("Something happened")
        return [faciesCode, fIndx]

    def __calcFaciesLevel3V(self, nodeListL3, alphaCoord):
        faciesCode = -1
        fIndx = -1
        x = alphaCoord[0]
        for k in range(len(nodeListL3)):
            itemL3 = nodeListL3[k]
            typeNode = itemL3[self.__node_index['type']]
            if typeNode != 'F':
                raise ValueError(
                    'Error in {}\n'
                    'Error: Programming error. Mismatch type. Expect F type.'
                    ''.format(self.__className)
                )
            if x <= itemL3[self.__node_index['x max']]:
                indx = itemL3[self.__node_index['index']]

                found = 0
                for groupIndx in range(self.__nOverLayFacies):
                    if self.__isBackGroundFacies[groupIndx][indx] == 1:
                        z = alphaCoord[groupIndx + 2]
                        if self.__lowAlpha[groupIndx] < z <= self.__highAlpha[groupIndx]:
                            fIndx = self.__orderIndex[self.__overlayFaciesIndx[groupIndx]]
                            faciesCode = self.__faciesCode[fIndx]
                            found = 1
                            break
                if found:
                    break

                fIndx = self.__orderIndex[indx]
                faciesCode = self.__faciesCode[fIndx]
                break

        if faciesCode < 0 or fIndx < 0:
            # TODO: Proper error message
            raise ValueError("Something happened")
        return [faciesCode, fIndx]

    def __calcPolyLevel(self, direction, nodeList, polyLevelAbove, levelNumber):
        TYPE = self.__node_index['type']
        DIR = self.__node_index['direction']
        NLIST = self.__node_index['list of nodes']
        # YMAX = self.__node_index['y max']
        POLY = self.__node_index['polygon']
        # XMIN = self.__node_index['x min']
        XMAX = self.__node_index['x max']
        # YMIN = self.__node_index['y min']
        YMAX = self.__node_index['y max']
        if direction == 'H':
            pt1Prev = polyLevelAbove[0]
            pt2Prev = polyLevelAbove[1]
            x1 = pt1Prev[0]
            x2 = pt2Prev[0]
            yPrev = pt1Prev[1]

            for k in range(len(nodeList)):
                poly = []
                item = nodeList[k]
                ymax = item[YMAX]
                pt1 = [x1, yPrev]
                pt4 = [x1, ymax]
                pt2 = [x2, yPrev]
                pt3 = [x2, ymax]
                yPrev = ymax
                poly.append(pt1)
                poly.append(pt2)
                poly.append(pt3)
                poly.append(pt4)
                item[POLY] = poly  # Assign calculated polygon

                # Calculate polygons for level below this node
                if levelNumber < 3:
                    typeNode = item[TYPE]
                    if typeNode == 'N':
                        directionNextLevel = item[DIR]
                        nodeListNextLevel = item[NLIST]
                        self.__calcPolyLevel(
                            directionNextLevel, nodeListNextLevel, poly, levelNumber + 1)

        else:
            pt1Prev = polyLevelAbove[0]
            pt4Prev = polyLevelAbove[3]
            y1 = pt1Prev[1]
            y2 = pt4Prev[1]
            xPrev = pt1Prev[0]

            for k in range(len(nodeList)):
                poly = []
                item = nodeList[k]
                typeNode = item[TYPE]
                xmax = item[XMAX]
                pt1 = [xPrev, y1]
                pt2 = [xmax, y1]
                pt3 = [xmax, y2]
                pt4 = [xPrev, y2]
                xPrev = xmax
                poly.append(pt1)
                poly.append(pt2)
                poly.append(pt3)
                poly.append(pt4)
                item[POLY] = poly  # Assign calculated polygon

                # Calculate polygons for level below this node
                if levelNumber < 3:
                    typeNode = item[TYPE]
                    if typeNode == 'N':
                        directionNextLevel = item[DIR]
                        nodeListNextLevel = item[NLIST]
                        self.__calcPolyLevel(
                            directionNextLevel, nodeListNextLevel, poly, levelNumber + 1)
        return

    def __writeDataForTruncRule(self):
        TYPE = self.__node_index['type']
        # DIR = self.__node_index['direction']
        NLIST = self.__node_index['list of nodes']
        # POLY = self.__node_index['polygon']
        INDX = self.__node_index['index']
        PFRAC = self.__node_index['probability fraction']
        PROB = self.__node_index['probability']
        XMIN = self.__node_index['x min']
        XMAX = self.__node_index['x max']
        YMIN = self.__node_index['y min']
        YMAX = self.__node_index['y max']

        nodeListL1 = self.__truncStructure[NLIST]
        for i in range(len(nodeListL1)):
            itemL1 = nodeListL1[i]
            prob = itemL1[PROB]
            xmin = itemL1[XMIN]
            xmax = itemL1[XMAX]
            ymin = itemL1[YMIN]
            ymax = itemL1[YMAX]
            if itemL1[TYPE] == 'F':
                indx = itemL1[INDX]
                probFrac = itemL1[PFRAC]
                fName = self.__faciesInTruncRule[indx]
                if self.__printInfo >= 3:
                    text = 'L1: {}  ProbFrac: {}  Prob: {}'.format(fName, probFrac, prob)
                    text += ' X: [{}, {}] Y: [{}, {}]'.format(xmin, xmax, ymin, ymax)
                    print(text)

            else:
                nodeListL2 = itemL1[NLIST]
                if self.__printInfo >= 3:
                    text = 'L1: GRP  Prob: {}'.format(prob)
                    text += ' X: [{}, {}] Y: [{}, {}]'.format(xmin, xmax, ymin, ymax)
                    print(text)
                for j in range(len(nodeListL2)):
                    itemL2 = nodeListL2[j]
                    prob = itemL2[PROB]
                    xmin = itemL2[XMIN]
                    xmax = itemL2[XMAX]
                    ymin = itemL2[YMIN]
                    ymax = itemL2[YMAX]
                    if itemL2[TYPE] == 'F':
                        indx = itemL2[INDX]
                        probFrac = itemL2[PFRAC]
                        fName = self.__faciesInTruncRule[indx]
                        if self.__printInfo >= 3:
                            text = '  L2: {}  ProbFrac: {}  Prob: {}'.format(fName, probFrac, prob)
                            text += ' X: [{}, {}] Y: [{}, {}]'.format(xmin, xmax, ymin, ymax)
                            print(text)
                    else:
                        nodeListL3 = itemL2[NLIST]
                        if self.__printInfo >= 3:
                            text = '  L2: GRP  Prob: {}'.format(prob)
                            text += ' X: [{}, {}] Y: [{}, {}]'.format(xmin, xmax, ymin, ymax)
                            print(text)
                        for k in range(len(nodeListL3)):
                            itemL3 = nodeListL3[k]
                            indx = itemL3[INDX]
                            probFrac = itemL3[PFRAC]
                            prob = itemL3[PROB]
                            xmin = itemL3[XMIN]
                            xmax = itemL3[XMAX]
                            ymin = itemL3[YMIN]
                            ymax = itemL3[YMAX]
                            fName = self.__faciesInTruncRule[indx]
                            if self.__printInfo >= 3:
                                text = '    L3: {}  ProbFrac: {}  Prob: {}'.format(fName, probFrac, prob)
                                text += ' X: [{}, {}] Y: [{}, {}]'.format(xmin, xmax, ymin, ymax)
                                print(text)

    def __getPolygonAndFaciesList(self):
        TYPE = self.__node_index['type']
        INDX = self.__node_index['index']
        NLIST = self.__node_index['list of nodes']
        POLY = self.__node_index['polygon']
        nodeListL1 = self.__truncStructure[NLIST]
        fIndxList = []
        polygons = []
        for i in range(len(nodeListL1)):
            itemL1 = nodeListL1[i]
            typeNodeL1 = itemL1[TYPE]
            if typeNodeL1 == 'F':
                indxL1 = itemL1[INDX]
                polyL1 = itemL1[POLY]
                fIndxList.append(indxL1)
                polygons.append(polyL1)
            else:
                nodeListL2 = itemL1[NLIST]
                for j in range(len(nodeListL2)):
                    itemL2 = nodeListL2[j]
                    typeNodeL2 = itemL2[TYPE]
                    if typeNodeL2 == 'F':
                        indxL2 = itemL2[INDX]
                        polyL2 = itemL2[POLY]
                        fIndxList.append(indxL2)
                        polygons.append(polyL2)
                    else:
                        nodeListL3 = itemL2[NLIST]
                        for k in range(len(nodeListL3)):
                            itemL3 = nodeListL3[k]
                            indxL3 = itemL3[INDX]
                            polyL3 = itemL3[POLY]
                            fIndxList.append(indxL3)
                            polygons.append(polyL3)

        self.__nPoly = len(polygons)
        self.__polygons = polygons
        self.__fIndxPerPolygon = fIndxList
        return

    def truncMapPolygons(self):
        assert self.__setTruncRuleIsCalled == True
        DIR = self.__node_index['direction']
        NLIST = self.__node_index['list of nodes']
        POLY = self.__node_index['polygon']
        polygons = []
        poly = []
        # Unit square (2D truncation map)
        pt1 = [0.0, 0.0]
        pt2 = [1.0, 0.0]
        pt3 = [1.0, 1.0]
        pt4 = [0.0, 1.0]
        poly.append(pt1)
        poly.append(pt2)
        poly.append(pt3)
        poly.append(pt4)

        self.__truncStructure[POLY] = poly
        directionL1 = self.__truncStructure[DIR]
        nodeListL1 = self.__truncStructure[NLIST]
        levelNumber = 1
        self.__calcPolyLevel(directionL1, nodeListL1, poly, levelNumber)

        # Create list of polygons and corresponding list of facies
        self.__getPolygonAndFaciesList()
        polygons = copy.deepcopy(self.__polygons)
        return [polygons]

    def faciesIndxPerPolygon(self):
        fIndxList = copy.copy(self.__fIndxPerPolygon)
        return fIndxList

    def initialize(self, mainFaciesTable, faciesInZone, truncStructureList,
                   backGroundFacies=None, overlayFacies=None, overlayTruncCenter=None, printInfo=0):
        """
           Description: Initialize the truncation object from input variables.
                        This function is used when the truncation object is not initialized 
                        by reading the specification from the model file.
           Input: mainFaciesTable - Specify the global facies table and is used to check that specified facies
                                    is legal.
                  faciesInZone    - List of facies to be modelled for the zone this truncation rule is defined for.
                  truncStructureList - Contain definition of truncation rule. See details in specification
                                       described for function __setTruncStructure.
                  backGroundFacies   - List of lists of background facies. The list backGroundFacies[groupIndx]
                                       is a list of background facies for overlay facies overlayFacies[groupIndx]
                                       where groupIndx run over the number of overlay facies.
                  overlayTruncCenter - List of values for the interval center value for the truncation interval for overlay facies.
              
        """
        # Initialize data structure
        self.__setEmpty()

        # Main facies table is set
        self.__mainFaciesTable = copy.copy(mainFaciesTable)
        self.__nFaciesMain = self.__mainFaciesTable.getNFacies()

        # Facies in zone are set
        self.__faciesInZone = copy.copy(faciesInZone)
        self.__nFacies = len(faciesInZone)
        self.__faciesIsDetermined = np.zeros(self.__nFacies, int)

        # Facies code for facies in zone
        self.__faciesCode = []
        for fName in self.__faciesInZone:
            fCode = self.__mainFaciesTable.getFaciesCodeForFaciesName(fName)
            self.__faciesCode.append(fCode)

        # Set truncation rule (hierarchy of rectangular polygons)
        self.__setTruncStructure(truncStructureList)

        if self.__printInfo >= 3:
            print('Debug info: Background facies defined: ')
            print(repr(self.__faciesInTruncRule))

        # Check consistency
        if overlayFacies != None:
            m1 = len(backGroundFacies)
            m2 = len(overlayFacies)
            m3 = len(overlayTruncCenter)
            if m1 != m2 or m1 != m3:
                raise ValueError(
                    'Programming error in function initialize in class ' + self.__className + '\n'
                    'Lenght of input lists are different from each other'
                )
            self.__nGaussFieldInModel = 2 + m2

        # Set which facies to be used as background facies when overprint facies is applied
        self.__defineBackgroundFaciesAndOverLayFacies(backGroundFacies, overlayFacies)

        # Parameter for overlay facies truncation
        self.__overLayTruncIntervalCenter = copy.copy(overlayTruncCenter)

        # Check that facies in truncation rule is consistent with facies in zone
        self.__checkFaciesForZone()

        self.__nFacies = len(self.__faciesInTruncRule)

    def __defineBackgroundFaciesAndOverLayFacies(self, backGroundFacies=None, overlayFacies=None):
        """
        Define the class member variables that is used to handle overlay facies.
        Input: backGroundFacies - A list of lists of background facies per overlay facies
               overlayFacies    - A list of overlay facies
        """
        if backGroundFacies is not None:
            assert len(backGroundFacies) == len(overlayFacies)

        nOverLayFacies = len(overlayFacies)
        self.__nOverLayFacies = nOverLayFacies
        self.__isBackGroundFacies = np.zeros((nOverLayFacies, len(self.__faciesInZone)), int)
        self.__backGroundFaciesIndx = []
        for groupIndx in range(nOverLayFacies):
            bgFaciesGroup = backGroundFacies[groupIndx]
            bgFaciesIndxList = []
            self.__backGroundFaciesIndx.append(bgFaciesIndxList)
            indx = -1
            for bgFaciesName in bgFaciesGroup:
                for i in range(len(self.__faciesInTruncRule)):
                    fN = self.__faciesInTruncRule[i]
                    if fN == bgFaciesName:
                        indx = i
                        break
                if indx < 0:
                    raise ValueError(
                        'Error in {}'
                        'Error: Inconsistent facies names as input for background facies. Programming error'
                        ''.format(self.__className)
                    )
                else:
                    bgFaciesIndxList.append(indx)
                    self.__isBackGroundFacies[groupIndx, indx] = 1
            overlayFaciesName = overlayFacies[groupIndx]
            [nFacies, indx, fIndx, isNew] = self.__addFaciesToTruncRule(overlayFaciesName)
            if isNew == 1:
                self.__overlayFaciesIndx.append(indx)
                self.__orderIndex.append(fIndx)
            else:
                raise ValueError(
                    'Error in {0}'
                    'Error: Specified overlay facies {1} is already used as background facies.'
                    ''.format(self.__className, overlayFaciesName)
                )

    def __setTruncStructure(self, truncStructureList):
        # Truncation structure specified by list of facies in hierarchical way with items of the form
        # [faciesName,level]
        # where level is one number for L1 ([1] or [2] ..), two number for L2 ([1,1] [1,2] ...) or for L3 ([2,1,1],[2,1,2]...)
        # item in list is of the form ['Facies',probFrac,L1,L2,L3]
        # Example: The list can be:
        # 'H'
        # ['F1',0.5,1,0,0]
        # ['F1',0.5,2,1,0]
        # ['F2',1.0,2,2,1]
        # ['F3',1.0,2,2,2]
        # ['F4',1.0,2,3,0]
        # ['F5',1.0,3,0,0]
        # This means: First element is either H or V for Horizontal subdivision or Vertical subdivision of level 1
        # Here Horizontal subdivision is chosen.
        # First polygon in the truncation map is a horizontal rectangle at bottom (Level 1 polygon)
        # The second Level 1 is composed and split:
        #   The first Level 2 polygon is the leftmost rectangle
        #   The second Level 2 polygon is again composed and split:
        #     The first Level 3 polygon is at bottom
        #     The second Level 3 polygon is at top
        #   The third Level 2 polygon is the rightmost rectangle.
        # The third Level 1 polygon is at top.

        # Index for elements in an item in the truncStructureList
        INDXFAC = 0
        INDXPFRAC = 1
        INDXL1 = 2
        INDXL2 = 3
        INDXL3 = 4

        # First item contain only 'H' or 'V'
        directionL1 = 'H'
        directionL2 = 'V'
        directionL3 = 'H'
        directionL1 = truncStructureList[0]
        if directionL1 != 'V' and directionL1 != 'H':
            raise ValueError("The direction of L1 must be either 'H' or 'V'. It is {}".format(directionL1))

        if directionL1 == 'V':
            directionL2 = 'H'
            directionL3 = 'V'

        nodeList = None
        poly = None
        nPoly = 0
        nFacies = 0
        truncStructure = ['N', directionL1, nodeList, 0.0, poly, 0.0, 1.0, 0.0, 1.0]
        nodeListLevel1 = []
        truncStructure[self.__node_index['list of nodes']] = nodeListLevel1
        L1Prev = 0
        L2Prev = 0
        L3Prev = 0
        for i in range(1, len(truncStructureList)):
            # L1 is an integer from 1 and up
            # L2 is either 0 which mean Level1 or an integer from 1 and up
            # L3 is either 0 which means Level2 or Level 1 or an integer from 1 and up
            item = truncStructureList[i]
            fName = item[INDXFAC]
            probFrac = item[INDXPFRAC]
            L1 = int(item[INDXL1])
            L2 = int(item[INDXL2])
            L3 = int(item[INDXL3])
            # print('L1,L2,L3: ' + str(L1) + ' ' + str(L2) + ' ' + str(L3))
            if L1 == 0:
                raise ValueError('Error: L1 = 0')
            elif L3 > 0 and L2 == 0:
                raise ValueError('Error: L3 > 0 and L2 = 0')
            elif L1 < L1Prev:
                raise ValueError('Error: L1 < L1Prev')
            elif L1 == L1Prev:
                if L2 < L2Prev:
                    raise ValueError('Error: L1 == L1Prev and L2 < L2Prev')
                elif L2 == L2Prev:
                    if L3 <= L3Prev:
                        raise ValueError('Error: L1 == L1Prev and L2 == L2Prev and L3 <= L3Prev')
                    elif L3 - L3Prev > 1:
                        raise ValueError(
                            'Error: L1 == L1Prev and L2 == L2Prev and L3 - L3Prev > 1')
                elif L2 - L2Prev > 1:
                    raise ValueError('Error: L1 == L1Prev and L2 - L2Prev > 1')
            elif L1 - L1Prev > 1:
                raise ValueError('Error: L1 - L1Prev > 1')

            elif L1 == L1Prev and L2 == L2Prev:
                if L3 != L3Prev + 1:
                    raise ValueError('Error: L1 == L1Prev and L2 == L2Prev and L3 != L3Prev + 1')

            elif L1 == L1Prev:
                if L3Prev == 0 and L3 == 0:
                    if L2 != L2Prev + 1:
                        raise ValueError('Error: L1 == L1Prev and L3 == 0 and L3Prev == 0 and L3 != L3Prev + 1')

            elif probFrac < 0.0 or probFrac > 1.0:
                raise ValueError('Error: ' + 'probFrac < 0 or probFrac > 1')

            if L1 > L1Prev:
                if L2 == 0:
                    # Create new facies node for L1 level
                    [nFacies, indx, fIndx, isNew] = self.__addFaciesToTruncRule(fName)
                    nPoly += 1
                    poly = []
                    nodeData = ['F', indx, probFrac, 0.0, poly, 0.0, 0.0, 0.0, 0.0]
                    nodeListLevel1.append(nodeData)
                    if isNew == 1:
                        self.__orderIndex.append(fIndx)
                elif L2 == 1:
                    # Create L1 parent node for L2 nodes
                    self.__useLevel2 = 1
                    poly = []
                    # nodeListLevel2 is pointer to list of level 2 nodes for current level 1 node
                    nodeListLevel2 = []
                    nodeData = ['N', directionL2, nodeListLevel2, 0.0, poly, 0.0, 0.0, 0.0, 0.0]
                    nodeListLevel1.append(nodeData)
                    if L3 == 0:
                        # Create L2 facies node
                        [nFacies, indx, fIndx, isNew] = self.__addFaciesToTruncRule(fName)
                        nPoly += 1
                        poly = []
                        nodeData = ['F', indx, probFrac, 0.0, poly, 0.0, 0.0, 0.0, 0.0]
                        nodeListLevel2.append(nodeData)
                        if isNew == 1:
                            self.__orderIndex.append(fIndx)
                    elif L3 == 1:
                        # Create L2 parent node for L3 nodes
                        self.__useLevel3 = 1
                        poly = []
                        # nodeListLevel3 is pointer to list of level 3 nodes for current level 2 node
                        nodeListLevel3 = []
                        nodeData = ['N', directionL3, nodeListLevel3, 0.0, poly, 0.0, 0.0, 0.0, 0.0]
                        nodeListLevel2.append(nodeData)
                        parentNodeDefinedL2 = 1

                        # Create L3 facies node
                        [nFacies, indx, fIndx, isNew] = self.__addFaciesToTruncRule(fName)
                        nPoly += 1
                        poly = []
                        nodeData = ['F', indx, probFrac, 0.0, poly, 0.0, 0.0, 0.0, 0.0]
                        nodeListLevel3.append(nodeData)
                        if isNew == 1:
                            self.__orderIndex.append(fIndx)

            elif L1 == L1Prev:
                if L2 > L2Prev:
                    self.__useLevel2 = 1
                    if L3 == 0:

                        # Create L2 facies node
                        [nFacies, indx, fIndx, isNew] = self.__addFaciesToTruncRule(fName)
                        nPoly += 1
                        poly = []
                        nodeData = ['F', indx, probFrac, 0.0, poly, 0.0, 0.0, 0.0, 0.0]
                        nodeListLevel2.append(nodeData)
                        if isNew == 1:
                            self.__orderIndex.append(fIndx)
                    elif L3 == 1:
                        # Create L2 parent node for L3 nodes
                        self.__useLevel3 = 1
                        poly = []
                        # nodeListLevel3 is pointer to list of level 3 nodes for current level 2 node
                        nodeListLevel3 = []
                        nodeData = ['N', directionL3, nodeListLevel3, 0.0, poly, 0.0, 0.0, 0.0, 0.0]
                        nodeListLevel2.append(nodeData)
                        parentNodeDefinedL2 = 1

                        # Create L3 facies node
                        [nFacies, indx, fIndx, isNew] = self.__addFaciesToTruncRule(fName)
                        nPoly += 1
                        poly = []
                        nodeData = ['F', indx, probFrac, 0.0, poly, 0.0, 0.0, 0.0, 0.0]
                        nodeListLevel3.append(nodeData)
                        if isNew == 1:
                            self.__orderIndex.append(fIndx)
                    else:
                        raise ValueError('Error: L3 cannot be > 1 when L2 has increased')

                elif L2 == L2Prev:
                    self.__useLevel2 = 1
                    if L3 > L3Prev:
                        # Create L3 facies node
                        self.__useLevel3 = 1
                        [nFacies, indx, fIndx, isNew] = self.__addFaciesToTruncRule(fName)
                        nPoly += 1
                        poly = []
                        nodeData = ['F', indx, probFrac, 0.0, poly, 0.0, 0.0, 0.0, 0.0]
                        nodeListLevel3.append(nodeData)
                        if isNew == 1:
                            self.__orderIndex.append(fIndx)
                    else:
                        raise ValueError('Error: L3 must be 1 larger than L3Prev when L1 == L1Prev and L2 == L2Prev')

            L1Prev = L1
            L2Prev = L2
            L3Prev = L3
        self.__truncStructure = truncStructure
        self.__nPoly = nPoly

    def XMLAddElement(self, parent):
        TYPE = self.__node_index['type']
        DIR = self.__node_index['direction']
        NLIST = self.__node_index['list of nodes']
        PFRAC = self.__node_index['probability fraction']
        INDX = self.__node_index['index']
        # Add to the parent element a new element with specified tag and attributes.
        # The attributes are a dictionary with {name:value}
        # After this function is called, the parent element has got a new child element
        # for the current class.
        nGaussField = self.__nOverLayFacies + 2
        attribute = {'name': 'Trunc2D_Cubic_Multi_Overlay', 'nGFields': str(nGaussField)}
        tag = 'TruncationRule'
        trRuleElement = Element(tag, attribute)
        # Put the xml commands for this truncation rule as the last child for the parent element
        parent.append(trRuleElement)
        # print(repr(self.__truncStructure))
        directionL1 = self.__truncStructure[DIR]
        nodeListL1 = self.__truncStructure[NLIST]
        tag = 'L1'
        attribute = {'direction': directionL1}
        nodeElementL1 = Element(tag, attribute)
        trRuleElement.append(nodeElementL1)
        for i in range(len(nodeListL1)):
            itemL1 = nodeListL1[i]
            typeNode = itemL1[TYPE]
            if typeNode == 'F':
                indx = itemL1[INDX]
                fName = self.__faciesInTruncRule[indx]
                probFrac = itemL1[PFRAC]
                tag = 'ProbFrac'
                attribute = {'name': fName}
                nodeElementL2 = Element(tag, attribute)
                nodeElementL2.text = ' ' + str(probFrac) + ' '
                nodeElementL1.append(nodeElementL2)
            else:
                directionL2 = itemL1[DIR]
                tag = 'L2'
                nodeElementL2 = Element(tag)
                nodeElementL1.append(nodeElementL2)
                nodeListL2 = itemL1[NLIST]
                for j in range(len(nodeListL2)):
                    itemL2 = nodeListL2[j]
                    typeNode = itemL2[TYPE]
                    if typeNode == 'F':
                        indx = itemL2[INDX]
                        fName = self.__faciesInTruncRule[indx]
                        probFrac = itemL2[PFRAC]
                        tag = 'ProbFrac'
                        attribute = {'name': fName}
                        nodeElementL3 = Element(tag, attribute)
                        nodeElementL3.text = ' ' + str(probFrac) + ' '
                        nodeElementL2.append(nodeElementL3)
                    else:
                        directionL3 = itemL2[DIR]
                        tag = 'L3'
                        nodeElementL3 = Element(tag)
                        nodeElementL2.append(nodeElementL3)
                        nodeListL3 = itemL2[NLIST]
                        for k in range(len(nodeListL3)):
                            itemL3 = nodeListL3[k]
                            indx = itemL3[INDX]
                            fName = self.__faciesInTruncRule[indx]
                            probFrac = itemL3[PFRAC]
                            tag = 'ProbFrac'
                            attribute = {'name': fName}
                            nodeElementL3Below = Element(tag, attribute)
                            nodeElementL3Below.text = ' ' + str(probFrac) + ' '
                            nodeElementL3.append(nodeElementL3Below)

        for groupIndx in range(self.__nOverLayFacies):
            indx = self.__overlayFaciesIndx[groupIndx]
            fName = self.__faciesInTruncRule[indx]
            tag = 'OverLayFacies'
            attribute = {'name': fName}
            overLayElement = Element(tag, attribute)
            trRuleElement.append(overLayElement)
            tag = 'TruncIntervalCenter'
            ticElement = Element(tag)
            ticElement.text = ' ' + str(self.__overLayTruncIntervalCenter[groupIndx]) + ' '
            overLayElement.append(ticElement)
            tag = 'Background'
            for i in range(len(self.__backGroundFaciesIndx[groupIndx])):
                indx = self.__backGroundFaciesIndx[groupIndx][i]
                fName = self.__faciesInTruncRule[indx]
                bElement = Element(tag)
                bElement.text = ' ' + fName + ' '
                overLayElement.append(bElement)
