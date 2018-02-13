#!/bin/env python
# -*- coding: utf-8 -*-
# This script use both nrlib and ROXAR API functions and run simulations sequentially and not in parallel

from pathlib import Path

import nrlib
import numpy as np

from src.algorithms.APSModel import APSModel
from src.utils.constants.simple import Debug
from src.utils.roxar.generalFunctionsUsingRoxAPI import getGridAttributes, setContinuous3DParameterValuesInZoneRegion


def getProjectRealizationSeed(seedFile):
    try:
        with open(seedFile, 'r') as file:
            seed = int(file.read())
    except:
        raise IOError('Can not open and read seed file: {}'.format(seedFile))
    return seed


def run_simulations(project, modelFile='APS.xml', realNumber=0, isShared=False):
    """
    Description: Run gauss simulations for the APS model i sequence

    """

    # Read APS model
    print('- Read file: ' + modelFile)
    apsModel = APSModel(modelFile)
    debug_level = apsModel.debug_level()
    seedFile = apsModel.getSeedFileName()
    # When running in single processing mode, there will not be created new start seeds in the RMS multi realization workflow loop
    # because the start random seed is created once per process, and the process is the same for all realizations in the loop.
    # Hence always read the start seed in single processing mode.
    # The seed can e.g be defined by using the RMS project realization seed number and should be set into the seed file
    # before calling the current script.
    writeSeedFile = False

    # Get grid dimensions
    gridModelName = apsModel.getGridModelName()
    gridModel = project.grid_models[gridModelName]
    grid = gridModel.get_grid()
    [_, _, _, _, _, _, simBoxXLength, simBoxYLength, azimuthAngleGrid, _, _, nx, ny, nz,
     nZonesGrid, zoneNames, nLayersPerZone, startLayerPerZone, endLayerPerZone] = getGridAttributes(grid, Debug.OFF)

    # Calculate grid cell size
    dx = simBoxXLength/nx
    dy = simBoxYLength/ny

    # Get region parameter name
    regionParamName = apsModel.getRegionParamName()

    # Set start seed if it is defined
    if not writeSeedFile:
        sfile = Path(seedFile)
        if sfile.is_file():
            startSeed = getProjectRealizationSeed(seedFile)
            nrlib.seed(startSeed)
        else:
            raise IOError(
                'Seed file: {} is not defined.\n'
                'This is required when the model has specified to read the seed from file.'.format(seedFile)
            )

    # Loop over all zones and simulate gauss fields
    allZoneModels = apsModel.getAllZoneModelsSorted()
    for key, zoneModel in allZoneModels.items():
        zoneNumber = key[0]
        regionNumber = key[1]
        if not apsModel.isSelected(zoneNumber, regionNumber):
            continue
        gaussFieldNames = zoneModel.getGaussFieldsInTruncationRule()
        simBoxThickness = zoneModel.getSimBoxThickness()

        # Zone index is counted from 0 while zone number from 1
        start = startLayerPerZone[zoneNumber-1]
        end   = endLayerPerZone[zoneNumber-1]
        nLayers = nLayersPerZone[zoneNumber-1]

        # Calculate grid cell size in z direction
        nz = nLayers
        dz =  simBoxThickness/nz

        if debug_level >= Debug.SOMEWHAT_VERBOSE:
            print('-- Zone: {}'.format(str(zoneNumber)))
        if debug_level >= Debug.VERBOSE:
            print('--   Grid layers: {}     Start layer: {}     End layer: {}'
                  ''.format(str(nLayers), str(start+1), str(end+1)))

        gaussResultListForZone = []
        for i in range(len(gaussFieldNames)):
            gaussFieldName = gaussFieldNames[i]
            azimuth = zoneModel.getAnisotropyAzimuthAngle(gaussFieldName)
            dip     = zoneModel.getAnisotropyDipAngle(gaussFieldName)
            power = zoneModel.getPower(gaussFieldName)
            variogramType = zoneModel.getVariogramType(gaussFieldName)
            vName = variogramType.name
            mainRange = zoneModel.getMainRange(gaussFieldName)
            perpRange = zoneModel.getPerpRange(gaussFieldName)
            vertRange = zoneModel.getVertRange(gaussFieldName)

            azimuthValueSimBox = azimuth - azimuthAngleGrid

            if debug_level >= Debug.VERBOSE:
                print('---  Simulate: {}  for zone: {}  for region: {}'
                      ''.format(gaussFieldName, str(zoneNumber), str(regionNumber)))
            if debug_level >= Debug.VERY_VERBOSE:
                print('     Zone,region             : ({},{})'.format(str(zoneNumber), str(regionNumber)))
                print('     Gauss field name        : {}'.format(gaussFieldName))
                print('     Variogram type          : {}'.format(vName))
                print('     Main range              : {}'.format(str(mainRange)))
                print('     Perpendicular range     : {}'.format(str(perpRange)))
                print('     Vertical range          : {}'.format(str(vertRange)))
                print('     Azimuth angle in sim box: {}'.format(str(azimuthValueSimBox)))
                print('     Dip angle               : {}'.format(str(dip)))
                print('     NX                      : {}'.format(str(nx)))
                print('     NY                      : {}'.format(str(ny)))
                print('     NZ for this zone        : {}'.format(str(nz)))
                print('     DX                      : {}'.format(str(dx)))
                print('     DY                      : {}'.format(str(dy)))
                print('     DZ for this zone        : {}'.format(str(dz)))

            # Define variogram
            variogramName = vName.lower()
            # Note: Since RMS is a left-handed coordinate system and NrLib treat the coordinate system as right-handed
            # we have to transform the azimuth angle to 90-azimuth to get it correct in RMS
            azimuthInNRLIB = 90.0 - azimuthValueSimBox
            if variogramName == 'general_exponential':
                simVariogram = nrlib.variogram(
                    variogramName, mainRange, perpRange, vertRange, azimuthInNRLIB, dip, power
                )
            else:
                simVariogram = nrlib.variogram(
                    variogramName, mainRange, perpRange, vertRange, azimuthInNRLIB, dip
                )

            if debug_level >= Debug.VERY_VERBOSE:
                [nx_padding, ny_padding, nz_padding] = nrlib.simulation_size(simVariogram, nx, dx, ny, dy, nz, dz)
                print('Debug output: Grid dimensions with padding for simulation:')
                print('     nx: {}   nx with padding: {}'.format(str(nx), str(nx_padding)))
                print('     ny: {}   ny with padding: {}'.format(str(ny), str(ny_padding)))
                print('     nz: {}   nz with padding: {}'.format(str(nz), str(nz_padding)))

            # Simulate gauss field. Return numpy 1D vector in F order
            gaussVector = nrlib.simulate(simVariogram, nx, dx, ny, dy, nz, dz)
            gaussResult = np.reshape(gaussVector, (nx, ny, nz), order='F')
            gaussResultListForZone.append(gaussResult)
            if debug_level >= Debug.VERBOSE:
                print('--- Finished running simulation of {} for zone,region: ({},{})'
                      ''.format(gaussFieldName, str(zoneNumber), str(regionNumber)))
                print('')

        # End loop over gauss fields for one zone
        setContinuous3DParameterValuesInZoneRegion(
            gridModel, gaussFieldNames, gaussResultListForZone, zoneNumber-1,
            regionNumber=regionNumber, regionParamName=regionParamName,
            realNumber=realNumber, isShared=isShared, debug_level=debug_level
        )
    # End loop over all active zones in the model

    if writeSeedFile:
        with open(seedFile, 'w') as file:
            startSeed = nrlib.seed()
            file.write(str(startSeed))

    seedFileLog = 'seedLogFile.dat'
    startSeed = nrlib.seed()
    with open(seedFileLog, 'a') as file:
        file.write(
            'RealNumber: {}  StartSeed for this realization: {}\n'.format(
                str(realNumber + 1), str(startSeed))
        )
    print('')


def run(roxar=None, project=None):
    modelFile = 'APS.xml'
    realNumber = project.current_realisation
    isShared = False
    run_simulations(project, modelFile=modelFile, realNumber=realNumber, isShared=isShared)
    print('Finished simulation of gaussian fields for APS')


if __name__ == '__main__':
    import roxar
    run(roxar, project)
