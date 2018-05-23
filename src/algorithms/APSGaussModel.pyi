# -*- coding: utf-8 -*-
from depricated.APSGaussFieldJobs import APSGaussFieldJobs
from numpy import float64
from src.algorithms.APSMainFaciesTable import APSMainFaciesTable
from src.algorithms.Trend3D import (
    Trend3D_elliptic,
    Trend3D_elliptic_cone,
    Trend3D_hyperbolic,
    Trend3D_linear,
    Trend3D_rms_param,
)
from src.utils.constants.simple import Debug, VariogramType
from typing import Any, List, Optional, Tuple, Union
from xml.etree.ElementTree import Element


class APSGaussModel:
    def XMLAddElement(self, parent: Element) -> None: ...
    def __init__(
        self,
        ET_Tree_zone: Optional[Element] = None,
        mainFaciesTable: Optional[APSMainFaciesTable] = None,
        gaussFieldJobs: Optional[APSGaussFieldJobs] = None,
        modelFileName: Optional[str] = None,
        debug_level: int = Debug.OFF,
        zoneNumber: int = 0,
        simBoxThickness: Union[int, float] = 0
    ) -> None: ...
    def calc2DVariogramFrom3DVariogram(
        self,
        gaussFieldName: str,
        gridAzimuthAngle: float,
        projection: str
    ) -> Tuple[float64, float64, float64, float64]: ...
    def findGaussFieldParameterItem(
        self,
        gaussFieldName: str
    ) -> Union[List[Union[str, VariogramType, float]], List[Union[str, float]], List[Union[str, float, int]]]: ...
    def getAnisotropyAzimuthAngle(self, gaussFieldName: str) -> float: ...
    def getAnisotropyDipAngle(self, gaussFieldName: str) -> float: ...
    def getMainRange(self, gaussFieldName: str) -> Union[int, float]: ...
    def getNGaussFields(self) -> int: ...
    def getPerpRange(self, gaussFieldName: str) -> Union[int, float]: ...
    def getPower(self, gaussFieldName: str) -> float: ...
    def getTrendItem(
        self,
        gfName: str
    ) -> Union[List[Union[str, bool, Trend3D_linear, float]], List[Union[str, bool, Trend3D_hyperbolic, float]], List[Union[str, bool, Trend3D_rms_param, float]], List[Union[str, bool, Trend3D_elliptic, float]]]: ...
    def getTrendModelObject(
        self,
        gfName: str
    ) -> Union[Trend3D_hyperbolic, Trend3D_elliptic, Trend3D_linear, Trend3D_rms_param]: ...
    def getUsedGaussFieldNames(self) -> List[str]: ...
    def getVariogramType(self, gaussFieldName: str) -> VariogramType: ...
    def getVertRange(self, gaussFieldName: str) -> float: ...
    def get_variogram(
        self,
        gf: Element,
        gfName: str
    ) -> Tuple[Element, VariogramType]: ...
    @staticmethod
    def get_variogram_type(
        variogram: Union[str, VariogramType, Element]
    ) -> VariogramType: ...
    def initialize(
        self,
        inputZoneNumber: int,
        mainFaciesTable: APSMainFaciesTable,
        gaussFieldJobs: APSGaussFieldJobs,
        gaussModelList: Union[List[List[Union[str, float, int]]], List[List[Union[str, float]]]],
        trendModelList: Any,
        simBoxThickness: float,
        previewSeedList: List[List[Union[str, int]]],
        debug_level: Debug = Debug.OFF
    ) -> None: ...
    def setAnisotropyAzimuthAngle(self, gaussFieldName: str, azimuth: float) -> int: ...
    def setAnisotropyDipAngle(self, gaussFieldName: str, dip: float) -> int: ...
    def setMainRange(self, gaussFieldName: str, range1: float) -> int: ...
    def setPerpRange(self, gaussFieldName: str, range2: float) -> int: ...
    def setPower(self, gaussFieldName: str, power: float) -> int: ...
    def setSeedForPreviewSimulation(self, gfName: str, seed: int) -> int: ...
    def setValue(self, gaussFieldName: str, variableName: str, value: float, checkMax: bool = False) -> int: ...
    def setVariogramType(self, gaussFieldName: str, variogramType: VariogramType) -> int: ...
    def setVertRange(self, gaussFieldName: str, range3: float) -> int: ...
    def updateGaussFieldParam(
        self,
        gfName: str,
        variogramType: VariogramType,
        range1: Union[int, float],
        range2: Union[int, float],
        range3: float,
        azimuth: float,
        dip: float,
        power: float,
        useTrend: bool = False,
        relStdDev: Union[int, float] = 0.0,
        trendModelObj: Optional[Any] = None
    ) -> int: ...
    def updateGaussFieldTrendParam(
        self,
        gfName: str,
        useTrend: int,
        trendModelObj: Union[Trend3D_hyperbolic, Trend3D_elliptic, Trend3D_linear, Trend3D_elliptic_cone],
        relStdDev: Union[int, float]
    ) -> int: ...
