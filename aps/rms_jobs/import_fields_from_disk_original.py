#!/bin/env python
# -*- coding: utf-8 -*-
# This module is used in FMU workflows to import gaussian field values from disk into APS.
# Here we can assume that the project.current_realisation = 0 always since FMU ONLY run with one
# realization in the RMS project and should have shared grid and shared parameters only.
from collections import defaultdict
from pathlib import Path

import numpy as np
import xtgeo

from aps.algorithms.APSModel import APSModel
from aps.algorithms.APSZoneModel import Conform
from aps.utils.exceptions.zone import MissingConformityException
from aps.utils.fmu import create_get_property, find_zone_range, get_ert_location
from aps.utils.constants.simple import Debug, GridModelConstants
from aps.utils.methods import get_debug_level
from aps.utils.roxar.grid_model import create_zone_parameter


def extract_values(field_values, defined, zone):
    values = np.zeros(defined.shape)
    zone_start, zone_end = find_zone_range(defined)
    nz = zone_end - zone_start + 1
    conformity = zone.grid_layout
    if conformity is None:
        raise MissingConformityException(zone)
    if conformity in [Conform.Proportional, Conform.TopConform]:
        # Only get the top n cells of field_values
        field_values = field_values[:, :, :nz]
    elif conformity in [Conform.BaseConform]:
        # Get the bottom n cells of field_values
        field_values = field_values[:, :, -nz:]
    else:
        # One such case is 'mixed conform'
        raise NotImplementedError('{} is not supported'.format(conformity.name))
    values[:, :, zone_start:zone_end + 1] = field_values
    return values * defined


def _trim(field_name, prefix):
    trimmed = False
    if field_name.startswith(prefix):
        field_name = field_name[len(prefix):]
        trimmed = True
    return field_name, trimmed


def get_field_names(aps_model: APSModel, zone_model):
    fields = defaultdict(list)
    zone_names = sorted(
        zone_model.codes.values(),
        key=len,
        reverse=True,
    )
    zones = {
        zone_model.codes[zone.zone_number]: zone
        for zone in aps_model.zone_models
    }
    for field_name in aps_model.gaussian_field_names:
        field_name, _ = _trim(field_name, prefix='aps_')
        for zone_name in zone_names:
            field_name, trimmed = _trim(field_name, prefix=zone_name + '_')
            if trimmed:
                break
        if not trimmed:
            raise ValueError('Cannot find a zone for the field {}'.format('aps_' + field_name))
        fields[field_name].append(
            (zone_name, zones[zone_name], )
        )
    return fields


def get_field_name(field_name, zone):
    return 'aps_{}_{}'.format(zone, field_name)


def run(project, model_file, geo_grid_name=None, load_dir=None, **kwargs):
    if project.current_realisation > 0:
        raise ValueError(f'In RMS models to be used with a FMU loop in ERT,'
                          'the grid and parameters should be shared and realisation = 1'
        )
    aps_model = APSModel(model_file)
    file_format = kwargs.get('field_file_format')
    if geo_grid_name is None:
        geo_grid_name = aps_model.grid_model_name
    get_property = create_get_property(project, aps_model)
    debug_level = get_debug_level(**kwargs)

    if load_dir is None:
        load_dir = get_ert_location() / '..' / '..'

    rms_grid = xtgeo.grid_from_roxar(project, geo_grid_name)
    fmu_grid = xtgeo.grid_from_roxar(project, aps_model.grid_model_name)
    try:
        zone_model = get_property(aps_model.zone_parameter, geo_grid_name)
    except:
        grid_model = project.grid_models[geo_grid_name]
        zone_model = create_zone_parameter(
            grid_model,
            name=GridModelConstants.ZONE_NAME,
            realization_number=project.current_realisation,
            set_shared=True,
            debug_level=Debug.VERBOSE
        )

    for field_name, zones in get_field_names(aps_model, zone_model).items():
        field_values = np.zeros(rms_grid.dimensions)
        for zone_name, zone in zones:
            defined = zone_model.values == zone.zone_number
            full_field_name = get_field_name(field_name, zone_name)
            field_location = load_dir / f'{full_field_name}.{file_format}'
            if field_location.exists():
                field = load_field_values(full_field_name, fmu_grid, field_location, debug_level=debug_level)
                field_values += extract_values(field, defined, zone)
            else:
                if full_field_name not in zone.gaussian_fields_in_truncation_rule:
                    # This is OK, as we don't need this field
                    continue
                raise FileNotFoundError('The file {} could not be found.'.format(field_location))
        nx, ny, nz = rms_grid.dimensions
        field_model = xtgeo.GridProperty(
            ncol=nx, nrow=ny, nlay=nz,
            values=field_values,
            name=field_name,
            discrete=False,
        )
        field_model.to_roxar(
            project,
            geo_grid_name,
            field_name,
            realisation=project.current_realisation,
        )


def _load_field_values_grdecl(field_name, grid, path):
    with open(path) as f:
        content = f.read()
    # Assuming there is only ONE field per file
    name, *content = content.split()
    if name != field_name:
        raise ValueError(
            'Invalid name. Was expecting {expected}, but {actual} was found'.format(
                expected=field_name,
                actual=name,
            )
        )
    if content[-1] == '/':
        content = content[:-1]
    field = np.array([float(point) for point in content])
    field = field.reshape(grid.dimensions, order='F')

    # FIXME: Causes segmentation fault....
    # field = xtgeo.gridproperty_from_file(
    #     str(path),
    #     name=field_name,
    #     grid=grid,
    # ).values
    return field


def _load_field_values_roff(field_name, grid, path):
    property = xtgeo.grid3d.GridProperty()
    property.from_file(path, fformat='roff', name=field_name)
    return property.values


def load_field_values(field_name: str, grid: xtgeo.Grid, path: Path, debug_level=Debug.OFF):
    if debug_level >= Debug.VERBOSE:
        print(f'-- Read file: {path}')
    if path.suffix == '.grdecl':
        return _load_field_values_grdecl(field_name, grid, path)
    elif path.suffix == '.roff':
        return _load_field_values_roff(field_name, grid, path)
    else:
        raise ValueError(f'Invalid file format, {path.suffix}')
