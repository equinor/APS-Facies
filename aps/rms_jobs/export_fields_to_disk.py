#!/bin/env python
# -*- coding: utf-8 -*-
# This module is used in FMU workflows to export gaussian field values to disk to be read by ERT.
# Here we can assume that the project.current_realisation = 0 always since FMU ONLY run with one
# realization in the RMS project and should have shared grid and shared parameters only.
# NOTE:
# The run function is called when the aps model file is modified to be run from ERTBOX grid
# This means that grid model is the ERTBOX grid and has one zone, but geomodel zone name is
# a part of the property names in this case.
# The field names are of the form:
#          aps_<zone_name>_<gaussfield_name>
# for models without regions and of the form:
#          aps_<zone_name>_<region_name>_<gaussfield_name>
# The parameter names for active cells are of the form:
#          aps_<zone_name>_active
# for models without region and of the form:
#          aps_<zone_name>_<region_name>_active

import copy
import xtgeo
import roxar
import numpy as np
from roxar import Direction

from aps.algorithms.APSModel import APSModel
from aps.utils.fmu import get_export_location
from aps.utils.roxar.grid_model import flip_grid_index_origo
from aps.utils.roxar.progress_bar import APSProgressBar
from aps.utils.constants.simple import Debug


def run(project, **kwargs):
    """Export simulated GRF fields from ERTBOX grid to file readable by ERT"""
    if project.current_realisation > 0:
        raise ValueError(
            f'In RMS models to be used with a FMU loop in ERT,'
            'the grid and parameters should be shared and realisation = 1'
        )
    model_file_name = kwargs.get('model_file', None)
    if model_file_name is None:
        raise ValueError('Model file name is required in export_fields_to_dist')
    fmu_mode = kwargs.get('fmu_mode', False)
    aps_model = APSModel(model_file_name)

    if not fmu_mode:
        raise ValueError(f'The export of GRF is only available in FMU mode with AHM')
    debug_level = aps_model.log_setting
    fmu_grid_name = aps_model.grid_model_name
    file_format = aps_model.fmu_field_file_format
    fmu_use_residual_fields = aps_model.fmu_use_residual_fields

    print(' ')
    print(f'Export 3D parameter files from {fmu_grid_name}')
    if debug_level >= Debug.ON:
        if fmu_use_residual_fields:
            print(
                f"- Only the residual for GRF's with trend is written to files to be read by ERT!"
            )
        else:
            print(f'- GRF files are written to files to be read by ERT')

    # Get the ERTBOX grid from RMS
    fmu_grid_model = project.grid_models[fmu_grid_name]
    if fmu_grid_model.is_empty(project.current_realisation):
        raise ValueError(
            f'Grid model for ERTBOX grid: {fmu_grid_name} is empty for realization {project.current_realisation}.'
        )
    grid3D = fmu_grid_model.get_grid(project.current_realisation)

    # For ERTBOX grid the simulation box dimensions from simbox_indexer and grid_indexer are the same.
    indexer = grid3D.simbox_indexer
    nx, ny, nz = indexer.dimensions
    handedness = indexer.ijk_handedness

    field_location = kwargs.get('save_dir', None)
    if field_location is None:
        field_location = get_export_location()

    # Loop over all GRF's used in the APS zone model for the current zone
    # and save the simulated GRF to file
    # The simbox_indexer is used and there are only one zone in ERTBOX
    # grid which is re-used for all geomodel grid zones

    # Loop over all zones defined in aps model
    active_params_save_to_file = []
    for zone in aps_model.zone_models:
        if aps_model.isSelected(zone.zone_number, zone.region_number):
            if debug_level >= Debug.VERBOSE:
                print(' ')
                print(
                    f'-- Export GRF fields for (zone,region) = ({zone.zone_number},{zone.region_number})'
                )

            for field_name in zone.gaussian_fields_in_truncation_rule:
                if fmu_use_residual_fields and zone.hasTrendModel(field_name):
                    field_name = field_name + '_residual'
                field_properties = fmu_grid_model.properties
                field_property = None
                if field_name in field_properties:
                    field_property = field_properties[field_name]
                    if field_property.is_empty(project.current_realisation):
                        raise ValueError(
                            f'The parameter {field_name} is empty in grid model {fmu_grid_name}'
                        )
                else:
                    raise ValueError(
                        f'The parameter  {field_name} does not exist in grid model {fmu_grid_name}'
                    )

                file_name_active = None
                for property in field_properties:
                    # sub_string is None if the property_name does not end with '_active'
                    # and contain the property_name except the '_active' else
                    sub_string = is_active_param_name(property.name)

                    # Check if the sub_string match the first part of field_name
                    if sub_string and is_active_param_defined_for_zone(
                        sub_string, field_name
                    ):
                        file_name_active = str(
                            field_location / f'{property.name}.{file_format}'
                        )
                        if file_name_active not in active_params_save_to_file:
                            active_params_save_to_file.append(file_name_active)
                            write_field_name_to_file(
                                file_name_active,
                                field_name,
                                file_format,
                                field_properties,
                                field_property,
                                handedness,
                                nx,
                                ny,
                                nz,
                                debug_level,
                            )

                file_name = str(field_location / f'{field_name}.{file_format}')
                write_field_name_to_file(
                    file_name,
                    field_name,
                    file_format,
                    field_properties,
                    field_property,
                    handedness,
                    nx,
                    ny,
                    nz,
                    debug_level,
                )

    APSProgressBar.increment()


def write_field_name_to_file(
    file_name,
    field_name,
    file_format,
    field_properties,
    field_property,
    handedness,
    nx,
    ny,
    nz,
    debug_level,
):
    if debug_level >= Debug.VERY_VERBOSE:
        print(f'--- Write parameter: {field_name} to file {file_name}')

    if file_format.upper() == 'ROFF':
        # Use ROFF Binary
        field_properties.save(
            file_name, field_name, format=roxar.FileFormat.ROFF_BINARY
        )
    else:
        # Use xtgeo for other formats not available from roxar.grids
        values = field_property.get_values()
        values3d = np.reshape(values, (nx, ny, nz))

        if handedness == Direction.right:
            # Current grid model is right-handed
            # Need to flip order of the values to get correct export
            # when using GRDECL format with xtgeo.GridProperty instance
            values3d_flipped = flip_grid_index_origo(values3d, ny)

            xtgeo_object = xtgeo.GridProperty(
                ncol=nx,
                nrow=ny,
                nlay=nz,
                values=values3d_flipped,
                name=field_name,
            )
        else:
            xtgeo_object = xtgeo.GridProperty(
                ncol=nx,
                nrow=ny,
                nlay=nz,
                values=values3d,
                name=field_name,
            )

            xtgeo_object.to_file(
                file_name,
                fformat=file_format,
                name=field_name,
            )


def is_active_param_name(property_name: str):
    words = property_name.split('_')
    if words[-1] == 'active':
        return copy.copy(property_name[:-7])
    return None


def is_active_param_defined_for_zone(name: str, field_name: str):
    if name is None:
        return False
    try:
        if field_name.index(name) == 0:
            # The field_name contains the name in first part of it
            return True
    except ValueError:
        return False
    return False
