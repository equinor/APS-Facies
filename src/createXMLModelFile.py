#!/bin/env python
# Python3  test preliminary preview 
# import roxar
import sys

import copy

from src import APSGaussFieldJobs, APSMainFaciesTable, APSModel, APSZoneModel

# import Trunc1D_xml
# import Trunc1D_A2_xml
# import Trunc2D_A_xml
# import Trunc2D_A2_xml
# import Trunc2D_B_xml
# import Trunc2D_B2_xml
# import Trunc2D_C_xml
# import Trunc3D_A_xml
# import importlib
# importlib.reload(APSModel)
# importlib.reload(APSZoneModel)
# importlib.reload(APSMainFaciesTable)
# importlib.reload(APSGaussFieldJobs)
# importlib.reload(Trunc2D_Cubic_Overlay_xml)
# importlib.reload(Trunc2D_Angle_Overlay_xml)
# importlib.reload(Trend3D_linear_model_xml)
# importlib.reload(DefineTruncStructure)

# -------- Main -------
print('Start CreateXMLModelFile')

# truncRuleName = 'A01'
# nFacies = 3
# faciesList = ['F1','F2','F3']
# faciesProbList = [0.5,0.3,0.2]


if len(sys.argv) <= 1:
    print('Usage: createXMPModelFile  <trunc-rule-name> <nFacies> <facies list> <facies prob list>')
    print('The number of names in facies list must be equal to the number of probabilities in facies prob list')
    sys.exit()

truncRuleName = sys.argv[1]
nFacies = int(sys.argv[2])
faciesList = []
faciesProbList = []
for i in range(3, 3 + nFacies):
    fName = copy.copy(sys.argv[i])
    fProb = sys.argv[i + nFacies]
    faciesList.append(fName)
    faciesProbList.append(fProb)
# print(repr(faciesList))
# print(repr(faciesProbList))
apsmodel = APSModel.APSModel()

apsmodel.setRmsProjectName('testNeslen.rms10')
apsmodel.setRmsWorkflowName('Example APS workflow')
apsmodel.setGaussFieldScriptName('MakeGaussFields.ipl')
apsmodel.setRmsGridModelName('APS_NESLEN_ODM')
apsmodel.setRmsZoneParamName('Zone')
apsmodel.setRmsResultFaciesParamName('FaciesReal')
printInfo = 1
apsmodel.setPrintInfo(printInfo)

mainFaciesTable = APSMainFaciesTable.APSMainFaciesTable()
faciesCode = 1
for fName in faciesList:
    mainFaciesTable.addFacies(fName, faciesCode)
    faciesCode += 1
apsmodel.setMainFaciesTable(mainFaciesTable)

defineTrRule = DefineTruncStructure.DefineTruncStructure()
nGF = defineTrRule.getTruncRuleNGaussFields(truncRuleName)

gfJobObject = APSGaussFieldJobs.APSGaussFieldJobs()
if nGF == 2:
    jobName = 'GF_1_2'
    gfNames = ['GF1', 'GF2']
    gfJobObject.addGaussFieldJob(jobName, gfNames)
elif nGF == 3:
    jobName = 'GF_3_5'
    gfNames = ['GF3', 'GF4', 'GF5']
    gfJobObject.addGaussFieldJob(jobName, gfNames)
elif nGF == 4:
    jobName = 'GF_6_9'
    gfNames = ['GF6', 'GF7', 'GF8', 'GF9']
    gfJobObject.addGaussFieldJob(jobName, gfNames)
else:
    print('Error: Number of gauss fields must be from 1 to 4.')
    sys.exit()

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

# Set horizon name under which the variogram asimuth trend map is located
hName = 'top_middle_Neslen_1'
zoneObject.setHorizonNameForVarioTrendMap(hName)

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
trendModelObject = Trend3D_linear_model_xml.Trend3D_linear_model(None, printInfo, None)
asimuthAngle = 125.0
stackingAngle = 0.1
direction = 1
relStdDev = 0.01
trendModelObject.initialize(asimuthAngle, stackingAngle, direction, printInfo)
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

print('Trunc rule name: ' + truncRuleName)
nFaciesInTrRule = defineTrRule.getTruncRuleNFacies(truncRuleName)
if len(faciesList) != nFaciesInTrRule:
    print('Error: Not the same number of facies in truncation rule as the number of facies specified')
    print('       Number of facies specified:     ' + str(len(faciesList)))
    print('       Number of facies in trunc rule: ' + str(nFaciesInTrRule))
    sys.exit()
truncRuleObject = defineTrRule.getTruncRuleObject(mainFaciesTable, faciesList, printInfo, truncRuleName)

# print(repr(truncRuleObject))
zoneObject.setTruncRule(truncRuleObject)
# print(repr(zoneObject))
apsmodel.addNewZone(zoneObject)

selectedZones = [1]
apsmodel.setSelectedZoneNumberList(selectedZones)
apsmodel.setPreviewZoneNumber(1)
apsmodel.setPrintInfo(1)
outfile = 'testOut' + '_' + truncRuleName + '.xml'
apsmodel.writeModel(outfile, printInfo)

# Read the xml file into an new APSModel object
apsmodel2 = APSModel.APSModel(outfile)
outfile2 = 'testOut2.xml'
apsmodel2.writeModel(outfile2, printInfo)

print('Finished')
