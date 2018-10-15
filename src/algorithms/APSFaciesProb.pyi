# -*- coding: utf-8 -*-
from src.algorithms.APSMainFaciesTable import APSMainFaciesTable
from src.utils.constants.simple import Debug
from typing import List, Optional, Union, Tuple
from xml.etree.ElementTree import Element

from src.utils.records import FaciesProbabilityRecord

FaciesName = str

class FaciesProbability:
    name: str
    probability: Union[int, str]
    def __init__(self, name: str, probability): ...
    @classmethod
    def from_definition(
            cls,
            definition: Union[
                FaciesProbabilityRecord,
                Tuple[str, Union[str, float]],
                List[Union[str, float]]
            ]
    ) -> FaciesProbability: ...


class APSFaciesProb:
    zone_number: int
    facies_in_zone_model: List[FaciesName]

    __class_name: str
    __useConstProb: bool
    __mainFaciesTable: APSMainFaciesTable
    __faciesProbForZoneModel: List[FaciesProbability]
    def __init__(
        self,
        ET_Tree_zone: Optional[Element] = None,
        mainFaciesTable: Optional[APSMainFaciesTable] = None,
        modelFileName: Optional[str] = None,
        debug_level: int = Debug.OFF,
        useConstProb: bool = False,
        zoneNumber: int = 0
    ) -> None: ...
    def __interpretXMLTree(self, ET_Tree_zone, modelFileName): ...
    def XMLAddElement(self, parent: Element) -> None: ...
    def findFaciesItem(self, facies_name: FaciesName) -> Optional[FaciesProbability]: ...
    def initialize(
        self,
        faciesList:         List[str],
        faciesProbList:     Union[List[str], List[float]],
        mainFaciesTable:    APSMainFaciesTable,
        useConstProb:       int,
        zoneNumber:         int,
        debug_level:        Debug                           = Debug.OFF
    ) -> None: ...
    def updateFaciesWithProbForZone(self, faciesList: List[str], faciesProbList: Union[List[str], List[float]]) -> int: ...
