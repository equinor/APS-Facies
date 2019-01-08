#!/bin/env python
# -*- coding: utf-8 -*-
import copy
from xml.etree.ElementTree import Element

import numpy as np

from src.algorithms.Trunc2D_Base_xml import Trunc2D_Base
from src.utils.constants.simple import Debug
from src.utils.xmlUtils import getKeyword

"""
-----------------------------------------------------------------------
class Trunc2D_Cubic

Description: This class is derived from Trunc2D_Base which contain common data structure for
             truncation algorithms with overlay facies.

             A general truncation rule using rectangular polygons for the truncation map is implemented here.
             It is specified in a hierarchical way with 3 levels of subdivision of the truncation
             unit square into rectangles.
             In addition to the facies specified for the 2D truncation map, it is possible
             to specify additional facies using additional gaussian fields. These facies are specified
             to overprint or "overlay" the "background" facies which was specified for the 2D truncation map.
             Note that for each overprint facies a subset of the facies defined by the two first
             Gaussian fields must be defined. The algorithm also requires that there can be only one
             overprint facies that can "overprint" a background facies. So if e.g. 3 background facies
             are modelled like F1,F2,F3 and 2 overprint facies are specified like F4,F5, then the background facies
             must be divided into 2 groups like e.g. (F1,F3) and (F2) where one group is overprinted by F4
             and the other by F5. It is not possible to the same background facies in two or more groups.
             It is also possible to define different rectangular polygons from the truncation map
             to belong to the same facies in order to generate truncation rule with non-neighbour
             polygons in the truncation map.

 Public member functions:
  Constructor:
    def __init__(self,trRuleXML=None, mainFaciesTable=None, faciesInZone=None,
                 nGaussFieldInModel=None, debug_level=Debug.OFF, modelFileName=None)



  Public functions:
    def initialize(self,mainFaciesTable,faciesInZone,truncStructureList,
                 backGroundFacies=None,overlayFacies=None,overlayTruncCenter=None,debug_level=Debug.OFF)
    def writeContentsInDataStructure(self):
    def getClassName(self)
    def useConstTruncModelParam(self)
    def setTruncRule(self, faciesProb, cellIndx=0)
    def defineFaciesByTruncRule(self, alphaCoord)
    def truncMapPolygons(self)
    def faciesIndxPerPolygon(self)
    def XMLAddElement(self, parent)


  Private functions:
    def __setEmpty(self)
    def __interpretXMLTree(self, trRuleXML, modelFileName):
    def __calcProbForEachNode(self, faciesProb)
    def __calcThresholdValues(self)
    def __calcFaciesLevel1V(self, nodeListL1, alphaCoord)
    def __calcFaciesLevel1H(self, nodeListL1, alphaCoord)
    def __calcFaciesLevel2H(self, nodeListL2, alphaCoord)
    def __calcFaciesLevel2V(self, nodeListL2, alphaCoord)
    def __calcFaciesLevel3H(self, nodeListL3, alphaCoord)
    def __calcFaciesLevel3V(self, nodeListL3, alphaCoord)
    def __calcPolyLevel(self, direction, nodeList, polyLevelAbove, levelNumber)
    def __writeDataForTruncRule(self)
    def __getPolygonAndFaciesList(self)
    def __setTruncStructure(self, truncStructureList)

-------------------------------------------------------------
"""


class Trunc2D_Cubic(Trunc2D_Base):
    """
    This class implements adaptive plurigaussian field truncation using two simulated gaussian fields (with trend).
    """

    def __setEmpty(self):

        # Specific variables for class Trunc2D_Cubic
        self._className = self.__class__.__name__

        # Variables containing truncations for the 2D truncation map
        self.__truncStructure = []
        self.__useLevel2 = 0
        self.__useLevel3 = 0
        # The trunc structure contain a tree structure of data for the hierarchy of
        # how the truncation map is split into rectangular polygons. In this data structure the nodes in the tree
        # is of two types. Either the node data is of form:
        #     ['N',direction,nodeList,prob,polygon,xmin,xmax,ymin.ymax]  or the form
        #     ['F',indx,     probFrac,prob,polygon,xmin,xmax,ymin,ymax]

        # The _node_index dictionary give name to each index in nodeData list
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

        # List of polygons the truncation map is split into
        self.__polygons = []

        # List of facies index ( index in faciesInZone) for each polygon
        self.__fIndxPerPolygon = []

        self.__roundOffResolution = 209

    def __init__(self, trRuleXML=None, mainFaciesTable=None, faciesInZone=None, gaussFieldsInZone=None,
                 debug_level=Debug.OFF, modelFileName=None, zoneNumber=None):
        """
        This constructor can either create a new object by reading the information
        from an XML tree or it can create an empty data structure for such an object.
        If an empty data structure is created, the initialize function must be used.

        About data structure:
        All information related to common data which is used by more than one truncation algorithm
        is saved in the base class Trunc2D_Base.

        The common data are:

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

            5. alphaIndx.
            The truncation cube is defined by coordinates (alpha1, alpha2) for the background facies truncation map
            and is extended to more dimensions if overlay facies is  modelled. The index list alphaIndx associate
            gauss field with alpha coordinates. j = alphaIndx[i]  where i is alpha coordinate number and j is gauss field number.

        The algorithm for Cubic truncation rule depends on specific data only relevant for
        this algorithm. The data structure for this includes a tree structure of nodes where each node
        is either a composed node or a simple node. A simple node contain information about a rectangular area
        in truncation map, and which facies it belongs to. A composed node consists of a tree structure of simple nodes.
        This hierarchical representation of the rectangular polygons splitting the unit square of the 2D truncation map
        has three levels. These levels are specified in the XML file by keywords L1,L2,L3.
        Within L1 keyword there can be either L2 or one or more ProbFrac keywords.
        Within L2 keyword there can be either L3 or one or more ProbFrac keywords.
        Within L3 keyword there can be only ProbFrac keywords (one or more).
        """
        # Initialize data structure to empty if trRule is None and call up the base class function setEmpty as well.
        # If the trRule is not none, the base class data structure is initialized.
        nGaussFieldsInBackGroundModel = 2
        super().__init__(trRuleXML, mainFaciesTable, faciesInZone, gaussFieldsInZone,
                         debug_level, modelFileName, nGaussFieldsInBackGroundModel)
        self.__setEmpty()

        if trRuleXML is not None:
            if self._debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: Read data from model file in: ' + self._className)

            # Read truncation rule for background facies from xml tree.
            # Here the hierarchy of polygons in the 2D truncation map defined by the two
            # first transformed gaussian fields is defined. This is specific for the Cubic truncations.
            self.__interpretXMLTree(trRuleXML[0], modelFileName)

            # Call base class method to read truncation rule for overlay facies.
            # Overlay facies truncation rules are read here. The overlay facies does not
            # have to know anything about how the 2D truncation map defined by the two first
            # transformed gaussian fields looks like. It only need to know which facies in the 2D map
            # is "background" for each overlay facies. Therefore data structure and methods
            # related to overprint facies is common to several different truncation algorithms.
            self._interpretXMLTree_overlay_facies(trRuleXML[0], modelFileName, zoneNumber)

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
            if self._debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: Create empty object for: ' + self._className)
                #  End of __init__

    def __interpretXMLTree(self, trRuleXML, modelFileName):
        """
        Initialize object from xml tree object trRuleXML.
        This function read Cubic truncation rules.
        It does however NOT read any Overlay facies.
        This is done by methods from base class which handle overlay facies.
        """
        self._className = 'Trunc2D_Cubic'
        if self._debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: -- Start read background model in ' + self._className + ' from model file')
        # Get info from the XML model file tree for this truncation rule
        TYPE = self.__node_index['type']
        NLIST = self.__node_index['list of nodes']
        INDX = self.__node_index['index']
        PFRAC = self.__node_index['probability fraction']

        truncStructure = []
        nPoly = 0
        # Keyword BackGroundModel
        bgmObj = getKeyword(trRuleXML, 'BackGroundModel', 'TruncationRule', modelFileName, required=True)

        kw1 = 'L1'
        L1Obj = getKeyword(bgmObj, kw1, 'BackGroundModel', modelFile=modelFileName, required=True)
        text = L1Obj.get('direction')
        directionL1 = text.strip()
        if directionL1 != 'H' and directionL1 != 'V':
            raise ValueError(
                'Error when reading model file: {}\n'
                'Error: Read truncation rule: {}\n'
                'Error: Specified attribute "direction" must be H or V.'
                ''.format(modelFileName, self._className)
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
            # print('Child L1 tag and attribute:')
            # print(childL1.tag,childL1.attrib)
            if childL1.tag == kw2:
                text = childL1.get('name')
                fName = text.strip()
                text = childL1.text
                probFrac = float(text.strip())
                if fName not in self._faciesInZone:
                    raise ValueError(
                        'Error when reading model file: {0}\n'
                        'Error: Read truncation rule: {1}\n'
                        'Error: Specified facies name in truncation rule: {2} is not defined for this zone.'
                        ''.format(modelFileName, self._className, fName)
                    )
                if probFrac < 0.0 or probFrac > 1.0:
                    raise ValueError(
                        'Error when reading model file: {}\n'
                        'Error: Read truncation rule: {}\n'
                        'Error: Specified probability fraction in truncation rule is outside [0,1].'
                        ''.format(modelFileName, self._className)
                    )

                nFacies, indx, fIndx, isNew = self._addFaciesToTruncRule(fName)
                nPoly += 1

                poly = []
                # nodeData = ['F',indx,probFrac,prob,polygon,xmin,xmax,ymin,ymax]
                nodeData = ['F', indx, probFrac, 0.0, poly, 0.0, 0.0, 0.0, 0.0]
                nodeListLevel1.append(nodeData)
                if isNew == 1:
                    self._orderIndex.append(fIndx)
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
                    # print('Child L2 tag and attribute:')
                    # print(childL2.tag,childL2.attrib)
                    if childL2.tag == kw2:
                        text = childL2.get('name')
                        fName = text.strip()
                        text = childL2.text
                        probFrac = float(text.strip())
                        if fName not in self._faciesInZone:
                            raise ValueError(
                                'Error when reading model file: ' + modelFileName + '\n'
                                'Error: Read truncation rule: ' + self._className + '\n'
                                'Error: Specified facies name in truncation rule: ' + fName +
                                ' is not defined for this zone.'
                            )
                        elif probFrac < 0.0 or probFrac > 1.0:
                            raise ValueError(
                                'Error when reading model file: ' + modelFileName + '\n'
                                'Error: Read truncation rule: ' + self._className + '\n'
                                'Error: Specified probability fraction in truncation rule is outside [0,1]'
                            )

                        nFacies, indx, fIndx, isNew = self._addFaciesToTruncRule(fName)
                        nPoly += 1

                        poly = []
                        # nodeData = ['F',indx,probFrac,prob,polygon,xmin,xmax,ymin,ymax]
                        nodeData = ['F', indx, probFrac, 0.0, poly, 0.0, 0.0, 0.0, 0.0]
                        nodeListLevel2.append(nodeData)
                        if isNew == 1:
                            self._orderIndex.append(fIndx)
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
                            # print('Child L3 tag and attribute:')
                            # print(childL3.tag,childL3.attrib)
                            if childL3.tag == kw2:
                                text = childL3.get('name')
                                fName = text.strip()
                                text = childL3.text
                                probFrac = float(text.strip())
                                if not (fName in self._faciesInZone):
                                    raise ValueError(
                                        'Error when reading model file: ' + modelFileName + '\n'
                                        'Error: Read truncation rule: ' + self._className + '\n'
                                        'Error: Specified facies name in truncation rule: ' + fName +
                                        ' is not defined for this zone.'
                                    )
                                if not (0.0 <= probFrac <= 1.0):
                                    raise ValueError(
                                        'Error when reading model file: ' + modelFileName + '\n'
                                        'Error: Read truncation rule: ' + self._className + '\n'
                                        'Error: Specified probability fraction in truncation rule is outside [0,1]'
                                    )

                                nFacies, indx, fIndx, isNew = self._addFaciesToTruncRule(fName)
                                nPoly += 1

                                poly = []
                                # nodeData = ['F',indx,probFrac,prob,polygon,xmin,xmax,ymin,ymax]
                                nodeData = ['F', indx, probFrac, 0.0, poly, 0.0, 0.0, 0.0, 0.0]
                                nodeListLevel3.append(nodeData)
                                if isNew == 1:
                                    self._orderIndex.append(fIndx)

        # End loop over L1 children

        # Number of background facies in total
        self._nBackGroundFacies = self.num_facies_in_truncation_rule

        # Check that specified probability fractions for each facies when summing over all polygons
        # for a facies is 1.0
        # Note that overlay facies is not a part of this calculations.
        sumProbFrac = np.zeros(self._nBackGroundFacies, np.float32)
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

        # Check the sum over background facies for probfrac
        for i in range(self.num_facies_in_truncation_rule):
            fName = self._faciesInTruncRule[i]
            if self._debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: Sum prob frac for facies {0} is: {1}'.format(fName, str(sumProbFrac[i])))

            if abs(sumProbFrac[i] - 1.0) > 0.001:
                raise ValueError(
                    'Error in {0}\n'
                    'Error: Sum of probability fractions over all polygons for facies {1} is not 1.0\n'
                    'Error: The sum is: {2}'.format(self._className, fName, str(sumProbFrac[i]))
                )
        self.__truncStructure = truncStructure
        if self._debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: -- End read background model in ' + self._className + ' from model file')

    def writeContentsInDataStructure(self):
        # Write common contents from base class
        super().writeContentsInDataStructure()

        print('')
        print('************  Contents specific to the "Cubic algorithm" *****************')
        print('Truncation structure:')
        for i in range(len(self.__truncStructure)):
            item = self.__truncStructure[i]
            print(repr(item))
        print('Use level 2: ' + str(self.__useLevel2))
        print('Use level 3: ' + str(self.__useLevel3))
        print('Internal indices in data structure (node_index):')
        print(self.__node_index)
        print('Number of polygons: ' + str(self.__nPoly()))
        for i in range(len(self.__polygons)):
            poly = self.__polygons[i]
            print('Polygon number: ' + str(i))
            for j in range(len(poly)):
                print(repr(poly[j]))
        print('Facies index for polygons:')
        print(repr(self.__fIndxPerPolygon))

    def getClassName(self):
        return copy.copy(self._className)

    def useConstTruncModelParam(self):
        # This is a function returning True if there are no truncation model
        # parameter that is spatially dependent. In the truncation rule here
        # there are no model parameters for the truncation model (except facies probability)
        return True

    def setTruncRule(self, faciesProb, cellIndx=0):
        """
        Calculate how truncation map is to be divided into polygons or threshold values.
        This function must be called each time the facies probability changes, so it must
        be called for each grid cell in a 3D modelling grid if the facies probability varies.
        This function must have the same input variables and the same output variables for
        each truncation algorithm that is implemented.

        :param faciesProb: Probability for each facies.
        :param cellIndx: Is not used here , but may be used in other algorithms where there are
                         model parameters  that may vary from cell to cell in the 3D modelling grid.
        """

        # Call common functions from base class
        # Check if facies probability is close to 1.0. In this case do not calculate truncation map.
        # Take care of overprint facies to get correct probability (volume in truncation cube)
        self._setTruncRuleIsCalled = True
        if self._isFaciesProbEqualOne(faciesProb):
            return

        area = self._modifyBackgroundFaciesArea(faciesProb)

        # Call methods specific for this truncation rule with corrected area due to overprint facies
        self.__calcProbForEachNode(area)
        self.__calcThresholdValues()

        if self._debug_level >= Debug.VERY_VERY_VERBOSE:
            self.__writeDataForTruncRule()

    def __calcProbForEachNode(self, faciesProb):
        TYPE = self.__node_index['type']
        NLIST = self.__node_index['list of nodes']
        PROB = self.__node_index['probability']
        INDX = self.__node_index['index']
        PFRAC = self.__node_index['probability fraction']
        nodeListL1 = self.__truncStructure[NLIST]
        cumProbL1 = 0.0
        for i in range(len(nodeListL1)):
            itemL1 = nodeListL1[i]
            if itemL1[TYPE] == 'F':
                indx = itemL1[INDX]
                fIndx = self._orderIndex[indx]
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
                        fIndx = self._orderIndex[indx]
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
                            fIndx = self._orderIndex[indx]
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
                'Error: cumProbL1 = {1}'.format(self._className, str(cumProbL1))
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
        eps = self.getEpsFaciesProb()
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
        # Check if the facies is deterministic (100% probability)
        for fIndx in range(len(self._faciesInZone)):
            if self._faciesIsDetermined[fIndx] == 1:
                faciesCode = self._faciesCode[fIndx]
                return faciesCode, fIndx
        directionL1 = self.__truncStructure[self.__node_index['direction']]
        nodeListL1 = self.__truncStructure[self.__node_index['list of nodes']]
        if directionL1 == 'H':
            faciesCode, fIndx = self.__calcFaciesLevel1H(nodeListL1, alphaCoord)
        else:
            faciesCode, fIndx = self.__calcFaciesLevel1V(nodeListL1, alphaCoord)
        return faciesCode, fIndx

    def __calcFaciesLevel1V(self, nodeListL1, alphaCoord):
        faciesCode = -1
        fIndx = -1
        # Use the alphaIndxList to find the alphaCoordinates that corresponds to alpha1 and alpha2
        x = alphaCoord[self._alphaIndxList[0]]
        y = alphaCoord[self._alphaIndxList[1]]
        for i in range(len(nodeListL1)):
            itemL1 = nodeListL1[i]
            typeNode = itemL1[self.__node_index['type']]
            if typeNode == 'F':
                if x <= itemL1[self.__node_index['x max']]:
                    indx = itemL1[self.__node_index['index']]
                    # Check truncations for overlay facies (call function from base class)
                    faciesCode, fIndx = self._truncateOverlayFacies(indx, alphaCoord)
                    break
            else:
                if x <= itemL1[self.__node_index['x max']]:
                    directionL2 = itemL1[self.__node_index['direction']]
                    nodeListL2 = itemL1[self.__node_index['list of nodes']]
                    if directionL2 == 'H':
                        faciesCode, fIndx = self.__calcFaciesLevel2H(nodeListL2, alphaCoord)
                    else:
                        faciesCode, fIndx = self.__calcFaciesLevel2V(nodeListL2, alphaCoord)
                    break
        if faciesCode < 0 or fIndx < 0:
            raise ValueError('Programming error. Could not find facies when applying truncation rule')
        return faciesCode, fIndx

    def __calcFaciesLevel1H(self, nodeListL1, alphaCoord):
        faciesCode = -1
        fIndx = -1
        x = alphaCoord[self._alphaIndxList[0]]
        y = alphaCoord[self._alphaIndxList[1]]
        for i in range(len(nodeListL1)):
            itemL1 = nodeListL1[i]
            typeNode = itemL1[self.__node_index['type']]
            if typeNode == 'F':
                if y <= itemL1[self.__node_index['y max']]:
                    indx = itemL1[self.__node_index['index']]
                    faciesCode, fIndx = self._truncateOverlayFacies(indx, alphaCoord)
                    break
            else:
                if y <= itemL1[self.__node_index['y max']]:
                    directionL2 = itemL1[self.__node_index['direction']]
                    nodeListL2 = itemL1[self.__node_index['list of nodes']]
                    if directionL2 == 'H':
                        faciesCode, fIndx = self.__calcFaciesLevel2H(nodeListL2, alphaCoord)
                    else:
                        faciesCode, fIndx = self.__calcFaciesLevel2V(nodeListL2, alphaCoord)
                    break
        if faciesCode < 0 or fIndx < 0:
            raise ValueError('Programming error. Could not find facies when applying truncation rule')
        return faciesCode, fIndx

    def __calcFaciesLevel2H(self, nodeListL2, alphaCoord):
        faciesCode = -1
        fIndx = -1
        x = alphaCoord[self._alphaIndxList[0]]
        y = alphaCoord[self._alphaIndxList[1]]
        for j in range(len(nodeListL2)):
            itemL2 = nodeListL2[j]
            typeNode = itemL2[self.__node_index['type']]
            if typeNode == 'F':
                if y <= itemL2[self.__node_index['y max']]:
                    indx = itemL2[self.__node_index['index']]
                    faciesCode, fIndx = self._truncateOverlayFacies(indx, alphaCoord)
                    break
            else:
                if y <= itemL2[self.__node_index['y max']]:
                    directionL3 = itemL2[self.__node_index['direction']]
                    nodeListL3 = itemL2[self.__node_index['list of nodes']]
                    if directionL3 == 'H':
                        faciesCode, fIndx = self.__calcFaciesLevel3H(nodeListL3, alphaCoord)
                    else:
                        faciesCode, fIndx = self.__calcFaciesLevel3V(nodeListL3, alphaCoord)
                    break
        if faciesCode < 0 or fIndx < 0:
            raise ValueError('Programming error. Could not find facies when applying truncation rule')
        return faciesCode, fIndx

    def __calcFaciesLevel2V(self, nodeListL2, alphaCoord):
        faciesCode = -1
        fIndx = -1
        x = alphaCoord[self._alphaIndxList[0]]
        y = alphaCoord[self._alphaIndxList[1]]
        for j in range(len(nodeListL2)):
            itemL2 = nodeListL2[j]
            typeNode = itemL2[self.__node_index['type']]
            if typeNode == 'F':
                if x <= itemL2[self.__node_index['x max']]:
                    indx = itemL2[self.__node_index['index']]
                    faciesCode, fIndx = self._truncateOverlayFacies(indx, alphaCoord)
                    break
            else:
                if x <= itemL2[self.__node_index['x max']]:
                    directionL3 = itemL2[self.__node_index['direction']]
                    nodeListL3 = itemL2[self.__node_index['list of nodes']]
                    if directionL3 == 'H':
                        faciesCode, fIndx = self.__calcFaciesLevel3H(nodeListL3, alphaCoord)
                    else:
                        faciesCode, fIndx = self.__calcFaciesLevel3V(nodeListL3, alphaCoord)
                    break
        if faciesCode < 0 or fIndx < 0:
            raise ValueError('Programming error. Could not find facies when applying truncation rule')
        return faciesCode, fIndx

    def __calcFaciesLevel3H(self, nodeListL3, alphaCoord):
        faciesCode = -1
        fIndx = -1
        y = alphaCoord[self._alphaIndxList[1]]
        for k in range(len(nodeListL3)):
            itemL3 = nodeListL3[k]
            typeNode = itemL3[self.__node_index['type']]
            if typeNode != 'F':
                raise ValueError(
                    'Error in {}\n'
                    'Error: Programming error. Mismatch type. Expect F type.'
                    ''.format(self._className)
                )

            if y <= itemL3[self.__node_index['y max']]:
                indx = itemL3[self.__node_index['index']]
                faciesCode, fIndx = self._truncateOverlayFacies(indx, alphaCoord)
                break
        if faciesCode < 0 or fIndx < 0:
            raise ValueError('Programming error. Could not find facies when applying truncation rule')
        return faciesCode, fIndx

    def __calcFaciesLevel3V(self, nodeListL3, alphaCoord):
        faciesCode = -1
        fIndx = -1
        x = alphaCoord[self._alphaIndxList[0]]
        for k in range(len(nodeListL3)):
            itemL3 = nodeListL3[k]
            typeNode = itemL3[self.__node_index['type']]
            if typeNode != 'F':
                raise ValueError(
                    'Error in {}\n'
                    'Error: Programming error. Mismatch type. Expect F type.'
                    ''.format(self._className)
                )
            if x <= itemL3[self.__node_index['x max']]:
                indx = itemL3[self.__node_index['index']]
                faciesCode, fIndx = self._truncateOverlayFacies(indx, alphaCoord)
                break

        if faciesCode < 0 or fIndx < 0:
            raise ValueError('Programming error. Could not find facies when applying truncation rule')
        return faciesCode, fIndx

    def __calcPolyLevel(self, direction, nodeList, polyLevelAbove, levelNumber):
        TYPE = self.__node_index['type']
        DIR = self.__node_index['direction']
        NLIST = self.__node_index['list of nodes']
        POLY = self.__node_index['polygon']
        XMAX = self.__node_index['x max']
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

    def __writeDataForTruncRule(self):
        TYPE = self.__node_index['type']
        NLIST = self.__node_index['list of nodes']
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
                fName = self._faciesInTruncRule[indx]
                text = 'L1: {}  ProbFrac: {}  Prob: {}'.format(fName, probFrac, prob)
                text += ' X: [{}, {}] Y: [{}, {}]'.format(xmin, xmax, ymin, ymax)
                if self._debug_level >= Debug.VERBOSE:
                    print(text)

            else:
                nodeListL2 = itemL1[NLIST]
                if self._debug_level >= Debug.VERBOSE:
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
                        fName = self._faciesInTruncRule[indx]
                        if self._debug_level >= Debug.VERBOSE:
                            text = '  L2: {}  ProbFrac: {}  Prob: {}'.format(fName, probFrac, prob)
                            text += ' X: [{}, {}] Y: [{}, {}]'.format(xmin, xmax, ymin, ymax)
                            print(text)
                    else:
                        nodeListL3 = itemL2[NLIST]
                        if self._debug_level >= Debug.VERBOSE:
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
                            fName = self._faciesInTruncRule[indx]
                            if self._debug_level >= Debug.VERBOSE:
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

        self.__polygons = polygons
        self.__fIndxPerPolygon = fIndxList
        return self.__polygons

    def __nPoly(self) -> int:
        """
        Getter for the number of polygons in the truncation map
        :return: The number of polygons int the truncation map
        :rtype: int
        """
        return len(self.__polygons)

    def truncMapPolygons(self):
        assert self._setTruncRuleIsCalled is True
        DIR = self.__node_index['direction']
        NLIST = self.__node_index['list of nodes']
        POLY = self.__node_index['polygon']
        # Unit square (2D truncation map)
        poly = [
            [0.0, 0.0],
            [1.0, 0.0],
            [1.0, 1.0],
            [0.0, 1.0],
        ]

        self.__truncStructure[POLY] = poly
        directionL1 = self.__truncStructure[DIR]
        nodeListL1 = self.__truncStructure[NLIST]
        levelNumber = 1
        self.__calcPolyLevel(directionL1, nodeListL1, poly, levelNumber)

        # Create list of polygons and corresponding list of facies
        self.__getPolygonAndFaciesList()
        polygons = copy.deepcopy(self.__polygons)
        return polygons

    def faciesIndxPerPolygon(self):
        fIndxList = copy.copy(self.__fIndxPerPolygon)
        return fIndxList

    def initialize(self, mainFaciesTable, faciesInZone, gaussFieldsInZone, alphaFieldNameForBackGroundFacies,
                   truncStructureList, overlayGroups=None, debug_level=Debug.OFF):
        """
        TODO: Update documentation

           Description: Initialize the truncation object from input variables.
                        This function is used when the truncation object is not initialized
                        by reading the specification from the model file.
           Input: mainFaciesTable - Specify the global facies table and is used to check that specified facies
                                    is legal.
                  faciesInZone    - List of facies to be modelled for the zone this truncation rule is defined for.
                  gaussFieldsInZone - List of gauss fields defined for the zone.
                  alphaFieldName1, alphaFieldName2 - Name of the gauss fields corresponding to alpha1 and alpha2 that define
                                                     background facies truncation map.
                  truncStructureList - Contain definition of truncation rule. See details in specification
                                       described for function __setTruncStructure.
                  overlayGroups - List of overlay facies with associated alphaFields and probability fractions.
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

        # Set truncation rule (hierarchy of rectangular polygons)
        self.__setTruncStructure(truncStructureList)

        if self._debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: Background facies defined:')
            print(repr(self._faciesInTruncRule))

        # Call base class function to fill data structure with overlay facies
        self._setOverlayFaciesDataStructure(overlayGroups)

        self._checkFaciesForZone()

    def __setTruncStructure(self, truncStructureList):
        # Truncation structure specified by list of facies in hierarchical way with items of the form
        # [faciesName,level]
        # where level is one number for L1 ([1] or [2] ..), two number for L2 ([1,1] [1,2] ...)
        # or for L3 ([2,1,1],[2,1,2]...)
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
                        raise ValueError('Error: L1 == L1Prev and L2 == L2Prev and L3 - L3Prev > 1')
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
                    nFacies, indx, fIndx, isNew = self._addFaciesToTruncRule(fName)
                    nPoly += 1
                    poly = []
                    nodeData = ['F', indx, probFrac, 0.0, poly, 0.0, 0.0, 0.0, 0.0]
                    nodeListLevel1.append(nodeData)
                    if isNew == 1:
                        self._orderIndex.append(fIndx)
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
                        nFacies, indx, fIndx, isNew = self._addFaciesToTruncRule(fName)
                        nPoly += 1
                        poly = []
                        nodeData = ['F', indx, probFrac, 0.0, poly, 0.0, 0.0, 0.0, 0.0]
                        nodeListLevel2.append(nodeData)
                        if isNew == 1:
                            self._orderIndex.append(fIndx)
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
                        nFacies, indx, fIndx, isNew = self._addFaciesToTruncRule(fName)
                        nPoly += 1
                        poly = []
                        nodeData = ['F', indx, probFrac, 0.0, poly, 0.0, 0.0, 0.0, 0.0]
                        nodeListLevel3.append(nodeData)
                        if isNew == 1:
                            self._orderIndex.append(fIndx)

            elif L1 == L1Prev:
                if L2 > L2Prev:
                    self.__useLevel2 = 1
                    if L3 == 0:

                        # Create L2 facies node
                        nFacies, indx, fIndx, isNew = self._addFaciesToTruncRule(fName)
                        nPoly += 1
                        poly = []
                        nodeData = ['F', indx, probFrac, 0.0, poly, 0.0, 0.0, 0.0, 0.0]
                        nodeListLevel2.append(nodeData)
                        if isNew == 1:
                            self._orderIndex.append(fIndx)
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
                        nFacies, indx, fIndx, isNew = self._addFaciesToTruncRule(fName)
                        nPoly += 1
                        poly = []
                        nodeData = ['F', indx, probFrac, 0.0, poly, 0.0, 0.0, 0.0, 0.0]
                        nodeListLevel3.append(nodeData)
                        if isNew == 1:
                            self._orderIndex.append(fIndx)
                    else:
                        raise ValueError('Error: L3 cannot be > 1 when L2 has increased')

                elif L2 == L2Prev:
                    self.__useLevel2 = 1
                    if L3 > L3Prev:
                        # Create L3 facies node
                        self.__useLevel3 = 1
                        nFacies, indx, fIndx, isNew = self._addFaciesToTruncRule(fName)
                        nPoly += 1
                        poly = []
                        nodeData = ['F', indx, probFrac, 0.0, poly, 0.0, 0.0, 0.0, 0.0]
                        nodeListLevel3.append(nodeData)
                        if isNew == 1:
                            self._orderIndex.append(fIndx)
                    else:
                        raise ValueError('Error: L3 must be 1 larger than L3Prev when L1 == L1Prev and L2 == L2Prev')

            L1Prev = L1
            L2Prev = L2
            L3Prev = L3
        self.__truncStructure = truncStructure

    def XMLAddElement(self, parent, zone_number, region_number, fmu_attributes):
        if self._debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: call XMLADDElement from ' + self._className)
        TYPE = self.__node_index['type']
        DIR = self.__node_index['direction']
        NLIST = self.__node_index['list of nodes']
        PFRAC = self.__node_index['probability fraction']
        INDX = self.__node_index['index']

        # Add to the parent element a new element with specified tag and attributes.
        # The attributes are a dictionary with {name:value}
        # After this function is called, the parent element has got a new child element
        # for the current class.
        nGF = self.getNGaussFieldsInModel()

        trRuleElement = Element('TruncationRule')
        parent.append(trRuleElement)

        attribute = {
            'nGFields': str(nGF)}
        trRuleTypeElement = Element('Trunc2D_Cubic', attribute)
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
        alphaFieldsElement.text = ' ' + gfName1 + ' ' + gfName2 + ' '
        bgModelElement.append(alphaFieldsElement)

        directionL1 = self.__truncStructure[DIR]
        nodeListL1 = self.__truncStructure[NLIST]
        tag = 'L1'
        attribute = {'direction': directionL1}
        nodeElementL1 = Element(tag, attribute)
        bgModelElement.append(nodeElementL1)
        for i in range(len(nodeListL1)):
            itemL1 = nodeListL1[i]
            typeNode = itemL1[TYPE]
            if typeNode == 'F':
                indx = itemL1[INDX]
                fName = self._faciesInTruncRule[indx]
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
                        fName = self._faciesInTruncRule[indx]
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
                            fName = self._faciesInTruncRule[indx]
                            probFrac = itemL3[PFRAC]
                            tag = 'ProbFrac'
                            attribute = {'name': fName}
                            nodeElementL3Below = Element(tag, attribute)
                            nodeElementL3Below.text = ' ' + str(probFrac) + ' '
                            nodeElementL3.append(nodeElementL3Below)

        super()._XMLAddElement(trRuleTypeElement)
