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
from aps.utils.methods import get_debug_level, get_specification_file
from aps.utils.roxar.grid_model import create_zone_parameter, get_zone_layer_numbering
from aps.utils.roxar.generalFunctionsUsingRoxAPI import set_continuous_3d_parameter_values_in_zone_region

def extract_values_from_fmu_grid_to_geogrid_simbox(field_values, zone, number_of_layers_in_geo_grid_zone):
    ''' Updates or replaces the input field_values for fmu grid to contain only the values
        that are used in the geomodel simbox. Use grid conformity definition
        to select layers from top of fmu ertbox grid or from bottom of ertbox grid.

    '''
    nz = number_of_layers_in_geo_grid_zone
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
    return field_values

def get_field_name(field_name, zone):
    return 'aps_{}_{}'.format(zone, field_name)

def _load_field_values_grdecl(field_name, path, grid=None):
    print(f'File name: {path}')
    print(f'Field name: {field_name}')
    print('Format: GRDECL')
    property = xtgeo.gridproperty_from_file(path, fformat='grdecl',
                                            name=field_name, grid=grid)
    return property.values

def _load_field_values_roff(field_name, path, grid=None):
    print(f'File name: {path}')
    print(f'Field name: {field_name}')
    print('Format: ROFF')
    property = xtgeo.gridproperty_from_file(path, fformat='roff',
                                            name=field_name)
    return property.values

def _trim(field_name, prefix):
    trimmed = False
    if field_name.startswith(prefix):
        field_name = field_name[len(prefix):]
        trimmed = True
    return field_name, trimmed

def field_name_from_full_name(full_field_name, zone_name):
    is_trimmed = False
    field_name_tmp, is_trimmed = _trim(full_field_name, prefix='aps_')
    if not is_trimmed:
        raise IOError(f'Unexpected name of field to import: {full_field_name}')
    is_trimmed = False
    field_name, is_trimmed  = _trim(field_name_tmp, prefix=zone_name + '_')
    if not is_trimmed:
        raise IOError(f'Unexpected name of field to import: {full_field_name}')
    return field_name

def load_field_values(field_name: str, path: Path, grid=None):
    if path.suffix.upper() == '.GRDECL':
        return _load_field_values_grdecl(field_name, path, grid=grid)
    elif path.suffix.upper() == '.ROFF':
        return _load_field_values_roff(field_name, path, grid=grid)
    else:
        raise ValueError(f'Invalid file format, {path.suffix}')

def run(project, model_file, geo_grid_name=None, load_dir=None, **kwargs):
    ''' Read properties from file into the ERTBOX grid.
        Update the modelling grid property using the mapping from ERTBOX grid to geogrid
    '''
    if project.current_realisation > 0:
        raise ValueError(f'In RMS models to be used with a FMU loop in ERT,'
                          'the grid and parameters should be shared and realisation = 1'
        )
    debug_level = get_debug_level(**kwargs)
    aps_model = APSModel(model_file, debug_level=None)
    file_format = kwargs.get('field_file_format')
    if geo_grid_name is None:
        geo_grid_name = aps_model.grid_model_name
    fmu_mode = kwargs.get('fmu_mode', False)
    if not fmu_mode:
        raise ValueError(f'The import of GRF is only available in FMU mode with AHM')
    fmu_grid_name = kwargs.get('fmu_simulation_grid_name')
    if debug_level >= Debug.VERBOSE:
        print(f'-- Grid model:  {geo_grid_name}')
        print(f'-- ERT box model:  {fmu_grid_name}')

    if load_dir is None:
        load_dir = get_ert_location() / '..' / '..'
        import_from_ert = True
        if debug_level >= Debug.VERBOSE:
            print(f'-- Import updated GRF from ERT from directory: \n'
                  f'   {load_dir}')
    else:
        if debug_level >= Debug.VERBOSE:
            print(f'-- Import simulated GRF from directory: \n'
                  f'   {load_dir}')

    # Get the ERTBOX grid from RMS
    fmu_grid_model =  project.grid_models[fmu_grid_name]
    if fmu_grid_model.is_empty(project.current_realisation):
        raise ValueError(f'Grid model for ERTBOX grid: {fmu_grid_name} '
                         f'is empty for realization {project.current_realisation}.')
    fmu_grid3D = fmu_grid_model.get_grid(project.current_realisation)
    xtgeo_fmu_grid = None
    if file_format.upper() == 'GRDECL':
         xtgeo_fmu_grid = xtgeo.grid_from_roxar(project, fmu_grid_name)

    # For ERTBOX grid the simulation box dimensions from simbox_indexer and grid_indexer are the same.
    indexer = fmu_grid3D.simbox_indexer
    nx, ny, nz  = indexer.dimensions


    # Geomodel grid
    geo_grid_model = project.grid_models[geo_grid_name]
    if geo_grid_model.is_empty(project.current_realisation):
        raise ValueError(f'Grid model for geo grid: {geo_grid_name} '
                         f'is empty for realization {project.current_realisation}.')
    grid3D = geo_grid_model.get_grid(project.current_realisation)

    # Get zone parameter for geomodel grid
    try:
        zone_property = geo_grid_model.properties[aps_model.zone_parameter]
    except:
        zone_property = create_zone_parameter(
            geo_grid_model,
            name=GridModelConstants.ZONE_NAME,
            realization_number=project.current_realisation,
            set_shared=geo_grid_model.shared,
            debug_level=debug_level,
        )

    number_of_layers_per_zone_in_geo_grid, _, _ = get_zone_layer_numbering(grid3D)
    if debug_level >= Debug.VERY_VERBOSE:
        print(f'--- Number of layers per zone in geogrid {number_of_layers_per_zone_in_geo_grid}')

    # Loop over all zones defined in aps model
    for zone in aps_model.zone_models:
        zone_number = zone.zone_number
        if aps_model.isSelected(zone_number,0):
            zone_name = zone_property.code_names[zone_number]
            parameter_names_fmu_grid = []
            parameter_values_fmu_grid =[]
            parameter_names_geo_grid = []
            parameter_values_geo_grid =[]
            for full_field_name in zone.gaussian_fields_in_truncation_rule:
                field_name = field_name_from_full_name(full_field_name, zone_name)
                field_location = load_dir / f'{full_field_name}.{file_format}'

                if field_location.exists():
                    # Read values into fmu grid (ERTBOX)
                    if debug_level >= Debug.VERY_VERBOSE:
                        print(f'--- Read parameter {full_field_name} from file {field_location}')

                    # field is a 3D numpy array
                    field = load_field_values(full_field_name,
                                              field_location,
                                              grid=xtgeo_fmu_grid)

                else:
                    raise FileNotFoundError(
                        f'\nThe file {field_location} for the parameter {full_field_name} is not found.'
                        f'\nCheck that ERT has created the file if ERT iteration > 0'
                    )

                # Field names and corresponding values to update the fmu grid with
                parameter_names_fmu_grid.append(full_field_name)
                parameter_values_fmu_grid.append(field)

                # Get the sub set of values from fmu grid that should be mapped into geogrid for the current zone
                nz_layers = number_of_layers_per_zone_in_geo_grid[zone_number-1]
                field = extract_values_from_fmu_grid_to_geogrid_simbox(field, zone, nz_layers)

                # Field names and corresponding values to update the geo grid with
                parameter_names_geo_grid.append(field_name)
                parameter_values_geo_grid.append(field)


            # Update fmu grid. Has only one zone but parameter name contains zone number
            zone_number_fmu_grid = 1
            if debug_level >= Debug.VERY_VERBOSE:
                for name in parameter_names_fmu_grid:
                    print(f'-- Update parameter {name} in {fmu_grid_name}')

            set_continuous_3d_parameter_values_in_zone_region(
                fmu_grid_model,
                parameter_names_fmu_grid,
                parameter_values_fmu_grid,
                zone_number_fmu_grid,
                realisation_number=project.current_realisation,
                is_shared=fmu_grid_model.shared,
            )

            # Update geogrid. Has often multiple zones
            if debug_level >= Debug.VERY_VERBOSE:
                for name in  parameter_names_geo_grid:
                    print(f'-- Update parameter {name} for zone number {zone_number} in {geo_grid_name}')

            set_continuous_3d_parameter_values_in_zone_region(
                geo_grid_model,
                parameter_names_geo_grid,
                parameter_values_geo_grid,
                zone_number,
                realisation_number=project.current_realisation,
                is_shared=geo_grid_model.shared,
            )







