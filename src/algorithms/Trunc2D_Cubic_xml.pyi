from numpy import float64, ndarray
from src.algorithms.APSMainFaciesTable import APSMainFaciesTable
from src.utils.constants.simple import Debug
from typing import List, Optional, Tuple, Union
from xml.etree.ElementTree import Element


class Trunc2D_Cubic:
    def __init__(
        self,
        trRuleXML: Optional[Element] = None,
        mainFaciesTable: Optional[APSMainFaciesTable] = None,
        faciesInZone: Optional[List[str]] = None,
        gaussFieldsInZone: Optional[List[str]] = None,
        keyResolution: int = 100,
        debug_level: int = Debug.OFF,
        modelFileName: Optional[str] = None,
        zoneNumber: Optional[int] = None
    ) -> None: ...
    def XMLAddElement(self, parent: Element) -> None: ...
    def defineFaciesByTruncRule(self, alphaCoord: ndarray) -> Tuple[int, int]: ...
    def getClassName(self) -> str: ...
    def initialize(
        self,
        mainFaciesTable: APSMainFaciesTable,
        faciesInZone: List[str],
        gaussFieldsInZone: List[str],
        alphaFieldNameForBackGroundFacies: List[str],
        truncStructureList: List[Union[str, List[Union[str, float, int]]]],
        overlayGroups: Optional[List[List[Union[List[List[Union[str, float]]], List[str]]]]] = None,
        debug_level: Debug = Debug.OFF
    ) -> None: ...
    def setTruncRule(self, faciesProb: List[float], cellIndx: int = 0) -> None: ...
    def truncMapPolygons(
        self
    ) -> Union[List[List[List[float]]], List[Union[List[List[float]], List[Union[List[float], List[float64]]], List[List[float64]]]], List[Union[List[Union[List[float], List[float64]]], List[List[float]]]]]: ...