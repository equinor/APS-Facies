import os
from abc import ABC, abstractmethod
from contextlib import contextmanager

import numpy as np
import xtgeo

from src.algorithms.APSModel import APSModel
from src.utils.decorators import cached
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


class FmuModelChange(ABC):
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


class UpdateGridModelName(FmuModelChange):
    def __init__(self, aps_model, fmu_simulation_grid_name, **kwargs):
        self.aps_model = aps_model
        self._original = aps_model.grid_model_name
        self.fmu_simulation_grid_name = fmu_simulation_grid_name

    def before(self):
        self.aps_model.grid_model_name = self.fmu_simulation_grid_name

    def after(self):
        self.aps_model.grid_model_name = self._original


class UpdateFieldNamesInZones(FmuModelChange):
    def __init__(self, aps_model, project, **kwargs):
        self.aps_model = aps_model
        self.project = project
        self._original_names = self._get_field_names(aps_model)

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


class UpdateSimBoxThicknessInZones(FmuModelChange):
    def __init__(self, project, aps_model, fmu_simulation_grid_name, **kwargs):
        self.project = project
        self.aps_model: APSModel = aps_model
        self.ert_grid_name = fmu_simulation_grid_name

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

    @property
    @cached
    def layers_in_geo_model_zones(self):
        grid = get_grid(self.project, self.aps_model)
        layers = []
        for zonation, *reverse in grid.grid_indexer.zonation.values():
            layers.append(zonation.stop - zonation.start)
        return layers

    @property
    def zone_models(self):
        return self.aps_model.zone_models

    @property
    @cached
    def nz_fmu_box(self):
        _, _, nz = get_grid(self.project, self.ert_grid_name).simbox_indexer.dimensions
        return nz


@contextmanager
def fmu_aware_model_file(*, fmu_mode, **kwargs):
    """Updates the name of the grid, if necessary"""
    aps_model = kwargs['aps_model']
    model_file = kwargs['model_file']
    changes = FmuModelChanges([
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
