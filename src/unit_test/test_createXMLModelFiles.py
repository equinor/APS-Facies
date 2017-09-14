#!/bin/env python
# Python3  test that the model files can be created correctly.

import numpy as np 
import sys
import copy
import time
import filecmp
import xml.etree.ElementTree as ET
from xml.dom import minidom

import APSModel
import APSMainFaciesTable
import APSZoneModel
import APSFaciesProb
import APSGaussFieldJobs
import APSGaussModel

import Trunc2D_Base_xml
import Trunc2D_Cubic_xml
import Trunc2D_Angle_xml
import Trunc3D_bayfill_xml

import Trend3D_linear_model_xml



def defineCommonModelParam():
   # The input data are global variables


   apsmodel.setRmsProjectName(rmsProject)
   apsmodel.setRmsWorkflowName(rmsWorkflow)
   apsmodel.setGaussFieldScriptName(gaussFieldSimScript)
   apsmodel.setRmsGridModelName(gridModelName)
   apsmodel.setRmsZoneParamName(zoneParamName)
   apsmodel.setRmsResultFaciesParamName(faciesRealParamNameResult)
   apsmodel.setPrintInfo(printInfo)

   # Define gauss field jobs
   gfJobObject = APSGaussFieldJobs.APSGaussFieldJobs()
   gfJobNames = ['GRFJob1','GRFJob2','GRFJob3']
   gfNamesPerJob = [['GRF1','GRF2'],['GRF3','GRF4','GRF5'],['GRF6','GRF7','GRF8','GRF9']]
   gfJobObject.initialize(gfJobNames, gfNamesPerJob,printInfo)
   apsmodel.setGaussFieldJobs(gfJobObject)

   # Define main facies table
   mainFaciesTable = APSMainFaciesTable.APSMainFaciesTable()
   mainFaciesTable.initialize(fTable)
   apsmodel.setMainFaciesTable(mainFaciesTable)

   
def addZoneParam():
   mainFaciesTable = apsmodel.getMainFaciesTable()
   gaussFieldJobs  = apsmodel.getGaussFieldJobs()

   # Define facies probabilities
   faciesProbObj = APSFaciesProb.APSFaciesProb()
   faciesProbObj.initialize(faciesInZone,faciesProbList,mainFaciesTable,useConstProb,zoneNumber,printInfo)

   # Define gauss field models
   gaussModelList = []
   trendModelList = []
   seedPreviewList = []
   for i in range(len(gfNames)):
      gaussModelList.append([gfNames[i], gfTypes[i], range1[i], range2[i], range3[i], angles[i], power[i]])

      # Set Gauss field trend parameters
      trendModelObject = Trend3D_linear_model_xml.Trend3D_linear_model(None,printInfo,None)
      trendModelObject.initialize(asimuthAngle[i],stackingAngle[i],direction[i],printInfo)
      trendModelList.append([gfNames[i],useTrend[i], trendModelObject,relStdDev[i]])

      seedPreviewList.append([gfNames[i],previewSeed[i]])

   gaussModelObj = APSGaussModel.APSGaussModel()
   gaussModelObj.initialize(zoneNumber, mainFaciesTable, gaussFieldJobs,
                            gaussModelList, trendModelList,
                            simBoxThickness, seedPreviewList, printInfo)

   # Define truncation rule model
   
   if truncType == 'Cubic':
      truncRuleObj = Trunc2D_Cubic_xml.Trunc2D_Cubic()
      truncRuleObj.initialize(mainFaciesTable, faciesInZone, truncStructureList,
                              backGroundFaciesGroups, overlayFacies, overlayTruncCenter, printInfo)
   elif truncType == 'Angle':
      truncRuleObj = Trunc2D_Angle_xml.Trunc2D_Angle()
      truncRuleObj.initialize(mainFaciesTable, faciesInZone, truncStructureList,
                              backGroundFaciesGroups, overlayFacies, overlayTruncCenter,
                              useConstTruncParam, printInfo)
      

   # Initialize data for this zone
   apsZoneModel = APSZoneModel.APSZoneModel()
   apsZoneModel.initialize(zoneNumber, useConstProb, simBoxThickness, horizonNameForVarioTrendMap, 
                           faciesProbObj, gaussModelObj, truncRuleObj, printInfo)
   
   # Add zone to APSModel 
   apsmodel.addNewZone(apsZoneModel)


def test_read_write_model():
   outfile1 = 'testOut1.xml'
   apsmodel.writeModel(outfile1,printInfo)

   # Read the xml file into an new APSModel object
   apsmodel2 = APSModel.APSModel(outfile1)
   outfile2 = 'testOut2.xml'
   apsmodel2.writeModel(outfile2,printInfo)
   print('Compare file: ' + outfile1 + ' and ' + outfile2)
   check = filecmp.cmp(outfile1,outfile2)

   if check == True:
      print('Files are equal. OK')
   else:
      print('Files are different. NOT OK')
   assert check == True

   
def test_read_write_model_update():
   # Read the xml file into an new APSModel object
   apsmodel2 = APSModel.APSModel(outfile1)
   outfile2 = 'testOut2.xml'
   apsmodel2.writeModel(outfile2,printInfo)
   print('Compare file: ' + outfile1 + ' and ' + outfile2)
   check = filecmp.cmp(outfile1,outfile2)

   if check == True:
      print('Files are equal. OK')
   else:
      print('Files are different. NOT OK')
   assert check == True


# -------- Main -------
print('Start test_createXMLModelFiles')

#Global variables
rmsProject = 'testNeslen.rms10'
rmsWorkflow = 'Example APS workflow'
gaussFieldSimScript = 'MakeGaussFields.ipl'
gridModelName = 'APS_NESLEN_ODM'
zoneParamName = 'Zone'
faciesRealParamNameResult = 'FaciesReal'
printInfo = 3


start = 1
end   = 2
nCase = 2

for testCase in range(start,end+1):
   print(' ')
   print('**** Case number: ' + str(testCase) + ' ****')

   if testCase == 1:
      # Global facies table, zone facies and facies probabilities 
      fTable = {2:'F2',1:'F1',3:'F3'}
      apsmodel = APSModel.APSModel()
      defineCommonModelParam()
      
      #  --- Zone 1 ---
      zoneNumber = 1
      horizonNameForVarioTrendMap = 'zone_1'
      simBoxThickness = 4.0

      # Facies prob for zone
      faciesInZone = ['F1','F2']
      useConstProb = 1
      faciesProbList = [0.4,0.6]

      # Gauss field parameters. One entry in list for each gauss field
      gfNames = ['GRF1','GRF2']
      gfTypes = ['GENERAL_EXPONENTIAL','SPHERICAL']
      range1  = [2000.0, 1500.0]
      range2  = [1400.0, 750.0]
      range3 =  [ 2.0, 1.0]
      angles =  [35.0, 125.0]
      power  =  [1.8, 1.0] 

      # Trend parameters. One entry in list for each gauss field
      useTrend = [1,0]
      relStdDev = [0.05, 0]
      asimuthAngle =  [125.0,0.0]
      stackingAngle = [0.1,0.0]
      direction = [1,1]

      previewSeed = [9282727,96785]

      # Truncation rule
      truncType ='Cubic'
      truncStructureList = ['V',['F1', 1.0 , 1, 0, 0],['F2', 1.0 , 2, 0, 0]]
      overlayFacies  = []
      backGroundFaciesGroups = []
      overlayTruncCenter = []
      useConstTruncParam = 1

      addZoneParam()

      #  --- Zone 2 ---
      zoneNumber = 2
      horizonNameForVarioTrendMap = 'zone_2'
      simBoxThickness = 12.0

      # Facies prob for zone
      faciesInZone = ['F3','F1','F2']
      useConstProb = 0
      faciesProbList = ['F3_prob','F1_prob','F2_prob']

      # Gauss field parameters. One entry in list for each gauss field
      gfNames = ['GRF3','GRF4','GRF5']
      gfTypes = ['GENERAL_EXPONENTIAL','SPHERICAL','EXPONENTIAL']
      range1  = [2000.0, 1500.0,6000.0]
      range2  = [1400.0, 750.0,250.0]
      range3 =  [ 2.0, 1.0,4.5]
      angles =  [35.0, 125.0,315.0]
      power  =  [1.8, 1.0,1.0] 

      # Trend parameters. One entry in list for each gauss field
      useTrend = [0,1,0]
      relStdDev = [0, 0.05, 0]
      asimuthAngle =  [0.0,125.0,0.0]
      stackingAngle = [0.0,0.1,0.0]
      direction = [1,-1,1]

      previewSeed = [8727,977727,776785]

      # Truncation rule
      truncType ='Angle'
      truncStructureList = [['F1', 0.0 , 1.0],['F3', 45.0 , 1.0]]
      overlayFacies  = ['F2']
      backGroundFaciesGroups = [['F1','F3']]
      overlayTruncCenter = [0.5]
      useConstTruncParam = 1

      addZoneParam()
      selectedZones =[1,2]
      apsmodel.setSelectedZoneNumberList(selectedZones)
      apsmodel.setPreviewZoneNumber(1)
   
      test_read_write_model()
      
   elif testCase == 2:
      # Global facies table, zone facies and facies probabilities 
      fTable = {2:'F2',1:'F1',3:'F3',4:'F4',5:'F5',6:'F6',7:'F7'}
      apsmodel = APSModel.APSModel()
      defineCommonModelParam()
      
      #  --- Zone 1 ---
      zoneNumber = 1
      horizonNameForVarioTrendMap = 'zone_1'
      simBoxThickness = 4.0

      # Facies prob for zone
      faciesInZone = ['F1','F2','F5','F7']
      useConstProb = 1
      faciesProbList = [0.4,0.5,0.03,0.07]

      # Gauss field parameters. One entry in list for each gauss field
      gfNames = ['GRF6','GRF7','GRF8','GRF9']
      gfTypes = ['GENERAL_EXPONENTIAL','SPHERICAL','EXPONENTIAL','GENERAL_EXPONENTIAL']
      range1  = [3000.0, 1500.0, 2500.0, 750.0]
      range2  = [1400.0, 750.0, 800.0, 5200.0]
      range3 =  [ 2.0, 1.0, 4.0, 120.0]
      angles =  [35.0, 125.0,95.0, 323.0]
      power  =  [1.8, 1.0, 1.0, 1.95] 

      # Trend parameters. One entry in list for each gauss field
      useTrend = [1,0,0,0]
      relStdDev = [0.05, 0, 0, 0]
      asimuthAngle =  [125.0, 0.0, 0.0, 0.0]
      stackingAngle = [0.1, 0.0, 0.0, 0.0]
      direction = [1,1,1,1]

      previewSeed = [9282727,96785, 88760019, 8156827]

      # Truncation rule
      truncType ='Cubic'
      truncStructureList = ['H',['F1', 1.0 , 1, 0, 0],['F2', 1.0 , 2, 0, 0]]
      overlayFacies  = ['F5', 'F7']
      backGroundFaciesGroups = [['F1'], ['F2']]
      overlayTruncCenter = [0.0, 0.8]
      useConstTruncParam = 1

      addZoneParam()

      #  --- Zone 2 ---
      zoneNumber = 2
      horizonNameForVarioTrendMap = 'zone_2'
      simBoxThickness = 12.0

      # Facies prob for zone
      faciesInZone = ['F3','F1','F2','F5','F6','F7']
      useConstProb = 0
      faciesProbList = ['F3_prob','F1_prob','F2_prob','F5_prob','F6_prob','F7_prob']

      gfNames = ['GRF6','GRF7','GRF8','GRF9']
      gfTypes = ['GENERAL_EXPONENTIAL','SPHERICAL','EXPONENTIAL','GENERAL_EXPONENTIAL']
      range1  = [2000.0, 2500.0, 1500.0, 1750.0]
      range2  = [1400.0, 750.0, 800.0, 5200.0]
      range3 =  [ 2.0, 1.0, 4.0, 120.0]
      angles =  [135.0, 25.0,75.0, 23.0]
      power  =  [1.8, 1.0, 1.0, 1.95] 

      # Trend parameters. One entry in list for each gauss field
      useTrend = [1, 0, 1, 0]
      relStdDev = [0.05, 0, 0.03, 0]
      asimuthAngle =  [125.0, 0.0, 90.0, 0.0]
      stackingAngle = [0.1, 0.0, 0.01, 0.0]
      direction = [1,1,-1,1]

      previewSeed = [9282727,96785, 88760019, 8156827]

      # Truncation rule
      truncType ='Angle'
      truncStructureList = [['F1', 0.0 , 1.0],['F3', 45.0 , 1.0],['F2', -35.0 , 1.0],['F5', 145.0 , 1.0]]
      overlayFacies  = ['F6','F7']
      backGroundFaciesGroups = [['F1','F3'],['F2','F5']]
      overlayTruncCenter = [0.5,0.7]
      useConstTruncParam = 1

      addZoneParam()
      selectedZones =[1,2]
      apsmodel.setSelectedZoneNumberList(selectedZones)
      apsmodel.setPreviewZoneNumber(1)
   
      test_read_write_model()


# Test updating of model
modelFile = 'testData_models/APS.xml'
apsmodel = APSModel.APSModel(modelFile)
# Do some updates of the model

zoneNumber = 1
zone1 = apsmodel.getZoneModel(zoneNumber)   

gaussFieldNames = zone1.getUsedGaussFieldNames()
nGaussFields = len(gaussFieldNames)
varioTypeList = ['SPHERICAL','EXPONENTIAL','GAUSSIAN','GENERAL_EXPONENTIAL','SPHERICAL']
mainRangeList = [1234.0, 5432.0,1200,1300,2150]
perpRangeList = [123.0, 543.0,120,130,215]
vertRangeList = [1.0, 5.0,1.2,1.3,2.15]
angleList = [0.0,90.0,125.0,40.0,50.0]
powerList = [1.0, 1.2,1.3,1.4,1.5]

for i in range(nGaussFields):
   gfName = gaussFieldNames[i]
   print('Update zone ' + str(zoneNumber)+ ' and gauss field ' + gfName)

   varioType = zone1.getVarioType(gfName)
   print('Original varioType: ' + varioType)
   varioType = varioTypeList[i]
   zone1.setVarioType(gfName,varioType)
   varioType1 = zone1.getVarioType(gfName)
   print('New varioType     : ' + varioType1)

   mainRange = zone1.getMainRange(gfName)
   print('Original MainRange: ' + str(mainRange))
   mainRange = mainRangeList[i]
   zone1.setMainRange(gfName,mainRange)
   mainRange1 = zone1.getMainRange(gfName)
   print('New MainRange: ' + str(mainRange1))

   perpRange = zone1.getPerpRange(gfName)
   print('Original PerpRange: ' + str(perpRange))
   perpRange = perpRangeList[i]
   zone1.setPerpRange(gfName,perpRange)
   perpRange1 =  zone1.getPerpRange(gfName)
   print('New PerpRange: ' + str(perpRange1))

   vertRange = zone1.getVertRange(gfName)
   print('Original VertRange: ' + str(vertRange))
   vertRange = vertRangeList[i]
   zone1.setVertRange(gfName,vertRange)
   vertRange1 =  zone1.getVertRange(gfName)
   print('New VertRange: ' + str(vertRange1))

   angle = zone1.getAnisotropyAsimuthAngle(gfName)
   print('Original angle: ' + str(angle))
   angle = angleList[i]
   zone1.setAnisotropyAsimuthAngle(gfName,angle)
   angle1 =  zone1.getAnisotropyAsimuthAngle(gfName)
   print('New angle: ' + str(angle1))
   if varioType =='GENERAL_EXPONENTIAL':
      power = zone1.getPower(gfName)
      print('Original exponent: ' + str(power))
      power = powerList[i]
      zone1.setPower(gfName,power)
      power1 =  zone1.getPower(gfName)
      print('New exponent: ' + str(power1))

outfile2 = 'testOut2_updated.xml'
apsmodel.writeModel(outfile2,printInfo)

reference_file = 'testData_models/APS_updated.xml'
print('Compare file: ' + outfile2 + ' and ' + reference_file)
check = filecmp.cmp(outfile2,reference_file)

if check == True:
   print('Files are equal. OK')
else:
   print('Files are different. NOT OK')
assert check == True


print('Finished')
