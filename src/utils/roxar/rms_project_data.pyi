# -*- coding: utf-8 -*-
import numpy as np
from enum import Enum
from typing import List, Dict, Union, Callable, NamedTuple, NewType, Type, Optional
from types import ModuleType

from src.algorithms.APSGaussModel import GaussianFieldName, SimulationBoxOrigin, GridSize, GaussianFieldSimulation

from roxar import Project
from roxar.grids import GridModel, GridModels, Properties, Property, BlockedWell, BlockedWellsSet, Grid3D
from roxar.zones import Zone, Zones

RoxarModule = ModuleType

class CodeName(NamedTuple):
    code: int
    name: str


TrendName = NewType('TrendName', str)
VariogramName = NewType('VariogramName', str)
GridName = NewType('GridName', str)
DirectionName = NewType('DirectionName', str)
OriginTypeName = NewType('OriginTypeName', str)

ZoneParameter = NewType('ZoneParameter', str)
RegionParameter = NewType('RegionParameter', str)
TrendParameter = NewType('TrendParameter', str)
ProbabilityCubeParameter = NewType('ProbabilityCubeParameter', str)


ZoneNumber = NewType('ZoneNumber', int)
ZoneName = NewType('ZoneName', str)

Average = NewType('Average', float)


def empty_if_none(func: Callable) -> Callable: ...
def _option_mapping() -> Dict[str, Type[Enum]]: ...


class RMSData:
    roxar:                              RoxarModule
    project:                            Project

    def __init__(
            self,
            roxar:                       RoxarModule,
            project:                     Project
    ): ...
    def is_discrete(
            self,
            _property
    ) -> bool: ...
    def is_continuous(
            self,
            _property
    ) -> bool: ...
    def get_grid_models(
            self
    ) -> GridModels: ...
    def get_grid_model(
            self,
            name: str
    ) -> GridModel: ...
    def get_grid(
            self,
            name:                        GridName,
            realization:                 Optional[int]                   = None
    ) -> Grid3D: ...
    def get_grid_model_names(
            self
    ) -> List[GridName]: ...
    def get_zone_parameters(
            self,
            grid_model_name:             GridName
    ) -> List[ZoneParameter]: ...
    def get_region_parameters(
            self,
            grid_model_name:             GridName
    ) -> List[RegionParameter]: ...
    def get_rms_trend_parameters(
            self,
            grid_model_name:             GridName
    ) -> List[TrendParameter]: ...
    def get_probability_cube_parameters(
            self,
            grid_model_name:             GridName
    ) -> List[ProbabilityCubeParameter]: ...
    def get_simulation_box_size(
            self,
            grid_model_name:             GridName
    ) -> SimulationBoxOrigin: ...
    def get_grid_size(
            self,
            grid_model_name:             GridName
    ) -> GridSize: ...
    def get_zones(
            self,
            grid_model_name:             GridName,
            zone_parameter:              ZoneParameter
    ) -> List[Dict]: ...
    def get_regions(
            self,
            grid_model_name:             GridName,
            zone_name:                   ZoneName,
            region_parameter:            RegionParameter,
    ) -> Properties: ...
    def is_zone_parameter(
            self,
            param:                       Property
    ) -> bool: ...
    def is_region_parameter(
            self,
            param:                       Property
    ) -> bool: ...
    def is_trend_parameter(
            self,
            param:                       Property
    ) -> bool: ...
    def is_probability_cube(
            self,
            param:                       Property
    ) -> bool: ...
    def _get_parameter_names(
            self,
            grid_model_name:             GridName,
            check:                       Callable
    ) -> List[str]: ...
    def _get_blocked_well_set(
            self,
            grid_model_name:             GridName
    ) -> BlockedWellsSet: ...
    def get_blocked_well_logs(
            self,
            grid_model_name:             GridName,
            blocked_well_name:           str
    ) -> List[str]: ...
    def get_blocked_well(
            self,
            grid_model_name:             GridName,
            blocked_well_name:           str
    ) -> BlockedWell: ...
    def calculate_average_of_probability_cube(
            self,
            grid_model_name:             GridName,
            probability_cube_parameters: List[ProbabilityCubeParameter],
            zones:                       Optional[List[ZoneNumber]]      = None
    ) -> Dict[ProbabilityCubeParameter, Average]: ...
    def get_blocked_well_set_names(
            self,
            grid_model_name:             str
    ) -> List[str]: ...
    def get_facies_table_from_blocked_well_log(
            self,
            grid_model_name:             str,
            bw_name:                     str,
            facies_log_name:             str
    ) -> Dict[str, int]: ...
    @staticmethod
    def get_constant(
            _property:                   str,
            _type:                       str
    ) -> Dict[str, float]: ...
    @staticmethod
    def get_options(
            _type:                       str
    ) -> Union[List[VariogramName], List[TrendName], List[DirectionName], List[OriginTypeName]]: ...
    @staticmethod
    def get_code_names(
            _property:                   Property
    ) -> List[CodeName]: ...
    @staticmethod
    def simulate_realization(fields: List[Dict], specification): ...
    @staticmethod
    def get_truncation_map_polygons(
            specification
    ): ...
    @staticmethod
    def simulate_gaussian_field(
            name:                        Union[GaussianFieldName, str],
            variogram:                   Dict,
            trend:                       Dict,
            settings:                    Optional[Dict]
    ) -> List[List[float]]: ...
    @staticmethod
    def is_aps_model_valid(encoded_xml): ...
    @staticmethod
    def _simulate_gaussian_field(field: Dict) -> GaussianFieldSimulation: ...

