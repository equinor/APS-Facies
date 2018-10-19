# -*- coding: utf-8 -*-
from src.algorithms.APSMainFaciesTable import APSMainFaciesTable
from src.utils.constants.simple import Debug
from typing import List, Optional, Union, Tuple, NewType
from xml.etree.ElementTree import Element

from src.utils.records import FaciesProbabilityRecord
from src.utils.roxar.rms_project_data import ZoneNumber

FaciesName = NewType('FaciesName', str)
Probability = Union[float, str]

Index = NewType('Index', int)
ErrorCode = NewType('ErrorCode', int)

class FaciesProbability:
    name:                       str
    probability:                Probability
    def __init__(
            self,
            name: str,
            probability
    ): ...
    @classmethod
    def from_definition(
            cls,
            definition: Union[
                FaciesProbabilityRecord,
                Tuple[str, Probability],
                List[Probability]
            ]
    ) -> FaciesProbability: ...


class APSFaciesProb:
    zone_number:                int
    facies_in_zone_model:       List[FaciesName]

    __class_name:               str
    __useConstProb:             bool
    __mainFaciesTable:          APSMainFaciesTable
    __faciesProbForZoneModel:   List[FaciesProbability]
    def __init__(
        self,
        ET_Tree_zone:           Optional[Element]               = None,
        mainFaciesTable:        Optional[APSMainFaciesTable]    = None,
        modelFileName:          Optional[str]                   = None,
        debug_level:            int                             = Debug.OFF,
        useConstProb:           bool                            = False,
        zoneNumber:             int                             = 0
    ) -> None: ...
    def __interpretXMLTree(
            self,
            ET_Tree_zone,
            modelFileName
    ): ...
    def XMLAddElement(
            self,
            parent: Element
    ) -> None: ...
    def findFaciesItem(
            self,
            facies_name:        FaciesName
    ) -> Optional[FaciesProbability]: ...
    def initialize(
        self,
        faciesList:             List[str],
        faciesProbList:         Union[List[str], List[float]],
        mainFaciesTable:        APSMainFaciesTable,
        useConstProb:           int,
        zoneNumber:             int,
        debug_level:            Debug                           = Debug.OFF
    ) -> None: ...
    def __roundOffProb(
            self,
            resolutionRoundOff: int = 100
    ) -> None: ...
    def __checkConstProbValuesAndNormalize(
            self,
            zoneNumber:         ZoneNumber
    ) -> None: ...
    def getAllProbParamForZone(self) -> List[str]: ...
    def getConstProbValue(
            self,
            facies_name:        FaciesName
    ) -> float: ...
    def updateFaciesWithProbForZone(
            self,
            faciesList:         List[str],
            faciesProbList:     Union[List[str], List[float]]
    ) -> ErrorCode: ...
    def updateSingleFaciesWithProbForZone(
            self,
            faciesName:         FaciesName,
            faciesProbCubeName: str
    ) -> ErrorCode: ...
    def removeFaciesWithProbForZone(
            self,
            fName:              FaciesName
    ) -> Index: ...
    def hasFacies(
            self,
            facies_name:        FaciesName
    ) -> bool: ...
    def getProbParamName(
            self,
            fName:              FaciesName
    ) -> Optional[str]: ...
