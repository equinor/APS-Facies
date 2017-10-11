#!/bin/env python
from xml.etree.ElementTree import Element

import copy

from src.utils.constants import Debug
from src.utils.methods import isNumber
from src.xmlFunctions import getKeyword, getTextCommand


class APSFaciesProb:
    """
    class APSFaciesProb

    Description:
    This class keep a list of facies names and associated facies probabilities for a zone.
    The facies probabilities can be specified either as float numbers or as RMS parameter
    names of facies probability cubes. The class contain functions to get the facies list
    and facies probabilities from an XML tree containing the model file.
    Alternatively an empty object can be created and an initialization function can be
    used to assign facies list and facies probabilities to the class.

    Constructor:
        def __init__(self, ET_Tree_zone=None, mainFaciesTable= None,modelFileName=None,
                     debug_level=Debug.OFF,useConstProb=0,zoneNumber=0)
    Public functions:
        def getAllProbParamForZone(self)
        def getConstProbValue(self,fName)
        def getFaciesInZoneModel(self)
        def updateFaciesWithProbForZone(self,faciesList,faciesProbList)
        def removeFaciesWithProbForZone(self,fName)
        def hasFacies(self,fName)
        def getProbParamName(self,fName)
        def XMLAddElement(self,parent)


    Private functions:
        def __setEmpty(self)
        def __interpretXMLTree(self,ET_Tree_zone,modelFileName)
        def __checkConstProbValuesAndNormalize(self,zoneNumber)

    """

    def __setEmpty(self):
        self.__className = 'APSFaciesProb'
        self.__faciesProbForZoneModel = []
        self.__faciesInZoneModel = []
        self.__useConstProb = 0
        self.__debug_level = 0
        self.__mainFaciesTable = None
        self.__zoneNumber = 0

        self.__FNAME = 0
        self.__FPROB = 1

    def __init__(self, ET_Tree_zone=None, mainFaciesTable=None, modelFileName=None,
                 debug_level=Debug.OFF, useConstProb=0, zoneNumber=0):

        self.__setEmpty()

        if ET_Tree_zone is not None:
            self.__useConstProb = useConstProb
            self.__debug_level = debug_level
            self.__mainFaciesTable = mainFaciesTable
            self.__zoneNumber = zoneNumber

            # Get data from xml tree
            if self.__debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: Call init ' + self.__className + ' and read from xml file')
            self.__interpretXMLTree(ET_Tree_zone, modelFileName)

            # End __init__

    def __interpretXMLTree(self, ET_Tree_zone, modelFileName):
        assert self.__mainFaciesTable is not None
        assert modelFileName is not None
        assert ET_Tree_zone is not None

        self.__faciesProbForZoneModel = []
        self.__faciesInZoneModel = []

        # Read Facies probability cubes for current zone model
        kw = 'FaciesProbForModel'
        obj = getKeyword(ET_Tree_zone, kw, 'Zone', modelFile=modelFileName)

        facForModel = obj

        for f in facForModel.findall('Facies'):
            text = f.get('name')
            name = text.strip()
            if self.__mainFaciesTable.checkWithFaciesTable(name):
                text = getTextCommand(f, 'ProbCube', 'Facies', modelFile=modelFileName)
                probCubeName = text.strip()
                if self.__useConstProb == 1:
                    if not isNumber(probCubeName):
                        raise ValueError(
                            'Error when reading model file: {0}\n'
                            'Error in {1}\n'
                            'Error in keyword: FaciesProbForModel for facies name: {2} in zone number: {3}\n'
                            '                  The specified probability is not a number even though '
                            'useConstProb keyword is set to 1.'
                            ''.format(modelFileName, self.__className, name, str(self.__zoneNumber))
                        )
                else:
                    if isNumber(probCubeName):
                        raise ValueError(
                            'Error when reading model file: {0}\n'
                            'Error in {1}\n'
                            'Error in keyword: FaciesProbForModel for facies name: {2} in zone number: {3}\n'
                            '                  The specified probability is not an RMS parameter name even though '
                            'useConstProb keyword is set to 0.'
                            ''.format(modelFileName, self.__className, name, str(self.__zoneNumber))
                        )

                item = [name, probCubeName]
                self.__faciesProbForZoneModel.append(item)
                self.__faciesInZoneModel.append(name)
            else:
                raise NameError(
                    'Error when reading model file: {0}\n'
                    'Error in {1}\n'
                    'Error in keyword: FaciesProbForModel in zone number: {2}. Facies name: {3}\n'
                    '                  is not defined in main facies table in command APSMainFaciesTable'
                    ''.format(modelFileName, self.__className, str(self.__zoneNumber), name)
                )

        if self.__faciesProbForZoneModel is None:
            raise NameError(
                'Error when reading model file: {0}\n'
                'Error: Missing keyword Facies under keyword FaciesProbForModel'
                ' in zone number: {1}\n'
                ''.format(modelFileName, self.__zoneNumber)
            )

        self.__checkConstProbValuesAndNormalize(self.__zoneNumber)

        if self.__debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: From ' + self.__className + ': Facies prob for current zone model: ')
            print(repr(self.__faciesProbForZoneModel))

    def initialize(self, faciesList, faciesProbList, mainFaciesTable, useConstProb, zoneNumber, debug_level=Debug.OFF):
        if debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: Call the initialize function in ' + self.__className)

        self.__setEmpty()
        self.__useConstProb = useConstProb
        self.__zoneNumber = zoneNumber
        self.__debug_level = debug_level
        self.__mainFaciesTable = mainFaciesTable
        self.updateFaciesWithProbForZone(faciesList, faciesProbList)

    def __checkConstProbValuesAndNormalize(self, zoneNumber):
        if self.__useConstProb == 1:
            sumProb = 0.0
            for i in range(len(self.__faciesProbForZoneModel)):
                item = self.__faciesProbForZoneModel[i]
                prob = float(item[self.__FPROB])
                sumProb += prob
            if abs(sumProb - 1.0) > 0.001:
                print('Warning in ' + self.__className)
                text = 'Warning: Specified constant probabilities sum up to: ' + str(sumProb)
                text = text + ' and not 1.0 in zone ' + str(zoneNumber)
                print(text)
                print('Warning: The specified probabilities will be normalized.')
                for i in range(len(self.__faciesProbForZoneModel)):
                    item = self.__faciesProbForZoneModel[i]
                    prob = float(item[self.__FPROB])
                    normalizedProb = prob / sumProb
                    item[self.__FPROB] = str(normalizedProb)

    def getAllProbParamForZone(self):
        found = 0
        allProbParamList = []
        for item in self.__faciesProbForZoneModel:
            probParamName = item[self.__FPROB]
            if self.__useConstProb == 0:
                if not probParamName in allProbParamList:
                    allProbParamList.append(probParamName)
        return allProbParamList

    def getConstProbValue(self, fName):
        if self.__useConstProb == 1:
            found = 0
            for item in self.__faciesProbForZoneModel:
                fN = item[self.__FNAME]
                if fN == fName:
                    probCubeName = item[self.__FPROB]
                    found = 1
                    break
            if found == 0:
                print('Error: Probability not found for facies: ' + fName)
                return -999
            else:
                return float(probCubeName)
        else:
            print('Error: Can not call getConstProbValue when useConstProb = 0')
            return -999

    def getFaciesInZoneModel(self):
        return copy.copy(self.__faciesInZoneModel)

    def findFaciesItem(self, faciesName):
        # Check that facies is defined
        itemWithFacies = None
        if self.__mainFaciesTable.checkWithFaciesTable(faciesName):
            for item in self.__faciesProbForZoneModel:
                name = item[self.__FNAME]
                if name == faciesName:
                    itemWithFacies = item
                    break
        return itemWithFacies

    def updateFaciesWithProbForZone(self, faciesList, faciesProbList):
        err = 0
        # Check that facies is defined
        for fName in faciesList:
            if not self.__mainFaciesTable.checkWithFaciesTable(fName):
                err = 1
                break
        if len(faciesList) != len(faciesProbList):
            err = 1

        for i in range(len(faciesList)):
            fName = faciesList[i]
            fProbName = faciesProbList[i]
            item = self.findFaciesItem(fName)
            if item is None:
                # insert new facies
                item = [fName, fProbName]
                self.__faciesProbForZoneModel.append(item)
                self.__faciesInZoneModel.append(fName)
            else:
                # Update facies probability cube name
                item[self.__FPROB] = fProbName
        return err

    def updateSingleFaciesWithProbForZone(self, faciesName, faciesProbCubeName):
        # Check that facies is defined
        if not self.__mainFaciesTable.checkWithFaciesTable(faciesName):
            err = 1
        else:
            err = 0
            itemWithFacies = self.findFaciesItem(faciesName)
            if itemWithFacies is None:
                # insert new facies
                itemWithFacies = [faciesName, faciesProbCubeName]
                self.__faciesProbForZoneModel.append(itemWithFacies)
                self.__faciesInZoneModel.append(faciesName)
            else:
                # Update facies probability cube name
                itemWithFacies[self.__FPROB] = faciesProbCubeName
        return err

    def removeFaciesWithProbForZone(self, fName):
        indx = -999
        for i in range(len(self.__faciesProbForZoneModel)):
            item = self.__faciesProbForZoneModel[i]
            name = item[self.__FNAME]
            if fName == name:
                indx = i
                break
        if indx != -999:
            # Remove data for this facies
            self.__faciesProbForZoneModel.pop(indx)
            self.__faciesInZoneModel.pop(indx)
        return

    def hasFacies(self, fName):
        n = len(self.__faciesProbForZoneModel)
        found = 0
        for i in range(n):
            item = self.__faciesProbForZoneModel[i]
            faciesName = item[self.__FNAME]
            if fName == faciesName:
                found = 1
                break
        if found == 0:
            return False
        else:
            return True

    def getProbParamName(self, fName):
        found = 0
        for item in self.__faciesProbForZoneModel:
            fN = item[self.__FNAME]
            if fN == fName:
                probCubeName = item[self.__FPROB]
                found = 1
                break
        if found == 0:
            return None
        else:
            return copy.copy(probCubeName)

    def XMLAddElement(self, parent):
        if self.__debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: call XMLADDElement from ' + self.__className)

        # Add command FaciesProbForModel
        tag = 'FaciesProbForModel'
        elem = Element(tag)
        parent.append(elem)
        fProbElement = elem
        for i in range(len(self.__faciesProbForZoneModel)):
            fName = self.__faciesProbForZoneModel[i][self.__FNAME]
            fProb = self.__faciesProbForZoneModel[i][self.__FPROB]
            tag = 'Facies'
            attribute = {'name': fName}
            fElement = Element(tag, attribute)
            fProbElement.append(fElement)
            tag = 'ProbCube'
            pElement = Element(tag)
            pElement.text = ' ' + str(fProb) + ' '
            fElement.append(pElement)
