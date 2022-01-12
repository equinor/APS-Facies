#!/bin/env python
# -*- coding: utf-8 -*-
import copy
from enum import Enum
from typing import List, Optional, Union, Tuple
from warnings import warn
from xml.etree.ElementTree import Element, ElementTree

import numpy as np

from aps.algorithms.APSFaciesProb import APSFaciesProb
from aps.algorithms.APSGaussModel import APSGaussModel, GaussianFieldName, GaussianField, Trend
from aps.algorithms.APSMainFaciesTable import APSMainFaciesTable
from aps.algorithms.Memoization import MemoizationItem, RoundOffConstant
from aps.algorithms.trend import Trend3D_hyperbolic, Trend3D_elliptic, Trend3D_linear, Trend3D_rms_param
from aps.algorithms.truncation_rules import Trunc2D_Angle, Trunc2D_Cubic, Trunc3D_bayfill
from aps.algorithms.properties import CrossSection
from aps.utils.constants.simple import Debug, VariogramType, Conform
from aps.utils.containers import FmuAttribute
from aps.utils.types import FaciesName
from aps.algorithms.truncation_rules.types import TruncationRule
from aps.utils.xmlUtils import (
    getFloatCommand,
    getIntCommand,
    getKeyword,
    getTextCommand,
    getBoolCommand,
    get_region_number,
)




class APSZoneModel:
    """
    Keep data structure for a zone

    Public member functions:
       def __init__(self, ET_Tree=None, zoneNumber=0, regionNumber=0, modelFileName=None,
            useConstProb=False, simBoxThickness=10.0,
            faciesProbObject=None, gaussModelObject=None, truncRuleObject=None,
            debug_level=Debug.OFF, keyResolution=100)

     --- Properties ---
       debug_level
       zone_number
       region_number
       used_gaussian_field_names

     --- Get functions ---
       def getVariogramType(self,gaussFieldName)
       def getVariogramTypeNumber(self,gaussFieldName)
       def getMainRange(self,gaussFieldName)
       def getPerpRange(self,gaussFieldName)
       def getVertRange(self,gaussFieldName)
       def getAzimuthAngle(self,gaussFieldName)
       def getDipAngle(self,gaussFieldName)
       def getPower(self,gaussFieldName)
       def getTruncRule(self)
       def getTrendModel(self,gfName)
       def getTrendModelObject(self, gfName)
       def getProbParamName(self,fName)
       def getAllProbParamForZone(self)
       def getConstProbValue(self,fName)
       def getGaussFieldsInTruncationRule(self)
       def getGaussFieldIndexListInZone(self)

       ---  Set functions ---
       def setVariogramType(self,gaussFieldName,variogramType)
       def setMainRange(self,gaussFieldName,range1)
       def setPerpRange(self,gaussFieldName,range2)
       def setVertRange(self,gaussFieldName,range3)
       def setAzimuthAngle(self,gaussFieldName,angle)
       def setDipAngle(self,gaussFieldName,angle)
       def setPower(self, gaussFieldName, power)
       def setUseConstProb(self, useConstProb)
       def setSeedForPreviewSimulation(self, gfName, seed)
       def setSimBoxThickness(self,thickness)
       def updateGaussFieldParam(self,gfName,variogramType,range1,range2,range3,angle,power,
                                 relStdDev=0.0,trendModelObj=None)
       def updateGaussFieldVariogramParam(self, gfName, variogramType, range1, range2, range3, angle, power)
       def removeGaussFieldParam(self,gfName)
       def updateGaussFieldTrendParam(self, gfName, trendModelObj, relStdDev)
       def updateFaciesWithProbForZone(self,faciesList,faciesProbList)
       def removeFaciesWithProbForZone(self,fName)
       def setTruncRule(self,truncRuleObj)

     ---  Calculate function ---
       def applyTruncations(self,probDefined,alpha_fields,faciesReal,nDefinedCells,cellIndexDefined)
       def applyTruncations_vectorized(self, probDefined, alpha_fields, faciesReal, nDefinedCells, cellIndexDefined)
       def simGaussFieldWithTrendAndTransform(
            self, (simBoxXsize, simBoxYsize, simBoxZsize),
            (gridNX, gridNY, gridNZ), gridAzimuthAngle, crossSectionType, crossSectionIndx)


     ---  write XML tree ---
       def XMLAddElement(self,parent)
       def getZoneNumber(self)

     --- Check functions ---
       def hasFacies(self,fName)
       def isMainLevelModel(self)

    Private member functions:
       def __interpretXMLTree(self, ET_Tree, modelFileName)
       def __checkConstProbValuesAndNormalize(self)
       def __updateGaussFieldVariogramParam(self,gfName,variogramType,range1,range2,range3,angle,power)
       def __updateGaussFieldTrendParam(self,gfName,trendModelObj,relStdDev)
    """

    def __init__(
        self,
        ET_Tree: Optional[ElementTree] = None,
        zoneNumber: int = 0,
        regionNumber: int = 0,
        modelFileName: Optional[str] = None,
        useConstProb: bool = False,
        simBoxThickness: float = 10.0,
        faciesProbObject: Optional[APSFaciesProb] = None,
        gaussModelObject: Optional[APSGaussModel] = None,
        truncRuleObject: Optional[TruncationRule] = None,
        debug_level: Debug = Debug.OFF,
        keyResolution: int = 100,
        grid_layout: Optional[Union[str, Conform]] = None,
    ) -> None:
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
        self.__trunc_rule = truncRuleObject
        self.__zoneNumber = zoneNumber
        self.__regionNumber = regionNumber
        self.__useConstProb = bool(useConstProb)
        self.__simBoxThickness = simBoxThickness

        self.__faciesProbObject = faciesProbObject
        self.__gaussModelObject = gaussModelObject

        self.__keyResolution = keyResolution
        self.__debug_level = debug_level
        self.grid_layout = grid_layout

        if ET_Tree is not None:
            self.__interpretXMLTree(ET_Tree, modelFileName, debug_level=self.__debug_level)

    def __interpretXMLTree(self, ET_Tree, modelFileName,debug_level=Debug.OFF):
        ''' The input XML tree is interpreted and values put into the data structure.'''
        #  Get root of xml tree for model specification
        root = ET_Tree.getroot()

        self.__debug_level = debug_level
        if self.__debug_level >= Debug.VERY_VERBOSE:
            print(f'\n--- Call init {self.__className}')

        # Optimization parameters
        obj = getKeyword(root, 'Optimization', 'Root', modelFile=modelFileName, required=False)
        if obj is not None:
            useMemoization = getIntCommand(
                obj, 'UseMemoization', 'Optimization',
                minValue=0, maxValue=1, defaultValue=1, modelFile=modelFileName, required=False
            )

            nIntervalForProbabilityInMemoizationKey = getIntCommand(
                obj, 'MemoizationResolution', 'Optimization',
                minValue=50, maxValue=1000, defaultValue=100, modelFile=modelFileName, required=False
            )
            if useMemoization == 1:
                self.__keyResolution = nIntervalForProbabilityInMemoizationKey
            else:
                self.__keyResolution = 0

        mainFaciesTable = APSMainFaciesTable(ET_Tree, modelFileName)

        zone_models = getKeyword(root, 'ZoneModels', 'Root', modelFile=modelFileName)
        for zone in zone_models.findall('Zone'):
            zone_number = int(zone.get('number'))
            if zone_number <= 0:
                raise ValueError('Zone number must be a positive integer number')

            region_number = get_region_number(zone)

            grid_layout = getTextCommand(zone, 'GridLayout', 'Zone', modelFile=modelFileName, required=False)
            self.grid_layout = grid_layout

            if zone_number == self.zone_number and region_number == self.region_number:

                useConstProb = getBoolCommand(zone, 'UseConstProb', 'Zone', model_file_name=modelFileName)
                self.__useConstProb = useConstProb

                kw = 'SimBoxThickness'
                simBoxThickness = getFloatCommand(zone, kw, 'Zone', minValue=0.0, modelFile=modelFileName)
                self.__simBoxThickness = simBoxThickness

                if self.__debug_level >= Debug.VERY_VERBOSE:
                    print(
                        f'--- From APSZoneModel: ZoneNumber:       {zone_number}\n'
                        f'--- From APSZoneModel: RegionNumber:     {region_number}\n'
                        f'--- From APSZoneModel: useConstProb:     {self.__useConstProb}\n'
                        f'--- From APSZoneModel: simBoxThickness:  {self.__simBoxThickness}\n'
                    )

                # Read facies probabilities
                self.__faciesProbObject = APSFaciesProb(
                    zone, mainFaciesTable, modelFileName,
                    self.__debug_level, self.__useConstProb, self.zone_number
                )
                # Read Gauss Fields model parameters
                self.__gaussModelObject = APSGaussModel(
                    zone, mainFaciesTable, modelFileName,
                    self.__debug_level, self.__simBoxThickness
                )

                # Read truncation rule for zone model
                trRule = zone.find('TruncationRule')
                if trRule is None:
                    raise NameError(
                        f'Error when reading model file: {modelFileName}\n'
                        'Error: Missing keyword TruncationRule '
                        'under keyword Zone'
                    )
                truncRuleName = trRule[0].tag
                if self.__debug_level >= Debug.VERY_VERBOSE:
                    print(f'--- TruncRuleName: {truncRuleName}')

                nGaussFieldInModel = int(trRule[0].get('nGFields'))
                if nGaussFieldInModel > self.__gaussModelObject.num_gaussian_fields:
                    raise ValueError(
                        f'Error: In {self.__className}\n'
                        f'Error: Number of specified RMS gaussian field 3D parameters in truncation rule {nGaussFieldInModel}\n'
                        f'       is larger than number of gauss fields {truncRuleName} specified for the zone'
                    )
                else:
                    faciesInZone = self.__faciesProbObject.facies_in_zone_model
                    gaussFieldsInZone = self.__gaussModelObject.used_gaussian_field_names
                    if truncRuleName == 'Trunc3D_Bayfill':
                        self.truncation_rule = Trunc3D_bayfill(
                            trRule, mainFaciesTable, faciesInZone, gaussFieldsInZone,
                            self.debug_level, modelFileName
                        )

                    elif truncRuleName == 'Trunc2D_Angle':
                        self.truncation_rule = Trunc2D_Angle(
                            trRule, mainFaciesTable, faciesInZone, gaussFieldsInZone,
                            self.key_resolution,
                            self.debug_level, modelFileName, self.zone_number
                        )
                    elif truncRuleName == 'Trunc2D_Cubic':
                        self.truncation_rule = Trunc2D_Cubic(
                            trRule, mainFaciesTable, faciesInZone, gaussFieldsInZone,
                            self.key_resolution,
                            self.debug_level, modelFileName, self.zone_number
                        )
                    else:
                        raise NameError(
                            f'Error in {self.__className}\n'
                            f'Error: Specified truncation rule name: {truncRuleName}\n'
                            '       is not implemented.'
                        )

                    if self.debug_level >= Debug.VERY_VERBOSE:
                        print(
                            '--- APSZoneModel:\n'
                            f'--- Truncation rule for current zone: {self.truncation_rule.getClassName()}'
                        )
                        print(
                            '--- APSZoneModel: Facies in truncation rule:'
                            f' {self.truncation_rule.getFaciesInTruncRule()}'
                        )

                break
                # End if zone number
        # End for zone

    def hasFacies(self, fName: FaciesName) -> bool:
        return self.__faciesProbObject.hasFacies(fName)

    @property
    def uses_region(self) -> bool:
        return self.region_number > 0

    @property
    def grid_layout(self) -> Optional[Conform]:
        return self._grid_layout

    @grid_layout.setter
    def grid_layout(self, value: Optional[Conform]):
        if value is not None:
            value = Conform(value)
        self._grid_layout = value

    @property
    def zone_number(self) -> int:
        return self.__zoneNumber

    @zone_number.setter
    def zone_number(self, value: int):
        self.__zoneNumber = value

    @property
    def region_number(self) -> int:
        return self.__regionNumber

    @property
    def key_resolution(self) -> int:
        return self.__keyResolution

    @property
    def use_constant_probabilities(self) -> bool:
        """Info about whether constant probabilities, or probability cubes are used."""
        return self.__useConstProb

    @property
    def facies_in_zone_model(self) -> List[str]:
        return self.__faciesProbObject.facies_in_zone_model

    @property
    def used_gaussian_field_names(self) -> List[GaussianFieldName]:
        if self.__gaussModelObject:
            return self.__gaussModelObject.used_gaussian_field_names
        return []

    def getVariogramType(self, gaussFieldName: GaussianFieldName) -> VariogramType:
        return copy.copy(self.__gaussModelObject.getVariogramType(gaussFieldName))

    def getVariogramTypeNumber(self, gaussFieldName: GaussianFieldName) -> int:
        return self.__gaussModelObject.getVariogramTypeNumber(gaussFieldName)

    def getMainRange(self, gaussFieldName: GaussianFieldName) -> float:
        return self.__gaussModelObject.getMainRange(gaussFieldName)

    def getMainRangeFmuUpdatable(self, gaussFieldName: GaussianFieldName) -> bool:
        return self.__gaussModelObject.getMainRangeFmuUpdatable(gaussFieldName)

    def getPerpRange(self, gaussFieldName: GaussianFieldName) -> float:
        return self.__gaussModelObject.getPerpRange(gaussFieldName)

    def getPerpRangeFmuUpdatable(self, gaussFieldName: GaussianFieldName) -> bool:
        return self.__gaussModelObject.getPerpRangeFmuUpdatable(gaussFieldName)

    def getVertRange(self, gaussFieldName: GaussianFieldName) -> float:
        return self.__gaussModelObject.getVertRange(gaussFieldName)

    def getVertRangeFmuUpdatable(self, gaussFieldName: GaussianFieldName) -> bool:
        return self.__gaussModelObject.getVertRangeFmuUpdatable(gaussFieldName)

    def getAzimuthAngle(self, gaussFieldName: GaussianFieldName) -> float:
        return self.__gaussModelObject.getAzimuthAngle(gaussFieldName)

    def getAzimuthAngleFmuUpdatable(self, gaussFieldName: GaussianFieldName) -> bool:
        return self.__gaussModelObject.getAzimuthAngleFmuUpdatable(gaussFieldName)

    def getDipAngle(self, gaussFieldName: GaussianFieldName) -> float:
        return self.__gaussModelObject.getDipAngle(gaussFieldName)

    def getDipAngleFmuUpdatable(self, gaussFieldName: GaussianFieldName) -> bool:
        return self.__gaussModelObject.getDipAngleFmuUpdatable(gaussFieldName)

    def getPower(self, gaussFieldName: GaussianFieldName) -> float:
        return self.__gaussModelObject.getPower(gaussFieldName)

    def getPowerFmuUpdatable(self, gaussFieldName: GaussianFieldName) -> bool:
        return self.__gaussModelObject.getPowerFmuUpdatable(gaussFieldName)

    @property
    def truncation_rule(self) -> TruncationRule:
        return self.__trunc_rule

    @truncation_rule.setter
    def truncation_rule(self, value: Optional[TruncationRule]):
        if value is None:
            warn('The truncation rule cannot be None for a zone model')
        self.__trunc_rule = value

    @property
    def gaussian_fields(self) -> List[GaussianField]:
        if self.__gaussModelObject:
            return self.__gaussModelObject.fields
        return []

    @property
    def sim_box_thickness(self) -> float:
        return self.__simBoxThickness

    @sim_box_thickness.setter
    def sim_box_thickness(self, thickness: float):
        self.__simBoxThickness = thickness

    def get_gaussian_field(self, name: GaussianFieldName) -> Optional[GaussianField]:
        return self.__gaussModelObject.get_model(name)

    def getTrendModel(self, gfName: GaussianFieldName) -> Union[
            Tuple[None, None, None, None],
            Tuple[bool, Union[Trend3D_hyperbolic, Trend3D_elliptic, Trend3D_linear, Trend3D_rms_param], float, bool],
        ]:
        return self.__gaussModelObject.getTrendModel(gfName)

    def getTrendModelObject(self, gfName: GaussianFieldName) -> Optional[Trend]:
        return self.__gaussModelObject.getTrendModelObject(gfName)

    def hasTrendModel(self, gfName: GaussianFieldName) -> bool:
        return self.__gaussModelObject.hasTrendModel(gfName)

    def getTruncationParam(self, gridModel: str, realNumber: int):
        if not self.truncation_rule.useConstTruncModelParam():
            self.truncation_rule.getTruncationParam(gridModel, realNumber)

    @property
    def debug_level(self) -> Debug:
        return self.__debug_level

    @debug_level.setter
    def debug_level(self, value: Debug):
        self.__debug_level = value

    def getProbParamName(self, fName: str) -> str:
        return self.__faciesProbObject.getProbParamName(fName)

    def getAllProbParamForZone(self):
        return self.__faciesProbObject.getAllProbParamForZone()

    def getConstProbValue(self, fName):
        return self.__faciesProbObject.getConstProbValue(fName)

    @property
    def gaussian_fields_in_truncation_rule(self) -> List[str]:
        return self.truncation_rule.getGaussFieldsInTruncationRule()

    def getGaussFieldsInTruncationRule(self) -> List[str]:
        return self.truncation_rule.getGaussFieldsInTruncationRule()

    def getGaussFieldIndexListInZone(self) -> List[int]:
        return self.truncation_rule.getGaussFieldIndexListInZone()

    def setVariogramType(self, gaussFieldName: GaussianFieldName, variogramType: VariogramType) -> None:
        return self.__gaussModelObject.setVariogramType(gaussFieldName, variogramType)

    def setMainRange(self, gaussFieldName: GaussianFieldName, range1: float) -> None:
        return self.__gaussModelObject.setMainRange(gaussFieldName, range1)

    def setMainRangeFmuUpdatable(self, gaussFieldName: GaussianFieldName, value: bool) -> None:
        return self.__gaussModelObject.setMainRangeFmuUpdatable(gaussFieldName, value)

    def setPerpRange(self, gaussFieldName: GaussianFieldName, range2: float) -> None:
        return self.__gaussModelObject.setPerpRange(gaussFieldName, range2)

    def setPerpRangeFmuUpdatable(self, gaussFieldName: GaussianFieldName, value: bool) -> None:
        return self.__gaussModelObject.setPerpRangeFmuUpdatable(gaussFieldName, value)

    def setVertRange(self, gaussFieldName: GaussianFieldName, range3: float) -> None:
        return self.__gaussModelObject.setVertRange(gaussFieldName, range3)

    def setVertRangeFmuUpdatable(self, gaussFieldName: GaussianFieldName, value: bool) -> None:
        return self.__gaussModelObject.setVertRangeFmuUpdatable(gaussFieldName, value)

    def setAzimuthAngle(self, gaussFieldName: GaussianFieldName, angle: float) -> None:
        return self.__gaussModelObject.setAzimuthAngle(gaussFieldName, angle)

    def setAzimuthAngleFmuUpdatable(self, gaussFieldName: GaussianFieldName, value: bool) -> None:
        return self.__gaussModelObject.setAzimuthAngleFmuUpdatable(gaussFieldName, value)

    def setDipAngle(self, gaussFieldName: GaussianFieldName, angle: float) -> None:
        return self.__gaussModelObject.setDipAngle(gaussFieldName, angle)

    def setDipAngleFmuUpdatable(self, gaussFieldName: GaussianFieldName, value: bool) -> None:
        return self.__gaussModelObject.setDipAngleFmuUpdatable(gaussFieldName, value)

    def setPower(self, gaussFieldName: GaussianFieldName, power: float) -> None:
        return self.__gaussModelObject.setPower(gaussFieldName, power)

    def setPowerFmuUpdatable(self, gaussFieldName: GaussianFieldName, value: bool) -> None:
        return self.__gaussModelObject.setPowerFmuUpdatable(gaussFieldName, value)

    def setRelStdDev(self, gaussFieldName, relStdDev):
        return self.__gaussModelObject.setRelStdDev(gaussFieldName, relStdDev)

    def setRelStdDevFmuUpdatable(self, gaussFieldName, value):
        return self.__gaussModelObject.setRelStdDevFmuUpdatable(gaussFieldName, value)

    def setUseConstProb(self, useConstProb):
        self.__useConstProb = useConstProb

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

    def applyTruncations(self, probDefined, alpha_fields, faciesReal, cellIndexDefined):
        ''' This function calculate the truncations. It calculates facies realization for all grid cells that are defined in cellIndexDefined.
            The input facies probabilities and transformed gauss fields are used together with the truncation rule.'''

        nDefinedCells = len(cellIndexDefined)
        debug_level = self.__debug_level
        faciesNames = self.facies_in_zone_model
        nFacies = len(faciesNames)
        classNameTrunc = self.truncation_rule.getClassName()
        if len(probDefined) != nFacies:
            raise ValueError(
                'Error: In class: {}. Mismatch in input to applyTruncations '
                ''.format(self.__className)
            )

        useConstTruncParam = self.truncation_rule.useConstTruncModelParam()
        nGaussFields = len(alpha_fields)
        faciesProb = np.zeros(nFacies, dtype=np.float32)
        volFrac = np.zeros(nFacies, dtype=np.float32)
        if debug_level >= Debug.VERBOSE:
            print(f'-- Truncation rule: {classNameTrunc}')

        alphaList = []
        if self.__useConstProb and useConstTruncParam:
            # Constant probability
            if debug_level >= Debug.VERY_VERBOSE:
                print('--- Using spatially constant probabilities for facies.')

            for f in range(nFacies):
                faciesProb[f] = probDefined[f]

            if self.debug_level >= Debug.VERY_VERBOSE:
                print(f'--- faciesProb: {faciesProb}')

            for gfName, alphaDataArray in alpha_fields.items():
                alphaList.append(alphaDataArray)
                if debug_level >= Debug.VERY_VERBOSE:
                    print(f'--- Use gauss fields: {gfName}')

            # Calculate truncation rules
            # The truncation map/cube is constant and does not vary from cell to cell
            self.truncation_rule.setTruncRule(faciesProb)

            for i in range(nDefinedCells):
                if debug_level == Debug.VERBOSE:
                    if np.mod(i, 500000) == 0:
                        if i == 0:
                            print('-- Calculate facies')
                        else:
                            print(f'-- Calculate facies for cell number: {i}')
                elif debug_level >= Debug.VERY_VERBOSE:
                    if np.mod(i, 50000) == 0:
                        if i == 0:
                            print('--- Calculate facies')
                        else:
                            print(f'--- Calculate facies for cell number: {i}')

                cellIndx = cellIndexDefined[i]
                # alphaCoord is the list (alpha1,alpha2,alpha3,..) of coordinate values in alpha space
                # The sequence is defined by the sequence they are specified in the model file.
                alphaCoord = []
                for gaussFieldIndx in range(nGaussFields):
                    alphaDataArray = alphaList[gaussFieldIndx]
                    alphaValue = alphaDataArray[cellIndx] if alphaDataArray is not None else -1.0
                    alphaCoord.append(alphaValue)

                # Calculate facies realization by applying truncation rules
                fCode, fIndx = self.truncation_rule.defineFaciesByTruncRule(alphaCoord)
                faciesReal[cellIndx] = fCode
                volFrac[fIndx] += 1

        else:
            if debug_level >= Debug.VERY_VERBOSE:
                print(
                    '--- Using spatially varying probabilities and/or '
                    'truncation parameters for facies.'
                )

            for gfName, alphaDataArray in alpha_fields.items():
                alphaList.append(alphaDataArray)
                if debug_level >= Debug.VERY_VERBOSE:
                    print(f'--- Use gauss fields: {gfName} ')

            for i in range(nDefinedCells):
                if debug_level >= Debug.VERY_VERBOSE and np.mod(i, 50000) == 0 and i == 0 or debug_level < Debug.VERY_VERBOSE and debug_level == Debug.VERBOSE and np.mod(i, 500000) == 0 and i == 0:
                    print('--- Calculate facies')
                elif debug_level >= Debug.VERY_VERBOSE and np.mod(i, 50000) == 0 or debug_level < Debug.VERY_VERBOSE and debug_level == Debug.VERBOSE and np.mod(i, 500000) == 0:
                    print(f'--- Calculate facies for cell number: {i}')
                for f in range(nFacies):
                    faciesProb[f] = probDefined[f] if self.__useConstProb else probDefined[f][i]
                # Calculate truncation rules
                # The truncation map/cube vary from cell to cell.
                cellIndx = cellIndexDefined[i]
                self.truncation_rule.setTruncRule(faciesProb, cellIndx)

                alphaCoord = []
                for gaussFieldIndx in range(nGaussFields):
                    alphaDataArray = alphaList[gaussFieldIndx]
                    alphaValue = alphaDataArray[cellIndx] if alphaDataArray is not None else -1.0
                    alphaCoord.append(alphaValue)
                # Calculate facies realization by applying truncation rules
                fCode, fIndx = self.truncation_rule.defineFaciesByTruncRule(alphaCoord)
                faciesReal[cellIndx] = fCode
                volFrac[fIndx] += 1

        if self.__debug_level >= Debug.VERY_VERBOSE:
            truncRuleName = self.truncation_rule.getClassName()
            if truncRuleName != 'Trunc3D_bayfill':
                nCount = self.truncation_rule.getNCountShiftAlpha()
                print(
                    f'--- In truncation rule {truncRuleName} small shifts of values '
                    'for orientation of facies boundary lines\n'
                    f'    are done {nCount} number of times for numerical reasons.'
                )

        for f in range(nFacies):
            volFrac[f] = volFrac[f] / float(nDefinedCells)
        return faciesReal, volFrac

    def applyTruncations_vectorized(self, probDefined, alpha_fields, faciesReal, cellIndexDefined):
        ''' This function calculate the truncations. It calculates facies realization for all grid cells that are defined in cellIndexDefined.
            The input facies probabilities and transformed gauss fields are used together with the truncation rule.'''

        debug_level = self.__debug_level
        order_index = self.truncation_rule.getOrderIndex()
        faciesNames = self.facies_in_zone_model
        nFacies = len(faciesNames)
        if len(probDefined) != nFacies:
            raise ValueError(f'Error: In class: {self.__className}. Mismatch in input to applyTruncations ')

        useConstTruncParam = self.truncation_rule.useConstTruncModelParam()
        if not useConstTruncParam:
            raise IOError(
                'Cannot use optimization if the truncation parameters  (angles) are not constant in non-cubic rule'
            )

        volFrac = np.zeros(nFacies, dtype=np.float32)

        if debug_level >= Debug.VERBOSE:
            print(f'-- Truncation rule: {self.truncation_rule.getClassName()}')
            for gfName, alphaDataArray in alpha_fields.items():
                print(f'-- Use gauss fields:{gfName}')

        nGaussFields, nDefinedCells = len(alpha_fields), len(cellIndexDefined)

        gaussFieldIndx = 0
        if self.__useConstProb:
            # Constant probability
            if debug_level >= Debug.VERBOSE:
                print('-- Using spatially constant probabilities for facies.')

            faciesProb = np.zeros(nFacies, dtype=np.float32)
            for f in range(nFacies):
                faciesProb[f] = probDefined[f]

            if debug_level >= Debug.VERY_VERBOSE:
                print(f'--- faciesProb: {faciesProb} ')
                print('---  Calculate truncation map/cube')
            # Calculate truncation rules
            # The truncation map/cube is constant and does not vary from cell to cell
            self.truncation_rule.setTruncRule(faciesProb)

            # Alpha vectors for the selected cells for current zone or (zone,region) combination
            alpha_coord_vectors = np.zeros((nDefinedCells, nGaussFields), dtype=np.float64)
            for gfName, alphaDataArray in alpha_fields.items():
                if alphaDataArray is None:
                    # This gauss field is not used for this zone, but numpy vector operations require that the vector exists
                    alpha_coord_vectors[:, gaussFieldIndx] = -1
                else:
                    alpha_coord_vectors[:, gaussFieldIndx] = alphaDataArray[cellIndexDefined]
                gaussFieldIndx += 1

            fCode_vector, fIndx_vector = self.truncation_rule.defineFaciesByTruncRule_vectorized(alpha_coord_vectors)

            # Facies codes for the selected cells are updated om faciesReal
            faciesReal[cellIndexDefined] = fCode_vector

            # Volume fraction of the different facies
            for i in range(nFacies):
                fIndx = order_index[i]
                # Number of grid cells having the specified facies
                volFrac[fIndx] = len(fIndx_vector[fIndx_vector == fIndx])

        else:
            # Varying probability from cell to cell and / or
            # varying truncation parameter from cell to cell
            if debug_level >= Debug.VERBOSE:
                print('-- Using spatially varying probabilities for facies.')
            faciesProb = np.zeros((nDefinedCells, nFacies), dtype=np.float32)

            for f in range(nFacies):
                faciesProb[:, f] = probDefined[f]

            # Alpha vectors for the selected cells for current zone or (zone,region) combination
            alpha_coord_vectors = np.zeros((nDefinedCells, nGaussFields), dtype=np.float32)
            for gfName, alphaDataArray in alpha_fields.items():
                if alphaDataArray is None:
                    # This gauss field is not used for this zone, but numpy vector operations require that the vector exists
                    alpha_coord_vectors[:, gaussFieldIndx] = -1
                else:
                    alpha_coord_vectors[:, gaussFieldIndx] = alphaDataArray[cellIndexDefined]
                gaussFieldIndx += 1

            # Calculate how many different truncation maps are necessary and add a set of grid cell indices to each item
            memo, num_maps = self.findDistinctTruncationCubes(faciesProb, nDefinedCells, nFacies)

            nCells = 0
            count_unique_truncation_cubes = 0
            if num_maps < 0.2 * nDefinedCells:
                # Use vectorization and look up facies for all cells having the same truncation cube at once
                if debug_level >= Debug.VERY_VERBOSE:
                    print('--- Using vectorization optimization')
                count_single_cell_truncation_cubes = 0
                for key, item in memo.items():
                    # Calculate truncation map
                    faciesProb = np.array(key)
                    self.truncation_rule.setTruncRule(faciesProb)
                    count_unique_truncation_cubes += 1
                    # Lookup facies
                    cell_indices_trunc_rule = item.get_cell_indices()
                    if len(cell_indices_trunc_rule) > 1:
                        # More than one cell having the same truncation cube
                        alpha_coord_selected = alpha_coord_vectors[cell_indices_trunc_rule, :]
                        faciesCode_vector, fIndx_vector = self.truncation_rule.defineFaciesByTruncRule_vectorized(
                            alpha_coord_selected)

                        # Facies codes for the selected cells are updated om faciesReal
                        faciesReal[cellIndexDefined[cell_indices_trunc_rule]] = faciesCode_vector

                        nCells += len(cell_indices_trunc_rule)
                        # Volume fraction of the different facies
                        for i in range(nFacies):
                            fIndx = order_index[i]
                            # Number of grid cells having the specified facies
                            volFrac[fIndx] += len(fIndx_vector[fIndx_vector == fIndx])
                    else:
                        # The truncation cube is for one cell only.
                        count_single_cell_truncation_cubes += 1
                        nCells += 1
                        index = cell_indices_trunc_rule[0]
                        alpha_coord = alpha_coord_vectors[index, :]
                        faciesCode, fIndx = self.truncation_rule.defineFaciesByTruncRule(alpha_coord)
                        faciesReal[cellIndexDefined[index]] = faciesCode
                        volFrac[fIndx] += 1

                    if debug_level >= Debug.VERY_VERBOSE:
                        if np.mod(nCells, 50000) == 0:
                            if nCells == 0:
                                print('--- Calculate facies')
                            else:
                                print(f'--- Calculate facies for cell number: {nCells}')
                    elif debug_level == Debug.VERBOSE:
                        if np.mod(nCells, 500000) == 0:
                            if nCells == 0:
                                print('-- Calculate facies')
                            else:
                                print(f'-- Calculate facies for cell number: {nCells}')

                if debug_level >= Debug.VERY_VERBOSE:
                    print(
                        '--- Number of cells where the truncation map is not '
                        f'shared with other cells is {count_single_cell_truncation_cubes} '
                        f'out of a total of {nDefinedCells} cells.'
                    )
                    print(
                        '--- Number of different truncation cubes '
                        f'is {count_unique_truncation_cubes} out of a total '
                        f'of {nDefinedCells} cells.'
                    )
            else:
                # Don't use vectorization and look up facies for all cells one by one.
                if debug_level >= Debug.VERY_VERBOSE:
                    print('--- No vectorization optimization')
                for key, item in memo.items():
                    # Calculate truncation map
                    faciesProb = np.array(key)
                    self.truncation_rule.setTruncRule(faciesProb)
                    count_unique_truncation_cubes += 1
                    # Lookup facies
                    cell_indices_trunc_rule = item.get_cell_indices()
                    for index in cell_indices_trunc_rule:
                        nCells += 1
                        alpha_coord = alpha_coord_vectors[index, :]
                        faciesCode, fIndx = self.truncation_rule.defineFaciesByTruncRule(alpha_coord)
                        faciesReal[cellIndexDefined[index]] = faciesCode
                        volFrac[fIndx] += 1

                        if debug_level >= Debug.VERY_VERBOSE:
                            if np.mod(nCells, 50000) == 0:
                                if nCells == 0:
                                    print('--- Calculate facies')
                                else:
                                    print(f'--- Calculate facies for cell number: {nCells}')
                        elif debug_level == Debug.VERBOSE:
                            if np.mod(nCells, 500000) == 0:
                                if nCells == 0:
                                    print('-- Calculate facies')
                                else:
                                    print(f'-- Calculate facies for cell number: {nCells}')

                assert nCells == nDefinedCells

            if debug_level >= Debug.VERY_VERBOSE:
                truncRuleName = self.truncation_rule.getClassName()
                if truncRuleName == 'Trunc2D_Angle':
                    nCount = self.truncation_rule.getNCountShiftAlpha()
                    print(
                        f'--- In truncation rule {truncRuleName} small shifts '
                        'of values for orientation of facies boundary lines\n'
                        f'    are done {nCount} number of times for numerical reasons.'
                    )

        for f in range(nFacies):
            volFrac[f] = volFrac[f] / float(nDefinedCells)
        return faciesReal, volFrac

    def XMLAddElement(self, parent: Element, fmu_attributes: List[FmuAttribute]) -> None:
        ''' Add command Zone and all its children to the XML tree'''
        if self.debug_level >= Debug.VERY_VERY_VERBOSE:
            print(f'--- call XMLADDElement from {self.__className}')

        tag = 'Zone'
        if self.region_number <= 0:
            attribute = {'number': str(self.zone_number)}
        else:
            attribute = {'number': str(self.zone_number), 'regionNumber': str(self.region_number)}
        elem = Element(tag, attribute)
        zoneElement = elem
        parent.append(zoneElement)

        # Add proportionality
        if self.grid_layout:
            elem = Element('GridLayout')
            elem.text = self.grid_layout.value
            zoneElement.append(elem)

        # Add child command UseConstProb
        tag = 'UseConstProb'
        elem = Element(tag)
        elem.text = f' {int(self.__useConstProb)} '
        zoneElement.append(elem)

        # Add child command SimBoxThickness
        tag = 'SimBoxThickness'
        elem = Element(tag)
        elem.text = f' {self.__simBoxThickness} '
        zoneElement.append(elem)

        # Add child command FaciesProbForModel
        self.__faciesProbObject.XMLAddElement(zoneElement)
        # Add child command GaussField
        self.__gaussModelObject.XMLAddElement(zoneElement, self.zone_number, self.region_number, fmu_attributes)
        # Add child command TruncationRule at end of the child list for
        self.truncation_rule.XMLAddElement(zoneElement, self.zone_number, self.region_number, fmu_attributes)

    def simGaussFieldWithTrendAndTransform(
        self,
        simulation_box_size: Tuple[float, float, float],
        grid_size: Tuple[int, int, int],
        gridAzimuthAngle: float,
        crossSection: CrossSection,
        simulation_box_origin,
    ) -> List[GaussianField]:
        """ Simulate 2D gauss field using specified trend"""
        return self.__gaussModelObject.simGaussFieldWithTrendAndTransform(
            simulation_box_size, grid_size, gridAzimuthAngle, crossSection, simulation_box_origin
        )

    def findDistinctTruncationCubes(self, probabilities, num_cells, num_facies):
        # probabilities_for_selected_grid_cells[cell, facies]
        resolution = self.__keyResolution
        if self.__keyResolution <= 0:
            # The value used when memoization is not used
            resolution = 100

        dValue = 1.0 / resolution
        # num_defined_cells = len(cell_index_defined)
        # for i in range(num_defined_cells):
        #    for j in range(num_facies):
        #        facieProbNew[i,j] = int(probabilities[i,j] * resolution + 0.5) * dValue

        # Round off to nearest number that is a multiple of 1/resolution.
        pNew = probabilities * resolution + 0.5
        pNewInt = pNew.astype(int)
        probabilities = pNewInt * dValue

        # Check if the normalization is more or less than 1
        # If so, modify the probability with largest value up/down by an amount equal to 1/resolution
        # Repeat this two times if necessary
        sumProb = np.sum(probabilities, axis=1)
        indxMax = np.argmax(probabilities, axis=1)
        check_modify = (sumProb > (RoundOffConstant.low + dValue))
        probabilities[check_modify, indxMax[check_modify]] -= dValue
        sumProb[check_modify] -= dValue
        check_modify = (sumProb > (RoundOffConstant.low + dValue))
        probabilities[check_modify, indxMax[check_modify]] -= dValue
        sumProb[check_modify] -= dValue

        check_modify = ((RoundOffConstant.high - dValue) > sumProb)
        probabilities[check_modify, indxMax[check_modify]] += dValue
        sumProb[check_modify] += dValue
        check_modify = ((RoundOffConstant.high - dValue) > sumProb)
        probabilities[check_modify, indxMax[check_modify]] += dValue

        # Create dictionary to keep data for all distinct truncation maps/cubes for Trunc2D_Angle type rules
        # The round-off probabilities are used as key.
        # For each unique round-off probability or key, initialize an empty datastructure to keep truncation map/cube
        # and a data set with all grid cell indices for grid cells having the same round-off probabilities.
        # All these grid cells will then share the same truncation map/cube.
        memo = {}
        for i in range(num_cells):
            key = (tuple(probabilities[i, :]))
            if key not in memo:
                # Create new item to keep truncation map/cube
                memo[key] = MemoizationItem(cell_index=i)
            else:
                # Existing item. Add the cell_index to this item.
                memo[key].add_cell_index(i)

        num_maps = len(memo)
        return memo, num_maps
