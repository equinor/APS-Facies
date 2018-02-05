#!/bin/env python
import numpy as np
import importlib
from xml.etree.ElementTree import Element

import src.Trend3D
#import src.simGauss2D
import src.simGauss2D_nrlib
import src.utils.xml

#importlib.reload(src.simGauss2D)
importlib.reload(src.simGauss2D_nrlib)
importlib.reload(src.utils.xml)
importlib.reload(src.Trend3D)

#from src.simGauss2D import simGaussField
from src.simGauss2D_nrlib import simGaussField
from src.utils.constants.simple import Debug, VariogramType
from src.utils.xml import getKeyword, getFloatCommand, getIntCommand
from src.utils.checks import isVariogramTypeOK
from src.Trend3D import Trend3D_linear, Trend3D_elliptic, Trend3D_hyperbolic, Trend3D_rms_param, Trend3D_elliptic_cone

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
    def getTrendModel(self,gfName)
    def getTrendModelObject(self,gfName)
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
                              useTrend=0,relStdDev=0.0,trendModelObj=None)
    def updateGaussFieldVariogramParam(self,gfName,variogramType,range1,range2,range3,azimuth,dip,power)
    def removeGaussFieldParam(self,gfName)
    def updateGaussFieldTrendParam(self,gfName,useTrend,trendModelObj,relStdDev)
    def XMLAddElement(self,parent)
    def simGaussFieldWithTrendAndTransform(self,nGaussFields,gridDimNx,gridDimNy,
                                           gridXSize,gridYSize,gridAzimuthAngle,previewCrossSection)

    Private functions:
    def __setEmpty(self)
    def __interpretXMLTree(ET_Tree_zone)
    def __isVariogramTypeOK(self,variogramType)
    def __getGFIndex(self,gfName)
    """

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

    def __setEmpty(self):

        # Dictionary give xml keyword for each variable
        self.__xml_keyword = {
            'MainRange': 'MainRange',
            'PerpRange': 'PerpRange',
            'VertRange': 'VertRange',
            'AzimuthAngle': 'AzimuthAngle',
            'DipAngle': 'DipAngle',
            'Power': 'Power'
        }

        # Dictionary give name to each index in __varioForGFModel list
        # item in list: [name,type,range1,range2,range3,azimuth,dip,power]
        self.__index_variogram = {
            'Name': 0,
            'Type': 1,
            'MainRange': 2,
            'PerpRange': 3,
            'VertRange': 4,
            'AzimuthAngle': 5,
            'DipAngle': 6,
            'Power': 7
        }
        # Dictionary give name to each index in __trendForGFModel list
        # item in list: [name,useTrend,trendModelObj,relStdDev]
        self.__index_trend = {
            'Name': 0,
            'Use trend': 1,
            'Object': 2,
            'RelStdev': 3
        }
        # Dictionaries of legal value ranges for gauss field parameters
        self.__minValue = {
            'MainRange': 0.0,
            'PerpRange': 0.0,
            'VertRange': 0.0,
            'AzimuthAngle': 0.0,
            'DipAngle': 0.0,
            'Power': 1.0
        }
        self.__maxValue = {
            'AzimuthAngle': 360.0,
            'DipAngle': 90.0,
            'Power': 2.0
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

    def __interpretXMLTree(self, ET_Tree_zone, gaussFieldJobs):
        """
        Description: Read Gauss field models for current zone. 
        Read trend models for the same gauss fields and start seed for 2D preview simulations. 
        """
        for gf in ET_Tree_zone.findall('GaussField'):
            gfName = gf.get('name')
            if self.__debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: Gauss field name: {}'.format(gfName))
            if not gaussFieldJobs.checkGaussFieldName(gfName):
                raise ValueError(
                    'In model file {0} in zone number: {1} in command GaussField.\n'
                    'Specified name of Gauss field:  {2} is not defined in any of '
                    'the specified gauss field simulation jobs'
                    ''.format(self.__modelFileName, str(self.__zoneNumber), gfName)
                )

            # Read variogram for current GF
            variogram, variogramType = self.get_variogram(gf, gfName)

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
            if variogramType == VariogramType.GENERAL_EXPONENTIAL:
                power = getFloatCommand(
                    variogram, 'Power', 'Vario',
                    minValue=self.__minValue['Power'],
                    maxValue=self.__maxValue['Power'],
                    modelFile=self.__modelFileName
                )

            # Read trend model for current GF
            trendObjXML = gf.find('Trend')
            trendModelObj = None
            useTrend = False
            relStdDev = 0.0
            if trendObjXML is not None:
                if self.__debug_level >= Debug.VERY_VERBOSE:
                    print('Debug output: Read trend')
                useTrend = True

                if self.__simBoxThickness <= 0.0:
                    raise ValueError(
                        'In model file {0} in keyword Trend for gauss field name: {1}\n'
                        'The use of trend functions requires that simulation box thickness is specified.\n'
                        ''.format(self.__modelFileName, gfName, self.__className)
                    )
                trendName = trendObjXML.get('name')
                if trendName == 'Linear3D':
                    trendModelObj = Trend3D_linear(trendObjXML, modelFileName=self.__modelFileName,
                                                   debug_level=self.__debug_level)
                elif trendName == 'Elliptic3D':
                    trendModelObj = Trend3D_elliptic(trendObjXML, modelFileName=self.__modelFileName, debug_level=self.__debug_level)
                elif trendName == 'Hyperbolic3D':
                    trendModelObj = Trend3D_hyperbolic(trendObjXML, modelFileName=self.__modelFileName, debug_level=self.__debug_level)
                elif trendName == 'RMSParameter':
                    trendModelObj = Trend3D_rms_param(trendObjXML, modelFileName=self.__modelFileName, debug_level=self.__debug_level)
                elif trendName == 'EllipticCone3D':
                    trendModelObj = Trend3D_elliptic_cone(trendObjXML, modelFileName=self.__modelFileName, debug_level=self.__debug_level)
                else:
                    raise NameError(
                        'Error in {className}\n'
                        'Error: Specified name of trend function {trendName} is not implemented.'
                        ''.format(className=self.__className, trendName=trendName)
                    )
            else:
                if self.__debug_level >= Debug.VERY_VERBOSE:
                    print('Debug output: No trend is specified')
                useTrend = False
                trendModelObj = None
                relStdDev = 0

            # Read RelstdDev
            if useTrend == True:
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
                dip, power, useTrend, relStdDev, trendModelObj
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

    def get_variogram(self, gf, gfName):
        variogram = getKeyword(gf, 'Vario', 'GaussField', modelFile=self.__modelFileName)
        variogramType = self.get_variogram_type(variogram)
        if not isVariogramTypeOK(variogramType):
            raise ValueError(
                'In model file {0} in zone number: {1} in command Vario for gauss field {2}.\n'
                'Specified variogram type is not defined.'
                ''.format(self.__modelFileName, self.__zoneNumber, gfName)
            )
        return variogram, variogramType

    @staticmethod
    def get_variogram_type(variogram) -> VariogramType:
        if isinstance(variogram, str):
            name = variogram
        elif isinstance(variogram, Element):
            name = variogram.get('name')
        elif isinstance(variogram, VariogramType):
            return variogram
        else:
            raise ValueError('Unknown type: {}'.format(str(variogram)))
        nameUpper = name.upper()
        if nameUpper == 'SPHERICAL':
            return VariogramType.SPHERICAL
        elif nameUpper == 'EXPONENTIAL':
            return VariogramType.EXPONENTIAL
        elif nameUpper == 'GAUSSIAN':
            return VariogramType.GAUSSIAN
        elif nameUpper == 'GENERAL_EXPONENTIAL':
            return VariogramType.GENERAL_EXPONENTIAL
        elif nameUpper == 'MATERN32':
            return VariogramType.MATERN32
        elif nameUpper == 'MATERN52':
            return VariogramType.MATERN52
        elif nameUpper == 'MATERN72':
            return VariogramType.MATERN72
        elif nameUpper == 'CONSTANT':
            return VariogramType.CONSTANT
        else:
            raise ValueError('Error: Unknown variogram type {}'.format(nameUpper))

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
        # trendModelList  = list of objects of the form: [gfName,useTrend,trendModelObj,relStdDev]
        # previewSeedList = list of objects of the form: [gfName,seedValue]
        assert len(trendModelList) == len(gaussModelList)
        for i in range(len(gaussModelList)):
            item = gaussModelList[i]
            if len(item) != len(self.__index_variogram):
                raise ValueError('Programming error: Input list items in gaussModelList is not of correct length')
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

            variogramType = self.get_variogram_type(item[GTYPE])
            if not isVariogramTypeOK(variogramType):
                raise ValueError(
                    'In initialize function for {0} in zone number: {1} for gauss field: {2}. '
                    'Specified variogram type: {3} is not defined.'
                    ''.format(self.__className, self.__zoneNumber, gfName, variogramType.name)
                )
            range1 = item[GRANGE1]
            range2 = item[GRANGE2]
            range3 = item[GRANGE3]
            azimuth = item[GAZIMUTH]
            dip = item[GDIP]
            power = item[GPOWER]

            trendModelObj = trendItem[TOBJ]
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
                trendModelObj=trendModelObj,
                relStdDev=relStdDev
            )

            # Set preview simulation start seed for gauss field
            self.setSeedForPreviewSimulation(gfName=gfName, seed=seed)

    def getNGaussFields(self):
        return len(self.__variogramForGFModel)

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
        variogramType = self.get_variogram_type(item[GTYPE])
        return variogramType

    def getVariogramTypeNumber(self, gaussFieldName):
        variogramType = self.getVariogramType(gaussFieldName)
        variogramTypeNumber = variogramType.value
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

    def getTrendItem(self, gfName):
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

    def getTrendModel(self, gfName):
        TUSE = self.__index_trend['Use trend']
        TOBJ = self.__index_trend['Object']
        TSTD = self.__index_trend['RelStdev']
        item = self.getTrendItem(gfName)
        if item is None:
            return None, None, None
        else:
            useTrend = item[TUSE]
            trendModelObj = item[TOBJ]
            relStdDev = item[TSTD]
            return useTrend, trendModelObj, relStdDev

    def getTrendModelObject(self, gfName):
        TOBJ = self.__index_trend['Object']
        item = self.getTrendItem(gfName)
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
        if isVariogramTypeOK(variogramType):
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
            useTrend=False, relStdDev=0.0, trendModelObj=None
    ):
        # Update or create new gauss field parameter object (with trend)
        GNAME = self.__index_variogram['Name']
        err = 0
        found = 0
        if not isVariogramTypeOK(variogramType):
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
        if variogramType == VariogramType.GENERAL_EXPONENTIAL:
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
                self.updateGaussFieldVariogramParameters(
                    gfName, variogramType, range1, range2, range3, azimuth, dip, power
                )
                self.updateGaussFieldTrendParam(gfName, useTrend, trendModelObj, relStdDev)
                found = 1
                break
        if found == 0:
            # Create data for a new gauss field for both variogram  data and trend data
            # But data for trend parameters must be set by another function and default is set here.
            itemVariogram = [gfName, variogramType.name, range1, range2, range3, azimuth, dip, power]
            self.__variogramForGFModel.append(itemVariogram)
            if trendModelObj is None:
                useTrend = False
                relStdDev = 0.0
            else:
                useTrend = True
            itemTrend = [gfName, useTrend, trendModelObj, relStdDev]
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
                item[GTYPE] = variogramType.name
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

    def updateGaussFieldTrendParam(self, gfName, useTrend, trendModelObj, relStdDev):
        # Update trend parameters for existing trend for gauss field model
        # But it does not create new trend object.
        TNAME = self.__index_trend['Name']
        TUSE = self.__index_trend['Use trend']
        TOBJ = self.__index_trend['Object']
        TSTD = self.__index_trend['RelStdev']
        err = 0
        if trendModelObj is None:
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
                    item[TOBJ] = trendModelObj
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
                raise ValueError('Error in class: ' + self.__className + ' in ' + 'XMLAddElement')
            useTrend = self.__trendForGFModel[i][TUSE]
            trendObj = self.__trendForGFModel[i][TOBJ]
            relStdDev = self.__trendForGFModel[i][TSTD]

            tag = 'GaussField'
            attribute = {'name': gfName}
            elem = Element(tag, attribute)
            parent.append(elem)
            gfElement = elem

            tag = 'Vario'
            attribute = {'name': variogramType if isinstance(variogramType, str) else variogramType.name}
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

            if variogramType in ['GENERAL_EXPONENTIAL', VariogramType.GENERAL_EXPONENTIAL]:
                tag = self.__xml_keyword['Power']
                elem = Element(tag)
                elem.text = ' ' + str(power) + ' '
                variogramElement.append(elem)

            if useTrend == True:
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

    def simGaussFieldWithTrendAndTransform(
            self, simBoxXsize, simBoxYsize, simBoxZsize,
            gridNX, gridNY, gridNZ, gridAzimuthAngle, crossSectionType, crossSectionRelativePos
    ):
        TUSE = self.__index_trend['Use trend']
        TOBJ = self.__index_trend['Object']
        TSTD = self.__index_trend['RelStdev']
        SVALUE = self.__index_seed['Seed']

        assert 0 <= crossSectionRelativePos <= 1.0
        if crossSectionType == 'IJ':
            gridDim1 = gridNX
            gridDim2 = gridNY
            size1 = simBoxXsize
            size2 = simBoxYsize
            projection = 'xy'
        elif crossSectionType == 'IK':
            gridDim1 = gridNX
            gridDim2 = gridNZ
            size1 = simBoxXsize
            size2 = simBoxZsize
            projection = 'xz'
        elif crossSectionType == 'JK':
            gridDim1 = gridNY
            gridDim2 = gridNZ
            size1 = simBoxYsize
            size2 = simBoxZsize
            projection = 'yz'
        else:
            raise ValueError('Undefined cross section {}'.format(crossSectionType))

        gaussFieldNamesInModel = self.getUsedGaussFieldNames()
        nGaussFields = len(gaussFieldNamesInModel)
        gaussFieldItems = []
        for i in range(nGaussFields):
            # Find data for specified Gauss field name
            name = gaussFieldNamesInModel[i]
            seedValue = self.__seedForPreviewForGFModel[i][SVALUE]
            variogramType = self.getVariogramType(name)
            variogramTypeNumber = self.getVariogramTypeNumber(name)
            mainRange = self.getMainRange(name)
            perpRange = self.getPerpRange(name)
            vertRange = self.getVertRange(name)
            azimuthVariogram = self.getAnisotropyAzimuthAngle(name)
            dipVariogram = self.getAnisotropyDipAngle(name)
            power = self.getPower(name)
            if self.__debug_level >= Debug.VERY_VERBOSE:
                print(' ')
                print('Debug output: Within simGaussFieldWithTrendAndTransform')
                print('Debug output: Simulate gauss field: ' + name)
                print('Debug output: VariogramType: ' + str(variogramType))
                print('Debug output: Azimuth angle for Main range direction: ' + str(azimuthVariogram))
                print('Debug output: Azimuth angle for grid: ' + str(gridAzimuthAngle))
                print('Debug output: Dip angle for Main range direction: ' + str(dipVariogram))

                if variogramType == VariogramType.GENERAL_EXPONENTIAL:
                    print('Debug output: Power    : ' + str(power))

                print('Debug output: Seed value: ' + str(seedValue))

            # Calculate 2D projection of the correlation ellipsoid
            [angle1, range1, angle2, range2] = self.calc2DVariogramFrom3DVariogram(name, gridAzimuthAngle, projection)
            azimuthVariogram = angle1
            if self.__debug_level >= Debug.VERY_VERBOSE:
                print(' ')
                print('Debug output: Range1 in projection: ' + projection + ' : ' + str(range1))
                print('Debug output: Range2 in projection: ' + projection + ' : ' + str(range2))
                print('Debug output: Angle from vertical axis for Range1 direction: ' + str(angle1))
                print('Debug output: Angle from vertical axis for Range2 direction: ' + str(angle2))
                print('Debug output: (gridDim1, gridDim2) = ({},{})'.format(str(gridDim1), str(gridDim2)))
                print('Debug output: (Size1, Size2) = ({},  {})'.format(str(size1), str(size2)))

            residualField = simGaussField(
                seedValue, gridDim1, gridDim2, size1, size2, variogramType,
                range1, range2, azimuthVariogram, power, self.__debug_level
            )

            # Calculate trend
            useTrend, trendModelObject, relStdDev = self.getTrendModel(name)
            if useTrend == True:
                if self.__debug_level >= Debug.VERBOSE:
                    print('    - Use Trend: {}'.format(trendModelObject.type.name))
                minMaxDifference, averageTrend, trendField = trendModelObject.createTrendFor2DProjection(
                    simBoxXsize, simBoxYsize, simBoxZsize, gridAzimuthAngle,
                    gridNX, gridNY, gridNZ, crossSectionType, crossSectionRelativePos
                )
                gaussFieldWithTrend = self.__addTrend(
                    residualField, trendField, relStdDev, minMaxDifference, averageTrend
                )
            else:
                gaussFieldWithTrend = residualField

            transField = self.__transformEmpiricDistributionToUniform(gaussFieldWithTrend)
            item = [name, transField]
            gaussFieldItems.append(item)
        # End for        

        return gaussFieldItems

    def __addTrend(self, residualField, trendField, relSigma, trendMaxMinDifference, averageTrend):
        """
        Description: Calculate standard deviation sigma = relSigma * trendMaxMinDifference.
        Add trend and residual field  Field = Trend + sigma*residual
        Input residualField and trendField should be 1D float numpy arrays of same size.
        Return is trend plus residual with correct standard deviation as numpy 1D array.
        """
        # Standard deviation
        if abs(trendMaxMinDifference) == 0.0:
            sigma = relSigma * averageTrend
        else:
            sigma = relSigma * trendMaxMinDifference
        if self.__debug_level >= Debug.VERY_VERBOSE:
            print('Debug output:  Relative standard deviation = ' + str(relSigma))
            print('Debug output:  Difference between max value and min value of trend = ' + str(trendMaxMinDifference))
            print('Debug output:  Calculated standard deviation = ' + str(sigma))
            print(' ')
        n = len(trendField)
        if len(trendField) != len(residualField):
            raise IOError('Internal error: Mismatch between size of trend field and residual field in __addTrend')

        gaussFieldWithTrend = np.zeros(n, np.float32)
        for i in range(n):
            gaussFieldWithTrend[i] = trendField[i] + residualField[i] * sigma
        return gaussFieldWithTrend

    def __transformEmpiricDistributionToUniform(self, inputValues):
        """
        Take input as numpy 1D float array and return numpy 1D float array where
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
        transformedValues = np.zeros(nVal, np.float32)
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
         Then rotate this ellipsoid first around x axis with angle defined as dipAngle in clockwise direction.
         The dip angle is the angle between the y axis and the new rotated y' axis along the main 
         principal direction of the ellopsoide.
         Then rotate the the ellipsoid an angle around the z axis. This is the azimuthAngle. The final orientation
         is then found and the coordinate system defined by the principal directions for the ellipsoide 
         are (x'',y'',z'') in which the M matrix is diagonal.
         Note that the coordinate system (x,y,z) is left handed and z axis is pointing 
         downward compared to a right handed coordinate system.
         To define the matrix M in (x,y,z) coordinate system given that we 
         know its half axes in the principal directions, we need the transformation from column vector of (x,y,z)
         which we call V vector to column vector of (x'',y'',z'') which we call V'':
             V'' =  R_azimuth * R_dip * V   where we call R = R_azimuth * R_dip
         where R_azimuth is the matrix rotating the ellipsoide around z axis an angle = azimuth angle
         and R_dip is the matrix rotating the vector V' = R_azimuth*V around the x axis and angle = dip angle.
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
        azimuth = -azimuth * np.pi / 180.0

        # Dip angle relative to local simulation box
        dip = self.getAnisotropyDipAngle(gaussFieldName)
        dip = -dip * np.pi / 180.0

        cosTheta = np.cos(azimuth)
        sinTheta = np.sin(azimuth)
        cosDip = np.cos(dip)
        sinDip = np.sin(dip)


        # define R_dip matrix
        # R_dip*V will rotate the vector V by the angle dip around the x-axis.
        # The vector [0,1,0] (unit vector in y direction)  will get a positive z component if dip angle is positive
        # (between 0 and 90 degrees).
        # Note that z axis is down and that the (x,y,z) coordinate system is left-handed.
        R_dip = np.array([
            [1.0, 0.0, 0.0],
            [0.0, cosDip, -sinDip],
            [0.0, sinDip, cosDip]
        ])


        # define R_azimuth matrix
        # R_azimuth*V will rotate the vector V by the angle azimuth around the z axis.
        # The vector [0,1,0] (unit vector in y direction) will get positive x component if azimuth angle
        # is positive (between 0 and 180 degrees)
        R_azimuth = np.array([
            [cosTheta, sinTheta, 0.0],
            [-sinTheta, cosTheta, 0.0],
            [0.0, 0.0, 1.0]
        ])

        # The combination R = R_azimuth * R_dip will
        # rotate the vector V first by a dip angle around x axis and then by an azimuth angle around z axis

        # calculate R matrix
        #R = R_azimuth.dot(R_dip)
        R = R_dip.dot(R_azimuth)


        # calculate M matrix in principal coordinates
        M_diag = np.array([
            [1.0 / (rx * rx), 0.0, 0.0],
            [0.0, 1.0 / (ry * ry), 0.0],
            [0.0, 0.0, 1.0 / (rz * rz)]
        ])

        # The M matrix in (x,y,z) coordinates is given by M = transpose(R) * M_diag * R since
        # [x',y',z'] * M_diag * transpose([x',y',z']) = [x,y,z] *transpose(R) * M_diag * R * transpose([x,y,z])
        tmp = M_diag.dot(R)
        Rt = np.transpose(R)
        M = Rt.dot(tmp)
        if self.__debug_level >= Debug.VERY_VERY_VERBOSE:
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
        angle1, range1, angle2, range2 = self.__calcProjection(U)

        return angle1, range1, angle2, range2

    def __calcProjection(self, U):
        funcName = '__calcProjection'
        if self.__debug_level >= Debug.VERY_VERY_VERBOSE:
            print('Debug output: U:')
            print(U)
        w, v = np.linalg.eigh(U)
        if self.__debug_level >= Debug.VERY_VERY_VERBOSE:
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
        if self.__debug_level >= Debug.VERY_VERY_VERBOSE:
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
        if self.__debug_level >= Debug.VERY_VERY_VERBOSE:
            print('Debug output: Function: {funcName} Direction (angle): {angle} for range: {range}'
                  ''.format(funcName=funcName, angle=str(angle2), range=str(range2)))

        # Angles are azimuth angles
        return angle1, range1, angle2, range2
