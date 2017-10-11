#!/bin/env python
# Python3  test that the model files can be created correctly.

import filecmp

from src.APSFaciesProb import APSFaciesProb
from src.APSGaussFieldJobs import APSGaussFieldJobs
from src.APSGaussModel import APSGaussModel
from src.APSMainFaciesTable import APSMainFaciesTable
from src.APSModel import APSModel
from src.APSZoneModel import APSZoneModel
from src.Trend3D_linear_model_xml import Trend3D_linear_model
from src.Trunc2D_Angle_xml import Trunc2D_Angle
from src.Trunc2D_Cubic_xml import Trunc2D_Cubic
from src.utils.constants import Debug
from src.unit_test.constants import (
    FACIES_REAL_PARAM_NAME_RESULT, GAUSS_FIELD_SIM_SCRIPT, GRID_MODEL_NAME, VERY_VERBOSE_DEBUG,
    RMS_PROJECT, RMS_WORKFLOW, ZONE_PARAM_NAME,
)


def defineCommonModelParam(
        apsmodel, rmsProject, rmsWorkflow, gaussFieldSimScript, gridModelName,
        zoneParamName, faciesRealParamNameResult, fTable, debug_level=Debug.OFF
):
    # The input data are global variables

    apsmodel.setRmsProjectName(rmsProject)
    apsmodel.setRmsWorkflowName(rmsWorkflow)
    apsmodel.setGaussFieldScriptName(gaussFieldSimScript)
    apsmodel.setRmsGridModelName(gridModelName)
    apsmodel.setRmsZoneParamName(zoneParamName)
    apsmodel.setRmsResultFaciesParamName(faciesRealParamNameResult)
    apsmodel.setPrintInfo(debug_level)

    # Define gauss field jobs
    gfJobObject = APSGaussFieldJobs()
    gfJobNames = ['GRFJob1', 'GRFJob2', 'GRFJob3']
    gfNamesPerJob = [['GRF1', 'GRF2'], ['GRF3', 'GRF4', 'GRF5'], ['GRF6', 'GRF7', 'GRF8', 'GRF9']]
    gfJobObject.initialize(gfJobNames, gfNamesPerJob, debug_level)
    apsmodel.setGaussFieldJobs(gfJobObject)

    # Define main facies table
    mainFaciesTable = APSMainFaciesTable()
    mainFaciesTable.initialize(fTable)
    apsmodel.setMainFaciesTable(mainFaciesTable)


def addZoneParam(
        apsmodel, truncType, faciesInZone, faciesProbList, useConstProb, zoneNumber, gfNames, gfTypes,
        range1, range2, range3, azimuthAngle, azimuthVarioAngles, dipVarioAngles, stackingAngle,
        power, direction, useTrend, relStdDev, previewSeed, simBoxThickness, truncStructureList,
        backGroundFaciesGroups, overlayFacies, overlayTruncCenter, useConstTruncParam,
        horizonNameForVarioTrendMap, debug_level=Debug.OFF
):
    mainFaciesTable = apsmodel.getMainFaciesTable()
    gaussFieldJobs = apsmodel.getGaussFieldJobs()

    # Define facies probabilities
    faciesProbObj = APSFaciesProb()
    faciesProbObj.initialize(faciesInZone, faciesProbList, mainFaciesTable, useConstProb, zoneNumber, debug_level)

    # Define gauss field models
    gaussModelList = []
    trendModelList = []
    seedPreviewList = []
    for i in range(len(gfNames)):
        gaussModelList.append([gfNames[i], gfTypes[i], range1[i], range2[i], range3[i],
                               azimuthVarioAngles[i], dipVarioAngles[i], power[i]])

        # Set Gauss field trend parameters
        trendModelObject = Trend3D_linear_model(None, debug_level, None)
        trendModelObject.initialize(azimuthAngle[i], stackingAngle[i], direction[i], debug_level)
        trendModelList.append([gfNames[i], useTrend[i], trendModelObject, relStdDev[i]])

        seedPreviewList.append([gfNames[i], previewSeed[i]])

    gaussModelObj = APSGaussModel()
    gaussModelObj.initialize(
        zoneNumber, mainFaciesTable, gaussFieldJobs,
        gaussModelList, trendModelList,
        simBoxThickness, seedPreviewList, debug_level
    )

    # Define truncation rule model

    if truncType == 'Cubic':
        truncRuleObj = Trunc2D_Cubic()
        truncRuleObj.initialize(
            mainFaciesTable, faciesInZone, truncStructureList,
            backGroundFaciesGroups, overlayFacies, overlayTruncCenter, debug_level
        )
    elif truncType == 'Angle':
        truncRuleObj = Trunc2D_Angle()
        truncRuleObj.initialize(
            mainFaciesTable, faciesInZone, truncStructureList, backGroundFaciesGroups,
            overlayFacies, overlayTruncCenter, useConstTruncParam, debug_level
        )
    else:
        raise ValueError("Invalid truncation type")

    # Initialize data for this zone
    apsZoneModel = APSZoneModel()
    apsZoneModel.initialize(
        zoneNumber, useConstProb, simBoxThickness, horizonNameForVarioTrendMap,
        faciesProbObj, gaussModelObj, truncRuleObj, debug_level
    )

    # Add zone to APSModel
    apsmodel.addNewZone(apsZoneModel)


def read_write_model(apsmodel, debug_level=Debug.OFF):
    outfile1 = 'testOut1.xml'
    apsmodel.writeModel(outfile1, debug_level=debug_level)

    # Read the xml file into an new APSModel object
    apsmodel2 = APSModel(outfile1, debug_level=debug_level)
    outfile2 = 'testOut2.xml'
    apsmodel2.writeModel(outfile2, debug_level=debug_level)
    print('Compare file: ' + outfile1 + ' and ' + outfile2)
    check = filecmp.cmp(outfile1, outfile2)

    if check:
        print('Files are equal. OK')
    else:
        print('Files are different. NOT OK')
    assert check is True


def read_write_model_update(debug_level=Debug.OFF):
    outfile1 = 'testOut1.xml'
    # Read the xml file into an new APSModel object
    apsmodel2 = APSModel(outfile1)
    outfile2 = 'testOut2.xml'
    apsmodel2.writeModel(outfile2, debug_level)
    print('Compare file: ' + outfile1 + ' and ' + outfile2)
    check = filecmp.cmp(outfile1, outfile2)

    if check:
        print('Files are equal. OK')
    else:
        print('Files are different. NOT OK')
    assert check is True


def test_create_XMLModelFiles():
    # -------- Main -------
    print('Start test_createXMLModelFiles')

    test_case_1()
    test_case_2()

    test_updating_model()

    test_variogram_generation()
    print('Finished')


def test_variogram_generation():
    apsGaussModel = APSGaussModel()
    zoneNumber = 1
    # Define main facies table
    mainFaciesTable = APSMainFaciesTable()
    fTable = fTable = {2: 'F2', 1: 'F1', 3: 'F3'}
    mainFaciesTable.initialize(fTable)
    gfJobs = APSGaussFieldJobs()
    gfJobNames = ['Job1', 'Job2']
    gfNamesPerJob = [['GRF1', 'GRF2'], ['GRF3', 'GRF4', 'GRF5']]
    gfJobs.initialize(gfJobNames, gfNamesPerJob)
    mainRange = 1000
    perpRange = 100
    vertRange = 1.0
    azimuth = 45.0
    dip = 1.0
    gfName = 'GRF1'
    gaussModelList = [['GRF1', 'SPHERICAL', mainRange, perpRange, vertRange, azimuth, dip, 1.0]]
    useTrend = 0
    relStdDev = 0.05
    trendModelObject = Trend3D_linear_model(None, VERY_VERBOSE_DEBUG, None)
    azimuthTrendAngle = 0.0
    stackingTrendAngle = 0.0
    direct = -1
    trendModelObject.initialize(azimuthTrendAngle, stackingTrendAngle, direct)
    trendModelList = [['GRF1', useTrend, trendModelObject, relStdDev]]
    simBoxThickness = 100.0
    prevSeedList = [['GRF1', 92828]]
    debug_level = Debug.VERY_VERBOSE
    apsGaussModel.initialize(
        zoneNumber, mainFaciesTable, gfJobs, gaussModelList,
        trendModelList, simBoxThickness, prevSeedList, debug_level
    )
    gridAzimuthAngle = 0.0
    projection = 'xy'
    apsGaussModel.calc2DVarioFrom3DVario(gfName, gridAzimuthAngle, projection)
    projection = 'xz'
    apsGaussModel.calc2DVarioFrom3DVario(gfName, gridAzimuthAngle, projection)
    projection = 'yz'
    apsGaussModel.calc2DVarioFrom3DVario(gfName, gridAzimuthAngle, projection)


def test_updating_model():
    # Test updating of model
    modelFile = 'testData_models/APS.xml'
    apsmodel = APSModel(modelFile, debug_level=Debug.VERY_VERBOSE_DEBUG)
    # Do some updates of the model
    zoneNumber = 1
    zone1 = apsmodel.getZoneModel(zoneNumber)
    gaussFieldNames = zone1.getUsedGaussFieldNames()
    nGaussFields = len(gaussFieldNames)
    varioTypeList = ['SPHERICAL', 'EXPONENTIAL', 'GAUSSIAN', 'GENERAL_EXPONENTIAL', 'SPHERICAL']
    mainRangeList = [1234.0, 5432.0, 1200.0, 1300.0, 2150.0]
    perpRangeList = [123.0, 543.0, 120.0, 130.0, 215.0]
    vertRangeList = [1.0, 5.0, 1.2, 1.3, 2.15]
    azimuthAngleList = [0.0, 90.0, 125.0, 40.0, 50.0]
    dipAngleList = [0.0, 0.01, 0.005, 0.009, 0.0008]
    powerList = [1.0, 1.2, 1.3, 1.4, 1.5]
    for i in range(nGaussFields):
        gfName = gaussFieldNames[i]
        print('Update zone ' + str(zoneNumber) + ' and gauss field ' + gfName)

        varioType = zone1.getVarioType(gfName)
        print('Original varioType: ' + varioType)
        varioType = varioTypeList[i]
        zone1.setVarioType(gfName, varioType)
        varioType1 = zone1.getVarioType(gfName)
        print('New varioType     : ' + varioType1)

        mainRange = zone1.getMainRange(gfName)
        print('Original MainRange: ' + str(mainRange))
        mainRange = mainRangeList[i]
        zone1.setMainRange(gfName, mainRange)
        mainRange1 = zone1.getMainRange(gfName)
        print('New MainRange: ' + str(mainRange1))

        perpRange = zone1.getPerpRange(gfName)
        print('Original PerpRange: ' + str(perpRange))
        perpRange = perpRangeList[i]
        zone1.setPerpRange(gfName, perpRange)
        perpRange1 = zone1.getPerpRange(gfName)
        print('New PerpRange: ' + str(perpRange1))

        vertRange = zone1.getVertRange(gfName)
        print('Original VertRange: ' + str(vertRange))
        vertRange = vertRangeList[i]
        zone1.setVertRange(gfName, vertRange)
        vertRange1 = zone1.getVertRange(gfName)
        print('New VertRange: ' + str(vertRange1))

        azimuth = zone1.getAnisotropyAzimuthAngle(gfName)
        print('Original azimuth angle: ' + str(azimuth))
        azimuth = azimuthAngleList[i]
        zone1.setAnisotropyAzimuthAngle(gfName, azimuth)
        azimuth1 = zone1.getAnisotropyAzimuthAngle(gfName)
        print('New azimuth angle: ' + str(azimuth1))

        dip = zone1.getAnisotropyDipAngle(gfName)
        print('Original dip angle: ' + str(dip))
        dip = dipAngleList[i]
        zone1.setAnisotropyDipAngle(gfName, dip)
        dip1 = zone1.getAnisotropyDipAngle(gfName)
        print('New dip angle: ' + str(dip1))

        if varioType == 'GENERAL_EXPONENTIAL':
            power = zone1.getPower(gfName)
            print('Original exponent: ' + str(power))
            power = powerList[i]
            zone1.setPower(gfName, power)
            power1 = zone1.getPower(gfName)
            print('New exponent: ' + str(power1))
    outfile2 = 'testOut2_updated.xml'
    apsmodel.writeModel(outfile2, VERY_VERBOSE_DEBUG)
    reference_file = 'testData_models/APS_updated.xml'
    print('Compare file: ' + outfile2 + ' and ' + reference_file)
    check = filecmp.cmp(outfile2, reference_file)
    if check:
        print('Files are equal. OK')
    else:
        print('Files are different. NOT OK')
    assert check is True


def test_case_2():
    print('')
    print('**** Case number: 2 ****')
    # Global facies table, zone facies and facies probabilities
    fTable = {2: 'F2', 1: 'F1', 3: 'F3', 4: 'F4', 5: 'F5', 6: 'F6', 7: 'F7'}
    apsmodel = APSModel()
    defineCommonModelParam(
        apsmodel, RMS_PROJECT, RMS_WORKFLOW, GAUSS_FIELD_SIM_SCRIPT, GRID_MODEL_NAME,
        ZONE_PARAM_NAME, FACIES_REAL_PARAM_NAME_RESULT, fTable, VERY_VERBOSE_DEBUG
    )
    #  --- Zone 1 ---
    zoneNumber = 1
    horizonNameForVarioTrendMap = 'zone_1'
    simBoxThickness = 4.0
    # Facies prob for zone
    faciesInZone = ['F1', 'F2', 'F5', 'F7']
    useConstProb = 1
    faciesProbList = [0.4, 0.5, 0.03, 0.07]
    # Gauss field parameters. One entry in list for each gauss field
    gfNames = ['GRF6', 'GRF7', 'GRF8', 'GRF9']
    gfTypes = ['GENERAL_EXPONENTIAL', 'SPHERICAL', 'EXPONENTIAL', 'GENERAL_EXPONENTIAL']
    range1 = [3000.0, 1500.0, 2500.0, 750.0]
    range2 = [1400.0, 750.0, 800.0, 5200.0]
    range3 = [2.0, 1.0, 4.0, 120.0]
    azimuthVarioAngles = [35.0, 125.0, 95.0, 323.0]
    dipVarioAngles = [0.01, 0.0, 0.0, 0.02]
    power = [1.8, 1.0, 1.0, 1.95]
    # Trend parameters. One entry in list for each gauss field
    useTrend = [1, 0, 0, 0]
    relStdDev = [0.05, 0, 0, 0]
    azimuthAngle = [125.0, 0.0, 0.0, 0.0]
    stackingAngle = [0.1, 0.0, 0.0, 0.0]
    direction = [1, 1, 1, 1]
    previewSeed = [9282727, 96785, 88760019, 8156827]
    # Truncation rule
    truncType = 'Cubic'
    truncStructureList = ['H', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0]]
    overlayFacies = ['F5', 'F7']
    backGroundFaciesGroups = [['F1'], ['F2']]
    overlayTruncCenter = [0.0, 0.8]
    useConstTruncParam = 1
    addZoneParam(
        apsmodel, truncType, faciesInZone, faciesProbList, useConstProb, zoneNumber, gfNames,
        gfTypes, range1, range2, range3, azimuthAngle, azimuthVarioAngles, dipVarioAngles,
        stackingAngle, power, direction, useTrend, relStdDev, previewSeed, simBoxThickness,
        truncStructureList, backGroundFaciesGroups, overlayFacies, overlayTruncCenter,
        useConstTruncParam, horizonNameForVarioTrendMap, VERY_VERBOSE_DEBUG
    )
    #  --- Zone 2 ---
    zoneNumber = 2
    horizonNameForVarioTrendMap = 'zone_2'
    simBoxThickness = 12.0
    # Facies prob for zone
    faciesInZone = ['F3', 'F1', 'F2', 'F5', 'F6', 'F7']
    useConstProb = 0
    faciesProbList = ['F3_prob', 'F1_prob', 'F2_prob', 'F5_prob', 'F6_prob', 'F7_prob']
    gfNames = ['GRF6', 'GRF7', 'GRF8', 'GRF9']
    gfTypes = ['GENERAL_EXPONENTIAL', 'SPHERICAL', 'EXPONENTIAL', 'GENERAL_EXPONENTIAL']
    range1 = [2000.0, 2500.0, 1500.0, 1750.0]
    range2 = [1400.0, 750.0, 800.0, 5200.0]
    range3 = [2.0, 1.0, 4.0, 120.0]
    azimuthVarioAngles = [135.0, 25.0, 75.0, 23.0]
    dipVarioAngles = [0.0, 0.0, 0.01, 0.02]
    power = [1.8, 1.0, 1.0, 1.95]
    # Trend parameters. One entry in list for each gauss field
    useTrend = [1, 0, 1, 0]
    relStdDev = [0.05, 0, 0.03, 0]
    azimuthAngle = [125.0, 0.0, 90.0, 0.0]
    stackingAngle = [0.1, 0.0, 0.01, 0.0]
    direction = [1, 1, -1, 1]
    previewSeed = [9282727, 96785, 88760019, 8156827]
    # Truncation rule
    truncType = 'Angle'
    truncStructureList = [['F1', 0.0, 1.0], ['F3', 45.0, 1.0], ['F2', -35.0, 1.0], ['F5', 145.0, 1.0]]
    overlayFacies = ['F6', 'F7']
    backGroundFaciesGroups = [['F1', 'F3'], ['F2', 'F5']]
    overlayTruncCenter = [0.5, 0.7]
    useConstTruncParam = 1
    addZoneParam(
        apsmodel, truncType, faciesInZone, faciesProbList, useConstProb, zoneNumber, gfNames,
        gfTypes, range1, range2, range3, azimuthAngle, azimuthVarioAngles, dipVarioAngles,
        stackingAngle, power, direction, useTrend, relStdDev, previewSeed, simBoxThickness,
        truncStructureList, backGroundFaciesGroups, overlayFacies, overlayTruncCenter,
        useConstTruncParam, horizonNameForVarioTrendMap, VERY_VERBOSE_DEBUG
    )
    selectedZones = [1, 2]
    apsmodel.setSelectedZoneNumberList(selectedZones)
    apsmodel.setPreviewZoneNumber(1)
    read_write_model(apsmodel, VERY_VERBOSE_DEBUG)


def test_case_1():
    print('')
    print('**** Case number: 1 ****')
    # Global facies table, zone facies and facies probabilities
    fTable = {2: 'F2', 1: 'F1', 3: 'F3'}
    apsmodel = APSModel()
    defineCommonModelParam(
        apsmodel, RMS_PROJECT, RMS_WORKFLOW, GAUSS_FIELD_SIM_SCRIPT, GRID_MODEL_NAME,
        ZONE_PARAM_NAME, FACIES_REAL_PARAM_NAME_RESULT, fTable, VERY_VERBOSE_DEBUG
    )
    #  --- Zone 1 ---
    zoneNumber = 1
    horizonNameForVarioTrendMap = 'zone_1'
    simBoxThickness = 4.0
    # Facies prob for zone
    faciesInZone = ['F1', 'F2']
    useConstProb = 1
    faciesProbList = [0.4, 0.6]
    # Gauss field parameters. One entry in list for each gauss field
    gfNames = ['GRF1', 'GRF2']
    gfTypes = ['GENERAL_EXPONENTIAL', 'SPHERICAL']
    range1 = [2000.0, 1500.0]
    range2 = [1400.0, 750.0]
    range3 = [2.0, 1.0]
    azimuthVarioAngles = [35.0, 125.0]
    dipVarioAngles = [0.0, 0.1]
    power = [1.8, 1.0]
    # Trend parameters. One entry in list for each gauss field
    useTrend = [1, 0]
    relStdDev = [0.05, 0]
    azimuthAngle = [125.0, 0.0]
    stackingAngle = [0.1, 0.0]
    direction = [1, 1]
    previewSeed = [9282727, 96785]
    # Truncation rule
    truncType = 'Cubic'
    truncStructureList = ['V', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0]]
    overlayFacies = []
    backGroundFaciesGroups = []
    overlayTruncCenter = []
    useConstTruncParam = 1
    addZoneParam(
        apsmodel, truncType, faciesInZone, faciesProbList, useConstProb, zoneNumber, gfNames,
        gfTypes, range1, range2, range3, azimuthAngle, azimuthVarioAngles, dipVarioAngles,
        stackingAngle, power, direction, useTrend, relStdDev, previewSeed, simBoxThickness,
        truncStructureList, backGroundFaciesGroups, overlayFacies, overlayTruncCenter,
        useConstTruncParam, horizonNameForVarioTrendMap, VERY_VERBOSE_DEBUG
    )
    #  --- Zone 2 ---
    zoneNumber = 2
    horizonNameForVarioTrendMap = 'zone_2'
    simBoxThickness = 12.0
    # Facies prob for zone
    faciesInZone = ['F3', 'F1', 'F2']
    useConstProb = 0
    faciesProbList = ['F3_prob', 'F1_prob', 'F2_prob']
    # Gauss field parameters. One entry in list for each gauss field
    gfNames = ['GRF3', 'GRF4', 'GRF5']
    gfTypes = ['GENERAL_EXPONENTIAL', 'SPHERICAL', 'EXPONENTIAL']
    range1 = [2000.0, 1500.0, 6000.0]
    range2 = [1400.0, 750.0, 250.0]
    range3 = [2.0, 1.0, 4.5]
    azimuthVarioAngles = [35.0, 125.0, 315.0]
    dipVarioAngles = [0.01, 0.0, 0.0]
    power = [1.8, 1.0, 1.0]
    # Trend parameters. One entry in list for each gauss field
    useTrend = [0, 1, 0]
    relStdDev = [0, 0.05, 0]
    azimuthAngle = [0.0, 125.0, 0.0]
    stackingAngle = [0.0, 0.1, 0.0]
    direction = [1, -1, 1]
    previewSeed = [8727, 977727, 776785]
    # Truncation rule
    truncType = 'Angle'
    truncStructureList = [['F1', 0.0, 1.0], ['F3', 45.0, 1.0]]
    overlayFacies = ['F2']
    backGroundFaciesGroups = [['F1', 'F3']]
    overlayTruncCenter = [0.5]
    useConstTruncParam = 1
    addZoneParam(
        apsmodel, truncType, faciesInZone, faciesProbList, useConstProb, zoneNumber, gfNames,
        gfTypes, range1, range2, range3, azimuthAngle, azimuthVarioAngles, dipVarioAngles,
        stackingAngle, power, direction, useTrend, relStdDev, previewSeed, simBoxThickness,
        truncStructureList, backGroundFaciesGroups, overlayFacies, overlayTruncCenter,
        useConstTruncParam, horizonNameForVarioTrendMap, VERY_VERBOSE_DEBUG
    )
    selectedZones = [1, 2]
    apsmodel.setSelectedZoneNumberList(selectedZones)
    apsmodel.setPreviewZoneNumber(1)
    read_write_model(apsmodel, VERY_VERBOSE_DEBUG)


if __name__ == '__main__':
    test_create_XMLModelFiles()
