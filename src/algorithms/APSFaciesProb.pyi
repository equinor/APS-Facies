# -*- coding: utf-8 -*-
from src.algorithms.APSMainFaciesTable import APSMainFaciesTable
from src.utils.constants.simple import Debug
from typing import List, Optional, Union
from xml.etree.ElementTree import Element


class APSFaciesProb:
    zone_number: int
    def __init__(
        self,
        ET_Tree_zone: Optional[Element] = None,
        mainFaciesTable: Optional[APSMainFaciesTable] = None,
        modelFileName: Optional[str] = None,
        debug_level: int = Debug.OFF,
        useConstProb: bool = False,
        zoneNumber: int = 0
    ) -> None: ...
    def XMLAddElement(self, parent: Element) -> None: ...
    def findFaciesItem(self, faciesName: str) -> None: ...
    def getFaciesInZoneModel(self) -> List[str]: ...
    def initialize(
        self,
        faciesList: List[str],
        faciesProbList: Union[List[str], List[float]],
        mainFaciesTable: APSMainFaciesTable,
        useConstProb: int,
        zoneNumber: int,
        debug_level: Debug = Debug.OFF
    ) -> None: ...
    def updateFaciesWithProbForZone(self, faciesList: List[str], faciesProbList: Union[List[str], List[float]]) -> int: ...
