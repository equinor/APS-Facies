#!/bin/env python
# -*- coding: utf-8 -*-
import os
from abc import ABCMeta, abstractmethod
from contextlib import contextmanager
from collections import defaultdict
from warnings import warn
from typing import Dict, Tuple, Optional, Union, Callable, List, TYPE_CHECKING, ContextManager
from pathlib import Path

import numpy as np
import xtgeo
from xtgeo.grid3d import GridProperty

from roxar import Project
from roxar.grids import Grid3D, GridModel
from aps.algorithms.APSGaussModel import GaussianField
from aps.algorithms.APSModel import APSModel
from aps.algorithms.APSZoneModel import Conform, APSZoneModel
from aps.algorithms.trend import Trend3D_elliptic_cone, ConicTrend
from aps.utils.constants.simple import OriginType, Debug, TrendType
from aps.utils.decorators import cached
from aps.utils.exceptions.zone import MissingConformityException


if TYPE_CHECKING:
    from typing import Literal
    # Literal was introduced in Python 3.8
    Handedness = Literal["left", "right"]


def create_get_property(
        project: Project,
        aps_model: Optional[Union[APSModel, str]],
) -> Callable[[str, Optional[str]], GridProperty]:
    def get_property(name, grid_name=None):
        if grid_name is None:
            if aps_model is None:
                raise ValueError("'aps_model' must be given, if 'grid_name' is not given")
            grid_name = _get_grid_name(aps_model)
        properties = project.grid_models[grid_name].properties
        if name in properties:
            if properties[name].is_empty(project.current_realisation):
                raise ValueError(f'The parameter {name} is empty in grid model {grid_name}')
        else:
            raise ValueError(f'The parameter  {name} does not exist in grid model {grid_name}')
        return xtgeo.gridproperty_from_roxar(project, grid_name, name, project.current_realisation)

    return get_property


def get_ert_location() -> Path:
    return Path(os.getcwd())


def get_top_location() -> Path:
    top_location = get_ert_location() / '..' / '..'
    return Path(top_location)


def is_initial_iteration(debug_level: Debug = Debug.OFF) -> bool:
    '''
    Check if folder with name equal to a non-negative integer exists.
    If a folder with name 0 is found or no folder with integer exists,
    the APS mode is to simulate and export GRF files to be used in ERT
    and this function return True.
    If a folder with name 1 or 2 or 3 or ... MAXITER is found,
    the APS mode is import updated GRF from ERT and this function return False
    '''
    MAXITER = 100
    toplevel = Path("../..").absolute()
    iterfolder = -1
    for folder in range(MAXITER):
        if (toplevel / str(folder)).exists():
            iterfolder = folder
            break
    return iterfolder <= 0

def get_export_location(create: bool = True) -> Path:
    field_location = get_ert_location() / '..' / 'output' / 'aps'
    if create and not field_location.exists():
        os.makedirs(field_location, exist_ok=True)
    return field_location


def get_grid(
        project:    Project,
        aps_model:  Union[APSModel, str],
) -> Grid3D:
    return project.grid_models[_get_grid_name(aps_model)].get_grid(project.current_realisation)


def _get_grid_name(arg: Union[str, APSModel]) -> str:
    if isinstance(arg, str):
        grid_name = arg
    else:
        grid_name = arg.grid_model_name
    return grid_name


class FmuModelChange(metaclass=ABCMeta):
    @abstractmethod
    def before(self) -> None:
        pass

    @abstractmethod
    def after(self) -> None:
        pass


class FmuModelChanges(list, FmuModelChange):
    def __init__(self, changes: List[FmuModelChange]):
        super(FmuModelChanges, self).__init__(changes)

    def before(self):
        for change in self:
            change.before()

    def after(self):
        for change in reversed(self):
            change.after()


class UpdateModel(FmuModelChange, metaclass=ABCMeta):
    def __init__(self, *, aps_model: APSModel, **kwargs):
        self.aps_model = aps_model

    @property
    def zone_models(self) -> List[APSZoneModel]:
        return self.aps_model.zone_models


class SimBoxDependentUpdate(UpdateModel, metaclass=ABCMeta):
    def __init__(self, *, project: Project, fmu_simulation_grid_name: str, **kwargs):
        super().__init__(**kwargs)
        self.project = project
        self.ert_grid_name = fmu_simulation_grid_name

    @property
    @cached
    def layers_in_geo_model_zones(self) -> List[int]:
        grid = get_grid(self.project, self.aps_model)
        layers = []
        for zonation, *reverse in grid.grid_indexer.zonation.values():
            layers.append(zonation.stop - zonation.start)
        return layers

    @property
    @cached
    def nz_fmu_box(self) -> int:
        _, _, nz = get_grid(self.project, self.ert_grid_name).simbox_indexer.dimensions
        return nz


class TrendUpdate(SimBoxDependentUpdate):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._original_values = self.get_original_values(self.aps_model)

    def before(self) -> None:
        necessary = False
        for zone_model in self.zone_models:
            for field in zone_model.gaussian_fields:
                if self.has_appropriate_trend(field):
                    necessary = True
                    self.update_trend(zone_model, field)
        if necessary and self.update_message:
            print(self.update_message)

    def after(self) -> None:
        for zone_model in self.zone_models:
            for field in zone_model.gaussian_fields:
                if self.has_appropriate_trend(field):
                    self.restore_trend(zone_model, field)

    def get_original_value(self, zone_model: APSZoneModel, field_model: GaussianField) -> float:
        return self._original_values[zone_model.zone_number][field_model.name]

    @abstractmethod
    def update_trend(self, zone_model: APSZoneModel, field_model: GaussianField) -> None:
        raise NotImplementedError

    @abstractmethod
    def restore_trend(self, zone_model: APSZoneModel, field_model: GaussianField) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_original_values(self, aps_model: APSModel) -> Dict[int, Dict[str, float]]:
        raise NotImplementedError

    @abstractmethod
    def has_appropriate_trend(self, field: GaussianField) -> bool:
        raise NotImplementedError

    @property
    def update_message(self) -> Optional[str]:
        return None


class UpdateGridModelName(UpdateModel):
    def __init__(self, fmu_simulation_grid_name: str, **kwargs):
        super().__init__(**kwargs)
        self._original = self.aps_model.grid_model_name
        self.fmu_simulation_grid_name = fmu_simulation_grid_name

    def before(self):
        self.aps_model.grid_model_name = self.fmu_simulation_grid_name

    def after(self):
        self.aps_model.grid_model_name = self._original


class UpdateFieldNamesInZones(UpdateModel):
    def __init__(self, project: Project, **kwargs):
        super().__init__(**kwargs)
        self.project = project
        self._original_names = self._get_field_names(self.aps_model)
        self._original_trend_param_names = self._get_trend_param_names(self.aps_model)

    @staticmethod
    def _get_field_names(aps_model: APSModel) -> Dict[Tuple[int, int, int], str]:
        names = {}
        for zone_model in aps_model.zone_models:
            for i, field in enumerate(zone_model.gaussian_fields):
                names[(zone_model.zone_number, zone_model.region_number, i)] = field.name
        return names

    @staticmethod
    def _get_trend_param_names(aps_model: APSModel) -> Dict[Tuple[int, int, int], str]:
        names = {}
        for zone_model in aps_model.zone_models:
            for i, field in enumerate(zone_model.gaussian_fields):
                if field.trend.use_trend:
                    trend_model = field.trend.model
                    if trend_model.type == TrendType.RMS_PARAM:
                        trend_param_name = trend_model.trend_parameter_name
                        names[(zone_model.zone_number, zone_model.region_number, i)] = trend_param_name
        return names

    def _get_original_field_name(self, zone_model: APSZoneModel, field_index: int) -> str:
        return self._original_names[(zone_model.zone_number, zone_model.region_number, field_index)]

    def _get_original_trend_param_name(self, zone_model: APSZoneModel, field_index: int) -> str:
        return self._original_trend_param_names[(zone_model.zone_number, zone_model.region_number, field_index)]

    @property
    @cached
    def grid_model(self) -> GridModel:
        return self.project.grid_models[self.aps_model.grid_model_name]

    @property
    @cached
    def zone_names(self) -> Dict[int, str]:
        return self.grid_model.properties[self.aps_model.zone_parameter].code_names

    @property
    @cached
    def region_names(self) -> Dict[int, str]:
        return self.grid_model.properties[self.aps_model.region_parameter].code_names

    def _get_fmu_field_name(self, zone_model: APSZoneModel, field_model: GaussianField) -> str:
        zone_name = self.zone_names[zone_model.zone_number]
        region_name = ''
        if zone_model.uses_region:
            region_name = self.region_names[zone_model.region_number]
        field_name = 'aps_' + zone_name
        if region_name:
            field_name += '_' + region_name
        field_name += '_' + field_model.name
        return field_name

    def _get_fmu_trend_param_name(self, zone_model: APSZoneModel, field_model: GaussianField) -> str:
        zone_name = self.zone_names[zone_model.zone_number]
        region_name = ''
        if zone_model.uses_region:
            region_name = self.region_names[zone_model.region_number]
        field_name = 'aps_' + zone_name
        if region_name:
            field_name += '_' + region_name

        if field_model.trend.use_trend:
            trend_model = field_model.trend.model
            if trend_model.type == TrendType.RMS_PARAM:
                trend_param_name = trend_model.trend_parameter_name
                field_name += '_' + trend_param_name
                return field_name
        return None

    @staticmethod
    def _change_field_name(field_model: GaussianField, name: str) -> None:
        field_model.name = name
        field_model.variogram.name = name
        field_model.trend.name = name

    @staticmethod
    def _change_trend_param_name(field_model: GaussianField, name: str) -> None:
        if not field_model.trend.use_trend:
            raise ValueError('Internal error. Use trend should be true ')
        if field_model.trend.model.type != TrendType.RMS_PARAM:
            raise ValueError('Internal error. Trend type should be RMS_PARAM here')

        field_model.trend.model.trend_parameter_name = name


    def before(self):
        self._change_names(
            name_getter=lambda zone_model, field_model, field_index: self._get_fmu_field_name(zone_model, field_model),
        )
        self._change_name_of_trend_params(
            name_getter=lambda zone_model, field_model, field_index: self._get_fmu_trend_param_name(zone_model, field_model),
        )

    def after(self):
        self._change_names(
            name_getter=lambda zone_model, field_model, field_index: self._get_original_field_name(zone_model,
                                                                                                   field_index),
        )
        self._change_name_of_trend_params(
            name_getter=lambda zone_model, field_model, field_index: self._get_original_trend_param_name(zone_model,
                                                                                                   field_index),
        )

    def _change_names(self, name_getter: Callable[[APSZoneModel, GaussianField, int], str]) -> None:
        aps_model: APSModel = self.aps_model
        mapping = {}
        for zone_model in aps_model.zone_models:
            for i, field in enumerate(zone_model.gaussian_fields):
                name = name_getter(zone_model, field, i)
                mapping[field.name] = name
                self._change_field_name(field, name)
            rule = zone_model.truncation_rule
            rule.names_of_gaussian_fields = [mapping[name] for name in rule.names_of_gaussian_fields]


    def _change_name_of_trend_params(self, name_getter: Callable[[APSZoneModel, GaussianField, int], str]) -> None:
        aps_model: APSModel = self.aps_model
        mapping = {}
        for zone_model in aps_model.zone_models:
            for i, field in enumerate(zone_model.gaussian_fields):
                if field.trend.use_trend:
                    trend_model = field.trend.model
                    if trend_model.type == TrendType.RMS_PARAM:
                        trend_param_name = trend_model.trend_parameter_name
                        name = name_getter(zone_model, field, i)
                        mapping[trend_param_name] = name
                        self._change_trend_param_name(field, name)


class UpdateSimBoxThicknessInZones(SimBoxDependentUpdate):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._original = {
            zone_model.zone_number: zone_model.sim_box_thickness
            for zone_model in self.zone_models
        }

    def before(self):
        for zone_model in self.zone_models:
            nz_geo_grid = self.layers_in_geo_model_zones[zone_model.zone_number - 1]
            zone_model.sim_box_thickness = zone_model.sim_box_thickness * self.nz_fmu_box / nz_geo_grid

    def after(self):
        for zone_model in self.zone_models:
            zone_model.sim_box_thickness = self._original[zone_model.zone_number]


class UpdateRelativeSizeForEllipticConeTrend(TrendUpdate):
    def update_trend(self, zone_model: APSZoneModel, field_model: GaussianField) -> None:
        nz_fmu_box = self.nz_fmu_box
        nz_geo_grid = self.layers_in_geo_model_zones[zone_model.zone_number - 1]
        original_relative_size = self.get_original_value(zone_model, field_model)
        if zone_model.grid_layout in [Conform.Proportional, Conform.TopConform]:
            fmu_relative_size = original_relative_size / (
                    1 + (nz_fmu_box - nz_geo_grid) * (1 - original_relative_size) / nz_geo_grid
            )
        elif zone_model.grid_layout in [Conform.BaseConform]:
            if original_relative_size >= 1 - nz_geo_grid / nz_fmu_box:
                fmu_relative_size = 1 - nz_fmu_box * (1 - original_relative_size) / nz_geo_grid
            else:
                fmu_relative_size = 0.001
        else:
            raise NotImplementedError('{} is not supported'.format(zone_model.grid_layout))
        field_model.trend.model.relative_size_of_ellipse = fmu_relative_size

    def restore_trend(self, zone_model: APSZoneModel, field_model: GaussianField) -> None:
        field_model.trend.model.relative_size_of_ellipse = self.get_original_value(zone_model, field_model)

    def get_original_values(self, aps_model: APSModel) -> Dict[int, Dict[str, float]]:
        relative_sizes: Dict[int, Dict[str, float]] = defaultdict(dict)
        for zone_model in aps_model.zone_models:
            for field in zone_model.gaussian_fields:
                trend = field.trend
                if self.has_appropriate_trend(field):
                    relative_sizes[zone_model.zone_number][field.name] = trend.model.relative_size_of_ellipse.value
        return relative_sizes

    def has_appropriate_trend(self, field: GaussianField) -> bool:
        return (
                field.trend.use_trend
                and isinstance(field.trend.model, Trend3D_elliptic_cone)
        )


class UpdateRelativePositionOfTrends(TrendUpdate):
    def update_trend(self, zone_model: APSZoneModel, field_model: GaussianField) -> None:
        nz_fmu = self.nz_fmu_box
        indexer = get_grid(self.project, self.aps_model.grid_model_name).simbox_indexer

        zonation, *_reverse = indexer.zonation[zone_model.zone_number - 1]
        nz_zone = zonation.stop - zonation.start

        trend = field_model.trend.model
        if self.has_appropriate_trend(field_model):
            z_original = float(trend.origin.z)
            # Update trend
            if zone_model.grid_layout is None:
                raise MissingConformityException(zone_model)
            if zone_model.grid_layout in [Conform.TopConform, Conform.Proportional]:
                trend.origin.z = z_original * nz_zone / nz_fmu
            elif zone_model.grid_layout in [Conform.BaseConform]:
                trend.origin.z = 1 - (nz_zone * (1 - z_original) / nz_fmu)
            else:
                raise NotImplementedError('{} is not supported'.format(zone_model.grid_layout))

    @property
    def update_message(self) -> str:
        return '- Updating the location of relative trends for ERTBOX simulation'

    def restore_trend(self, zone_model: APSZoneModel, field_model: GaussianField) -> None:
        field_model.trend.model.origin.z = self.get_original_value(zone_model, field_model)

    def has_appropriate_trend(self, field: GaussianField) -> bool:
        trend = field.trend.model
        return isinstance(trend, ConicTrend) and trend.origin_type == OriginType.RELATIVE

    def get_original_values(self, aps_model: APSModel) -> Dict[int, Dict[str, float]]:
        relative_depths = defaultdict(dict)
        for zone_model in aps_model.zone_models:
            for field in zone_model.gaussian_fields:
                if self.has_appropriate_trend(field):
                    relative_depths[zone_model.zone_number][field.name] = field.trend.model.origin.z
        return relative_depths


class UpdateTrends(FmuModelChanges):
    def __init__(self, **kwargs):
        super(FmuModelChanges, self).__init__([
            UpdateRelativeSizeForEllipticConeTrend(**kwargs),
            UpdateRelativePositionOfTrends(**kwargs),
        ])


class UpdateGridOrientation(FmuModelChange):
    def __init__(self, *, project: Project, aps_model: APSModel, **kwargs):
        grid = get_grid(project, aps_model)
        self.skip = grid.has_dual_index_system
        if self.skip:
            warn(f'Ensuring correct rotation of the grid, is not supported for grids with reverse faults, yet')
        else:
            self._grid = xtgeo.grid_from_roxar(project, aps_model.grid_model_name, project.current_realisation)
            self._original = self._grid.ijk_handedness

    def turn_grid(self, handedness: 'Handedness') -> None:
        if self._grid.ijk_handedness != handedness:
            self._grid.reverse_row_axis()

    def before(self):
        # nrlib uses a right-handed coordinate system
        if not self.skip:
            self.turn_grid('right')

    def after(self):
        if not self.skip:
            self.turn_grid(self._original)


@contextmanager
def fmu_aware_model_file(*, fmu_mode: bool, **kwargs) -> ContextManager[str]:
    """Updates the name of the grid, if necessary"""
    model_file = kwargs['model_file']
    debug_level = kwargs['debug_level']
    # Instantiate the APS model anew, as it may have been modified by `global_variables`
    aps_model = kwargs['aps_model'] = APSModel(model_file)

    changes = FmuModelChanges([
        UpdateTrends(**kwargs),
        UpdateSimBoxThicknessInZones(**kwargs),
        UpdateFieldNamesInZones(**kwargs),
        UpdateGridModelName(**kwargs),
    ])
    if fmu_mode:
        print('FMU mode. Update APS model parameters')
        changes.before()
        if debug_level >= Debug.VERY_VERBOSE:
            filename = "debug_model_with_updated_param.xml"
            print(f"--- Write model file for debug purpose: {filename} ")
            aps_model.dump(filename)

    try:
        aps_model.dump(model_file)
        yield model_file
    finally:
        if fmu_mode:
            changes.after()
        aps_model.dump(model_file)
        if debug_level >= Debug.VERY_VERBOSE:
            filename = "debug_model_with original_param.xml"
            print(f"--- Write model file for debug purpose: {filename} ")
            aps_model.dump(filename)



def find_zone_range(defined: np.ndarray) -> Tuple[int, int]:
    _, _, loc = np.where(defined == np.True_)
    return loc.min(), loc.max()
