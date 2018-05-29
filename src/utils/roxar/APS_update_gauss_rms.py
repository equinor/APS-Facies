#!/bin/env python3
# -*- coding: utf-8 -*-
# This script call ROXAR API functions
import numpy as np

from src.algorithms.APSModel import APSModel
from src.utils.methods import get_run_parameters
from src.utils.roxar.APSDataFromRMS import APSDataFromRMS
from src.utils.roxar.generalFunctionsUsingRoxAPI import setContinuous3DParameterValuesInZone
from src.utils.constants.simple import Debug


def run_main(
        project,
        model_file='APS.xml',
        rms_data_file_name='rms_project_data_for_APS_gui.xml',
        inputDir='./tmp_gauss_sim',
        isShared=False
):
    """
    Description: Read simulated gaussian fields from disk and put into the RMS project

    """
    realization_number = project.current_realisation

    # Read APS model
    print('- Read file: ' + model_file)
    apsModel = APSModel(model_file)
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
            'You may have to fix the model file or extract data from RMS for correct grid model again'.format(
                gridModelName, gridModelNameFromRMSData)
        )
    [nx, ny, _, _, _, _, _, _, _] = rmsData.getGridSize()

    # Loop over all zones and simulate gauss fields
    gridModel = project.grid_models[gridModelName]
    allZoneModels = apsModel.getAllZoneModelsSorted()
    for key, zoneModel in allZoneModels.items():
        zoneNumber = key[0]
        regionNumber = key[1]
        if not apsModel.isSelected(zoneNumber, regionNumber):
            continue
        gaussFieldNames = zoneModel.getGaussFieldsInTruncationRule()
        nLayers = rmsData.getNumberOfLayersInZone(zoneNumber)
        if debug_level >= Debug.ON:
            print(gaussFieldNames)
        gaussResultListForZone = []
        for i in range(len(gaussFieldNames)):
            gaussFieldName = gaussFieldNames[i]
            fileName = inputDir + '/' + gaussFieldName + '_' + str(zoneNumber) + '_' + str(regionNumber) + '.npy'
            gaussVector = np.load(fileName)
            gaussResult = np.reshape(gaussVector, (nx, ny, nLayers), order='F')
            if debug_level >= Debug.ON:
                print('-- Update RMS parameter: {} for zone: {}'.format(gaussFieldName, str(zoneNumber)))
            gaussResultListForZone.append(gaussResult)
        setContinuous3DParameterValuesInZone(
            gridModel, gaussFieldNames, gaussResultListForZone, zoneNumber - 1,
            realNumber=realization_number, isShared=isShared, debug_level=debug_level
        )
        # End loop over gauss fields for one zone
    # End loop over all active zones in the model
    if debug_level >= Debug.ON:
        print('')
        print('- Finished reading simulated gauss fields from disk and update RMS project')
        print('')


def run(roxar=None, project=None, **kwargs):
    model_file, rms_data_file_name, _, input_dir, _ = get_run_parameters(**kwargs)
    run_main(project, model_file=model_file, rms_data_file_name=rms_data_file_name, inputDir=input_dir)


if __name__ == '__main__':
    import roxar
    run(roxar, project)
