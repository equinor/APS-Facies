#!/bin/env python
# -*- coding: utf-8 -*-
# This script use both nrlib and ROXAR API functions and run simulations sequentially and not in parallel
from pathlib import Path

import nrlib
import numpy as np

from aps.algorithms.APSModel import APSModel
from aps.utils.constants.simple import Debug
from aps.utils.io import ensure_folder_exists
from aps.utils.methods import get_specification_file, get_debug_level
from aps.utils.roxar.generalFunctionsUsingRoxAPI import (
    set_continuous_3d_parameter_values_in_zone_region,
    get_project_realization_seed,
)
from aps.utils.roxar.grid_model import GridAttributes, get_zone_names
from aps.utils.methods import get_seed_log_file
from aps.utils.trend import add_trends


def define_variogram(variogram, azimuth_value_sim_box):
    variogram_name = variogram.type.name.lower()
    # Note: Since RMS is a left-handed coordinate system and NrLib treat the coordinate
    # system as right-handed, we have to transform the azimuth angle to 90-azimuth
    # to get it correct in RMS.
    azimuth_in_nrlib = 90.0 - azimuth_value_sim_box
    args = [
        variogram.ranges.main, variogram.ranges.perpendicular, variogram.ranges.vertical,
        azimuth_in_nrlib, variogram.angles.dip,
    ]
    if variogram_name == 'general_exponential':
        args.append(variogram.power)
    args = [float(arg) for arg in args]

    return nrlib.variogram(variogram_name, *args)


def run_simulations(
        project, model_file='APS.xml', realisation=0,
        is_shared=False, seed_file_log='seedLogFile.dat',
        write_rms_parameters_for_qc_purpose=False,
        fmu_mode=False,
):
    """
    Description: Run gauss simulations for the APS model i sequence

    """

    # Read APS model
    aps_model = APSModel(model_file)
    debug_level = aps_model.log_setting
    fmu_with_residual_grf = aps_model.fmu_use_residual_fields
    if debug_level >= Debug.ON:
        print(f'- Read file: {model_file}')


    # When running in single processing mode, there will not be created
    # new start seeds in the RMS multi realization
    # workflow loop because the start random seed is created once per process,
    # and the process is the same for all realizations in the loop.
    # Hence always read the start seed in single processing mode.
    # The seed can e.g be defined by using the RMS project
    # realization seed number and should be set into the seed file
    # before calling the current script.

    grid_model = project.grid_models[aps_model.grid_model_name]
    zone_names = get_zone_names(grid_model)
    if fmu_mode:
        # Ensure that the grid is shared and the realisation number
        # is 1 and that there are only one zone and one region.
        if realisation > 1:
            raise ValueError('The realisation number must be 1 in FMU mode.')
        grid = grid_model.get_grid(realisation)
        # Get grid dimensions
        grid_attributes = GridAttributes(grid, zone_names, debug_level=Debug.OFF)
        num_layers_per_zone = grid_attributes.num_layers_per_zone
        if len(num_layers_per_zone) != 1:
            raise ValueError('The ERTBOX grid can only have 1 zone')
    else:
        grid = grid_model.get_grid(realisation)
        # Get grid dimensions
        grid_attributes = GridAttributes(grid, zone_names, debug_level=debug_level)
        num_layers_per_zone = grid_attributes.num_layers_per_zone

    nx, ny, nz = grid_attributes.simbox_dimensions

    # Calculate grid cell size
    dx = grid_attributes.sim_box_size.x_length / nx
    dy = grid_attributes.sim_box_size.y_length / ny

    # Set start seed
    start_seed = get_project_realization_seed(project)
    nrlib.seed(start_seed)
    if debug_level >= Debug.VERY_VERBOSE:
        print(f"--- Start seed value: {nrlib.seed()}")

    # Loop over all zones and simulate gauss fields
    all_zone_models = aps_model.sorted_zone_models
    for key, zone_model in all_zone_models.items():
        zone_number, region_number = key
        if not aps_model.isSelected(zone_number, region_number):
            continue
        gauss_field_names = zone_model.gaussian_fields_in_truncation_rule
        # Add zone names / number, if FMU
        if fmu_mode:
            assert len(num_layers_per_zone) == 1
            zone_index = 0
        else:
            # Zone index is counted from 0 while zone number from 1
            zone_index = zone_number - 1
        num_layers = num_layers_per_zone[zone_index]

        # Calculate grid cell size in z direction
        nz = num_layers
        dz = zone_model.sim_box_thickness / nz

        if debug_level >= Debug.ON:
            if region_number == 0:
                print(f'- Zone: {zone_number}')
            else:
                print(f'- Zone: {zone_number}   Region: {region_number}  ')
        if debug_level >= Debug.VERY_VERBOSE:
            start = grid_attributes.start_layers_per_zone[zone_index]
            end = grid_attributes.end_layers_per_zone[zone_index]
            print(f'--- Grid layers: {num_layers} Start layer: {start + 1} End layer: {end}')

        gauss_result_list_for_zone = []
        for gauss_field_name in gauss_field_names:
            field = zone_model.get_gaussian_field(gauss_field_name)
            if field is None:
                raise KeyError(
                    f"No Gaussian Random Field named {gauss_field_name}"
                    f" is defined in zone {zone_number}"
                    f'{f", {region_number}" if region_number else "."}'
                )
            use_residuals = True
            if zone_model.hasTrendModel(gauss_field_name):
                _, _, rel_std_dev, _ = zone_model.getTrendModel(gauss_field_name)
                if rel_std_dev < 0.001:
                    use_residuals = False
            if use_residuals:
                variogram = field.variogram

                azimuth_value_sim_box = variogram.angles.azimuth - grid_attributes.sim_box_size.azimuth_angle

                if debug_level >= Debug.VERBOSE:
                    if region_number > 0:
                        print(f'-- Simulate: {gauss_field_name}  for zone: {zone_number}  for region: {region_number}')
                    else:
                        print(f'-- Simulate: {gauss_field_name}  for zone: {zone_number}')
                if debug_level >= Debug.VERY_VERBOSE:
                    print(f'     Zone,region             : ({zone_number}, {region_number})')
                    print(f'     Gauss field name        : {gauss_field_name}')
                    print(f'     Variogram type          : {variogram.type.name.upper()}')
                    print(f'     Main range              : {variogram.ranges.main}')
                    print(f'     Perpendicular range     : {variogram.ranges.perpendicular}')
                    print(f'     Vertical range          : {variogram.ranges.vertical}')
                    print(f'     Azimuth angle in sim box: {azimuth_value_sim_box}')
                    print(f'     Dip angle               : {variogram.angles.dip}')
                    print(f'     NX                      : {nx}')
                    print(f'     NY                      : {ny}')
                    print(f'     NZ for this zone        : {nz}')
                    print(f'     DX                      : {dx}')
                    print(f'     DY                      : {dy}')
                    print(f'     DZ for this zone        : {dz}')

                # Define variogram
                sim_variogram = define_variogram(variogram, azimuth_value_sim_box)

                if debug_level >= Debug.VERY_VERBOSE:
                    nx_padding, ny_padding, nz_padding = nrlib.simulation_size(sim_variogram, nx, dx, ny, dy, nz, dz)
                    print( '---  Grid dimensions with padding for simulation:')
                    print(f'     nx: {nx}   nx with padding: {nx_padding}')
                    print(f'     ny: {ny}   ny with padding: {ny_padding}')
                    print(f'     nz: {nz}   nz with padding: {nz_padding}')

                # Simulate gauss field. Return numpy 1D vector in F order
                gauss_vector = nrlib.simulate(sim_variogram, nx, dx, ny, dy, nz, dz)
            else:
                # No need to simulate gauss field, but set it to 0
                if debug_level >= Debug.VERBOSE:
                    print(
                        f"-- No simulation of: {gauss_field_name} "
                        f"for zone: {zone_number},  region: {region_number}."
                    )
                    print(f"-- Relative standard deviation is: {rel_std_dev}  < 0.001")

                gauss_vector = np.zeros((nx*ny*nz), dtype=np.float32)
            gauss_result = np.reshape(gauss_vector, (nx, ny, nz), order='F')
            gauss_result_list_for_zone.append(gauss_result)
            if debug_level >= Debug.VERBOSE:
                if region_number > 0:
                    print(
                        f'-- Finished running simulation of {gauss_field_name} for zone,region: '
                        f'({zone_number}, {region_number})\n'
                    )
                else:
                    print(
                        f'-- Finished running simulation of {gauss_field_name} for zone: {zone_number}\n'
                    )

        set_continuous_3d_parameter_values_in_zone_region(
            grid_model,
            gauss_field_names,
            gauss_result_list_for_zone,
            zone_number,
            region_number=region_number,
            region_parameter_name=aps_model.region_parameter,
            realisation_number=realisation,
            is_shared=is_shared,
            debug_level=debug_level,
            fmu_mode=fmu_mode,
            use_left_handed_grid_indexing=True,
        )


        add_trends(
            project, aps_model, zone_number, region_number,
            write_rms_parameters_for_qc_purpose=write_rms_parameters_for_qc_purpose,
            debug_level=debug_level,
            fmu_mode=fmu_mode,
            is_shared=is_shared,
            fmu_with_residual_grf=fmu_with_residual_grf,
            fmu_add_trend_if_use_residual=False
        )
        # End loop over gauss fields for one zone

    # End loop over all active zones in the model

    if seed_file_log and aps_model.write_seeds:
        if isinstance(seed_file_log, str):
            seed_file_log = Path(seed_file_log)
        ensure_folder_exists(seed_file_log)
        if seed_file_log.is_dir():
            seed_file_log = seed_file_log / 'seedLogFile.dat'
        with open(seed_file_log, 'a+', encoding='utf-8') as file:
            file.write(f'RealNumber: {realisation}  StartSeed for this realization: {1 + nrlib.seed()}\n')
    if debug_level >= Debug.ON:
        print('- Finished simulation of gaussian fields for APS')


def run(project, **kwargs):
    model_file = get_specification_file(**kwargs)
    seed_file_log = get_seed_log_file(**kwargs)
    fmu_mode = kwargs.get('fmu_mode', False)
    fmu_mode_only_param = kwargs.get('fmu_mode_only_param', False)
    write_rms_parameters_for_qc_purpose = kwargs.get('write_rms_parameters_for_qc_purpose',False)
    real_number = project.current_realisation

    print(f'\nSimulation of gaussian fields for realisation number: {real_number+1}')

    is_shared = fmu_mode or fmu_mode_only_param

    run_simulations(
        project,
        model_file,
        real_number,
        is_shared,
        seed_file_log,
        write_rms_parameters_for_qc_purpose=write_rms_parameters_for_qc_purpose,
        fmu_mode=fmu_mode,
    )
