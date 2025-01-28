# -*- coding: utf-8 -*-
from warnings import warn

from typing import List, Optional, Union, Tuple
from xml.etree.ElementTree import Element

from aps.algorithms.APSMainFaciesTable import APSMainFaciesTable
from aps.utils.constants.simple import Debug
from aps.utils.numeric import isNumber
from aps.utils.types import Probability, FaciesName, ErrorCode, Index, ZoneNumber
from aps.utils.xmlUtils import getKeyword, getTextCommand
from aps.utils.records import FaciesProbabilityRecord


class FaciesProbability:
    __slots__ = '_name', '_probability'

    def __init__(self, name: FaciesName, probability: Probability):
        self._name = name
        self._probability = probability

    def __repr__(self):
        return '{}("{}", {})'.format(
            self.__class__.__name__, self.name, self.probability
        )

    @property
    def name(self) -> FaciesName:
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def probability(self) -> Probability:
        probability = self._probability
        try:
            return float(probability)
        except ValueError:
            return probability

    @probability.setter
    def probability(self, value):
        self._probability = value

    def __getitem__(self, item):
        if item == 0:
            return self.name
        elif item == 1:
            return self.probability
        else:
            raise IndexError('list index out of range')

    @classmethod
    def from_definition(
        cls,
        definition: Union[
            FaciesProbabilityRecord, Tuple[str, Probability], List[Probability]
        ],
    ) -> 'FaciesProbability':
        definition = FaciesProbabilityRecord._make(definition)
        return cls(
            name=definition.Name,
            probability=definition.Probability,
        )


class APSFaciesProb:
    """
    This class keep a list of facies names and associated facies probabilities for a zone.
    The facies probabilities can be specified either as float numbers or as RMS parameter
    names of facies probability cubes. The class contain functions to get the facies list
    and facies probabilities from an XML tree containing the model file.
    Alternatively an empty object can be created and an initialization function can be
    used to assign facies list and facies probabilities to the class.

    Constructor:
        def __init__(self, ET_Tree_zone=None, mainFaciesTable= None,modelFileName=None,
                     debug_level=Debug.OFF,useConstProb=False, zoneNumber=0)
    Public functions:
        def initialize(self, faciesList, faciesProbList, mainFaciesTable, useConstProb, zoneNumber, debug_level=Debug.OFF)
        def getAllProbParamForZone(self)
        def getConstProbValue(self,fName)
        def findFaciesItem(self, faciesName)
        def updateFaciesWithProbForZone(self,faciesList,faciesProbList)
        def updateSingleFaciesWithProbForZone(self, faciesName, faciesProbCubeName)
        def removeFaciesWithProbForZone(self,fName)
        def hasFacies(self,fName)
        def getProbParamName(self,fName)
        def XMLAddElement(self,parent)


    Private functions:
        def __interpretXMLTree(self,ET_Tree_zone,modelFileName)
        def __checkConstProbValuesAndNormalize(self,zoneNumber)
        def __roundOffProb(self, resolutionRoundOff=100)
    """

    def __init__(
        self,
        ET_Tree_zone: Optional[Element] = None,
        mainFaciesTable: Optional[APSMainFaciesTable] = None,
        modelFileName: Optional[str] = None,
        debug_level: int = Debug.OFF,
        useConstProb: bool = False,
        zoneNumber: int = 0,
    ):
        self.__class_name: str = self.__class__.__name__
        self.__faciesProbForZoneModel: List[FaciesProbability] = []
        self.__useConstProb: bool = 0
        self.__debug_level = Debug.OFF
        self.__mainFaciesTable: APSMainFaciesTable = None
        self.__zoneNumber = 0

        if ET_Tree_zone is not None:
            self.__useConstProb = useConstProb
            self.__debug_level = debug_level
            self.__mainFaciesTable = mainFaciesTable
            self.__zoneNumber = zoneNumber

            # Get data from xml tree
            if self.__debug_level >= Debug.VERY_VERBOSE:
                print(f'--- Call init {self.__class_name} and read from xml file')
            self.__interpretXMLTree(ET_Tree_zone, modelFileName)

            # End __init__

    @property
    def facies_in_zone_model(self) -> List[FaciesName]:
        return [facies.name for facies in self.__faciesProbForZoneModel]

    def __interpretXMLTree(self, ET_Tree_zone, modelFileName):
        assert self.__mainFaciesTable is not None
        assert ET_Tree_zone is not None

        self.__faciesProbForZoneModel = []

        # Read Facies probability cubes for current zone model
        kw = 'FaciesProbForModel'
        obj = getKeyword(ET_Tree_zone, kw, 'Zone', modelFile=modelFileName)

        facForModel = obj

        for f in facForModel.findall('Facies'):
            text = f.get('name')
            name = text.strip()
            if self.__mainFaciesTable.has_facies_int_facies_table(name):
                text = getTextCommand(f, 'ProbCube', 'Facies', modelFile=modelFileName)
                prob_cube_name = text.strip()
                if self.__useConstProb:
                    if not isNumber(prob_cube_name):
                        raise ValueError(
                            'Error when reading model file: {0}\n'
                            'Error in {1}\n'
                            'Error in keyword: FaciesProbForModel for facies name: {2} in zone number: {3}\n'
                            '                  The specified probability is not a number even though '
                            'useConstProb keyword is set to True.'
                            ''.format(
                                modelFileName, self.__class_name, name, self.zone_number
                            )
                        )
                else:
                    if isNumber(prob_cube_name):
                        raise ValueError(
                            'Error when reading model file: {0}\n'
                            'Error in {1}\n'
                            'Error in keyword: FaciesProbForModel for facies name: {2} in zone number: {3}\n'
                            '                  The specified probability is not an RMS parameter name even though '
                            'useConstProb keyword is set to False.'
                            ''.format(
                                modelFileName, self.__class_name, name, self.zone_number
                            )
                        )

                item = FaciesProbability(name, prob_cube_name)
                self.__faciesProbForZoneModel.append(item)
            else:
                raise NameError(
                    'Error when reading model file: {0}\n'
                    'Error in {1}\n'
                    'Error in keyword: FaciesProbForModel in zone number: {2}. Facies name: {3}\n'
                    '                  is not defined in main facies table in command APSMainFaciesTable'
                    ''.format(modelFileName, self.__class_name, self.zone_number, name)
                )

        if self.__faciesProbForZoneModel is None:
            raise NameError(
                'Error when reading model file: {0}\n'
                'Error: Missing keyword Facies under keyword FaciesProbForModel'
                ' in zone number: {1}\n'
                ''.format(modelFileName, self.zone_number)
            )

        self.__checkConstProbValuesAndNormalize(self.zone_number)

        if self.__debug_level >= Debug.VERY_VERBOSE:
            print(f'--- From {self.__class_name} Facies prob for current zone model:')
            print(repr(self.__faciesProbForZoneModel))

    def initialize(
        self,
        faciesList: List[str],
        faciesProbList: Union[List[str], List[float]],
        mainFaciesTable: APSMainFaciesTable,
        useConstProb: int,
        zoneNumber: int,
        debug_level: Debug = Debug.OFF,
    ) -> None:
        """Initialize an APSFaciesProb object."""
        if debug_level >= Debug.VERY_VERBOSE:
            print(f'--- Call the initialize function in {self.__class_name}')

        self.__useConstProb = useConstProb
        self.__zoneNumber = zoneNumber
        self.__debug_level = debug_level
        self.__mainFaciesTable = mainFaciesTable
        self.updateFaciesWithProbForZone(faciesList, faciesProbList)

    def __roundOffProb(self, resolutionRoundOff: int = 100) -> None:
        """Round off the probability value to nearest value which is a multiple of resolutionRoundOff
        if it is specified as a constant value"""
        if self.__useConstProb:
            for item in self.__faciesProbForZoneModel:
                prob = float(item.probability)
                probNew = int(prob * resolutionRoundOff + 0.5) / resolutionRoundOff
                item.probability = probNew

    def __checkConstProbValuesAndNormalize(self, zoneNumber: ZoneNumber) -> None:
        """Normalize probabilities for the case that constant probabilities is specified."""
        if not self.__useConstProb:
            return
        sumProb = 0.0
        for item in self.__faciesProbForZoneModel:
            prob = item.probability
            sumProb += prob
        if abs(sumProb - 1.0) > 0.001:
            warn(
                f'Specified constant probabilities sum up to: {sumProb} and not 1.0 in zone {zoneNumber}'
            )
            warn('The specified probabilities will be normalized.')
            for item in self.__faciesProbForZoneModel:
                prob = item.probability
                normalized_prob = prob / sumProb
                item.probability = str(normalized_prob)

    def getAllProbParamForZone(self) -> List[str]:
        """Return list of name of all specified RMS probability parameter names"""
        allProbParamList = []
        for item in self.__faciesProbForZoneModel:
            if not self.__useConstProb:
                probParamName = item.probability
                if probParamName not in allProbParamList:
                    allProbParamList.append(probParamName)
        return allProbParamList

    def getConstProbValue(self, facies_name: FaciesName) -> float:
        """Return probability (a number) for specified facies name. This is done when the specified probabilities
        are constants (numbers)"""
        if self.__useConstProb:
            for item in self.__faciesProbForZoneModel:
                fN = item.name
                if fN == facies_name:
                    return float(item.probability)
            raise ValueError(f'Probability for facies {facies_name} is not found')
        raise ValueError('Can not call getConstProbValue when useConstProb = 0')

    @property
    def zone_number(self) -> int:
        return self.__zoneNumber

    def findFaciesItem(self, facies_name: FaciesName) -> Optional[FaciesProbability]:
        # Check that facies is defined
        itemWithFacies = None
        if self.__mainFaciesTable.has_facies_int_facies_table(facies_name):
            for item in self.__faciesProbForZoneModel:
                name = item.name
                if name == facies_name:
                    itemWithFacies = item
                    break
        return itemWithFacies

    def updateFaciesWithProbForZone(
        self,
        faciesList: List[str],
        faciesProbList: Union[List[str], List[float]],
    ) -> ErrorCode:
        """Update existing facies with new facies probability/probability parameter name.
        For new facies, add facies and corresponding probability/probability parameter name"""
        err = 0
        # Check that facies is defined
        for fName in faciesList:
            if not self.__mainFaciesTable.has_facies_int_facies_table(fName):
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
                self.__faciesProbForZoneModel.append(
                    FaciesProbability(fName, fProbName)
                )
            else:
                # Update facies probability cube name
                item.probability = fProbName
        return err

    def updateSingleFaciesWithProbForZone(
        self, faciesName: FaciesName, faciesProbCubeName: str
    ) -> ErrorCode:
        """Update specified facies with new facies probability parameter name.
        If the facies does not exist, add it"""
        # Check that facies is defined
        if not self.__mainFaciesTable.has_facies_int_facies_table(faciesName):
            err = 1
        else:
            err = 0
            itemWithFacies = self.findFaciesItem(faciesName)
            if itemWithFacies is None:
                # insert new facies
                self.__faciesProbForZoneModel.append(
                    FaciesProbability(faciesName, faciesProbCubeName)
                )
            else:
                # Update facies probability cube name
                itemWithFacies.probability = faciesProbCubeName
        return err

    def removeFaciesWithProbForZone(self, fName: FaciesName) -> Index:
        """Remove a specified facies and its probability"""
        indx = -999
        for i in range(len(self.__faciesProbForZoneModel)):
            item = self.__faciesProbForZoneModel[i]
            name = item.name
            if fName == name:
                indx = i
                break
        if indx != -999:
            # Remove data for this facies
            self.__faciesProbForZoneModel.pop(indx)

    def hasFacies(self, facies_name: FaciesName) -> bool:
        """Check that facies with specified name exist"""
        for item in self.__faciesProbForZoneModel:
            _facies_name = item.name
            if facies_name == _facies_name:
                return True
        return False

    def getProbParamName(self, fName: FaciesName) -> Optional[str]:
        """Get probability parameter name for given facies name"""
        for item in self.__faciesProbForZoneModel:
            if item.name == fName:
                return item.probability
        return None

    def XMLAddElement(self, parent: Element) -> None:
        if self.__debug_level >= Debug.VERY_VERBOSE:
            print(f'--- call XMLADDElement from {self.__class_name}')

        # Add command FaciesProbForModel
        facies_probability = Element('FaciesProbForModel')
        parent.append(facies_probability)
        for item in self.__faciesProbForZoneModel:
            facies = Element('Facies', {'name': item.name})
            facies_probability.append(facies)
            probability = Element('ProbCube')
            probability.text = ' ' + str(item.probability) + ' '
            facies.append(probability)
