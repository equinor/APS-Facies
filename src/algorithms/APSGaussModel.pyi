# -*- coding: utf-8 -*-
from numpy import float64, ndarray
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
from typing import List, Optional, Tuple, Union, TypeVar, Generic, NewType, Dict, Callable
from xml.etree.ElementTree import Element

from src.utils.records import TrendRecord, VariogramRecord

Number = Union[int, float]

GridSize = Tuple[int, int, int]
SimulationBoxSize = Tuple[float, float, float]

PropertyName = str
XMLKeyword = str

T = TypeVar('T')
GaussianFieldName = NewType('GaussianFieldName', str)


def _make_ranged_property(
        name: str,
        error_template: str,
        minimum: Optional[Number] = None,
        maximum: Optional[Number] = None,
        additional_validator: Optional[Callable] = None,
        show_given_value: bool=True,
) -> property: ...
def _make_bounded_property(
        name: str,
        minimum: Number,
        maximum: Number,
        error_template: str,
        additional_validator: Optional[Callable] = None,
) -> property: ...
def _make_lower_bounded_property(
        name: str,
        additional_validator: Optional[Callable] = None
) -> property: ...
def _make_trend(name: str) -> property: ...
def _make_angle(name: str) -> property: ...

class GaussianFieldSimulation:
    def __init__(
            self,
            name: GaussianFieldName,
            field: ndarray,
            cross_section: CrossSection,
            grid_azimuth_angle: float,
            grid_size: GridSize,
            simulation_box_size: SimulationBoxSize,
    ) -> None: ...
    name: GaussianFieldName
    field: ndarray
    cross_section: CrossSection
    grid_azimuth_angle: float
    grid_size: GridSize
    simulation_box_size: SimulationBoxSize

class GaussianField:
    def __init__(
            self,
            name: Union[GaussianFieldName, str],
            variogram: Optional[Variogram] = None,
            trend: Optional[Trend] = None,
            seed: int = 0,
    ) -> None: ...
    name: GaussianFieldName
    variogram: Variogram
    trend: Trend
    seed: int
    def __getitem__(self, item): ...
    def _simulate(
            self,
            cross_section: CrossSection,
            grid_azimuth_angle: float,
            grid_size: GridSize,
            simulation_box_size: SimulationBoxSize,
            debug_level: Debug = Debug.OFF
    ) -> ndarray: ...
    def simulate(
            self,
            cross_section: CrossSection,
            grid_azimuth_angle: float,
            grid_size: GridSize,
            simulation_box_size: SimulationBoxSize,
            debug_level: Debug = Debug.OFF
    ) -> GaussianFieldSimulation: ...


class FmuProperty(Generic[T]):
    value: T
    updatable: bool
    def __init__(self, value: T, updatable: bool = False) -> None: ...
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...
    # def __lt__(self, other: FmuProperty) -> bool: ...
    # def __eq__(self, other: FmuProperty) -> bool: ...


class CrossSection:
    _type: CrossSectionType
    _relative_position: float
    def __init__(
            self,
            type: Union[CrossSectionType, str],
            relative_position: float
    ) -> None: ...

    @property
    def type(self) -> CrossSectionType: ...
    @type.setter
    def type(self, value: Union[str, CrossSectionType]) -> None: ...
    relative_position: float


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
    def as_list(self) -> List: ...


class Variogram:
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
        grid_azimuth_angle: float,
        projection: str,
        debug_level: Debug = Debug.OFF,
    ) -> Tuple[float64, float64, float64, float64]: ...

class APSGaussModel:
    debug_level: Debug
    num_gaussian_fields: int
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
        zoneNumber: int = 0,
        simBoxThickness: Number = 0
    ) -> None: ...
    def __interpretXMLTree(self, ET_Tree_zone): ...
    def XMLAddElement(self, parent: Element, fmu_attributes: List[str]) -> None: ...
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
    def getTrendModelObject(self, gfName: GaussianFieldName) -> Trend3D: ...
    def getVariogramType(self, gaussFieldName: GaussianFieldName) -> VariogramType: ...
    def getVariogramTypeNumber(self, gaussFieldName: GaussianFieldName) -> int: ...
    def getVertRange(self, gaussFieldName: GaussianFieldName) -> float: ...
    def _get_value_from_xml(self, property_name: str, xml_tree: Element) -> Tuple[Number, bool]: ...
    def get_variogram(
        self,
        gf: Element,
        gf_name: GaussianFieldName
    ) -> Tuple[Element, VariogramType]: ...
    def get_variogram_model(self, name: GaussianFieldName) -> Variogram: ...
    @staticmethod
    def get_variogram_type(
        variogram: Union[str, VariogramType, Element]
    ) -> VariogramType: ...
    def initialize(
        self,
        zone_number: int,
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
        grid_azimuth_angle: float,
        cross_section: CrossSection,
    ) -> List[GaussianField]: ...
    def calc2DVariogramFrom3DVariogram(
            self,
            name: GaussianFieldName,
            grid_azimuth_angle: float,
            projection: str,
    ) -> Tuple[float64, float64, float64, float64]: ...
    @staticmethod
    def _get_projection_parameters(
            cross_section_type,
            grid_size,
            simulation_box_size
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
