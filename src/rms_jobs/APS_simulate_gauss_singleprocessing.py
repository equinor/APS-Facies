#!/bin/env python
# -*- coding: utf-8 -*-
# This script use both nrlib and ROXAR API functions and run simulations sequentially and not in parallel
from pathlib import Path

import nrlib
import numpy as np

from src.algorithms.APSModel import APSModel
from src.utils.constants.simple import Debug
from src.utils.io import ensure_folder_exists
from src.utils.methods import get_specification_file
from src.utils.roxar.generalFunctionsUsingRoxAPI import (
    setContinuous3DParameterValuesInZoneRegion,
    get_project_realization_seed,
)
from src.utils.roxar.grid_model import GridAttributes
from src.utils.methods import get_seed_log_file
from src.utils.trend import add_trends


def run_simulations(
        project, model_file='APS.xml', realisation=0, is_shared=False, seed_file_log='seedLogFile.dat',
        layers_per_zone=None, write_rms_parameters_for_qc_purpose=True,
        fmu_mode=False,
):
    """
    Description: Run gauss simulations for the APS model i sequence

    """

    # Read APS model
    print('- Read file: ' + model_file)
    aps_model = APSModel(model_file)
    debug_level = aps_model.debug_level
    # When running in single processing mode, there will not be created new start seeds in the RMS multi realization
    # workflow loop because the start random seed is created once per process,
    # and the process is the same for all realizations in the loop.
    # Hence always read the start seed in single processing mode.
    # The seed can e.g be defined by using the RMS project realization seed number and should be set into the seed file
    # before calling the current script.

    # Get grid dimensions
    grid_model = project.grid_models[aps_model.grid_model_name]
    grid = grid_model.get_grid()
    grid_attributes = GridAttributes(grid)

    num_layers_per_zone = grid_attributes.num_layers_per_zone

    nx, ny, nz = grid_attributes.sim_box_size.dimensions

    # Calculate grid cell size
    dx = grid_attributes.sim_box_size.x_length / nx
    dy = grid_attributes.sim_box_size.y_length / ny

    # Set start seed
    start_seed = get_project_realization_seed(project)
    nrlib.seed(start_seed)

    # Loop over all zones and simulate gauss fields
    all_zone_models = aps_model.sorted_zone_models
    for key, zone_model in all_zone_models.items():
        zone_number, region_number = key
        if not aps_model.isSelected(zone_number, region_number):
            continue
        gauss_field_names = zone_model.gaussian_fields_in_truncation_rule  # Add zone names / number, if FMU
        sim_box_thickness = zone_model.sim_box_thickness

        if fmu_mode:
            assert len(num_layers_per_zone) == 1
            zone_index = 0
        else:
            # Zone index is counted from 0 while zone number from 1
            zone_index = zone_number - 1
        num_layers = num_layers_per_zone[zone_index]

        # Calculate grid cell size in z direction
        nz = num_layers
        dz = sim_box_thickness / nz
        if layers_per_zone is not None:
            dz = sim_box_thickness / layers_per_zone[zone_number - 1]

        if debug_level >= Debug.SOMEWHAT_VERBOSE:
            print('-- Zone: {}'.format(zone_number))
        if debug_level >= Debug.VERBOSE:
            start = grid_attributes.start_layers_per_zone[zone_index]
            end = grid_attributes.end_layers_per_zone[zone_index]
            print('--   Grid layers: {}     Start layer: {}     End layer: {}'.format(num_layers, start + 1, end))

        gauss_result_list_for_zone = []
        for gauss_field_name in gauss_field_names:
            azimuth = zone_model.getAzimuthAngle(gauss_field_name)
            dip = zone_model.getDipAngle(gauss_field_name)
            power = zone_model.getPower(gauss_field_name)
            variogram_type = zone_model.getVariogramType(gauss_field_name)
            v_name = variogram_type.name
            main_range = zone_model.getMainRange(gauss_field_name)
            perpendicular_range = zone_model.getPerpRange(gauss_field_name)
            vertical_range = zone_model.getVertRange(gauss_field_name)

            azimuth_value_sim_box = azimuth - grid_attributes.sim_box_size.azimuth_angle

            if debug_level >= Debug.VERBOSE:
                print(
                    '---  Simulate: {}  for zone: {}  for region: {}'
                    ''.format(gauss_field_name, zone_number, region_number)
                )
            if debug_level >= Debug.VERY_VERBOSE:
                print(
                    '     Zone,region             : ({},{})\n'
                    '     Gauss field name        : {}\n'
                    '     Variogram type          : {}\n'
                    '     Main range              : {}\n'
                    '     Perpendicular range     : {}\n'
                    '     Vertical range          : {}\n'
                    '     Azimuth angle in sim box: {}\n'
                    '     Dip angle               : {}\n'
                    '     NX                      : {}\n'
                    '     NY                      : {}\n'
                    '     NZ for this zone        : {}\n'
                    '     DX                      : {}\n'
                    '     DY                      : {}\n'
                    '     DZ for this zone        : {}'
                    ''.format(
                        zone_number, region_number, gauss_field_name, v_name,
                        main_range, perpendicular_range, vertical_range, azimuth_value_sim_box,
                        dip, nx, ny, nz, dx, dy, dz)
                )

            # Define variogram
            variogram_name = v_name.lower()
            # Note: Since RMS is a left-handed coordinate system and NrLib treat the coordinate system as right-handed
            # we have to transform the azimuth angle to 90-azimuth to get it correct in RMS
            azimuth_in_nrlib = 90.0 - azimuth_value_sim_box
            if variogram_name == 'general_exponential':
                sim_variogram = nrlib.variogram(
                    variogram_name, main_range, perpendicular_range, vertical_range, azimuth_in_nrlib, dip, power
                )
            else:
                sim_variogram = nrlib.variogram(
                    variogram_name, main_range, perpendicular_range, vertical_range, azimuth_in_nrlib, dip
                )

            if debug_level >= Debug.VERY_VERBOSE:
                [nx_padding, ny_padding, nz_padding] = nrlib.simulation_size(sim_variogram, nx, dx, ny, dy, nz, dz)
                print('Debug output: Grid dimensions with padding for simulation:')
                print('     nx: {}   nx with padding: {}'.format(nx, nx_padding))
                print('     ny: {}   ny with padding: {}'.format(ny, ny_padding))
                print('     nz: {}   nz with padding: {}'.format(nz, nz_padding))

            # Simulate gauss field. Return numpy 1D vector in F order
            gauss_vector = nrlib.simulate(sim_variogram, nx, dx, ny, dy, nz, dz)
            gauss_result = np.reshape(gauss_vector, (nx, ny, nz), order='F')
            gauss_result_list_for_zone.append(gauss_result)
            if debug_level >= Debug.VERBOSE:
                print('--- Finished running simulation of {} for zone,region: ({},{})'
                      ''.format(gauss_field_name, zone_number, region_number))
                print('')

        setContinuous3DParameterValuesInZoneRegion(
            grid_model,
            gauss_field_names,
            gauss_result_list_for_zone,
            zone_number,
            regionNumber=region_number,
            regionParamName=aps_model.region_parameter,
            realNumber=realisation,
            isShared=is_shared,
            debug_level=debug_level,
            fmu_mode=fmu_mode,
        )

        add_trends(
            project, aps_model, zone_number, region_number,
            write_rms_parameters_for_qc_purpose=write_rms_parameters_for_qc_purpose,
            debug_level=debug_level,
            fmu_mode=fmu_mode,
        )
        # End loop over gauss fields for one zone

    # End loop over all active zones in the model

    if seed_file_log and aps_model.write_seeds:
        if isinstance(seed_file_log, str):
            seed_file_log = Path(seed_file_log)
        ensure_folder_exists(seed_file_log)
        if seed_file_log.is_dir():
            seed_file_log = seed_file_log / 'seedLogFile.dat'
        with open(seed_file_log, 'a+') as file:
            file.write(
                'RealNumber: {}  StartSeed for this realization: {}\n'.format(realisation + 1, nrlib.seed())
            )
    print('')


def run(roxar=None, project=None, **kwargs):
    model_file = get_specification_file(**kwargs)
    seed_file_log = get_seed_log_file(**kwargs)
    layers_per_zone = kwargs.get('layers_per_zone', None)
    fmu_mode = kwargs.get('fmu_mode', False)
    write_rms_parameters_for_qc_purpose = kwargs.get('write_rms_parameters_for_qc_purpose', True)
    real_number = project.current_realisation
    is_shared = False

    run_simulations(
        project,
        model_file,
        real_number,
        is_shared,
        seed_file_log,
        layers_per_zone=layers_per_zone,
        write_rms_parameters_for_qc_purpose=write_rms_parameters_for_qc_purpose,
        fmu_mode=fmu_mode,
    )
    print('Finished simulation of gaussian fields for APS')


if __name__ == '__main__':
    import roxar

    run(roxar, project)
