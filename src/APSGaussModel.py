#!/bin/env python
import sys
import copy
import numpy as np

from Trend3D_linear_model_xml import Trend3D_linear_model

import xml.etree.ElementTree as ET
from  xml.etree.ElementTree import Element, SubElement, dump
from xmlFunctions import getKeyword, getFloatCommand, getTextCommand, getIntCommand

# Functions to draw 2D gaussian fields with linear trend and transformed to unifor distribution
from simGauss2D import  simGaussFieldAddTrendAndTransform 
#from src.utils.methods import isNumber
from methods import isNumber

class APSGaussModel:
    """
    Description: This class contain model parameter specification of the gaussian fields to be simulated for a zone.
    The class contain both variogram data and trend data. Both functions to read the parameters from and XML tree
    for the model file and functions to create an object from an initialization function exist.
    
    Constructor:
    def __init__(self,ET_Tree_zone=None, mainFaciesTable= None,modelFileName = None,
                 printInfo=0,zoneNumber=0,simBoxThickness=0)
    
    Public functions:
    def initialize(self,inputZoneNumber,mainFaciesTable,gaussModelList,trendModelList,
                   simBoxThickness,previewSeed,printInfo)
    def getZoneNumber(self)
    def getUsedGaussFieldNames(self)
    def getVarioType(self,gaussFieldName)
    def getVarioTypeNumber(self,gaussFieldName)
    def getMainRange(self,gaussFieldName)
    def getPerpRange(self,gaussFieldName)
    def getVertRange(self,gaussFieldName)
    def getAnisotropyAsimuthAngle(self,gaussFieldName)
    def getPower(self,gaussFieldName)
    def getTrendRuleModel(self,gfName)
    def getTrendRuleModelObject(self,gfName)
    def printInfo(self)
    def setZoneNumber(self,zoneNumber)
    def setVarioType(self,gaussFieldName,varioType)
    def setRange1(self,gaussFieldName,range1)
    def setRange2(self,gaussFieldName,range2)
    def setRange3(self,gaussFieldName,range3)
    def setAngle(self,gaussFieldName,angle)
    def setPower(self,gaussFieldName,power)
    def setSeedForPreviewSimulation(self,gfName,seed)
    def updateGaussFieldParam(self,gfName,varioType,range1,range2,range3,angle,power,
                              useTrend=0,relStdDev=0.0,trendRuleModelObj=None)
    def updateGaussFieldVarioParam(self,gfName,varioType,range1,range2,range3,angle,power)
    def removeGaussFieldParam(self,gfName)
    def updateGaussFieldTrendParam(self,gfName,useTrend,trendRuleModelObj,relStdDev)
    def XMLAddElement(self,parent)
    def simGaussFieldWithTrendAndTransform(self,nGaussFields,gridDimNx,gridDimNy,
                                           gridXSize,gridYSize,gridAsimuthAngle)

    Private functions:
    def __setEmpty(self)
    def __interpretXMLTree(ET_Tree_zone)
    def __isVarioTypeOK(self,varioType)
    def __getGFIndex(self,gfName)
    """

    def __setEmpty(self):



        # Dictionary give name to each index in __varioForGFModel list
        # item in list: [name,type,range1,range2,range3,angle,power]
        self.__index_vario = {
            'Name': 0,
            'Type': 1,
            'MainRange': 2,
            'PerpRange': 3,
            'VertRange': 4,
            'Angle': 5,
            'Power': 6
            }
        # Dictionary give name to each index in __trendForGFModel list
        # item in list: [name,useTrend,trendRuleModelObj,relStdDev]
        self.__index_trend = {
            'Name': 0,
            'Use trend': 1,
            'Object': 2,
            'RelStdev': 3
            }
        # Dictionaries of legal value ranges for gauss field parameters
        self.__minValue ={
            'MainRange':0.0,
            'PerpRange':0.0,
            'VertRange':0.0,
            'Angle': 0.0,
            'Power': 1.0
            }
        self.__maxValue ={
            'Angle': 360.0,
            'Power': 2.0
            }

        # Dictionary give number to variogram type
        # NOTE: This table must be consistent with simGauss2D
        self.__varioTypeNumber = {
            'SPHERICAL': 1,
            'EXPONENTIAL': 2,
            'GAUSSIAN': 3,
            'GENERAL_EXPONENTIAL': 4
            }
        # Dictionary give name to each index in __seedForPreviewForGFModel
        # item in list: [name,value]
        self.__index_seed={
            'Name':0,
            'Seed':1
            }

        self.__className = 'APSGaussModel'
        self.__printInfo = 0
        self.__mainFaciesTable = None
        self.__varioForGFModel = []
        self.__trendForGFModel = []
        self.__seedForPreviewForGFModel = []
        self.__simBoxThickness = 0
        self.__zoneNumber = 0
        self.__modelFileName = None


    def __init__(self,ET_Tree_zone=None, mainFaciesTable=None, gaussFieldJobs=None, modelFileName=None,
                 printInfo=0,zoneNumber=0,simBoxThickness=0):
        """
        Decription: Can create empty object or object with data read from xml tree representing the model file.
        """
        self.__setEmpty()
            
        if ET_Tree_zone is not None:
            # Get data from xml tree
            if printInfo >= 3:
                print('Debug output: Call init ' + self.__className + ' and read from xml file')

            assert mainFaciesTable
            assert zoneNumber
            assert simBoxThickness
            assert modelFileName

            self.__mainFaciesTable = mainFaciesTable
            self.__zoneNumber = zoneNumber
            self.__simBoxThickness = simBoxThickness
            self.__modelFileName = modelFileName
            self.__printInfo = printInfo

            self.__interpretXMLTree(ET_Tree_zone, gaussFieldJobs)

    # End __init__


    def __interpretXMLTree(self,ET_Tree_zone, gaussFieldJobs):
        """
        Description: Read Gauss field models for current zone. 
        Read trend models for the same gauss fields and start seed for 2D preview simulations. 
        """
        for gf in ET_Tree_zone.findall('GaussField'):
            gfName   = gf.get('name')
            if not gaussFieldJobs.checkGaussFieldName(gfName):
                raise ValueError(
                    'In model file {0} in zone number: {1} in command GaussField.\n'
                    'Specified name of Gauss field:  {2} is not defined in any of '
                    'the specified gauss field simulation jobs'
                    ''.format(self.__modelFileName,str(self.__zoneNumber),gfName)
                )
            
            # Read variogram for current GF
            vario = getKeyword(gf, 'Vario', 'GaussField', modelFile=self.__modelFileName)
            varioType = vario.get('name')
            if not self.__isVarioTypeOK(varioType):
                raise ValueError(
                    'In model file {0} in zone number: {1} in command Vario.\n'
                    'Specified variogram type: {1} is not defined.'
                    ''.format(self.__modelFileName,gfName)
                    )

            range1 = getFloatCommand(vario, 'MainRange', 'Vario', minValue=0.0,
                                     modelFile=self.__modelFileName)

            range2 = getFloatCommand(vario, 'PerpRange', 'Vario', minValue=0.0,
                                     modelFile=self.__modelFileName)

            range3 = getFloatCommand(vario, 'VertRange', 'Vario', minValue=0.0,
                                     modelFile=self.__modelFileName)

            angle = getFloatCommand(vario, 'Angle', 'Vario', modelFile=self.__modelFileName)

            power = 1.0
            if varioType == 'GENERAL_EXPONENTIAL':
                power = getFloatCommand(vario, 'Power', 'Vario',
                                        minValue = 1.0, maxValue = 2.0, modelFile=self.__modelFileName)
                
            # Read trend model for current GF
            trendObjXML  = gf.find('Trend')
            trendRuleModelObj = None
            if trendObjXML != None:
                if self.__printInfo >= 3:
                    print('Debug output: Read trend')
                useTrend = 1


                if self.__simBoxThickness <= 0.0: 
                    raise ValueError(
                        'In model file {0} in keyword Trend for gauss field name: {1}\n'
                        'The use of trend functions requires that simulation box thickness is specified.\n'
                        ''.format(self.__modelFileName,gfName,self.__className)
                        )
                trendName = trendObjXML.get('name')
                if trendName == 'Linear3D':
                    trendRuleModelObj =  Trend3D_linear_model(trendObjXML,self.__printInfo,self.__modelFileName)
                else:
                    raise NameError(
                        'Error in ' + self.__className + '\n'
                        'Error: Specified name of trend function ' + trendName + ' is not implemented.'
                        )
            else:
                if self.__printInfo >= 3:
                    print('Debug output: No trend is specified')
                useTrend = 0
                trendRuleModelObj = None
                relStdDev = 0
                            
            # Read RelstdDev
            if useTrend == 1:
                relStdDev = getFloatCommand(gf, 'RelStdDev', 'GaussField', 0.0,
                                            modelFile=self.__modelFileName)

            # Read preview seed for current GF
            seed = getIntCommand(gf, 'SeedForPreview', 'GaussField', modelFile=self.__modelFileName)
            item = [gfName,seed]

            # Add gauss field parameters to data structure
            self.updateGaussFieldParam(gfName,varioType,range1,range2,range3,angle,power,
                                       useTrend,relStdDev,trendRuleModelObj)
            # Set preview simulation start seed for gauss field
            self.setSeedForPreviewSimulation(gfName,seed)

        # End loop over gauss fields for current zone model

        if self.__varioForGFModel is None:
            raise NameError(
                'Error when reading model file: ' + self.__modelFileName + '\n'
                'Error: Missing keyword GaussField under keyword Zone'
                )

        if self.__printInfo >= 3:
            print('Debug output: Gauss field variogram parameter for current zone model:')
            print(repr(self.__varioForGFModel))
            
            print('Debug output:Gauss field trend parameter for current zone model:')
            print(repr(self.__trendForGFModel))
            
            print('Debug output: Gauss field preview seed for current zone model:')
            print(repr(self.__seedForPreviewForGFModel))



    def initialize(self,inputZoneNumber,mainFaciesTable,gaussFieldJobs,
                   gaussModelList,trendModelList,
                   simBoxThickness,previewSeedList,printInfo):
                
        if printInfo >= 3:
            print('Debug output: Call the initialize function in ' + self.__className)

        # Set default values
        self.__setEmpty()

        GNAME = self.__index_vario['Name']
        GTYPE = self.__index_vario['Type']
        GRANGE1 = self.__index_vario['MainRange']
        GRANGE2 = self.__index_vario['PerpRange']
        GRANGE3 = self.__index_vario['VertRange']
        GANGLE  = self.__index_vario['Angle']
        GPOWER  = self.__index_vario['Power']

        TNAME = self.__index_trend['Name']
        TUSE  = self.__index_trend['Use trend']
        TOBJ  = self.__index_trend['Object']
        TSTD  = self.__index_trend['RelStdev']

        SNAME = self.__index_seed['Name']
        SVALUE =self.__index_seed['Seed']


        self.__zoneNumber = inputZoneNumber
        self.__printInfo = printInfo
        self.__simBoxThickness = simBoxThickness
        self.__mainFaciesTable = mainFaciesTable
        
        # gaussModelList  = list of objects of the form: [gfName,type,range1,range2,range3,angle,power]
        # trendModelList  = list of objects of the form: [gfName,useTrend,trendRuleModelObj,relStdDev]
        # previewSeedList = list of objects of the form: [gfName,seedValue]
        assert len(trendModelList) == len(gaussModelList)
        for i in range(len(gaussModelList)):
            item = gaussModelList[i]
            trendItem = trendModelList[i]
            seedItem  = previewSeedList[i]
            assert item[GNAME] == trendItem[TNAME]
            assert item[GNAME] == seedItem[SNAME]

            gfName = item[GNAME]
            if not gaussFieldJobs.checkGaussFieldName(gfName):
                raise ValueError(
                    'In model file {0} in zone number: {1} in command GaussField.'
                    'Specified name of Gauss field:  {2} is not defined in any of '
                    'the specified gauss field simulation jobs'
                    ''.format(self.__modelFileName,str(self.__zoneNumber),gfName)
                    )

            varioType = item[GTYPE]
            if not self.__isVarioTypeOK(varioType):
                raise ValueError(
                    'In initialize function for {0} in zone number: {1}. '
                    'Specified variogram type: {2} is not defined.'
                    ''.format(self.__className,self.__zoneNumber,varioType)
                    )
            range1 = item[GRANGE1]
            range2 = item[GRANGE2]
            range3 = item[GRANGE3]
            angle  = item[GANGLE]
            power  = item[GPOWER]

            trendRuleModelObj = trendItem[TOBJ]
            relStdDev = trendItem[TSTD]
            useTrend  = trendItem[TUSE]
            seed = seedItem[SVALUE]

            # Set variogram parameters for this gauss field
            self.updateGaussFieldParam(gfName,varioType,range1,range2,range3,angle,power)

            # Set trend model parameters for this gauss field
            self.updateGaussFieldTrendParam(gfName,useTrend,trendRuleModelObj,relStdDev)

            # Set preview simulation start seed for gauss field
            self.setSeedForPreviewSimulation(gfName,seed)

        
    def getNGaussFields(self):
        return len(self.__varioForGFModel)

    def __isVarioTypeOK(self,varioType):
        isOK = 0
        if varioType == 'SPHERICAL':
            isOK = 1
        elif varioType == 'EXPONENTIAL':
            isOK = 1
        elif varioType == 'GAUSSIAN':
            isOK = 1
        elif varioType == 'GENERAL_EXPONENTIAL':
            isOK = 1
        if isOK == 0:
            print('Error: Specified variogram : ' + varioType + ' is not implemented')
            print('Error: Allowed variograms are: ')
            print('       SPHERICAL')
            print('       EXPONENTIAL')
            print('       GAUSSIAN')
            print('       GENERAL_EXPONENTIAL')
            return False
        return True
            

    def getZoneNumber(self):
        return self.__zoneNumber

    def getUsedGaussFieldNames(self):
        gfNames = []
        GNAME = self.__index_vario['Name']
        nGF     = len(self.__varioForGFModel)
        for i in range(nGF):
            item = self.__varioForGFModel[i]
            name = item[GNAME]
            gfNames.append(name)
        return gfNames

    def findGaussFieldParameterItem(self,gaussFieldName):
        GNAME = self.__index_vario['Name']
        nGF     = len(self.__varioForGFModel)
        found = False
        itemWithParameters = None
        for i in range(nGF):
            item = self.__varioForGFModel[i]
            name = item[GNAME]
            if name == gaussFieldName:
                itemWithParameters = item
                found = True
                break
        if not found:
            raise ValueError('Variogram data for gauss field name: {} is not found.'.format(gaussFieldName))
        return itemWithParameters

    def getVarioType(self,gaussFieldName):
        GTYPE = self.__index_vario['Type']
        item = self.findGaussFieldParameterItem(gaussFieldName)
        varioType = item[GTYPE]
        return varioType

    def getVarioTypeNumber(self,gaussFieldName):
        varioType = self.getVarioType(gaussFieldName)
        varioTypeNumber = self.__varioTypeNumber[varioType]
        return varioTypeNumber


    def getMainRange(self,gaussFieldName):
        GRANGE1 = self.__index_vario['MainRange']
        item = self.findGaussFieldParameterItem(gaussFieldName)
        r = item[GRANGE1]
        return r

    def getPerpRange(self,gaussFieldName):
        GRANGE2 = self.__index_vario['PerpRange']
        item = self.findGaussFieldParameterItem(gaussFieldName)
        r = item[GRANGE2]
        return r

    def getVertRange(self,gaussFieldName):
        GRANGE3 = self.__index_vario['VertRange']
        item = self.findGaussFieldParameterItem(gaussFieldName)
        r = item[GRANGE3]
        return r

    def getAnisotropyAsimuthAngle(self,gaussFieldName):
        GANGLE = self.__index_vario['Angle']
        item = self.findGaussFieldParameterItem(gaussFieldName)
        r = item[GANGLE]
        return r

    def getPower(self,gaussFieldName):
        GPOWER = self.__index_vario['Power']
        item = self.findGaussFieldParameterItem(gaussFieldName)
        r = item[GPOWER]
        return r

    def getTrendRuleItem(self,gfName):
        TNAME = self.__index_trend['Name']
        found = False
        itemForTrendParam = None
        for item in self.__trendForGFModel:
            name = item[TNAME]
            if name == gfName:
                found = True
                itemForTrendParam = item
        if not found:
            return None
        else:
            return itemForTrendParam

    def getTrendRuleModel(self,gfName):
        TUSE  = self.__index_trend['Use trend']
        TOBJ  = self.__index_trend['Object']
        TSTD  = self.__index_trend['RelStdev']
        item  = self.getTrendRuleItem(gfName)
        if item is None:
            return None
        else:
            useTrend = item[TUSE]
            trendModelObj = item[TOBJ]
            relStdDev = item[TSTD]
            return [useTrend,trendModelObj,relStdDev]


    def getTrendRuleModelObject(self,gfName):
        TOBJ  = self.__index_trend['Object']
        item  = self.getTrendRuleItem(gfName)
        if item is None:
            return None
        else:
            trendModelObj = item[TOBJ]
            return trendModelObj

    def printInfo(self):
        return self.__printInfo

    def __getGFIndex(self,gfName):
        GNAME = self.__index_vario['Name']

        indx = -1
        for i in range(len(self.__varioForGFModel)):
            item = self.__varioForGFModel[i]
            gf = item[GNAME]
            if gf== gfName:
                indx = i
                break
        return indx

    def setZoneNumber(self,zoneNumber):
        self.__zoneNumber = zoneNumber
        return

    def setValue(self,gaussFieldName,variableName,value,checkMax=False):
        # Minimum allowed value
        minValue = self.__minValue[variableName]

        # Max allowed value
        if checkMax:
            maxValue = self.__maxValue[variableName]

        # index to where the variable is located in the __varioFORGFModel
        variableIndex = self.__index_vario[variableName]

        err = 0
        if(value < minValue):
            err = 1
        if checkMax:
            if(value > maxValue):
                err = 1
        if err == 0:
            gfList = self.getUsedGaussFieldNames()
            if gaussFieldName  in gfList:
                indx = self.__getGFIndex(gaussFieldName)
                item = self.__varioForGFModel[indx]
                item[variableIndex] = value
            else:
                err = 1
        return err
    
    def setVarioType(self,gaussFieldName,varioType):
        GTYPE = self.__index_vario['Type']
        err = 0
        if  self.__isVarioTypeOK(varioType):
            gfList = self.getUsedGaussFieldNames()
            if gaussFieldName  in gfList:
                indx = self.__getGFIndex(gaussFieldName)
                item = self.__varioForGFModel[indx]
                item[GTYPE] = varioType
            else:
                err = 1
        else:
            err = 1
        return err

    def setMainRange(self,gaussFieldName,range1):
        err = self.setValue(gaussFieldName,'MainRange',range1)
        return err


    def setPerpRange(self,gaussFieldName,range2):
        err = self.setValue(gaussFieldName,'PerpRange',range2)
        return err

    def setVertRange(self,gaussFieldName,range3):
        err = self.setValue(gaussFieldName,'VertRange',range3)
        return err

    def setAnisotropyAsimuthAngle(self,gaussFieldName,angle):
        err = self.setValue(gaussFieldName,'Angle',angle,checkMax=True)
        return err

    def setPower(self,gaussFieldName,power):
        err = self.setValue(gaussFieldName,'Power',power,checkMax=True)
        return err


    def setSeedForPreviewSimulation(self,gfName,seed):
        SNAME = self.__index_seed['Name']
        SVALUE = self.__index_seed['Seed']
        err = 0
        found = 0
        for i in range(len(self.__seedForPreviewForGFModel)):
            item = self.__seedForPreviewForGFModel[i]
            name = item[SNAME]
            if name == gfName:
                found = 1
                item[SVALUE] = seed
                break
        if found == 0:
            err = 1
        return err


    def updateGaussFieldParam(self,gfName,varioType,range1,range2,range3,angle,power,
                              useTrend=0,relStdDev=0.0,trendRuleModelObj=None):
        # Update or create new gauss field parameter object (with trend)
        GNAME = self.__index_vario['Name']
        err = 0
        found = 0
        if  not self.__isVarioTypeOK(varioType):
            print('Error in ' + self.__className + ' in ' + 'updateGaussFieldParam')
            raise ValueError('Undefined variogram type specified.')
            err = 1
        if range1 < 0:
            print('Error in ' + self.__className + ' in ' + 'updateGaussFieldParam')
            raise ValueError('Correlation range < 0.0')
            err = 1
        if range2 < 0:
            print('Error in ' + self.__className + ' in ' + 'updateGaussFieldParam')
            raise ValueError('Correlation range < 0.0')
            err = 1
        if range3 < 0:
            print('Error in ' + self.__className + ' in ' + 'updateGaussFieldParam')
            raise ValueError('Correlation range < 0.0')
            err = 1
        if varioType == 'GENERAL_EXPONENTIAL':
            if power < 1.0 or power > 2.0:
                print('Error in ' + self.__className + ' in ' + 'updateGaussFieldParam')
                raise ValueError('Exponent in GENERAL_EXPONENTIAL variogram is outside [1.0,2.0]')
                err = 1
        if relStdDev < 0.0:
            print('Error in ' + self.__className + ' in ' + 'updateGaussFieldParam')
            raise ValueError('Relative standard deviation used when trends are specified is negative.')
            err = 1

        # Check if gauss field is already defined, then update parameters or create new
        for item in self.__varioForGFModel:
            name = item[GNAME]
            if name == gfName:
                self.updateGaussFieldVarioParam(gfName,varioType,range1,range2,range3,angle,power)
                self.updateGaussFieldTrendParam(gfName,useTrend,trendRuleModelObj,relStdDev)
                found = 1
                break   
        if found == 0:
            # Create data for a new gauss field for both variogram  data and trend data
            # But data for trend parameters must be set by another function and default is set here.
            itemVario = [gfName,varioType,range1,range2,range3,angle,power]
            self.__varioForGFModel.append(itemVario)
            if trendRuleModelObj == None:
                useTrend = 0
                relStdDev = 0.0
            else:
                useTrend = 1
            itemTrend = [gfName,useTrend,trendRuleModelObj,relStdDev]
            self.__trendForGFModel.append(itemTrend)
            defaultSeed = 0
            self.__seedForPreviewForGFModel.append([gfName,defaultSeed])
        return err

    def updateGaussFieldVarioParam(self,gfName,varioType,range1,range2,range3,angle,power):
        # Update gauss field variogram parameters for existing gauss field model
        # But it does not create new object.
        GNAME = self.__index_vario['Name']
        GTYPE = self.__index_vario['Type']
        GRANGE1 = self.__index_vario['MainRange']
        GRANGE2 = self.__index_vario['PerpRange']
        GRANGE3 = self.__index_vario['VertRange']
        GANGLE  = self.__index_vario['Angle']
        GPOWER  = self.__index_vario['Power']

        err = 0
        found = 0
        # Check that gauss field is already defined, then update parameters.
        for item in self.__varioForGFModel:
            name = item[GNAME]
            if name == gfName:
                found = 1
                item[GTYPE]   = varioType
                item[GRANGE1] = range1
                item[GRANGE2] = range2
                item[GRANGE3] = range3
                item[GANGLE]  = angle
                item[GPOWER]  = power
                break   
        if found == 0:
            err = 1
        return err

    def removeGaussFieldParam(self,gfName):
        GNAME = self.__index_vario['Name']
        indx = -1
        for i in range(len(self.__varioForGFModel)):
            item = self.__varioForGFModel[i]
            name = item[GNAME]
            if name == gfName:
                indx = i
                break
        if indx != -1:
            # Remove from list
            self.__varioForGFModel.pop(indx)
            self.__trendForGFModel.pop(indx)
            self.__seedForPreviewForGFModel.pop(indx)
        return

    def updateGaussFieldTrendParam(self,gfName,useTrend,trendRuleModelObj,relStdDev):
        # Update trend parameters for existing trend for gauss field model
        # But it does not create new trend object.
        TNAME = self.__index_trend['Name']
        TUSE  = self.__index_trend['Use trend']
        TOBJ  = self.__index_trend['Object']
        TSTD  = self.__index_trend['RelStdev']
        err = 0
        if trendRuleModelObj == None:
            err = 1
        else:
            # Check if gauss field is already defined, then update parameters
            found = 0
            for item in self.__trendForGFModel:
                name = item[TNAME]
                if name == gfName:
                    found = 1
                    item[TUSE] = useTrend
                    item[TSTD] = relStdDev
                    item[TOBJ] = trendRuleModelObj
                    break   
            if found == 0:
                # This gauss field was not found.
                err = 1
        return err


    def XMLAddElement(self,parent):
        GNAME = self.__index_vario['Name']
        GTYPE = self.__index_vario['Type']
        GRANGE1 = self.__index_vario['MainRange']
        GRANGE2 = self.__index_vario['PerpRange']
        GRANGE3 = self.__index_vario['VertRange']
        GANGLE  = self.__index_vario['Angle']
        GPOWER  = self.__index_vario['Power']

        TNAME = self.__index_trend['Name']
        TUSE  = self.__index_trend['Use trend']
        TOBJ  = self.__index_trend['Object']
        TSTD  = self.__index_trend['RelStdev']

        SNAME = self.__index_seed['Name']
        SVALUE =self.__index_seed['Seed']

        if self.__printInfo >= 3:
            print('Debug output: call XMLADDElement from ' + self.__className)

        # Add child command GaussField
        nGaussFieldsForModel = len(self.__varioForGFModel)
        for i in range(nGaussFieldsForModel):
            gfName     = self.__varioForGFModel[i][GNAME]
            varioType  = self.__varioForGFModel[i][GTYPE]
            range1     = self.__varioForGFModel[i][GRANGE1]
            range2     = self.__varioForGFModel[i][GRANGE2]
            range3     = self.__varioForGFModel[i][GRANGE3]
            angle      = self.__varioForGFModel[i][GANGLE]
            power      = self.__varioForGFModel[i][GPOWER]

            if gfName != self.__trendForGFModel[i][TNAME]:
                print('Error in class: ' + self.__className + ' in ' + 'XMLAddElement')
                sys.exit()
            useTrend   = self.__trendForGFModel[i][TUSE]
            trendObj   = self.__trendForGFModel[i][TOBJ]
            relStdDev  = self.__trendForGFModel[i][TSTD]

            tag = 'GaussField'
            attribute = {'name':gfName}
            elem = Element(tag,attribute)
            parent.append(elem)
            gfElement = elem
            tag = 'Vario'
            attribute = {'name':varioType}
            elem = Element(tag,attribute)
            gfElement.append(elem)
            varioElement = elem
            tag = 'MainRange'
            elem = Element(tag)
            elem.text = ' ' + str(range1) + ' '
            varioElement.append(elem)
            tag = 'PerpRange'
            elem = Element(tag)
            elem.text = ' ' + str(range2) + ' '
            varioElement.append(elem)
            tag = 'VertRange'
            elem = Element(tag)
            elem.text = ' ' + str(range3) + ' '
            varioElement.append(elem)
            tag = 'Angle'
            elem = Element(tag)
            elem.text = ' ' + str(angle) + ' '
            varioElement.append(elem)
            if varioType == 'GENERAL_EXPONENTIAL':
                tag = 'Power'
                elem = Element(tag)
                elem.text = ' ' + str(power) + ' '
                varioElement.append(elem)

            if useTrend == 1:
                # Add trend
                trendObj.XMLAddElement(gfElement)

                tag = 'RelStdDev'
                elem = Element(tag)
                elem.text = ' ' + str(relStdDev) + ' ' 
                gfElement.append(elem)

            tag = 'SeedForPreview'
            elem = Element(tag)
            seedValue = self.__seedForPreviewForGFModel[i][SVALUE]
            elem.text = ' ' + str(seedValue) + ' '
            gfElement.append(elem)



    def simGaussFieldWithTrendAndTransform(self,nGaussFields,gridDimNx,gridDimNy,
                                           gridXSize,gridYSize,gridAsimuthAngle):
        TUSE  = self.__index_trend['Use trend']
        TOBJ  = self.__index_trend['Object']
        TSTD  = self.__index_trend['RelStdev']
        SVALUE =self.__index_seed['Seed']

        nx = gridDimNx
        ny = gridDimNy
        xsize = gridXSize
        ysize = gridYSize
        
        gaussFieldNamesForSimulation = self.getUsedGaussFieldNames()
        assert nGaussFields == len(gaussFieldNamesForSimulation)
        gaussFields = []
        for i in range(nGaussFields):
            # Find data for specified Gauss field name
            name      = gaussFieldNamesForSimulation[i]
            seedValue = self.__seedForPreviewForGFModel[i][SVALUE]
            varioType = self.getVarioType(name)
            varioTypeNumber = self.getVarioTypeNumber(name)
            r1        = self.getMainRange(name)
            r2        = self.getPerpRange(name)
            r3        = self.getVertRange(name)
            angle     = self.getAnisotropyAsimuthAngle(name)
            angle = angle - gridAsimuthAngle

            power     = self.getPower(name)

            useTrend     = self.__trendForGFModel[i][TUSE]
            trendAsimuth = 0.0
            if useTrend == 1:
                trendObj     = self.__trendForGFModel[i][TOBJ]
                trendAsimuth = trendObj.getAsimuth() - gridAsimuthAngle

            relSigma     = self.__trendForGFModel[i][TSTD]
            if self.__printInfo >= 3:
                print('Simulate gauss field: ' + name)
                print('VarioType: ' + str(varioType))
                print('VarioTypeNumber: ' + str(varioTypeNumber))
                print('Range1   : ' + str(r1))
                print('Range2   : ' + str(r2))
                print('Range3   : ' + str(r3))
                if varioTypeNumber == 4:
                    print('Power    : ' + str(power))
                print('Relative asimuth anisotropy angle    : ' + str(angle))
                if useTrend == 1:
                    print('Use trend:  YES')
                    print('Relative TrendAsimuth: ' + str(trendAsimuth))
                    print('RelSigma : ' + str(relSigma))
                else:
                    print('Use trend:  NO')

                print('Seed value: ' + str(seedValue))

            # Angle relative to x axis is input in degrees.
            angle = 90.0 - angle
            gfRealization = np.zeros(nx*ny,float)
            [gfRealization] =  simGaussFieldAddTrendAndTransform(seedValue,nx,ny,xsize,ysize,
                                                                 varioTypeNumber,r1,r2,angle,power,
                                                                 useTrend,trendAsimuth,relSigma,self.__printInfo)

            gaussFields.append(gfRealization)
        # End for        

        return gaussFields

    
