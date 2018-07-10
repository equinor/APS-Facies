# -*- coding: utf-8 -*-
from numpy import float64, ndarray

from src.utils.constants.simple import Debug, OriginType, TrendType
from typing import List, Optional, Union, Tuple
from xml.etree.ElementTree import Element


class Trend3D:
    type: TrendType
    def _XMLAddElementTag(
        self,
        trendElement: Element,
        zone_number: Union[int, str],
        region_number: Optional[Union[str, int]],
        gf_name: str,
        fmu_attributes: List[str]
    ) -> None: ...
    def __init__(
        self,
        trendRuleXML: Optional[Element],
        modelFileName: Optional[str] = None,
        debug_level: int = Debug.OFF
    ) -> None: ...
    def _interpretXMLTree(self, trendRuleXML: Element, modelFileName: str) -> None: ...
    def _setTrendCenter(
        self,
        x0: float,
        y0: float,
        azimuthAngle: float,
        simBoxXLength: float,
        simBoxYLength: float,
        simBoxThickness: float,
        origin_type: Optional[OriginType] = None,
        origin: Optional[List[float]] = None
    ) -> None: ...
    def createTrendFor2DProjection(
        self,
        sim_box_size,
        azimuthSimBox: float,
        preview_size,
        projectionType: str,
        crossSectionRelativePos: float
    ) -> Tuple[float64, float64, ndarray]: ...
    def getAzimuth(self) -> float: ...
    def getStackingAngle(self) -> float: ...
    def getStackingDirection(self) -> int: ...
    def get_origin_type_from_model_file(
        self,
        model_file_name: str,
        trendRuleXML: Element
    ) -> OriginType: ...
    def XMLAddElement(self, parent: Element, fmu_attributes: List[str]) -> None: ...
    def initialize(
        self,
        azimuthAngle: float = 0.0,
        azimuthAngleFmuUpdatable: bool = False,
        stackingAngle: float = 0.01,
        stackingAngleFmuUpdatable: bool = False,
        direction: int = 1,
        debug_level: Debug = Debug.OFF
    ) -> None: ...
    def setAzimuth(self, angle: float) -> None: ...
    def setStackingAngle(self, stackingAngle: float) -> None: ...
    def setStackingDirection(self, direction: int) -> None: ...
    def createTrendFor2DProjection(
            self,
            sim_box_size,
            azimuthSimBox,
            preview_size,
            projectionType,
            crossSectionRelativePos
    ): ...

class Trend3D_linear(Trend3D):
    def XMLAddElement(self, parent: Element, fmu_attributes: List[str]) -> None: ...
    def __init__(
        self,
        trendRuleXML: Optional[Element],
        zone_number: Union[int, str],
        region_number: Optional[Union[int, str]],
        gf_name: str,
        modelFileName: Optional[str] = None,
        debug_level: Debug = Debug.OFF
    ) -> None: ...
    def _interpretXMLTree(self, trendRuleXML: Element, modelFileName: str) -> None: ...
    def initialize(
        self,
        azimuthAngle: float,
        azimuthAngleFmuUpdatable: bool,
        stackingAngle: float,
        stackingAngleFmuUpdatable: bool,
        direction: int,
        debug_level: Debug = Debug.OFF
    ) -> None: ...


class Trend3D_elliptic(Trend3D):
    def XMLAddElement(self, parent: Element, fmu_attributes: List[str]) -> None: ...
    def __init__(
        self,
        trendRuleXML: Optional[Element],
        zone_number: Union[int, str],
        region_number: Optional[Union[int, str]],
        gf_name: str,
        modelFileName: Optional[str] = None,
        debug_level: Debug = Debug.OFF
    ) -> None: ...
    def _interpretXMLTree(self, trendRuleXML: Element, modelFileName: str) -> None: ...
    def getCurvature(self) -> float: ...
    def getOrigin(self) -> List[float]: ...
    def getOriginType(self) -> OriginType: ...
    def initialize(
        self,
        azimuthAngle: float,
        azimuthAngleFmuUpdatable: bool,
        stackingAngle: float,
        stackingAngleFmuUpdatable: bool,
        direction: int,
        curvature: float = 1.0,
        curvatureFmuUpdatable: bool = False,
        origin: Optional[List[float]] = None,
        originFmuUpdatable: bool = False,
        origin_type: OriginType = OriginType.RELATIVE,
        debug_level: Debug = Debug.OFF
    ) -> None: ...
    def setCurvature(self, curvature: float) -> None: ...
    def setOrigin(self, origin: List[float]) -> None: ...
    def setOriginType(self, originType: OriginType) -> None: ...


class Trend3D_hyperbolic(Trend3D):
    def XMLAddElement(self, parent: Element, fmu_attributes: List[str]) -> None: ...
    def __init__(
        self,
        trendRuleXML: Optional[Element],
        zone_number: Union[int, str],
        region_number: Optional[Union[int, str]],
        gf_name: str,
        modelFileName: Optional[str] = None,
        debug_level: int = Debug.OFF
    ) -> None: ...
    def _calculateTrendModelParam(self, useRelativeAzimuth: bool = False) -> List[float]: ...
    def _hyperbolicTrendFunction(
        self,
        parametersForTrendCalc: List[float],
        x: float,
        y: float,
        z: float
    ) -> float64: ...
    def _interpretXMLTree(self, trendRuleXML: Element, modelFileName: str) -> None: ...
    def _setTrendCenter(
        self,
        x0: float,
        y0: float,
        azimuthAngle: float,
        simBoxXLength: float,
        simBoxYLength: float,
        simBoxThickness: float,
        origin_type: None = None,
        origin: None = None
    ) -> None: ...
    def _trendValueCalculationSimBox(
        self,
        parametersForTrendCalc: List[float],
        i: int,
        j: int,
        k: float,
        xinc: float,
        yinc: float,
        zinc: float
    ) -> float64: ...
    def _writeTrendSpecificParam(self) -> None: ...
    def getCurvature(self) -> float: ...
    def getMigrationAngle(self) -> float: ...
    def getOrigin(self) -> List[float]: ...
    def getOriginType(self) -> OriginType: ...
    def initialize(
        self,
        azimuthAngle: float,
        azimuthAngleFmuUpdatable: bool,
        stackingAngle: float,
        stackingAngleFmuUpdatable: bool,
        direction: int,
        migrationAngle: float,
        migrationAngleFmuUpdatable: bool,
        curvature: float,
        curvatureFmuUpdatable: bool,
        origin: Optional[List[float]] = None,
        originFmuUpdatable: bool = False,
        origin_type: OriginType = OriginType.RELATIVE,
        debug_level: Debug = Debug.OFF
    ) -> None: ...
    def setCurvature(self, curvature: float) -> None: ...
    def setMigrationAngle(self, migrationAngle: float) -> None: ...
    def setOrigin(self, origin: List[float]) -> None: ...
    def setOriginType(self, originType: OriginType) -> None: ...


class Trend3D_rms_param(Trend3D):
    def XMLAddElement(self, parent: Element, fmu_attributes: List[str]) -> None: ...
    def __init__(
        self,
        trendRuleXML: Element,
        zone_number: str,
        region_number: str,
        gf_name: str,
        modelFileName: Optional[str] = None,
        debug_level: int = Debug.OFF,
    ) -> None: ...
    def _interpretXMLTree(self, trendRuleXML: Element, modelFileName: str) -> None: ...
    def getTrendParamName(self) -> str: ...
    def setTrendParamName(self, paramName: str) -> None: ...


class Trend3D_elliptic_cone(Trend3D):
    def XMLAddElement(self, parent: Element, fmu_attributes: List[str]) -> None: ...
    def __init__(
        self,
        trendRuleXML: Optional[Element],
        zone_number: Union[int, str],
        region_number: Optional[int],
        gf_name: str,
        modelFileName: Optional[str] = None,
        debug_level: int = Debug.OFF
    ) -> None: ...
    def _interpretXMLTree(self, trendRuleXML: Element, modelFileName: str) -> None: ...
    def initialize(
        self,
        azimuthAngle: float,
        azimuthAngleFmuUpdatable: bool,
        stackingAngle: float,
        stackingAngleFmuUpdatable: bool,
        direction: int,
        migrationAngle: float = 0.0,
        migrationAngleFmuUpdatable: bool = False,
        curvature: float = 1.0,
        curvatureFmuUpdatable: bool = False,
        relativeSize: float = 1.0,
        relativeSizeFmuUpdatable: bool = False,
        origin: Optional[List[float]] = None,
        originFmuUpdatable: bool = False,
        origin_type: OriginType = OriginType.RELATIVE,
        debug_level: Debug = Debug.OFF
    ) -> None: ...
