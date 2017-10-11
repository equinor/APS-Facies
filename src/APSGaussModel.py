#!/bin/env python
import sys
from xml.etree.ElementTree import Element

import numpy as np

from src.Trend3D_linear_model_xml import Trend3D_linear_model
# Functions to draw 2D gaussian fields with linear trend and transformed to unifor distribution
from src.simGauss2D import simGaussField, simGaussFieldAddTrendAndTransform
from src.xmlFunctions import getFloatCommand, getIntCommand, getKeyword


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
    def getAnisotropyAzimuthAngle(self,gaussFieldName)
    def getAnisotropyDipAngle(self,gaussFieldName)
    def getPower(self,gaussFieldName)
    def getTrendRuleModel(self,gfName)
    def getTrendRuleModelObject(self,gfName)
    def printInfo(self)
    def setZoneNumber(self,zoneNumber)
    def setVarioType(self,gaussFieldName,varioType)
    def setRange1(self,gaussFieldName,range1)
    def setRange2(self,gaussFieldName,range2)
    def setRange3(self,gaussFieldName,range3)
    def setAnisotropyAzimuthAngle(self,gaussFieldName)
    def setAnisotropyDipAngle(self,gaussFieldName)
    def setPower(self,gaussFieldName,power)
    def setSeedForPreviewSimulation(self,gfName,seed)
    def updateGaussFieldParam(self,gfName,varioType,range1,range2,range3,azimuth,dip,power,
                              useTrend=0,relStdDev=0.0,trendRuleModelObj=None)
    def updateGaussFieldVarioParam(self,gfName,varioType,range1,range2,range3,azimuth,dip,power)
    def removeGaussFieldParam(self,gfName)
    def updateGaussFieldTrendParam(self,gfName,useTrend,trendRuleModelObj,relStdDev)
    def XMLAddElement(self,parent)
    def simGaussFieldWithTrendAndTransform(self,nGaussFields,gridDimNx,gridDimNy,
                                           gridXSize,gridYSize,gridAzimuthAngle,previewCrossSection)

    Private functions:
    def __setEmpty(self)
    def __interpretXMLTree(ET_Tree_zone)
    def __isVarioTypeOK(self,varioType)
    def __getGFIndex(self,gfName)
    """

    def __setEmpty(self):

        # Dictionary give xml keyword for each variable
        self.__xml_keyword = {
            'MainRange':    'MainRange',
            'PerpRange':    'PerpRange',
            'VertRange':    'VertRange',
            'AzimuthAngle': 'AzimuthAngle',
            'DipAngle':     'DipAngle',
            'Power':        'Power'
        }

        # Dictionary give name to each index in __varioForGFModel list
        # item in list: [name,type,range1,range2,range3,azimuth,dip,power]
        self.__index_vario = {
            'Name':         0,
            'Type':         1,
            'MainRange':    2,
            'PerpRange':    3,
            'VertRange':    4,
            'AzimuthAngle': 5,
            'DipAngle':     6,
            'Power':        7
        }
        # Dictionary give name to each index in __trendForGFModel list
        # item in list: [name,useTrend,trendRuleModelObj,relStdDev]
        self.__index_trend = {
            'Name':      0,
            'Use trend': 1,
            'Object':    2,
            'RelStdev':  3
        }
        # Dictionaries of legal value ranges for gauss field parameters
        self.__minValue = {
            'MainRange':    0.0,
            'PerpRange':    0.0,
            'VertRange':    0.0,
            'AzimuthAngle': 0.0,
            'DipAngle':     0.0,
            'Power':        1.0
        }
        self.__maxValue = {
            'AzimuthAngle': 360.0,
            'DipAngle':     90.0,
            'Power':        2.0
        }

        # Dictionary give number to variogram type
        # NOTE: This table must be consistent with simGauss2D
        self.__varioTypeNumber = {
            'SPHERICAL':           1,
            'EXPONENTIAL':         2,
            'GAUSSIAN':            3,
            'GENERAL_EXPONENTIAL': 4
        }
        # Dictionary give name to each index in __seedForPreviewForGFModel
        # item in list: [name,value]
        self.__index_seed = {
            'Name': 0,
            'Seed': 1
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

    def __interpretXMLTree(self, ET_Tree_zone, gaussFieldJobs):
        """
        Description: Read Gauss field models for current zone. 
        Read trend models for the same gauss fields and start seed for 2D preview simulations. 
        """
        for gf in ET_Tree_zone.findall('GaussField'):
            gfName = gf.get('name')
            if not gaussFieldJobs.checkGaussFieldName(gfName):
                raise ValueError(
                    'In model file {0} in zone number: {1} in command GaussField.\n'
                    'Specified name of Gauss field:  {2} is not defined in any of '
                    'the specified gauss field simulation jobs'
                    ''.format(self.__modelFileName, str(self.__zoneNumber), gfName)
                )

            # Read variogram for current GF
            vario = getKeyword(gf, 'Vario', 'GaussField', modelFile=self.__modelFileName)
            varioType = vario.get('name')
            if not self.__isVarioTypeOK(varioType):
                raise ValueError(
                    'In model file {0} in zone number: {1} in command Vario.\n'
                    'Specified variogram type: {1} is not defined.'
                    ''.format(self.__modelFileName, gfName)
                )

            range1 = getFloatCommand(vario, 'MainRange', 'Vario', minValue=0.0,
                                     modelFile=self.__modelFileName)

            range2 = getFloatCommand(vario, 'PerpRange', 'Vario', minValue=0.0,
                                     modelFile=self.__modelFileName)

            range3 = getFloatCommand(vario, 'VertRange', 'Vario', minValue=0.0,
                                     modelFile=self.__modelFileName)

            azimuth = getFloatCommand(vario, 'AzimuthAngle', 'Vario',
                                      minValue=self.__minValue['AzimuthAngle'],
                                      maxValue=self.__maxValue['AzimuthAngle'],
                                      modelFile=self.__modelFileName)

            dip = getFloatCommand(vario, 'DipAngle', 'Vario',
                                  minValue=self.__minValue['DipAngle'],
                                  maxValue=self.__maxValue['DipAngle'],
                                  modelFile=self.__modelFileName)

            power = 1.0
            if varioType == 'GENERAL_EXPONENTIAL':
                power = getFloatCommand(vario, 'Power', 'Vario',
                                        minValue=self.__minValue['Power'],
                                        maxValue=self.__maxValue['Power'],
                                        modelFile=self.__modelFileName)

            # Read trend model for current GF
            trendObjXML = gf.find('Trend')
            trendRuleModelObj = None
            if trendObjXML != None:
                if self.__printInfo >= 3:
                    print('Debug output: Read trend')
                useTrend = 1

                if self.__simBoxThickness <= 0.0:
                    raise ValueError(
                        'In model file {0} in keyword Trend for gauss field name: {1}\n'
                        'The use of trend functions requires that simulation box thickness is specified.\n'
                        ''.format(self.__modelFileName, gfName, self.__className)
                    )
                trendName = trendObjXML.get('name')
                if trendName == 'Linear3D':
                    trendRuleModelObj = Trend3D_linear_model(trendObjXML, self.__printInfo, self.__modelFileName)
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
            item = [gfName, seed]

            # Add gauss field parameters to data structure
            self.updateGaussFieldParam(gfName, varioType, range1, range2, range3, azimuth, dip, power,
                                       useTrend, relStdDev, trendRuleModelObj)
            # Set preview simulation start seed for gauss field
            self.setSeedForPreviewSimulation(gfName, seed)

        # End loop over gauss fields for current zone model

        if self.__varioForGFModel is None:
            raise NameError(
                'Error when reading model file: ' + self.__modelFileName + '\n'
                                                                           'Error: Missing keyword GaussField under '
                                                                           'keyword Zone'
            )

        if self.__printInfo >= 3:
            print('Debug output: Gauss field variogram parameter for current zone model:')
            print(repr(self.__varioForGFModel))

            print('Debug output:Gauss field trend parameter for current zone model:')
            print(repr(self.__trendForGFModel))

            print('Debug output: Gauss field preview seed for current zone model:')
            print(repr(self.__seedForPreviewForGFModel))

    def initialize(self, inputZoneNumber, mainFaciesTable, gaussFieldJobs,
                   gaussModelList, trendModelList,
                   simBoxThickness, previewSeedList, printInfo):

        if printInfo >= 3:
            print('Debug output: Call the initialize function in ' + self.__className)

        # Set default values
        self.__setEmpty()

        GNAME = self.__index_vario['Name']
        GTYPE = self.__index_vario['Type']
        GRANGE1 = self.__index_vario['MainRange']
        GRANGE2 = self.__index_vario['PerpRange']
        GRANGE3 = self.__index_vario['VertRange']
        GAZIMUTH = self.__index_vario['AzimuthAngle']
        GDIP = self.__index_vario['DipAngle']
        GPOWER = self.__index_vario['Power']

        TNAME = self.__index_trend['Name']
        TUSE = self.__index_trend['Use trend']
        TOBJ = self.__index_trend['Object']
        TSTD = self.__index_trend['RelStdev']

        SNAME = self.__index_seed['Name']
        SVALUE = self.__index_seed['Seed']

        self.__zoneNumber = inputZoneNumber
        self.__printInfo = printInfo
        self.__simBoxThickness = simBoxThickness
        self.__mainFaciesTable = mainFaciesTable

        # gaussModelList  = list of objects of the form: [gfName,type,range1,range2,range3,azimuth,dip,power]
        # trendModelList  = list of objects of the form: [gfName,useTrend,trendRuleModelObj,relStdDev]
        # previewSeedList = list of objects of the form: [gfName,seedValue]
        assert len(trendModelList) == len(gaussModelList)
        for i in range(len(gaussModelList)):
            item = gaussModelList[i]
            if len(item) != len(self.__index_vario):
                raise ValueError('Programming error: Input list items in gausModelList is not of correct length')
            trendItem = trendModelList[i]
            seedItem = previewSeedList[i]
            assert item[GNAME] == trendItem[TNAME]
            assert item[GNAME] == seedItem[SNAME]

            gfName = item[GNAME]
            if not gaussFieldJobs.checkGaussFieldName(gfName):
                raise ValueError(
                    'In model file {0} in zone number: {1} in command GaussField.'
                    'Specified name of Gauss field:  {2} is not defined in any of '
                    'the specified gauss field simulation jobs'
                    ''.format(self.__modelFileName, str(self.__zoneNumber), gfName)
                )

            varioType = item[GTYPE]
            if not self.__isVarioTypeOK(varioType):
                raise ValueError(
                    'In initialize function for {0} in zone number: {1}. '
                    'Specified variogram type: {2} is not defined.'
                    ''.format(self.__className, self.__zoneNumber, varioType)
                )
            range1 = item[GRANGE1]
            range2 = item[GRANGE2]
            range3 = item[GRANGE3]
            azimuth = item[GAZIMUTH]
            dip = item[GDIP]
            power = item[GPOWER]

            trendRuleModelObj = trendItem[TOBJ]
            relStdDev = trendItem[TSTD]
            useTrend = trendItem[TUSE]
            seed = seedItem[SVALUE]

            # Set variogram parameters for this gauss field
            self.updateGaussFieldParam(gfName, varioType, range1, range2, range3, azimuth, dip, power)

            # Set trend model parameters for this gauss field
            self.updateGaussFieldTrendParam(gfName, useTrend, trendRuleModelObj, relStdDev)

            # Set preview simulation start seed for gauss field
            self.setSeedForPreviewSimulation(gfName, seed)

    def getNGaussFields(self):
        return len(self.__varioForGFModel)

    def __isVarioTypeOK(self, varioType):
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
        nGF = len(self.__varioForGFModel)
        for i in range(nGF):
            item = self.__varioForGFModel[i]
            name = item[GNAME]
            gfNames.append(name)
        return gfNames

    def findGaussFieldParameterItem(self, gaussFieldName):
        GNAME = self.__index_vario['Name']
        nGF = len(self.__varioForGFModel)
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

    def getVarioType(self, gaussFieldName):
        GTYPE = self.__index_vario['Type']
        item = self.findGaussFieldParameterItem(gaussFieldName)
        varioType = item[GTYPE]
        return varioType

    def getVarioTypeNumber(self, gaussFieldName):
        varioType = self.getVarioType(gaussFieldName)
        varioTypeNumber = self.__varioTypeNumber[varioType]
        return varioTypeNumber

    def getMainRange(self, gaussFieldName):
        GRANGE1 = self.__index_vario['MainRange']
        item = self.findGaussFieldParameterItem(gaussFieldName)
        r = item[GRANGE1]
        return r

    def getPerpRange(self, gaussFieldName):
        GRANGE2 = self.__index_vario['PerpRange']
        item = self.findGaussFieldParameterItem(gaussFieldName)
        r = item[GRANGE2]
        return r

    def getVertRange(self, gaussFieldName):
        GRANGE3 = self.__index_vario['VertRange']
        item = self.findGaussFieldParameterItem(gaussFieldName)
        r = item[GRANGE3]
        return r

    def getAnisotropyAzimuthAngle(self, gaussFieldName):
        GAZIMUTH = self.__index_vario['AzimuthAngle']
        item = self.findGaussFieldParameterItem(gaussFieldName)
        r = item[GAZIMUTH]
        return r

    def getAnisotropyDipAngle(self, gaussFieldName):
        GDIP = self.__index_vario['DipAngle']
        item = self.findGaussFieldParameterItem(gaussFieldName)
        r = item[GDIP]
        return r

    def getPower(self, gaussFieldName):
        GPOWER = self.__index_vario['Power']
        item = self.findGaussFieldParameterItem(gaussFieldName)
        r = item[GPOWER]
        return r

    def getTrendRuleItem(self, gfName):
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

    def getTrendRuleModel(self, gfName):
        TUSE = self.__index_trend['Use trend']
        TOBJ = self.__index_trend['Object']
        TSTD = self.__index_trend['RelStdev']
        item = self.getTrendRuleItem(gfName)
        if item is None:
            return None
        else:
            useTrend = item[TUSE]
            trendModelObj = item[TOBJ]
            relStdDev = item[TSTD]
            return [useTrend, trendModelObj, relStdDev]

    def getTrendRuleModelObject(self, gfName):
        TOBJ = self.__index_trend['Object']
        item = self.getTrendRuleItem(gfName)
        if item is None:
            return None
        else:
            trendModelObj = item[TOBJ]
            return trendModelObj

    def printInfo(self):
        return self.__printInfo

    def __getGFIndex(self, gfName):
        GNAME = self.__index_vario['Name']

        indx = -1
        for i in range(len(self.__varioForGFModel)):
            item = self.__varioForGFModel[i]
            gf = item[GNAME]
            if gf == gfName:
                indx = i
                break
        return indx

    def setZoneNumber(self, zoneNumber):
        self.__zoneNumber = zoneNumber
        return

    def setValue(self, gaussFieldName, variableName, value, checkMax=False):
        # Minimum allowed value
        minValue = self.__minValue[variableName]

        # Max allowed value
        if checkMax:
            maxValue = self.__maxValue[variableName]

        # index to where the variable is located in the __varioFORGFModel
        variableIndex = self.__index_vario[variableName]

        err = 0
        if value < minValue:
            err = 1
        if checkMax:
            if value > maxValue:
                err = 1
        if err == 0:
            gfList = self.getUsedGaussFieldNames()
            if gaussFieldName in gfList:
                indx = self.__getGFIndex(gaussFieldName)
                item = self.__varioForGFModel[indx]
                item[variableIndex] = value
            else:
                err = 1
        return err

    def setVarioType(self, gaussFieldName, varioType):
        GTYPE = self.__index_vario['Type']
        err = 0
        if self.__isVarioTypeOK(varioType):
            gfList = self.getUsedGaussFieldNames()
            if gaussFieldName in gfList:
                indx = self.__getGFIndex(gaussFieldName)
                item = self.__varioForGFModel[indx]
                item[GTYPE] = varioType
            else:
                err = 1
        else:
            err = 1
        return err

    def setMainRange(self, gaussFieldName, range1):
        err = self.setValue(gaussFieldName, 'MainRange', range1)
        return err

    def setPerpRange(self, gaussFieldName, range2):
        err = self.setValue(gaussFieldName, 'PerpRange', range2)
        return err

    def setVertRange(self, gaussFieldName, range3):
        err = self.setValue(gaussFieldName, 'VertRange', range3)
        return err

    def setAnisotropyAzimuthAngle(self, gaussFieldName, azimuth):
        err = self.setValue(gaussFieldName, 'AzimuthAngle', azimuth, checkMax=True)
        return err

    def setAnisotropyDipAngle(self, gaussFieldName, dip):
        err = self.setValue(gaussFieldName, 'DipAngle', dip, checkMax=True)
        return err

    def setPower(self, gaussFieldName, power):
        err = self.setValue(gaussFieldName, 'Power', power, checkMax=True)
        return err

    def setSeedForPreviewSimulation(self, gfName, seed):
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

    def updateGaussFieldParam(self, gfName, varioType, range1, range2, range3, azimuth, dip, power,
                              useTrend=0, relStdDev=0.0, trendRuleModelObj=None):
        # Update or create new gauss field parameter object (with trend)
        GNAME = self.__index_vario['Name']
        err = 0
        found = 0
        if not self.__isVarioTypeOK(varioType):
            print('Error in ' + self.__className + ' in ' + 'updateGaussFieldParam')
            raise ValueError('Undefined variogram type specified.')
        if range1 < 0:
            print('Error in ' + self.__className + ' in ' + 'updateGaussFieldParam')
            raise ValueError('Correlation range < 0.0')
        if range2 < 0:
            print('Error in ' + self.__className + ' in ' + 'updateGaussFieldParam')
            raise ValueError('Correlation range < 0.0')
        if range3 < 0:
            print('Error in ' + self.__className + ' in ' + 'updateGaussFieldParam')
            raise ValueError('Correlation range < 0.0')
        if varioType == 'GENERAL_EXPONENTIAL':
            if power < 1.0 or power > 2.0:
                print('Error in ' + self.__className + ' in ' + 'updateGaussFieldParam')
                raise ValueError('Exponent in GENERAL_EXPONENTIAL variogram is outside [1.0,2.0]')
        if relStdDev < 0.0:
            print('Error in ' + self.__className + ' in ' + 'updateGaussFieldParam')
            raise ValueError('Relative standard deviation used when trends are specified is negative.')

        # Check if gauss field is already defined, then update parameters or create new
        for item in self.__varioForGFModel:
            name = item[GNAME]
            if name == gfName:
                self.updateGaussFieldVarioParam(gfName, varioType, range1, range2, range3, azimuth, dip, power)
                self.updateGaussFieldTrendParam(gfName, useTrend, trendRuleModelObj, relStdDev)
                found = 1
                break
        if found == 0:
            # Create data for a new gauss field for both variogram  data and trend data
            # But data for trend parameters must be set by another function and default is set here.
            itemVario = [gfName, varioType, range1, range2, range3, azimuth, dip, power]
            self.__varioForGFModel.append(itemVario)
            if trendRuleModelObj is None:
                useTrend = 0
                relStdDev = 0.0
            else:
                useTrend = 1
            itemTrend = [gfName, useTrend, trendRuleModelObj, relStdDev]
            self.__trendForGFModel.append(itemTrend)
            defaultSeed = 0
            self.__seedForPreviewForGFModel.append([gfName, defaultSeed])
        return err

    def updateGaussFieldVarioParam(self, gfName, varioType, range1, range2, range3, azimuth, dip, power):
        # Update gauss field variogram parameters for existing gauss field model
        # But it does not create new object.
        GNAME = self.__index_vario['Name']
        GTYPE = self.__index_vario['Type']
        GRANGE1 = self.__index_vario['MainRange']
        GRANGE2 = self.__index_vario['PerpRange']
        GRANGE3 = self.__index_vario['VertRange']
        GAZIMUTH = self.__index_vario['AzimuthAngle']
        GDIP = self.__index_vario['DipAngle']
        GPOWER = self.__index_vario['Power']

        err = 0
        found = 0
        # Check that gauss field is already defined, then update parameters.
        for item in self.__varioForGFModel:
            name = item[GNAME]
            if name == gfName:
                found = 1
                item[GTYPE] = varioType
                item[GRANGE1] = range1
                item[GRANGE2] = range2
                item[GRANGE3] = range3
                item[GAZIMUTH] = azimuth
                item[GDIP] = dip
                item[GPOWER] = power
                break
        if found == 0:
            err = 1
        return err

    def removeGaussFieldParam(self, gfName):
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

    def updateGaussFieldTrendParam(self, gfName, useTrend, trendRuleModelObj, relStdDev):
        # Update trend parameters for existing trend for gauss field model
        # But it does not create new trend object.
        TNAME = self.__index_trend['Name']
        TUSE = self.__index_trend['Use trend']
        TOBJ = self.__index_trend['Object']
        TSTD = self.__index_trend['RelStdev']
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

    def XMLAddElement(self, parent):
        GNAME = self.__index_vario['Name']
        GTYPE = self.__index_vario['Type']
        GRANGE1 = self.__index_vario['MainRange']
        GRANGE2 = self.__index_vario['PerpRange']
        GRANGE3 = self.__index_vario['VertRange']
        GAZIMUTH = self.__index_vario['AzimuthAngle']
        GDIP = self.__index_vario['DipAngle']
        GPOWER = self.__index_vario['Power']

        TNAME = self.__index_trend['Name']
        TUSE = self.__index_trend['Use trend']
        TOBJ = self.__index_trend['Object']
        TSTD = self.__index_trend['RelStdev']

        SNAME = self.__index_seed['Name']
        SVALUE = self.__index_seed['Seed']

        if self.__printInfo >= 3:
            print('Debug output: call XMLADDElement from ' + self.__className)

        # Add child command GaussField
        nGaussFieldsForModel = len(self.__varioForGFModel)
        for i in range(nGaussFieldsForModel):
            gfName = self.__varioForGFModel[i][GNAME]
            varioType = self.__varioForGFModel[i][GTYPE]
            range1 = self.__varioForGFModel[i][GRANGE1]
            range2 = self.__varioForGFModel[i][GRANGE2]
            range3 = self.__varioForGFModel[i][GRANGE3]
            azimuth = self.__varioForGFModel[i][GAZIMUTH]
            dip = self.__varioForGFModel[i][GDIP]
            power = self.__varioForGFModel[i][GPOWER]

            if gfName != self.__trendForGFModel[i][TNAME]:
                print('Error in class: ' + self.__className + ' in ' + 'XMLAddElement')
                sys.exit()
            useTrend = self.__trendForGFModel[i][TUSE]
            trendObj = self.__trendForGFModel[i][TOBJ]
            relStdDev = self.__trendForGFModel[i][TSTD]

            tag = 'GaussField'
            attribute = {'name': gfName}
            elem = Element(tag, attribute)
            parent.append(elem)
            gfElement = elem
            tag = 'Vario'
            attribute = {'name': varioType}
            elem = Element(tag, attribute)
            gfElement.append(elem)
            varioElement = elem
            tag = self.__xml_keyword['MainRange']
            elem = Element(tag)
            elem.text = ' ' + str(range1) + ' '
            varioElement.append(elem)
            tag = self.__xml_keyword['PerpRange']
            elem = Element(tag)
            elem.text = ' ' + str(range2) + ' '
            varioElement.append(elem)
            tag = self.__xml_keyword['VertRange']
            elem = Element(tag)
            elem.text = ' ' + str(range3) + ' '
            varioElement.append(elem)
            tag = self.__xml_keyword['AzimuthAngle']
            elem = Element(tag)
            elem.text = ' ' + str(azimuth) + ' '
            varioElement.append(elem)
            tag = self.__xml_keyword['DipAngle']
            elem = Element(tag)
            elem.text = ' ' + str(dip) + ' '
            varioElement.append(elem)
            if varioType == 'GENERAL_EXPONENTIAL':
                tag = self.__xml_keyword['Power']
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

    def simGaussFieldWithTrendAndTransform(self, nGaussFields, gridDimNx, gridDimNy,
                                           gridXSize, gridYSize, gridAzimuthAngle, previewCrossSection):
        TUSE = self.__index_trend['Use trend']
        TOBJ = self.__index_trend['Object']
        TSTD = self.__index_trend['RelStdev']
        SVALUE = self.__index_seed['Seed']

        nx = gridDimNx
        ny = gridDimNy
        xsize = gridXSize
        ysize = gridYSize

        gaussFieldNamesForSimulation = self.getUsedGaussFieldNames()
        assert nGaussFields == len(gaussFieldNamesForSimulation)
        gaussFields = []
        for i in range(nGaussFields):
            # Find data for specified Gauss field name
            name = gaussFieldNamesForSimulation[i]
            seedValue = self.__seedForPreviewForGFModel[i][SVALUE]
            varioType = self.getVarioType(name)
            varioTypeNumber = self.getVarioTypeNumber(name)
            #            r1        = self.getMainRange(name)
            #            r2        = self.getPerpRange(name)
            #            r3        = self.getVertRange(name)
            #            azimuthVario  = self.getAnisotropyAzimuthAngle(name)
            #            dipVario  = self.getAnisotropyDipAngle(name)
            #            azimuthVario = azimuthVario - gridAzimuthAngle

            power = self.getPower(name)

            useTrend = self.__trendForGFModel[i][TUSE]
            trendAzimuth = 0.0
            if useTrend == 1:
                trendObj = self.__trendForGFModel[i][TOBJ]
                trendAzimuth = trendObj.getAzimuth() - gridAzimuthAngle

            relSigma = self.__trendForGFModel[i][TSTD]
            if self.__printInfo >= 3:
                print('Debug output: Simulate gauss field: ' + name)
                print('Debug output: VarioType: ' + str(varioType))
                print('Debug output: VarioTypeNumber: ' + str(varioTypeNumber))

                if varioTypeNumber == 4:
                    print('Debug output: Power    : ' + str(power))

                if useTrend == 1:
                    print('Debug output: Use trend:  YES')
                    print('Debug output: Relative TrendAzimuth: ' + str(trendAzimuth))
                    print('Debug output: RelSigma : ' + str(relSigma))
                else:
                    print('Debug output: Use trend:  NO')

                print('Debug output: Seed value: ' + str(seedValue))

            # Calculate 2D projection of the correlation ellipsoid
            if previewCrossSection == 'IJ':
                projection = 'xy'
            elif previewCrossSection == 'IK':
                projection = 'xz'
            elif previewCrossSection == 'JK':
                projection = 'yz'

            [angle1, range1, angle2, range2] = self.calc2DVarioFrom3DVario(name, gridAzimuthAngle, projection)
            azimuthVario = angle1
            if self.__printInfo >= 3:
                print('Debug output: Range1 in projection: ' + projection + ' : ' + str(range1))
                print('Debug output: Range2 in projection: ' + projection + ' : ' + str(range2))
                print('Debug output: Angle from vertical axis for Range1 direction: ' + str(angle1))
                print('Debug output: Angle from vertical axis for Range2 direction: ' + str(angle2))

            # Angle relative to first  axis is input in degrees.
            azimuthVario = 90.0 - azimuthVario
            gfRealization = np.zeros(nx * ny, float)
            [gfRealization] = simGaussFieldAddTrendAndTransform(seedValue, nx, ny, xsize, ysize,
                                                                varioTypeNumber, range1, range2, azimuthVario, power,
                                                                useTrend, trendAzimuth, relSigma, self.__printInfo)

            gaussFields.append(gfRealization)
        # End for        

        return gaussFields

    def simGaussFieldWithTrendAndTransformNew(self, nGaussFields,
                                              simBoxXsize, simBoxYsize, simBoxZsize,
                                              gridNX, gridNY, gridNZ,
                                              gridAzimuthAngle, crossSectionType):
        TUSE = self.__index_trend['Use trend']
        TOBJ = self.__index_trend['Object']
        TSTD = self.__index_trend['RelStdev']
        SVALUE = self.__index_seed['Seed']

        # Note Note that nx and ny here means the number of grid cells in the two dimensions 
        # to be simulated as a cross section of the 3D simulation box. Hence it does not mean x and y direction
        # of the 3D simulation box since the cross section can be IK (or xz) or JK (or yz) and not in general IJ (or
        # xy).
        if crossSectionType == 'IJ':
            gridDim1 = gridNX
            gridDim2 = gridNY
            size1 = simBoxXsize
            size2 = simBoxYsize
            crossSectionIndx = int(gridNZ / 2)
            projection = 'xy'
        elif crossSectionType == 'IK':
            gridDim1 = gridNX
            gridDim2 = gridNZ
            size1 = simBoxXsize
            size2 = simBoxZsize
            crossSectionIndx = int(gridNY / 2)
            projection = 'xz'
        elif crossSectionType == 'JK':
            gridDim1 = gridNY
            gridDim2 = gridNZ
            size1 = simBoxYsize
            size2 = simBoxZsize
            crossSectionIndx = int(gridNX / 2)
            projection = 'yz'
        else:
            raise ValueError('Undefined cross section {}'.format(crossSectionType))

        gaussFieldNamesForSimulation = self.getUsedGaussFieldNames()
        assert nGaussFields == len(gaussFieldNamesForSimulation)
        gaussFields = []
        for i in range(nGaussFields):
            # Find data for specified Gauss field name
            name = gaussFieldNamesForSimulation[i]
            seedValue = self.__seedForPreviewForGFModel[i][SVALUE]
            varioType = self.getVarioType(name)
            varioTypeNumber = self.getVarioTypeNumber(name)
            mainRange = self.getMainRange(name)
            perpRange = self.getPerpRange(name)
            vertRange = self.getVertRange(name)
            azimuthVario = self.getAnisotropyAzimuthAngle(name)
            dipVario = self.getAnisotropyDipAngle(name)
            power = self.getPower(name)
            if self.__printInfo >= 3:
                print('Debug output: Within simGaussFieldWithTrendAndTransformNew')
                print('Debug output: Simulate gauss field: ' + name)
                print('Debug output: VarioType: ' + str(varioType))
                print('Debug output: VarioTypeNumber: ' + str(varioTypeNumber))
                print('Debug output: Azimuth angle for Main range direction: ' + str(azimuthVario))
                print('Debug output: Dip angle for Main range direction: ' + str(dipVario))

                if varioTypeNumber == 4:
                    print('Debug output: Power    : ' + str(power))

                print('Debug output: Seed value: ' + str(seedValue))

            # Calculate 2D projection of the correlation ellipsoid
            [angle1, range1, angle2, range2] = self.calc2DVarioFrom3DVario(name, gridAzimuthAngle, projection)
            azimuthVario = angle1
            if self.__printInfo >= 3:
                print('Debug output: Range1 in projection: ' + projection + ' : ' + str(range1))
                print('Debug output: Range2 in projection: ' + projection + ' : ' + str(range2))
                print('Debug output: Angle from vertical axis for Range1 direction: ' + str(angle1))
                print('Debug output: Angle from vertical axis for Range2 direction: ' + str(angle2))

            residualField = simGaussField(seedValue, gridDim1, gridDim2, size1, size2,
                                          varioTypeNumber, range1, range2,
                                          azimuthVario, power,
                                          self.__printInfo)

            # Calculate trend
            [useTrend, trendModelObject, relStdDev] = self.getTrendRuleModel(name)
            if useTrend == 1:
                [minMaxDifference, trendField] = trendModelObject.createTrendFor2DProjection(simBoxXsize,
                                                                                             simBoxYsize,
                                                                                             simBoxZsize,
                                                                                             gridAzimuthAngle,
                                                                                             gridNX, gridNY, gridNZ,
                                                                                             crossSectionType,
                                                                                             crossSectionIndx)
                gaussFieldWithTrend = self.__addTrend(residualField, trendField,
                                                      relStdDev, minMaxDifference)
            else:
                gaussFieldWithTrend = residualField

            transField = self.__transformEmpiricDistributionToUniform(gaussFieldWithTrend)

            gaussFields.append(transField)
        # End for        

        return gaussFields

    def __addTrend(self, residualField, trendField, relSigma, trendMaxMinDifference):
        """
        Description: Calculate standard deviation sigma = relSigma * trendMaxMinDifference
        Add trend and residual field  Field = Trend + sigma*residual
        Input residualField and trendField should be 1D float numpy arrays of same size.
        Return is trend plus residual with correct standard deviation as numpy 1D array.
        """
        # Standard deviation
        sigma = relSigma * trendMaxMinDifference
        if self.__printInfo >= 3:
            print('Debug output:  Relative standard deviation = ' + str(relSigma))
            print('Debug output:  Difference between max value and min value of trend = ' + str(trendMaxMinDifference))
            print('Debug output:  Calculated standard deviation = ' + str(sigma))
            print(' ')
        n = len(trendField)
        print('len(trendField), len(residualField): ' + str(len(trendField)) + ' ' + str(len(residualField)))
        assert len(trendField) == len(residualField)
        gaussFieldWithTrend = np.zeros(n, float)
        for i in range(n):
            gaussFieldWithTrend[i] = trendField[i] + residualField[i] * sigma
        return gaussFieldWithTrend

    def __transformEmpiricDistributionToUniform(self, inputValues):
        """
        Description: Take input as numpy 1D float array and return numpy 1D float array where 
        the values is transformed to uniform distribution.
        The input array is regarded as outcome of  probability distribution. 
        The output assigm the empiric percentile from the cumulative empiric distribution 
        to each array element. This ensure that the probability distribution of the output 
        regarded as outcome from a probability distribution is uniform.
        """
        # Transform into uniform distribution
        if self.__printInfo >= 3:
            print('Debug output:  Transform 2D Gauss field by empiric transformation to uniform distribution')
            print(' ')

        nVal = len(inputValues)
        transformedValues = np.zeros(nVal, float)
        sort_indx = np.argsort(inputValues)
        for i in range(nVal):
            indx = sort_indx[i]
            u = float(i) / float(nVal)
            transformedValues[indx] = u

        return transformedValues

    def calc2DVarioFrom3DVario(self, gaussFieldName, gridAzimuthAngle, projection):
        """
         Variogram ellipsoid in 3D is defined by a symmetric 3x3 matrix M such that
         transpose(V)*M * V = 1 where transpose(V) = [x,y,z]. The principal directions are found
         by diagonalization of the matrix. The diagonal matrix has the diagonal matrix elements 
         D11 = 1/(B*B)  D22 = 1/(A*A)  D33 = 1/(C*C) where A,B,C are the half axes in the three
         principal directions. For variogram ellipsoid the MainRange = A, PerpRange = B, VertRange = C.
         To define the orientation, first define a ellipsoid oriented with 
         MainRange in y direction, PerpRange in x direction and VertRange in z direction.
         Then rotate this ellipsoid first around z axis with angle defined as AzimuthAngle in clockwise direction.
         The azimuth angle is the angle between the y axis and the new rotated y' axis.
         Then rotate the the ellipsoid an angle around the new x' axis. This is the dip angle. The final orientation
         is then found and the principal axes are (x'',y'',z'') in which the M matrix is diagonal.
         Note that the coordinate system (x,y,z) is left handed and z axis is pointing 
         downward compared to a right handed coordinate system.
         To define the matrix M in (x,y,z) coordinate system given that we 
         know its half axes in the principal directions, we need the transformation from column vector of (x,y,z)
         which we call V vector to column vector of (x'',y'',z'') which we call V'':
             V'' =  R_dip * R_azimuth * V   where we call R = R_dip * R_azimuth
         where R_azimuth is the matrix rotating the ellipse around z axis an angle = azimuth angle
         and R_dip is the matrix rotating the vector V' = R_azimuth*V around the x' axis and angle = dip angle.
         The final matrix M in x,y,z coordinates is then transpose(R)*M_diagonal*R.

         If we now assume y = 0, then the variogram ellipsoid becomes a variogram ellipse 
         and we can determine the half axes in this ellipse and its orientation by restricting ourself 
         to the x,z plane and calculate the principal directions of this ellipse. 
         The diagonal components after diagonalizing this 2x2 matrix is the correlation lengths in 
         the x,z plane and the rotation of the ellipse in the x,z plane is found from the principal 
         directions of the ellipse. The correlation lengths and the direction calculated for the ellipse is
         returned from this function and can be used to simulate a 2D cross section in xz direction. The same can be
         done
         for x,y plane with z = 0 and for y,z plane for x = 0.
         """
        funcName = 'calc2DVarioFrom3DVario'
        if self.__printInfo>=3:
            print('Debug output: Function: {}'.format(funcName))
        ry = self.getMainRange(gaussFieldName)
        rx = self.getPerpRange(gaussFieldName)
        rz = self.getVertRange(gaussFieldName)

        # Azimuth relative to global x,y,z coordinates
        azimuth = self.getAnisotropyAzimuthAngle(gaussFieldName)

        # Azimuth relative to local coordinate system defined by the orientation of the grid (simulation box)
        azimuth = azimuth - gridAzimuthAngle
        azimuth = azimuth * np.pi / 180.0

        # Dip angle relative to local simulation box
        dip = self.getAnisotropyDipAngle(gaussFieldName)
        dip = dip * np.pi / 180.0

        cosTheta = np.cos(azimuth)
        sinTheta = np.sin(azimuth)
        cosDip = np.cos(dip)
        sinDip = np.sin(dip)

        # define R_azimuth matrix:
        R_azimuth = np.array([[cosTheta, -sinTheta, 0.0],
                              [sinTheta, cosTheta, 0.0],
                              [0.0, 0.0, 1.0]])

        # define R_dip matrix
        R_dip = np.array([[1.0, 0.0, 0.0],
                          [0.0, cosDip, sinDip],
                          [0.0, -sinDip, cosDip]])

        # calculate R matrix
        R = R_dip.dot(R_azimuth)
        # calculate M matrix in principal coordinates
        M_diag = np.array([[1.0 / (rx * rx), 0.0, 0.0],
                           [0.0, 1.0 / (ry * ry), 0.0],
                           [0.0, 0.0, 1.0 / (rz * rz)]])
        # calculate M matrix in x,y,z coordinates
        tmp = M_diag.dot(R)
        Rt = np.transpose(R)
        M = Rt.dot(tmp)
        if self.__printInfo >= 3:
            print('Debug output: M:')
            print(M)
            print(' ')
        # calculate eigenvalues and rotation angle in any of the projections xy,xz,yz
        # Let U be the 2x2 matrix in the projection (where row and column corresponding to 
        # the coordinate that is set to 0 is removed
        if projection == 'xy':
            U = np.array([[M[0, 0], M[0, 1]],
                          [M[0, 1], M[1, 1]]])
        elif projection == 'xz':
            U = np.array([[M[0, 0], M[0, 2]],
                          [M[0, 2], M[2, 2]]])
        elif projection == 'yz':
            U = np.array([[M[1, 1], M[1, 2]],
                          [M[1, 2], M[2, 2]]])
        else:
            raise ValueError('Unknown projection for calculation of 2D variogram ellipse from 3D variogram ellipsoid')
        # angles are azimuth angles (Measured from 2nd axis clockwise)
        [angle1, range1, angle2, range2] = self.__calcProjection(U)

        return [angle1, range1, angle2, range2]

    def __calcProjection(self, U):
        funcName = '__calcProjection'
        if self.__printInfo >= 3:
            print('Debug output: U:')
            print(U)
        w, v = np.linalg.eigh(U)
        if self.__printInfo >= 3:
            print('Debug output: Eigenvalues:')
            print(w)
            print('Debug output: Eigenvectors')
            print(v)
            
        # Largest eigenvalue and corresponding eigenvector should be defined as main principal range and direction 
        if v[0, 1] != 0.0:
            angle = np.arctan(v[0, 0] / v[0, 1])
            angle = angle * 180.0 / np.pi
            if angle < 0.0:
                angle = angle + 180.0
        else:
            # y component is 0, hence the direction is defined by the x axis
            angle = 90.0
        angle1 = angle
        range1 = np.sqrt(1.0 / w[0])
        if self.__printInfo >= 3:
            print('Debug output: Function: {funcName} Direction (angle): {angle} for range: {range}'
                  ''.format(funcName=funcName, angle=str(angle1), range=str(range1)))

        # Smallest eigenvalue and corresponding eigenvector should be defined as perpendicular principal direction 
        if v[1, 1] != 0.0:
            angle = np.arctan(v[1, 0] / v[1, 1])
            angle = angle * 180.0 / np.pi
            if angle < 0.0:
                angle = angle + 180.0
        else:
            # y component is 0, hence the direction is defined by the x axis
            angle = 90.0
        angle2 = angle
        range2 = np.sqrt(1.0 / w[1])
        if self.__printInfo >= 3:
            print('Debug output: Function: {funcName} Direction (angle): {angle} for range: {range}'
                  ''.format(funcName=funcName, angle=str(angle2), range=str(range2)))

        # Angles are azimuth angles
        return [angle1, range1, angle2, range2]
