#!/bin/env python
# -*- coding: utf-8 -*-
# This script does not call ROXAR API functions

import os
import time
import numpy as np
import multiprocessing as mp

from src.algorithms.APSModel import APSModel
from src.utils.methods import get_run_parameters
from src.utils.roxar.APSDataFromRMS import APSDataFromRMS
from src.utils.constants.simple import Debug


def simulateGauss(
        simParamObject, outputDir, logFileName=None, seedFileName=None,
        writeSeedFile=True, debug_level=Debug.OFF
):
    import nrlib
    zoneNumber = simParamObject['zoneNumber']
    regionNumber = simParamObject['regionNumber']
    gaussFieldName = simParamObject['gaussFieldName']
    variogramType = simParamObject['variogramType']
    mainRange = simParamObject['mainRange']
    perpRange = simParamObject['perpRange']
    vertRange = simParamObject['vertRange']
    azimuth = simParamObject['azimuth']
    dip = simParamObject['dip']
    power = simParamObject['power']
    nx = simParamObject['nx']
    ny = simParamObject['ny']
    nz = simParamObject['nz']
    dx = simParamObject['dx']
    dy = simParamObject['dy']
    dz = simParamObject['dz']
    if logFileName is not None:
        file = open(logFileName,'w')
        file.write('\n')
        file.write('    Zone,region             : ({},{})'.format(str(zoneNumber), str(regionNumber)))
        file.write('    Gauss field name        : {}\n'.format(gaussFieldName))
        file.write('    Variogram type          : {}\n'.format(variogramType.name))
        file.write('    Main range              : {}\n'.format(str(mainRange)))
        file.write('    Perpendicular range     : {}\n'.format(str(perpRange)))
        file.write('    Vertical range          : {}\n'.format(str(vertRange)))
        file.write('    Azimuth angle in sim box: {}\n'.format(str(azimuth)))
        file.write('    Dip angle               : {}\n'.format(str(dip)))
        file.write('    NX                      : {}\n'.format(str(nx)))
        file.write('    NY                      : {}\n'.format(str(ny)))
        file.write('    NZ for this zone        : {}\n'.format(str(nz)))
        file.write('    DX                      : {}\n'.format(str(dx)))
        file.write('    DY                      : {}\n'.format(str(dy)))
        file.write('    DZ for this zone        : {}\n'.format(str(dz)))

    if debug_level >= Debug.VERBOSE:
        print('')
        print('    Call simulateGauss for (zone,region): ({},{}) for field: {}'.format(str(zoneNumber), str(regionNumber), gaussFieldName))
    if debug_level >= Debug.VERY_VERBOSE:
        print('    Zone,region             : ({},{})'.format(str(zoneNumber), str(regionNumber)))
        print('    Gauss field name        : {}'.format(gaussFieldName))
        print('    Variogram type          : {}'.format(variogramType.name))
        print('    Main range              : {}'.format(str(mainRange)))
        print('    Perpendicular range     : {}'.format(str(perpRange)))
        print('    Vertical range          : {}'.format(str(vertRange)))
        print('    Azimuth angle in sim box: {}'.format(str(azimuth)))
        print('    Dip angle               : {}'.format(str(dip)))
        print('    NX                      : {}'.format(str(nx)))
        print('    NY                      : {}'.format(str(ny)))
        print('    NZ for this zone        : {}'.format(str(nz)))
        print('    DX                      : {}'.format(str(dx)))
        print('    DY                      : {}'.format(str(dy)))
        print('    DZ for this zone        : {}'.format(str(dz)))

    variogramMapping = {
        'EXPONENTIAL': 'exponential',
        'SPHERICAL': 'spherical',
        'GAUSSIAN': 'gaussian',
        'GENERAL_EXPONENTIAL': 'general_exponential',
        'MATERN32':'matern32',
        'MATERN52':'matern52',
        'MATERN72':'matern72',
        'CONSTANT':'constant'
        }

    if not writeSeedFile and seedFileName is not None:
        # Read start seed from seed file for current gauss field, zone and region
        # Initialize start seed
        try:
            with open(seedFileName,'r') as sfile:
                inputString =  sfile.read()
                words = inputString.split()
                startSeed = -1
                for i in range(len(words)):
                    w = words[i]
                    if w == gaussFieldName:
                        zNr = int(words[i+1])
                        rNr = int(words[i+2])
                        if zNr == zoneNumber and rNr == regionNumber:
                            # Found the correct line for the seed
                            startSeed = int(words[i+3])
                            if debug_level >= Debug.VERY_VERBOSE:
                                print('  Read seed: {} from seed file: {}'.format(str(startSeed), seedFileName))
                            break
                if startSeed == -1:
                    raise IOError(
                        'The seed file: {} does not contain seed value for '
                        'gauss field name: {}   zone number: {}    and region number: {}'.format(
                            seedFileName, str(gaussFieldName), str(zoneNumber), str(regionNumber)
                        )
                    )
        except:
            raise IOError('Can not open and read seed file: {}'.format(seedFileName))

    nrlib.seed(startSeed)

    # Define variogram
    variogramName = variogramMapping[variogramType.name]

    #  Note that since RMS uses left-handed coordinate system while nrlib uses right-handed coordinate system, we have to use
    #  azimuth for nrlib simulation equal to: ( 90 - specified azimuth in simulation box).
    if variogramName == 'general_exponential':
        simVariogram = nrlib.variogram(variogramName, mainRange, perpRange, vertRange, 90.0 - azimuth, dip, power)
    else:
        simVariogram = nrlib.variogram(variogramName, mainRange, perpRange, vertRange, 90.0 - azimuth, dip)

    # Simulate gauss field. Return numpy 1D vector in F order. Get padding + grid size as information
    [nx_padding, ny_padding, nz_padding] = nrlib.simulation_size(simVariogram, nx, dx, ny, dy, nz, dz)
    if logFileName is not None:
        file.write('    Simulation grid size with padding due to correlation lengths for gauss field {} for zone,region: ({},{})\n'
                   ''.format(gaussFieldName, str(zoneNumber), str(regionNumber)))
        file.write('      nx with padding: {}\n'.format(str(nx_padding)))
        file.write('      ny with padding: {}\n'.format(str(ny_padding)))
        file.write('      nz with padding: {}\n'.format(str(nz_padding)))
    gaussVector = nrlib.simulate(simVariogram, nx, dx, ny, dy, nz, dz)

    # Get the start seed
    startSeed = nrlib.seed()
    if debug_level >= Debug.VERBOSE:
        print('    Start seed: {}'.format(startSeed))

    # write result to binary file using numpy binary file format
    fileName = outputDir + '/' + gaussFieldName + '_' + str(zoneNumber) + '_' + str(regionNumber)
    np.save(fileName,gaussVector)

    if logFileName is not None:
        file.write('    Start seed: {}\n'.format(str(startSeed)))
        file.write('    Write file: {}\n'.format(fileName))
        file.write('    Finished running simulation of {} for zone,region: ({},{})\n'.format(gaussFieldName, str(zoneNumber), str(regionNumber)))
        file.write('')
        file.close()
        if debug_level >= Debug.VERBOSE:
            print('    Write file: {}'.format(logFileName))

    if writeSeedFile:
        # Save start seed if writeSeedFile is True and seedFileName is defined
        if seedFileName is not None:
            file = open(seedFileName,'w')
            file.write(' {}  {}  {}  {}\n'
                       ''.format(gaussFieldName, str(zoneNumber), str(regionNumber), str(startSeed))
                       )
            file.close()
            if debug_level >= Debug.VERBOSE:
                print('    Write file: {}'.format(seedFileName))

    if debug_level >= Debug.VERBOSE:
        print('    Write file: {}'.format(fileName))
        print('    Finished running simulation of {} for zone,region: ({},{})'.format(gaussFieldName, str(zoneNumber), str(regionNumber)))
        print('')


def run_simulations(
    modelFile='APS.xml',
    rms_data_file_name='rms_project_data_for_APS_gui.xml',
    outputDir='./tmp_gauss_sim',
    writeLogFile=True):
    """
    Description: Run gauss simulations for the APS model

    """

    # Read APS model
    print('- Read file: ' + modelFile)
    apsModel = APSModel(modelFile)
    debug_level = apsModel.debug_level()
    seedFileName = apsModel.getSeedFileName()
    writeSeedFile = apsModel.writeSeeds
    print('Write seed file: '+str(writeSeedFile))

    # Get grid dimensions

    gridModelName = apsModel.getGridModelName()

    if debug_level >= Debug.VERBOSE:
        print('- Read file: {rms_data_file_name}'.format(rms_data_file_name=rms_data_file_name))
    rmsData = APSDataFromRMS()

    rmsData.readRMSDataFromXMLFile(rms_data_file_name)
    gridModelNameFromRMSData = rmsData.getGridModelName()
    if gridModelName != gridModelNameFromRMSData:
        raise IOError(
            'The specified grid model in model file: {} and in RMS data file: {} are different.\n'
            'You may have to fix the model file or extract data from RMS for correct grid model again'.format(gridModelName, gridModelNameFromRMSData)
            )
    [nx, ny, _, _, simBoxXLength, simBoxYLength, _, _, azimuthAngleGrid] = rmsData.getGridSize()

    # Calculate grid cell size
    dx = simBoxXLength/nx
    dy = simBoxYLength/ny

    # Loop over all zones and simulate gauss fields
    allZoneModels = apsModel.getAllZoneModelsSorted()
    for key, zoneModel in allZoneModels.items():
        zoneNumber = key[0]
        regionNumber = key[1]
        if not apsModel.isSelected(zoneNumber, regionNumber):
            continue
        gaussFieldNames = zoneModel.getGaussFieldsInTruncationRule()
        [start, end] = rmsData.getStartAndEndLayerInZone(zoneNumber)
        nLayers = rmsData.getNumberOfLayersInZone(zoneNumber)

        processes = []
        for i in range(len(gaussFieldNames)):
            gaussFieldName = gaussFieldNames[i]
            azimuthValue = zoneModel.getAnisotropyAzimuthAngle(gaussFieldName)
            dipValue     = zoneModel.getAnisotropyDipAngle(gaussFieldName)
            power = zoneModel.getPower(gaussFieldName)
            variogramType = zoneModel.getVariogramType(gaussFieldName)
            mainRange = zoneModel.getMainRange(gaussFieldName)
            perpRange = zoneModel.getPerpRange(gaussFieldName)
            vertRange = zoneModel.getVertRange(gaussFieldName)

            azimuthValueSimBox = azimuthValue - azimuthAngleGrid
            simBoxThickness = zoneModel.getSimBoxThickness()

            # Calculate grid cell size in z direction
            nz = nLayers
            dz = simBoxThickness/nz

            # Define data set for simulation
            simParam = {
                'zoneNumber': zoneNumber,
                'regionNumber': regionNumber,
                'gaussFieldName': gaussFieldName,
                'variogramType': variogramType,
                'mainRange': mainRange,
                'perpRange': perpRange,
                'vertRange': vertRange,
                'azimuth': azimuthValueSimBox,
                'dip': dipValue,
                'nx': nx, 'ny': ny, 'nz': nz,
                'dx': dx, 'dy': dy, 'dz': dz,
                'power': power,
            }

            # Add process to simulate gauss field
            logFileName=None
            if writeLogFile:
                logFileName = outputDir + '/' + gaussFieldName + '_' + str(zoneNumber) + '_' + str(regionNumber) + '.log'
            #debug_level = Debug.OFF
            if writeSeedFile:
                seedFileNameForThisProcess = outputDir + '/' + 'seed_' + gaussFieldName + '_' + str(zoneNumber) + '_' + str(regionNumber)
            else:
                seedFileNameForThisProcess = seedFileName
            simGaussProcess = mp.Process(
                target=simulateGauss,
                args=(simParam, outputDir, logFileName, seedFileNameForThisProcess, writeSeedFile, debug_level)
            )
            processes.append(simGaussProcess)
        # End loop over gauss fields for one zone

        # Submit simulations of all gauss fields for current zone,region model and wait for the result
        # 'Run processes'
        for p in processes:
            print('- Start simulate: {} for zone: {} for region: {}'.format(gaussFieldName, str(zoneNumber), str(regionNumber)))
            p.start()
            # Wait at least one second before continuing to ensure that automatically generated start seed values are different
            # since seed values are generated automatically based on clock time.
            time.sleep(1.05)

        # Exit processes
        for p in processes:
            p.join()
    # End loop over all active zones in the model

    if writeSeedFile:
        # Make one seed file for all gauss simulations which can be used to reproduce the realizations
        command = 'cat ' + outputDir + '/' + 'seed_* > ' + seedFileName
        print('command: ' + command)
        os.system(command)
        if debug_level >= Debug.ON:
            print('- Write seed file: {}'.format(seedFileName))
    print('')
    print('- Finished simulating all gaussian fields')
    print('')


def run(roxar=None, project=None, **kwargs):
    model_file, rms_data_file_name, _, output_dir, _ = get_run_parameters(**kwargs)
    write_log_file = True
    run_simulations(
        modelFile=model_file,
        rms_data_file_name=rms_data_file_name,
        outputDir=output_dir,
        writeLogFile=write_log_file
    )


if __name__ == '__main__':
    run()
