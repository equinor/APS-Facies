import os
from abc import ABCMeta, abstractmethod
from contextlib import contextmanager
from collections import defaultdict
from typing import Dict

import numpy as np
import xtgeo

from src.algorithms.APSModel import APSModel
from src.algorithms.APSZoneModel import Conform
from src.algorithms.Trend3D import Trend3D_elliptic_cone, ConicTrend
from src.utils.constants.simple import OriginType
from src.utils.decorators import cached
from src.utils.exceptions.zone import MissingConformityException
from src.utils.roxar.generalFunctionsUsingRoxAPI import get_project_dir


def get_exported_field_name(field, zone, aps_model=None, project=None):
    if isinstance(zone, str):
        zone_name = zone
    else:
        required = {
            'aps_model': aps_model,
            'project': project
        }
        if any(arg is None for arg in required.values()):
            missing = [arg for arg, value in required.items() if value is None]
            raise TypeError(
                '{func_name}() missing, {num_args} required positional argument{plural}: {arguments}'.format(
                    func_name=get_exported_field_name.__name__,
                    num_args=len(missing),
                    plural='s' if len(missing) > 1 else '',
                    arguments=' and '.join("'{}'".format(arg) for arg in missing)
                )
            )
        grid = get_grid(project, aps_model)
        zone_name = grid.zone_names[zone.zone_number - 1]  # Zones are 1-indexed
    if isinstance(field, str):
        name = field
    else:
        name = field.name
    return 'aps_{zone_name}_{field_name}.grdecl'.format(
        zone_name=zone_name,
        field_name=name,
    )


def create_get_property(project, aps_model=None):
    def get_property(name, grid_name=None):
        if grid_name is None:
            if aps_model is None:
                raise ValueError("'aps_model' must be given, if 'grid_name' is not given")
            grid_name = _get_grid_name(aps_model)
        return xtgeo.gridproperty_from_roxar(project, grid_name, name, project.current_realisation)
    return get_property


def get_export_location(project, create=True):
    field_location = get_project_dir(project) / '..' / 'output' / 'aps'
    if create and not field_location.exists():
        os.makedirs(field_location, exist_ok=True)
    return field_location


def get_grid(project, aps_model):
    return project.grid_models[_get_grid_name(aps_model)].get_grid(project.current_realisation)


def _get_grid_name(arg):
    if isinstance(arg, str):
        grid_name = arg
    else:
        grid_name = arg.grid_model_name
    return grid_name


class FmuModelChange(metaclass=ABCMeta):
    @abstractmethod
    def before(self):
        pass

    @abstractmethod
    def after(self):
        pass


class FmuModelChanges(list, FmuModelChange):
    def __init__(self, changes):
        super(FmuModelChanges, self).__init__(changes)

    def before(self):
        for change in self:
            change.before()

    def after(self):
        for change in reversed(self):
            change.after()


class UpdateModel(FmuModelChange, metaclass=ABCMeta):
    def __init__(self, *, aps_model, **kwargs):
        self.aps_model = aps_model

    @property
    def zone_models(self):
        return self.aps_model.zone_models


class SimBoxDependentUpdate(UpdateModel, metaclass=ABCMeta):
    def __init__(self, *, project, fmu_simulation_grid_name, **kwargs):
        super().__init__(**kwargs)
        self.project = project
        self.ert_grid_name = fmu_simulation_grid_name

    @property
    @cached
    def layers_in_geo_model_zones(self):
        grid = get_grid(self.project, self.aps_model)
        layers = []
        for zonation, *reverse in grid.grid_indexer.zonation.values():
            layers.append(zonation.stop - zonation.start)
        return layers

    @property
    @cached
    def nz_fmu_box(self):
        _, _, nz = get_grid(self.project, self.ert_grid_name).simbox_indexer.dimensions
        return nz


class TrendUpdate(SimBoxDependentUpdate):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._original_values = self.get_original_values(self.aps_model)

    def before(self):
        necessary = False
        for zone_model in self.zone_models:
            for field in zone_model.gaussian_fields:
                if self.has_appropriate_trend(field):
                    necessary = True
                    self.update_trend(zone_model, field)
        if necessary and self.update_message:
            print(self.update_message)

    def after(self):
        for zone_model in self.zone_models:
            for field in zone_model.gaussian_fields:
                if self.has_appropriate_trend(field):
                    self.restore_trend(zone_model, field)

    def get_original_value(self, zone_model, field_model):
        return self._original_values[zone_model.zone_number][field_model.name]

    @abstractmethod
    def update_trend(self, zone_model, field_model):
        raise NotImplementedError

    @abstractmethod
    def restore_trend(self, zone_model, field_model):
        raise NotImplementedError

    @abstractmethod
    def get_original_values(self, aps_model):
        raise NotImplementedError

    @abstractmethod
    def has_appropriate_trend(self, field):
        raise NotImplementedError

    @property
    def update_message(self):
        return None


class UpdateGridModelName(UpdateModel):
    def __init__(self, fmu_simulation_grid_name, **kwargs):
        super().__init__(**kwargs)
        self._original = self.aps_model.grid_model_name
        self.fmu_simulation_grid_name = fmu_simulation_grid_name

    def before(self):
        self.aps_model.grid_model_name = self.fmu_simulation_grid_name

    def after(self):
        self.aps_model.grid_model_name = self._original


class UpdateFieldNamesInZones(UpdateModel):
    def __init__(self, project, **kwargs):
        super().__init__(**kwargs)
        self.project = project
        self._original_names = self._get_field_names(self.aps_model)

    @staticmethod
    def _get_field_names(aps_model):
        names = {}
        for zone_model in aps_model.zone_models:
            for i, field in enumerate(zone_model.gaussian_fields):
                names[(zone_model.zone_number, zone_model.region_number, i)] = field.name
        return names

    def _get_original_field_name(self, zone_model, field_index):
        return self._original_names[(zone_model.zone_number, zone_model.region_number, field_index)]

    @property
    @cached
    def grid_model(self):
        return self.project.grid_models[self.aps_model.grid_model_name]

    @property
    @cached
    def zone_names(self):
        return self.grid_model.properties[self.aps_model.zone_parameter].code_names

    @property
    @cached
    def region_names(self):
        return self.grid_model.properties[self.aps_model.region_parameter].code_names

    def _get_fmu_field_name(self, zone_model, field_model):
        zone_name = self.zone_names[zone_model.zone_number]
        region_name = ''
        if zone_model.uses_region:
            region_name = self.region_names[zone_model.region_number]
        field_name = 'aps_' + zone_name
        if region_name:
            field_name += '_' + region_name
        field_name += '_' + field_model.name
        return field_name

    @staticmethod
    def _change_field_name(field_model, name):
        field_model.name = name
        field_model.variogram.name = name
        field_model.trend.name = name

    def before(self):
        self._change_names(
            name_getter=lambda zone_model, field_model, field_index: self._get_fmu_field_name(zone_model, field_model),
        )

    def after(self):
        self._change_names(
            name_getter=lambda zone_model, field_model, field_index: self._get_original_field_name(zone_model, field_index),
        )

    def _change_names(self, name_getter):
        aps_model: APSModel = self.aps_model
        mapping = {}
        for zone_model in aps_model.zone_models:
            for i, field in enumerate(zone_model.gaussian_fields):
                name = name_getter(zone_model, field, i)
                mapping[field.name] = name
                self._change_field_name(field, name)
            rule = zone_model.truncation_rule
            rule.names_of_gaussian_fields = [mapping[name] for name in rule.names_of_gaussian_fields]


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
    def update_trend(self, zone_model, field_model):
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

    def restore_trend(self, zone_model, field_model):
        field_model.trend.model.relative_size_of_ellipse = self.get_original_value(zone_model, field_model)

    def get_original_values(self, aps_model):
        relative_sizes: Dict[int, Dict[str, float]] = defaultdict(dict)
        for zone_model in aps_model.zone_models:
            for field in zone_model.gaussian_fields:
                trend = field.trend
                if self.has_appropriate_trend(field):
                    relative_sizes[zone_model.zone_number][field.name] = trend.model.relative_size_of_ellipse.value
        return relative_sizes

    def has_appropriate_trend(self, field):
        return (
            field.trend.use_trend
            and isinstance(field.trend.model, Trend3D_elliptic_cone)
        )


class UpdateRelativePositionOfTrends(TrendUpdate):
    def update_trend(self, zone_model, field_model):
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
    def update_message(self):
        return 'Updating the location of relative trends'

    def restore_trend(self, zone_model, field_model):
        field_model.trend.model.origin.z = self.get_original_value(zone_model, field_model)

    def has_appropriate_trend(self, field):
        trend = field.trend.model
        return isinstance(trend, ConicTrend) and trend.origin_type == OriginType.RELATIVE

    def get_original_values(self, aps_model):
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


@contextmanager
def fmu_aware_model_file(*, fmu_mode, **kwargs):
    """Updates the name of the grid, if necessary"""
    aps_model = kwargs['aps_model']
    model_file = kwargs['model_file']
    changes = FmuModelChanges([
        UpdateTrends(**kwargs),
        UpdateSimBoxThicknessInZones(**kwargs),
        UpdateFieldNamesInZones(**kwargs),
        UpdateGridModelName(**kwargs),
    ])
    if fmu_mode:
        changes.before()
    try:
        aps_model.dump(model_file)
        yield model_file
    finally:
        if fmu_mode:
            changes.after()
        aps_model.dump(model_file)


def find_zone_range(defined):
    _, _, loc = np.where(defined == np.True_)
    return loc.min(), loc.max()
