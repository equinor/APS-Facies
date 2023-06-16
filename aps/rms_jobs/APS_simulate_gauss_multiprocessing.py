#!/bin/env python
# -*- coding: utf-8 -*-
# This script does not call ROXAR API functions

import os
import time
import numpy as np
import multiprocessing as mp

from aps.algorithms.APSModel import APSModel
from aps.utils.methods import get_run_parameters
from aps.utils.roxar.APSDataFromRMS import APSDataFromRMS
from aps.utils.constants.simple import Debug


def simulateGauss(
        simParamObject, outputDir, logFileName=None, seedFileName=None,
        writeSeedFile=True, debug_level=Debug.OFF
):
    import gaussianfft
    zone_number = simParamObject['zoneNumber']
    region_number = simParamObject['regionNumber']
    gauss_field_name = simParamObject['gaussFieldName']
    variogram_type = simParamObject['variogramType']
    main_range = simParamObject['mainRange']
    perpendicular_range = simParamObject['perpRange']
    vertical_range = simParamObject['vertRange']
    azimuth = simParamObject['azimuth']
    dip = simParamObject['dip']
    power = simParamObject['power']
    nx = simParamObject['nx']
    ny = simParamObject['ny']
    nz = simParamObject['nz']
    dx = simParamObject['dx']
    dy = simParamObject['dy']
    dz = simParamObject['dz']

    description = f'''
    Zone,region             : ({zone_number}, {region_number})
    Gauss field name        : {gauss_field_name}
    Variogram type          : {variogram_type.name}
    Main range              : {main_range}
    Perpendicular range     : {perpendicular_range}
    Vertical range          : {vertical_range}
    Azimuth angle in sim box: {azimuth}
    Dip angle               : {dip}
    NX                      : {nx}
    NY                      : {ny}
    NZ for this zone        : {nz}
    DX                      : {dx}
    DY                      : {dy}
    DZ for this zone        : {dz}
'''
    if logFileName is not None:
        file = open(logFileName, 'w', encoding='utf-8')
        file.write(description)

    if debug_level >= Debug.VERBOSE:
        print('')
        print(f'    Call simulateGauss for (zone,region): ({zone_number}, {region_number}) for field: {gauss_field_name}')
    if debug_level >= Debug.VERY_VERBOSE:
        print(description)

    variogram_mapping = {
        'EXPONENTIAL': 'exponential',
        'SPHERICAL': 'spherical',
        'GAUSSIAN': 'gaussian',
        'GENERAL_EXPONENTIAL': 'general_exponential',
        'MATERN32': 'matern32',
        'MATERN52': 'matern52',
        'MATERN72': 'matern72',
        'CONSTANT': 'constant'
        }

    if not (writeSeedFile or seedFileName is None):
        # Read start seed from seed file for current gauss field, zone and region
        # Initialize start seed
        try:
            with open(seedFileName, 'r', encoding='utf-8') as sfile:
                inputString = sfile.read()
                words = inputString.split()
                startSeed = -1
                for i in range(len(words)):
                    w = words[i]
                    if w == gauss_field_name:
                        zNr = int(words[i + 1])
                        rNr = int(words[i + 2])
                        if zNr == zone_number and rNr == region_number:
                            # Found the correct line for the seed
                            startSeed = int(words[i + 3])
                            if debug_level >= Debug.VERY_VERBOSE:
                                print('  Read seed: {} from seed file: {}'.format(startSeed, seedFileName))
                            break
                if startSeed == -1:
                    raise IOError(
                        f'The seed file: {seedFileName} does not contain seed value for '
                        f'gauss field name: {gauss_field_name}'
                        f'   zone number: {zone_number}    and region number: {region_number}'
                    )
        except Exception:
            raise IOError(f'Can not open and read seed file: {seedFileName}')

        if debug_level >= Debug.ON:
            print(f'-  Start seed: {startSeed}')
        gaussianfft.seed(startSeed)

    # Define variogram
    variogramName = variogram_mapping[variogram_type.name]

    #  Note that since RMS uses left-handed coordinate system while gaussianfft uses right-handed coordinate system, we have to use
    #  azimuth for gaussianfft simulation equal to: ( 90 - specified azimuth in simulation box).
    if variogramName == 'general_exponential':
        simVariogram = gaussianfft.variogram(variogramName, main_range, perpendicular_range, vertical_range, 90.0 - azimuth, dip, power)
    else:
        simVariogram = gaussianfft.variogram(variogramName, main_range, perpendicular_range, vertical_range, 90.0 - azimuth, dip)

    # Simulate gauss field. Return numpy 1D vector in F order. Get padding + grid size as information
    [nx_padding, ny_padding, nz_padding] = gaussianfft.simulation_size(simVariogram, nx, dx, ny, dy, nz, dz)
    if logFileName is not None:
        file.write(f'''
    Simulation grid size with padding due to correlation lengths for gauss field {gauss_field_name} for zone,region: ({zone_number}, {region_number})
      nx with padding: {nx_padding}
      ny with padding: {ny_padding}
      nz with padding: {nz_padding}
''')
    gaussVector = gaussianfft.simulate(simVariogram, nx, dx, ny, dy, nz, dz)

    # Get the start seed
    startSeed = gaussianfft.seed()
    if debug_level >= Debug.VERBOSE:
        print(f'    Start seed: {startSeed}')

    # write result to binary file using numpy binary file format
    fileName = f'{outputDir}/{gauss_field_name}_{zone_number}_{region_number}'
    np.save(fileName, gaussVector)

    if logFileName is not None:
        file.write(f'''\
    Start seed: {startSeed}
    Write file: {fileName}
    Finished running simulation of {gauss_field_name} for zone,region: ({zone_number}, {region_number})

''')
        file.close()
        if debug_level >= Debug.VERBOSE:
            print(f'    Write file: {logFileName}')

    if writeSeedFile and seedFileName is not None:
        file = open(seedFileName, 'w', encoding='utf-8')
        file.write(f' {gauss_field_name}  {zone_number}  {region_number}  {startSeed}\n')
        file.close()
        if debug_level >= Debug.VERBOSE:
            print(f'    Write file: {seedFileName}')

    if debug_level >= Debug.VERBOSE:
        print(f'    Write file: {fileName}')
        print(f'    Finished running simulation of {gauss_field_name} for zone,region: ({zone_number}, {region_number})')
        print('')


def run_simulations(
    model_file='APS.xml',
    rms_data_file_name='rms_project_data_for_APS_gui.xml',
    output_dir='./tmp_gauss_sim',
    write_log_file=True,
):
    """
    Description: Run gauss simulations for the APS model

    """

    # Read APS model
    print(f'- Read file: {model_file}')
    aps_model = APSModel(model_file)
    debug_level = aps_model.debug_level
    seed_file_name = aps_model.seed_file_name
    write_seed_file = aps_model.write_seeds
    if debug_level >= Debug.ON:
        if write_seed_file:
            print(f'Write seed file: {seed_file_name}')
        else:
            print(f'Read seed file: {seed_file_name}')

    # Get grid dimensions

    grid_model_name = aps_model.grid_model_name

    if debug_level >= Debug.VERBOSE:
        print(f'- Read file: {rms_data_file_name}')
    rms_data = APSDataFromRMS(debug_level=debug_level)

    rms_data.readRMSDataFromXMLFile(rms_data_file_name)
    grid_model_name_from_rms_data = rms_data.grid_model_name
    if grid_model_name != grid_model_name_from_rms_data:
        raise IOError(
            f'The specified grid model in model file: {grid_model_name} and '
            f'in RMS data file: {grid_model_name_from_rms_data} are different.\n'
            'You may have to fix the model file or extract data from RMS for correct grid model again'
        )
    nx, ny, _, _, sim_box_x_length, sim_box_y_length, _, _, azimuth_angle_grid = rms_data.getGridSize()

    # Calculate grid cell size
    dx = sim_box_x_length/nx
    dy = sim_box_y_length/ny

    # Loop over all zones and simulate gauss fields
    all_zone_models = aps_model.sorted_zone_models
    for key, zone_model in all_zone_models.items():
        zone_number, region_number = key
        if not aps_model.isSelected(zone_number, region_number):
            continue
        gauss_field_names = zone_model.getGaussFieldsInTruncationRule()
        [start, end] = rms_data.getStartAndEndLayerInZone(zone_number)
        num_layers = rms_data.getNumberOfLayersInZone(zone_number)

        processes = []
        for gauss_field_name in gauss_field_names:
            azimuth = zone_model.getAzimuthAngle(gauss_field_name)
            dip     = zone_model.getDipAngle(gauss_field_name)
            power = zone_model.getPower(gauss_field_name)
            variogram_type = zone_model.getVariogramType(gauss_field_name)
            main_range = zone_model.getMainRange(gauss_field_name)
            perpendicular_range = zone_model.getPerpRange(gauss_field_name)
            vertical_range = zone_model.getVertRange(gauss_field_name)

            azimuth_value_sim_box = azimuth - azimuth_angle_grid
            sim_box_thickness = zone_model.sim_box_thickness

            # Calculate grid cell size in z direction
            nz = num_layers
            dz = sim_box_thickness / nz

            # Define data set for simulation
            sim_param = {
                'zoneNumber': zone_number,
                'regionNumber': region_number,
                'gaussFieldName': gauss_field_name,
                'variogramType': variogram_type,
                'mainRange': main_range,
                'perpRange': perpendicular_range,
                'vertRange': vertical_range,
                'azimuth': azimuth_value_sim_box,
                'dip': dip,
                'nx': nx, 'ny': ny, 'nz': nz,
                'dx': dx, 'dy': dy, 'dz': dz,
                'power': power,
            }

            # Add process to simulate gauss field
            log_file_name = None
            if write_log_file:
                log_file_name = f'{output_dir}/{gauss_field_name}_{zone_number}_{region_number}.log'
            if write_seed_file:
                seed_file_name_for_this_process = f'{output_dir}/seed_{gauss_field_name}_{zone_number}_{region_number}'
            else:
                seed_file_name_for_this_process = seed_file_name
            sim_gauss_process = mp.Process(
                target=simulateGauss,
                args=(
                    sim_param, output_dir, log_file_name, seed_file_name_for_this_process, write_seed_file, debug_level,
                )
            )
            processes.append(sim_gauss_process)
        # End loop over gauss fields for one zone

        # Submit simulations of all gauss fields for the current zone/region model and wait for the result
        # 'Run processes'
        for i in range(len(processes)):
            p = processes[i]
            gauss_field_name = gauss_field_names[i]
            print(f'- Start simulate: {gauss_field_name} for zone: {zone_number} for region: {region_number}')
            p.start()
            # Wait at least one second before continuing to ensure that automatically generated start seed values are
            # different since seed values are generated automatically based on clock time.
            time.sleep(1.05)

        # Exit processes
        for p in processes:
            p.join()
    # End loop over all active zones in the model

    if write_seed_file:
        # Make one seed file for all gauss simulations which can be used to reproduce the realizations
        command = f'cat {output_dir}/seed_* > {seed_file_name}'
        os.system(command)
        if debug_level >= Debug.ON:
            print(f'- Write seed file: {seed_file_name}')
    print('')
    print('- Finished simulating all gaussian fields')
    print('')


def run(roxar=None, project=None, **kwargs):
    params = get_run_parameters(**kwargs)
    model_file = params['model_file']
    rms_data_file_name = params['rms_data_file']
    output_dir = params['input_directory']
    write_log_file = params['write_log_file']
    run_simulations(
        model_file=model_file,
        rms_data_file_name=rms_data_file_name,
        output_dir=output_dir,
        write_log_file=write_log_file
    )


if __name__ == '__main__':
    run()
