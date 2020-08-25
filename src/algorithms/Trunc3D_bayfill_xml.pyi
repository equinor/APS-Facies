# -*- coding: utf-8 -*-
from numpy import ndarray

from src.algorithms.Trunc2D_Base_xml import Trunc2D_Base
from src.algorithms.APSMainFaciesTable import APSMainFaciesTable
from src.utils.constants.simple import Debug
from typing import List, Optional, Tuple, Union
from xml.etree.ElementTree import Element

from src.utils.containers import FmuAttribute


class Trunc3D_bayfill(Trunc2D_Base):
    _setTruncRuleIsCalled: bool
    __eps: float
    _alphaIndxList: List[int]
    __useConstTruncModelParam: bool

    __param_sf_name: str
    __param_sf: float
    _is_param_sf_fmuupdatable: bool

    __param_ysf: float
    _is_param_ysf_fmuupdatable: bool

    __param_sbhd: float
    _is_param_sbhd_fmuupdatable: bool

    def __init__(
        self,
        trRuleXML: Optional[Element] = None,
        mainFaciesTable: Optional[APSMainFaciesTable] = None,
        faciesInZone: Optional[List[str]] = None,
        gaussFieldsInZone: Optional[List[str]] = None,
        debug_level: int = Debug.OFF,
        modelFileName: Optional[str] = None
    ) -> None: ...
    def __interpretXMLTree(self, trRuleXML, modelFileName): ...
    def XMLAddElement(self, parent: Element, zone_number:str, region_number:str, fmu_attributes: List[FmuAttribute]) -> None: ...
    def defineFaciesByTruncRule(self, alphaCoord: Union[ndarray, List[float]]) -> Tuple[int, int]: ...
    def getClassName(self) -> str: ...
    def getFaciesInTruncRule(self) -> List[str]: ...
    def getNGaussFieldsInModel(self) -> int: ...
    def getUseZ(self) -> bool: ...
    def initialize(
        self,
        mainFaciesTable: APSMainFaciesTable,
        faciesInZone: List[str],
        faciesInTruncRule: List[str],
        gaussFieldsInZone: List[str],
        alphaFieldNameForBackGroundFacies: List[str],
        sf_value: float,
        sf_name: Optional[str],
        sf_fmu_updatable: bool,
        ysf: float,
        ysf_fmu_updatable: bool,
        sbhd: float,
        sbhd_fmu_updatable: bool,
        useConstTruncParam: int,
        debug_level: Debug = Debug.OFF
    ) -> None: ...
    def getTruncationParam(self, gridModel, realNumber): ...
    def faciesIndxPerPolygon(self): ...
    def setTruncRule(self, faciesProb: Union[ndarray, List[float]], cellIndx: int = 0) -> None: ...
    def useConstTruncModelParam(self) -> bool: ...
    def __zeroPolygon(self) -> List[List[float]]: ...
    def __unitSquarePolygon(self) -> List[List[float]]: ...
    def truncMapPolygons(
        self
    ) -> Union[List[Union[List[Union[List[float], List[Union[float, int]]]], List[List[float]]]], List[List[List[float]]]]: ...
    def setSFParam(self, sfValue: float) -> None: ...
    def setSFParamFmuUpdatable(self, value: bool) -> None: ...
    def setYSFParam(self, ysfValue: float) -> None: ...
    def setYSFParamFmuUpdatable(self, value: bool) -> None: ...
    def setSBHDParam(self, sbhdValue: float) -> None: ...
    def setSBHDParamFmuUpdatable(self, value: bool) -> None: ...
