#!/bin/env python
# Python3  test preliminary preview 
# import roxar
import sys

import importlib

from src import (
    APSGaussFieldJobs, APSMainFaciesTable, APSModel, APSZoneModel, DefineTruncStructure,
    Trend3D_linear_model_xml, Trunc2D_Angle_Overlay_xml, Trunc2D_Cubic_Overlay_xml, Trunc3D_bayfill_xml
)

from src.utils.constants import Debug

importlib.reload(APSModel)
importlib.reload(APSZoneModel)
importlib.reload(APSMainFaciesTable)
importlib.reload(APSGaussFieldJobs)
importlib.reload(Trunc2D_Cubic_Overlay_xml)
importlib.reload(Trunc2D_Angle_Overlay_xml)
importlib.reload(Trend3D_linear_model_xml)
importlib.reload(DefineTruncStructure)

# -------- Main -------
print('Start testCreateXMLModelFile')
apsmodel = APSModel.APSModel()

apsmodel.setRmsProjectName('testNeslen.rms10')
apsmodel.setRmsWorkflowName('Example APS workflow')
apsmodel.setGaussFieldScriptName('MakeGaussFields.ipl')
apsmodel.setRmsGridModelName('APS_NESLEN_ODM')
apsmodel.setRmsZoneParamName('Zone')
apsmodel.setRmsResultFaciesParamName('FaciesReal')
debug_level = Debug.VERY_VERBOSE
apsmodel.set_debug_level(debug_level)

mainFaciesTable = APSMainFaciesTable.APSMainFaciesTable()
mainFaciesTable.addFacies('F1', 1)
mainFaciesTable.addFacies('F2', 2)
mainFaciesTable.addFacies('F3', 3)
mainFaciesTable.addFacies('F4', 4)
mainFaciesTable.addFacies('F5', 5)
mainFaciesTable.addFacies('F6', 6)
mainFaciesTable.addFacies('F7', 7)
mainFaciesTable.addFacies('F8', 8)
mainFaciesTable.addFacies('F9', 9)
mainFaciesTable.addFacies('F10', 10)
apsmodel.setMainFaciesTable(mainFaciesTable)

defineTruncStructureObject = DefineTruncStructure.DefineTruncStructure()

gfJobObject = APSGaussFieldJobs.APSGaussFieldJobs()
jobName = 'GF_1_2'
gfNames = ['GF1', 'GF2']
gfJobObject.addGaussFieldJob(jobName, gfNames)
jobName = 'GF_3_5'
gfNames = ['GF3', 'GF4', 'GF5']
gfJobObject.addGaussFieldJob(jobName, gfNames)
jobName = 'GF_6_9'
gfNames = ['GF6', 'GF7', 'GF8', 'GF9']
gfJobObject.addGaussFieldJob(jobName, gfNames)
jobName = 'GF_10_14'
gfNames = ['GF10', 'GF11', 'GF12', 'GF13', 'GF14']
gfJobObject.addGaussFieldJob(jobName, gfNames)

apsmodel.setGaussFieldJobs(gfJobObject)

# ------- Zone 1 --------------------------
# Create zoneModel object
zoneObject = APSZoneModel.APSZoneModel()

# Set zone number
zoneObject.setZoneNumber(1)
err = zoneObject.setMainFaciesTable(mainFaciesTable)
if err:
    print('Error in zoneObject.setMainFaciesTable')
    sys.exit()

# Set if probabilities is constant or not
zoneObject.setUseConstProb(1)

# Set zone simbox thickness
err = zoneObject.setSimBoxThickness(4.0)
if err:
    print('Error in zoneObject.setSimBoxThickness')
    sys.exit()

# Set horizon name under which the variogram azimuth trend map is located
hName = 'top_middle_Neslen_1'
zoneObject.setHorizonNameForVarioTrendMap(hName)

# Set facies with associated probabilities for the zone
# faciesList = ['F1','F2','F3','F4','F5','F7']
faciesList = ['F1', 'F2', 'F3', 'F4']
faciesProbList = ['0.30', '0.30', '0.30', '0.10']
# faciesProbList = ['0.20','0.20','0.20','0.15','0.15','0.1']
err = zoneObject.updateFaciesWithProbForZone(faciesList, faciesProbList)
if err:
    print('Error in zoneObject.updateFaciesWithProbForZone')
    sys.exit()

# Set Gauss field with parameters
gfName = 'GF3'
varioType = 'SPHERICAL'
range1 = 5500.0
range2 = 5000.0
range3 = 2.0
angle = 35.0
power = 0

# Set Gauss field trend parameters
trendModelObject = Trend3D_linear_model_xml.Trend3D_linear_model(None, debug_level, None)
azimuthAngle = 125.0
stackingAngle = 0.1
direction = 1
relStdDev = 0.01
trendModelObject.initialize(azimuthAngle, stackingAngle, direction, debug_level)
err = zoneObject.updateGaussFieldParam(gfName, varioType, range1, range2, range3, angle, power,
                                       relStdDev, trendModelObject)
if err:
    print('Error in zoneObject.updateGaussFieldParam')
    sys.exit()

# Set Gauss field preview random seed
seed = 276787
err = zoneObject.setSeedForPreviewSimulation(gfName, seed)
if err:
    print('Error in zoneObject.setSeedForPreviewSimulation')
    sys.exit()

# Set Gauss field with parameters
gfName = 'GF4'
varioType = 'SPHERICAL'
range1 = 5500.0
range2 = 1500.0
range3 = 2.0
angle = 35.0
power = 0.0
err = zoneObject.updateGaussFieldParam(gfName, varioType, range1, range2, range3, angle, power)
if err:
    print('Error in zoneObject.updateGaussFieldParam')
    sys.exit()

# Set Gauss field preview random seed
seed = 75151556
err = zoneObject.setSeedForPreviewSimulation(gfName, seed)
if err:
    print('Error in zoneObject.setSeedForPreviewSimulation')
    sys.exit()

# Set Gauss field with parameters
gfName = 'GF5'
varioType = 'GENERAL_EXPONENTIAL'
range1 = 6000.0
range2 = 1300.0
range3 = 2.0
angle = 125.0
power = 1.8
err = zoneObject.updateGaussFieldParam(gfName, varioType, range1, range2, range3, angle, power)
if err:
    print('Error in zoneObject.updateGaussFieldParam')
    sys.exit()

# Set Gauss field preview random seed
seed = 7772627
err = zoneObject.setSeedForPreviewSimulation(gfName, seed)
if err:
    print('Error in zoneObject.setSeedForPreviewSimulation')
    sys.exit()

truncName = 'C03'
print('Trunc name: ' + truncName)
truncRuleObject = Trunc2D_Cubic_Overlay_xml.Trunc2D_Cubic_Overlay()
backgroundFacies = ['F1', 'F2', 'F3']
overlayFacies = 'F4'
overlayTruncCenter = 0.0
# truncStructure =['H',['F1',1.0,1,0,0],['F4',0.5,2,0,0],['F2',1.0,3,1,0],['F3',1.0,3,2,1],['F4',0.5,3,2,2]]
# faciesInTruncRule = ['F1','F2','F3','F4','F5']
faciesInTruncRule = ['F1', 'F2', 'F3', 'F4']
defineTruncStructureObject = DefineTruncStructure.DefineCubicTruncStructure()
truncStructure = defineTruncStructureObject.getTruncStructure(faciesInTruncRule, truncName)
truncRuleObject.initialize(
    mainFaciesTable, faciesList, truncStructure,
    backgroundFacies, overlayFacies, overlayTruncCenter, debug_level
)

zoneObject.setTruncRule(truncRuleObject)

apsmodel.addNewZone(zoneObject)

# selectedZones = [1]
# apsmodel.setSelectedZoneNumberList(selectedZones)
# apsmodel.setPreviewZoneNumber(1)


# modelNumbers = ['09','10','11','12','13','14','15','16','17','18','19','20','31']
# modelNumbers = ['21','22','23','24','25','26','27','28','29','30']
modelNumbers = ['03']
# modelNumbers = ['03','04','05','06','07','08']
for i in modelNumbers:
    print('i= ' + i)
    truncName = 'C' + i
    print('Trunc name: ' + truncName)
    truncRuleObject = Trunc2D_Cubic_Overlay_xml.Trunc2D_Cubic_Overlay()
    backgroundFacies = ['F1', 'F2', 'F3']
    overlayFacies = 'F4'
    overlayTruncCenter = 0.0
    # truncStructure =['H',['F1',1.0,1,0,0],['F4',0.5,2,0,0],['F2',1.0,3,1,0],['F3',1.0,3,2,1],['F4',0.5,3,2,2]]
    # faciesInTruncRule = ['F2','F3','F1','F4','F5']
    #   faciesInTruncRule = ['F1','F2','F3','F4','F5']
    faciesInTruncRule = ['F1', 'F2', 'F3', 'F4']
    #   defineTruncStructureObject = DefineTruncStructure.DefineCubicTruncStructure()
    truncStructure = defineTruncStructureObject.getTruncStructure(faciesInTruncRule, truncName)
    truncRuleObject.initialize(
        mainFaciesTable, faciesList, truncStructure,
        backgroundFacies, overlayFacies, overlayTruncCenter, debug_level
)
    # Set new truncation rule
    zoneObject.setTruncRule(truncRuleObject)

   # outfile = 'testOut'+'_' + str(i) + '.xml'
   #apsmodel.writeModel(outfile, debug_level)

   # Read the xml file into an new APSModel object
   # apsmodel2 = APSModel.APSModel(outfile)
   # outfile2 = 'testOut2'+'_' + str(i) + '.xml'
   # apsmodel2.writeModel(outfile2, debug_level)


# ------- Zone 2 --------------------------        

# Create zoneModel object
zoneObject = APSZoneModel.APSZoneModel()

# Set zone number
zoneObject.setZoneNumber(2)
err = zoneObject.setMainFaciesTable(mainFaciesTable)
if err:
    print('Error in zoneObject.setMainFaciesTable')
    sys.exit()

# Set if probabilities is constant or not
zoneObject.setUseConstProb(1)

# Set zone simbox thickness
err = zoneObject.setSimBoxThickness(4.0)
if err:
    print('Error in zoneObject.setSimBoxThickness')
    sys.exit()

# Set horizon name under which the variogram azimuth trend map is located
hName = 'top_middle_Neslen_2'
zoneObject.setHorizonNameForVarioTrendMap(hName)

# Set facies with associated probabilities for the zone
faciesList = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8']
faciesProbList = ['0.15', '0.25', '0.1', '0.10', '0.10', '0.1', '0.1', '0.1']
err = zoneObject.updateFaciesWithProbForZone(faciesList, faciesProbList)
if err:
    print('Error in zoneObject.updateFaciesWithProbForZone')
    sys.exit()

# Set Gauss field with parameters
gfName = 'GF1'
varioType = 'EXPONENTIAL'
range1 = 1000.0
range2 = 500.0
range3 = 2.0
angle = 35.0
power = 0

# Set Gauss field trend parameters
trendModelObject = Trend3D_linear_model_xml.Trend3D_linear_model(None, debug_level, None)
azimuthAngle = 125.0
stackingAngle = 0.1
direction = -1
relStdDev = 0.02
trendModelObject.initialize(azimuthAngle, stackingAngle, direction, debug_level)
err = zoneObject.updateGaussFieldParam(gfName, varioType, range1, range2, range3,
                                       angle, power, relStdDev, trendModelObject)
if err:
    print('Error in zoneObject.updateGaussFieldParam')
    sys.exit()

# Set Gauss field preview random seed
seed = 276787
err = zoneObject.setSeedForPreviewSimulation(gfName, seed)
if err:
    print('Error in zoneObject.setSeedForPreviewSimulation')
    sys.exit()

# Set Gauss field with parameters
gfName = 'GF2'
varioType = 'EXPONENTIAL'
range1 = 1000.0
range2 = 1000.0
range3 = 2.0
angle = 35.0
power = 0.0
err = zoneObject.updateGaussFieldParam(gfName, varioType, range1, range2, range3, angle, power)
if err:
    print('Error in zoneObject.updateGaussFieldParam')
    sys.exit()

# Set Gauss field preview random seed
seed = 75151556
err = zoneObject.setSeedForPreviewSimulation(gfName, seed)
if err:
    print('Error in zoneObject.setSeedForPreviewSimulation')
    sys.exit()

# Set Gauss field with parameters
gfName = 'GF3'
varioType = 'GENERAL_EXPONENTIAL'
range1 = 3000.0
range2 = 500.0
range3 = 2.0
angle = 35.0
power = 1.8
err = zoneObject.updateGaussFieldParam(gfName, varioType, range1, range2, range3, angle, power)
if err:
    print('Error in zoneObject.updateGaussFieldParam')
    sys.exit()

# Set Gauss field preview random seed
seed = 7772627
err = zoneObject.setSeedForPreviewSimulation(gfName, seed)
if err:
    print('Error in zoneObject.setSeedForPreviewSimulation')
    sys.exit()

truncRuleObject = Trunc2D_Angle_Overlay_xml.Trunc2D_Angle_Overlay()
backgroundFacies = ['F2']
overlayFacies = 'F4'
overlayTruncCenter = 0.50
useConstTruncParam = 1
truncStructure = [['F2', '0.0', 0.5], ['F1', '90.0', 1.0], ['F3', '45.0', 1.0],
                  ['F6', '-45.0', 0.6], ['F2', '0.0', 0.5], ['F5', '-90.0', 1.0],
                  ['F7', '-180.0', 1.0], ['F8', '-90.0', 1.0], ['F6', '-45.0', 0.4]]
truncRuleObject.initialize(mainFaciesTable, faciesList, truncStructure,
                           backgroundFacies, overlayFacies, overlayTruncCenter,
                           useConstTruncParam, debug_level)

zoneObject.setTruncRule(truncRuleObject)

apsmodel.addNewZone(zoneObject)

useConstTrend = 1
if useConstTrend == 0:
    truncRuleObject.setUseTrendForAngles(useConstTrend)
    err = 0
    err += truncRuleObject.setAngleTrend(0, 'TruncAngle_F2_1')
    err += truncRuleObject.setAngleTrend(1, 'TruncAngle_F1')
    err += truncRuleObject.setAngleTrend(2, 'TruncAngle_F3')
    err += truncRuleObject.setAngleTrend(3, 'TruncAngle_F6_1')
    err += truncRuleObject.setAngleTrend(4, 'TruncAngle_F2_2')
    err += truncRuleObject.setAngleTrend(5, 'TruncAngle_F5')
    err += truncRuleObject.setAngleTrend(6, 'TruncAngle_F7')
    err += truncRuleObject.setAngleTrend(7, 'TruncAngle_F8')
    err += truncRuleObject.setAngleTrend(8, 'TruncAngle_F6_2')
else:
    err = 0
    err += truncRuleObject.setAngle(0, -45.0)
    err += truncRuleObject.setAngle(1, 90.0)
    err += truncRuleObject.setAngle(2, 0.0)
    err += truncRuleObject.setAngle(3, 45.0)
    err += truncRuleObject.setAngle(4, 60.0)
    err += truncRuleObject.setAngle(5, -60.0)
    err += truncRuleObject.setAngle(6, -180.0)
    err += truncRuleObject.setAngle(7, 90.0)
    err += truncRuleObject.setAngle(8, 0.0)
    if err > 0:
        print('Error when setAngle')

# ------- Zone 3 --------------------------

# Create zoneModel object
zoneObject = APSZoneModel.APSZoneModel()

# Set zone number
zoneObject.setZoneNumber(3)
err = zoneObject.setMainFaciesTable(mainFaciesTable)
if err:
    print('Error in zoneObject.setMainFaciesTable')
    sys.exit()

# Set if probabilities is constant or not
zoneObject.setUseConstProb(1)

# Set zone simbox thickness
err = zoneObject.setSimBoxThickness(4.0)
if err:
    print('Error in zoneObject.setSimBoxThickness')
    sys.exit()

# Set horizon name under which the variogram azimuth trend map is located
hName = 'top_middle_Neslen_3'
zoneObject.setHorizonNameForVarioTrendMap(hName)

# Set facies with associated probabilities for the zone
faciesList = ['F1', 'F2', 'F3', 'F4', 'F5']
faciesProbList = ['0.20', '0.20', '0.20', '0.20', '0.20']
err = zoneObject.updateFaciesWithProbForZone(faciesList, faciesProbList)
if err:
    print('Error in zoneObject.updateFaciesWithProbForZone')
    sys.exit()

# Set Gauss field with parameters
gfName = 'GF1'
varioType = 'EXPONENTIAL'
range1 = 1000.0
range2 = 500.0
range3 = 2.0
angle = 35.0
power = 0

# Set Gauss field trend parameters
trendModelObject = Trend3D_linear_model_xml.Trend3D_linear_model(None, debug_level, None)
azimuthAngle = 125.0
stackingAngle = 0.1
direction = -1
relStdDev = 0.02
trendModelObject.initialize(azimuthAngle, stackingAngle, direction, debug_level)
err = zoneObject.updateGaussFieldParam(gfName, varioType, range1, range2, range3,
                                       angle, power, relStdDev, trendModelObject)
if err:
    print('Error in zoneObject.updateGaussFieldParam')
    sys.exit()

# Set Gauss field preview random seed
seed = 276787
err = zoneObject.setSeedForPreviewSimulation(gfName, seed)
if err:
    print('Error in zoneObject.setSeedForPreviewSimulation')
    sys.exit()

# Set Gauss field with parameters
gfName = 'GF2'
varioType = 'EXPONENTIAL'
range1 = 1000.0
range2 = 1000.0
range3 = 2.0
angle = 35.0
power = 0.0
err = zoneObject.updateGaussFieldParam(gfName, varioType, range1, range2, range3, angle, power)
if err:
    print('Error in zoneObject.updateGaussFieldParam')
    sys.exit()

# Set Gauss field preview random seed
seed = 75151556
err = zoneObject.setSeedForPreviewSimulation(gfName, seed)
if err:
    print('Error in zoneObject.setSeedForPreviewSimulation')
    sys.exit()

# Set Gauss field with parameters
gfName = 'GF3'
varioType = 'GENERAL_EXPONENTIAL'
range1 = 3000.0
range2 = 500.0
range3 = 2.0
angle = 35.0
power = 1.8
err = zoneObject.updateGaussFieldParam(gfName, varioType, range1, range2, range3, angle, power)
if err:
    print('Error in zoneObject.updateGaussFieldParam')
    sys.exit()

# Set Gauss field preview random seed
seed = 7772627
err = zoneObject.setSeedForPreviewSimulation(gfName, seed)
if err:
    print('Error in zoneObject.setSeedForPreviewSimulation')
    sys.exit()
probCombination = []
probCombination.append(['0.0', '0.0', '0.0', '1.0', '0.0'])
probCombination.append(['0.0', '0.0', '0.0', '0.0', '1.0'])
probCombination.append(['0.0', '1.0', '0.0', '0.0', '0.0'])
probCombination.append(['0.0', '0.0', '1.0', '0.0', '0.0'])
probCombination.append(['0.40', '0.15', '0.25', '0.15', '0.05'])
probCombination.append(['0.10', '0.30', '0.25', '0.30', '0.05'])
probCombination.append(['0.65', '0.05', '0.20', '0.05', '0.05'])
probCombination.append(['0.10', '0.40', '0.20', '0.25', '0.05'])
probCombination.append(['0.05', '0.05', '0.70', '0.10', '0.10'])
probCombination.append(['0.40', '0.0', '0.40', '0.0', '0.20'])
for i in range(4):
    faciesProbList = probCombination[i]
    err = zoneObject.updateFaciesWithProbForZone(faciesList, faciesProbList)
    if err > 0:
        print('Error: When updating facies with probability')
        sys.exit()
    truncRuleObject = Trunc3D_bayfill_xml.Trunc3D_bayfill()
    useConstTruncParam = 1
    faciesInTruncRule = ['F5', 'F4', 'F3', 'F2', 'F1']
    sf_value = 0.5
    sf_name = 'sf_param'
    ysf = 0.3
    sbhd = 0.6
    truncRuleObject.initialize(mainFaciesTable, faciesList, faciesInTruncRule,
                               sf_value, sf_name, ysf, sbhd,
                               useConstTruncParam, debug_level)

    zoneObject.setTruncRule(truncRuleObject)
    if i == 0:
        apsmodel.addNewZone(zoneObject)

    selectedZones = [1, 2, 3]
    apsmodel.setSelectedZoneNumberList(selectedZones)
    apsmodel.setPreviewZoneNumber(3)
    if i < 10:
        name = 'B0' + str(i)
    else:
        name = 'B' + str(i)
    outfile = 'testOut' + '_' + name + '.xml'
    apsmodel.writeModel(outfile, debug_level)

# Read the xml file into an new APSModel object
# apsmodel2 = APSModel.APSModel(outfile)
# outfile2 = 'testOut2.xml'
# apsmodel2.writeModel(outfile2, debug_level)

print('Finished')
