#!/bin/env python
import copy
import importlib
import numpy as np
from xml.etree.ElementTree import Element

import src.algorithms.APSFaciesProb
import src.algorithms.APSGaussFieldJobs
import src.algorithms.APSGaussModel
import src.algorithms.APSMainFaciesTable
import src.algorithms.Trunc2D_Angle_xml
import src.algorithms.Trunc2D_Cubic_xml
import src.algorithms.Trunc3D_bayfill_xml
import src.utils.xml

importlib.reload(src.algorithms.APSFaciesProb)
importlib.reload(src.algorithms.APSGaussFieldJobs)
importlib.reload(src.algorithms.APSGaussModel)
importlib.reload(src.algorithms.APSMainFaciesTable)
importlib.reload(src.algorithms.Trunc2D_Angle_xml)
importlib.reload(src.algorithms.Trunc2D_Cubic_xml)
importlib.reload(src.algorithms.Trunc3D_bayfill_xml)
importlib.reload(src.utils.xml)

from src.algorithms.APSFaciesProb import APSFaciesProb
from src.algorithms.APSGaussFieldJobs import APSGaussFieldJobs
from src.algorithms.APSGaussModel import APSGaussModel
from src.algorithms.APSMainFaciesTable import APSMainFaciesTable
from src.algorithms.Trunc2D_Angle_xml import Trunc2D_Angle
from src.algorithms.Trunc2D_Cubic_xml import Trunc2D_Cubic
from src.algorithms.Trunc3D_bayfill_xml import Trunc3D_bayfill
from src.utils.constants.simple import Debug
from src.utils.xml import getKeyword, getTextCommand, getFloatCommand, getIntCommand


class APSZoneModel:
    """
    Keep data structure for a zone

    Public member functions:
      Constructor:  def __init__(self,ET_Tree= None,inputZoneNumber=0,
                                 inputMainLevelFacies=None,modelFileName=None)
     --- Get functions ---
       def getZoneNumber(self)
       def useConstProb(self)
       def getMainLevelFacies(self)
       def getFaciesInZoneModel(self)
       def getUsedGaussFieldNames(self)
       def getVariogramType(self,gaussFieldName)
       def getVariogramTypeNumber(self,gaussFieldName)
       def getMainRange(self,gaussFieldName)
       def getPerpRange(self,gaussFieldName)
       def getVertRange(self,gaussFieldName)
       def getAnisotropyAzimuthAngle(self,gaussFieldName)
       def getAnisotropyDipAngle(self,gaussFieldName)
       def getPower(self,gaussFieldName)
       def getTruncRule(self)
       def getTrendModel(self,gfName)
       def getSimBoxThickness(self)
       def getTruncationParam(self,get3DParamFunction,gridModel,realNumber)
       def debug_level(self)
       def getProbParamName(self,fName)
       def getAllProbParamForZone(self)
       def getConstProbValue(self,fName)
       def getHorizonNameForVariogramTrendMap(self)


       ---  Set functions ---
       def setZoneNumber(self,zoneNumber)
       def setVariogramType(self,gaussFieldName,variogramType)
       def setRange1(self,gaussFieldName,range1)
       def setRange2(self,gaussFieldName,range2)
       def setRange3(self,gaussFieldName,range3)
       def setAnisotropyAzimuthAngle(self,gaussFieldName,angle)
      def setAnisotropyDipAngle(self,gaussFieldName,angle)

     ---  Set functions ---
       def setZoneNumber(self,zoneNumber)
       def setVariogramType(self,gaussFieldName,variogramType)
       def setRange1(self,gaussFieldName,range1)
       def setRange2(self,gaussFieldName,range2)
       def setRange3(self,gaussFieldName,range3)
       def setAngle(self,gaussFieldName,angle)
       def setPower(self,gaussFieldName,power)
       def setUseConstProb(self)
       def setSeedForPreviewSimulation(self)
       def setMainFaciesTable(self,mainFaciesTable)
       def setSimBoxThickness(self,thickness)
       def updateGaussFieldParam(self,gfName,variogramType,range1,range2,range3,angle,power,
                                 relStdDev=0.0,trendModelObj=None)
       def removeGaussFieldParam(self,gfName)
       def updateFaciesWithProbForZone(self,faciesList,faciesProbList)
       def removeFaciesWithProbForZone(self,fName)
       def setTruncRule(self,truncRuleObj)
       def setHorizonNameForVariogramTrendMap(self,horizonNameForVariogramTrendMap)

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
       def __checkConstProbValuesAndNormalize(self)
       def __getGFIndex(self,gfName)
       def __updateGaussFieldVariogramParam(self,gfName,variogramType,range1,range2,range3,angle,power)
       def __updateGaussFieldTrendParam(self,gfName,trendModelObj,relStdDev)
    """

    def __init__(
            self, ET_Tree=None, zoneNumber=0, regionNumber=0, modelFileName=None,
            useConstProb=False, simBoxThickness=10.0, horizonNameForVariogramTrendMap=None,
            faciesProbObject=None, gaussModelObject=None, truncRuleObject=None,
            debug_level=Debug.OFF, keyResolution=100
    ):
        """
         If the object is created by reading the xml tree for model parameters, it is required that
         zoneNumber is set to a value > 0 and optionally that regionNumber is set to a value > 0.
         The modelFileName is only used for more informative error messages and should also be defined in this case.
         None of the other parameters should be defined since they are read from the xml tree.
         If regionNumber is > 0 then both zone parameter and region parameter is used to define which grid cells
         is to be used when calculating facies. If zoneNumber is 0, the region parameter is not used to
         define which grid cells to calculate facies for.
        
         If the object is not created by reading the xml tree, then the ET_Tree should be None and
         modelFileName should not be defined. Then all other parameters must be defined.
        """
        self.__className = self.__class__.__name__
        # Local variables
        self.__zoneNumber = zoneNumber
        self.__regionNumber = regionNumber
        self.__useConstProb = useConstProb
        self.__simBoxThickness = simBoxThickness

        self.__faciesProbObject = faciesProbObject
        self.__gaussModelObject = gaussModelObject

        self.__truncRule = truncRuleObject
        self.__horizonNameForVariogramTrendMap = horizonNameForVariogramTrendMap
        self.__keyResolution = keyResolution
        self.__debug_level = debug_level

        if ET_Tree is not None:
            self.__interpretXMLTree(ET_Tree, modelFileName)

    def __interpretXMLTree(self, ET_Tree, modelFileName):
        #  Get root of xml tree for model specification
        root = ET_Tree.getroot()

        # --- PrintInfo ---
        kw = 'PrintInfo'
        self.__debug_level = getIntCommand(root, kw, defaultValue=1, required=False)

        if self.__debug_level >= Debug.VERY_VERBOSE:
            print('')
            print('Debug output: Call init ' + self.__className)

        # Optimization parameters
        obj = getKeyword(root, 'Optimization', 'Root', modelFile=modelFileName, required=False)
        if obj is not None:
            useMemoization = getIntCommand(obj, 'UseMemoization', 'Optimization',
                                           minValue=0, maxValue=1, defaultValue=1,
                                           modelFile=modelFileName, required=False)

            nIntervalForProbabilityInMemoizationKey = getIntCommand(obj, 'MemoizationResolution', 'Optimization',
                                                                    minValue=100, maxValue=10000,
                                                                    defaultValue=100, modelFile=modelFileName,
                                                                    required=False)
            if useMemoization == 1:
                self.__keyResolution = nIntervalForProbabilityInMemoizationKey
            else:
                self.__keyResolution = 0

        mainFaciesTable = APSMainFaciesTable(ET_Tree, modelFileName)
        gaussFieldJobs = APSGaussFieldJobs(ET_Tree, modelFileName)

        regionNumber = 0
        zoneNumber   = 0
        zoneModels = getKeyword(root, 'ZoneModels', 'Root', modelFile=modelFileName)
        for zone in zoneModels.findall('Zone'):
            zoneNumber = int(zone.get('number'))
            if zoneNumber <= 0:
                raise ValueError('Zone number must be a positive integer number')
            
            regionNumberAsText = zone.get('regionNumber')
            if regionNumberAsText is not None:
                regionNumber = int(regionNumberAsText)
                if regionNumber < 0:
                    raise ValueError('Region number must be positive integer if region is used.\n'
                                     'Zero as region number means that regions is not used for the zone.\n'
                                     'Can not have negative region number: {}'.format(str(regionNumber))
                                     )
            else:
                regionNumber = 0
            if self.__debug_level == Debug.VERY_VERBOSE:
                    print('Debug output: Zone number: {}  Region number: {}'.format(str(zoneNumber), str(regionNumber)))
            else:
                if self.__debug_level == Debug.VERY_VERBOSE:
                    print('Debug output: Zone number: {}'.format(str(zoneNumber)))
                
            if zoneNumber == self.__zoneNumber and regionNumber == self.__regionNumber:

                useConstProb = getIntCommand(zone, 'UseConstProb', 'Zone', modelFile=modelFileName)
                self.__useConstProb = useConstProb

                kw = 'SimBoxThickness'
                simBoxThickness = getFloatCommand(zone, kw, 'Zone', minValue=0.0, modelFile=modelFileName)
                self.__simBoxThickness = simBoxThickness

                kw = 'HorizonNameVarioTrend'
                mapName = getTextCommand(zone, kw, 'Zone', modelFile=modelFileName, required=False)
                self.__horizonNameForVariogramTrendMap = mapName

                if self.__debug_level >= Debug.VERY_VERBOSE:
                    print('Debug output: From APSZoneModel: ZoneNumber:      ' + str(zoneNumber))
                    print('Debug output: From APSZoneModel: RegionNumber:    ' + str(regionNumber))
                    print('Debug output: From APSZoneModel: useConstProb:    ' + str(self.__useConstProb))
                    print('Debug output: From APSZoneModel: simBoxThickness: ' + str(self.__simBoxThickness))
                    text = 'Debug output: From APSZoneModel: Horizon name to be used for saving \n'
                    text += '              azimuth variogram trend for this zone: '
                    text += str(self.__horizonNameForVariogramTrendMap)
                    print(text)

                # Read facies probabilities
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
                if nGaussFieldInModel > nGaussFieldInZone:
                    raise ValueError(
                        'Error: In {className}\n'
                        'Error: Number of specified RMS gaussian field 3D parameters in truncation rule {nGFTruncRule}\n'
                        '       is larger than number of gauss fields {nGFModel} specified for the zone'
                        ''.format(
                            className=self.__className,
                            nGFTruncRule=str(nGaussFieldInModel),
                            nGFModel=truncRuleName
                        )
                    )
                else:
                    faciesInZone = self.__faciesProbObject.getFaciesInZoneModel()
                    gaussFieldsInZone = self.__gaussModelObject.getUsedGaussFieldNames()
                    if truncRuleName == 'Trunc3D_Bayfill':
                        self.__truncRule = Trunc3D_bayfill(
                            trRule, mainFaciesTable, faciesInZone, gaussFieldsInZone,
                            self.__debug_level, modelFileName
                        )

                    elif truncRuleName == 'Trunc2D_Angle':
                        self.__truncRule = Trunc2D_Angle(
                            trRule, mainFaciesTable, faciesInZone, gaussFieldsInZone,
                            self.__keyResolution,
                            self.__debug_level, modelFileName, self.__zoneNumber
                        )
                    elif truncRuleName == 'Trunc2D_Cubic':
                        self.__truncRule = Trunc2D_Cubic(
                            trRule, mainFaciesTable, faciesInZone, gaussFieldsInZone,
                            self.__keyResolution,
                            self.__debug_level, modelFileName, self.__zoneNumber
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

    def hasFacies(self, fName):
        return self.__faciesProbObject.hasFacies(fName)


    def getZoneNumber(self):
        return self.__zoneNumber

    def getRegionNumber(self):
        return self.__regionNumber

    def useConstProb(self) -> bool:
        return self.__useConstProb

    def getFaciesInZoneModel(self):
        return self.__faciesProbObject.getFaciesInZoneModel()

    def getUsedGaussFieldNames(self):
        return self.__gaussModelObject.getUsedGaussFieldNames()

    def getVariogramType(self, gaussFieldName):
        return copy.copy(self.__gaussModelObject.getVariogramType(gaussFieldName))

    def getVariogramTypeNumber(self, gaussFieldName):
        return self.__gaussModelObject.getVariogramTypeNumber(gaussFieldName)

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

    def getTrendModel(self, gfName):
        return self.__gaussModelObject.getTrendModel(gfName)

    def getTrendModelObject(self, gfName):
        return self.__gaussModelObject.getTrendModelObject(gfName)

    def getSimBoxThickness(self):
        return self.__simBoxThickness

#    def getTruncationParam(self, get3DParamFunction, gridModel, realNumber):
        # Input: get3DParamFunction - Function pointer for function to be applied
        #                             to get 3D parameter from RMS project. Is used
        #                             to avoid calling functions using RoxAPI here.
        #        gridModel - Pointer to grid model object in RMS
        #        NOTE: Will only call the function to read RMS parameter from
        #              truncation rules that has defined this as a possibility.
#        if not self.__truncRule.useConstTruncModelParam():
#            self.__truncRule.getTruncationParam(get3DParamFunction, gridModel, realNumber)

    def getTruncationParam(self, gridModel, realNumber):
        if not self.__truncRule.useConstTruncModelParam():
            self.__truncRule.getTruncationParam(gridModel, realNumber)

    def get_debug_level(self):
        return self.__debug_level

    def getHorizonNameForVariogramTrendMap(self):
        return copy.copy(self.__horizonNameForVariogramTrendMap)

    def getProbParamName(self, fName):
        return self.__faciesProbObject.getProbParamName(fName)

    def getAllProbParamForZone(self):
        return self.__faciesProbObject.getAllProbParamForZone()

    def getConstProbValue(self, fName):
        return self.__faciesProbObject.getConstProbValue(fName)

    def getGaussFieldsInTruncationRule(self):
        return self.__truncRule.getGaussFieldsInTruncationRule()

    def getGaussFieldIndexListInZone(self):
        return self.__truncRule.getGaussFieldIndexListInZone()
    
    def setZoneNumber(self, zoneNumber):
        self.__zoneNumber = zoneNumber
        return

    def setVariogramType(self, gaussFieldName, variogramType):
        return self.__gaussModelObject.setVariogramType(gaussFieldName, variogramType)

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

    def updateGaussFieldParam(self, gfName, variogramType, range1, range2, range3, angle, power,
                              relStdDev=0.0, trendModelObj=None):
        return self.__gaussModelObject.updateGaussFieldParam(
            gfName, variogramType, range1, range2, range3, angle, power,
            relStdDev, trendModelObj
        )

    def updateGaussFieldVariogramParam(self, gfName, variogramType, range1, range2, range3, angle, power):
        return self.__gaussModelObject.updateGaussFieldVariogramParameters(
            gfName, variogramType, range1, range2, range3, angle, power
        )

    def removeGaussFieldParam(self, gfName):
        self.__gaussModelObject.removeGaussFieldParam(gfName)

    def updateGaussFieldTrendParam(self, gfName, trendModelObj, relStdDev):
        self.__gaussModelObject.updateGaussFieldTrendParam(gfName, trendModelObj, relStdDev)

    def setTruncRule(self, truncRuleObj):
        err = 0
        if truncRuleObj is None:
            err = 1
        else:
            self.__truncRule = truncRuleObj
        return err

    def setHorizonNameForVariogramTrendMap(self, horizonNameForVariogramTrendMap):
        self.__horizonNameForVariogramTrendMap = copy.copy(horizonNameForVariogramTrendMap)

    def applyTruncations(self, probDefined, GFAlphaList, faciesReal, nDefinedCells, cellIndexDefined):

        # GFAlphaList has items =[name,valueArray]
        # Use NAME and VAL as index names
        NAME = 0
        VAL = 1

        truncObject = self.__truncRule
        debug_level = self.__debug_level
        faciesNames = self.getFaciesInZoneModel()
        nFacies = len(faciesNames)
        classNameTrunc = truncObject.getClassName()
        if len(probDefined) != nFacies:
            raise ValueError(
                'Error: In class: {}. Mismatch in input to applyTruncations '
                ''.format(self.__className)
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
                    if np.mod(i, 50000) == 0:
                        print('--- Calculate facies for cell number: ' + str(i))

                cellIndx = cellIndexDefined[i]
                # alphaCoord is the list (alpha1,alpha2,alpha3,..) of coordinate values in alpha space
                # The sequence is defined by the sequence they are specified in the model file.
                alphaCoord = []
                for gaussFieldIndx in range(nGaussFields):
                    alphaDataArray = alphaList[gaussFieldIndx]
                    alphaCoord.append(alphaDataArray[cellIndx])

                # Calculate facies realization by applying truncation rules
                fCode, fIndx = truncObject.defineFaciesByTruncRule(alphaCoord)
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
                        truncRuleName = truncObject.getClassName()
                        if truncRuleName == 'Trunc2D_Angle' or truncRuleName == 'Trunc2D_Cubic':
                            nCalc = truncObject.getNCalcTruncMap()
                            nLookup = truncObject.getNLookupTruncMap()
                            print('--- Calculate facies for cell number: {}    New truncation cubes: {}    Re-used truncation cubes: {}'
                                  ''.format(str(i), str(nCalc), str(nLookup))
                                  )
                        else:
                            print('--- Calculate facies for cell number: {}'.format(str(i)))

                elif debug_level == Debug.VERBOSE:
                    if np.mod(i, 500000) == 0:
                        print('--- Calculate facies for cell number: {}'.format(str(i)))

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
                # The sequence is defined by the sequence they are specified in the model file.
                for gaussFieldIndx in range(nGaussFields):
                    alphaDataArray = alphaList[gaussFieldIndx]
                    alphaCoord.append(alphaDataArray[cellIndx])
                # Calculate facies realization by applying truncation rules
                fCode, fIndx = truncObject.defineFaciesByTruncRule(alphaCoord)
                faciesReal[cellIndx] = fCode
                volFrac[fIndx] += 1

        if self.__debug_level >= Debug.VERBOSE:
            truncRuleName = truncObject.getClassName()
            if truncRuleName == 'Trunc2D_Angle' or truncRuleName == 'Trunc2D_Cubic':
                nCalc = truncObject.getNCalcTruncMap()
                nLookup = truncObject.getNLookupTruncMap()
                print(
                    '--- In truncation rule {} the truncation cube is recalculated {} number of times\n'
                    '    due to varying facies probabilities and previous calculated truncation cubes are re-used {} of times.\n'
                    ''.format(truncRuleName, str(nCalc), str(nLookup))
                )
                if truncRuleName == 'Trunc2D_Angle':
                    nCount = truncObject.getNCountShiftAlpha()
                    print('Debug output: Small shifts of values for orientation of facies boundary lines are done {} number of times for numerical reasons.'
                          ''.format(str(nCount)))

        for f in range(nFacies):
            volFrac[f] = volFrac[f] / float(nDefinedCells)
        return faciesReal, volFrac

    def XMLAddElement(self, parent):
        # Add command Zone and all its children
        if self.__debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: call XMLADDElement from ' + self.__className)

        tag = 'Zone'
        if self.__regionNumber <= 0:
            attribute = {'number': str(self.__zoneNumber)}
        else:
            attribute = {'number': str(self.__zoneNumber), 'regionNumber': str(self.__regionNumber)}
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
        if self.__horizonNameForVariogramTrendMap is not None:
            tag = 'HorizonNameVarioTrend'
            elem = Element(tag)
            elem.text = ' ' + self.__horizonNameForVariogramTrendMap + ' '
            zoneElement.append(elem)

        # Add child command FaciesProbForModel
        self.__faciesProbObject.XMLAddElement(zoneElement)
        # Add child command GaussField
        self.__gaussModelObject.XMLAddElement(zoneElement)
        # Add child command TruncationRule at end of the child list for
        self.__truncRule.XMLAddElement(zoneElement)

    def simGaussFieldWithTrendAndTransform(
            self, simBoxXsize, simBoxYsize, simBoxZsize,
            gridNX, gridNY, gridNZ, gridAzimuthAngle, crossSectionType, crossSectionIndx):
        return self.__gaussModelObject.simGaussFieldWithTrendAndTransform(
            simBoxXsize, simBoxYsize, simBoxZsize,
            gridNX, gridNY, gridNZ, gridAzimuthAngle, crossSectionType, crossSectionIndx
        )
