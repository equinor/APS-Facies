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
from src.Trunc3D_bayfill_xml import Trunc3D_bayfill
from src.unit_test.constants import (
    FACIES_REAL_PARAM_NAME_RESULT, GAUSS_FIELD_SIM_SCRIPT, GRID_MODEL_NAME, RMS_PROJECT, RMS_WORKFLOW, ZONE_PARAM_NAME,
    NO_VERBOSE_DEBUG,VERY_VERBOSE_DEBUG
)
from src.utils.constants.simple import Debug, VariogramType


def defineCommonModelParam(
        apsmodel, rmsProject, rmsWorkflow, gaussFieldSimScript, gridModelName,
        zoneParamName, faciesRealParamNameResult, fTable, debug_level=VERY_VERBOSE_DEBUG
):
    # The input data are global variables

    apsmodel.setRmsProjectName(rmsProject)
    apsmodel.setRmsWorkflowName(rmsWorkflow)
    apsmodel.setGaussFieldScriptName(gaussFieldSimScript)
    apsmodel.setRmsGridModelName(gridModelName)
    apsmodel.setRmsZoneParamName(zoneParamName)
    apsmodel.setRmsResultFaciesParamName(faciesRealParamNameResult)
    apsmodel.set_debug_level(debug_level)
    print('Debug level: {}'.format(str(apsmodel.debug_level())))
    # Define gauss field jobs
    gfJobObject = APSGaussFieldJobs()
    gfJobNames = ['GRFJob1', 'GRFJob2', 'GRFJob3']
    gfNamesPerJob = [['GRF1', 'GRF2'], ['GRF3', 'GRF4', 'GRF5'], ['GRF6', 'GRF7', 'GRF8', 'GRF9']]
    gfJobObject.initialize(gfJobNames=gfJobNames, gfNamesPerJob=gfNamesPerJob, debug_level=debug_level)
    apsmodel.setGaussFieldJobs(gfJobObject)

    # Define main facies table
    mainFaciesTable = APSMainFaciesTable(fTable=fTable)
    apsmodel.setMainFaciesTable(mainFaciesTable)


def addZoneParam(
        apsmodel,
        zoneNumber=0,
        regionNumber=0,
        horizonNameForVariogramTrendMap=None,
        simBoxThickness=0.0,
        # Facies prob for zone
        faciesInZone=None,
        useConstProb=0,
        faciesProbList=None,
        # Gauss field parameters. One entry in list for each gauss field
        gaussFieldsInZone=None,
        gfTypes=None,
        range1=None,
        range2=None,
        range3=None,
        azimuthVariogramAngles=None,
        dipVariogramAngles=None,
        power=None,
        # Trend parameters. One entry in list for each gauss field
        useTrend=None,
        relStdDev=None,
        azimuthAngle=None,
        stackingAngle=None,
        direction=None,
        previewSeed=None,
        # Truncation rule
        truncType=None,
        alphaFieldNameForBackGroundFacies=None,
        truncStructureList=None,
        overlayGroups=None,
        useConstTruncParam=None,
        faciesInTruncRule=None,
        sf_value=None,
        sf_name=None,
        ysf=None,
        sbhd=None,
        debug_level=Debug.OFF
):
    mainFaciesTable = apsmodel.getMainFaciesTable()
    gaussFieldJobs = apsmodel.getGaussFieldJobs()

    # Define facies probabilities
    faciesProbObj = APSFaciesProb()
    faciesProbObj.initialize(
        faciesList=faciesInZone, faciesProbList=faciesProbList, mainFaciesTable=mainFaciesTable,
        useConstProb=useConstProb, zoneNumber=zoneNumber, debug_level=debug_level
    )

    # Define gauss field models
    gaussModelList = []
    trendModelList = []
    seedPreviewList = []
    for i in range(len(gaussFieldsInZone)):
        gaussModelList.append([
            gaussFieldsInZone[i], gfTypes[i], range1[i], range2[i], range3[i],
            azimuthVariogramAngles[i], dipVariogramAngles[i], power[i]
        ])

        # Set Gauss field trend parameters
        trendModelObject = Trend3D_linear_model(trendRuleXML=None, debug_level=debug_level, modelFileName=None)
        trendModelObject.initialize(azimuthAngle[i], stackingAngle[i], direction[i], debug_level)
        trendModelList.append([gaussFieldsInZone[i], useTrend[i], trendModelObject, relStdDev[i]])

        seedPreviewList.append([gaussFieldsInZone[i], previewSeed[i]])

    gaussModelObj = APSGaussModel()
    gaussModelObj.initialize(
        inputZoneNumber=zoneNumber, mainFaciesTable=mainFaciesTable, gaussFieldJobs=gaussFieldJobs,
        gaussModelList=gaussModelList, trendModelList=trendModelList, simBoxThickness=simBoxThickness,
        previewSeedList=seedPreviewList, debug_level=debug_level
    )

    # Define truncation rule model

    if truncType == 'Cubic':
        truncRuleObj = Trunc2D_Cubic()
        truncRuleObj.initialize(
            mainFaciesTable=mainFaciesTable,
            faciesInZone=faciesInZone,
            gaussFieldsInZone=gaussFieldsInZone,
            alphaFieldNameForBackGroundFacies=alphaFieldNameForBackGroundFacies,
            truncStructureList=truncStructureList,
            overlayGroups=overlayGroups,
            debug_level=debug_level

        )
    elif truncType == 'Angle':
        truncRuleObj = Trunc2D_Angle()
        truncRuleObj.initialize(
            mainFaciesTable=mainFaciesTable,
            faciesInZone=faciesInZone,
            gaussFieldsInZone=gaussFieldsInZone,
            alphaFieldNameForBackGroundFacies=alphaFieldNameForBackGroundFacies,
            truncStructure=truncStructureList,
            overlayGroups=overlayGroups,
            useConstTruncParam=useConstTruncParam,
            debug_level=debug_level
        )
    elif truncType == 'Bayfill':
        truncRuleObj = Trunc3D_bayfill()
        truncRuleObj.initialize(
            mainFaciesTable=mainFaciesTable,
            faciesInZone=faciesInZone,
            faciesInTruncRule=faciesInTruncRule,
            gaussFieldsInZone=gaussFieldsInZone,
            alphaFieldNameForBackGroundFacies=alphaFieldNameForBackGroundFacies,
            sf_value=sf_value,
            sf_name=sf_name,
            ysf=ysf,
            sbhd=sbhd,
            useConstTruncParam=useConstTruncParam,
            debug_level=debug_level
        )
    else:
        raise ValueError("Invalid truncation type")

    # Initialize data for this zone
    apsZoneModel = APSZoneModel(
        zoneNumber=zoneNumber, regionNumber=regionNumber, useConstProb=useConstProb, simBoxThickness=simBoxThickness,
        horizonNameForVariogramTrendMap=horizonNameForVariogramTrendMap, faciesProbObject=faciesProbObj,
        gaussModelObject=gaussModelObj, truncRuleObject=truncRuleObj, debug_level=debug_level
    )

    # Add zone to APSModel
    apsmodel.addNewZone(apsZoneModel)

    # Delete zone to APSModel
    apsmodel.deleteZone(zoneNumber, regionNumber)

    # Add zone to APSModel
    apsmodel.addNewZone(apsZoneModel)

    # Get zone numbers and region numbers
    print('Zone numbers:')
    print(apsmodel.getZoneNumberList())

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
    print('')


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
    print('')


def test_create_XMLModelFiles():
    # -------- Main -------
    print('Start test_createXMLModelFiles')

    test_case_1()
    test_case_2()
    test_case_3()

    test_updating_model()

    test_variogram_generation()
    print('Finished')


def test_variogram_generation():
    print('****** Set variogram parameters ******')
    apsGaussModel = APSGaussModel()
    zoneNumber = 1
    # Define main facies table
    fTable = {2: 'F2', 1: 'F1', 3: 'F3'}
    mainFaciesTable = APSMainFaciesTable(fTable=fTable)
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
    trendModelObject = Trend3D_linear_model(None, Debug.OFF, None)
    azimuthTrendAngle = 0.0
    stackingTrendAngle = 0.0
    direct = -1
    trendModelObject.initialize(azimuthTrendAngle, stackingTrendAngle, direct)
    trendModelList = [['GRF1', useTrend, trendModelObject, relStdDev]]
    simBoxThickness = 100.0
    prevSeedList = [['GRF1', 92828]]
    debug_level = Debug.VERY_VERBOSE
    apsGaussModel.initialize(
        inputZoneNumber=zoneNumber, mainFaciesTable=mainFaciesTable, gaussFieldJobs=gfJobs,
        gaussModelList=gaussModelList, trendModelList=trendModelList, simBoxThickness=simBoxThickness,
        previewSeedList=prevSeedList, debug_level=debug_level
    )
    gridAzimuthAngle = 0.0
    projection = 'xy'
    apsGaussModel.calc2DVariogramFrom3DVariogram(gfName, gridAzimuthAngle, projection)
    projection = 'xz'
    apsGaussModel.calc2DVariogramFrom3DVariogram(gfName, gridAzimuthAngle, projection)
    projection = 'yz'
    apsGaussModel.calc2DVariogramFrom3DVariogram(gfName, gridAzimuthAngle, projection)


def test_updating_model():
    print('***** Case: Update parameters *****')
    # Test updating of model
    modelFile = 'testData_models/APS.xml'
    apsmodel = APSModel(modelFileName=modelFile, debug_level=Debug.OFF)
    # Do some updates of the model
    zoneNumber = 1
    zone = apsmodel.getZoneModel(zoneNumber)
    gaussFieldNames = zone.getUsedGaussFieldNames()
    nGaussFields = len(gaussFieldNames)
    variogramTypeList = [
        VariogramType.SPHERICAL, VariogramType.EXPONENTIAL, VariogramType.GAUSSIAN,
        VariogramType.GENERAL_EXPONENTIAL, VariogramType.SPHERICAL
    ]
    mainRangeList = [1234.0, 5432.0, 1200.0, 1300.0, 2150.0]
    perpRangeList = [123.0, 543.0, 120.0, 130.0, 215.0]
    vertRangeList = [1.0, 5.0, 1.2, 1.3, 2.15]
    azimuthAngleList = [0.0, 90.0, 125.0, 40.0, 50.0]
    dipAngleList = [0.0, 0.01, 0.005, 0.009, 0.0008]
    powerList = [1.0, 1.2, 1.3, 1.4, 1.5]
    for i in range(nGaussFields):
        gfName = gaussFieldNames[i]
        print('Update zone ' + str(zoneNumber) + ' and gauss field ' + gfName)

        variogramType = variogramTypeList[i]
        assertPropertyGetterSetter(gfName, variogramType, zone, 'VariogramType')

        mainRange = mainRangeList[i]
        assertPropertyGetterSetter(gfName, mainRange, zone, 'MainRange')

        perpRange = perpRangeList[i]
        assertPropertyGetterSetter(gfName, perpRange, zone, 'PerpRange')

        vertRange = vertRangeList[i]
        assertPropertyGetterSetter(gfName, vertRange, zone, 'VertRange')

        azimuth = azimuthAngleList[i]
        assertPropertyGetterSetter(gfName, azimuth, zone, 'AnisotropyAzimuthAngle')

        dip = dipAngleList[i]
        assertPropertyGetterSetter(gfName, dip, zone, 'AnisotropyDipAngle')

        if variogramType == VariogramType.GENERAL_EXPONENTIAL:
            power = powerList[i]
            assertPropertyGetterSetter(gfName, power, zone, 'Power')
    outfile2 = 'testOut2_updated.xml'
    apsmodel.writeModel(outfile2, Debug.OFF)
    reference_file = 'testData_models/APS_updated.xml'
    print('Compare file: ' + outfile2 + ' and ' + reference_file)
    check = filecmp.cmp(outfile2, reference_file)
    if check:
        print('Files are equal. OK')
    else:
        print('Files are different. NOT OK')
    assert check is True


def assertPropertyGetterSetter(gaussianFieldName: str, value: object, zone: APSZoneModel, baseName: str):
    getter = zone.__getattribute__('get' + baseName)
    setter = zone.__getattribute__('set' + baseName)

    # TODO: Add an assert!
    original = getter(gaussianFieldName)
    setter(gaussianFieldName, value)
    new = getter(gaussianFieldName)
    print(baseName + ' ' + str(original) + ' -> ' + str(new))


def test_case_1():
    print('')
    print('**** Case number: 1 ****')

    #  --- Zone 1 ---
    test_case_1_zone_1()

    #  --- Zone 2 ---
    test_case_1_zone_2()


def test_case_2():
    print('')
    print('**** Case number: 2 ****')

    #  --- Zone 1 ---
    test_case_2_zone_1()

    #  --- Zone 2 ---
    test_case_2_zone_2()


def test_case_3():
    print('')
    print('**** Case number: 3 ****')

    #  --- Zone 1 ---
    test_case_3_zone_1()


def test_case_1_zone_1():
    print('Common parameters')
    fTable = {2: 'F2', 1: 'F1', 3: 'F3'}
    apsmodel = APSModel()
    defineCommonModelParam(
        apsmodel=apsmodel, rmsProject=RMS_PROJECT, rmsWorkflow=RMS_WORKFLOW, gaussFieldSimScript=GAUSS_FIELD_SIM_SCRIPT,
        gridModelName=GRID_MODEL_NAME, zoneParamName=ZONE_PARAM_NAME,
        faciesRealParamNameResult=FACIES_REAL_PARAM_NAME_RESULT, fTable=fTable, debug_level=Debug.VERY_VERBOSE
    )
    # Only one zone
    print('Zone: 1')
    add_zone_1_for_case_1(apsmodel)
    selectedZoneNumber = 1
    selectedRegionNumber = 0
    apsmodel.setSelectedZoneAndRegionNumber(selectedZoneNumber, selectedRegionNumber)
    apsmodel.setPreviewZoneAndRegionNumber(selectedZoneNumber, selectedRegionNumber)
    read_write_model(apsmodel, Debug.VERY_VERBOSE)


def test_case_1_zone_2():
    print('Common parameters')
    fTable = {2: 'F2', 1: 'F1', 3: 'F3'}
    apsmodel = APSModel()
    defineCommonModelParam(
        apsmodel=apsmodel, rmsProject=RMS_PROJECT, rmsWorkflow=RMS_WORKFLOW, gaussFieldSimScript=GAUSS_FIELD_SIM_SCRIPT,
        gridModelName=GRID_MODEL_NAME, zoneParamName=ZONE_PARAM_NAME,
        faciesRealParamNameResult=FACIES_REAL_PARAM_NAME_RESULT, fTable=fTable, debug_level=Debug.SOMEWHAT_VERBOSE
    )
    # Two zones
    print('Zone: 1')
    add_zone_1_for_case_1(apsmodel)
    print('Zone: 2')
    add_zone_2_for_case_1(apsmodel)
    selectedZoneNumber = 1
    selectedRegionNumber = 0
    apsmodel.setSelectedZoneAndRegionNumber(selectedZoneNumber, selectedRegionNumber)

    selectedZoneNumber = 2
    selectedRegionNumber = 0
    apsmodel.setSelectedZoneAndRegionNumber(selectedZoneNumber, selectedRegionNumber)
    apsmodel.setPreviewZoneAndRegionNumber(selectedZoneNumber, selectedRegionNumber)
    read_write_model(apsmodel, Debug.SOMEWHAT_VERBOSE)


def test_case_2_zone_1():
    print('Common parameters')
    fTable = {2: 'F2', 1: 'F1', 3: 'F3', 4: 'F4', 5: 'F5', 6: 'F6', 7: 'F7'}
    apsmodel = APSModel()
    defineCommonModelParam(
        apsmodel=apsmodel, rmsProject=RMS_PROJECT, rmsWorkflow=RMS_WORKFLOW, gaussFieldSimScript=GAUSS_FIELD_SIM_SCRIPT,
        gridModelName=GRID_MODEL_NAME, zoneParamName=ZONE_PARAM_NAME,
        faciesRealParamNameResult=FACIES_REAL_PARAM_NAME_RESULT, fTable=fTable, debug_level=Debug.SOMEWHAT_VERBOSE
    )

    # Only one zone
    print('Zone: 1')
    add_zone_1_for_case_2(apsmodel)
    selectedZoneNumber = 1
    selectedRegionNumber = 0
    apsmodel.setSelectedZoneAndRegionNumber(selectedZoneNumber, selectedRegionNumber)
    apsmodel.setPreviewZoneAndRegionNumber(selectedZoneNumber, selectedRegionNumber)
    read_write_model(apsmodel, Debug.SOMEWHAT_VERBOSE)


def test_case_2_zone_2():
    print('Common parameters')
    fTable = {2: 'F2', 1: 'F1', 3: 'F3', 4: 'F4', 5: 'F5', 6: 'F6', 7: 'F7'}
    apsmodel = APSModel()
    defineCommonModelParam(
        apsmodel=apsmodel, rmsProject=RMS_PROJECT, rmsWorkflow=RMS_WORKFLOW, gaussFieldSimScript=GAUSS_FIELD_SIM_SCRIPT,
        gridModelName=GRID_MODEL_NAME, zoneParamName=ZONE_PARAM_NAME,
        faciesRealParamNameResult=FACIES_REAL_PARAM_NAME_RESULT, fTable=fTable, debug_level=Debug.SOMEWHAT_VERBOSE
    )
    # Two zones
    print('Zone: 1')
    add_zone_1_for_case_2(apsmodel)
    print('Zone: 2')
    add_zone_2_for_case_2(apsmodel)
    selectedZoneNumber = 1
    selectedRegionNumber = 0
    apsmodel.setSelectedZoneAndRegionNumber(selectedZoneNumber, selectedRegionNumber)

    selectedZoneNumber = 2
    selectedRegionNumber = 0
    apsmodel.setSelectedZoneAndRegionNumber(selectedZoneNumber, selectedRegionNumber)
    apsmodel.setPreviewZoneAndRegionNumber(selectedZoneNumber, selectedRegionNumber)
    read_write_model(apsmodel, Debug.SOMEWHAT_VERBOSE)


def test_case_3_zone_1():
    print('Common parameters')
    fTable = {2: 'F2', 1: 'F1', 3: 'F3', 4: 'F4', 5: 'F5', 6: 'F6', 7: 'F7'}
    apsmodel = APSModel()
    defineCommonModelParam(
        apsmodel=apsmodel, rmsProject=RMS_PROJECT, rmsWorkflow=RMS_WORKFLOW, gaussFieldSimScript=GAUSS_FIELD_SIM_SCRIPT,
        gridModelName=GRID_MODEL_NAME, zoneParamName=ZONE_PARAM_NAME,
        faciesRealParamNameResult=FACIES_REAL_PARAM_NAME_RESULT, fTable=fTable, debug_level=Debug.SOMEWHAT_VERBOSE
    )
    # Only one zone
    print('Zone: 1')
    add_zone_1_for_case_3(apsmodel)
    selectedZoneNumber = 1
    selectedRegionNumber = 0
    apsmodel.setSelectedZoneAndRegionNumber(selectedZoneNumber, selectedRegionNumber)
    apsmodel.setPreviewZoneAndRegionNumber(selectedZoneNumber, selectedRegionNumber)
    read_write_model(apsmodel, Debug.SOMEWHAT_VERBOSE)


def add_zone_1_for_case_1(apsmodel):
    addZoneParam(
        apsmodel=apsmodel,
        zoneNumber=1,
        regionNumber=0,
        horizonNameForVariogramTrendMap='zone_1',
        simBoxThickness=4.0,
        # Facies prob for zone
        faciesInZone=['F1', 'F2'],
        useConstProb=1,
        faciesProbList=[0.4, 0.6],
        # Gauss field parameters. One entry in list for each gauss field
        gaussFieldsInZone=['GRF1', 'GRF2'],
        gfTypes=['GENERAL_EXPONENTIAL', 'SPHERICAL'],
        range1=[2000.0, 1500.0],
        range2=[1400.0, 750.0],
        range3=[2.0, 1.0],
        azimuthVariogramAngles=[35.0, 125.0],
        dipVariogramAngles=[0.0, 0.1],
        power=[1.8, 1.0],
        # Trend parameters. One entry in list for each gauss field
        useTrend=[1, 0],
        relStdDev=[0.05, 0],
        azimuthAngle=[125.0, 0.0],
        stackingAngle=[0.1, 0.0],
        direction=[1, 1],
        previewSeed=[9282727, 96785],
        # Truncation rule
        truncType='Cubic',
        alphaFieldNameForBackGroundFacies=['GRF1', 'GRF2'],
        truncStructureList=['V', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0]],
        overlayGroups=[],
        useConstTruncParam=1,
        sf_value=0.0,
        sf_name=None,
        ysf=0.0,
        sbhd=0.0,
        debug_level=NO_VERBOSE_DEBUG
    )


def add_zone_2_for_case_1(apsmodel):
    addZoneParam(
        apsmodel=apsmodel,
        zoneNumber=2,
        regionNumber=0,
        horizonNameForVariogramTrendMap='zone_2',
        simBoxThickness=12.0,
        # Facies prob for zone
        faciesInZone=['F3', 'F1', 'F2'],
        useConstProb=0,
        faciesProbList=['F3_prob', 'F1_prob', 'F2_prob'],
        # Gauss field parameters. One entry in list for each gauss field
        gaussFieldsInZone=['GRF3', 'GRF4', 'GRF5'],
        gfTypes=['GENERAL_EXPONENTIAL', 'SPHERICAL', 'EXPONENTIAL'],
        range1=[2000.0, 1500.0, 6000.0],
        range2=[1400.0, 750.0, 250.0],
        range3=[2.0, 1.0, 4.5],
        azimuthVariogramAngles=[35.0, 125.0, 315.0],
        dipVariogramAngles=[0.01, 0.0, 0.0],
        power=[1.8, 1.0, 1.0],
        # Trend parameters. One entry in list for each gauss field
        useTrend=[0, 1, 0],
        relStdDev=[0, 0.05, 0],
        azimuthAngle=[0.0, 125.0, 0.0],
        stackingAngle=[0.0, 0.1, 0.0],
        direction=[1, -1, 1],
        previewSeed=[8727, 977727, 776785],
        # Truncation rule
        truncType='Angle',
        alphaFieldNameForBackGroundFacies=['GRF3', 'GRF4'],
        truncStructureList=[['F1', 0.0, 1.0], ['F3', 45.0, 1.0]],
        overlayGroups=[[[['GRF5', 'F2', 1.0, 0.5]], ['F1', 'F3']]],
        useConstTruncParam=1,
        debug_level=NO_VERBOSE_DEBUG
    )


def add_zone_1_for_case_2(apsmodel):
    addZoneParam(
        apsmodel=apsmodel,
        zoneNumber=1,
        regionNumber=0,
        horizonNameForVariogramTrendMap='zone_1',
        simBoxThickness=4.0,
        # Facies prob for zone
        faciesInZone=['F1', 'F2', 'F5', 'F7'],
        useConstProb=1,
        faciesProbList=[0.4, 0.5, 0.03, 0.07],
        # Gauss field parameters. One entry in list for each gauss field
        gaussFieldsInZone=['GRF6', 'GRF7', 'GRF8', 'GRF9'],
        gfTypes=['GENERAL_EXPONENTIAL', 'SPHERICAL', 'EXPONENTIAL', 'GENERAL_EXPONENTIAL'],
        range1=[3000.0, 1500.0, 2500.0, 750.0],
        range2=[1400.0, 750.0, 800.0, 5200.0],
        range3=[2.0, 1.0, 4.0, 120.0],
        azimuthVariogramAngles=[35.0, 125.0, 95.0, 323.0],
        dipVariogramAngles=[0.01, 0.0, 0.0, 0.02],
        power=[1.8, 1.0, 1.0, 1.95],
        # Trend parameters. One entry in list for each gauss field
        useTrend=[1, 0, 0, 0],
        relStdDev=[0.05, 0, 0, 0],
        azimuthAngle=[125.0, 0.0, 0.0, 0.0],
        stackingAngle=[0.1, 0.0, 0.0, 0.0],
        direction=[1, 1, 1, 1],
        previewSeed=[9282727, 96785, 88760019, 8156827],
        # Truncation rule
        truncType='Cubic',
        alphaFieldNameForBackGroundFacies=['GRF6', 'GRF7'],
        truncStructureList=['H', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0]],
        overlayGroups=[[[['GRF8', 'F5', 1.0, 0.0]], ['F1']], [[['GRF9', 'F7', 1.0, 0.8]], ['F2']]],
        useConstTruncParam=1,
        debug_level=NO_VERBOSE_DEBUG
    )


def add_zone_2_for_case_2(apsmodel):
    addZoneParam(
        apsmodel=apsmodel,
        zoneNumber=2,
        regionNumber=0,
        horizonNameForVariogramTrendMap='zone_2',
        simBoxThickness=12.0,
        # Facies prob for zone
        faciesInZone=['F3', 'F1', 'F2', 'F5', 'F6', 'F7'],
        useConstProb=0,
        faciesProbList=['F3_prob', 'F1_prob', 'F2_prob', 'F5_prob', 'F6_prob', 'F7_prob'],
        # Gauss field parameters. One entry in list for each gauss field
        gaussFieldsInZone=['GRF6', 'GRF7', 'GRF8', 'GRF9'],
        gfTypes=['GENERAL_EXPONENTIAL', 'SPHERICAL', 'EXPONENTIAL', 'GENERAL_EXPONENTIAL'],
        range1=[2000.0, 2500.0, 1500.0, 1750.0],
        range2=[1400.0, 750.0, 800.0, 5200.0],
        range3=[2.0, 1.0, 4.0, 120.0],
        azimuthVariogramAngles=[135.0, 25.0, 75.0, 23.0],
        dipVariogramAngles=[0.0, 0.0, 0.01, 0.02],
        power=[1.8, 1.0, 1.0, 1.95],
        # Trend parameters. One entry in list for each gauss field
        useTrend=[1, 0, 1, 0],
        relStdDev=[0.05, 0, 0.03, 0],
        azimuthAngle=[125.0, 0.0, 90.0, 0.0],
        stackingAngle=[0.1, 0.0, 0.01, 0.0],
        direction=[1, 1, -1, 1],
        previewSeed=[9282727, 96785, 88760019, 8156827],
        # Truncation rule
        truncType='Angle',
        alphaFieldNameForBackGroundFacies=['GRF6', 'GRF7'],
        truncStructureList=[['F1', 0.0, 1.0], ['F3', 45.0, 1.0], ['F2', -35.0, 1.0], ['F5', 145.0, 1.0]],
        overlayGroups=[[[['GRF8', 'F6', 1.0, 0.5]], ['F1', 'F3']], [[['GRF9', 'F7', 1.0, 0.7]], ['F2', 'F5']]],
        useConstTruncParam=1,
        debug_level=NO_VERBOSE_DEBUG
    )


def add_zone_1_for_case_3(apsmodel):
    addZoneParam(
        apsmodel=apsmodel,
        zoneNumber=1,
        regionNumber=0,
        horizonNameForVariogramTrendMap='zone_1',
        simBoxThickness=4.0,
        # Facies prob for zone
        faciesInZone=['F1', 'F2', 'F5', 'F7', 'F3'],
        useConstProb=1,
        faciesProbList=[0.4, 0.4, 0.03, 0.07, 0.1],
        # Gauss field parameters. One entry in list for each gauss field
        gaussFieldsInZone=['GRF6', 'GRF7', 'GRF8', 'GRF9'],
        gfTypes=['GENERAL_EXPONENTIAL', 'SPHERICAL', 'EXPONENTIAL', 'GENERAL_EXPONENTIAL'],
        range1=[3000.0, 1500.0, 2500.0, 750.0],
        range2=[1400.0, 750.0, 800.0, 5200.0],
        range3=[2.0, 1.0, 4.0, 120.0],
        azimuthVariogramAngles=[35.0, 125.0, 95.0, 323.0],
        dipVariogramAngles=[0.01, 0.0, 0.0, 0.02],
        power=[1.8, 1.0, 1.0, 1.95],
        # Trend parameters. One entry in list for each gauss field
        useTrend=[1, 0, 0, 0],
        relStdDev=[0.05, 0, 0, 0],
        azimuthAngle=[125.0, 0.0, 0.0, 0.0],
        stackingAngle=[0.1, 0.0, 0.0, 0.0],
        direction=[1, 1, 1, 1],
        previewSeed=[9282727, 96785, 88760019, 8156827],
        # Truncation rule
        truncType='Bayfill',
        alphaFieldNameForBackGroundFacies=['GRF6', 'GRF7', 'GRF8'],
        sf_value=0.65,
        ysf=0.5,
        sbhd=0.55,
        useConstTruncParam=1,
        faciesInTruncRule=['F1', 'F2', 'F3', 'F5', 'F7'],
        debug_level=NO_VERBOSE_DEBUG
    )


if __name__ == '__main__':
    test_create_XMLModelFiles()
