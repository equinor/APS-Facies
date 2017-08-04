#!/bin/env python
import sys
import copy
import numpy as np

# Functions to draw 2D gaussian fields with linear trend and transformed to unifor distribution
from simGauss2D import  simGaussFieldAddTrendAndTransform 

from Trunc2D_Angle_Overlay_xml import  Trunc2D_Angle_Overlay
from Trunc2D_Cubic_Overlay_xml import  Trunc2D_Cubic_Overlay
from Trunc3D_bayfill_xml import  Trunc3D_bayfill

from Trend3D_linear_model_xml import Trend3D_linear_model

import xml.etree.ElementTree as ET
from  xml.etree.ElementTree import Element, SubElement, dump
from APSMainFaciesTable import APSMainFaciesTable
from APSGaussFieldJobs  import APSGaussFieldJobs

# ----------------------------------------------------------------
# class APSZoneModel
# Description: Keep data structure for a zone
#
# Public member functions:
#   Constructor:  def __init__(self,ET_Tree= None,inputZoneNumber=0,
#                              inputMainLevelFacies=None,modelFileName=None)
#  --- Get functions ---
#    def getZoneNumber(self)
#    def useConstProb(self)
#    def getMainLevelFacies(self)
#    def getFaciesInZoneModel(self)
#    def getUsedGaussFieldNames(self)
#    def getVarioType(self,gaussFieldName)
#    def getVarioTypeNumber(self,gaussFieldName)
#    def getMainRange(self,gaussFieldName)
#    def getPerpRange(self,gaussFieldName)
#    def getVertRange(self,gaussFieldName)
#    def getAnisotropyAsimuthAngle(self,gaussFieldName)
#    def getPower(self,gaussFieldName)
#    def getTruncRule(self)
#    def getTrendRuleModel(self,gfName)
#    def getSimBoxThickness(self)
#    def getTruncationParam(self,get3DParamFunction,gridModel,realNumber)
#    def printInfo(self)
#    def getProbParamName(self,fName)
#    def getAllProbParamForZone(self)
#    def getConstProbValue(self,fName)
#    def getHorizonNameForVarioTrendMap(self)
#
#
#  ---  Set functions ---
#    def setZoneNumber(self,zoneNumber)
#    def setVarioType(self,gaussFieldName,varioType)
#    def setRange1(self,gaussFieldName,range1)
#    def setRange2(self,gaussFieldName,range2)
#    def setRange3(self,gaussFieldName,range3)
#    def setAngle(self,gaussFieldName,angle)
#    def setPower(self,gaussFieldName,power)
#    def setUseConstProb(self)
#    def setSeedForPreviewSimulation(self)
#    def setMainFaciesTable(self,mainFaciesTable)
#    def setSimBoxThickness(self,thickness)
#    def updateGaussFieldParam(self,gfName,varioType,range1,range2,range3,angle,power,
#                              relStdDev=0.0,trendRuleModelObj=None)
#    def removeGaussFieldParam(self,gfName)
#    def updateFaciesWithProbForZone(self,faciesList,faciesProbList)
#    def removeFaciesWithProbForZone(self,fName)
#    def setTruncRule(self,truncRuleObj)
#    def setHorizonNameForVarioTrendMap(self,horizonNameForVarioTrendMap)

#  ---  Calculate function ---
#    def applyTruncations(self,probDefined,GFAlphaList,faciesReal,nDefinedCells,cellIndexDefined)
#    def simGaussFieldWithTrendAndTransform(self,gridDimNx,gridDimNy,gridXSize,gridYSize,gridAsimuthAngle)
#
#
#  ---  write XML tree --- 
#    def XMLAddElement(self,parent)
#
#  --- Check functions ---
#    def hasFacies(self,fName)
#    def isMainLevelModel(self)
#
# Private member functions:
#    def __interpretXMLTree(ET_Tree)
#    def __isVarioTypeOK(self,varioType)
#    def __checkConstProbValuesAndNormalize(self)
#    def __getGFIndex(self,gfName)
#    def __updateGaussFieldVarioParam(self,gfName,varioType,range1,range2,range3,angle,power)
#    def __updateGaussFieldTrendParam(self,gfName,trendRuleModelObj,relStdDev)
#
# ----------------------------------------------------------------
class APSZoneModel:

    def __init__(self,ET_Tree= None,inputZoneNumber=0,inputMainLevelFacies=None,modelFileName=None):
        # Local variables
        self.__printInfo = 0
        self.__useConstProb = 0
        self.__className = 'APSZoneModel'
        self.__modelFileName = modelFileName
        self.__simBoxThickness = 10.0

        # List of facies name in the zone model with associated probability cube names
        # and list of facies names should always be of the same length and kept in sync.
        self.__faciesProbForZoneModel = []
        self.__faciesInZoneModel = []

        # List of gauss field data is split into one list for variogram data and one list for trend data
        # but they should always be of the same length and kept in sync, 
        # but trend data in the list can be disabled.
        self.__trendForGFModel = []
        self.__varioForGFModel = []

        self.__seedForPreviewForGFModel  = []
        self.__mainFaciesTable = None
        self.__truncRule = None
        self.__zoneNumber = inputZoneNumber
        self.__faciesLevel = 1
        self.__mainLevelFacies = inputMainLevelFacies
        self.__horizonNameForVarioTrendMap = None

        # Index values for varioForGFModel list elements
        # item in list: [name,type,range1,range2,range3,angle,power]
        self.__GNAME   = 0 
        self.__GTYPE   = 1
        self.__GRANGE1 = 2
        self.__GRANGE2 = 3
        self.__GRANGE3 = 4
        self.__GANGLE  = 5
        self.__GPOWER  = 6

        # Index values for faciesProbForZoneModel list elements
        # item in list: [name,probName]
        self.__FNAME   = 0
        self.__FPROB   = 1

        # Index values for trendForGFModel  list elements
        # item in list: [name,useTrend,trendRuleModelObj,relStdDev]
        self.__TNAME   = 0
        self.__TUSE    = 1
        self.__TOBJ    = 2
        self.__TSTD    = 3

        # Index values for seedForPreviewForGFModel
        # item in list: [name,value]
        self.__SNAME  = 0
        self.__SVALUE = 1
        
        if ET_Tree == None:
            return

        self.__interpretXMLTree(ET_Tree)
        return
    # End __init__

    def __interpretXMLTree(self,ET_Tree):
        #  Get root of xml tree for model specification
        root = ET_Tree.getroot()

        # --- PrintInfo ---
        kw = 'PrintInfo'
        obj =  root.find(kw)
        if obj == None:
            # Default value is set
            self.__printInfo = 1
        else:
            text = obj.text
            self.__printInfo = int(text.strip())

        if self.__printInfo >= 3:
            print(' ')
            print('Debug output: Call init ' + self.__className)

        mainFaciesTable = APSMainFaciesTable(ET_Tree,self.__modelFileName)
        gaussFieldJobs = APSGaussFieldJobs(ET_Tree,self.__modelFileName)
        self.__mainFaciesTable = mainFaciesTable
        
        err = 0
        zoneModels = root.find('ZoneModels')
        for zone in zoneModels.findall('Zone'):
            zoneNumber      = int(zone.get('number'))
            mainLevelFacies = zone.get('mainLevelFacies')
            if zoneNumber == self.__zoneNumber and mainLevelFacies == self.__mainLevelFacies:
                if mainLevelFacies == None:
                    self.__faciesLevel = 1
                else:
                    self.__faciesLevel = 2
                    
                obj = zone.find('UseConstProb')
                if obj == None:
                    raise NameError(
                        'Error when reading model file: ' + self.__modelFileName +'\n'
                        'Error: Missing keyword UseConstProb under keyword Zone'
                        )
                text = obj.text
                self.__useConstProb    = int(text.strip())

                kw = 'SimBoxThickness'
                obj = zone.find(kw)
                if obj != None:
                    text = obj.text
                    self.__simBoxThickness    = float(text.strip())
                    if self.__simBoxThickness <= 0.0:
                        raise ValueError(
                            'Error in ' + self.__className +'\n'
                            'Error: In keyword: ' + kw+'\n'
                            'Error: Specified 0 or negative simulation box thickness for zone ' + str(zoneNumber)
                            )
                else:
                    raise ValueError(
                        'Error in ' + self.__className + '\n'
                        'Error: Missing keyword: ' + kw + ' in zone number ' + str(zoneNumber)
                        )


                kw = 'HorizonNameVarioTrend'
                refSurfObj = zone.find(kw)
                if refSurfObj == None:
                    print('Warning: Keyword: ' + kw + ' is not specified.')
                    print('Warning: Can not update variogram asimuth angle without using trend maps.')
                else:
                    text = refSurfObj.text
                    self.__horizonNameForVarioTrendMap = copy.copy(text.strip())



                if self.__printInfo >= 3:
                    print('Debug output: From APSZoneModel: ZoneNumber: '+ str(zoneNumber))
                    print('Debug output: From APSZoneModel: mainLevelFacies: ' + str(mainLevelFacies))
                    print('Debug output: From APSZoneModel: useConstProb: ' + str(self.__useConstProb))
                    print('Debug output: From APSZoneModel: simBoxThickness: ' + str(self.__simBoxThickness))
                    text = 'Debug output: From APSZoneModel: Horizon name to be used for saving \n'
                    text = text + '              asimuth variogram trend for this zone: ' 
                    text = text + str(self.__horizonNameForVarioTrendMap) 
                    print(text)

                # Read Facies probability cubes for current zone model
                obj = zone.find('FaciesProbForModel')
                if obj == None:
                    raise NameError(
                        'Error when reading model file: ' + self.__modelFileName + '\n'
                        'Error: Missing keyword FaciesProbForModel under keyword Zone'
                        )

                facForModel = obj

                for f in facForModel.findall('Facies'):
                    text     = f.get('name')
                    name     = text.strip()
                    if mainFaciesTable.checkWithFaciesTable(name):
                        text     = f.find('ProbCube').text
                        probCubeName = text.strip()
                        item = [name,probCubeName]
                        self.__faciesProbForZoneModel.append(item)
                        self.__faciesInZoneModel.append(name)
                    else:
                        raise NameError(
                            'Error in ' + self.__className + '\n'
                            'Error in keyword: FaciesProbForModel. Facies name: ' + name +'\n'
                            '                  is not defined in main facies table in command APSMainFaciesTable'
                            )

                if self.__faciesProbForZoneModel == None:
                    raise NameError(
                        'Error when reading model file: ' + self.__modelFileName + '\n'
                        'Error: Missing keyword Facies under keyword FaciesProbForModel'
                        )

                self.__checkConstProbValuesAndNormalize()


                if self.__printInfo >= 3:
                    print('Debug output: From APSZoneModel: Facies prob for current zone model: ')
                    print(repr(self.__faciesProbForZoneModel))

                # Read Gauss field models for current zone 
                for gf in zone.findall('GaussField'):
                    name   = gf.get('name')
                    if gaussFieldJobs.checkGaussFieldName(name):
                        # Read variogram for current GF
                        vario  = gf.find('Vario')
                        if vario == None:
                            err = 1
                        else:
                            varioType  = vario.get('name')
                            if not self.__isVarioTypeOK(varioType):
                                err = 1

                            obj = vario.find('MainRange')
                            if obj == None:
                                err = 1
                            else:
                                text   = obj.text
                                range1 = float(text.strip())
                            obj = vario.find('PerpRange')
                            if obj == None:
                                err = 1
                            else:
                                text   = obj.text
                                range2 = float(text.strip())
                            obj = vario.find('VertRange')
                            if obj == None:
                                err = 1
                            else:
                                text   = obj.text
                                range3 = float(text.strip())

                            obj = vario.find('Angle')
                            if obj == None:
                                err = 1
                            else:
                                text   = obj.text
                                angle = float(text.strip())

                            power = 1.0
                            if varioType == 'GENERAL_EXPONENTIAL':
                                p = vario.find('Power')
                                if p != None:
                                    text = p.text
                                    power  = float(text.strip())
                                else:
                                    text = 'Error: In class ' + self.__className
                                    text = text + 'Variograms specified as GENERAL_EXPONENTIAL lack specification of exponent'
                                    print(text)
                                    err = 1
                                    power = -999

                        self.__varioForGFModel.append([name,varioType,range1,range2,range3,angle,power])

                        # Read trend model for current GF
                        
                        trendObjXML  = gf.find('Trend')
                        trendRuleModelObj = None
                        if trendObjXML != None:
                            if self.__printInfo >= 3:
                                print('Debug output: Read trend')
                            useTrend = 1


                            if self.__simBoxThickness <= 0.0: 
                                print('Warning when reading model file: ' + self.__modelFileName)
                                print('Warning: Missing keyword SimBoxThickness under keyword Zone')
                                print('Warning: Use a default thickness of 10.0 m')
                                self.__simBoxThickness = 10.0

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
                            kw = 'RelStdDev'
                            relstdObj = gf.find(kw)
                            if relstdObj == None:
                                relStdDev = 0.0
                                raise ValueError(
                                    'Error in ' + self.__className + '\n'
                                    'Error: Missing keyword ' + kw
                                    )
                            else:
                                text    = relstdObj.text 
                                relStdDev = float(text.strip())

                        self.__trendForGFModel.append([name,useTrend,trendRuleModelObj,relStdDev])

                        # Read preview seed for current GF
                        obj     = gf.find('SeedForPreview')
                        if obj != None:
                            text    = obj.text
                            seed = int(text.strip())
                            item = [name,seed]
                            self.__seedForPreviewForGFModel.append(item)
                    else:
                        raise NameError(
                            'Error in ' + self.__className + '\n'
                            'Error in zone: ' + str(zoneNumber) +'\n'
                            'Error: Keyword GaussField has specified non-existing gauss field parameter name: ' + name +'\n'
                            'Error: This parameter name is not specified in command GaussFieldJobs.'
                            )


                # End loop over gauss fields for current zone model
                if self.__varioForGFModel == None:
                    raise NameError(
                        'Error when reading model file: ' + self.__modelFileName + '\n'
                        'Error: Missing keyword GaussField under keyword Zone'
                        )

                if err == 0:
                    if self.__printInfo >= 3:
                        print('Debug output: Gauss field variogram parameter for current zone model:')
                        print(repr(self.__varioForGFModel))

                        print('Debug output:Gauss field trend parameter for current zone model:')
                        print(repr(self.__trendForGFModel))

                        print('Debug output: Gauss field preview seed for current zone model:')
                        print(repr(self.__seedForPreviewForGFModel))
                

                    

                    # Read truncation rule for zone model
                    trRule = zone.find('TruncationRule')
                    if trRule == None:
                        raise NameError(
                            'Error when reading model file: ' + self.__modelFileName +'\n'
                            'Error: Missing keyword TruncationRule under keyword Zone'
                            )
                    truncRuleName = trRule.get('name')
                    if self.__printInfo >= 3:
                        print('Debug output: TruncRuleName: ' + truncRuleName)

                    nGaussFieldInModel  = int(trRule.get('nGFields'))
                    if nGaussFieldInModel != len(self.__varioForGFModel):
                        raise ValueError(
                            'Error: In ' + self.__className + '\n'
                            'Error: Number of specified RMS gaussian field 3D parameters does not match '
                            '       truncation rule: ' + truncRuleName
                            )
                    else:
                        faciesInZone = self.__faciesInZoneModel
                        if truncRuleName == 'Trunc3D_Bayfill':
                            self.__truncRule = Trunc3D_bayfill(trRule,mainFaciesTable,faciesInZone,
                                                               self.__printInfo,self.__modelFileName)


                        elif truncRuleName == 'Trunc2D_Angle_Overlay':
                            self.__truncRule = Trunc2D_Angle_Overlay(trRule,mainFaciesTable,faciesInZone,
                                                                     self.__printInfo,self.__modelFileName)
                    
                        elif truncRuleName == 'Trunc2D_Cubic_Overlay':
                            self.__truncRule = Trunc2D_Cubic_Overlay(trRule,mainFaciesTable,faciesInZone,
                                                                     self.__printInfo,self.__modelFileName)
                        else:
                            raise NameError(
                                'Error in ' + self.__className + '\n'
                                'Error: Specified truncation rule name: ' + truncRuleName +'\n' 
                                '       is not implemented.' 
                                )

                        if self.__printInfo >= 3:
                            text = 'Debug output: APSZoneModel: Truncation rule for current zone: ' 
                            text = text + self.__truncRule.getClassName()
                            print(text)
                            print('Debug output: APSZoneModel: Facies in truncation rule: ')
                            print( repr(self.__truncRule.getFaciesInTruncRule()))

                break
            # End if zone number
        # End for zone
        if err == 1:
            raise ValueError('Some errors occured')
        return

    def initialize(self,inputZoneNumber,mainFaciesTable,truncRule,faciesNames, probNames,gaussNames):
        # Set default values
        self.__zoneNumber = inputZoneNumber
        self.__printInfo = 0
        self.__useConstProb = 0
        self.__simBoxThickness = 10.0
        self.__mainFaciesTable = mainFaciesTable
        self.__truncRule = Trunc1D.Trunc1D()
        self.__truncRule.initialize(mainFaciesTable,faciesNames)

        self.updateFaciesWithProbForZone(faciesNames,probNames)
        for gfName in gaussNames:
            varioType = 'GENERAL_EXPONENTIAL'
            range1    = 1000.0
            range2    = 1000.0
            range3    = 1.0
            angle     = 0.0
            power     = 1.8
            self.updateGaussFieldParam(gfName,varioType,range1,range2,range3,angle,power)

        return


    def hasFacies(self,fName):
        n = len(self.__faciesProbForZoneModel)
        found = 0
        for i in range(n):
            item = self.__faciesProbForZoneModel[i]
            faciesName = item[self.__FNAME]
            if fName == faciesName:
                found = 1
                break
        if found== 0:
            return False
        else:
            return True

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

    def useConstProb(self):
        return self.__useConstProb

    def isMainLevelModel(self):
        if self.__faciesLevel == 1:
            return True
        else:
            return False


    def getMainLevelFacies(self):
        return copy.copy(self.__mainLevelFacies)

    def getFaciesInZoneModel(self):
        return copy.copy(self.__faciesInZoneModel)

    def getUsedGaussFieldNames(self):
        gfNames = []
        nGF     = len(self.__varioForGFModel)
        for i in range(nGF):
            item = self.__varioForGFModel[i]
            name = item[self.__GNAME]
            gfNames.append(name)
        return gfNames


    def getVarioType(self,gaussFieldName):
        gfNames = []
        nGF     = len(self.__varioForGFModel)
        found = 0
        for i in range(nGF):
            item = self.__varioForGFModel[i]
            name = item[self.__GNAME]
            if name == gaussFieldName:
                # item = [name,varioType,range1,range2,range3,angle]
                varioType = item[self.__GTYPE]
                found = 1
                break
        if found == 0:
            print('Error: Variogram data for gauss field name: ' + gaussFieldName + ' is not found.')
            varioType = None
        return copy.copy(varioType)

    def getVarioTypeNumber(self,gaussFieldName):
        gfNames = []
        nGF     = len(self.__varioForGFModel)
        found = 0
        for i in range(nGF):
            item = self.__varioForGFModel[i]
            name = item[self.__GNAME]
            if name == gaussFieldName:
                # item = [name,varioType,range1,range2,range3,angle]
                varioType = item[self.__GTYPE]
                found = 1
                break
        if found == 0:
            print('Error: Variogram data for gauss field name: ' + gaussFieldName + ' is not found.')
            varioType = None

        # NOTE: This table must be consistent with simGauss2D
        if varioType == 'SPHERICAL':
            varioTypeNumber = 1
        elif varioType == 'EXPONENTIAL':
            varioTypeNumber = 2
        elif varioType == 'GAUSSIAN':
            varioTypeNumber = 3
        elif varioType == 'GENERAL_EXPONENTIAL':
            varioTypeNumber = 4
        else:
            # Undefined
            varioTypeNumber = 0
        return varioTypeNumber

    def getMainRange(self,gaussFieldName):
        gfNames = []
        nGF     = len(self.__varioForGFModel)
        found = 0
        r = 0
        for i in range(nGF):
            item = self.__varioForGFModel[i]
            name = item[self.__GNAME]
            if name == gaussFieldName:
                # item = [name,varioType,range1,range2,range3,angle]
                r = item[self.__GRANGE1]
                found = 1
                break
        if found == 0:
            print('Error: Variogram data for gauss field name: ' + gaussFieldName + ' is not found.')

        return r

    def getPerpRange(self,gaussFieldName):
        gfNames = []
        nGF     = len(self.__varioForGFModel)
        found = 0
        r = 0
        for i in range(nGF):
            item = self.__varioForGFModel[i]
            name = item[self.__GNAME]
            if name == gaussFieldName:
                # item = [name,varioType,range1,range2,range3,angle]
                r = item[self.__GRANGE2]
                found = 1
                break
        if found == 0:
            print('Error: Variogram data for gauss field name: ' + gaussFieldName + ' is not found.')

        return r

    def getVertRange(self,gaussFieldName):
        gfNames = []
        nGF     = len(self.__varioForGFModel)
        found = 0
        r = 0
        for i in range(nGF):
            item = self.__varioForGFModel[i]
            name = item[self.__GNAME]
            if name == gaussFieldName:
                # item = [name,varioType,range1,range2,range3,angle]
                r = item[self.__GRANGE3]
                found = 1
                break
        if found == 0:
            print('Error: Variogram data for gauss field name: ' + gaussFieldName + ' is not found.')

        return r

    def getAnisotropyAsimuthAngle(self,gaussFieldName):
        gfNames = []
        nGF     = len(self.__varioForGFModel)
        found = 0
        r = 0
        for i in range(nGF):
            item = self.__varioForGFModel[i]
            name = item[self.__GNAME]
            if name == gaussFieldName:
                # item = [name,varioType,range1,range2,range3,angle]
                r = item[self.__GANGLE]
                found = 1
                break
        if found == 0:
            print('Error: Variogram data for gauss field name: ' + gaussFieldName + ' is not found.')

        return r


    def getPower(self,gaussFieldName):
        gfNames = []
        nGF     = len(self.__varioForGFModel)
        found = 0
        r = 0
        for i in range(nGF):
            item = self.__varioForGFModel[i]
            name = item[self.__GNAME]
            if name == gaussFieldName:
                # item = [name,varioType,range1,range2,range3,angle,power]
                r = item[self.__GPOWER]
                found = 1
                break
        if found == 0:
            print('Error: Variogram data for gauss field name: ' + gaussFieldName + ' is not found.')

        return r

    def getTruncRule(self):
        return self.__truncRule

    def getTrendRuleModel(self,gfName):
        found = 0
        for item in self.__trendForGFModel:
            name = item[self.__TNAME]
            if name == gfName:
                found = 1
                useTrend = item[self.__TUSE]
                trendModelObj = item[self.__TOBJ]
                relStdDev = item[self.__TSTD]
        if found == 1:
            return [useTrend,trendModelObj,relStdDev]
        else:
            return None

    def getTrendRuleModelObject(self,gfName):
        found = 0
        for item in self.__trendForGFModel:
            name = item[self.__TNAME]
            if name == gfName:
                found = 1
                trendModelObj = item[self.__TOBJ]
        if found == 1:
            return trendModelObj
        else:
            return None

    def getSimBoxThickness(self):
        return self.__simBoxThickness

    def getTruncationParam(self,get3DParamFunction,gridModel,realNumber):
        if not self.__truncRule.useConstTruncModelParam():
            self.__truncRule.getTruncationParam(get3DParamFunction,gridModel,realNumber)

    def printInfo(self):
        return self.__printInfo


    def getHorizonNameForVarioTrendMap(self):
        return copy.copy(self.__horizonNameForVarioTrendMap)


    def getProbParamName(self,fName):
        found  = 0
        for item in self.__faciesProbForZoneModel:
            fN = item[self.__FNAME]
            if fN == fName:
                probCubeName = item[self.__FPROB]
                found = 1
                break
        if found == 0:
            return None
        else:
            return copy.copy(probCubeName)

    def getAllProbParamForZone(self):
        found  = 0
        allProbParamList = []
        for item in self.__faciesProbForZoneModel:
            probParamName = item[self.__FPROB]
            if self.__useConstProb  == 0:
                if not probParamName in allProbParamList:
                    allProbParamList.append(probParamName)
        return allProbParamList

    def getConstProbValue(self,fName):
        if self.__useConstProb == 1:
            found  = 0
            for item in self.__faciesProbForZoneModel:
                fN = item[self.__FNAME]
                if fN == fName:
                    probCubeName = item[self.__FPROB]
                    found = 1
                    break
            if found == 0:
                print('Error: Probability not found for facies: ' + fName)
                return -999
            else:
                return float(probCubeName)
        else:
            print('Error: Can not call getConstProbValue when useConstProb = 0')
            return  -999

    def __getGFIndex(self,gfName):
        indx = -999
        for i in range(len(self.__varioForGFModel)):
            item = self.__varioForGFModel[i]
            gf = item[self.__GNAME]
            if gf== gfName:
                indx = i
                break
        return indx

    def setZoneNumber(self,zoneNumber):
        self.__zoneNumber = zoneNumber
        return
    
    def setVarioType(self,gaussFieldName,varioType):
        err = 0
        if  self.__isVarioTypeOK(varioType):
            gfList = self.getUsedGaussFieldNames()
            if gaussFieldName  in gfList:
                indx = self.__getGFIndex(gaussFieldName)
                item = self.__varioForGFModel[indx]
                item[self.__GTYPE] = varioType
            else:
                err = 1
        else:
            err = 1
        return err

    def setRange1(self,gaussFieldName,range1):
        err = 0
        if range1 < 0.0:
            err = 1
        else:
            gfList = self.getUsedGaussFieldNames()
            if gaussFieldName  in gfList:
                indx = self.__getGFIndex(gaussFieldName)
                item = self.__varioForGFModel[indx]
                item[self.__GRANGE1] = range1
            else:
                err = 1
        return err


    def setRange2(self,gaussFieldName,range2):
        err = 0
        if range2 < 0.0:
            err = 1
        else:
            gfList = self.getUsedGaussFieldNames()
            if gaussFieldName  in gfList:
                indx = self.__getGFIndex(gaussFieldName)
                item = self.__varioForGFModel[indx]
                item[self.__GRANGE2] = range2
            else:
                err = 1
        return err

    def setRange3(self,gaussFieldName,range3):
        err = 0
        if range3 < 0.0:
            err = 1
        else:
            gfList = self.getUsedGaussFieldNames()
            if gaussFieldName  in gfList:
                indx = self.__getGFIndex(gaussFieldName)
                item = self.__varioForGFModel[indx]
                item[self.__GRANGE3] = range3
            else:
                err = 1
        return err

    def setAngle(self,gaussFieldName,angle):
        err = 0
        gfList = self.getUsedGaussFieldNames()
        if gaussFieldName  in gfList:
            indx = self.__getGFIndex(gaussFieldName)
            item = self.__varioForGFModel[indx]
            item[self.__GANGLE] = angle
        else:
            err = 1
        return err

    def setPower(self,gaussFieldName,power):
        err = 0
        if power < 1.0 or power > 2.0:
            err = 1
        else:
            gfList = self.getUsedGaussFieldNames()
            if gaussFieldName  in gfList:
                indx = self.__getGFIndex(gaussFieldName)
                item = self.__varioForGFModel[indx]
                item[self.__GPOWER] = power
            else:
                err = 1
        return err

    def setMainFaciesTable(self,mainFaciesTable):
        err = 0
        if mainFaciesTable == None:
            err = 1
        else:
            self.__mainFaciesTable = mainFaciesTable
        return err

    def setUseConstProb(self,useConstProb):
        self.__useConstProb = useConstProb
        return

    def setSeedForPreviewSimulation(self,gfName,seed):
        err = 0
        found = 0
        for i in range(len(self.__seedForPreviewForGFModel)):
            item = self.__seedForPreviewForGFModel[i]
            name = item[self.__SNAME]
            if name == gfName:
                found = 1
                item[self.__SVALUE] = seed
                break
        if found == 0:
            err = 1
        return err

    def setSimBoxThickness(self,thickness):
        err = 0
        if thickness < 0.0:
            err = 1
        self.__simBoxThickness = thickness
        return err

    def updateFaciesWithProbForZone(self,faciesList,faciesProbList):
        err = 0
        # Check that facies is defined
        for fName in faciesList:
            if not self.__mainFaciesTable.checkWithFaciesTable(fName):
                err = 1
                break
        if len(faciesList) != len(faciesProbList):
            err = 1

        for i in range(len(faciesList)):
            fName = faciesList[i]
            fProbName = faciesProbList[i]
            found = 0
            for item in self.__faciesProbForZoneModel:
                name = item[self.__FNAME]
                if name == fName:
                    # Update facies probability cube name
                    found = 1
                    item[self.__FPROB] = copy.copy(fProbName)
                    break
            if found == 0:
                # insert new facies
                item = [fName,fProbName]
                self.__faciesProbForZoneModel.append(item)
                self.__faciesInZoneModel.append(fName)
        return err 

    def removeFaciesWithProbForZone(self,fName):
        indx = -999
        for i in range(len(self.__faciesProbForZoneModel)):
            item = self.__faciesProbForZoneModel[i]
            name = item[self.__FNAME]
            if fName == name:
                indx = i
                break
        if indx != -999:
            # Remove data for this facies
            self.__faciesProbForZoneModel.pop(indx)
            self.__faciesInZoneModel.pop(indx)
        return

    def updateGaussFieldParam(self,gfName,varioType,range1,range2,range3,angle,power,
                              relStdDev=0.0,trendRuleModelObj=None):
        # Update or create new gauss field parameter object (with trend)
        err = 0
        found = 0
        if  not self.__isVarioTypeOK(varioType):
            print('Error in ' + self.__className + ' in ' + 'updateGaussFieldParam')
            print('Error: Undefined variogram type specified.')
            err = 1
        if range1 < 0:
            print('Error in ' + self.__className + ' in ' + 'updateGaussFieldParam')
            print('Error: Correlation range < 0.0')
            err = 1
        if range2 < 0:
            print('Error in ' + self.__className + ' in ' + 'updateGaussFieldParam')
            print('Error: Correlation range < 0.0')
            err = 1
        if range3 < 0:
            print('Error in ' + self.__className + ' in ' + 'updateGaussFieldParam')
            print('Error: Correlation range < 0.0')
            err = 1
        if varioType == 'GENERAL_EXPONENTIAL':
            if power < 1.0 or power > 2.0:
                print('Error in ' + self.__className + ' in ' + 'updateGaussFieldParam')
                print('Error: Exponent in GENERAL_EXPONENTIAL variogram is outside [1.0,2.0]')
                err = 1
        if relStdDev < 0.0:
            print('Error in ' + self.__className + ' in ' + 'updateGaussFieldParam')
            print('Error: Relative standard deviation used when trends are specified is negative.')
            err = 1

        # Check if gauss field is already defined, then update parameters or create new
        for item in self.__varioForGFModel:
            name = item[self.__GNAME]
            if name == gfName:
                self.updateGaussFieldVarioParam(gfName,varioType,range1,range2,range3,angle,power)
                self.updateGaussFieldTrendParam(gfName,trendRuleModelObj,relStdDev)
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
        err = 0
        found = 0
        # Check that gauss field is already defined, then update parameters.
        for item in self.__varioForGFModel:
            name = item[self.__GNAME]
            if name == gfName:
                found = 1
                item[self.__GTYPE]   = varioType
                item[self.__GRANGE1] = range1
                item[self.__GRANGE2] = range2
                item[self.__GRANGE3] = range3
                item[self.__GANGLE]  = angle
                item[self.__GPOWER]  = power
                break   
        if found == 0:
            err = 1
        return err

    def removeGaussFieldParam(self,gfName):
        indx = -999
        for i in range(len(self.__varioForGFModel)):
            item = self.__varioForGFModel[i]
            name = item[self.__GNAME]
            if name == gfName:
                indx = i
                break
        if indx != -999:
            # Remove from list
            self.__varioForGFModel.pop(indx)
            self.__trendForGFModel.pop(indx)
            self.__seedForPreviewForGFModel.pop(indx)
        return

    def updateGaussFieldTrendParam(self,gfName,trendRuleModelObj,relStdDev):
        # Update trend parameters for existing trend for gauss field model
        # But it does not create new trend object.
        err = 0
        if trendRuleModelObj == None:
            err = 1
        else:
            # Check if gauss field is already defined, then update parameters
            found = 0
            for item in self.__trendForGFModel:
                name = item[self.__TNAME]
                if name == gfName:
                    found = 1
                    item[self.__TUSE] = 1
                    item[self.__TSTD] = relStdDev
                    item[self.__TOBJ] = trendRuleModelObj
                    break   
            if found == 0:
                # This gauss field was not found.
                err = 1
        return err


    def setTruncRule(self,truncRuleObj):
        err = 0
        if truncRuleObj == None:
            err = 1
        else:
            self.__truncRule = truncRuleObj
        return err

    def setHorizonNameForVarioTrendMap(self,horizonNameForVarioTrendMap):
        self.__horizonNameForVarioTrendMap = copy.copy(horizonNameForVarioTrendMap)
        return 

    def __checkConstProbValuesAndNormalize(self):
        if self.__useConstProb == 1:
            sumProb = 0.0
            for i in range(len(self.__faciesProbForZoneModel)):
                item = self.__faciesProbForZoneModel[i]
                prob  = float(item[self.__FPROB])
                sumProb  += prob
            if abs(sumProb - 1.0) > 0.001:
                print('Warning in ' + self.__className)
                text = 'Warning: Specified constant probabilities sum up to: ' + str(sumProb) 
                text = text + ' and not 1.0 in zone: ' + str(self.__zoneNumber)
                print(text)
                print('Warning: The specified probabilities will be normalized.')
                for i in range(len(self.__faciesProbForZoneModel)):
                    item = self.__faciesProbForZoneModel[i]
                    prob  = float(item[self.__FPROB])
                    normalizedProb = prob/sumProb
                    item[self.__FPROB] = str(normalizedProb)
        return

    def applyTruncations(self,probDefined,GFAlphaList,faciesReal,nDefinedCells,cellIndexDefined):

        # GFAlphaList has items =[name,valueArray]
        # Use NAME and VAL as index names
        NAME = 0
        VAL  = 1

        # GFAlphaList has one item for each transformed gaussian field
        # Use ALPHA1,ALPHA2,ALPHA3 as index names
        ALPHA1 = 0
        ALPHA2 = 1
        ALPHA3 = 2

        truncObject    = self.__truncRule
        functionName   = 'applyTruncations'
        printInfo      = self.__printInfo
        faciesNames    = self.__faciesInZoneModel
        nFacies        = len(faciesNames)
        classNameTrunc = truncObject.getClassName()
        if len(probDefined) != nFacies:
            raise ValueError(
                'Error: In class: ' + self.__className + '\n'
                'Error: Mismatch in input to applyTruncations'
                )

        useConstTruncParam = truncObject.useConstTruncModelParam()
        nGaussFields = len(GFAlphaList)
        faciesProb     = np.zeros(nFacies,np.float32)
        volFrac        = np.zeros(nFacies,np.float32)
        if printInfo >= 2:
            print('--- Truncation rule: ' + classNameTrunc)

        if self.__useConstProb==1 and useConstTruncParam == 1:
            # Constant probability 
            if printInfo >= 3:
                print('Debug output: Using spatially constant probabilities for facies.')

            for f in range(nFacies):
                faciesProb[f] = probDefined[f]

            if self.__printInfo >= 3:
                print('Debug output: faciesProb:')
                print(repr(faciesProb))

            if nGaussFields == 1:
                item   = GFAlphaList[ALPHA1]
                gfName1 = item[NAME]
                alpha1 = item[VAL]

                # Calculate truncation rules
                if printInfo >= 3:
                    print('Debug output: Use gauss fields: ' + gfName1)
                truncObject.setTruncRule(faciesProb)
                for i in range(nDefinedCells):
                    if printInfo == 2:
                        if np.mod(i,500000)==0:
                            print('--- Calculate facies for cell number: ' + str(i))
                    elif printInfo >=3:
                        if np.mod(i,10000)==0:
                            print('--- Calculate facies for cell number: ' + str(i))
        
                    # One transformed gaussian field.
                    cellIndx = cellIndexDefined[i]
                    u1 = alpha1[cellIndx]
                    [fCode,fIndx] = truncObject.defineFaciesByTruncRule(u1)
                    faciesReal[cellIndx] = fCode
                    volFrac[fIndx] += 1
            elif nGaussFields == 2:
                item   = GFAlphaList[ALPHA1]
                gfName1 = item[NAME]
                alpha1  = item[VAL]
                if printInfo >= 3:
                    print('Debug output: Use gauss fields: ' + gfName1)

                item   = GFAlphaList[ALPHA2]
                gfName2 = item[NAME]
                alpha2  = item[VAL]

                if printInfo >= 3:
                    print('Debug output: Use gauss fields: ' + gfName2)

                # Calculate truncation rules
                truncObject.setTruncRule(faciesProb)
                for i in range(nDefinedCells):
                    if printInfo == 2:
                        if np.mod(i,500000)==0:
                            print('--- Calculate facies for cell number: ' + str(i))
                    elif printInfo >=3:
                        if np.mod(i,10000)==0:
                            print('--- Calculate facies for cell number: ' + str(i))
        
                    # Truncate GF.  Two transformed gaussian fields.
                    cellIndx = cellIndexDefined[i]
                    u1 = alpha1[cellIndx]
                    u2 = alpha2[cellIndx]
                    [fCode,fIndx] = truncObject.defineFaciesByTruncRule(u1,u2)
                    faciesReal[cellIndx] = fCode
                    volFrac[fIndx] += 1
            elif nGaussFields == 3:
                item   = GFAlphaList[ALPHA1]
                gfName1 = item[NAME]
                alpha1  = item[VAL]
                if printInfo >= 3:
                    print('Debug output: Use gauss fields: ' + gfName1)


                item   = GFAlphaList[ALPHA2]
                gfName2 = item[NAME]
                alpha2  = item[VAL]
                if printInfo >= 3:
                    print('Debug output: Use gauss fields: ' + gfName2)


                item   = GFAlphaList[ALPHA3]
                gfName3 = item[NAME]
                alpha3  = item[VAL]
                if printInfo >= 3:
                    print('Debug output: Use gauss fields: ' + gfName3)


                # Calculate truncation rules
                truncObject.setTruncRule(faciesProb)
                for i in range(nDefinedCells):
                    if printInfo == 2:
                        if np.mod(i,500000)==0:
                            print('--- Calculate facies for cell number: ' + str(i))
                    elif printInfo >=3:
                        if np.mod(i,10000)==0:
                            print('--- Calculate facies for cell number: ' + str(i))
        
                    # Truncate GF.  Three transformed gaussian fields.
                    cellIndx = cellIndexDefined[i]
                    u1 = alpha1[cellIndx]
                    u2 = alpha2[cellIndx]
                    u3 = alpha3[cellIndx]
                    [fCode,fIndx] = truncObject.defineFaciesByTruncRule(u1,u2,u3)
                    faciesReal[cellIndx] = fCode
                    volFrac[fIndx] += 1

        else:
            # Varying probability from cell to cell and / or 
            # varying truncation parameter from cell to cell
            if printInfo >= 3:
                text = 'Debug output: Using spatially varying probabilities and/or '
                text = text + 'truncation parameters for facies.' 
                print(text)

            if nGaussFields == 1:
                item   = GFAlphaList[ALPHA1]
                gfName1 = item[NAME]
                alpha1 = item[VAL]

                if printInfo >= 3:
                    print('Debug output: Use gauss fields: ' + gfName1)

                for i in range(nDefinedCells):
                    if printInfo == 2:
                        if np.mod(i,500000)==0:
                            print('--- Calculate facies for cell number: ' + str(i))
                    elif printInfo >=3:
                        if np.mod(i,10000)==0:
                            print('--- Calculate facies for cell number: ' + str(i))

                    if self.__useConstProb==1:
                        for f in range(nFacies):
                            faciesProb[f] = probDefined[f]
                    else:
                        for f in range(nFacies):
                            faciesProb[f] = probDefined[f][i]


                    # Calculate truncation rules
                    cellIndx = cellIndexDefined[i]
                    truncObject.setTruncRule(faciesProb,cellIndx)

                    # Truncate GF.  One transformed gaussian field.
                    u1 = alpha1[cellIndx]
#                    print('u1: '+ str(u1))
                    [fCode,fIndx] = truncObject.defineFaciesByTruncRule(u1)
                    faciesReal[cellIndx] = fCode
                    volFrac[fIndx] += 1
#                    print('cellIndx= ' + str(cellIndx) + '  fCode= ' + str(fCode) + ' fIndx= ' + str(fIndx))
            elif nGaussFields == 2:
                item   = GFAlphaList[ALPHA1]
                gfName1 = item[NAME]
                alpha1  = item[VAL]
                if printInfo >= 3:
                    print('Debug output: Use gauss fields: ' + gfName1)

                item   = GFAlphaList[ALPHA2]
                gfName2 = item[NAME]
                alpha2  = item[VAL]
                if printInfo >= 3:
                    print('Debug output: Use gauss fields: ' + gfName2)

                for i in range(nDefinedCells):
                    if printInfo == 2:
                        if np.mod(i,500000)==0:
                            print('--- Calculate facies for cell number: ' + str(i))
                    elif printInfo >=3:
                        if np.mod(i,10000)==0:
                            print('--- Calculate facies for cell number: ' + str(i))
        
                    if self.__useConstProb==1:
                        for f in range(nFacies):
                            faciesProb[f] = probDefined[f]
                    else:
                        for f in range(nFacies):
                            faciesProb[f] = probDefined[f][i]

                    # Calculate truncation rules
                    cellIndx = cellIndexDefined[i]
                    truncObject.setTruncRule(faciesProb,cellIndx)

                    # Truncate GF.  One transformed gaussian field.
                    u1 = alpha1[cellIndx]
                    u2 = alpha2[cellIndx]
                    [fCode,fIndx] = truncObject.defineFaciesByTruncRule(u1,u2)
                    faciesReal[cellIndx] = fCode
                    volFrac[fIndx] += 1

            elif nGaussFields == 3:
                item   = GFAlphaList[ALPHA1]
                gfName1 = item[NAME]
                alpha1  = item[VAL]
                if printInfo >= 3:
                    print('Debug output: Use gauss fields: ' + gfName1)

                item   = GFAlphaList[ALPHA2]
                gfName2 = item[NAME]
                alpha2  = item[VAL]
                if printInfo >= 3:
                    print('Debug output: Use gauss fields: ' + gfName2)

                item   = GFAlphaList[ALPHA3]
                gfName3 = item[NAME]
                alpha3  = item[VAL]
                if printInfo >= 3:
                    print('Debug output: Use gauss fields: ' + gfName3)

                for i in range(nDefinedCells):
                    if printInfo == 2:
                        if np.mod(i,500000)==0:
                            print('--- Calculate facies for cell number: ' + str(i))
                    elif printInfo >=3:
                        if np.mod(i,10000)==0:
                            print('--- Calculate facies for cell number: ' + str(i))
                
                    if self.__useConstProb==1:
                        for f in range(nFacies):
                            faciesProb[f] = probDefined[f]
                    else:
                        for f in range(nFacies):
                            faciesProb[f] = probDefined[f][i]

                    # Calculate truncation rules
                    cellIndx = cellIndexDefined[i]
                    truncObject.setTruncRule(faciesProb,cellIndx)

                    # Truncate GF.  One transformed gaussian field.
                    u1 = alpha1[cellIndx]
                    u2 = alpha2[cellIndx]
                    u3 = alpha3[cellIndx]
                    [fCode,fIndx] = truncObject.defineFaciesByTruncRule(u1,u2,u3)
                    faciesReal[cellIndx] = fCode
                    volFrac[fIndx] += 1

        for f in range(nFacies):
            volFrac[f] = volFrac[f]/float(nDefinedCells)    
        return [faciesReal,volFrac]


    def XMLAddElement(self,parent):

        # Add command Zone and all its childs

        tag = 'Zone'
        if self.__faciesLevel == 1:
            attribute = {'number':str(self.__zoneNumber)}
        else:
            attribute = {'number':str(self.__zoneNumber),'mainLevelFacies':self.__mainLevelFacies.strip()}
        elem = Element(tag,attribute)
        zoneElement = elem
        parent.append(zoneElement)

        # Add child command UseConstProb
        tag = 'UseConstProb'
        elem = Element(tag)
        elem.text = ' ' + str(self.__useConstProb) + ' ' 
        zoneElement.append(elem)

        # Add child command SimBoxThickness
        tag = 'SimBoxThickness'
        elem = Element(tag)
        elem.text = ' ' + str(self.__simBoxThickness) + ' ' 
        zoneElement.append(elem)

        # Add child command HorizonNameVarioTrend
        if self.__horizonNameForVarioTrendMap != None:
            tag = 'HorizonNameVarioTrend'
            elem = Element(tag)
            elem.text = ' ' + self.__horizonNameForVarioTrendMap + ' '
            zoneElement.append(elem)

        # Add child command FaciesProbForModel
        tag = 'FaciesProbForModel'
        elem = Element(tag)
        zoneElement.append(elem)
        fProbElement = elem
        for i in range(len(self.__faciesProbForZoneModel)):
            fName = self.__faciesProbForZoneModel[i][self.__FNAME]
            fProb = self.__faciesProbForZoneModel[i][self.__FPROB]
            tag = 'Facies'
            attribute = {'name':fName}
            fElement = Element(tag,attribute)
            fProbElement.append(fElement)
            tag = 'ProbCube'
            pElement = Element(tag)
            pElement.text = ' ' + str(fProb) + ' '
            fElement.append(pElement)


        # Add child command GaussField
        nGaussFieldsForModel = len(self.__varioForGFModel)
        for i in range(nGaussFieldsForModel):
            gfName     = self.__varioForGFModel[i][self.__GNAME]
            varioType  = self.__varioForGFModel[i][self.__GTYPE]
            range1     = self.__varioForGFModel[i][self.__GRANGE1]
            range2     = self.__varioForGFModel[i][self.__GRANGE2]
            range3     = self.__varioForGFModel[i][self.__GRANGE3]
            angle      = self.__varioForGFModel[i][self.__GANGLE]
            power      = self.__varioForGFModel[i][self.__GPOWER]

            if gfName != self.__trendForGFModel[i][self.__TNAME]:
                print('Error in class: ' + self.__className + ' in ' + 'XMLAddElement')
                sys.exit()
            useTrend   = self.__trendForGFModel[i][self.__TUSE]
            trendObj   = self.__trendForGFModel[i][self.__TOBJ]
            relStdDev  = self.__trendForGFModel[i][self.__TSTD]

            tag = 'GaussField'
            attribute = {'name':gfName}
            elem = Element(tag,attribute)
            zoneElement.append(elem)
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
            seedValue = self.__seedForPreviewForGFModel[i][self.__SVALUE]
            elem.text = ' ' + str(seedValue) + ' '
            gfElement.append(elem)


        # Add child command TruncationRule at end of the child list for
        self.__truncRule.XMLAddElement(zoneElement)
        return



    def simGaussFieldWithTrendAndTransform(self,gridDimNx,gridDimNy,gridXSize,gridYSize,gridAsimuthAngle):
        nx = gridDimNx
        ny = gridDimNy
        xsize = gridXSize
        ysize = gridYSize
        a1 = np.zeros(nx*ny,float)
        a2 = np.zeros(nx*ny,float)
        a3 = np.zeros(nx*ny,float)
        
        gaussFieldNamesForSimulation = self.getUsedGaussFieldNames()
        nGaussFields = len(gaussFieldNamesForSimulation)
        for i in range(nGaussFields):
            # Find data for specified Gauss field name
            name      = gaussFieldNamesForSimulation[i]
            seedValue = self.__seedForPreviewForGFModel[i][self.__SVALUE]
            varioType = self.getVarioType(name)
            varioTypeNumber = self.getVarioTypeNumber(name)
            r1        = self.getMainRange(name)
            r2        = self.getPerpRange(name)
            r3        = self.getVertRange(name)
            angle     = self.getAnisotropyAsimuthAngle(name)
            angle = angle - gridAsimuthAngle

            power     = self.getPower(name)

            useTrend     = self.__trendForGFModel[i][self.__TUSE]
            trendAsimuth = 0.0
            if useTrend == 1:
                trendObj     = self.__trendForGFModel[i][self.__TOBJ]
                trendAsimuth = trendObj.getAsimuth() - gridAsimuthAngle

            relSigma     = self.__trendForGFModel[i][self.__TSTD]
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
            if i== 0:
                # Gauss field 1
                [a1] = simGaussFieldAddTrendAndTransform(seedValue,nx,ny,xsize,ysize,
                                                         varioTypeNumber,r1,r2,angle,power,
                                                         useTrend,trendAsimuth,relSigma,self.__printInfo)
            if i== 1:
                # Gauss field 2
                [a2] = simGaussFieldAddTrendAndTransform(seedValue,nx,ny,xsize,ysize,
                                                         varioTypeNumber,r1,r2,angle,power,
                                                         useTrend,trendAsimuth,relSigma,self.__printInfo)
            if i==2:
                # Gauss field 3
                [a3] = simGaussFieldAddTrendAndTransform(seedValue,nx,ny,xsize,ysize,
                                                         varioTypeNumber,r1,r2,angle,power,
                                                         useTrend,trendAsimuth,relSigma,self.__printInfo)
        # End for        

        return [a1,a2,a3]

    
