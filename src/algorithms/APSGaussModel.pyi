# -*- coding: utf-8 -*-
from numpy import float64, ndarray

from src.algorithms.properties import FmuProperty, CrossSection
from src.algorithms.APSMainFaciesTable import APSMainFaciesTable
from src.algorithms.Trend3D import (
    Trend3D_elliptic,
    Trend3D_elliptic_cone,
    Trend3D_hyperbolic,
    Trend3D_linear,
    Trend3D_rms_param,
    Trend3D,
)
from src.utils.constants.simple import Debug, VariogramType, CrossSectionType
from typing import List, Optional, Tuple, Union, TypeVar, NewType, Dict, Callable
from xml.etree.ElementTree import Element

from src.utils.records import TrendRecord, VariogramRecord

Number = Union[int, float]

GridSize = Tuple[int, int, int]
SimulationBoxSize = Tuple[float, float, float]
SimulationBoxOrigin = Tuple[float, float]

PropertyName = str
XMLKeyword = str

T = TypeVar('T')
GaussianFieldName = NewType('GaussianFieldName', str)


class GaussianFieldSimulationSettings:
    cross_section: CrossSection
    grid_azimuth: float
    grid_size: GridSize
    simulation_box_size: SimulationBoxSize
    simulation_box_origin: SimulationBoxOrigin
    seed: int
    dimensions: Tuple[int, int]
    def __init__(
            self,
            cross_section: CrossSection,
            grid_azimuth: float,
            grid_size: GridSize,
            simulation_box_size: SimulationBoxSize,
            simulation_box_origin: SimulationBoxOrigin,
            seed: int,
    ): ...
    def merge(
            self,
            cross_section: Optional[CrossSection] = None,
            grid_azimuth: Optional[float] = None,
            grid_size: Optional[GridSize] = None,
            simulation_box_size: Optional[SimulationBoxSize] = None,
            simulation_box_origin: Optional[SimulationBoxOrigin] = None,
            seed: Optional[int] = None,
    ) -> GaussianFieldSimulationSettings: ...
    @classmethod
    def from_dict(cls, **kwargs) -> GaussianFieldSimulationSettings: ...


class GaussianFieldSimulation:
    def __init__(
            self,
            name: GaussianFieldName,
            field: ndarray,
            settings: GaussianFieldSimulationSettings,
    ) -> None: ...
    name: GaussianFieldName
    field: ndarray
    settings: GaussianFieldSimulationSettings
    cross_section: CrossSection
    grid_azimuth: float
    grid_size: GridSize
    simulation_box_size: SimulationBoxSize
    def field_as_matrix(self, grid_index_order: str = 'C') -> ndarray: ...


class GaussianField:
    def __init__(
            self,
            name: Union[GaussianFieldName, str],
            variogram: Optional[Variogram] = None,
            trend: Optional[Trend] = None,
            seed: Optional[int] = None,
            settings: Optional[GaussianFieldSimulationSettings] = None
    ) -> None: ...
    name: GaussianFieldName
    variogram: Variogram
    trend: Trend
    seed: int
    settings: Optional[GaussianFieldSimulationSettings]
    def __getitem__(self, item): ...
    def _simulate(
            self,
            cross_section: Optional[CrossSection] = None,
            grid_azimuth: Optional[float] = None,
            grid_size: Optional[GridSize] = None,
            simulation_box_size: Optional[SimulationBoxSize] = None,
            simulation_box_origin: Optional[SimulationBoxOrigin] = None,
            debug_level: Debug = Debug.OFF
    ) -> ndarray: ...
    def simulate(
            self,
            cross_section: Optional[CrossSection] = None,
            grid_azimuth: Optional[float] = None,
            grid_size: Optional[GridSize] = None,
            simulation_box_size: Optional[SimulationBoxSize] = None,
            simulation_box_origin: Optional[SimulationBoxOrigin] = None,
            debug_level: Debug = Debug.OFF
    ) -> GaussianFieldSimulation: ...


MainRange = FmuProperty[int]
PerpendicularRange = FmuProperty[int]
VerticalRange = FmuProperty[int]


class Ranges:
    def __init__(
            self,
            main: Union[MainRange, int],
            perpendicular: Union[PerpendicularRange, int],
            vertical: Union[VerticalRange, int],
    ) -> None: ...
    main: MainRange
    perpendicular: PerpendicularRange
    vertical: VerticalRange

    range1: MainRange
    range2: PerpendicularRange
    range3: VerticalRange


class Angles:
    def __init__(
            self,
            azimuth: Union[FmuProperty[float], float],
            dip: Union[FmuProperty[float], float],
    ) -> None: ...
    azimuth: FmuProperty[float]
    dip: FmuProperty[float]


class Trend:
    def __init__(
            self,
            name: GaussianFieldName,
            use_trend: bool = False,
            model: Optional[Trend3D] = None,
            relative_std_dev: Optional[FmuProperty[float]] = None,
    ) -> None: ...
    name: GaussianFieldName
    use_trend: bool
    model: Trend3D
    relative_std_dev: FmuProperty[float]
    @classmethod
    def from_definition(cls, definition: Union[TrendRecord, List]) -> Trend: ...
    def as_list(self) -> Tuple[GaussianFieldName, bool, Optional[Trend3D], float, bool]: ...
    @classmethod
    def from_dict(cls, name: GaussianFieldName, use: bool = False, **kwargs) -> Trend: ...
    @staticmethod
    def get_model(**kwargs) -> Trend3D: ...

class Variogram:
    types: VariogramType
    def __init__(
            self,
            name: Union[GaussianFieldName, str],
            type: VariogramType,
            ranges: Ranges,
            angles: Angles,
            power: Optional[FmuProperty] = None,
    ) -> None: ...
    name: GaussianFieldName
    type: VariogramType
    ranges: Ranges
    angles: Angles
    power: FmuProperty[float]

    def __getitem__(self, item): ...
    def as_list(self) -> List: ...

    @classmethod
    def from_definition(cls, definition: Union[VariogramRecord, List]): ...
    @staticmethod
    def __mapping__() -> Dict[str, int]: ...
    def calc_2d_variogram_from_3d_variogram(
        self,
        grid_azimuth: float,
        projection: str,
        debug_level: Debug = Debug.OFF,
    ) -> Tuple[float64, float64, float64, float64]: ...

class APSGaussModel:
    debug_level: Debug
    num_gaussian_fields: int
    fields: List[GaussianField]
    used_gaussian_field_names: List[GaussianFieldName]
    _gaussian_models: Dict[GaussianFieldName, GaussianField]
    __xml_keyword: Dict[PropertyName, XMLKeyword]
    __class_name: str
    __main_facies_table: Optional[APSMainFaciesTable]
    __sim_box_thickness: int
    __model_file_name: str
    @property
    def zone_number(self) -> int: ...
    @zone_number.setter
    def zone_number(self, value: int): ...
    def __init__(
        self,
        ET_Tree_zone: Optional[Element] = None,
        mainFaciesTable: Optional[APSMainFaciesTable] = None,
        modelFileName: Optional[str] = None,
        debug_level: int = Debug.OFF,
        simBoxThickness: Number = 0
    ) -> None: ...
    def __interpretXMLTree(self, ET_Tree_zone): ...
    def XMLAddElement(self, parent: Element, zone_number: int, region_number: int, fmu_attributes: List[str]) -> None: ...
    def findGaussFieldParameterItem(self, gaussFieldName: GaussianFieldName) -> List[Union[str, float, bool]]: ...
    def getAzimuthAngle(self, gaussFieldName: GaussianFieldName) -> float: ...
    def getDipAngle(self, gaussFieldName: GaussianFieldName) -> float: ...
    def getMainRange(self, gaussFieldName: GaussianFieldName) -> float: ...
    def getAnisotropyAzimuthAngle(self, gaussFieldName: GaussianFieldName) -> float: ...
    def getAnisotropyDipAngle(self, gaussFieldName: GaussianFieldName) -> float: ...
    def getPerpRange(self, gaussFieldName: GaussianFieldName) -> float: ...
    def getPower(self, gaussFieldName: GaussianFieldName) -> float: ...
    def __get_property(self, gaussFieldName: GaussianFieldName, keyword: str) -> Union[str, float, bool]: ...
    def getTrendItem(self, gfName: GaussianFieldName ) -> Trend: ...
    def getTrendModel(self, gfName: GaussianFieldName) -> Union[Trend3D_hyperbolic, Trend3D_elliptic, Trend3D_linear, Trend3D_rms_param]: ...
    def hasTrendModel(self, gfName: GaussianFieldName) -> bool: ...
    def getTrendModelObject(self, gfName: GaussianFieldName) -> Trend3D: ...
    def getVariogramType(self, gaussFieldName: GaussianFieldName) -> VariogramType: ...
    def getVariogramTypeNumber(self, gaussFieldName: GaussianFieldName) -> int: ...
    def getVertRange(self, gaussFieldName: GaussianFieldName) -> float: ...
    def _get_value_from_xml(self, property_name: str, xml_tree: Element) -> Tuple[Number, bool]: ...
    def get_variogram(
        self,
        gf: Element,
        gf_name: GaussianFieldName,
        zone_number: int,
    ) -> Tuple[Element, VariogramType]: ...
    def get_variogram_model(self, name: GaussianFieldName) -> Variogram: ...
    @staticmethod
    def get_variogram_type(
        variogram: Union[str, VariogramType, Element]
    ) -> VariogramType: ...
    def initialize(
        self,
        main_facies_table: APSMainFaciesTable,
        gauss_model_list: List[List[Union[str, float, bool]]],
        trend_model_list: Union[List[Union[List[Union[str, int, Trend3D_hyperbolic, float]], List[Union[str, int, Trend3D_elliptic]]]], List[Union[List[Union[str, int, Trend3D_hyperbolic, float]], List[Union[str, int, Trend3D_elliptic_cone, float]], List[Union[str, int, Trend3D_hyperbolic]]]], List[Union[List[Union[str, int, Trend3D_linear]], List[Union[str, int, Trend3D_elliptic, float]], List[Union[str, int, Trend3D_elliptic]]]], List[Union[List[Union[str, int, Trend3D_linear, float]], List[Union[str, int, Trend3D_linear]]]], List[Union[List[Union[str, int, Trend3D_hyperbolic, float]], List[Union[str, int, Trend3D_elliptic]], List[Union[str, int, Trend3D_elliptic, float]]]]],
        sim_box_thickness: float,
        preview_seed_list: List[List[Union[str, int]]],
        debug_level: Debug = Debug.OFF
    ) -> None: ...
    def setAzimuthAngle(self, gaussFieldName: GaussianFieldName, azimuth: float): ...
    def setDipAngle(self, gaussFieldName: GaussianFieldName, dip: float): ...
    def setMainRange(self, gaussFieldName: GaussianFieldName, range1: float) -> int: ...
    def setPerpRange(self, gaussFieldName: GaussianFieldName, range2: float) -> int: ...
    def setPower(self, gaussFieldName: GaussianFieldName, power: float) -> int: ...
    def setSeedForPreviewSimulation(self, gf_name: GaussianFieldName, seed: int) -> int: ...
    def setVariogramType(self, gaussFieldName: GaussianFieldName, variogramType: VariogramType) -> int: ...
    def setVertRange(self, gaussFieldName: GaussianFieldName, range3: float) -> int: ...
    def updateGaussFieldParam(
        self,
        gf_name: GaussianFieldName,
        variogram_type: VariogramType,
        range1: float,
        range2: float,
        range3: float,
        azimuth: float,
        dip: float,
        power: float,
        range1_fmu_updatable: bool,
        range2_fmu_updatable: bool,
        range3_fmu_updatable: bool,
        azimuth_fmu_updatable: bool,
        dip_fmu_updatable: bool,
        power_fmu_updatable: bool,
        use_trend: bool = False,
        rel_std_dev: float = 0.0,
        rel_std_dev_fmu_updatable: bool = False,
        trend_model_obj: Optional[Trend3D] = None
    ) -> int: ...
    def _add_xml_element(
            self,
            gf_name: GaussianFieldName,
            property_name: str,
            parent: Element,
            variogram_element: Element,
            fmu_attributes: List,
            create_fmu_variable: Callable
    ) -> None: ...
    def simGaussFieldWithTrendAndTransform(
        self,
        simulation_box_size: SimulationBoxSize,
        grid_size: GridSize,
        grid_azimuth: float,
        cross_section: CrossSection,
        simulation_box_origin,
    ) -> List[GaussianField]: ...
    def calc2DVariogramFrom3DVariogram(
            self,
            name: GaussianFieldName,
            grid_azimuth: float,
            projection: str,
    ) -> Tuple[float64, float64, float64, float64]: ...
    @staticmethod
    def _get_projection_parameters(
            cross_section_type: CrossSectionType,
            grid_size: GridSize,
            simulation_box_size: SimulationBoxSize,
    ) -> Tuple[Tuple[int, int], Tuple[float, float], str]: ...
    @staticmethod
    def create_gauss_field_trend(
            gf_name: GaussianFieldName,
            use_trend: bool,
            trend_model_obj: Trend3D,
            rel_std_dev: float,
            rel_std_dev_fmu_updatable: bool
    ) -> Trend: ...
    def updateGaussFieldTrendParam(
        self,
        gf_name: GaussianFieldName,
        use_trend: bool,
        trend_model_obj: Trend3D,
        rel_std_dev: Number,
        rel_std_dev_fmu_updatable: bool,
    ) -> int: ...
