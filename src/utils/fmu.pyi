from abc import abstractmethod, ABC
from contextlib import contextmanager
from pathlib import Path
from typing import Union, overload, Callable, Optional, Generator, List, Tuple, Dict, Iterable

import numpy as np
import xtgeo

from src.algorithms import APSModel
from src.algorithms.APSGaussModel import GaussianField
from src.algorithms.APSZoneModel import APSZoneModel, Trend

from roxar import Project
from roxar.grids import Grid3D, GridModel


@overload
def get_exported_field_name(
        field:      Union[xtgeo.GridProperty, str],
        zone:       APSZoneModel,
        aps_model:  APSModel,
        project:    Project,
) -> str: ...
@overload
def get_exported_field_name(
        field:      Union[xtgeo.GridProperty, str],
        zone:       str,
) -> str: ...

def create_get_property(
        project:    Project,
        aps_model:  Optional[Union[APSModel, str]],
) -> Callable[[str, Optional[str]], xtgeo.GridProperty]:...

def get_export_location(
        project:    Project,
        create:     bool    = True,
) -> Path: ...

@overload
def get_grid(
        project:    Project,
        aps_model:  APSModel,
) -> Grid3D: ...
@overload
def get_grid(
        project:         Project,
        grid_model_name: str,
) -> Grid3D: ...

def layers_in_geo_model_zones(project: Project, aps_model: APSModel) -> List[int]: ...
def _get_grid_name(arg: Union[str, APSModel]) -> str: ...


class FmuModelChange(ABC):
    @abstractmethod
    def before(self) -> None: ...
    @abstractmethod
    def after(self) -> None: ...

class FmuModelChanges(list, FmuModelChange):
    def __init__(self, changes: List[FmuModelChange]): ...
    def before(self) -> None: ...
    def after(self) -> None: ...
    def __iter__(self) -> Iterable[FmuModelChange]: ...

class UpdateGridModelName(FmuModelChange):
    aps_model: APSModel
    fmu_simulation_grid_name: str

    def __init__(self, aps_model: APSModel, fmu_simulation_grid_name: str, **kwargs): ...
    def before(self) -> None: ...
    def after(self) -> None: ...


class UpdateFieldNamesInZones(FmuModelChange):
    aps_model: APSModel
    project: Project
    _original_names: Dict[Tuple[int, int, int], str]
    grid_model: GridModel
    zone_names: Dict[int. str]
    region_names: Dict[int, str]

    def __init__(self, aps_model: APSModel, project: Project, **kwargs): ...
    def before(self) -> None: ...
    def after(self) -> None: ...
    @staticmethod
    def _get_field_names(aps_model: APSModel) -> Dict[Tuple[int, int, int], str]: ...
    @staticmethod
    def _change_field_name(field_model: GaussianField, name: str) -> None: ...
    def _get_original_field_name(self, zone_model: APSZoneModel) -> str: ...
    def _get_fmu_field_name(self, zone_model: APSZoneModel, field_model: GaussianField) -> str: ...
    def _change_names(self, name_getter: Callable[[APSZoneModel, GaussianField, int], str]) -> None: ...


class UpdateRelativeSizeForEllipticConeTrend(FmuModelChange):
    project: Project
    aps_model: APSModel
    layers_in_geo_model_zones: List[int]
    nz_fmu_box: int
    _original_relative_sizes: Dict[int, Dict[str, float]]

    def __init__(self, project: Project, aps_model: APSModel, fmu_simulation_grid_name: str, **kwargs): ...
    def before(self) -> None: ...
    def after(self) -> None: ...

    def get_original_relative_size(self, zone_model: APSZoneModel, field_model: GaussianField) -> float: ...
    @classmethod
    def get_relative_sizes(cls, aps_model: APSModel) -> Dict[int, Dict[str, float]]: ...
    @staticmethod
    def has_elliptic_cone_trend(field: GaussianField) -> bool: ...


class UpdateSimBoxThicknessInZones(FmuModelChange):
    project: Project
    aps_model: APSModel
    _original: Dict[int, float]

    # Properties
    layers_in_geo_model_zones: List[int]
    nz_fmu_box: int
    ert_grid_name: str
    zone_models: List[APSZoneModel]

    def __init__(self, project: Project, aps_model: APSModel, fmu_simulation_grid_name: str, **kwargs): ...
    def before(self) -> None: ...
    def after(self) -> None: ...


@contextmanager
def fmu_aware_model_file(*, fmu_mode: bool, **kwargs) -> Generator[str]: ...

def find_zone_range(defined: np.ndarray) -> Tuple[int, int]: ...
