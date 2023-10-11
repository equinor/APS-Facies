#!/bin/env python
# -*- coding: utf-8 -*-
# This module is used in FMU workflows to import gaussian field values from disk into APS.
# Here we can assume that the project.current_realisation = 0 always since FMU ONLY run with one
# realization in the RMS project and should have shared grid and shared parameters only.
# There are two different modes of handling the GRF fields having trends.
# The first is to let ERT update the GRF (having trend +residual).
# The other option is to let ERT update the residuals only.
#
# In the first option when running with ERT iteration 0 (initial ensemble),
# APS will create GRF with trend in the ERTBOX gridmodel, export all the GRF's to files to be used by ERT.
# At the same time the GRF fields will be copied to the geomodel from the ERTBOX grid model (by extracting
# the values in the ERTBOX grid that corresponds to grid cells in the geomodel grid.
# In the first option when running with ERT iteration > 0, the GRF fields have been updated by ERT and is imported
# into the ERTBOX grid model. Using the same procedure as for ERT iteration 0,
# the GRF values are copied into the geomodel grid.
#
# In the second option (when ERT update the GRF residuals instead of the full GRF with both trend and residual),
# for ERT iteration = 0 (initial ensemble), APS code will simulate the GRF residuals and calculate the GRF trends
# if any, and save them in ERTBOX as two different 3D parameters. The residual GRF fields will be saved to files
# to be read by ERT. At the same time the code will calculate the GRF including trend and residual in ERTBOX grid model
# and copy as described above back to the geomodel. So in the geomodel the GRF's will as before have the
# full version with both trend and residuals since that is required before applying truncation rules
# and calculate facies realisation.
# In the second option for ERT iteration > 0, ERT will create new updated versions of the residual fields
# which is saved in files.  The aps code will import the files and for GRF that have trends, the residual values from
# ERT is added to the trend calculated by the aps code (also using the updated trend model parameters
# if they are specified to be updated by ERT). And finally all the imported GRF fields
# (including the added trends for those that should have trends) is then copied back to the geomodel grid.

from pathlib import Path
from roxar import Direction

import numpy as np
import xtgeo

from aps.algorithms.APSModel import APSModel
from aps.algorithms.APSZoneModel import Conform
from aps.utils.exceptions.zone import MissingConformityException
from aps.utils.constants.simple import Debug
from aps.utils.roxar.grid_model import (
    create_zone_parameter,
    get_zone_layer_numbering,
    getContinuous3DParameterValues,
    GridSimBoxSize,
    flip_grid_index_origo)
from aps.utils.roxar.generalFunctionsUsingRoxAPI import set_continuous_3d_parameter_values_in_zone_region
from aps.utils.roxar.progress_bar import APSProgressBar
from aps.utils.trend import add_trends
from aps.utils.aps_config import APSConfig

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
    return f'aps_{zone}_{field_name}'

def _load_field_values_grdecl(field_name, path, grid=None,debug_level=Debug.OFF):
    if debug_level >= Debug.VERY_VERBOSE:
        print(f'--- File name: {path}')
        print(f'--- Field name: {field_name}')
        print('--- Format: GRDECL')
    property = xtgeo.gridproperty_from_file(path, fformat='grdecl',
                                            name=field_name, grid=grid)
    return property.values

def _load_field_values_roff(field_name, path, grid=None, debug_level=Debug.OFF):
    if debug_level >= Debug.VERY_VERBOSE:
        print(f'--- File name: {path}')
        print(f'--- Field name: {field_name}')
        print('--- Format: ROFF')
    property = xtgeo.gridproperty_from_file(path, fformat='roff',
                                            name=field_name)
    return property.values

def _trim(field_name, prefix):
    trimmed = False
    if field_name.startswith(prefix):
        field_name = field_name[len(prefix):]
        trimmed = True
    return field_name, trimmed

def field_name_from_full_name(full_field_name, zone_name, region_name=""):
    is_trimmed = False
    field_name_tmp, is_trimmed = _trim(full_field_name, prefix='aps_')
    if not is_trimmed:
        raise IOError(f'Unexpected name of field to import: {full_field_name}')
    is_trimmed = False
    if len(region_name) == 0:
        field_name, is_trimmed  = _trim(field_name_tmp, prefix=zone_name + '_')
    else:
        field_name, is_trimmed  = _trim(field_name_tmp, prefix=zone_name + '_' + region_name + '_')
    if not is_trimmed:
        raise IOError(f'Unexpected name of field to import: {full_field_name}')
    return field_name

def load_field_values(field_name: str, path: Path, grid=None, debug_level=Debug.OFF):
    if path.suffix.upper() == '.GRDECL':
        return _load_field_values_grdecl(field_name, path, grid=grid, debug_level=debug_level)
    elif path.suffix.upper() == '.ROFF':
        return _load_field_values_roff(field_name, path, grid=grid, debug_level=debug_level)
    else:
        raise ValueError(f'Invalid file format, {path.suffix}')

def run(project, model_file, geo_grid_name, load_dir=None, **kwargs):
    ''' Read properties from file into the ERTBOX grid.
        Update the modelling grid property using the mapping from ERTBOX grid to geogrid
    '''
    if project.current_realisation > 0:
        raise ValueError(f'In RMS models to be used with a FMU loop in ERT,'
                          'the grid and parameters should be shared and realisation = 1'
        )
    aps_model = APSModel(model_file)
    debug_level = aps_model.log_setting
    file_format = aps_model.fmu_field_file_format
    use_residuals = aps_model.fmu_use_residual_fields

    if geo_grid_name is None:
        raise ValueError(f"Missing geo grid name as input to import of GRF from ERT")
    fmu_mode = kwargs.get('fmu_mode', False)
    if not fmu_mode:
        raise ValueError(f'The import of GRF is only available in FMU mode with AHM')
    fmu_grid_name = kwargs.get('fmu_simulation_grid_name')
    import_from_ert = False
    if load_dir is None:
        load_dir = Path(APSConfig.top_dir())
        import_from_ert = True

    print(" ")
    if import_from_ert:
        print(f"Import parameters for ERT updated ensemble from files into {fmu_grid_name} and {geo_grid_name}")
    else:
        print(f"Import parameters for initial ensemble from files into {fmu_grid_name} and {geo_grid_name}")

    if debug_level >= Debug.VERBOSE:
        print(f"-- Import directory: \n   {load_dir}")

    # Geomodel grid
    geo_grid_model = project.grid_models[geo_grid_name]
    if geo_grid_model.is_empty(project.current_realisation):
        raise ValueError(f'Grid model for geo grid: {geo_grid_name} '
                         f'is empty for realization {project.current_realisation}.')
    grid3D = geo_grid_model.get_grid(project.current_realisation)
    number_of_layers_per_zone_in_geo_grid, _, _ = get_zone_layer_numbering(grid3D)
    attributes = GridSimBoxSize(grid3D, debug_level=debug_level)
    handedness = attributes.handedness

    # Get the ERTBOX grid from RMS
    fmu_grid_model =  project.grid_models[fmu_grid_name]
    if fmu_grid_model.is_empty(project.current_realisation):
        raise ValueError(f'Grid model for ERTBOX grid: {fmu_grid_name} '
                         f'is empty for realization {project.current_realisation}.')

    xtgeo_fmu_grid = None
    if file_format.upper() == 'GRDECL':
         xtgeo_fmu_grid = xtgeo.grid_from_roxar(project, fmu_grid_name)


    # Get zone parameter for geomodel grid if it exist.
    # Create it if non-existing. Fill it if empty.
    zone_property = create_zone_parameter(
            geo_grid_model,
            realization_number=project.current_realisation,
            set_shared=geo_grid_model.shared
        )
    zone_names = zone_property.code_names
    region_names = None
    region_param_name = None
    if aps_model.use_regions:
        region_param_name = aps_model.region_parameter
        if region_param_name in geo_grid_model.properties:
            region_param = geo_grid_model.properties[region_param_name]
            if not region_param.is_empty(project.current_realisation):
                region_names = region_param.code_names

    if not use_residuals:
        import_and_update_ertbox_and_geogrid(project,
            aps_model,
            fmu_grid_model,
            geo_grid_model,
            zone_names,
            load_dir,
            file_format,
            xtgeo_fmu_grid,
            number_of_layers_per_zone_in_geo_grid,
            region_names=region_names,
            region_param_name=region_param_name,
            debug_level=debug_level)
    else:
        import_and_update_ertbox_and_geogrid_with_residuals(project,
            aps_model,
            fmu_grid_model,
            geo_grid_model,
            zone_names,
            load_dir,
            file_format,
            xtgeo_fmu_grid,
            number_of_layers_per_zone_in_geo_grid,
            handedness=handedness,
            region_names=region_names,
            region_param_name=region_param_name,
            debug_level=debug_level)

    APSProgressBar.increment()

def import_and_update_ertbox_and_geogrid(project,
    aps_model: APSModel,
    fmu_grid_model,
    geo_grid_model,
    zone_names: dict,
    load_dir: Path,
    file_format: str,
    xtgeo_fmu_grid: xtgeo.Grid,
    number_of_layers_per_zone_in_geo_grid: list,
    region_names: dict = None,
    region_param_name: str = None,
    debug_level: Debug = Debug.OFF):

    # Loop over all zones defined in aps model
    for zone in aps_model.zone_models:
        if aps_model.isSelected(zone.zone_number,zone.region_number):
            zone_name = zone_names[zone.zone_number]
            region_name = ""
            if region_names:
                region_name = region_names[zone.region_number]

            parameter_names_fmu_grid = []
            parameter_names_geo_grid = []

            parameter_values_fmu_grid =[]
            parameter_values_geo_grid =[]

            # Get the sub set of values from fmu grid that should be mapped into geogrid for the current zone
            nz_layers = number_of_layers_per_zone_in_geo_grid[zone.zone_number-1]
            for full_field_name in zone.gaussian_fields_in_truncation_rule:
                field_name = field_name_from_full_name(full_field_name, zone_name, region_name=region_name)
                field_location = load_dir / f'{full_field_name}.{file_format}'

                if field_location.exists():
                    # Read values into fmu grid (ERTBOX)
                    # field is a 3D numpy array
                    field = load_field_values(full_field_name,
                                field_location,
                                grid=xtgeo_fmu_grid,
                                debug_level=debug_level)

                else:
                    raise FileNotFoundError(
                        f'\nThe file {field_location} for the parameter {full_field_name} is not found.'
                        f'\nCheck that ERT has created the file if ERT iteration > 0'
                    )

                # Field names and corresponding values to update the fmu grid with
                parameter_names_fmu_grid.append(full_field_name)
                parameter_values_fmu_grid.append(field)

                field_extracted = extract_values_from_fmu_grid_to_geogrid_simbox(field, zone, nz_layers)

                # Field names and corresponding values to update the geo grid with
                parameter_names_geo_grid.append(field_name)
                parameter_values_geo_grid.append(field_extracted)


            # Update fmu grid. Has only one zone but parameter name contains zone name
            if debug_level >= Debug.VERY_VERBOSE:
                for name in parameter_names_fmu_grid:
                    print(f'--- Load parameter {name} from file into {fmu_grid_model.name}')
            zone_number_fmu_grid = 1
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
                    if aps_model.use_regions:
                        print(f'--- Update parameter {name} for (zone number, region number) = ({zone.zone_number},{zone.region_number})  in {geo_grid_model.name}')
                    else:
                        print(f'--- Update parameter {name} for zone number {zone.zone_number} in {geo_grid_model.name}')

            set_continuous_3d_parameter_values_in_zone_region(
                geo_grid_model,
                parameter_names_geo_grid,
                parameter_values_geo_grid,
                zone.zone_number,
                zone.region_number,
                region_parameter_name=region_param_name,
                realisation_number=project.current_realisation,
                is_shared=geo_grid_model.shared,
            )


def import_and_update_ertbox_and_geogrid_with_residuals(project,
    aps_model: APSModel,
    fmu_grid_model,
    geo_grid_model,
    zone_names: dict,
    load_dir: Path,
    file_format: str,
    xtgeo_fmu_grid: xtgeo.Grid,
    number_of_layers_per_zone_in_geo_grid: list,
    handedness=Direction.right,
    region_names: dict = None,
    region_param_name: str = None,
    debug_level: Debug = Debug.OFF):

    use_residuals = True
    (nx_ertbox, ny_ertbox, nz_ertbox) = fmu_grid_model.get_grid(project.current_realisation).simbox_indexer.dimensions
    # Loop over all zones defined in aps model

    for zone in aps_model.zone_models:
        if aps_model.isSelected(zone.zone_number,0):
            zone_name = zone_names[zone.zone_number]
            region_name = ""
            if aps_model.use_regions:
                region_name = region_names[zone.region_number]
            parameter_names_fmu_grid = []
            parameter_names_geo_grid = []

            parameter_values_fmu_grid = []
            parameter_values_geo_grid = []

            # Get the sub set of values from fmu grid that should be mapped into geogrid for the current zone
            nz_layers = number_of_layers_per_zone_in_geo_grid[zone.zone_number-1]

            for full_field_name in zone.gaussian_fields_in_truncation_rule:
                field_name = field_name_from_full_name(full_field_name, zone_name, region_name=region_name)
                if zone.hasTrendModel(full_field_name):
                    full_field_name_residual = full_field_name + '_residual'
                    field_location = load_dir / f'{full_field_name_residual}.{file_format}'
                    field_name_in_file = full_field_name_residual
                else:
                    field_location = load_dir / f'{full_field_name}.{file_format}'
                    field_name_in_file = full_field_name

                if field_location.exists():
                    # Read values into fmu grid (ERTBOX)
                    # field is a 3D numpy array
                    field = load_field_values(field_name_in_file,
                                field_location,
                                grid=xtgeo_fmu_grid,
                                debug_level=debug_level)

                else:
                    raise FileNotFoundError(
                        f'\nThe file {field_location} for the parameter {full_field_name} is not found.'
                        f'\nCheck that ERT has created the file if ERT iteration > 0'
                    )

                # Field names and corresponding values to update the fmu grid with
                # Separate parameters are created for residual fields for QC purpose
                # Before the trend is added, they are equal.
                parameter_names_fmu_grid.append(full_field_name)
                parameter_names_geo_grid.append(field_name)
                parameter_values_fmu_grid.append(field)


            # Update fmu grid. Has only one zone but parameter name contains zone name.
            if debug_level >= Debug.VERY_VERBOSE:
                for name in parameter_names_fmu_grid:
                    print(f'--- Load parameter {name} from file into {fmu_grid_model.name}')
            zone_number_fmu_grid = 1
            set_continuous_3d_parameter_values_in_zone_region(
                fmu_grid_model,
                parameter_names_fmu_grid,
                parameter_values_fmu_grid,
                zone_number_fmu_grid,
                realisation_number=project.current_realisation,
                is_shared=fmu_grid_model.shared,
            )

            add_trends(
                project,
                aps_model,
                zone.zone_number,
                zone.region_number,
                write_rms_parameters_for_qc_purpose=False,
                debug_level=debug_level,
                fmu_mode=True,
                is_shared=fmu_grid_model.shared,
                fmu_with_residual_grf=use_residuals,
                fmu_add_trend_if_use_residual=True)


            for full_field_name in zone.gaussian_fields_in_truncation_rule:
                field_ertbox_1D = getContinuous3DParameterValues(fmu_grid_model, full_field_name,
                                    realization_number=project.current_realisation)

                # This works because the ERTBOX field values are all defined to the length
                # of the 1D array returned from the RMS 3D parameter match the ertbox size
                field_ertbox_3D = np.reshape(field_ertbox_1D, (nx_ertbox, ny_ertbox, nz_ertbox))
                if handedness == Direction.right:
                    field_ertbox_3D_flip = flip_grid_index_origo(field_ertbox_3D, ny_ertbox)
                    field_ertbox_3D = field_ertbox_3D_flip
                field_extracted = extract_values_from_fmu_grid_to_geogrid_simbox(field_ertbox_3D, zone, nz_layers)
                parameter_values_geo_grid.append(field_extracted)

            # Update geogrid. Has often multiple zones
            if debug_level >= Debug.VERBOSE:
                for name in  parameter_names_geo_grid:
                    if aps_model.use_regions:
                        print(f'-- Update parameter {name} for (zone number, region number) = ({zone.zone_number},{zone.region_number}) in {geo_grid_model.name}')
                    else:
                        print(f'-- Update parameter {name} for zone number {zone.zone_number} in {geo_grid_model.name}')

            set_continuous_3d_parameter_values_in_zone_region(
                geo_grid_model,
                parameter_names_geo_grid,
                parameter_values_geo_grid,
                zone.zone_number,
                zone.region_number,
                region_parameter_name=region_param_name,
                realisation_number=project.current_realisation,
                is_shared=geo_grid_model.shared,
            )
