#!/bin/env python
from xml.etree.ElementTree import Element

import copy
import numpy as np

from src.APSFaciesProb import APSFaciesProb
from src.APSGaussFieldJobs import APSGaussFieldJobs
from src.APSGaussModel import APSGaussModel
from src.APSMainFaciesTable import APSMainFaciesTable
from src.Trunc2D_Angle_xml import Trunc2D_Angle
# To be outphased:
from src.Trunc2D_Cubic_xml import Trunc2D_Cubic
from src.Trunc3D_bayfill_xml import Trunc3D_bayfill
# Functions to draw 2D gaussian fields with linear trend and transformed to uniform distribution
from src.utils.constants import Debug
from src.xmlFunctions import getFloatCommand, getIntCommand, getKeyword, getTextCommand


class APSZoneModel:
    """
    ----------------------------------------------------------------
    class APSZoneModel
    Description: Keep data structure for a zone

    Public member functions:
      Constructor:  def __init__(self,ET_Tree= None,inputZoneNumber=0,
                                 inputMainLevelFacies=None,modelFileName=None)
     --- Get functions ---
       def getZoneNumber(self)
       def useConstProb(self)
       def getMainLevelFacies(self)
       def getFaciesInZoneModel(self)
       def getUsedGaussFieldNames(self)
       def getVarioType(self,gaussFieldName)
       def getVarioTypeNumber(self,gaussFieldName)
       def getMainRange(self,gaussFieldName)
       def getPerpRange(self,gaussFieldName)
       def getVertRange(self,gaussFieldName)
       def getAnisotropyAzimuthAngle(self,gaussFieldName)
       def getAnisotropyDipAngle(self,gaussFieldName)
       def getPower(self,gaussFieldName)
       def getTruncRule(self)
       def getTrendRuleModel(self,gfName)
       def getSimBoxThickness(self)
       def getTruncationParam(self,get3DParamFunction,gridModel,realNumber)
       def debug_level(self)
       def getProbParamName(self,fName)
       def getAllProbParamForZone(self)
       def getConstProbValue(self,fName)
       def getHorizonNameForVarioTrendMap(self)


       ---  Set functions ---
       def setZoneNumber(self,zoneNumber)
       def setVarioType(self,gaussFieldName,varioType)
       def setRange1(self,gaussFieldName,range1)
       def setRange2(self,gaussFieldName,range2)
       def setRange3(self,gaussFieldName,range3)
       def setAnisotropyAzimuthAngle(self,gaussFieldName,angle)
      def setAnisotropyDipAngle(self,gaussFieldName,angle)

     ---  Set functions ---
       def setZoneNumber(self,zoneNumber)
       def setVarioType(self,gaussFieldName,varioType)
       def setRange1(self,gaussFieldName,range1)
       def setRange2(self,gaussFieldName,range2)
       def setRange3(self,gaussFieldName,range3)
       def setAngle(self,gaussFieldName,angle)
       def setPower(self,gaussFieldName,power)
       def setUseConstProb(self)
       def setSeedForPreviewSimulation(self)
       def setMainFaciesTable(self,mainFaciesTable)
       def setSimBoxThickness(self,thickness)
       def updateGaussFieldParam(self,gfName,varioType,range1,range2,range3,angle,power,
                                 relStdDev=0.0,trendRuleModelObj=None)
       def removeGaussFieldParam(self,gfName)
       def updateFaciesWithProbForZone(self,faciesList,faciesProbList)
       def removeFaciesWithProbForZone(self,fName)
       def setTruncRule(self,truncRuleObj)
       def setHorizonNameForVarioTrendMap(self,horizonNameForVarioTrendMap)

     ---  Calculate function ---
       def applyTruncations(self,probDefined,GFAlphaList,faciesReal,nDefinedCells,cellIndexDefined)
       def simGaussFieldWithTrendAndTransform(
           self, nGaussFields, gridDimNx, gridDimNy,
           gridXSize, gridYSize, gridAzimuthAngle
        )


     ---  write XML tree ---
       def XMLAddElement(self,parent)
       def getZoneNumber(self)

     --- Check functions ---
       def hasFacies(self,fName)
       def isMainLevelModel(self)

    Private member functions:
       def __interpretXMLTree(ET_Tree)
       def __isVarioTypeOK(self,varioType)
       def __checkConstProbValuesAndNormalize(self)
       def __getGFIndex(self,gfName)
       def __updateGaussFieldVarioParam(self,gfName,varioType,range1,range2,range3,angle,power)
       def __updateGaussFieldTrendParam(self,gfName,trendRuleModelObj,relStdDev)

    ----------------------------------------------------------------
    """

    def __init__(self, ET_Tree=None, inputZoneNumber=0, inputMainLevelFacies=None, modelFileName=None):

        self.__setEmpty()

        self.__zoneNumber = inputZoneNumber
        self.__mainLevelFacies = inputMainLevelFacies

        if ET_Tree is not None:
            self.__interpretXMLTree(ET_Tree, modelFileName)

    # End __init__

    def __setEmpty(self):
        # Local variables
        self.__debug_level = Debug.OFF
        self.__useConstProb = 0
        self.__className = 'APSZoneModel'
        self.__simBoxThickness = 10.0

        self.__faciesProbObject = None
        self.__gaussModelObject = None

        self.__truncRule = None
        self.__zoneNumber = 0
        self.__faciesLevel = 1
        self.__mainLevelFacies = None
        self.__horizonNameForVarioTrendMap = None

    def __interpretXMLTree(self, ET_Tree, modelFileName):
        #  Get root of xml tree for model specification
        root = ET_Tree.getroot()

        # --- PrintInfo ---
        kw = 'PrintInfo'
        self.__debug_level = getIntCommand(root, kw, defaultValue=1, required=False)

        if self.__debug_level >= Debug.VERY_VERBOSE:
            print(' ')
            print('Debug output: Call init ' + self.__className)

        mainFaciesTable = APSMainFaciesTable(ET_Tree, modelFileName)
        gaussFieldJobs = APSGaussFieldJobs(ET_Tree, modelFileName)

        zoneModels = getKeyword(root, 'ZoneModels', 'Root', modelFile=modelFileName)
        for zone in zoneModels.findall('Zone'):
            zoneNumber = int(zone.get('number'))
            mainLevelFacies = zone.get('mainLevelFacies')
            if zoneNumber == self.__zoneNumber and mainLevelFacies == self.__mainLevelFacies:
                if mainLevelFacies is None:
                    self.__faciesLevel = 1
                else:
                    self.__faciesLevel = 2

                useConstProb = getIntCommand(zone, 'UseConstProb', 'Zone', modelFile=modelFileName)
                self.__useConstProb = useConstProb

                kw = 'SimBoxThickness'
                simBoxThickness = getFloatCommand(zone, kw, 'Zone', minValue=0.0, modelFile=modelFileName)
                self.__simBoxThickness = simBoxThickness

                kw = 'HorizonNameVarioTrend'
                mapName = getTextCommand(zone, kw, 'Zone', modelFile=modelFileName)
                self.__horizonNameForVarioTrendMap = mapName

                if self.__debug_level >= Debug.VERY_VERBOSE:
                    print('Debug output: From APSZoneModel: ZoneNumber: ' + str(zoneNumber))
                    print('Debug output: From APSZoneModel: mainLevelFacies: ' + str(mainLevelFacies))
                    print('Debug output: From APSZoneModel: useConstProb: ' + str(self.__useConstProb))
                    print('Debug output: From APSZoneModel: simBoxThickness: ' + str(self.__simBoxThickness))
                    text = 'Debug output: From APSZoneModel: Horizon name to be used for saving \n'
                    text += '              azimuth variogram trend for this zone: '
                    text += str(self.__horizonNameForVarioTrendMap)
                    print(text)

                # Read facies probabilties
                self.__faciesProbObject = APSFaciesProb(
                    zone, mainFaciesTable, modelFileName,
                    self.__debug_level, self.__useConstProb, self.__zoneNumber
                )
                # Read Gauss Fields model parameters
                self.__gaussModelObject = APSGaussModel(
                    zone, mainFaciesTable, gaussFieldJobs, modelFileName,
                    self.__debug_level, self.__zoneNumber, self.__simBoxThickness
                )

                # Read truncation rule for zone model
                trRule = zone.find('TruncationRule')
                if trRule is None:
                    raise NameError(
                        'Error when reading model file: {modelName}\n'
                        'Error: Missing keyword TruncationRule '
                        'under keyword Zone'
                        ''.format(modelName=modelFileName)
                    )
                truncRuleName = trRule.get('name')
                if self.__debug_level >= Debug.VERY_VERBOSE:
                    print('Debug output: TruncRuleName: ' + truncRuleName)

                nGaussFieldInModel = int(trRule.get('nGFields'))
                nGaussFieldInZone = self.__gaussModelObject.getNGaussFields()
                if nGaussFieldInModel != nGaussFieldInZone:
                    raise ValueError(
                        'Error: In {0}\n'
                        'Error: Number of specified RMS gaussian field 3D parameters: {1}\n'
                        '       does not match number of gaussian fields in truncation rule {2} which is {3}'
                        ''.format(
                            self.__className, str(nGaussFieldInModel), truncRuleName,
                            str(len(self.__varioForGFModel))
                        )
                    )
                else:
                    faciesInZone = self.__faciesProbObject.getFaciesInZoneModel()
                    if truncRuleName == 'Trunc3D_Bayfill':
                        self.__truncRule = Trunc3D_bayfill(
                            trRule, mainFaciesTable, faciesInZone, nGaussFieldInModel,
                            self.__debug_level, modelFileName
                        )

                    elif truncRuleName == 'Trunc2D_Angle':
                        self.__truncRule = Trunc2D_Angle(
                            trRule, mainFaciesTable, faciesInZone, nGaussFieldInModel, self.__debug_level, modelFileName
                        )
                    elif truncRuleName == 'Trunc2D_Cubic':
                        self.__truncRule = Trunc2D_Cubic(
                            trRule, mainFaciesTable, faciesInZone, nGaussFieldInModel, self.__debug_level, modelFileName
                        )
                    else:
                        raise NameError(
                            'Error in {className}\n'
                            'Error: Specified truncation rule name: {truncationRule}\n'
                            '       is not implemented.'
                            ''.format(className=self.__className, truncationRule=truncRuleName)
                        )

                    if self.__debug_level >= Debug.VERY_VERBOSE:
                        text = 'Debug output: APSZoneModel: Truncation rule for current zone: '
                        text += self.__truncRule.getClassName()
                        print(text)
                        print('Debug output: APSZoneModel: Facies in truncation rule: ')
                        print(repr(self.__truncRule.getFaciesInTruncRule()))
                break
                # End if zone number
        # End for zone

        return

    def initialize(self, inputZoneNumber, useConstProb, simBoxThickness, horizonNameForVarioTrendMap,
                   faciesProbObject, gaussModelObject, truncRuleObject, debug_level=Debug.OFF):
        if self.__debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: Call the initialize function in ' + self.__className)

        # Set default values
        self.__setEmpty()
        self.__zoneNumber = inputZoneNumber
        self.__useConstProb = useConstProb
        self.__simBoxThickness = simBoxThickness
        self.__horizonNameForVarioTrendMap = horizonNameForVarioTrendMap
        self.__faciesProbObject = faciesProbObject
        self.__gaussModelObject = gaussModelObject
        self.__truncRule = truncRuleObject

        self.__debug_level = debug_level

        return

    def hasFacies(self, fName):
        return self.__faciesProbObject.hasFacies(fName)

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
        return self.__faciesProbObject.getFaciesInZoneModel()

    def getUsedGaussFieldNames(self):
        return self.__gaussModelObject.getUsedGaussFieldNames()

    def getVarioType(self, gaussFieldName):
        return copy.copy(self.__gaussModelObject.getVarioType(gaussFieldName))

    def getVarioTypeNumber(self, gaussFieldName):
        return self.__gaussModelObject.getVarioTypeNumber(gaussFieldName)

    def getMainRange(self, gaussFieldName):
        return self.__gaussModelObject.getMainRange(gaussFieldName)

    def getPerpRange(self, gaussFieldName):
        return self.__gaussModelObject.getPerpRange(gaussFieldName)

    def getVertRange(self, gaussFieldName):
        return self.__gaussModelObject.getVertRange(gaussFieldName)

    def getAnisotropyAzimuthAngle(self, gaussFieldName):
        return self.__gaussModelObject.getAnisotropyAzimuthAngle(gaussFieldName)

    def getAnisotropyDipAngle(self, gaussFieldName):
        return self.__gaussModelObject.getAnisotropyDipAngle(gaussFieldName)

    def getPower(self, gaussFieldName):
        return self.__gaussModelObject.getPower(gaussFieldName)

    def getTruncRule(self):
        return self.__truncRule

    def getTrendRuleModel(self, gfName):
        return self.__gaussModelObject.getTrendRuleModel(gfName)

    def getTrendRuleModelObject(self, gfName):
        return self.__gaussModelObject.getTrendRuleModelObject(gfName)

    def getSimBoxThickness(self):
        return self.__simBoxThickness

    def getTruncationParam(self, get3DParamFunction, gridModel, realNumber):
        # Input: get3DParamFunction - Function pointer for function to be applied
        #                             to get 3D parameter from RMS project. Is used
        #                             to avoid calling functions using RoxAPI here.
        #        gridModel - Pointer to grid model object in RMS
        #        NOTE: Will only call the function to read RMS parameter from
        #              truncation rules that has defined this as a possibility.
        if not self.__truncRule.useConstTruncModelParam():
            self.__truncRule.getTruncationParam(get3DParamFunction, gridModel, realNumber)

    def printInfo(self):
        return self.__debug_level

    def getHorizonNameForVarioTrendMap(self):
        return copy.copy(self.__horizonNameForVarioTrendMap)

    def getProbParamName(self, fName):
        return self.__faciesProbObject.getProbParamName(fName)

    def getAllProbParamForZone(self):
        return self.__faciesProbObject.getAllProbParamForZone()

    def getConstProbValue(self, fName):
        return self.__faciesProbObject.getConstProbValue(fName)

    def setZoneNumber(self, zoneNumber):
        self.__zoneNumber = zoneNumber
        return

    def setVarioType(self, gaussFieldName, varioType):
        return self.__gaussModelObject.setVarioType(gaussFieldName, varioType)

    def setMainRange(self, gaussFieldName, range1):
        return self.__gaussModelObject.setMainRange(gaussFieldName, range1)

    def setPerpRange(self, gaussFieldName, range2):
        return self.__gaussModelObject.setPerpRange(gaussFieldName, range2)

    def setVertRange(self, gaussFieldName, range3):
        return self.__gaussModelObject.setVertRange(gaussFieldName, range3)

    def setAnisotropyAzimuthAngle(self, gaussFieldName, angle):
        return self.__gaussModelObject.setAnisotropyAzimuthAngle(gaussFieldName, angle)

    def setAnisotropyDipAngle(self, gaussFieldName, angle):
        return self.__gaussModelObject.setAnisotropyDipAngle(gaussFieldName, angle)

    def setPower(self, gaussFieldName, power):
        return self.__gaussModelObject.setPower(gaussFieldName, power)

    def setUseConstProb(self, useConstProb):
        self.__useConstProb = useConstProb
        return

    def setSeedForPreviewSimulation(self, gfName, seed):
        return self.__gaussModelObject.setSeedForPreviewSimulation(gfName, seed)

    def setSimBoxThickness(self, thickness):
        err = 0
        if thickness < 0.0:
            err = 1
        self.__simBoxThickness = thickness
        return err

    def updateFaciesWithProbForZone(self, faciesList, faciesProbList):
        return self.__faciesProbObject.updateFaciesWithProbForZone(faciesList, faciesProbList)

    def removeFaciesWithProbForZone(self, fName):
        self.__faciesProbObject.removeFaciesWithProbForZone(fName)

    def updateGaussFieldParam(self, gfName, varioType, range1, range2, range3, angle, power,
                              relStdDev=0.0, trendRuleModelObj=None):
        return self.__gaussModelObject.updateGaussFieldParam(
            gfName, varioType, range1, range2, range3, angle, power,
            relStdDev, trendRuleModelObj
        )

    def updateGaussFieldVarioParam(self, gfName, varioType, range1, range2, range3, angle, power):
        return self.__gaussModelObject.updateGaussFieldVarioParam(
            gfName, varioType, range1, range2, range3, angle, power
        )

    def removeGaussFieldParam(self, gfName):
        self.__gaussModelObject.removeGaussFieldParam(gfName)

    def updateGaussFieldTrendParam(self, gfName, trendRuleModelObj, relStdDev):
        self.__gaussModelObject.updateGaussFieldTrendParam(gfName, trendRuleModelObj, relStdDev)

    def setTruncRule(self, truncRuleObj):
        err = 0
        if truncRuleObj == None:
            err = 1
        else:
            self.__truncRule = truncRuleObj
        return err

    def setHorizonNameForVarioTrendMap(self, horizonNameForVarioTrendMap):
        self.__horizonNameForVarioTrendMap = copy.copy(horizonNameForVarioTrendMap)
        return

    def applyTruncations(self, probDefined, GFAlphaList, faciesReal, nDefinedCells, cellIndexDefined):

        # GFAlphaList has items =[name,valueArray]
        # Use NAME and VAL as index names
        NAME = 0
        VAL = 1

        truncObject = self.__truncRule
        functionName = 'applyTruncations'
        debug_level = self.__debug_level
        faciesNames = self.getFaciesInZoneModel()
        nFacies = len(faciesNames)
        classNameTrunc = truncObject.getClassName()
        if len(probDefined) != nFacies:
            raise ValueError(
                'Error: In class: ' + self.__className + '\n'
                                                         'Error: Mismatch in input to applyTruncations'
            )

        useConstTruncParam = truncObject.useConstTruncModelParam()
        nGaussFields = len(GFAlphaList)
        faciesProb = np.zeros(nFacies, np.float32)
        volFrac = np.zeros(nFacies, np.float32)
        if debug_level >= Debug.VERBOSE:
            print('--- Truncation rule: ' + classNameTrunc)

        if self.__useConstProb == 1 and useConstTruncParam == 1:
            # Constant probability
            if debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: Using spatially constant probabilities for facies.')

            for f in range(nFacies):
                faciesProb[f] = probDefined[f]

            if self.__debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: faciesProb:')
                print(repr(faciesProb))

            alphaList = []
            for gaussFieldIndx in range(nGaussFields):
                item = GFAlphaList[gaussFieldIndx]
                gfName = item[NAME]
                alphaDataArray = item[VAL]
                alphaList.append(alphaDataArray)
                if debug_level >= Debug.VERY_VERBOSE:
                    print('Debug output: Use gauss fields: ' + gfName)

            # Calculate truncation rules
            # The truncation map/cube is constant and does not vary from cell to cell
            truncObject.setTruncRule(faciesProb)

            for i in range(nDefinedCells):
                if debug_level == Debug.VERBOSE:
                    if np.mod(i, 500000) == 0:
                        print('--- Calculate facies for cell number: ' + str(i))
                elif debug_level >= Debug.VERY_VERBOSE:
                    if np.mod(i, 10000) == 0:
                        print('--- Calculate facies for cell number: ' + str(i))

                cellIndx = cellIndexDefined[i]
                # alphaCoord is the list (alpha1,alpha2,alpha3,..) of coordinate values in alpha space
                alphaCoord = []
                for gaussFieldIndx in range(nGaussFields):
                    alphaDataArray = alphaList[gaussFieldIndx]
                    alphaCoord.append(alphaDataArray[cellIndx])

                # Calculate facies realization by applying truncation rules
                [fCode, fIndx] = truncObject.defineFaciesByTruncRule(alphaCoord)
                faciesReal[cellIndx] = fCode
                volFrac[fIndx] += 1

        else:
            # Varying probability from cell to cell and / or
            # varying truncation parameter from cell to cell
            if debug_level >= Debug.VERY_VERBOSE:
                text = 'Debug output: Using spatially varying probabilities and/or '
                text = text + 'truncation parameters for facies.'
                print(text)

            alphaList = []
            for gaussFieldIndx in range(nGaussFields):
                item = GFAlphaList[gaussFieldIndx]
                gfName = item[NAME]
                alphaDataArray = item[VAL]
                if debug_level >= Debug.VERY_VERBOSE:
                    print('Debug output: Use gauss fields: ' + gfName)
                alphaList.append(alphaDataArray)

            for i in range(nDefinedCells):
                if debug_level >= Debug.VERY_VERBOSE:
                    if np.mod(i, 50000) == 0:
                        print('--- Calculate facies for cell number: ' + str(i))
                elif debug_level == Debug.VERBOSE:
                    if np.mod(i, 500000) == 0:
                        print('--- Calculate facies for cell number: ' + str(i))

                if self.__useConstProb == 1:
                    for f in range(nFacies):
                        faciesProb[f] = probDefined[f]
                else:
                    for f in range(nFacies):
                        faciesProb[f] = probDefined[f][i]

                # Calculate truncation rules
                # The truncation map/cube vary from cell to cell.
                cellIndx = cellIndexDefined[i]
                truncObject.setTruncRule(faciesProb, cellIndx)

                alphaCoord = []
                # alphaCoord is the list (alpha1,alpha2,alpha3,..) of coordinate values in alpha space
                for gaussFieldIndx in range(nGaussFields):
                    alphaDataArray = alphaList[gaussFieldIndx]
                    alphaCoord.append(alphaDataArray[cellIndx])
                # Calculate facies realization by applying truncation rules
                [fCode, fIndx] = truncObject.defineFaciesByTruncRule(alphaCoord)
                faciesReal[cellIndx] = fCode
                volFrac[fIndx] += 1

        if self.__debug_level >= Debug.VERY_VERY_VERBOSE:
            truncRuleName = truncObject.getClassName()
            if truncRuleName == 'Trunc2D_Angle':
                nCalc = truncObject.getNCalcTruncMap()
                nLookup = truncObject.getNLookupTruncMap()
                nCount = truncObject.getNCountShiftAlpha()
                print(
                    'Debug info: In truncation rule ' + truncRuleName + 'nCalc = ' + str(nCalc)
                    + ' nLookup = ' + str(nLookup) + ' nCountShiftAlpha = ' + str(nCount)
                )

        for f in range(nFacies):
            volFrac[f] = volFrac[f] / float(nDefinedCells)
        return [faciesReal, volFrac]

    def XMLAddElement(self, parent):

        # Add command Zone and all its childs
        if self.debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: call XMLADDElement from ' + self.__className)

        tag = 'Zone'
        if self.__faciesLevel == 1:
            attribute = {'number': str(self.__zoneNumber)}
        else:
            attribute = {'number': str(self.__zoneNumber), 'mainLevelFacies': self.__mainLevelFacies.strip()}
        elem = Element(tag, attribute)
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
        self.__faciesProbObject.XMLAddElement(zoneElement)
        # Add child command GaussField
        self.__gaussModelObject.XMLAddElement(zoneElement)
        # Add child command TruncationRule at end of the child list for
        self.__truncRule.XMLAddElement(zoneElement)
        return

    def simGaussFieldWithTrendAndTransform(
            self, nGaussFields, gridDimNx, gridDimNy,
            gridXSize, gridYSize, gridAzimuthAngle, previewCrossSection):
        return self.__gaussModelObject.simGaussFieldWithTrendAndTransform(
            nGaussFields, gridDimNx, gridDimNy, gridXSize, gridYSize,
            gridAzimuthAngle, previewCrossSection
        )

    def simGaussFieldWithTrendAndTransformNew(
            self, nGaussFields, simBoxXsize, simBoxYsize, simBoxZsize,
            gridNX, gridNY, gridNZ, gridAzimuthAngle, crossSectionType):
        return self.__gaussModelObject.simGaussFieldWithTrendAndTransformNew(
            nGaussFields, simBoxXsize, simBoxYsize, simBoxZsize,
            gridNX, gridNY, gridNZ, gridAzimuthAngle, crossSectionType
        )
