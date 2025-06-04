#!/bin/env python
# Python3  test that the model files can be created correctly.
from typing import List, Tuple, TypedDict, Union

import pytest

from aps.algorithms.APSFaciesProb import APSFaciesProb
from aps.algorithms.APSGaussModel import APSGaussModel
from aps.algorithms.APSMainFaciesTable import APSMainFaciesTable
from aps.algorithms.APSModel import APSModel
from aps.algorithms.APSZoneModel import APSZoneModel
from aps.algorithms.trend import (
    Trend3D_elliptic,
    Trend3D_elliptic_cone,
    Trend3D_hyperbolic,
    Trend3D_linear,
)
from aps.algorithms.truncation_rules import (
    Trunc2D_Angle,
    Trunc2D_Cubic,
    Trunc3D_bayfill,
)
from aps.tests.constants import (
    FACIES_REAL_PARAM_NAME_RESULT,
    GRID_MODEL_NAME,
    NO_VERBOSE_DEBUG,
    REGION_PARAM_NAME,
    RMS_PROJECT,
    RMS_WORKFLOW,
    SEED_FILE_NAME,
    VERY_VERBOSE_DEBUG,
    ZONE_PARAM_NAME,
)
from aps.tests.types import FaciesTableType, OverlayGroupType
from aps.utils.checks import compare
from aps.utils.constants.simple import (
    Debug,
    OriginType,
    TransformType,
    TrendType,
    VariogramType,
)


@pytest.fixture
def data_directory(data_directory):
    return data_directory / 'models'


def defineCommonModelParam(
    apsmodel,
    rmsProject,
    rmsWorkflow,
    gridModelName,
    zoneParamName,
    regionParamName,
    faciesRealParamNameResult,
    seedFileName,
    fTable,
    fTable_blockedWell,
    fTable_blockedWellLog,
    debug_level=VERY_VERBOSE_DEBUG,
):
    # The input data are global variables

    if rmsProject is not None:
        apsmodel.rms_project_name = rmsProject
    if rmsWorkflow is not None:
        apsmodel.setRmsWorkflowName(rmsWorkflow)
    apsmodel.setRmsGridModelName(gridModelName)
    apsmodel.setRmsZoneParamName(zoneParamName)
    apsmodel.setRmsResultFaciesParamName(faciesRealParamNameResult)
    if regionParamName:
        apsmodel.setRmsRegionParamName(regionParamName)
    apsmodel.seed_file_name = seedFileName
    apsmodel.debug_level = debug_level
    print('Debug level: {}'.format(apsmodel.debug_level))
    apsmodel.transform_type = TransformType.EMPIRIC

    # Define main facies table
    main_facies_table = APSMainFaciesTable(
        facies_table=fTable,
        blocked_well=fTable_blockedWell,
        blocked_well_log=fTable_blockedWellLog,
    )
    apsmodel.setMainFaciesTable(main_facies_table)


class ZoneDescription(TypedDict, total=False):
    zoneNumber: int
    regionNumber: int
    simBoxThickness: float
    # Facies prob for zone
    faciesInZone: List[str]
    useConstProb: bool
    faciesProbList: List[str | float]
    # Gauss field parameters. One entry in list for each gauss field
    gaussFieldsInZone: List[str]
    gfTypes: List[str]
    range1: List[float]
    range1FmuUpdatable: List[bool]
    range2: List[float]
    range2FmuUpdatable: List[bool]
    range3: List[float]
    range3FmuUpdatable: List[bool]
    azimuthVariogramAngles: List[float]
    azimuthVariogramAnglesFmuUpdatable: List[bool]
    dipVariogramAngles: List[float]
    dipVariogramAnglesFmuUpdatable: List[bool]
    power: List[float]
    powerFmuUpdatable: List[bool]
    # Trend parameters. One entry in list for each gauss field
    useTrend: List[bool]
    relStdDev: List[float]
    relStdDevFmuUpdatable: List[bool]
    azimuthAngle: List[float]
    azimuthAngleFmuUpdatable: List[bool]
    stackingAngle: List[float]
    stackingAngleFmuUpdatable: List[bool]
    direction: List[int]
    trendType: List[TrendType]
    curvature: List[float]
    curvatureFmuUpdatable: List[bool]
    migrationAngle: List[float]
    migrationAngleFmuUpdatable: List[bool]
    relativeSize: List[float]
    relativeSizeFmuUpdatable: List[bool]
    origin_x: List[float]
    origin_y: List[float]
    origin_z_simbox: List[float]
    originFmuUpdatable: List[bool]
    origin_type: List[OriginType]
    previewSeed: List[int]
    # Truncation rule
    truncType: str
    alphaFieldNameForBackGroundFacies: List[str]
    truncStructureList: Union[...]  # Truncation structure
    overlayGroups: List[OverlayGroupType]
    useConstTruncParam: bool
    faciesInTruncRule: List[str]
    sf_value: float
    sf_name: str
    sf_fmu_updatable: bool
    ysf: float
    ysf_fmu_updatable: bool
    sbhd: float
    sbhd_fmu_updatable: bool
    grid_layouts: List[str]  # literal values
    debug_level: Debug


def addZoneParam(
    apsmodel,
    zoneNumber=0,
    regionNumber=0,
    simBoxThickness=0.0,
    # Facies prob for zone
    faciesInZone=None,
    useConstProb=0,
    faciesProbList=None,
    # Gauss field parameters. One entry in list for each gauss field
    gaussFieldsInZone=None,
    gfTypes=None,
    range1=None,
    range1FmuUpdatable=None,
    range2=None,
    range2FmuUpdatable=None,
    range3=None,
    range3FmuUpdatable=None,
    azimuthVariogramAngles=None,
    azimuthVariogramAnglesFmuUpdatable=None,
    dipVariogramAngles=None,
    dipVariogramAnglesFmuUpdatable=None,
    power=None,
    powerFmuUpdatable=None,
    # Trend parameters. One entry in list for each gauss field
    useTrend=None,
    relStdDev=None,
    relStdDevFmuUpdatable=None,
    azimuthAngle=None,
    azimuthAngleFmuUpdatable=None,
    stackingAngle=None,
    stackingAngleFmuUpdatable=None,
    direction=None,
    trendType=None,
    curvature=None,
    curvatureFmuUpdatable=None,
    migrationAngle=None,
    migrationAngleFmuUpdatable=None,
    relativeSize=None,
    relativeSizeFmuUpdatable=None,
    origin_x=None,
    origin_y=None,
    origin_z_simbox=None,
    originFmuUpdatable=None,
    origin_type=None,
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
    sf_fmu_updatable=None,
    ysf=None,
    ysf_fmu_updatable=None,
    sbhd=None,
    sbhd_fmu_updatable=None,
    grid_layouts=None,
    debug_level=Debug.OFF,
):
    main_facies_table = apsmodel.getMainFaciesTable()

    # Define facies probabilities
    facies_probabilities = APSFaciesProb()
    facies_probabilities.initialize(
        faciesList=faciesInZone,
        faciesProbList=faciesProbList,
        mainFaciesTable=main_facies_table,
        useConstProb=useConstProb,
        zoneNumber=zoneNumber,
        debug_level=debug_level,
    )

    # Define gauss field models
    gaussModelList = []
    trendModelList = []
    seedPreviewList = []
    for i in range(len(gaussFieldsInZone)):
        gaussModelList.append(
            [
                gaussFieldsInZone[i],
                gfTypes[i],
                range1[i],
                range2[i],
                range3[i],
                azimuthVariogramAngles[i],
                dipVariogramAngles[i],
                power[i],
                range1FmuUpdatable[i],
                range2FmuUpdatable[i],
                range3FmuUpdatable[i],
                azimuthVariogramAnglesFmuUpdatable[i],
                dipVariogramAnglesFmuUpdatable[i],
                powerFmuUpdatable[i],
            ]
        )

        # Set Gauss field trend parameters
        if trendType[i] == TrendType.LINEAR:
            trend_model = Trend3D_linear(
                azimuthAngle[i],
                azimuthAngleFmuUpdatable[i],
                stackingAngle[i],
                stackingAngleFmuUpdatable[i],
                direction[i],
                debug_level,
            )
            trendModelList.append(
                [
                    gaussFieldsInZone[i],
                    useTrend[i],
                    trend_model,
                    relStdDev[i],
                    relStdDevFmuUpdatable[i],
                ]
            )

        elif trendType[i] == TrendType.ELLIPTIC:
            origin = (origin_x[i], origin_y[i], origin_z_simbox[i])
            trend_model = Trend3D_elliptic(
                azimuthAngle[i],
                azimuthAngleFmuUpdatable[i],
                stackingAngle[i],
                stackingAngleFmuUpdatable[i],
                curvature[i],
                curvatureFmuUpdatable[i],
                origin,
                originFmuUpdatable[i],
                origin_type[i],
                direction[i],
                debug_level,
            )
            trendModelList.append(
                [
                    gaussFieldsInZone[i],
                    useTrend[i],
                    trend_model,
                    relStdDev[i],
                    relStdDevFmuUpdatable[i],
                ]
            )

        elif trendType[i] == TrendType.HYPERBOLIC:
            origin = (origin_x[i], origin_y[i], origin_z_simbox[i])
            trend_model = Trend3D_hyperbolic(
                azimuthAngle[i],
                azimuthAngleFmuUpdatable[i],
                stackingAngle[i],
                stackingAngleFmuUpdatable[i],
                curvature[i],
                curvatureFmuUpdatable[i],
                migrationAngle[i],
                migrationAngleFmuUpdatable[i],
                origin,
                originFmuUpdatable[i],
                origin_type[i],
                direction[i],
                debug_level,
            )
            trendModelList.append(
                [
                    gaussFieldsInZone[i],
                    useTrend[i],
                    trend_model,
                    relStdDev[i],
                    relStdDevFmuUpdatable[i],
                ]
            )

        elif trendType[i] == TrendType.ELLIPTIC_CONE:
            origin = (origin_x[i], origin_y[i], origin_z_simbox[i])
            trend_model = Trend3D_elliptic_cone(
                azimuthAngle[i],
                azimuthAngleFmuUpdatable[i],
                stackingAngle[i],
                stackingAngleFmuUpdatable[i],
                curvature[i],
                curvatureFmuUpdatable[i],
                migrationAngle[i],
                migrationAngleFmuUpdatable[i],
                relativeSize[i],
                relativeSizeFmuUpdatable[0],
                origin,
                originFmuUpdatable[i],
                origin_type[i],
                direction[i],
                debug_level,
            )
            trendModelList.append(
                [
                    gaussFieldsInZone[i],
                    useTrend[i],
                    trend_model,
                    relStdDev[i],
                    relStdDevFmuUpdatable[i],
                ]
            )

        elif trendType[i] == TrendType.NONE:
            # Create an arbitary trend object which is not initialized
            # TODO: Make instance of Trend3D?
            trend_model = Trend3D_hyperbolic()
            trendModelList.append(
                [
                    gaussFieldsInZone[i],
                    useTrend[i],
                    trend_model,
                    relStdDev[i],
                    relStdDevFmuUpdatable[i],
                ]
            )

        seedPreviewList.append([gaussFieldsInZone[i], previewSeed[i]])

    gauss_model = APSGaussModel()
    gauss_model.initialize(
        main_facies_table=main_facies_table,
        gauss_model_list=gaussModelList,
        trend_model_list=trendModelList,
        sim_box_thickness=simBoxThickness,
        preview_seed_list=seedPreviewList,
        debug_level=debug_level,
    )

    if truncType == 'Angle':
        truncRuleObj = Trunc2D_Angle()
        truncRuleObj.initialize(
            mainFaciesTable=main_facies_table,
            faciesInZone=faciesInZone,
            gaussFieldsInZone=gaussFieldsInZone,
            alphaFieldNameForBackGroundFacies=alphaFieldNameForBackGroundFacies,
            truncStructure=truncStructureList,
            overlayGroups=overlayGroups,
            useConstTruncParam=useConstTruncParam,
            debug_level=debug_level,
        )
    elif truncType == 'Bayfill':
        truncRuleObj = Trunc3D_bayfill()
        truncRuleObj.initialize(
            mainFaciesTable=main_facies_table,
            faciesInZone=faciesInZone,
            faciesInTruncRule=faciesInTruncRule,
            gaussFieldsInZone=gaussFieldsInZone,
            alphaFieldNameForBackGroundFacies=alphaFieldNameForBackGroundFacies,
            sf_value=sf_value,
            sf_name=sf_name,
            sf_fmu_updatable=sf_fmu_updatable,
            ysf=ysf,
            ysf_fmu_updatable=ysf_fmu_updatable,
            sbhd=sbhd,
            sbhd_fmu_updatable=sbhd_fmu_updatable,
            useConstTruncParam=useConstTruncParam,
            debug_level=debug_level,
        )
    elif truncType == 'Cubic':
        truncRuleObj = Trunc2D_Cubic()
        truncRuleObj.initialize(
            mainFaciesTable=main_facies_table,
            faciesInZone=faciesInZone,
            gaussFieldsInZone=gaussFieldsInZone,
            alphaFieldNameForBackGroundFacies=alphaFieldNameForBackGroundFacies,
            truncStructureList=truncStructureList,
            overlayGroups=overlayGroups,
            debug_level=debug_level,
        )
    else:
        raise ValueError('Invalid truncation type')
    # Initialize data for this zone
    apsZoneModel = APSZoneModel(
        zoneNumber=zoneNumber,
        regionNumber=regionNumber,
        useConstProb=useConstProb,
        simBoxThickness=simBoxThickness,
        faciesProbObject=facies_probabilities,
        gaussModelObject=gauss_model,
        truncRuleObject=truncRuleObj,
        grid_layout=grid_layouts[i] if grid_layouts else None,
        debug_level=debug_level,
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


@pytest.fixture
def aps_model(
    facies_table: FaciesTableType,
    zone_descriptions: List[ZoneDescription],
    zone_region_selections: List[Tuple[int, int]],
    rmsProject=RMS_PROJECT,
    rmsWorkflow=RMS_WORKFLOW,
    gridModelName=GRID_MODEL_NAME,
    zoneParamName=ZONE_PARAM_NAME,
    regionParamName=REGION_PARAM_NAME,
    faciesRealParamNameResult=FACIES_REAL_PARAM_NAME_RESULT,
    seedFileName=SEED_FILE_NAME,
    fTable_blockedWell='BW',
    fTable_blockedWellLog='facies',
    debug_level: Debug = Debug.OFF,
):
    apsmodel = APSModel()
    defineCommonModelParam(
        apsmodel=apsmodel,
        rmsProject=rmsProject,
        rmsWorkflow=rmsWorkflow,
        gridModelName=gridModelName,
        zoneParamName=zoneParamName,
        regionParamName=regionParamName,
        faciesRealParamNameResult=faciesRealParamNameResult,
        seedFileName=seedFileName,
        fTable=facies_table,
        fTable_blockedWell=fTable_blockedWell,
        fTable_blockedWellLog=fTable_blockedWellLog,
        debug_level=debug_level,
    )
    for zone_description in zone_descriptions:
        addZoneParam(apsmodel, **zone_description)
    for zone_number, region_number in zone_region_selections:
        apsmodel.setSelectedZoneAndRegionNumber(zone_number, region_number)
        apsmodel.setPreviewZoneAndRegionNumber(zone_number, region_number)
    return apsmodel


@pytest.mark.parametrize(
    [
        'facies_table',
        'zone_descriptions',
        'zone_region_selections',
        'debug_level',
    ],
    [
        (
            {2: 'F2', 1: 'F1', 3: 'F3'},
            [
                ZoneDescription(
                    zoneNumber=1,
                    regionNumber=0,
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
                    range1FmuUpdatable=[False, False],
                    range2FmuUpdatable=[False, False],
                    range3FmuUpdatable=[False, False],
                    azimuthVariogramAnglesFmuUpdatable=[False, False],
                    dipVariogramAnglesFmuUpdatable=[False, False],
                    powerFmuUpdatable=[False, False],
                    # Trend parameters. One entry in list for each gauss field
                    useTrend=[1, 0],
                    relStdDev=[0.05, 0.0],
                    relStdDevFmuUpdatable=[True, True],
                    azimuthAngle=[125.0, 0.0],
                    stackingAngle=[0.1, 0.0],
                    azimuthAngleFmuUpdatable=[True, True],
                    stackingAngleFmuUpdatable=[True, True],
                    direction=[1, 1],
                    trendType=[TrendType.LINEAR, TrendType.LINEAR],
                    previewSeed=[9282727, 96785],
                    # Truncation rule
                    truncType='Cubic',
                    alphaFieldNameForBackGroundFacies=['GRF1', 'GRF2'],
                    truncStructureList=[
                        'V',
                        ['F1', 1.0, 1, 0, 0],
                        ['F2', 1.0, 2, 0, 0],
                    ],
                    overlayGroups=[],
                    useConstTruncParam=1,
                    sf_value=0.0,
                    sf_name=None,
                    ysf=0.0,
                    sbhd=0.0,
                    grid_layouts=['TopConform', 'TopConform'],
                ),
            ],
            [
                [1, 0],
            ],
            Debug.VERY_VERBOSE,
        ),
        (
            {2: 'F2', 1: 'F1', 3: 'F3'},
            [
                ZoneDescription(
                    zoneNumber=1,
                    regionNumber=0,
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
                    range1FmuUpdatable=[False, False],
                    range2FmuUpdatable=[False, False],
                    range3FmuUpdatable=[False, False],
                    azimuthVariogramAnglesFmuUpdatable=[False, False],
                    dipVariogramAnglesFmuUpdatable=[False, False],
                    powerFmuUpdatable=[False, False],
                    # Trend parameters. One entry in list for each gauss field
                    useTrend=[1, 0],
                    relStdDev=[0.05, 0.0],
                    relStdDevFmuUpdatable=[True, True],
                    azimuthAngle=[125.0, 0.0],
                    stackingAngle=[0.1, 0.0],
                    azimuthAngleFmuUpdatable=[True, True],
                    stackingAngleFmuUpdatable=[True, True],
                    direction=[1, 1],
                    trendType=[TrendType.LINEAR, TrendType.LINEAR],
                    previewSeed=[9282727, 96785],
                    # Truncation rule
                    truncType='Cubic',
                    alphaFieldNameForBackGroundFacies=['GRF1', 'GRF2'],
                    truncStructureList=[
                        'V',
                        ['F1', 1.0, 1, 0, 0],
                        ['F2', 1.0, 2, 0, 0],
                    ],
                    overlayGroups=[],
                    useConstTruncParam=1,
                    sf_value=0.0,
                    sf_name=None,
                    ysf=0.0,
                    sbhd=0.0,
                    grid_layouts=['TopConform', 'TopConform'],
                    debug_level=NO_VERBOSE_DEBUG,
                ),
                ZoneDescription(
                    zoneNumber=2,
                    regionNumber=0,
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
                    range1FmuUpdatable=[True, False, True],
                    range2FmuUpdatable=[True, False, True],
                    range3FmuUpdatable=[True, False, True],
                    azimuthVariogramAnglesFmuUpdatable=[True, False, True],
                    dipVariogramAnglesFmuUpdatable=[True, False, True],
                    powerFmuUpdatable=[True, False, True],
                    # Trend parameters. One entry in list for each gauss field
                    useTrend=[0, 1, 0],
                    relStdDev=[0, 0.05, 0],
                    relStdDevFmuUpdatable=[True, True, True],
                    azimuthAngle=[0.0, 125.0, 0.0],
                    stackingAngle=[0.0, 0.1, 0.0],
                    azimuthAngleFmuUpdatable=[True, True, True],
                    stackingAngleFmuUpdatable=[True, True, True],
                    direction=[1, -1, 1],
                    trendType=[
                        TrendType.LINEAR,
                        TrendType.ELLIPTIC,
                        TrendType.ELLIPTIC,
                    ],
                    curvature=[1.0, 2.0, 1.0],
                    curvatureFmuUpdatable=[True, True, True],
                    migrationAngle=[0, 0, 0],
                    migrationAngleFmuUpdatable=[True, True, True],
                    origin_x=[0.5, 0.5, 0.5],
                    origin_y=[0.0, 0.0, 0.0],
                    origin_z_simbox=[0.0, 0.0, 0.0],
                    originFmuUpdatable=[True, True, True],
                    origin_type=[
                        OriginType.RELATIVE,
                        OriginType.RELATIVE,
                        OriginType.RELATIVE,
                    ],
                    previewSeed=[8727, 977727, 776785],
                    # Truncation rule
                    truncType='Angle',
                    alphaFieldNameForBackGroundFacies=['GRF3', 'GRF4'],
                    truncStructureList=[
                        ['F1', 0.0, 1.0, True],
                        ['F3', 45.0, 1.0, False],
                    ],
                    overlayGroups=[[[['GRF5', 'F2', 1.0, 0.5]], ['F1', 'F3']]],
                    useConstTruncParam=1,
                    grid_layouts=['TopConform', 'TopConform', 'TopConform'],
                    debug_level=NO_VERBOSE_DEBUG,
                ),
            ],
            [
                [1, 0],
                [2, 0],
            ],
            Debug.ON,
        ),
        (
            {2: 'F2', 1: 'F1', 3: 'F3', 4: 'F4', 5: 'F5', 6: 'F6', 7: 'F7'},
            [
                ZoneDescription(
                    zoneNumber=1,
                    regionNumber=0,
                    simBoxThickness=4.0,
                    # Facies prob for zone
                    faciesInZone=['F1', 'F2', 'F5', 'F7'],
                    useConstProb=1,
                    faciesProbList=[0.4, 0.5, 0.03, 0.07],
                    # Gauss field parameters. One entry in list for each gauss field
                    gaussFieldsInZone=['GRF6', 'GRF7', 'GRF8', 'GRF9'],
                    gfTypes=[
                        'GENERAL_EXPONENTIAL',
                        'SPHERICAL',
                        'EXPONENTIAL',
                        'GENERAL_EXPONENTIAL',
                    ],
                    range1=[3000.0, 1500.0, 2500.0, 750.0],
                    range2=[1400.0, 750.0, 800.0, 5200.0],
                    range3=[2.0, 1.0, 4.0, 120.0],
                    azimuthVariogramAngles=[35.0, 125.0, 95.0, 323.0],
                    dipVariogramAngles=[0.01, 0.0, 0.0, 0.02],
                    power=[1.8, 1.0, 1.0, 1.95],
                    range1FmuUpdatable=[True, True, True, True],
                    range2FmuUpdatable=[True, True, True, True],
                    range3FmuUpdatable=[True, True, True, True],
                    azimuthVariogramAnglesFmuUpdatable=[True, True, True, True],
                    dipVariogramAnglesFmuUpdatable=[True, True, True, True],
                    powerFmuUpdatable=[True, True, True, True],
                    # Trend parameters. One entry in list for each gauss field
                    useTrend=[1, 0, 0, 0],
                    relStdDev=[0.05, 0, 0, 0],
                    relStdDevFmuUpdatable=[True, True, True, True],
                    azimuthAngle=[125.0, 0.0, 0.0, 0.0],
                    stackingAngle=[0.1, 0.0, 0.0, 0.0],
                    azimuthAngleFmuUpdatable=[True, True, True, True],
                    stackingAngleFmuUpdatable=[True, True, True, True],
                    direction=[1, 1, 1, 1],
                    trendType=[
                        TrendType.HYPERBOLIC,
                        TrendType.ELLIPTIC,
                        TrendType.ELLIPTIC,
                        TrendType.ELLIPTIC,
                    ],
                    curvature=[2.0, 2.0, 1.0, 1.0],
                    curvatureFmuUpdatable=[True, True, True, True],
                    migrationAngle=[88.0, 0, 0, 0],
                    migrationAngleFmuUpdatable=[True, True, True, True],
                    origin_x=[0.5, 0.5, 0.5, 0.5],
                    origin_y=[0.5, 0.0, 0.0, 0.0],
                    origin_z_simbox=[0.5, 0.0, 0.0, 0.0],
                    originFmuUpdatable=[True, True, True, True],
                    origin_type=[
                        OriginType.RELATIVE,
                        OriginType.RELATIVE,
                        OriginType.RELATIVE,
                        OriginType.RELATIVE,
                    ],
                    previewSeed=[9282727, 96785, 88760019, 8156827],
                    # Truncation rule
                    truncType='Cubic',
                    alphaFieldNameForBackGroundFacies=['GRF6', 'GRF7'],
                    truncStructureList=[
                        'H',
                        ['F1', 1.0, 1, 0, 0],
                        ['F2', 1.0, 2, 0, 0],
                    ],
                    overlayGroups=[
                        [[['GRF8', 'F5', 1.0, 0.0]], ['F1']],
                        [[['GRF9', 'F7', 1.0, 0.8]], ['F2']],
                    ],
                    useConstTruncParam=1,
                    grid_layouts=[
                        'TopConform',
                        'TopConform',
                        'TopConform',
                        'TopConform',
                    ],
                    debug_level=NO_VERBOSE_DEBUG,
                ),
            ],
            [
                [1, 0],
            ],
            Debug.ON,
        ),
        (
            {2: 'F2', 1: 'F1', 3: 'F3', 4: 'F4', 5: 'F5', 6: 'F6', 7: 'F7'},
            [
                ZoneDescription(
                    zoneNumber=1,
                    regionNumber=0,
                    simBoxThickness=4.0,
                    # Facies prob for zone
                    faciesInZone=['F1', 'F2', 'F5', 'F7'],
                    useConstProb=1,
                    faciesProbList=[0.4, 0.5, 0.03, 0.07],
                    # Gauss field parameters. One entry in list for each gauss field
                    gaussFieldsInZone=['GRF6', 'GRF7', 'GRF8', 'GRF9'],
                    gfTypes=[
                        'GENERAL_EXPONENTIAL',
                        'SPHERICAL',
                        'EXPONENTIAL',
                        'GENERAL_EXPONENTIAL',
                    ],
                    range1=[3000.0, 1500.0, 2500.0, 750.0],
                    range2=[1400.0, 750.0, 800.0, 5200.0],
                    range3=[2.0, 1.0, 4.0, 120.0],
                    azimuthVariogramAngles=[35.0, 125.0, 95.0, 323.0],
                    dipVariogramAngles=[0.01, 0.0, 0.0, 0.02],
                    power=[1.8, 1.0, 1.0, 1.95],
                    range1FmuUpdatable=[True, True, True, True],
                    range2FmuUpdatable=[True, True, True, True],
                    range3FmuUpdatable=[True, True, True, True],
                    azimuthVariogramAnglesFmuUpdatable=[True, True, True, True],
                    dipVariogramAnglesFmuUpdatable=[True, True, True, True],
                    powerFmuUpdatable=[True, True, True, True],
                    # Trend parameters. One entry in list for each gauss field
                    useTrend=[1, 0, 0, 0],
                    relStdDev=[0.05, 0, 0, 0],
                    relStdDevFmuUpdatable=[True, True, True, True],
                    azimuthAngle=[125.0, 0.0, 0.0, 0.0],
                    stackingAngle=[0.1, 0.0, 0.0, 0.0],
                    azimuthAngleFmuUpdatable=[True, True, True, True],
                    stackingAngleFmuUpdatable=[True, True, True, True],
                    direction=[1, 1, 1, 1],
                    trendType=[
                        TrendType.HYPERBOLIC,
                        TrendType.ELLIPTIC,
                        TrendType.ELLIPTIC,
                        TrendType.ELLIPTIC,
                    ],
                    curvature=[2.0, 2.0, 1.0, 1.0],
                    curvatureFmuUpdatable=[True, True, True, True],
                    migrationAngle=[88.0, 0, 0, 0],
                    migrationAngleFmuUpdatable=[True, True, True, True],
                    origin_x=[0.5, 0.5, 0.5, 0.5],
                    origin_y=[0.5, 0.0, 0.0, 0.0],
                    origin_z_simbox=[0.5, 0.0, 0.0, 0.0],
                    originFmuUpdatable=[True, True, True, True],
                    origin_type=[
                        OriginType.RELATIVE,
                        OriginType.RELATIVE,
                        OriginType.RELATIVE,
                        OriginType.RELATIVE,
                    ],
                    previewSeed=[9282727, 96785, 88760019, 8156827],
                    # Truncation rule
                    truncType='Cubic',
                    alphaFieldNameForBackGroundFacies=['GRF6', 'GRF7'],
                    truncStructureList=[
                        'H',
                        ['F1', 1.0, 1, 0, 0],
                        ['F2', 1.0, 2, 0, 0],
                    ],
                    overlayGroups=[
                        [[['GRF8', 'F5', 1.0, 0.0]], ['F1']],
                        [[['GRF9', 'F7', 1.0, 0.8]], ['F2']],
                    ],
                    useConstTruncParam=1,
                    grid_layouts=[
                        'TopConform',
                        'TopConform',
                        'TopConform',
                        'TopConform',
                    ],
                    debug_level=NO_VERBOSE_DEBUG,
                ),
                ZoneDescription(
                    zoneNumber=2,
                    regionNumber=0,
                    simBoxThickness=12.0,
                    # Facies prob for zone
                    faciesInZone=['F3', 'F1', 'F2', 'F5', 'F6', 'F7'],
                    useConstProb=0,
                    faciesProbList=[
                        'F3_prob',
                        'F1_prob',
                        'F2_prob',
                        'F5_prob',
                        'F6_prob',
                        'F7_prob',
                    ],
                    # Gauss field parameters. One entry in list for each gauss field
                    gaussFieldsInZone=['GRF6', 'GRF7', 'GRF8', 'GRF9'],
                    gfTypes=[
                        'GENERAL_EXPONENTIAL',
                        'SPHERICAL',
                        'EXPONENTIAL',
                        'GENERAL_EXPONENTIAL',
                    ],
                    range1=[2000.0, 2500.0, 1500.0, 1750.0],
                    range2=[1400.0, 750.0, 800.0, 5200.0],
                    range3=[2.0, 1.0, 4.0, 120.0],
                    azimuthVariogramAngles=[135.0, 25.0, 75.0, 23.0],
                    dipVariogramAngles=[0.0, 0.0, 0.01, 0.02],
                    power=[1.8, 1.0, 1.0, 1.95],
                    range1FmuUpdatable=[True, True, True, True],
                    range2FmuUpdatable=[True, True, True, True],
                    range3FmuUpdatable=[True, True, True, True],
                    azimuthVariogramAnglesFmuUpdatable=[True, True, True, True],
                    dipVariogramAnglesFmuUpdatable=[True, True, True, True],
                    powerFmuUpdatable=[True, True, True, True],
                    # Trend parameters. One entry in list for each gauss field
                    useTrend=[1, 0, 1, 0],
                    relStdDev=[0.05, 0, 0.03, 0],
                    relStdDevFmuUpdatable=[True, True, True, True],
                    azimuthAngle=[125.0, 0.0, 90.0, 0.0],
                    stackingAngle=[0.1, 0.0, 0.01, 0.0],
                    azimuthAngleFmuUpdatable=[True, True, True, True],
                    stackingAngleFmuUpdatable=[True, True, True, True],
                    direction=[1, 1, -1, 1],
                    trendType=[
                        TrendType.HYPERBOLIC,
                        TrendType.ELLIPTIC,
                        TrendType.ELLIPTIC,
                        TrendType.ELLIPTIC,
                    ],
                    curvature=[10.0, 2.0, 1.0, 1.0],
                    curvatureFmuUpdatable=[True, True, True, True],
                    migrationAngle=[88.0, 0, 0, 0],
                    migrationAngleFmuUpdatable=[True, True, True, True],
                    origin_x=[0.5, 0.5, 0.5, 0.5],
                    origin_y=[0.5, 0.0, 0.0, 0.0],
                    origin_z_simbox=[0.5, 0.0, 0.0, 0.0],
                    originFmuUpdatable=[True, True, True, True],
                    origin_type=[
                        OriginType.RELATIVE,
                        OriginType.RELATIVE,
                        OriginType.RELATIVE,
                        OriginType.RELATIVE,
                    ],
                    previewSeed=[9282727, 96785, 88760019, 8156827],
                    # Truncation rule
                    truncType='Angle',
                    alphaFieldNameForBackGroundFacies=['GRF6', 'GRF7'],
                    truncStructureList=[
                        ['F1', 0.0, 1.0, True],
                        ['F3', 45.0, 1.0, True],
                        ['F2', -35.0, 1.0, True],
                        ['F5', 145.0, 1.0, True],
                    ],
                    overlayGroups=[
                        [[['GRF8', 'F6', 1.0, 0.5]], ['F1', 'F3']],
                        [[['GRF9', 'F7', 1.0, 0.7]], ['F2', 'F5']],
                    ],
                    useConstTruncParam=1,
                    grid_layouts=[
                        'TopConform',
                        'TopConform',
                        'TopConform',
                        'TopConform',
                    ],
                    debug_level=NO_VERBOSE_DEBUG,
                ),
            ],
            [
                [1, 0],
                [2, 0],
            ],
            Debug.ON,
        ),
        (
            {2: 'F2', 1: 'F1', 3: 'F3', 4: 'F4', 5: 'F5', 6: 'F6', 7: 'F7'},
            [
                ZoneDescription(
                    zoneNumber=1,
                    regionNumber=0,
                    simBoxThickness=4.0,
                    # Facies prob for zone
                    faciesInZone=['F1', 'F2', 'F5', 'F7', 'F3'],
                    useConstProb=1,
                    faciesProbList=[0.4, 0.4, 0.03, 0.07, 0.1],
                    # Gauss field parameters. One entry in list for each gauss field
                    gaussFieldsInZone=['GRF6', 'GRF7', 'GRF8', 'GRF9'],
                    gfTypes=[
                        'GENERAL_EXPONENTIAL',
                        'SPHERICAL',
                        'EXPONENTIAL',
                        'GENERAL_EXPONENTIAL',
                    ],
                    range1=[3000.0, 1500.0, 2500.0, 750.0],
                    range2=[1400.0, 750.0, 800.0, 5200.0],
                    range3=[2.0, 1.0, 4.0, 120.0],
                    azimuthVariogramAngles=[35.0, 125.0, 95.0, 323.0],
                    dipVariogramAngles=[0.01, 0.0, 0.0, 0.02],
                    power=[1.8, 1.0, 1.0, 1.95],
                    range1FmuUpdatable=[True, False, True, False],
                    range2FmuUpdatable=[True, False, True, False],
                    range3FmuUpdatable=[True, False, True, False],
                    azimuthVariogramAnglesFmuUpdatable=[True, False, True, False],
                    dipVariogramAnglesFmuUpdatable=[True, False, True, False],
                    powerFmuUpdatable=[True, False, True, False],
                    # Trend parameters. One entry in list for each gauss field
                    useTrend=[1, 0, 0, 0],
                    relStdDev=[0.05, 0, 0, 0],
                    relStdDevFmuUpdatable=[True, True, True, True],
                    azimuthAngle=[125.0, 0.0, 0.0, 0.0],
                    stackingAngle=[0.1, 0.0, 0.0, 0.0],
                    azimuthAngleFmuUpdatable=[True, True, True, True],
                    stackingAngleFmuUpdatable=[True, True, True, True],
                    direction=[1, 1, 1, 1],
                    trendType=[
                        TrendType.HYPERBOLIC,
                        TrendType.ELLIPTIC,
                        TrendType.ELLIPTIC,
                        TrendType.ELLIPTIC,
                    ],
                    curvature=[6.1, 2.0, 1.0, 1.0],
                    curvatureFmuUpdatable=[True, True, True, True],
                    migrationAngle=[0.0, 0.0, 0.0, 0.0],
                    migrationAngleFmuUpdatable=[True, True, True, True],
                    origin_x=[450000.0, 0.5, 0.5, 0.5],
                    origin_y=[6000000.0, 0.5, 0.0, 0.0],
                    origin_z_simbox=[0.5, 0.0, 0.0, 0.0],
                    originFmuUpdatable=[True, True, True, True],
                    origin_type=[
                        OriginType.ABSOLUTE,
                        OriginType.RELATIVE,
                        OriginType.RELATIVE,
                        OriginType.RELATIVE,
                    ],
                    previewSeed=[9282727, 96785, 88760019, 8156827],
                    # Truncation rule
                    truncType='Bayfill',
                    alphaFieldNameForBackGroundFacies=['GRF6', 'GRF7', 'GRF8'],
                    sf_value=0.65,
                    ysf=0.5,
                    sbhd=0.55,
                    useConstTruncParam=1,
                    faciesInTruncRule=['F1', 'F2', 'F3', 'F5', 'F7'],
                    grid_layouts=[
                        'TopConform',
                        'TopConform',
                        'TopConform',
                        'TopConform',
                    ],
                    debug_level=NO_VERBOSE_DEBUG,
                )
            ],
            [
                [1, 0],
            ],
            Debug.ON,
        ),
        (
            {2: 'F2', 1: 'F1', 3: 'F3', 4: 'F4', 5: 'F5', 6: 'F6', 7: 'F7'},
            [
                ZoneDescription(
                    zoneNumber=1,
                    regionNumber=0,
                    simBoxThickness=4.0,
                    # Facies prob for zone
                    faciesInZone=['F1', 'F2', 'F5', 'F7', 'F3'],
                    useConstProb=1,
                    faciesProbList=[0.4, 0.4, 0.03, 0.07, 0.1],
                    # Gauss field parameters. One entry in list for each gauss field
                    gaussFieldsInZone=['GRF6', 'GRF7', 'GRF8', 'GRF9'],
                    gfTypes=[
                        'GENERAL_EXPONENTIAL',
                        'SPHERICAL',
                        'EXPONENTIAL',
                        'GENERAL_EXPONENTIAL',
                    ],
                    range1=[3000.0, 1500.0, 2500.0, 750.0],
                    range2=[1400.0, 750.0, 800.0, 5200.0],
                    range3=[2.0, 1.0, 4.0, 120.0],
                    azimuthVariogramAngles=[35.0, 125.0, 95.0, 323.0],
                    dipVariogramAngles=[0.01, 0.0, 0.0, 0.02],
                    power=[1.8, 1.0, 1.0, 1.95],
                    range1FmuUpdatable=[True, False, True, False],
                    range2FmuUpdatable=[True, False, True, False],
                    range3FmuUpdatable=[True, False, True, False],
                    azimuthVariogramAnglesFmuUpdatable=[True, False, True, False],
                    dipVariogramAnglesFmuUpdatable=[True, False, True, False],
                    powerFmuUpdatable=[True, False, True, False],
                    # Trend parameters. One entry in list for each gauss field
                    useTrend=[1, 1, 0, 0],
                    relStdDev=[0.05, 0.06, 0, 0],
                    relStdDevFmuUpdatable=[True, True, True, True],
                    azimuthAngle=[125.0, 80.0, 0.0, 0.0],
                    stackingAngle=[0.1, 0.025, 0.0, 0.0],
                    azimuthAngleFmuUpdatable=[True, True, True, True],
                    stackingAngleFmuUpdatable=[True, True, True, True],
                    direction=[1, 1, 1, 1],
                    trendType=[
                        TrendType.HYPERBOLIC,
                        TrendType.ELLIPTIC_CONE,
                        TrendType.NONE,
                        TrendType.NONE,
                    ],
                    curvature=[2.5, 2.9, 0, 0],
                    curvatureFmuUpdatable=[True, True, True, True],
                    migrationAngle=[89.5, 88.0, 0, 0],
                    migrationAngleFmuUpdatable=[True, True, True, True],
                    relativeSize=[0, 1.0, 0, 0],
                    relativeSizeFmuUpdatable=[True, True, True, True],
                    origin_x=[0.5, 0.5, 0.5, 0.5],
                    origin_y=[0.0, 0.0, 0.0, 0.0],
                    origin_z_simbox=[1.0, 1.0, 1.0, 1.0],
                    originFmuUpdatable=[True, True, True, True],
                    origin_type=[
                        OriginType.RELATIVE,
                        OriginType.RELATIVE,
                        OriginType.RELATIVE,
                        OriginType.RELATIVE,
                    ],
                    previewSeed=[9282727, 96785, 88760019, 8156827],
                    # Truncation rule
                    truncType='Bayfill',
                    alphaFieldNameForBackGroundFacies=['GRF6', 'GRF7', 'GRF8'],
                    sf_value=0.65,
                    ysf=0.5,
                    sbhd=0.55,
                    useConstTruncParam=1,
                    faciesInTruncRule=['F1', 'F2', 'F3', 'F5', 'F7'],
                    grid_layouts=[
                        'TopConform',
                        'TopConform',
                        'TopConform',
                        'TopConform',
                    ],
                    debug_level=NO_VERBOSE_DEBUG,
                )
            ],
            [
                [1, 0],
            ],
            Debug.ON,
        ),
    ],
)
def test_read_write_model(
    aps_model,
    output_directory,
    debug_level,
):
    outfile1 = output_directory / 'testOut1.xml'
    attributesFile = output_directory / 'fmu_attributes.yaml'
    aps_model.write_model(outfile1, attributesFile, debug_level=debug_level)

    # Read the xml file into an new APSModel object
    apsmodel2 = APSModel(outfile1, debug_level=debug_level)
    outfile2 = output_directory / 'testOut2.xml'
    attributesFile = output_directory / 'fmu_attributes.yaml'
    apsmodel2.write_model(outfile2, attributesFile, debug_level=debug_level)
    print(f'Compare file: {outfile1} and {outfile2}')
    check = compare(outfile1, outfile2)

    assert check is True
    print('')


def test_should_not_be_able_to_add_zones_with_region_to_apsmodel_when_regionparamname_is_empty():
    create_apsmodel_with_and_without_regions_and_regionparam(True, True)
    with pytest.raises(ValueError):
        create_apsmodel_with_and_without_regions_and_regionparam(True, False)
    create_apsmodel_with_and_without_regions_and_regionparam(False, True)
    create_apsmodel_with_and_without_regions_and_regionparam(False, False)


def test_should_not_be_able_to_remove_region_parameter_name_when_at_least_one_zone_has_region_number():
    aps_model = create_apsmodel_with_and_without_regions_and_regionparam(True, True)
    with pytest.raises(ValueError):
        aps_model.setRmsRegionParamName(None)
    aps_model = create_apsmodel_with_and_without_regions_and_regionparam(True, True)
    with pytest.raises(ValueError):
        aps_model.setRmsRegionParamName('')


def test_read_and_write_modelfiles_without_project_name_work_flow_name_and_region_parameter_name(
    output_directory,
    debug_level=Debug.OFF,
):
    _attributes_file = output_directory / 'fmu_attributes.yaml'

    aps_model = create_apsmodel_with_and_without_regions_and_regionparam(False, True)
    aps_model.rms_project_name = None
    aps_model.setRmsWorkflowName(None)
    aps_model.setRmsRegionParamName(None)

    outfile1 = output_directory / 'testOut4.xml'
    aps_model.write_model(outfile1, _attributes_file, debug_level=Debug.OFF)

    aps_model_2 = APSModel(outfile1, debug_level=Debug.READ)

    outfile2 = output_directory / 'testOut5.xml'
    aps_model_2.write_model(outfile2, _attributes_file, debug_level=Debug.OFF)

    assert compare(outfile1, outfile2)


def test_variogram_generation():
    print('****** Set variogram parameters ******')
    apsGaussModel = APSGaussModel()
    zoneNumber = 1
    # Define main facies table
    fTable = {2: 'F2', 1: 'F1', 3: 'F3'}
    mainFaciesTable = APSMainFaciesTable(facies_table=fTable)
    mainRange = 1000
    perpRange = 100
    vertRange = 1.0
    azimuth = 45.0
    dip = 1.0
    range1FmuUpdatable = True
    range2FmuUpdatable = True
    range3FmuUpdatable = True
    azimuthVariogramAnglesFmuUpdatable = True
    dipVariogramAnglesFmuUpdatable = True
    powerFmuUpdatable = True
    gfName = 'GRF1'
    gaussModelList = [
        [
            'GRF1',
            'SPHERICAL',
            mainRange,
            perpRange,
            vertRange,
            azimuth,
            dip,
            1.0,
            range1FmuUpdatable,
            range2FmuUpdatable,
            range3FmuUpdatable,
            azimuthVariogramAnglesFmuUpdatable,
            dipVariogramAnglesFmuUpdatable,
            powerFmuUpdatable,
        ],
    ]
    useTrend = 0
    relStdDev = 0.05
    relStdDevFmuUpdatable = True
    trendModelObject = Trend3D_linear(
        azimuth_angle=0.0,
        stacking_angle=0.0,
        azimuth_angle_fmu_updatable=True,
        stacking_angle_fmu_updatable=True,
        direction=-1,
    )
    trendModelList = [
        ['GRF1', useTrend, trendModelObject, relStdDev, relStdDevFmuUpdatable]
    ]
    simBoxThickness = 100.0
    prevSeedList = [['GRF1', 92828]]
    debug_level = Debug.VERY_VERBOSE
    apsGaussModel.initialize(
        main_facies_table=mainFaciesTable,
        gauss_model_list=gaussModelList,
        trend_model_list=trendModelList,
        sim_box_thickness=simBoxThickness,
        preview_seed_list=prevSeedList,
        debug_level=debug_level,
    )
    gridAzimuthAngle = 0.0
    projection = 'xy'
    apsGaussModel.calc2DVariogramFrom3DVariogram(gfName, gridAzimuthAngle, projection)
    projection = 'xz'
    apsGaussModel.calc2DVariogramFrom3DVariogram(gfName, gridAzimuthAngle, projection)
    projection = 'yz'
    apsGaussModel.calc2DVariogramFrom3DVariogram(gfName, gridAzimuthAngle, projection)


def test_read_and_write_aps_model(data_directory, output_directory):
    """
    ******  Case: Read APSModel file and write back APSModel file in sorted order for (zone,region) key *****
            Input has format version 1.0 and output has format version 1.1
    """
    apsmodel = APSModel(
        model_file_name=data_directory / 'APS.xml',
        debug_level=Debug.VERBOSE,
        log_setting=Debug.VERY_VERBOSE,
    )
    outfile3 = output_directory / 'testOut3.xml'
    attributes_file = output_directory / 'fmu_attributes.yaml'
    apsmodel.write_model(outfile3, attributes_file)
    reference_file = data_directory / 'APS_sorted.xml'
    check = compare(outfile3, reference_file)
    assert check is True, f'Compare file: {outfile3} and {reference_file}'


def test_read_and_write_aps_model_with_job_settings_version1(
    data_directory, output_directory
):
    """
    ******  Case: Read APSModel file and write back APSModel file with job settings extension
            Input has format version 1.1 and output has format version 1.1
    """
    apsmodel = APSModel(
        model_file_name=data_directory / 'APS_with_job_settings.xml',
        log_setting=Debug.VERY_VERBOSE,
    )
    outfile3 = output_directory / 'testOut3B.xml'
    attributes_file = output_directory / 'fmu_attributes.yaml'
    apsmodel.write_model(outfile3, attributes_file)
    reference_file = data_directory / 'APS_with_job_settings_out.xml'
    check = compare(outfile3, reference_file)
    assert check is True, f'Compare file: {outfile3} and {reference_file}'


def test_read_and_write_aps_model_with_job_settings_version2(
    data_directory, output_directory
):
    """
    ******  Case: Read APSModel file and write back APSModel file with job settings extension
            Input has format version 1.0 and output has format version 1.0
    """
    apsmodel = APSModel(
        model_file_name=data_directory / 'APS.xml',
        debug_level=Debug.VERY_VERBOSE,
        log_setting=Debug.VERBOSE,
        aps_model_version='1.0',
    )
    outfile3 = output_directory / 'testOut3C.xml'
    attributes_file = output_directory / 'fmu_attributes.yaml'
    apsmodel.write_model(outfile3, attributes_file)
    reference_file = data_directory / 'APS_without_job_settings.xml'
    check = compare(outfile3, reference_file)
    assert check is True, f'Compare file: {outfile3} and {reference_file}'


def test_read_and_write_aps_model_with_job_settings_version3(
    data_directory, output_directory
):
    """
    ******  Case: Read APSModel file and write back APSModel file with job settings extension
            Input has format version 1.1 and output has format version 1.0
    """
    apsmodel = APSModel(
        model_file_name=data_directory / 'APS_with_job_settings.xml',
        debug_level=Debug.VERY_VERBOSE,
        log_setting=Debug.VERBOSE,
        aps_model_version='1.0',
    )
    outfile3 = output_directory / 'testOut3D.xml'
    attributes_file = output_directory / 'fmu_attributes.yaml'
    apsmodel.write_model(outfile3, attributes_file)
    reference_file = data_directory / 'APS_without_job_settings2.xml'
    check = compare(outfile3, reference_file)
    assert check is True, f'Compare file: {outfile3} and {reference_file}'


def test_updating_model1(data_directory, output_directory):
    print('***** Case: Update parameters case 1 *****')
    # Test updating of model
    apsmodel = APSModel(
        model_file_name=data_directory / 'APS.xml',
        debug_level=Debug.VERBOSE,
        log_setting=Debug.VERBOSE,
    )
    # Do some updates of the model
    zoneNumber = 1
    zone = apsmodel.getZoneModel(zoneNumber)
    gaussFieldNames = zone.used_gaussian_field_names
    nGaussFields = len(gaussFieldNames)
    variogramTypeList = [
        VariogramType.SPHERICAL,
        VariogramType.EXPONENTIAL,
        VariogramType.GAUSSIAN,
        VariogramType.GENERAL_EXPONENTIAL,
        VariogramType.SPHERICAL,
    ]
    mainRangeList = [1234.0, 5432.0, 1200.0, 1300.0, 2150.0]
    perpRangeList = [123.0, 543.0, 120.0, 130.0, 215.0]
    vertRangeList = [1.0, 5.0, 1.2, 1.3, 2.15]
    azimuthAngleList = [0.0, 90.0, 125.0, 40.0, 50.0]
    dipAngleList = [0.0, 0.01, 0.005, 0.009, 0.0008]
    powerList = [1.0, 1.2, 1.3, 1.4, 1.5]
    mainRangeFmuUpdatableList = [True, False, True, False, True]
    perpRangeFmuUpdatableList = [True, False, True, False, True]
    vertRangeFmuUpdatableList = [True, False, True, False, True]
    azimuthAngleFmuUpdatableList = [True, False, True, False, True]
    dipAngleFmuUpdatableList = [True, False, True, False, True]
    powerFmuUpdatableList = [True, False, True, True, True]
    gridLayputs = ['BaseConform', None, 'BaseConform', 'BaseConform', 'BaseConform']
    for i in range(nGaussFields):
        gfName = gaussFieldNames[i]
        print('Update zone ' + str(zoneNumber) + ' and gauss field ' + gfName)

        variogramType = variogramTypeList[i]
        assertPropertyGetterSetter(gfName, variogramType, zone, 'VariogramType')

        mainRange = mainRangeList[i]
        assertPropertyGetterSetter(gfName, mainRange, zone, 'MainRange')

        mainRangeFmuUpdatable = mainRangeFmuUpdatableList[i]
        assertPropertyGetterSetter(
            gfName, mainRangeFmuUpdatable, zone, 'MainRangeFmuUpdatable'
        )

        perpRange = perpRangeList[i]
        assertPropertyGetterSetter(gfName, perpRange, zone, 'PerpRange')

        perpRangeFmuUpdatable = perpRangeFmuUpdatableList[i]
        assertPropertyGetterSetter(
            gfName, perpRangeFmuUpdatable, zone, 'PerpRangeFmuUpdatable'
        )

        vertRange = vertRangeList[i]
        assertPropertyGetterSetter(gfName, vertRange, zone, 'VertRange')

        vertRangeFmuUpdatable = vertRangeFmuUpdatableList[i]
        assertPropertyGetterSetter(
            gfName, vertRangeFmuUpdatable, zone, 'VertRangeFmuUpdatable'
        )

        azimuth = azimuthAngleList[i]
        assertPropertyGetterSetter(gfName, azimuth, zone, 'AzimuthAngle')

        azimuthAngleFmuUpdatable = azimuthAngleFmuUpdatableList[i]
        assertPropertyGetterSetter(
            gfName, azimuthAngleFmuUpdatable, zone, 'AzimuthAngleFmuUpdatable'
        )

        dip = dipAngleList[i]
        assertPropertyGetterSetter(gfName, dip, zone, 'DipAngle')

        dipAngleFmuUpdatable = dipAngleFmuUpdatableList[i]
        assertPropertyGetterSetter(
            gfName, dipAngleFmuUpdatable, zone, 'DipAngleFmuUpdatable'
        )

        if variogramType == VariogramType.GENERAL_EXPONENTIAL:
            power = powerList[i]
            assertPropertyGetterSetter(gfName, power, zone, 'Power')

            powerFmuUpdatable = powerFmuUpdatableList[i]
            assertPropertyGetterSetter(
                gfName, powerFmuUpdatable, zone, 'PowerFmuUpdatable'
            )

    outfile2 = output_directory / 'testOut1_updated.xml'
    attributes_file = output_directory / 'fmu_attributes.yaml'
    apsmodel.write_model(outfile2, attributes_file, debug_level=Debug.OFF)
    reference_file = data_directory / 'APS_updated1.xml'
    print(f'Compare file: {outfile2} and {reference_file}')
    check = compare(outfile2, reference_file)
    assert check is True


def test_updating_model2(data_directory, output_directory):
    print('***** Case: Update parameters case 2 *****')
    # Test updating of model
    apsmodel = APSModel(
        model_file_name=data_directory / 'APS.xml',
        debug_level=Debug.VERBOSE,
        log_setting=Debug.VERBOSE,
    )
    # Do some updates of the model
    zoneNumber = 2
    regionNumber = 4
    zone = apsmodel.getZoneModel(zoneNumber, regionNumber)
    gaussFieldNames = zone.used_gaussian_field_names
    nGaussFields = len(gaussFieldNames)
    variogramTypeList = [
        VariogramType.SPHERICAL,
        VariogramType.EXPONENTIAL,
        VariogramType.GAUSSIAN,
        VariogramType.GENERAL_EXPONENTIAL,
        VariogramType.SPHERICAL,
    ]
    mainRangeList = [2099.0, 3210.0, 1204.0, 1308.0, 1090.0]
    perpRangeList = [123.0, 543.0, 120.0, 130.0, 215.0]
    vertRangeList = [1.0, 5.0, 1.2, 1.3, 2.15]
    azimuthAngleList = [0.0, 90.0, 125.0, 40.0, 50.0]
    dipAngleList = [0.0, 0.01, 0.005, 0.009, 0.0008]
    powerList = [1.0, 1.2, 1.3, 1.4, 1.5]
    for i in range(nGaussFields):
        gfName = gaussFieldNames[i]
        if regionNumber > 0:
            print(
                f'Update (zone, region): ({zoneNumber}, {regionNumber})  Gauss field: {gfName}'
            )
        else:
            print(f'Update zone: {zoneNumber} Gauss field: {gfName}')

        variogramType = variogramTypeList[i]
        assertPropertyGetterSetter(gfName, variogramType, zone, 'VariogramType')

        mainRange = mainRangeList[i]
        assertPropertyGetterSetter(gfName, mainRange, zone, 'MainRange')

        perpRange = perpRangeList[i]
        assertPropertyGetterSetter(gfName, perpRange, zone, 'PerpRange')

        vertRange = vertRangeList[i]
        assertPropertyGetterSetter(gfName, vertRange, zone, 'VertRange')

        azimuth = azimuthAngleList[i]
        assertPropertyGetterSetter(gfName, azimuth, zone, 'AzimuthAngle')

        dip = dipAngleList[i]
        assertPropertyGetterSetter(gfName, dip, zone, 'DipAngle')

        if variogramType == VariogramType.GENERAL_EXPONENTIAL:
            power = powerList[i]
            assertPropertyGetterSetter(gfName, power, zone, 'Power')
    outfile2 = output_directory / 'testOut2_updated.xml'
    attributes_file = output_directory / 'fmu_attributes.yaml'
    apsmodel.write_model(outfile2, attributes_file, debug_level=Debug.OFF)
    reference_file = data_directory / 'APS_updated2.xml'
    print(f'Compare file: {outfile2} and {reference_file}')
    check = compare(outfile2, reference_file)
    assert check is True


def test_updating_model3(data_directory, output_directory):
    print('***** Case: Update parameters case 3 *****')
    # Test updating of model
    apsmodel = APSModel(
        model_file_name=data_directory / 'APS.xml',
        debug_level=Debug.ON,
        log_setting=Debug.ON,
    )
    # Do some updates of the model
    zoneNumber = 2
    regionNumber = 3
    zone = apsmodel.getZoneModel(zoneNumber, regionNumber)
    gaussFieldNames = zone.used_gaussian_field_names
    nGaussFields = len(gaussFieldNames)
    variogramTypeList = [
        VariogramType.SPHERICAL,
        VariogramType.EXPONENTIAL,
        VariogramType.GAUSSIAN,
        VariogramType.GENERAL_EXPONENTIAL,
        VariogramType.SPHERICAL,
    ]
    mainRangeList = [2099.0, 3210.0, 1204.0, 1308.0]
    perpRangeList = [123.0, 543.0, 120.0, 130.0]
    vertRangeList = [1.0, 5.0, 1.2, 1.3]
    azimuthAngleList = [0.0, 90.0, 125.0, 40.0]
    dipAngleList = [0.0, 0.01, 0.005, 0.009]
    powerList = [1.0, 1.2, 1.3, 1.4]

    useTrend = [1, 1, 1, 1, 0]
    relStdDev = [0.01, 0.02, 0.02, 0.03, 0.04]
    trend_azimuthAngle = [10.0, 25.0, 35.0, 45.0, 55.0]
    trend_stackingAngle = [89.9, 0.0, 89.5, 0.0, 0.0]
    trend_direction = [1, 1, 1, -1, 1]
    trendType = [
        TrendType.LINEAR,
        TrendType.ELLIPTIC,
        TrendType.HYPERBOLIC,
        TrendType.RMS_PARAM,
        TrendType.NONE,
    ]
    trend_curvature = [2.0, 1.0, 2.5, 0.0, 0.0]
    trend_migrationAngle = [0.0, 0.0, 89.0, 0.0, 0.0]
    trend_origin_x = [0.0, 0.5, 0.5, 0.7, 0.0]
    trend_origin_y = [0.0, 0.0, 0.0, 1.0, 0.0]
    trend_origin_z_simbox = [0.0, 1.0, 0.5, 0.5, 0.0]
    trend_origin_type = [
        OriginType.RELATIVE,
        OriginType.RELATIVE,
        OriginType.RELATIVE,
        OriginType.RELATIVE,
        OriginType.RELATIVE,
    ]
    trend_rms_param_name = ['', '', '', 'New_trend_param', '']
    for i in range(nGaussFields):
        gfName = gaussFieldNames[i]
        if regionNumber > 0:
            print(
                'Update (zone,region):  ({},{})  Gauss field: {}'.format(
                    str(zoneNumber), str(regionNumber), gfName
                )
            )
        else:
            print('Update zone:  {}  Gauss field: {}'.format(str(zoneNumber), gfName))

        variogramType = variogramTypeList[i]
        assertPropertyGetterSetter(gfName, variogramType, zone, 'VariogramType')

        mainRange = mainRangeList[i]
        assertPropertyGetterSetter(gfName, mainRange, zone, 'MainRange')

        perpRange = perpRangeList[i]
        assertPropertyGetterSetter(gfName, perpRange, zone, 'PerpRange')

        vertRange = vertRangeList[i]
        assertPropertyGetterSetter(gfName, vertRange, zone, 'VertRange')

        azimuth = azimuthAngleList[i]
        assertPropertyGetterSetter(gfName, azimuth, zone, 'AzimuthAngle')

        dip = dipAngleList[i]
        assertPropertyGetterSetter(gfName, dip, zone, 'DipAngle')

        if variogramType == VariogramType.GENERAL_EXPONENTIAL:
            power = powerList[i]
            assertPropertyGetterSetter(gfName, power, zone, 'Power')

        if useTrend[i]:
            trendModelObj = zone.getTrendModelObject(gfName)
            if trendType[i] != TrendType.RMS_PARAM:
                trendAzimuth = trend_azimuthAngle[i]
                getSetTrendParameters(trendAzimuth, trendModelObj, 'azimuth')

                trendStackingAngle = trend_stackingAngle[i]
                getSetTrendParameters(
                    trendStackingAngle, trendModelObj, 'stacking_angle'
                )

                trendStackingDirection = trend_direction[i]
                getSetTrendParameters(
                    trendStackingDirection, trendModelObj, 'stacking_direction'
                )

            if trendType[i] == TrendType.ELLIPTIC:
                trendCurvature = trend_curvature[i]
                getSetTrendParameters(trendCurvature, trendModelObj, 'curvature')

                trendOrigin = [
                    trend_origin_x[i],
                    trend_origin_y[i],
                    trend_origin_z_simbox[i],
                ]
                getSetTrendParameters(trendOrigin, trendModelObj, 'origin')

                trendOriginType = trend_origin_type[i]
                getSetTrendParameters(trendOriginType, trendModelObj, 'origin_type')
            elif trendType[i] == TrendType.HYPERBOLIC:
                trendCurvature = trend_curvature[i]
                getSetTrendParameters(trendCurvature, trendModelObj, 'curvature')

                trendMigration = trend_migrationAngle[i]
                getSetTrendParameters(trendMigration, trendModelObj, 'migration_angle')

                trendOrigin = [
                    trend_origin_x[i],
                    trend_origin_y[i],
                    trend_origin_z_simbox[i],
                ]
                getSetTrendParameters(trendOrigin, trendModelObj, 'origin')

                trendOriginType = trend_origin_type[i]
                getSetTrendParameters(trendOriginType, trendModelObj, 'origin_type')

            elif trendType[i] == TrendType.RMS_PARAM:
                trendParamName = trend_rms_param_name[i]
                getSetTrendParameters(
                    trendParamName, trendModelObj, 'trend_parameter_name'
                )

    outfile3 = output_directory / 'testOut3_updated.xml'
    attributes_file = output_directory / 'fmu_attributes.yaml'
    apsmodel.write_model(outfile3, attributes_file, debug_level=Debug.OFF)
    reference_file = data_directory / 'APS_updated3.xml'
    print(f'Compare file: {outfile3} and {reference_file}')
    check = compare(outfile3, reference_file)
    assert check is True


def assertPropertyGetterSetter(
    gaussian_field_name: str, value: object, zone: APSZoneModel, base_name: str
):
    getter = zone.__getattribute__('get' + base_name)
    setter = zone.__getattribute__('set' + base_name)

    # TODO: Add an assert!
    original = getter(gaussian_field_name)
    setter(gaussian_field_name, value)
    new = getter(gaussian_field_name)
    print(base_name + ' ' + str(original) + ' -> ' + str(new))


def getSetTrendParameters(value, trend, _property):
    original = getattr(trend, _property)
    setattr(trend, _property, value)
    new = getattr(trend, _property)
    assert value == new
    print(_property + ' ' + str(original) + ' -> ' + str(new))


def get_apsmodel_with_no_fmu_markers():
    fTable = {2: 'F2', 1: 'F1', 3: 'F3', 4: 'F4', 5: 'F5'}
    apsmodel = APSModel()
    defineCommonModelParam(
        apsmodel=apsmodel,
        rmsProject=RMS_PROJECT,
        rmsWorkflow=RMS_WORKFLOW,
        gridModelName=GRID_MODEL_NAME,
        zoneParamName=ZONE_PARAM_NAME,
        regionParamName=REGION_PARAM_NAME,
        faciesRealParamNameResult=FACIES_REAL_PARAM_NAME_RESULT,
        seedFileName=SEED_FILE_NAME,
        fTable=fTable,
        fTable_blockedWell='BW',
        fTable_blockedWellLog='facies',
        debug_level=Debug.VERY_VERBOSE,
    )
    # Only one zone
    print('Zone: 1')
    add_angle_zone_with_no_fmu_markers(apsmodel)
    add_bayfill_zone_with_no_fmu_markers(apsmodel)
    selectedZoneNumber = 1
    selectedRegionNumber = 0
    apsmodel.setSelectedZoneAndRegionNumber(selectedZoneNumber, selectedRegionNumber)
    apsmodel.setPreviewZoneAndRegionNumber(selectedZoneNumber, selectedRegionNumber)
    return apsmodel


def get_apsmodel_with_all_fmu_markers():
    fTable = {2: 'F2', 1: 'F1', 3: 'F3', 4: 'F4', 5: 'F5'}
    apsmodel = APSModel()
    defineCommonModelParam(
        apsmodel=apsmodel,
        rmsProject=RMS_PROJECT,
        rmsWorkflow=RMS_WORKFLOW,
        gridModelName=GRID_MODEL_NAME,
        zoneParamName=ZONE_PARAM_NAME,
        regionParamName=REGION_PARAM_NAME,
        faciesRealParamNameResult=FACIES_REAL_PARAM_NAME_RESULT,
        seedFileName=SEED_FILE_NAME,
        fTable=fTable,
        fTable_blockedWell='BW',
        fTable_blockedWellLog='facies',
        debug_level=Debug.VERY_VERBOSE,
    )
    # Only one zone
    print('Zone: 1')
    add_angle_zone_with_all_fmu_markers(apsmodel)
    add_bayfill_zone_with_all_fmu_markers(apsmodel)
    selectedZoneNumber = 1
    selectedRegionNumber = 0
    apsmodel.setSelectedZoneAndRegionNumber(selectedZoneNumber, selectedRegionNumber)
    apsmodel.setPreviewZoneAndRegionNumber(selectedZoneNumber, selectedRegionNumber)
    return apsmodel


def create_apsmodel_with_and_without_regions_and_regionparam(
    include_region_number, add_region_param_name
):
    print('Common parameters')
    fTable = {2: 'F2', 1: 'F1', 3: 'F3'}
    apsmodel = APSModel()
    kwagrs = dict(
        apsmodel=apsmodel,
        rmsProject=RMS_PROJECT,
        rmsWorkflow=RMS_WORKFLOW,
        gridModelName=GRID_MODEL_NAME,
        zoneParamName=ZONE_PARAM_NAME,
        regionParamName=None,
        faciesRealParamNameResult=FACIES_REAL_PARAM_NAME_RESULT,
        seedFileName=SEED_FILE_NAME,
        fTable=fTable,
        fTable_blockedWell='BW',
        fTable_blockedWellLog='facies',
        debug_level=Debug.VERY_VERBOSE,
    )
    if add_region_param_name:
        kwagrs['regionParamName'] = REGION_PARAM_NAME
    defineCommonModelParam(**kwagrs)
    if include_region_number:
        add_zone_with_region_number(apsmodel)
    else:
        add_zone_without_region_number(apsmodel)
    return apsmodel


def add_zone_with_region_number(apsmodel):
    addZoneParam(
        apsmodel=apsmodel,
        zoneNumber=1,
        regionNumber=1,
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
        range1FmuUpdatable=[False, False],
        range2FmuUpdatable=[False, False],
        range3FmuUpdatable=[False, False],
        azimuthVariogramAnglesFmuUpdatable=[False, False],
        dipVariogramAnglesFmuUpdatable=[False, False],
        powerFmuUpdatable=[False, False],
        # Trend parameters. One entry in list for each gauss field
        useTrend=[1, 0],
        relStdDev=[0.05, 0.0],
        relStdDevFmuUpdatable=[True, True],
        azimuthAngle=[125.0, 0.0],
        stackingAngle=[0.1, 0.0],
        azimuthAngleFmuUpdatable=[True, True],
        stackingAngleFmuUpdatable=[True, True],
        direction=[1, 1],
        trendType=[TrendType.LINEAR, TrendType.LINEAR],
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
        grid_layouts=['TopConform', 'TopConform'],
        debug_level=NO_VERBOSE_DEBUG,
    )


def add_zone_without_region_number(apsmodel):
    addZoneParam(
        apsmodel=apsmodel,
        zoneNumber=1,
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
        range1FmuUpdatable=[False, False],
        range2FmuUpdatable=[False, False],
        range3FmuUpdatable=[False, False],
        azimuthVariogramAnglesFmuUpdatable=[False, False],
        dipVariogramAnglesFmuUpdatable=[False, False],
        powerFmuUpdatable=[False, False],
        # Trend parameters. One entry in list for each gauss field
        useTrend=[1, 0],
        relStdDev=[0.05, 0.0],
        relStdDevFmuUpdatable=[True, True],
        azimuthAngle=[125.0, 0.0],
        stackingAngle=[0.1, 0.0],
        azimuthAngleFmuUpdatable=[True, True],
        stackingAngleFmuUpdatable=[True, True],
        direction=[1, 1],
        trendType=[TrendType.LINEAR, TrendType.LINEAR],
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
        grid_layouts=['TopConform', 'TopConform'],
        debug_level=NO_VERBOSE_DEBUG,
    )


def add_angle_zone_with_no_fmu_markers(apsmodel):
    addZoneParam(
        apsmodel=apsmodel,
        zoneNumber=1,
        regionNumber=0,
        simBoxThickness=4.0,
        # Facies prob for zone
        faciesInZone=['F1', 'F3'],
        useConstProb=1,
        faciesProbList=[0.4, 0.6],
        # Gauss field parameters. One entry in list for each gauss field
        gaussFieldsInZone=['GRF1', 'GRF2', 'GRF3', 'GRF4'],
        gfTypes=[
            'GENERAL_EXPONENTIAL',
            'SPHERICAL',
            'GENERAL_EXPONENTIAL',
            'SPHERICAL',
        ],
        range1=[2000.0, 1500.0, 2000.0, 1500.0],
        range1FmuUpdatable=[False, False, False, False],
        range2=[1400.0, 750.0, 1400.0, 750.0],
        range2FmuUpdatable=[False, False, False, False],
        range3=[2.0, 1.0, 2.0, 1.0],
        range3FmuUpdatable=[False, False, False, False],
        azimuthVariogramAngles=[35.0, 125.0, 35.0, 125.0],
        azimuthVariogramAnglesFmuUpdatable=[False, False, False, False],
        dipVariogramAngles=[0.0, 0.1, 0.0, 0.1],
        dipVariogramAnglesFmuUpdatable=[False, False, False, False],
        power=[1.8, 1.0, 1.8, 1.0],
        powerFmuUpdatable=[False, False, False, False],
        # Trend parameters. One entry in list for each gauss field
        useTrend=[1, 1, 1, 1],
        relStdDev=[0.05, 0, 0.05, 0],
        relStdDevFmuUpdatable=[False, False, False, False],
        azimuthAngle=[125.0, 0.0, 125.0, 0.0],
        azimuthAngleFmuUpdatable=[False, False, False, False],
        stackingAngle=[0.1, 0.0, 0.1, 0.0],
        stackingAngleFmuUpdatable=[False, False, False, False],
        direction=[1, 1, 1, 1],
        trendType=[
            TrendType.LINEAR,
            TrendType.ELLIPTIC,
            TrendType.HYPERBOLIC,
            TrendType.ELLIPTIC_CONE,
        ],
        curvature=[1.0, 2.0, 1.5, 2.0],
        curvatureFmuUpdatable=[False, False, False, False],
        migrationAngle=[0, 0, 0, 0],
        migrationAngleFmuUpdatable=[False, False, False, False],
        relativeSize=[0, 1.5, 0, 1],
        relativeSizeFmuUpdatable=[False, False, False, False],
        origin_x=[0.5, 0.5, 0.5, 0.5],
        origin_y=[0.0, 0.0, 0.0, 0.0],
        origin_z_simbox=[1.0, 1.0, 1.0, 1.0],
        originFmuUpdatable=[False, False, False, False],
        origin_type=[
            OriginType.RELATIVE,
            OriginType.RELATIVE,
            OriginType.RELATIVE,
            OriginType.RELATIVE,
        ],
        previewSeed=[9282727, 96785, 9282727, 96785],
        # Truncation rule
        truncType='Angle',
        alphaFieldNameForBackGroundFacies=['GRF3', 'GRF4'],
        truncStructureList=[['F1', 0.0, 1.0, False], ['F3', 45.0, 1.0, False]],
        # overlayGroups=[[[['GRF4', 'F2', 1.0, 0.5]], ['F1', 'F3']]],
        useConstTruncParam=1,
        debug_level=Debug.VERBOSE,
    )


def add_bayfill_zone_with_no_fmu_markers(apsmodel):
    addZoneParam(
        apsmodel=apsmodel,
        zoneNumber=2,
        regionNumber=0,
        simBoxThickness=4.0,
        # Facies prob for zone
        faciesInZone=['F1', 'F2', 'F3', 'F4', 'F5'],  # Må ha 5 facies for Bayfill
        useConstProb=1,
        faciesProbList=[0.4, 0.6, 0.0, 0.0, 0.0],
        # Gauss field parameters. One entry in list for each gauss field
        gaussFieldsInZone=['GRF1', 'GRF2', 'GRF3', 'GRF4'],
        gfTypes=[
            'GENERAL_EXPONENTIAL',
            'SPHERICAL',
            'GENERAL_EXPONENTIAL',
            'SPHERICAL',
        ],
        range1=[2000.0, 1500.0, 2000.0, 1500.0],
        range1FmuUpdatable=[False, False, False, False],
        range2=[1400.0, 750.0, 1400.0, 750.0],
        range2FmuUpdatable=[False, False, False, False],
        range3=[2.0, 1.0, 2.0, 1.0],
        range3FmuUpdatable=[False, False, False, False],
        azimuthVariogramAngles=[35.0, 125.0, 35.0, 125.0],
        azimuthVariogramAnglesFmuUpdatable=[False, False, False, False],
        dipVariogramAngles=[0.0, 0.1, 0.0, 0.1],
        dipVariogramAnglesFmuUpdatable=[False, False, False, False],
        power=[1.8, 1.0, 1.8, 1.0],
        powerFmuUpdatable=[False, False, False, False],
        # Trend parameters. One entry in list for each gauss field
        useTrend=[1, 1, 1, 1],
        relStdDev=[0.05, 0, 0.05, 0],
        relStdDevFmuUpdatable=[False, False, False, False],
        azimuthAngle=[125.0, 0.0, 125.0, 0.0],
        azimuthAngleFmuUpdatable=[False, False, False, False],
        stackingAngle=[0.1, 0.0, 0.1, 0.0],
        stackingAngleFmuUpdatable=[False, False, False, False],
        direction=[1, 1, 1, 1],
        trendType=[
            TrendType.LINEAR,
            TrendType.ELLIPTIC,
            TrendType.HYPERBOLIC,
            TrendType.ELLIPTIC_CONE,
        ],
        curvature=[1.0, 2.0, 1.5, 2.0],
        curvatureFmuUpdatable=[False, False, False, False],
        migrationAngle=[0, 0, 0, 0],
        migrationAngleFmuUpdatable=[False, False, False, False],
        relativeSize=[0, 1.5, 0, 1],
        relativeSizeFmuUpdatable=[False, False, False, False],
        origin_x=[0.5, 0.5, 0.5, 0.5],
        origin_y=[0.0, 0.0, 0.0, 0.0],
        origin_z_simbox=[1.0, 1.0, 1.0, 1.0],
        originFmuUpdatable=[False, False, False, False],
        origin_type=[
            OriginType.RELATIVE,
            OriginType.RELATIVE,
            OriginType.RELATIVE,
            OriginType.RELATIVE,
        ],
        previewSeed=[9282727, 96785, 9282727, 96785],
        # Truncation rule
        truncType='Bayfill',
        alphaFieldNameForBackGroundFacies=['GRF2', 'GRF3', 'GRF4'],
        sf_value=0.65,
        sf_fmu_updatable=False,
        ysf=0.5,
        ysf_fmu_updatable=False,
        sbhd=0.55,
        sbhd_fmu_updatable=False,
        useConstTruncParam=1,
        faciesInTruncRule=['F1', 'F2', 'F3', 'F4', 'F5'],
        debug_level=NO_VERBOSE_DEBUG,
    )


def add_angle_zone_with_all_fmu_markers(apsmodel):
    addZoneParam(
        apsmodel=apsmodel,
        zoneNumber=1,
        regionNumber=0,
        simBoxThickness=4.0,
        # Facies prob for zone
        faciesInZone=['F1', 'F3'],
        useConstProb=1,
        faciesProbList=[0.4, 0.6],
        # Gauss field parameters. One entry in list for each gauss field
        gaussFieldsInZone=['GRF1', 'GRF2', 'GRF3', 'GRF4'],
        gfTypes=[
            'GENERAL_EXPONENTIAL',
            'SPHERICAL',
            'GENERAL_EXPONENTIAL',
            'SPHERICAL',
        ],
        range1=[2000.0, 1500.0, 2000.0, 1500.0],
        range1FmuUpdatable=[True, True, True, True],
        range2=[1400.0, 750.0, 1400.0, 750.0],
        range2FmuUpdatable=[True, True, True, True],
        range3=[2.0, 1.0, 2.0, 1.0],
        range3FmuUpdatable=[True, True, True, True],
        azimuthVariogramAngles=[35.0, 125.0, 35.0, 125.0],
        azimuthVariogramAnglesFmuUpdatable=[True, True, True, True],
        dipVariogramAngles=[0.0, 0.1, 0.0, 0.1],
        dipVariogramAnglesFmuUpdatable=[True, True, True, True],
        power=[1.8, 1.0, 1.8, 1.0],
        powerFmuUpdatable=[True, True, True, True],
        # Trend parameters. One entry in list for each gauss field
        useTrend=[1, 1, 1, 1],
        relStdDev=[0.05, 0, 0.05, 0],
        relStdDevFmuUpdatable=[True, True, True, True],
        azimuthAngle=[125.0, 0.0, 125.0, 0.0],
        azimuthAngleFmuUpdatable=[True, True, True, True],
        stackingAngle=[0.1, 0.0, 0.1, 0.0],
        stackingAngleFmuUpdatable=[True, True, True, True],
        direction=[1, 1, 1, 1],
        trendType=[
            TrendType.LINEAR,
            TrendType.ELLIPTIC,
            TrendType.HYPERBOLIC,
            TrendType.ELLIPTIC_CONE,
        ],
        curvature=[1.0, 2.0, 1.5, 2.0],
        curvatureFmuUpdatable=[True, True, True, True],
        migrationAngle=[0, 0, 0, 0],
        migrationAngleFmuUpdatable=[True, True, True, True],
        relativeSize=[0, 1.5, 0, 1],
        relativeSizeFmuUpdatable=[True, True, True, True],
        origin_x=[0.5, 0.5, 0.5, 0.5],
        origin_y=[0.0, 0.0, 0.0, 0.0],
        origin_z_simbox=[1.0, 1.0, 1.0, 1.0],
        originFmuUpdatable=[True, True, True, True],
        origin_type=[
            OriginType.RELATIVE,
            OriginType.RELATIVE,
            OriginType.RELATIVE,
            OriginType.RELATIVE,
        ],
        previewSeed=[9282727, 96785, 9282727, 96785],
        # Truncation rule
        truncType='Angle',
        alphaFieldNameForBackGroundFacies=['GRF3', 'GRF4'],
        truncStructureList=[['F1', 0.0, 1.0, True], ['F3', 45.0, 1.0, True]],
        # overlayGroups=[[[['GRF4', 'F2', 1.0, 0.5]], ['F1', 'F3']]],
        useConstTruncParam=1,
        debug_level=Debug.VERBOSE,
    )


def add_bayfill_zone_with_all_fmu_markers(apsmodel):
    addZoneParam(
        apsmodel=apsmodel,
        zoneNumber=2,
        regionNumber=0,
        simBoxThickness=4.0,
        # Facies prob for zone
        faciesInZone=['F1', 'F2', 'F3', 'F4', 'F5'],  # Må ha 5 facies for Bayfill
        useConstProb=1,
        faciesProbList=[0.4, 0.6, 0.0, 0.0, 0.0],
        # Gauss field parameters. One entry in list for each gauss field
        gaussFieldsInZone=['GRF1', 'GRF2', 'GRF3', 'GRF4'],
        gfTypes=[
            'GENERAL_EXPONENTIAL',
            'SPHERICAL',
            'GENERAL_EXPONENTIAL',
            'SPHERICAL',
        ],
        range1=[2000.0, 1500.0, 2000.0, 1500.0],
        range1FmuUpdatable=[True, True, True, True],
        range2=[1400.0, 750.0, 1400.0, 750.0],
        range2FmuUpdatable=[True, True, True, True],
        range3=[2.0, 1.0, 2.0, 1.0],
        range3FmuUpdatable=[True, True, True, True],
        azimuthVariogramAngles=[35.0, 125.0, 35.0, 125.0],
        azimuthVariogramAnglesFmuUpdatable=[True, True, True, True],
        dipVariogramAngles=[0.0, 0.1, 0.0, 0.1],
        dipVariogramAnglesFmuUpdatable=[True, True, True, True],
        power=[1.8, 1.0, 1.8, 1.0],
        powerFmuUpdatable=[True, True, True, True],
        # Trend parameters. One entry in list for each gauss field
        useTrend=[1, 1, 1, 1],
        relStdDev=[0.05, 0, 0.05, 0],
        relStdDevFmuUpdatable=[True, True, True, True],
        azimuthAngle=[125.0, 0.0, 125.0, 0.0],
        azimuthAngleFmuUpdatable=[True, True, True, True],
        stackingAngle=[0.1, 0.0, 0.1, 0.0],
        stackingAngleFmuUpdatable=[True, True, True, True],
        direction=[1, 1, 1, 1],
        trendType=[
            TrendType.LINEAR,
            TrendType.ELLIPTIC,
            TrendType.HYPERBOLIC,
            TrendType.ELLIPTIC_CONE,
        ],
        curvature=[1.0, 2.0, 1.5, 2.0],
        curvatureFmuUpdatable=[True, True, True, True],
        migrationAngle=[0, 0, 0, 0],
        migrationAngleFmuUpdatable=[True, True, True, True],
        relativeSize=[0, 1.5, 0, 1],
        relativeSizeFmuUpdatable=[True, True, True, True],
        origin_x=[0.5, 0.5, 0.5, 0.5],
        origin_y=[0.0, 0.0, 0.0, 0.0],
        origin_z_simbox=[1.0, 1.0, 1.0, 1.0],
        originFmuUpdatable=[True, True, True, True],
        origin_type=[
            OriginType.RELATIVE,
            OriginType.RELATIVE,
            OriginType.RELATIVE,
            OriginType.RELATIVE,
        ],
        previewSeed=[9282727, 96785, 9282727, 96785],
        # Truncation rule
        truncType='Bayfill',
        alphaFieldNameForBackGroundFacies=['GRF2', 'GRF3', 'GRF4'],
        sf_value=0.65,
        sf_fmu_updatable=True,
        ysf=0.5,
        ysf_fmu_updatable=True,
        sbhd=0.55,
        sbhd_fmu_updatable=True,
        useConstTruncParam=1,
        faciesInTruncRule=['F1', 'F2', 'F3', 'F4', 'F5'],
        debug_level=NO_VERBOSE_DEBUG,
    )


if __name__ == '__main__':
    pytest.main([__file__])
