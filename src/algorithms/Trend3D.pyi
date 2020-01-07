# -*- coding: utf-8 -*-
from numpy import float64, ndarray

from src.algorithms.APSGaussModel import GaussianFieldName, SimulationBoxOrigin
from src.algorithms.properties import CrossSection, FmuProperty
from src.utils.constants.simple import Debug, OriginType, TrendType, Direction, TrendParameter
from typing import List, Optional, Union, Tuple, Dict, Any, Type
from xml.etree.ElementTree import Element


Point3D = Tuple[float, float, float]

HyperbolicTrendParameters = Tuple[float, float, float, float, float, float]


def validator(self, value: Union[FmuProperty[float], float]) -> bool: ...
def required_parameters(_type: TrendType) -> List[TrendParameter]: ...


class Point3DProperty:
    _dimension: int
    x: FmuProperty[float]
    y: FmuProperty[float]
    z: FmuProperty[float]
    def __init__(self, *args): ...
    def __getitem__(self, item: int) -> FmuProperty[float]: ...

    def as_point(self) -> Point3D: ...
    def fmu_as_point(self) -> Tuple[bool, bool, bool]: ...


class Trend3D:
    type:               TrendType
    azimuth:            FmuProperty[float]
    stacking_angle:     FmuProperty[float]
    stacking_direction: Direction

    _x_center: float
    _y_center: float
    _z_center: float

    _x_sim_box: float
    _y_sim_box: float
    _z_sim_box: float

    _start_layer:   int
    _end_layer:     int

    _x_center_in_sim_box_coordinates: float
    _y_center_in_sim_box_coordinates: float
    _z_center_in_sim_box_coordinates: float

    _relative_azimuth: float

    _debug_level: Debug

    _class_name: str
    def _XMLAddElementTag(
        self,
        trend_element:  Element,
        zone_number:    Union[int, str],
        region_number:  Optional[Union[str, int]],
        gf_name:        str,
        fmu_attributes: List[str]
    ) -> None: ...
    def __init__(
            self,
            azimuth_angle:                  float       = 0.0,
            azimuth_angle_fmu_updatable:    bool        = False,
            stacking_angle:                 float       = 0.0001,
            stacking_angle_fmu_updatable:   bool        = False,
            direction:                      Direction   = Direction.PROGRADING,
            debug_level:                    Debug       = Debug.OFF,
            **kwargs
    ) -> None: ...
    @classmethod
    def from_xml(
            cls,
            trend_rule_xml:     Element,
            model_file_name:    Optional[str]   = None,
            debug_level:        Debug           = Debug.OFF
    ) -> Trend3D: ...
    def as_dict(self) -> Dict[str, Any]: ...

    def _setTrendCenter(
        self,
        x0: float,
        y0: float,
        azimuth_angle: float,
        sim_box_x_length: float,
        sim_box_y_length: float,
        sim_box_thickness: float,
        origin_type: Optional[OriginType] = None,
        origin: Optional[Union[Point3D, Point3DProperty]] = None
    ) -> None: ...
    def _calculateTrendModelParam(self, use_relative_azimuth: bool = False): ...
    def _writeTrendSpecificParam(self) -> None: ...
    def _trendValueCalculation(self, parameters_for_trend_calc, x, y, k, zinc): ...
    def _trendValueCalculationSimBox(
            self,
            parametersForTrendCalc: Tuple,
            i,
            j,
            k,
            xinc,
            yinc,
            zinc
    ): ...
    def createTrend(
            self,
            grid_model,
            realization_number,
            cell_index_defined,
            zone_number,
            sim_box_thickness,
            zinc: Optional[float] = None,
    ): ...
    def createTrendFor2DProjection(
        self,
        sim_box_size,
        azimuth_sim_box: float,
        preview_size,
        cross_section: CrossSection,
        sim_box_origin: SimulationBoxOrigin,
    ) -> Tuple[float64, float64, ndarray]: ...
    def getStackingDirection(self) -> int: ...
    def XMLAddElement(
            self,
            parent: Element,
            zone_number: int,
            region_number: int,
            gf_name: str,
            fmu_attributes: List[str]
    ) -> None: ...
    def setStackingDirection(self, direction: int) -> None: ...

class Trend3D_linear(Trend3D):
    type: TrendType
    _zone_number: int
    _region_number: int
    _gf_name: str
    def XMLAddElement(
            self,
            parent:         Element,
            zone_number:    int,
            region_number:  int,
            gf_name:        GaussianFieldName,
            fmu_attributes: List[str]
    ) -> None: ...
    def __init__(
            self,
            azimuth_angle:                  float       = 0.0,
            azimuth_angle_fmu_updatable:    bool        = False,
            stacking_angle:                 float       = 0.0001,
            stacking_angle_fmu_updatable:   bool        = False,
            direction:                      Direction   = Direction.PROGRADING,
            debug_level:                    Debug       = Debug.OFF,
            **kwargs
    ) -> None: ...
    @classmethod
    def from_xml(
            cls,
            trend_rule_xml:     Element,
            model_file_name:    Optional[str]   = None,
            debug_level:        Debug           = Debug.OFF
    ) -> Trend3D_linear: ...
    def _trendValueCalculationSimBox(
            self,
            parameters_for_trend_calc: Tuple[float, float, float],
            i,
            j,
            k,
            xinc,
            yinc,
            zinc
    ): ...
    def _linearTrendFunction(
            self,
            parameters_for_trend_calc: Tuple[float, float, float],
            x_rel: float,
            y_rel: float,
            z_rel: float,
    ) -> float: ...
    def _calculateTrendModelParam(self, use_relative_azimuth: bool = False) -> Tuple[float, float, float]: ...
    def _writeTrendSpecificParam(self) -> None: ...
    def _trendValueCalculation(self, parameters_for_trend_calc, x, y, k, zinc): ...


class Trend3D_conic(Trend3D):
    type:               OriginType
    curvature:          FmuProperty[float]
    origin:             Point3DProperty
    origin_type:        OriginType
    migration_angle:    FmuProperty[float]

    _isOriginXFMUUpdatable: bool
    _isOriginYFMUUpdatable: bool
    _isOriginZFMUUpdatable: bool

    _zCenterInSimBoxCoordinates: float
    _xCenterInSimBoxCoordinates: float
    _yCenterInSimBoxCoordinates: float

    _zone_number:   int
    _region_number: int
    _gf_name:       str
    def __init__(
            self,
            azimuth_angle:                  float                                   = 0.0,
            azimuth_angle_fmu_updatable:    bool                                    = False,
            stacking_angle:                 float                                   = 0.0001,
            stacking_angle_fmu_updatable:   bool                                    = False,
            curvature:                      float                                   = 0.0001,
            curvature_fmu_updatable:        bool                                    = False,
            migration_angle:                Optional[float]                         = None,
            migration_angle_fmu_updatable:  bool                                    = False,
            origin:                         Tuple[float, float, float]              = (0.0, 0.0, 0.0),
            origin_fmu_updatable:           Union[bool, Tuple[bool, bool, bool]]    = (False, False, False),
            origin_type:                    OriginType                              = OriginType.RELATIVE,
            direction:                      Direction                               = Direction.PROGRADING,
            debug_level:                    Debug                                   = Debug.OFF,
            **kwargs
    ) -> None: ...
    @classmethod
    def from_xml(
            cls,
            trend_rule_xml:         Element,
            model_file_name:        Optional[str]   = None,
            debug_level:            Debug           = Debug.OFF,
            get_migration_angle:    bool            = True,
            get_origin_z:           bool            = True,
    ) -> Trend3D_conic: ...
    def setCurvatureFmuUpdatable(self, value: bool) -> None: ...

    def setOriginXFmuUpdatable(self, value: bool) -> None: ...
    def setOriginYFmuUpdatable(self, value: bool) -> None: ...
    def setOriginZFmuUpdatable(self, value: bool) -> None: ...


class Trend3D_elliptic(Trend3D_conic):
    def __init__(
            self,
            azimuth_angle:                  float                                   = 0.0,
            azimuth_angle_fmu_updatable:    bool                                    = False,
            stacking_angle:                 float                                   = 0.0001,
            stacking_angle_fmu_updatable:   bool                                    = False,
            curvature:                      float                                   = 0.0001,
            curvature_fmu_updatable:        bool                                    = False,
            origin:                         Tuple[float, float, float]              = (0.0, 0.0, 0.0),
            origin_fmu_updatable:           Union[bool, Tuple[bool, bool, bool]]    = (False, False, False),
            origin_type:                    OriginType                              = OriginType.RELATIVE,
            direction:                      Direction                               = Direction.PROGRADING,
            debug_level:                    Debug                                   = Debug.OFF,
            **kwargs
    ) -> None: ...
    def XMLAddElement(
            self,
            parent: Element,
            zone_number: int,
            region_number: int,
            gf_name: GaussianFieldName,
            fmu_attributes: List[str]
    ) -> None: ...
    @classmethod
    def from_xml(
            cls,
            trend_rule_xml:     Element,
            model_file_name:    Optional[str]   = None,
            debug_level:        Debug           = Debug.OFF,
            **kwargs
    ) -> Trend3D_elliptic: ...
    def _trendValueCalculation(self, parameters_for_trend_calc, x, y, k, zinc):...
    def _calculateTrendModelParam(self, use_relative_azimuth: bool = False) -> Tuple[float, float, float, float, float]: ...
    def _ellipticTrendFunction(
            self,
            parameters_for_trend_calc: Tuple[float, float, float, float, float],
            x: float,
            y: float,
            z: float,
    ) -> float: ...
    def _trendValueCalculationSimBox(
            self,
            parameters_for_trend_calc: Tuple[float, float, float, float, float],
            i,
            j,
            k,
            xinc,
            yinc,
            zinc
    ): ...
    def _writeTrendSpecificParam(self) -> None: ...


class Trend3D_hyperbolic(Trend3D_conic):
    type: TrendType
    def __init__(
            self,
            azimuth_angle:                  float                                   = 0.0,
            azimuth_angle_fmu_updatable:    bool                                    = False,
            stacking_angle:                 float                                   = 0.0001,
            stacking_angle_fmu_updatable:   bool                                    = False,
            curvature:                      float                                   = 0.0001,
            curvature_fmu_updatable:        bool                                    = False,
            migration_angle:                float                                   = 0.0,
            migration_angle_fmu_updatable:  bool                                    = False,
            origin:                         Tuple[float, float, float]              = (0.0, 0.0, 0.0),
            origin_fmu_updatable:           Union[bool, Tuple[bool, bool, bool]]    = (False, False, False),
            origin_type:                    OriginType                              = OriginType.RELATIVE,
            direction:                      Direction                               = Direction.PROGRADING,
            debug_level:                    Debug                                   = Debug.OFF,
            **kwargs
    ) -> None: ...
    @classmethod
    def from_xml(
            cls,
            trend_rule_xml:     Element,
            model_file_name:    Optional[str]   = None,
            debug_level:        Debug           = Debug.OFF, **kwargs
    ) -> Trend3D_hyperbolic: ...
    def XMLAddElement(
            self,
            parent: Element,
            zone_number: int,
            region_number: int,
            gf_name: GaussianFieldName,
            fmu_attributes: List[str]
    ) -> None: ...
    def _calculateTrendModelParam(self, use_relative_azimuth: bool = False) -> HyperbolicTrendParameters: ...
    def _hyperbolicTrendFunction(
        self,
        parameters_for_trend_calc: HyperbolicTrendParameters,
        x: float,
        y: float,
        z: float
    ) -> float64: ...
    def _setTrendCenter(
        self,
        x0:                 float,
        y0:                 float,
        azimuth_angle:       float,
        sim_box_x_length:      float,
        sim_box_y_length:      float,
        sim_box_thickness:    float,
        origin_type:        Optional[OriginType]    = None,
        origin:             Optional[Point3D]       = None
    ) -> None: ...
    def _trendValueCalculation(self, parameters_for_trend_calc, x, y, k, zinc):...
    def _trendValueCalculationSimBox(
        self,
        parametersForTrendCalc: HyperbolicTrendParameters,
        i:      int,
        j:      int,
        k:      float,
        xinc:   float,
        yinc:   float,
        zinc:   float
    ) -> float64: ...
    def _writeTrendSpecificParam(self) -> None: ...
    def _trendValueCalculationSimBox(
            self,
            parameters_for_trend_calc: HyperbolicTrendParameters,
            i,
            j,
            k,
            xinc,
            yinc,
            zinc
    ): ...


class Trend3D_rms_param(Trend3D):
    trend_parameter_name: str
    type: TrendType
    def __init__(
        self,
        rms_parameter_name:     str,
        debug_level:            Debug = Debug.OFF,
    ) -> None: ...
    @classmethod
    def from_xml(
            cls,
            trend_rule_xml:     Element,
            model_file_name:    Optional[str]   = None,
            debug_level:        Debug           = Debug.OFF
    ) -> Trend3D_rms_param: ...
    def XMLAddElement(
            self,
            parent:         Element,
            zone_number:    int,
            region_number:  int,
            gf_name:        str,
            fmu_attributes: List[str]
    ) -> None: ...
    def _writeTrendSpecificParam(self) -> None: ...


class Trend3D_elliptic_cone(Trend3D_conic):
    relative_size_of_ellipse: FmuProperty[float]
    def __init__(
            self,
            azimuth_angle:                  float                                   = 0.0,
            azimuth_angle_fmu_updatable:    bool                                    = False,
            stacking_angle:                 float                                   = 0.0001,
            stacking_angle_fmu_updatable:   bool                                    = False,
            curvature:                      float                                   = 0.0001,
            curvature_fmu_updatable:        bool                                    = False,
            migration_angle:                float                                   = 0.0,
            migration_angle_fmu_updatable:  bool                                    = False,
            relative_size:                  float                                   = 1.0,
            relative_size_fmu_updatable:    bool                                    = False,
            origin:                         Tuple[float, float, float]              = (0.0, 0.0, 0.0),
            origin_fmu_updatable:           Union[bool, Tuple[bool, bool, bool]]    = (False, False, False),
            origin_type:                    OriginType                              = OriginType.RELATIVE,
            direction:                      Direction                               = Direction.PROGRADING,
            debug_level:                    Debug                                   = Debug.OFF,
            **kwargs
    ) -> None: ...
    @classmethod
    def from_xml(
            cls,
            trend_rule_xml:     Element,
            model_file_name:    Optional[str]   = None,
            debug_level:        Debug           = Debug.OFF,
            **kwargs
    ) -> Trend3D_elliptic_cone: ...
    def XMLAddElement(
            self,
            parent:         Element,
            zone_number:    int,
            region_number:  int,
            gf_name:        str,
            fmu_attributes: List[str]
    ) -> None: ...
    def _trendValueCalculation(self, parameters_for_trend_calc, x, y, k, zinc): ...
    def _trendValueCalculationSimBox(
            self,
            parameters_for_trend_calc: HyperbolicTrendParameters,
            i,
            j,
            k,
            xinc,
            yinc,
            zinc
    ): ...
    def _calculateTrendModelParam(self, use_relative_azimuth: bool = False) -> HyperbolicTrendParameters: ...
    def _ellipticConeTrendFunction(
            self,
            parameters_for_trend_calc: HyperbolicTrendParameters,
            x:      float,
            y:      float,
            z:      float,
            zinc:   Union[int, float],
    ) -> float: ...
    def _writeTrendSpecificParam(self) -> None: ...

ConicTrend: Type[Trend3D_conic]
