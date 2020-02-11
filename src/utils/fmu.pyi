from abc import abstractmethod, ABCMeta
from contextlib import contextmanager
from pathlib import Path
from typing import Union, overload, Callable, Optional, Generator, List, Tuple, Dict, Iterable, Literal

import numpy as np
import xtgeo

from src.algorithms.APSModel import APSModel
from src.algorithms.APSGaussModel import GaussianField
from src.algorithms.APSZoneModel import APSZoneModel

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

def get_ert_location() -> Path: ...
def get_export_location(
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

def _get_grid_name(arg: Union[str, APSModel]) -> str: ...


class FmuModelChange(metaclass=ABCMeta):
    @abstractmethod
    def before(self) -> None: ...
    @abstractmethod
    def after(self) -> None: ...

class UpdateModel(FmuModelChange, metaclass=ABCMeta):
    aps_model: APSModel
    zone_models: List[APSZoneModel]
    def __init__(self, aps_model: APSModel, **kwargs): ...

class SimBoxDependentUpdate(UpdateModel, metaclass=ABCMeta):
    project: Project
    ert_grid_name: str

    # Properties
    layers_in_geo_model_zones: List[int]
    nz_fmu_box: int

    def __init__(self, *, project: Project, fmu_simulation_grid_name: str, **kwargs): ...


class TrendUpdate(SimBoxDependentUpdate, metaclass=ABCMeta):
    _original_values: Dict[int, Dict[str, float]]
    update_message: Optional[str]

    def before(self) -> None: ...
    def after(self) -> None: ...

    @abstractmethod
    def update_trend(self, zone_model: APSZoneModel, field_model: GaussianField) -> None: ...
    @abstractmethod
    def restore_trend(self, zone_model: APSZoneModel, field_model: GaussianField) -> None: ...
    @abstractmethod
    def get_original_values(self, aps_model: APSModel) -> Dict[int, Dict[str, float]]: ...
    def get_original_value(self, zone_model: APSZoneModel, field_model: GaussianField) -> float: ...
    @abstractmethod
    def has_appropriate_trend(self, field: GaussianField) -> bool: ...


class FmuModelChanges(list, FmuModelChange):
    def __init__(self, changes: List[FmuModelChange]): ...
    def before(self) -> None: ...
    def after(self) -> None: ...
    def __iter__(self) -> Iterable[FmuModelChange]: ...

class UpdateGridModelName(UpdateModel):
    fmu_simulation_grid_name: str

    def __init__(self, fmu_simulation_grid_name: str, **kwargs): ...
    def before(self) -> None: ...
    def after(self) -> None: ...


class UpdateFieldNamesInZones(UpdateModel):
    project: Project
    _original_names: Dict[Tuple[int, int, int], str]
    grid_model: GridModel
    zone_names: Dict[int, str]
    region_names: Dict[int, str]

    def __init__(self, project: Project, **kwargs): ...
    def before(self) -> None: ...
    def after(self) -> None: ...
    @staticmethod
    def _get_field_names(aps_model: APSModel) -> Dict[Tuple[int, int, int], str]: ...
    @staticmethod
    def _change_field_name(field_model: GaussianField, name: str) -> None: ...
    def _get_original_field_name(self, zone_model: APSZoneModel, field_index: int) -> str: ...
    def _get_fmu_field_name(self, zone_model: APSZoneModel, field_model: GaussianField) -> str: ...
    def _change_names(self, name_getter: Callable[[APSZoneModel, GaussianField, int], str]) -> None: ...


class UpdateRelativeSizeForEllipticConeTrend(TrendUpdate):
    def update_trend(self, zone_model: APSZoneModel, field_model: GaussianField) -> None: ...
    def restore_trend(self, zone_model: APSZoneModel, field_model: GaussianField) -> None: ...

    def get_original_values(self, aps_model: APSModel) -> Dict[int, Dict[str, float]]: ...
    def has_appropriate_trend(self, field: GaussianField) -> bool: ...


class UpdateSimBoxThicknessInZones(UpdateModel):
    project: Project
    _original: Dict[int, float]

    # Properties
    layers_in_geo_model_zones: List[int]
    nz_fmu_box: int
    ert_grid_name: str
    zone_models: List[APSZoneModel]

    def __init__(self, project: Project, fmu_simulation_grid_name: str, **kwargs): ...
    def before(self) -> None: ...
    def after(self) -> None: ...


class UpdateRelativePositionOfTrends(TrendUpdate):
    update_message: str

    def update_trend(self, zone_model: APSZoneModel, field_model: GaussianField) -> None: ...
    def restore_trend(self, zone_model: APSZoneModel, field_model: GaussianField) -> None: ...

    def has_appropriate_trend(self, field: GaussianField) -> bool: ...
    def get_original_values(self, aps_model: APSModel) -> Dict[int, Dict[str, float]]: ...


class UpdateTrends(FmuModelChanges):
    def __init__(self, **kwargs): ...


Handedness = Literal["left", "right"]


class UpdateGridOrientation(FmuModelChange):
    _grid: xtgeo.Grid
    _original: Handedness

    def __init__(self, *, project: Project, aps_model: APSModel, **kwargs): ...
    def turn_grid(self, handedness: Handedness) -> None: ...
    def before(self) -> None: ...
    def after(self) -> None: ...


@contextmanager
def fmu_aware_model_file(*, fmu_mode: bool, **kwargs) -> Generator[str]: ...

def find_zone_range(defined: np.ndarray) -> Tuple[int, int]: ...
