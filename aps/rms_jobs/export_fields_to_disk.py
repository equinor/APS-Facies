#!/bin/env python
# -*- coding: utf-8 -*-
import xtgeo

from aps.algorithms.APSModel import APSModel
from aps.utils.fmu import create_get_property, get_export_location, find_zone_range
from aps.utils.methods import get_specification_file


def run(project, **kwargs):
    model_file = get_specification_file(**kwargs)
    aps_model = APSModel(model_file, debug_level=None)
    fmu_grid_name = kwargs.get('fmu_simulation_grid_name')
    file_format = kwargs.get('field_file_format')
    fmu_grid = xtgeo.grid_from_roxar(
        project,
        fmu_grid_name,
        project.current_realisation,
    )
    nx, ny, nz = fmu_grid.dimensions

    field_location = kwargs.get('save_dir', None)
    if field_location is None:
        field_location = get_export_location()

    fmu_mode = kwargs.get('fmu_mode', False)

    get_property = create_get_property(project, fmu_grid_name)

    zone_model = get_property(aps_model.zone_parameter)

    for zone in aps_model.zone_models:
        defined = zone_model.values == (1 if fmu_mode else zone.zone_number)
        zone_start, zone_end = find_zone_range(defined)
        for field_name in zone.gaussian_fields_in_truncation_rule:
            field_model = get_property(field_name)
            values = (field_model.values * defined)[:, :, zone_start:zone_end + 1]

            fmu_field_model = xtgeo.GridProperty(
                ncol=nx, nrow=ny, nlay=nz,
                values=values,
                name=field_name,
            )
            fmu_field_model.to_file(
                str(field_location / f'{field_name}.{file_format}'),
                fformat=file_format,
                name=field_name,
            )
