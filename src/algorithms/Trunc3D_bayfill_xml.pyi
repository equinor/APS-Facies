# -*- coding: utf-8 -*-
from numpy import ndarray
from src.algorithms.APSMainFaciesTable import APSMainFaciesTable
from src.utils.constants.simple import Debug
from typing import List, Optional, Tuple, Union
from xml.etree.ElementTree import Element


class Trunc3D_bayfill:
    def __init__(
        self,
        trRuleXML: Optional[Element] = None,
        mainFaciesTable: Optional[APSMainFaciesTable] = None,
        faciesInZone: Optional[List[str]] = None,
        gaussFieldsInZone: Optional[List[str]] = None,
        debug_level: int = Debug.OFF,
        modelFileName: Optional[str] = None
    ) -> None: ...
    def XMLAddElement(self, parent: Element) -> None: ...
    def defineFaciesByTruncRule(self, alphaCoord: ndarray) -> Tuple[int, int]: ...
    def getClassName(self) -> str: ...
    def getFaciesInTruncRule(self) -> List[str]: ...
    def getNGaussFieldsInModel(self) -> int: ...
    def initialize(
        self,
        mainFaciesTable: APSMainFaciesTable,
        faciesInZone: List[str],
        faciesInTruncRule: List[str],
        gaussFieldsInZone: List[str],
        alphaFieldNameForBackGroundFacies: List[str],
        sf_value: float,
        sf_name: Optional[str],
        ysf: float,
        sbhd: float,
        useConstTruncParam: int,
        debug_level: Debug = Debug.OFF
    ) -> None: ...
    def setTruncRule(self, faciesProb: List[float], cellIndx: int = 0) -> None: ...
    def truncMapPolygons(
        self
    ) -> Union[List[Union[List[Union[List[float], List[Union[float, int]]]], List[List[float]]]], List[List[List[float]]]]: ...