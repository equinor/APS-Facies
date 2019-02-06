#!/bin/env python
# -*- coding: utf-8 -*-
# This script use both nrlib and ROXAR API functions and run simulations sequentially and not in parallel

import nrlib
import numpy as np

from src.algorithms.APSModel import APSModel
from src.utils.constants.simple import Debug
from src.utils.methods import get_specification_file
from src.utils.roxar.generalFunctionsUsingRoxAPI import (
    setContinuous3DParameterValuesInZoneRegion,
    get_project_realization_seed,
)
from src.utils.roxar.grid_model import getGridAttributes


def run_simulations(project, modelFile='APS.xml', realNumber=0, isShared=False):
    """
    Description: Run gauss simulations for the APS model i sequence

    """

    # Read APS model
    print('- Read file: ' + modelFile)
    apsModel = APSModel(modelFile)
    debug_level = apsModel.debug_level
    # When running in single processing mode, there will not be created new start seeds in the RMS multi realization workflow loop
    # because the start random seed is created once per process, and the process is the same for all realizations in the loop.
    # Hence always read the start seed in single processing mode.
    # The seed can e.g be defined by using the RMS project realization seed number and should be set into the seed file
    # before calling the current script.

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

    # Set start seed
    startSeed = get_project_realization_seed(project)
    nrlib.seed(startSeed)

    # Loop over all zones and simulate gauss fields
    allZoneModels = apsModel.sorted_zone_models
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
            print('-- Zone: {}'.format(zoneNumber))
        if debug_level >= Debug.VERBOSE:
            print('--   Grid layers: {}     Start layer: {}     End layer: {}'
                  ''.format(nLayers, start + 1, end + 1))

        gaussResultListForZone = []
        for i in range(len(gaussFieldNames)):
            gaussFieldName = gaussFieldNames[i]
            azimuth = zoneModel.getAzimuthAngle(gaussFieldName)
            dip     = zoneModel.getDipAngle(gaussFieldName)
            power = zoneModel.getPower(gaussFieldName)
            variogramType = zoneModel.getVariogramType(gaussFieldName)
            vName = variogramType.name
            mainRange = zoneModel.getMainRange(gaussFieldName)
            perpRange = zoneModel.getPerpRange(gaussFieldName)
            vertRange = zoneModel.getVertRange(gaussFieldName)

            azimuthValueSimBox = azimuth - azimuthAngleGrid

            if debug_level >= Debug.VERBOSE:
                print('---  Simulate: {}  for zone: {}  for region: {}'
                      ''.format(gaussFieldName, zoneNumber, regionNumber))
            if debug_level >= Debug.VERY_VERBOSE:
                print('     Zone,region             : ({},{})'.format(zoneNumber, regionNumber))
                print('     Gauss field name        : {}'.format(gaussFieldName))
                print('     Variogram type          : {}'.format(vName))
                print('     Main range              : {}'.format(mainRange))
                print('     Perpendicular range     : {}'.format(perpRange))
                print('     Vertical range          : {}'.format(vertRange))
                print('     Azimuth angle in sim box: {}'.format(azimuthValueSimBox))
                print('     Dip angle               : {}'.format(dip))
                print('     NX                      : {}'.format(nx))
                print('     NY                      : {}'.format(ny))
                print('     NZ for this zone        : {}'.format(nz))
                print('     DX                      : {}'.format(dx))
                print('     DY                      : {}'.format(dy))
                print('     DZ for this zone        : {}'.format(dz))

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
                print('     nx: {}   nx with padding: {}'.format(nx, nx_padding))
                print('     ny: {}   ny with padding: {}'.format(ny, ny_padding))
                print('     nz: {}   nz with padding: {}'.format(nz, nz_padding))

            # Simulate gauss field. Return numpy 1D vector in F order
            gaussVector = nrlib.simulate(simVariogram, nx, dx, ny, dy, nz, dz)
            gaussResult = np.reshape(gaussVector, (nx, ny, nz), order='F')
            gaussResultListForZone.append(gaussResult)
            if debug_level >= Debug.VERBOSE:
                print('--- Finished running simulation of {} for zone,region: ({},{})'
                      ''.format(gaussFieldName, zoneNumber, regionNumber))
                print('')

        # End loop over gauss fields for one zone
        setContinuous3DParameterValuesInZoneRegion(
            gridModel, gaussFieldNames, gaussResultListForZone, zoneNumber-1,
            regionNumber=regionNumber, regionParamName=regionParamName,
            realNumber=realNumber, isShared=isShared, debug_level=debug_level
        )
    # End loop over all active zones in the model

    seedFileLog = 'seedLogFile.dat'
    startSeed = nrlib.seed()
    with open(seedFileLog, 'a') as file:
        file.write(
            'RealNumber: {}  StartSeed for this realization: {}\n'.format(
                str(realNumber + 1), str(startSeed))
        )
    print('')


def run(roxar=None, project=None, **kwargs):
    model_file = get_specification_file(**kwargs)
    real_number = project.current_realisation
    is_shared = False
    run_simulations(project, modelFile=model_file, realNumber=real_number, isShared=is_shared)
    print('Finished simulation of gaussian fields for APS')


if __name__ == '__main__':
    import roxar
    run(roxar, project)
