#!/bin/env python
import sys
from xml.etree.ElementTree import Element

import numpy as np

from src.Trend3D_linear_model_xml import Trend3D_linear_model
# Functions to draw 2D gaussian fields with linear trend and transformed to unifor distribution
from src.simGauss2D import simGaussField, simGaussFieldAddTrendAndTransform
from src.utils.constants import Debug
from src.xmlFunctions import getFloatCommand, getIntCommand, getKeyword
from src.utils.constants import Debug


class APSGaussModel:
    """
    Description: This class contain model parameter specification of the gaussian fields to be simulated for a zone.
    The class contain both variogram data and trend data. Both functions to read the parameters from and XML tree
    for the model file and functions to create an object from an initialization function exist.
    
    Constructor:
    def __init__(self,ET_Tree_zone=None, mainFaciesTable= None,modelFileName = None,
                 debug_level=Debug.OFF,zoneNumber=0,simBoxThickness=0)
    
    Public functions:
    def initialize(self,inputZoneNumber,mainFaciesTable,gaussModelList,trendModelList,
                   simBoxThickness,previewSeed,debug_level=Debug.OFF)
    def getZoneNumber(self)
    def getUsedGaussFieldNames(self)
    def getVariogramType(self,gaussFieldName)
    def getVariogramTypeNumber(self,gaussFieldName)
    def getMainRange(self,gaussFieldName)
    def getPerpRange(self,gaussFieldName)
    def getVertRange(self,gaussFieldName)
    def getAnisotropyAzimuthAngle(self,gaussFieldName)
    def getAnisotropyDipAngle(self,gaussFieldName)
    def getPower(self,gaussFieldName)
    def getTrendRuleModel(self,gfName)
    def getTrendRuleModelObject(self,gfName)
    def get_debug_level(self)
    def setZoneNumber(self,zoneNumber)
    def setVariogramType(self,gaussFieldName,variogramType)
    def setRange1(self,gaussFieldName,range1)
    def setRange2(self,gaussFieldName,range2)
    def setRange3(self,gaussFieldName,range3)
    def setAnisotropyAzimuthAngle(self,gaussFieldName)
    def setAnisotropyDipAngle(self,gaussFieldName)
    def setPower(self,gaussFieldName,power)
    def setSeedForPreviewSimulation(self,gfName,seed)
    def updateGaussFieldParam(self,gfName,variogramType,range1,range2,range3,azimuth,dip,power,
                              useTrend=0,relStdDev=0.0,trendRuleModelObj=None)
    def updateGaussFieldVariogramParam(self,gfName,variogramType,range1,range2,range3,azimuth,dip,power)
    def removeGaussFieldParam(self,gfName)
    def updateGaussFieldTrendParam(self,gfName,useTrend,trendRuleModelObj,relStdDev)
    def XMLAddElement(self,parent)
    def simGaussFieldWithTrendAndTransform(self,nGaussFields,gridDimNx,gridDimNy,
                                           gridXSize,gridYSize,gridAzimuthAngle,previewCrossSection)

    Private functions:
    def __setEmpty(self)
    def __interpretXMLTree(ET_Tree_zone)
    def __isVariogramTypeOK(self,variogramType)
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
        self.__index_variogram = {
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
        self.__variogramTypeNumber = {
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
        self.__debug_level = Debug.OFF
        self.__mainFaciesTable = None
        self.__variogramForGFModel = []
        self.__trendForGFModel = []
        self.__seedForPreviewForGFModel = []
        self.__simBoxThickness = 0
        self.__zoneNumber = 0
        self.__modelFileName = None

    def __init__(self, ET_Tree_zone=None, mainFaciesTable=None, gaussFieldJobs=None, modelFileName=None,
                 debug_level=Debug.OFF, zoneNumber=0, simBoxThickness=0):
        """
        Description: Can create empty object or object with data read from xml tree representing the model file.
        """
        self.__setEmpty()

        if ET_Tree_zone is not None:
            # Get data from xml tree
            if debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: Call init ' + self.__className + ' and read from xml file')

            assert mainFaciesTable
            assert zoneNumber
            assert simBoxThickness
            assert modelFileName

            self.__mainFaciesTable = mainFaciesTable
            self.__zoneNumber = zoneNumber
            self.__simBoxThickness = simBoxThickness
            self.__modelFileName = modelFileName
            self.__debug_level = debug_level

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
            variogram = getKeyword(gf, 'Vario', 'GaussField', modelFile=self.__modelFileName)
            variogramType = variogram.get('name')
            if not self.__isVariogramTypeOK(variogramType):
                raise ValueError(
                    'In model file {0} in zone number: {1} in command Vario.\n'
                    'Specified variogram type: {1} is not defined.'
                    ''.format(self.__modelFileName, gfName)
                )

            range1 = getFloatCommand(
                variogram, 'MainRange', 'Vario', minValue=0.0, modelFile=self.__modelFileName
            )

            range2 = getFloatCommand(
                variogram, 'PerpRange', 'Vario', minValue=0.0, modelFile=self.__modelFileName
            )

            range3 = getFloatCommand(
                variogram, 'VertRange', 'Vario', minValue=0.0, modelFile=self.__modelFileName
            )

            azimuth = getFloatCommand(
                variogram, 'AzimuthAngle', 'Vario',
                minValue=self.__minValue['AzimuthAngle'],
                maxValue=self.__maxValue['AzimuthAngle'],
                modelFile=self.__modelFileName
            )

            dip = getFloatCommand(
                variogram, 'DipAngle', 'Vario',
                minValue=self.__minValue['DipAngle'],
                maxValue=self.__maxValue['DipAngle'],
                modelFile=self.__modelFileName
            )

            power = 1.0
            if variogramType == 'GENERAL_EXPONENTIAL':
                power = getFloatCommand(
                    variogram, 'Power', 'Vario',
                    minValue=self.__minValue['Power'],
                    maxValue=self.__maxValue['Power'],
                    modelFile=self.__modelFileName
                )

            # Read trend model for current GF
            trendObjXML = gf.find('Trend')
            trendRuleModelObj = None
            useTrend = 0
            relStdDev = 0.0
            if trendObjXML is not None:
                if self.__debug_level >= Debug.VERY_VERBOSE:
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
                    trendRuleModelObj = Trend3D_linear_model(trendObjXML, self.__debug_level, self.__modelFileName)
                else:
                    raise NameError(
                        'Error in {className}\n'
                        'Error: Specified name of trend function {trendName} is not implemented.'
                        ''.format(className=self.__className, trendName=trendName)
                    )
            else:
                if self.__debug_level >= Debug.VERY_VERBOSE:
                    print('Debug output: No trend is specified')
                useTrend = 0
                trendRuleModelObj = None
                relStdDev = 0

            # Read RelstdDev
            if useTrend == 1:
                relStdDev = getFloatCommand(
                    gf, 'RelStdDev', 'GaussField', 0.0,
                    modelFile=self.__modelFileName
                )

            # Read preview seed for current GF
            seed = getIntCommand(gf, 'SeedForPreview', 'GaussField', modelFile=self.__modelFileName)
            item = [gfName, seed]

            # Add gauss field parameters to data structure
            self.updateGaussFieldParam(
                gfName, variogramType, range1, range2, range3, azimuth,
                dip, power, useTrend, relStdDev, trendRuleModelObj
            )
            # Set preview simulation start seed for gauss field
            self.setSeedForPreviewSimulation(gfName, seed)

        # End loop over gauss fields for current zone model

        if self.__variogramForGFModel is None:
            raise NameError(
                'Error when reading model file: {modelName}\n'
                'Error: Missing keyword GaussField under '
                'keyword Zone'
                ''.format(modelName=self.__modelFileName)
            )

        if self.__debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: Gauss field variogram parameter for current zone model:')
            print(repr(self.__variogramForGFModel))

            print('Debug output:Gauss field trend parameter for current zone model:')
            print(repr(self.__trendForGFModel))

            print('Debug output: Gauss field preview seed for current zone model:')
            print(repr(self.__seedForPreviewForGFModel))

    def initialize(self, inputZoneNumber, mainFaciesTable, gaussFieldJobs,
                   gaussModelList, trendModelList,
                   simBoxThickness, previewSeedList, debug_level=Debug.OFF):

        if debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: Call the initialize function in ' + self.__className)

        # Set default values
        self.__setEmpty()

        GNAME = self.__index_variogram['Name']
        GTYPE = self.__index_variogram['Type']
        GRANGE1 = self.__index_variogram['MainRange']
        GRANGE2 = self.__index_variogram['PerpRange']
        GRANGE3 = self.__index_variogram['VertRange']
        GAZIMUTH = self.__index_variogram['AzimuthAngle']
        GDIP = self.__index_variogram['DipAngle']
        GPOWER = self.__index_variogram['Power']

        TNAME = self.__index_trend['Name']
        TUSE = self.__index_trend['Use trend']
        TOBJ = self.__index_trend['Object']
        TSTD = self.__index_trend['RelStdev']

        SNAME = self.__index_seed['Name']
        SVALUE = self.__index_seed['Seed']

        self.__zoneNumber = inputZoneNumber
        self.__debug_level = debug_level
        self.__simBoxThickness = simBoxThickness
        self.__mainFaciesTable = mainFaciesTable

        # gaussModelList  = list of objects of the form: [gfName,type,range1,range2,range3,azimuth,dip,power]
        # trendModelList  = list of objects of the form: [gfName,useTrend,trendRuleModelObj,relStdDev]
        # previewSeedList = list of objects of the form: [gfName,seedValue]
        assert len(trendModelList) == len(gaussModelList)
        for i in range(len(gaussModelList)):
            item = gaussModelList[i]
            if len(item) != len(self.__index_variogram):
                raise ValueError('Programming error: Input list items in gausModelList is not of correct length')
            trendItem = trendModelList[i]
            seedItem = previewSeedList[i]
            assert item[GNAME] == trendItem[TNAME]
            assert item[GNAME] == seedItem[SNAME]

            gfName = item[GNAME]
            if not gaussFieldJobs.checkGaussFieldName(gfName):
                raise ValueError(
                    'In zone number: {0} in command GaussField. '
                    'Specified name of Gauss field:  {1} is not defined in any of '
                    'the specified gauss field simulation jobs'
                    ''.format(str(self.__zoneNumber), gfName)
                )

            variogramType = item[GTYPE]
            if not self.__isVariogramTypeOK(variogramType):
                raise ValueError(
                    'In initialize function for {0} in zone number: {1}. '
                    'Specified variogram type: {2} is not defined.'
                    ''.format(self.__className, self.__zoneNumber, variogramType)
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
            self.updateGaussFieldParam(
                gfName=gfName,
                variogramType=variogramType,
                range1=range1,
                range2=range2,
                range3=range3,
                azimuth=azimuth,
                dip=dip,
                power=power
            )

            # Set trend model parameters for this gauss field
            self.updateGaussFieldTrendParam(
                gfName=gfName,
                useTrend=useTrend,
                trendRuleModelObj=trendRuleModelObj,
                relStdDev=relStdDev
            )

            # Set preview simulation start seed for gauss field
            self.setSeedForPreviewSimulation(gfName=gfName, seed=seed)

    def getNGaussFields(self):
        return len(self.__variogramForGFModel)

    @staticmethod
    def __isVariogramTypeOK(variogramType):
        isOK = 0
        if variogramType == 'SPHERICAL':
            isOK = 1
        elif variogramType == 'EXPONENTIAL':
            isOK = 1
        elif variogramType == 'GAUSSIAN':
            isOK = 1
        elif variogramType == 'GENERAL_EXPONENTIAL':
            isOK = 1
        if isOK == 0:
            print('Error: Specified variogram : ' + variogramType + ' is not implemented')
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
        GNAME = self.__index_variogram['Name']
        nGF = len(self.__variogramForGFModel)
        for i in range(nGF):
            item = self.__variogramForGFModel[i]
            name = item[GNAME]
            gfNames.append(name)
        return gfNames

    def findGaussFieldParameterItem(self, gaussFieldName):
        GNAME = self.__index_variogram['Name']
        nGF = len(self.__variogramForGFModel)
        found = False
        itemWithParameters = None
        for i in range(nGF):
            item = self.__variogramForGFModel[i]
            name = item[GNAME]
            if name == gaussFieldName:
                itemWithParameters = item
                found = True
                break
        if not found:
            raise ValueError('Variogram data for gauss field name: {} is not found.'.format(gaussFieldName))
        return itemWithParameters

    def getVariogramType(self, gaussFieldName):
        GTYPE = self.__index_variogram['Type']
        item = self.findGaussFieldParameterItem(gaussFieldName)
        variogramType = item[GTYPE]
        return variogramType

    def getVariogramTypeNumber(self, gaussFieldName):
        variogramType = self.getVariogramType(gaussFieldName)
        variogramTypeNumber = self.__variogramTypeNumber[variogramType]
        return variogramTypeNumber

    def getMainRange(self, gaussFieldName):
        GRANGE1 = self.__index_variogram['MainRange']
        item = self.findGaussFieldParameterItem(gaussFieldName)
        r = item[GRANGE1]
        return r

    def getPerpRange(self, gaussFieldName):
        GRANGE2 = self.__index_variogram['PerpRange']
        item = self.findGaussFieldParameterItem(gaussFieldName)
        r = item[GRANGE2]
        return r

    def getVertRange(self, gaussFieldName):
        GRANGE3 = self.__index_variogram['VertRange']
        item = self.findGaussFieldParameterItem(gaussFieldName)
        r = item[GRANGE3]
        return r

    def getAnisotropyAzimuthAngle(self, gaussFieldName):
        GAZIMUTH = self.__index_variogram['AzimuthAngle']
        item = self.findGaussFieldParameterItem(gaussFieldName)
        r = item[GAZIMUTH]
        return r

    def getAnisotropyDipAngle(self, gaussFieldName):
        GDIP = self.__index_variogram['DipAngle']
        item = self.findGaussFieldParameterItem(gaussFieldName)
        r = item[GDIP]
        return r

    def getPower(self, gaussFieldName):
        GPOWER = self.__index_variogram['Power']
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

    def get_debug_level(self):
        return self.__debug_level

    def __getGFIndex(self, gfName):
        GNAME = self.__index_variogram['Name']

        indx = -1
        for i in range(len(self.__variogramForGFModel)):
            item = self.__variogramForGFModel[i]
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
        maxValue = 0.0
        if checkMax:
            maxValue = self.__maxValue[variableName]

        # index to where the variable is located in the __varioFORGFModel
        variableIndex = self.__index_variogram[variableName]

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
                item = self.__variogramForGFModel[indx]
                item[variableIndex] = value
            else:
                err = 1
        return err

    def setVariogramType(self, gaussFieldName, variogramType):
        GTYPE = self.__index_variogram['Type']
        err = 0
        if self.__isVariogramTypeOK(variogramType):
            gfList = self.getUsedGaussFieldNames()
            if gaussFieldName in gfList:
                indx = self.__getGFIndex(gaussFieldName)
                item = self.__variogramForGFModel[indx]
                item[GTYPE] = variogramType
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

    def updateGaussFieldParam(
            self, gfName, variogramType, range1, range2, range3, azimuth, dip, power,
            useTrend=0, relStdDev=0.0, trendRuleModelObj=None
    ):
        # Update or create new gauss field parameter object (with trend)
        GNAME = self.__index_variogram['Name']
        err = 0
        found = 0
        if not self.__isVariogramTypeOK(variogramType):
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
        if variogramType == 'GENERAL_EXPONENTIAL':
            if power < 1.0 or power > 2.0:
                print('Error in ' + self.__className + ' in ' + 'updateGaussFieldParam')
                raise ValueError('Exponent in GENERAL_EXPONENTIAL variogram is outside [1.0,2.0]')
        if relStdDev < 0.0:
            print('Error in ' + self.__className + ' in ' + 'updateGaussFieldParam')
            raise ValueError('Relative standard deviation used when trends are specified is negative.')

        # Check if gauss field is already defined, then update parameters or create new
        for item in self.__variogramForGFModel:
            name = item[GNAME]
            if name == gfName:
                self.updateGaussFieldVariogramParameters(gfName, variogramType, range1, range2, range3, azimuth, dip, power)
                self.updateGaussFieldTrendParam(gfName, useTrend, trendRuleModelObj, relStdDev)
                found = 1
                break
        if found == 0:
            # Create data for a new gauss field for both variogram  data and trend data
            # But data for trend parameters must be set by another function and default is set here.
            itemVario = [gfName, variogramType, range1, range2, range3, azimuth, dip, power]
            self.__variogramForGFModel.append(itemVario)
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

    def updateGaussFieldVariogramParameters(self, gfName, variogramType, range1, range2, range3, azimuth, dip, power):
        # Update gauss field variogram parameters for existing gauss field model
        # But it does not create new object.
        GNAME = self.__index_variogram['Name']
        GTYPE = self.__index_variogram['Type']
        GRANGE1 = self.__index_variogram['MainRange']
        GRANGE2 = self.__index_variogram['PerpRange']
        GRANGE3 = self.__index_variogram['VertRange']
        GAZIMUTH = self.__index_variogram['AzimuthAngle']
        GDIP = self.__index_variogram['DipAngle']
        GPOWER = self.__index_variogram['Power']

        err = 0
        found = 0
        # Check that gauss field is already defined, then update parameters.
        for item in self.__variogramForGFModel:
            name = item[GNAME]
            if name == gfName:
                found = 1
                item[GTYPE] = variogramType
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
        GNAME = self.__index_variogram['Name']
        indx = -1
        for i in range(len(self.__variogramForGFModel)):
            item = self.__variogramForGFModel[i]
            name = item[GNAME]
            if name == gfName:
                indx = i
                break
        if indx != -1:
            # Remove from list
            self.__variogramForGFModel.pop(indx)
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
        if trendRuleModelObj is None:
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
        GNAME = self.__index_variogram['Name']
        GTYPE = self.__index_variogram['Type']
        GRANGE1 = self.__index_variogram['MainRange']
        GRANGE2 = self.__index_variogram['PerpRange']
        GRANGE3 = self.__index_variogram['VertRange']
        GAZIMUTH = self.__index_variogram['AzimuthAngle']
        GDIP = self.__index_variogram['DipAngle']
        GPOWER = self.__index_variogram['Power']

        TNAME = self.__index_trend['Name']
        TUSE = self.__index_trend['Use trend']
        TOBJ = self.__index_trend['Object']
        TSTD = self.__index_trend['RelStdev']

        SNAME = self.__index_seed['Name']
        SVALUE = self.__index_seed['Seed']

        if self.__debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: call XMLADDElement from ' + self.__className)

        # Add child command GaussField
        nGaussFieldsForModel = len(self.__variogramForGFModel)
        for i in range(nGaussFieldsForModel):
            gfName = self.__variogramForGFModel[i][GNAME]
            variogramType = self.__variogramForGFModel[i][GTYPE]
            range1 = self.__variogramForGFModel[i][GRANGE1]
            range2 = self.__variogramForGFModel[i][GRANGE2]
            range3 = self.__variogramForGFModel[i][GRANGE3]
            azimuth = self.__variogramForGFModel[i][GAZIMUTH]
            dip = self.__variogramForGFModel[i][GDIP]
            power = self.__variogramForGFModel[i][GPOWER]

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
            attribute = {'name': variogramType}
            elem = Element(tag, attribute)
            gfElement.append(elem)
            variogramElement = elem
            tag = self.__xml_keyword['MainRange']
            elem = Element(tag)
            elem.text = ' ' + str(range1) + ' '
            variogramElement.append(elem)
            tag = self.__xml_keyword['PerpRange']
            elem = Element(tag)
            elem.text = ' ' + str(range2) + ' '
            variogramElement.append(elem)
            tag = self.__xml_keyword['VertRange']
            elem = Element(tag)
            elem.text = ' ' + str(range3) + ' '
            variogramElement.append(elem)
            tag = self.__xml_keyword['AzimuthAngle']
            elem = Element(tag)
            elem.text = ' ' + str(azimuth) + ' '
            variogramElement.append(elem)
            tag = self.__xml_keyword['DipAngle']
            elem = Element(tag)
            elem.text = ' ' + str(dip) + ' '
            variogramElement.append(elem)
            if variogramType == 'GENERAL_EXPONENTIAL':
                tag = self.__xml_keyword['Power']
                elem = Element(tag)
                elem.text = ' ' + str(power) + ' '
                variogramElement.append(elem)

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



    def simGaussFieldWithTrendAndTransform(self, nGaussFields,
                                           simBoxXsize, simBoxYsize, simBoxZsize,
                                           gridNX, gridNY, gridNZ,
                                           gridAzimuthAngle, crossSectionType, crossSectionIndx):
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
            assert crossSectionIndx >= 0 and crossSectionIndx < gridNZ
#            crossSectionIndx = int(gridNZ / 2)
            projection = 'xy'
        elif crossSectionType == 'IK':
            gridDim1 = gridNX
            gridDim2 = gridNZ
            size1 = simBoxXsize
            size2 = simBoxZsize
            assert crossSectionIndx >= 0 and crossSectionIndx < gridNY
#            crossSectionIndx = int(gridNY / 2)
            projection = 'xz'
        elif crossSectionType == 'JK':
            gridDim1 = gridNY
            gridDim2 = gridNZ
            size1 = simBoxYsize
            size2 = simBoxZsize
            assert crossSectionIndx >= 0 and crossSectionIndx < gridNX
#            crossSectionIndx = int(gridNX / 2)
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
            varigramoType = self.getVariogramType(name)
            variogramTypeNumber = self.getVariogramTypeNumber(name)
            mainRange = self.getMainRange(name)
            perpRange = self.getPerpRange(name)
            vertRange = self.getVertRange(name)
            azimuthVariogram = self.getAnisotropyAzimuthAngle(name)
            dipVariogram = self.getAnisotropyDipAngle(name)
            power = self.getPower(name)
            if self.__debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: Within simGaussFieldWithTrendAndTransformNew')
                print('Debug output: Simulate gauss field: ' + name)
                print('Debug output: VariogramType: ' + str(varigramoType))
                print('Debug output: VariogramTypeNumber: ' + str(variogramTypeNumber))
                print('Debug output: Azimuth angle for Main range direction: ' + str(azimuthVariogram))
                print('Debug output: Dip angle for Main range direction: ' + str(dipVariogram))

                if variogramTypeNumber == 4:
                    print('Debug output: Power    : ' + str(power))

                print('Debug output: Seed value: ' + str(seedValue))

            # Calculate 2D projection of the correlation ellipsoid
            [angle1, range1, angle2, range2] = self.calc2DVariogramFrom3DVariogram(name, gridAzimuthAngle, projection)
            azimuthVariogram = angle1
            if self.__debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: Range1 in projection: ' + projection + ' : ' + str(range1))
                print('Debug output: Range2 in projection: ' + projection + ' : ' + str(range2))
                print('Debug output: Angle from vertical axis for Range1 direction: ' + str(angle1))
                print('Debug output: Angle from vertical axis for Range2 direction: ' + str(angle2))

            residualField = simGaussField(seedValue, gridDim1, gridDim2, size1, size2,
                                          variogramTypeNumber, range1, range2,
                                          azimuthVariogram, power,
                                          self.__debug_level)

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
        if self.__debug_level >= Debug.VERY_VERBOSE:
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
        if self.__debug_level >= Debug.VERY_VERBOSE:
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

    def calc2DVariogramFrom3DVariogram(self, gaussFieldName, gridAzimuthAngle, projection):
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
        funcName = 'calc2DVariogramFrom3DVariogram'
        if self.__debug_level >= Debug.VERY_VERBOSE:
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
        if self.__debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: M:')
            print(M)
            print(' ')
        # calculate eigenvalues and rotation angle in any of the projections xy,xz,yz
        # Let U be the 2x2 matrix in the projection (where row and column corresponding to 
        # the coordinate that is set to 0 is removed
        if projection == 'xy':
            U = np.array([
                [M[0, 0], M[0, 1]],
                [M[0, 1], M[1, 1]]
            ])
        elif projection == 'xz':
            U = np.array([
                [M[0, 0], M[0, 2]],
                [M[0, 2], M[2, 2]]
            ])
        elif projection == 'yz':
            U = np.array([
                [M[1, 1], M[1, 2]],
                [M[1, 2], M[2, 2]]
            ])
        else:
            raise ValueError('Unknown projection for calculation of 2D variogram ellipse from 3D variogram ellipsoid')
        # angles are azimuth angles (Measured from 2nd axis clockwise)
        [angle1, range1, angle2, range2] = self.__calcProjection(U)

        return [angle1, range1, angle2, range2]

    def __calcProjection(self, U):
        funcName = '__calcProjection'
        if self.__debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: U:')
            print(U)
        w, v = np.linalg.eigh(U)
        if self.__debug_level >= Debug.VERY_VERBOSE:
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
        if self.__debug_level >= Debug.VERY_VERBOSE:
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
        if self.__debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: Function: {funcName} Direction (angle): {angle} for range: {range}'
                  ''.format(funcName=funcName, angle=str(angle2), range=str(range2)))

        # Angles are azimuth angles
        return [angle1, range1, angle2, range2]
