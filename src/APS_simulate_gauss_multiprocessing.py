#!/bin/env python
# This script does not call ROXAR API functions

use_multiprocessing = True
testing_multi_processing = False
import sys
import time
import copy
import numpy as np
import importlib

import nrlib


import src.APSModel 
import src.APSZoneModel 
import src.APSRandomSeed 
import src.APSDataFromRMS

importlib.reload(src.APSModel)
importlib.reload(src.APSZoneModel)
importlib.reload(src.APSRandomSeed)
importlib.reload(src.APSDataFromRMS)


from src.APSModel import APSModel
from src.APSZoneModel import APSZoneModel
from src.APSRandomSeed import APSRandomSeed
from src.APSDataFromRMS import APSDataFromRMS
from src.utils.constants.simple import Debug, VariogramType


if use_multiprocessing:
    import multiprocessing as mp

def simulateGauss(simParamObject,outputDir,logFileName=None, debug_level=Debug.OFF):
    zoneNumber = simParamObject['zoneNumber']
    regionNumber = simParamObject['regionNumber']
    gaussFieldName = simParamObject['gaussFieldName']
    variogramType  = simParamObject['variogramType']
    mainRange = simParamObject['mainRange']
    perpRange = simParamObject['perpRange']
    vertRange = simParamObject['vertRange']
    azimuth   = simParamObject['azimuth']
    dip   = simParamObject['dip']
    power = simParamObject['power']
    nx = simParamObject['nx']
    ny = simParamObject['ny']
    nz = simParamObject['nz']
    dx = simParamObject['dx']
    dy = simParamObject['dy']
    dz = simParamObject['dz']
    startSeed = simParamObject['seed']
    if logFileName is not None:
        file = open(logFileName,'w')
        file.write('\n')
        file.write('    Call simulateGauss for (zone,region): ({},{}) for field: {}\n'.format(str(zoneNumber), str(regionNumber), gaussFieldName))
        file.write('    Zone,region             : ({},{})'.format(str(zoneNumber), str(regionNumber)))
        file.write('    Gauss field name        : {}\n'.format(gaussFieldName))
        file.write('    Variogram type          : {}\n'.format(variogramType))
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
        print('    Variogram type          : {}'.format(variogramType))
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
    if testing_multi_processing:
        result = [zoneNumber, regionNumber, gaussFieldName, simParamObject]
        print('Call simulateGauss for {}'.format(gaussFieldName))
        return

    # Define variogram
    variogramName = variogramMapping[variogramType.name]
#    print('Variogram to be used in nrlib.simulate: {}'.format(variogramName))
    if variogramName == 'general_exponential':
        simVariogram = nrlib.variogram(variogramName, mainRange, perpRange, vertRange, azimuth, dip, power)
    else:
        simVariogram = nrlib.variogram(variogramName, mainRange, perpRange, vertRange, azimuth, dip)


    # Simulate gauss field. Return numpy 1D vector in F order
    if startSeed != 0:
        nrlib.seed(startSeed)
#    else:
#        startSeed = nrlib.seed()
    [nx_padding, ny_padding, nz_padding] = nrlib.simulation_size(simVariogram, nx, dx, ny, dy, nz, dz)
    if logFileName is not None:
        file.write('    Simulation grid size with padding due to correlation lengths for gauss field {} for zone,region: ({},{})\n'
                   ''.format(gaussFieldName, str(zoneNumber), str(regionNumber)))
        file.write('      nx with padding: {}\n'.format(str(nx_padding)))
        file.write('      ny with padding: {}\n'.format(str(ny_padding)))
        file.write('      nz with padding: {}\n'.format(str(nz_padding)))
    gaussVector = nrlib.simulate(simVariogram, nx, dx, ny, dy, nz, dz)
    # write result to binary file using numpy binary file format
    fileName = outputDir + '/' + gaussFieldName + '_' + str(zoneNumber) + '_' + str(regionNumber)
    np.save(fileName,gaussVector)
    endSeed = nrlib.seed()
    if logFileName is not None:
#        file.write('    Start seed: {}\n'.format(str(startSeed)))
        file.write('    End   seed: {}\n'.format(str(endSeed)))
        file.write('    Write file: {}\n'.format(fileName))
        file.write('    Finished running simulation of {} for zone,region: ({},{})\n'.format(gaussFieldName, str(zoneNumber), str(regionNumber)))
        file.write('')
        file.close()

    if debug_level >= Debug.VERBOSE:
#        print('    Start seed: {}'.format(str(startSeed)))
        print('    Write file: {}'.format(fileName))
        print('    Finished running simulation of {} for zone,region: ({},{})'.format(gaussFieldName, str(zoneNumber), str(regionNumber)))
        print('')



def run_simulations(
    modelFile='APS.xml',
    rms_data_file_name='rms_project_data_for_APS_gui.xml',
    outputDir='./tmp_gauss_sim',
    seedFile='./seedFile.dat',
    writeLogFile=True):
    """
    Description: Run gauss simulations for the APS model

    """

    # Read APS model
    print('- Read file: ' + modelFile)
    apsModel = APSModel(modelFile)
    debug_level = apsModel.debug_level()



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

    if seedFile is not None:
        seedData = APSRandomSeed(seedFile)

    # Loop over all zones and simulate gauss fields
    allZoneModels = apsModel.getAllZoneModelsSorted()        
    for key, zoneModel in allZoneModels.items():
        zoneNumber = key[0]
        regionNumber = key[1]
        if not apsModel.isSelected(zoneNumber, regionNumber):
            continue
        gaussFieldNames = zoneModel.getUsedGaussFieldNames()
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
            dz =  simBoxThickness/nz

            # Get random seed
            if seedData.checkReadSeedFile():
                startSeed=seedData.getSeed(gaussFieldName,zoneNumber,regionNumber)
            else:
                startSeed = 0
            # print('Start seed: {}'.format(str(startSeed)))
            
            # Define data set for simulation
            simParam = {}
            simParam['zoneNumber'] = zoneNumber
            simParam['regionNumber'] = regionNumber
            simParam['gaussFieldName'] = gaussFieldName
            simParam['variogramType'] = variogramType
            simParam['mainRange'] = mainRange
            simParam['perpRange'] = perpRange
            simParam['vertRange'] = vertRange
            simParam['azimuth'] = azimuthValueSimBox
            simParam['dip'] = dipValue
            simParam['nx'] = nx
            simParam['ny'] = ny
            simParam['nz'] = nz
            simParam['dx'] = dx
            simParam['dy'] = dy
            simParam['dz'] = dz
            simParam['power'] = power
            simParam['seed'] = startSeed
            if use_multiprocessing:
                # Add process to simulate gauss field
                logFileName=None
                if writeLogFile:
                    logFileName = outputDir + '/' + gaussFieldName + '_' + str(zoneNumber) + '_' + str(regionNumber) + '.log'
                debug_level = Debug.OFF
                print('- Simulate: {} for zone: {} for region: {}'.format(gaussFieldName, str(zoneNumber), str(regionNumber)))
                simGaussProcess = mp.Process(target=simulateGauss,args=(simParam, outputDir, logFileName, debug_level))
                processes.append(simGaussProcess)
            else:
                # Add process to simulate gauss field
                logFileName=None
                if writeLogFile:
                    logFileName = outputDir + '/' + gaussFieldName + '_' + str(zoneNumber) + '_' + str(regionNumber) + '.log'
                debug_level = Debug.OFF
                print('- Simulate: {} for zone: {} for region: {}'.format(gaussFieldName, str(zoneNumber), str(regionNumber)))
                simulateGauss(simParam, outputDir, logFileName, debug_level)
        # End loop over gauss fields for one zone

        if use_multiprocessing:
            # Submit simulations of all gauss fields for current zone,region model and wait for the result
            # 'Run processes'
            for p in processes:
                p.start()

            # Exit processes
            for p in processes:
                p.join()
    # End loop over all active zones in the model
    print('')
    print('- Finished simulating all gaussian fields')
    print('')
    
        
if __name__ == '__main__':
    modelFile='APS.xml'
    rms_data_file_name='rms_project_data_for_APS_gui.xml'
    outputDir='./tmp_gauss_sim'
    seedFile='./seedFile.dat'
    writeLogFile=True

    run_simulations(
        modelFile=modelFile, 
        rms_data_file_name=rms_data_file_name, 
        outputDir=outputDir, 
        seedFile=seedFile, 
        writeLogFile=writeLogFile 
        )
