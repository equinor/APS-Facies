#!/bin/env python
# -*- coding: utf-8 -*-
import collections
import copy
import datetime
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element

from depricated.APSGaussFieldJobs import APSGaussFieldJobs
from src.algorithms.APSMainFaciesTable import APSMainFaciesTable
from src.algorithms.APSZoneModel import APSZoneModel
from src.utils.constants.simple import Debug
from src.utils.exceptions.xml import MissingAttributeInKeyword
from src.utils.numeric import isNumber
from src.utils.xmlUtils import getIntCommand, getKeyword, getTextCommand, prettify


class APSModel:
    """
    Class APSModel  - contains the data structure for data read from model file

    Class member variables:

    Public member functions:
      Constructor: def __init__(self,modelFileName= None)

      def updateXMLModelFile(self, modelFileName, parameterFileName, debug_level=Debug.OFF)
                - Read xml model file and IPL parameter file and write
                  updated xml model file without putting any data into the data structure.


      def createSimGaussFieldIPL()
                - Write IPL file to simulate gaussian fields

      def XMLAddElement(self,root)
                - Add data to xml tree

      def writeModel(self,modelFileName, debug_level=Debug.OFF)
                - Create xml tree with model specification by calling XMLAddElement
                - Write xml tree with model specification to file

      def writeModelFromXMLRoot(self,inputETree,outputModelFileName)
                - Write specified xml tree to file

      Get data from data structure:

       def getXmlTree(self)
       def getRoot(self)
       def getSelectedZoneNumberList(self)
       def getZoneModel(self,zoneNumber,regionNumber=None)
       def getGridModelName(self)
       def getResultFaciesParamName(self)
       def getZoneNumberList(self)
       def getPreviewZoneNumber(self)
       def getAllGaussFieldNamesUsed(self)
       def getZoneParamName(self)
       def debug_level(self)
       def getMainFaciesTable(self)
       def getRMSProjectName(self)
       def getRMSGaussFieldScriptName(self)
       def getAllProbParam(self)

      Set data and update data structure:

       def setRmsProjectName(self,name)
       def setRmsWorkflowName(self,name)
       def setGaussFieldScriptName(self,name)
       def setRmsGridModelName(self,name)
       def setRmsZoneParamName(self,name)
       def setRmsResultFaciesParamName(self,name)
       def set_debug_level(self,debug_level)
       def setSelectedZoneNumberList(self,selectedZoneNumbers)
       def setPreviewZoneNumber(self,zoneNumber)
       def addNewZone(self,zoneObject)
       def deleteZone(self,zoneNumber)
       def setMainFaciesTable(self,faciesTableObj)
       def setGaussFieldJobs(self,gfJobObject)


    Private member functions:
     def __interpretXMLModelFile(self,modelFileName)
                 - Read xml file and put the data into data structure

     def __readParamFromFile(self,inputFile,debug_level)
                 - Read IPL include file to get updated model parameters from FMU

    -----------------------------------------------------------------------------
    """

    def __init__(
            self, modelFileName=None, apsmodelversion='1.0', rmsProjectName='', rmsWorkflowName='', rmsGaussFieldScriptName='',
            rmsGridModelName='', rmsSingleZoneGrid='False', rmsZoneParameterName='', rmsRegionParameterName='',
            rmsFaciesParameterName='', seedFileName='seed.dat', writeSeeds=True, rmsGFJobs=None,
            rmsHorizonRefName='', rmsHorizonRefNameDataType='', mainFaciesTable=None, zoneModelTable=None,
            previewZone=0, previewRegion=0, previewCrossSectionType='IJ', previewCrossSectionRelativePos=0.5,
            previewScale=1.0, debug_level=Debug.OFF):
        """
         The following parameters are necessary to define a model:
         If a model is created from a model file, the only necessary input is modelFileName

         If the model is created from e.g APSGUI, these parameters must be specified:
         rmsProjectName - Name of RMS project which will run a workflow using the APS method
         rmsWorkflowName - Name of RMS workflow for APS model
         rmsGaussFieldScriptName - temporary file used by the workflow. This file should not be specified
                                   my the user but get a default name. It contains the IPL script to
                                   create gaussian fields which will run RMS petrosim jobs
                                   to create the gaussian fields. This file will not be used
                                   when our new gaussian simulation code implemented into the APS src code.
         rmsGridModelName - Name of grid model in RMS project.
         rmsSingleZoneGrid - Boolean value. True if the RMS grid model specified with rmsGridModelName is a single zone grid and false if not
         rmsZoneParameterName - Zone parameter for the grid model in the RMS project.
         rmsRegionParameterName - Region parameter for the grid model in the RMS project.
         rmsFaciesParameterName - Facies parameter to be updated in the grid model in the RMS project by the APS model.
         rmsGFJobs -  Object of the GaussFieldJobs which contain list of RMS petrosim jobs and name of
                      Gaussian fields each of those RMS jobs creates.
                      This is necessary as a link between the gauss fields created in the RMS project and
                      the gauss fields used in the APS model. As soon as the new gauss fields code is implemented
                      the APS model is no longer dependent on RMS petrosim jobs and this
                      structure here will not be necessary anymore.
         rmsHorizonRefName - This is name of a Horizon surface which is used to define the 2D grid resolution
                             of 2D surfaces containing variogram azimuth anisotropy angles.
                            This is only necessary as a workaround as long as the project depends on creating
                            gaussian fields using RMS petrosim module, and this will no longer be necessary
                            when the new gaussian field simulation is implemented in the APS code.
         rmsHorizonRefNameDataType - Horizon representation data type for horizons.
                                     Is used when creating rmsHorizonSurfacies containing variogram anisotropy
                                     for azimuth angle. This data will no longer be necessary when the gaussian
                                     fields are created by the new gaussian field simulation code to be used in APS model.
         mainFaciesTable - Object containing the global facies table with facies names an associated
                           facies code common for the RMS project. All facies to be modelled must be defined
                           in the mainFaciesTable.
         zoneModelTable - Disctionary with key = (zoneNumber, regionNumber) containing zoneModels as values.
                          Each zoneModel will be associated with the grid cells in the gridmodel that belongs to
                          a specified zoneNumber and regionNumber. If regionNumber is not used (is equal to 0),
                          the facies realization will be calculated for the grid cells belonging to the specified zone number.
                          The maximum possible zoneModels will be the sum over all defined (zoneNumber,regionNumber) pairs
                          that exist in the gridmodel. It is possible that an APS model is defined for
                          only one (zoneNumber,regionNumber) pair and is not defined any grid cells not satisfying
                          this criteria.
         previewZone, previewRegion, previewCrossSectionType, previewCrossSectionRelativePos:
                          Variables used in the testPreview script and will not be necessary in the APSGUI.
                          As long as there are benefit related to using the testPreview script, these parameters are relevant.
         The pair (previewZone, previewRegion) - Zone and region number for the APS zone model to create preview plot for.
         previewCrossSectionType - Either IJ, IK, JK for the cross section to make plots for.
         previewCrossSectionRelativePos - The previewCrossSectionRelativePos must be a float number between 0 and 1.
                                          and mean for IJ cross sections that the cross section correspond to
                                          an index = previewCrossSectionRelativePos * nz and similar fo IK and JK cross sections.
         previewScale - Scaling factor between K direction and I or J direction (Vertical scaling factor)
         debugLevel - Define amouth of output to the screen during runs

        """
        # Local variables
        self.__className = self.__class__.__name__

        self.__apsModelVersion = apsmodelversion

        self.__rmsProjectName = rmsProjectName
        self.__rmsWorkflowName = rmsWorkflowName
        self.__rmsGaussFieldScriptName = rmsGaussFieldScriptName

        self.__rmsGridModelName = rmsGridModelName
        self.__rmsSingleZoneGrid = rmsSingleZoneGrid
        self.__rmsZoneParamName = rmsZoneParameterName
        self.__rmsRegionParamName = rmsRegionParameterName
        self.__rmsFaciesParamName = rmsFaciesParameterName
        self.__seedFileName = seedFileName
        self.writeSeeds = writeSeeds
        self.__rmsGFJobs = rmsGFJobs

        self.__refHorizonNameForVariogramTrend = rmsHorizonRefName
        self.__refHorizonReprNameForVariogramTrend = rmsHorizonRefNameDataType

        self.__faciesTable = mainFaciesTable
        self.__zoneModelTable = zoneModelTable if zoneModelTable else {}
        self.__sortedZoneModelTable = {}
        self.__zoneNumberList = []
        self.__selectedZoneAndRegionNumberTable = {}
        self.__selectAllZonesAndRegions = True
        self.__previewZone = previewZone
        self.__previewRegion = previewRegion
        self.__previewCrossSectionType = previewCrossSectionType
        self.__previewCrossSectionRelativePos = previewCrossSectionRelativePos
        self.__previewScale = previewScale
        self.__debug_level = debug_level

        # Read model if it is defined
        if modelFileName is None:
            if len(self.__zoneModelTable) > 0:
                # Define sorted sequence of the zone models
                self.__sortedZoneModelTable = collections.OrderedDict(sorted(self.__zoneModelTable.items()))
            return
        self.__interpretXMLModelFile(modelFileName, debug_level=debug_level)

    def __interpretXMLModelFile(self, modelFileName, debug_level=Debug.OFF):
        tree = ET.parse(modelFileName)
        self.__ET_Tree = tree
        root = tree.getroot()

        apsmodelversion = root.get('version')
        if apsmodelversion is None:
            raise ValueError(
                'attribute version is not defined in root element'
            )
        else:

            if apsmodelversion != "1.0":
                raise ValueError(
                    'Illegal value ( {} ) specified for apsmodelversion (only 1.0 is supported)'.format(apsmodelversion)
                )
            else:
                self.__apsModelVersion = apsmodelversion

        # --- PrintInfo ---
        kw = 'PrintInfo'
        obj = root.find(kw)
        if obj is None:
            # Default value is set
            self.__debug_level = debug_level
        else:
            text = obj.text
            self.set_debug_level(text)
        if self.__debug_level >= Debug.VERY_VERBOSE:
            print('')
            print('Debug output: ------------ Start reading model file in APSModel ------------------')
            print('')

        # --- Preview ---
        kw = 'Preview'
        obj = root.find(kw)
        if obj is not None:
            text = obj.get('zoneNumber')
            if text is None:
                raise MissingAttributeInKeyword(kw, 'zoneNumber')
            self.__previewZone = int(text)

            text = obj.get('regionNumber')
            if text is None:
                raise MissingAttributeInKeyword(kw, 'regionNumber')
            self.__previewRegion = int(text)

            text = obj.get('crossSectionType')
            if text is None:
                raise MissingAttributeInKeyword(kw, 'crossSectionType')
            self.__previewCrossSectionType = text

            text = obj.get('crossSectionRelativePos')
            if text is None:
                raise MissingAttributeInKeyword(kw, 'crossSectionRelativePos')
            self.__previewCrossSectionRelativePos = float(text.strip())

            text = obj.get('scale')
            if text is None:
                raise MissingAttributeInKeyword(kw, 'scale')
            self.__previewScale = float(text.strip())

        placement = {
            'RMSProjectName': '__rmsProjectName',
            'RMSWorkflowName': '__rmsWorkflowName',
            'GridModelName': '__rmsGridModelName',
            'ZoneParamName': '__rmsZoneParamName',
            'ResultFaciesParamName': '__rmsFaciesParamName',
        }
        for keyword, variable in placement.items():
            prefix = '_' + self.__class__.__name__
            value = getTextCommand(root, keyword, parentKeyword='APSModel', modelFile=modelFileName)
            self.__setattr__(prefix + variable, value)

        # Read optional keyword for IPL script file
        keyword = 'RMSGaussFieldScriptName'
        value = getTextCommand(root, keyword, modelFile=modelFileName,required=False)
        if value is not None:
            self.__rmsGaussFieldScriptName = value

        # Read optional keyword for region parameter
        keyword = 'RegionParamName'
        value = getTextCommand(root, keyword, parentKeyword='APSModel', defaultText=None,  modelFile=modelFileName, required=False)
        if value is not None:
            self.__rmsRegionParamName = value

        # Read optional keyword which specify whether the gridmodel is a single zone grid or multi zone grid
        keyword = 'UseSingleZoneGrid'
        value = getIntCommand(root, keyword, parentKeyword='APSModel',
                              minValue=0, maxValue=1, defaultValue=0,
                              modelFile=modelFileName, required=False
        )
        if value == 0:
            self.__rmsSingleZoneGrid = False
        else:
            self.__rmsSingleZoneGrid = True

        # Read optional keyword to specify name of seed file
        keyword = 'SeedFile'
        value = getTextCommand(root, keyword, parentKeyword='APSModel', defaultText='seed.dat',  modelFile=modelFileName, required=False)
        self.__seedFileName = value

        # Read optional keyword to specify the boolean variable writeSeeds
        keyword = 'WriteSeeds'
        value = getTextCommand(root, keyword, parentKeyword='APSModel', defaultText='yes',  modelFile=modelFileName, required=False)
        if  value.upper() == 'YES':
            self.writeSeeds = True
        else:
            self.writeSeeds = False

        # Read all gauss field jobs and their gauss field 3D parameter names
        self.__rmsGFJobs = APSGaussFieldJobs(ET_Tree=self.__ET_Tree, modelFileName=modelFileName)

        # Read all facies names available
        self.__faciesTable = APSMainFaciesTable(ET_Tree=self.__ET_Tree, modelFileName=modelFileName)

        if self.__debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: RMSGridModel:                       ' + self.__rmsGridModelName)
            if not self.__rmsSingleZoneGrid:
                print('Debug output: RMS grid is multi zone grid:        ' + 'Yes')
            else:
                print('Debug output: RMS grid is multi zone grid:        ' + 'No')
            print('Debug output: RMSZoneParamName:                   ' + self.__rmsZoneParamName)
            print('Debug output: RMSFaciesParamName:                 ' + self.__rmsFaciesParamName)
            print('Debug output: RMSRegionParamName:                 ' + self.__rmsRegionParamName)
            print('Debug output: Name of RMS project read:           ' + self.__rmsProjectName)
            print('Debug output: Name of RMS workflow read:          ' + self.__rmsWorkflowName)
            print('Debug output: Name of RMS gauss field IPL script: ' + self.__rmsGaussFieldScriptName)

        # Read all zones for models specifying main level facies
        # --- ZoneModels ---
        zModels = root.find('ZoneModels')
        if zModels is None:
            raise IOError(
                'Error when reading model file: {}\n'
                'Error: Missing keyword ZoneModels'
                ''.format(modelFileName)
            )

        # --- Zone ---
        if  self.__debug_level >= Debug.VERY_VERBOSE:
            print('')
            print('--- Number of specified zone models: {}'.format(str(len(zModels.findall('Zone')))))
            print('')

        for zone in zModels.findall('Zone'):
            if zone is None:
                raise IOError(
                    'Error when reading model file: {}\n'
                    'Error: Missing keyword Zone in keyword ZoneModels'
                    ''.format(modelFileName)
                )
            regionNumber = 0
            zoneNumber = int(zone.get('number'))
            if zoneNumber <= 0:
                raise ValueError('Zone number must be positive integer. '
                                 'Can not have zone number: {}'.format(str(zoneNumber))
                                 )
            regionNumberAsText = zone.get('regionNumber')
            if regionNumberAsText is not None:
                regionNumber = int(regionNumberAsText)
            if regionNumber < 0:
                raise ValueError('Region number must be positive integer if region is used.\n'
                                 'Zero as region number means that regions is not used for the zone.\n'
                                 'Can not have negative region number: {}'.format(str(regionNumber))
                                 )

            # The model is identified by the combination (zoneNumber, regionNumber)
            zoneModelKey = (zoneNumber, regionNumber)
            if zoneModelKey not in self.__zoneModelTable:

                if self.__debug_level >= Debug.VERY_VERBOSE:
                    print('')
                    print('')
                    if regionNumber <= 0:
                        print('Debug output: ---- Read zone model for zone number: {}'
                              ''.format(str(zoneNumber)))
                    else:
                        print('Debug output: ---- Read zone model for (zone,region) number: ({},{})'
                              ''.format(str(zoneNumber), str(regionNumber)))

                zoneModel = APSZoneModel(
                    ET_Tree=self.__ET_Tree,
                    zoneNumber=zoneNumber,
                    regionNumber=regionNumber,
                    modelFileName=modelFileName
                )
                # This zoneNumber, regionNumber combination is not defined previously
                # and must be added to the dictionary
                self.__zoneModelTable[zoneModelKey] = zoneModel
            else:
                raise ValueError('Can not have two or more entries of  keyword Zone with the same '
                                 'zoneNumber and regionNumber.\n'
                                 'Can not have multiple specification of (zoneNumber, regionNumber) = ({},{})'
                                 ''.format(str(zoneNumber), str(regionNumber))
                                 )



        # --- SelectedZones ---
        kw = 'SelectedZonesAndRegions'
        obj = getKeyword(root,kw,modelFile=modelFileName,required=False)
        if obj is not None:
            # The keyword is specified. This means that in general a subset of
            # all zones and region combinations are selected.
            # Read this sub set of zone and region combinations.
            self.__selectAllZonesAndRegions = False
            kw2 = 'SelectedZoneWithRegions'
            objSelectedZone=None
            for objSelectedZone in obj.findall(kw2):
                text = objSelectedZone.get('zone')
                zNumber = int(text.strip())

                text = objSelectedZone.text
                if len(text.strip()) == 0:
                    rNumber = 0
                    # Empty list of region numbers
                    zoneModel = self.getZoneModel(zoneNumber=zNumber, regionNumber=rNumber)
                    if zoneModel is None:
                        raise ValueError(
                            'Can not select to use zone model with zone number: {} and region number: {} '
                            'This zone model is not defined'
                            ''.format(str(zNumber), str(rNumber))
                        )
                    # A model for (zoneNumber,regionNumber=0) is defined
                    selectedKey = (zNumber, rNumber)
                    self.__selectedZoneAndRegionNumberTable[selectedKey] = 1
                else:
                    words = text.split()
                    for w in words:
                        w2 = w.strip()
                        if isNumber(w2):
                            rNumber = int(w2)
                            zoneModel = self.getZoneModel(zoneNumber=zNumber, regionNumber=rNumber)
                            if zoneModel is None:
                                raise ValueError('Can not select to use zone model with zone number: {} and region number: {} '
                                                 'This zone model is not defined'
                                                 ''.format(str(zNumber), str(rNumber))
                                )
                            # A model for this (zoneNumber,regionNumber) pair is defined
                            selectedKey = (zNumber, rNumber)
                            self.__selectedZoneAndRegionNumberTable[selectedKey] = 1

            if objSelectedZone is None:
                raise ValueError(
                    'Keyword ZoneNumber under keyword SelectedZonesAndRegions is not defined.\n'
                    'Specify at least one zone to be selected to be used.'
                )
        else:
            # Keyword is not specified. This means that one should choose the default
            # which is to select all defined  (zone,region) models
            self.__selectAllZonesAndRegions = True

        self.__checkZoneModels()

        # Define sorted sequence of the zone models
        self.__sortedZoneModelTable = collections.OrderedDict(sorted(self.__zoneModelTable.items()))

        if self.__debug_level >= Debug.SOMEWHAT_VERBOSE:
            if self.__debug_level >= Debug.SOMEWHAT_VERBOSE:
                print('- Zone models are defined for the following combination '
                      'of zone and region numbers:')
                for key , value in self.__sortedZoneModelTable.items():
                    zNumber = key[0]
                    rNumber = key[1]
                    if rNumber == 0:
                        print('    Zone: {}'.format(str(zNumber)))
                    else:
                        print('    Zone: {}  Region: {}'.format(str(zNumber), str(rNumber)))
            print('')
            print('------------ End reading model file in APSModel ------------------')
            print('')

    def updateXMLModelFile(self, modelFileName, parameterFileName, debug_level=Debug.OFF):
        # Read XML model file
        tree = ET.parse(modelFileName)
        root = tree.getroot()

        # Scan XML model file for variables that can be updated by FMU/ERT
        # These variables belongs to xml keywords with attribute 'kw'.
        # So search for attribute 'kw' to find all these variables. The attribute value is a keyword
        # name that will be used as identifier.
        if debug_level > Debug.SOMEWHAT_VERBOSE:
            print('')
            print('-- Model parameters marked as possible to update when running in batch mode')
            print('Keyword:                        Tag:                Value: ')
        keywordsDefinedForUpdating = []
        for obj in root.findall(".//*[@kw]"):
            keyWord = obj.get('kw')
            tag = obj.tag
            value = obj.text
            keywordsDefinedForUpdating.append([keyWord.strip(), value.strip()])
            if debug_level > Debug.SOMEWHAT_VERBOSE:
                print('{0:30} {1:20}  {2:10}'.format(keyWord, tag, value))

        # Read keywords from parameterFileName (Global IPL include file with variables updated by FMU/ERT)
        keywordsRead = self.__readParamFromFile(parameterFileName, debug_level)
        # keywordsRead = [name,value]

        # Set new values
        for i in range(len(keywordsDefinedForUpdating)):
            item = keywordsDefinedForUpdating[i]
            keyword = item[0]
            oldValue = item[1]
            for j in range(len(keywordsRead)):
                itemRead = keywordsRead[j]
                kw = itemRead[0]
                value = itemRead[1]
                if kw == keyword:
                    # set new value
                    item[1] = ' ' + value.strip() + ' '
        if debug_level >= Debug.VERY_VERBOSE:
            print('Debug output:  Keywords and values that is updated in xml tree: ')

        for obj in root.findall(".//*[@kw]"):
            keyWord = obj.get('kw')
            tag = obj.tag
            oldValue = obj.text

            found = 0
            for i in range(len(keywordsDefinedForUpdating)):
                item = keywordsDefinedForUpdating[i]
                kw = item[0]
                val = item[1]
                if kw == keyWord:
                    # Update value in XML tree for this keyword
                    obj.text = val
                    found = 1
                    break
            if found == 1:
                if debug_level >= Debug.VERY_VERBOSE:
                    print('{0:30} {1:20}  {2:10}'.format(keyWord, oldValue, obj.text))
            else:
                raise ValueError(
                    'Error: Inconsistency. Programming error in function updateXMLModelFile in class APSModel'
                )

        if debug_level >= Debug.VERY_VERBOSE:
            print('')

        return tree

    def __checkZoneModels(self):
        """
        Description: Run through all zone models and check that:
           If a zone model is specified with region number 0, it is not allowed to specify zone models for the same
           zone which is individual for regions > 0 as well. The reason is that a zone model with region 0 (which means not using regions)
           and zone models for the same zone but specified for individual regions will change facies code in a set of cells in the grid that
           is common and hence "overwrite" each other.
        """
        zoneNumbers = []
        for key, zoneModel in self.__zoneModelTable.items():
            zNumber = key[0]
            rNumber = key[1]
            if zNumber in zoneNumbers:
                if rNumber == 0:
                    raise ValueError(
                    'There exists more than one zone model for zone: {}'.format(str(zNumber))
                    )
                else:
                    # This is a model for a new region for an existing zone number that has several regions
                    zoneNumbers.append(zNumber)
            else:
                # This is a model for a new (zone,region) combination for a new zone number
                zoneNumbers.append(zNumber)

    @staticmethod
    def __readParamFromFile(inputFile, debug_level=Debug.OFF):
        # Search through the file line for line and skip lines commented out with '//'
        # Collect all variables that are assigned value as the three first words on a line
        # like e.g VARIABLE_NAME = 10
        if debug_level >= Debug.SOMEWHAT_VERBOSE:
            print('- Read file: ' + inputFile)
        nKeywords = 0
        keywordsFMU = []
        with open(inputFile, 'r') as file:
            lines = file.readlines()

            for line in lines:
                words = line.split()
                nWords = len(words)
                if nWords < 3:
                    # Skip line (searching for an assignment like keyword = value with at least 3 words
                    continue
                if words[0] == '//':
                    # Skip line
                    continue

                if words[1] == '=':
                    # This is assumed to be an assignment
                    nKeywords += 1
                    value = copy.copy(words[2])
                    keyword = copy.copy(words[0])
                    keywordsFMU.append([keyword, value])
        if debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: Keywords and values found in parameter file:  ' + inputFile)
            for item in keywordsFMU:
                kw = item[0]
                val = item[1]
                print('  {0:30} {1:20}'.format(kw, val))
            print('')
        # End read file

        return keywordsFMU

    #  ---- Get functions -----
    def getXmlTree(self):
        tree = self.__ET_Tree
        return tree

    def getRoot(self):
        tree = self.getXmlTree()
        root = tree.getroot()
        return root

    def isAllZoneRegionModelsSelected(self):
        return self.__selectAllZonesAndRegions

    def getSelectedZoneNumberList(self):
        selectedZoneNumberList = []
        keyList = list(self.__selectedZoneAndRegionNumberTable.keys())
        for i in range(len(keyList)):
            item = keyList[i]
            zNumber = item[0]
            if zNumber not in selectedZoneNumberList:
                selectedZoneNumberList.append(zNumber)
        return copy.copy(selectedZoneNumberList)

    def getSelectedRegionNumberListForSpecifiedZoneNumber(self,zoneNumber):
        selectedRegionNumberList = []
        keyList = sorted(list(self.__selectedZoneAndRegionNumberTable.keys()))
        for i in range(len(keyList)):
            item = keyList[i]
            zNumber = item[0]
            rNumber = item[1]
            if zNumber == zoneNumber:
                if rNumber not in selectedRegionNumberList:
                    selectedRegionNumberList.append(rNumber)
        return selectedRegionNumberList

    def isSelected(self, zoneNumber, regionNumber):
        if self.isAllZoneRegionModelsSelected():
            return True
        key = (zoneNumber, regionNumber)
        if key in self.__selectedZoneAndRegionNumberTable:
            return True
        else:
            return False

    # Get pointer to zone model object
    def getZoneModel(self, zoneNumber, regionNumber=0):
        key = (zoneNumber, regionNumber)
        try:
            foundZoneModel = self.__zoneModelTable[key]
            return foundZoneModel
        except KeyError:
            return None

    def getAllZoneModels(self):
        return self.__zoneModelTable

    def getAllZoneModelsSorted(self):
        return self.__sortedZoneModelTable

    def getGridModelName(self):
        return copy.copy(self.__rmsGridModelName)

    def getResultFaciesParamName(self):
        return copy.copy(self.__rmsFaciesParamName)

    def getZoneNumberList(self):
        zoneNumberList = []
        keyList = list(self.__zoneModelTable.keys())
        for i in range(len(keyList)):
            item = keyList[i]
            zNumber = item[0]
            if zNumber not in zoneNumberList:
                zoneNumberList.append(zNumber)
        return zoneNumberList

    def getRegionNumberListForSpecifiedZoneNumber(self,zoneNumber):
        regionNumberList = []
        keyList = list(self.__zoneModelTable.keys())
        for i in range(len(keyList)):
            item = keyList[i]
            zNumber = item[0]
            rNumber = item[1]
            if zNumber == zoneNumber:
                if rNumber not in regionNumberList:
                    regionNumberList.append(rNumber)
        return regionNumberList

    def getPreviewZoneNumber(self):
        return self.__previewZone

    def getPreviewRegionNumber(self):
        return self.__previewRegion

    def getPreviewCrossSectionType(self):
        return self.__previewCrossSectionType

    def getPreviewCrossSectionRelativePos(self):
        return self.__previewCrossSectionRelativePos

    def getPreviewScale(self):
        return self.__previewScale

    def getAllGaussFieldNamesUsed(self):
        gfAllZones = []
        for key, zoneModel in self.__zoneModelTable.items():
            print('In getAllGaussFieldNamesUsed: key=({},{})'.format(str(key[0]),str(key[1])))
            gfNames = zoneModel.getUsedGaussFieldNames()
            for gf in gfNames:
                # Add the gauss field name to the list if it not already is in the list
                print('Gauss field name: {}'.format(gf))
                if gf not in gfAllZones:
                    gfAllZones.append(gf)
        return copy.copy(gfAllZones)

    def getZoneParamName(self):
        return copy.copy(self.__rmsZoneParamName)

    def getRegionParamName(self):
        if self.__rmsRegionParamName != '':
            return copy.copy(self.__rmsRegionParamName)
        else:
            return ''

    def getSeedFileName(self):
        return self.__seedFileName

    def debug_level(self):
        return self.__debug_level

    # Get pointer to facies table object
    def getMainFaciesTable(self):
        return self.__faciesTable

    def getRMSProjectName(self):
        return copy.copy(self.__rmsProjectName)

    def getRMSGaussFieldScriptName(self):
        return copy.copy(self.__rmsGaussFieldScriptName)

    def getAllProbParam(self):
        allProbList = []
        for key, zoneModel in self.__zoneModelTable.items():
            print('In getAllProbParam: key=({},{})'.format(str(key[0]),str(key[1])))
            probParamList = zoneModel.getAllProbParamForZone()
            for pName in probParamList:
                if pName not in allProbList:
                    allProbList.append(pName)
        return allProbList

    # ----- Set functions -----
    def setRmsProjectName(self, name):
        self.__rmsProjectName = copy.copy(name)

    def setRmsWorkflowName(self, name):
        self.__rmsWorkflowName = copy.copy(name)

    def setGaussFieldScriptName(self, name):
        self.__rmsGaussFieldScriptName = copy.copy(name)

    def setRmsGridModelName(self, name):
        self.__rmsGridModelName = copy.copy(name)

    def setRmsZoneParamName(self, name):
        self.__rmsZoneParamName = copy.copy(name)

    def setRmsResultFaciesParamName(self, name):
        self.__rmsFaciesParamName = copy.copy(name)

    def setSeedFileName(self,name):
        self.__seedFileName = copy.copy(name)

    def set_debug_level(self, debug_level):
        if isinstance(debug_level, str):
            debug_level = int(debug_level.strip())
        if isinstance(debug_level, int):
            debug_level = Debug(debug_level)
        if debug_level not in Debug:
            debug_level = Debug.OFF
        self.__debug_level = debug_level

    def setSelectedZoneAndRegionNumber(self, selectedZoneNumber,selectedRegionNumber=0):
        """
        Description: Select a new pair of (zoneNumber, regionNumber) which has not been already selected.
        """
        # Check that the specified pair (selectedZoneNumber, selectedRegionNumber) is an existing zone model
        key = (selectedZoneNumber, selectedRegionNumber)
        if key in self.__zoneModelTable:
            if not key in self.__selectedZoneAndRegionNumberTable:
                self.__selectedZoneAndRegionNumberTable[key] = 1
        else:
            raise ValueError(
                'Can not select (zoneNumber, regionNumber) = ({},{}) since the zone model does not exist'
                ''.format(str(selectedZoneNumber), str(selectedRegionNumber))
                )

    def setPreviewZoneAndRegionNumber(self, zoneNumber,regionNumber=0):
        key = (zoneNumber, regionNumber)
        if key in self.__zoneModelTable:
            self.__previewZoneNumber = zoneNumber
            self.__previewRegionNumber = regionNumber
        else:
            raise ValueError(
                'Error in {} in setPreviewZoneNumber\n'
                'Error:  (zoneNumber, regionNumber) = ({},{}) is not defined in the model'
                ''.format(self.__className, str(zoneNumber), str(regionNumber))
                )

    def setPreviewCrossSectionType(self, crossSectionType):
        if not (crossSectionType == 'IJ' or crossSectionType == 'IK' or crossSectionType == 'JK'):
            raise ValueError(
                'Error in setPreviewCrossSectionType\n'
                'Error:  Cross section is not IJ, IK or JK.'
            )
        else:
            self.__previewCrossSectionType = crossSectionType

    def setPreviewCrossSectionRelativePos(self, crossSectionRelativePos):
        if not 0<= crossSectionRelativePos <= 1:
            raise ValueError(
                'Error in setPreviewCrossSectionRelativePos\n'
                'The specified value must be in the interval [0.0, 1.0]'
            )
        else:
            self.__previewCrossSectionRelativePos = crossSectionRelativePos

    def setPreviewScale(self, scale):
        if not (scale > 0.0):
            raise ValueError(
                'Error in {} in setPreviewScale\n'
                'Error:  Scale factor must be > 0'
            )
        else:
            self.__previewScale = scale

    def addNewZone(self, zoneObject):
        zoneNumber = zoneObject.getZoneNumber()
        regionNumber = zoneObject.getRegionNumber()
        if self.__debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: Call addNewZone')
            print('Debug output: From addNewZone: (ZoneNumber, regionNumber)=({},{})'.format(str(zoneNumber), str(regionNumber)))
        key = (zoneNumber, regionNumber)
        if not key in self.__zoneModelTable:
            self.__zoneModelTable[key] = zoneObject
        else:
            raise ValueError('Can not add zone with (zoneNumber,regionNumber)=({},{})to the APSModel\n'
                             'A zone with this zone and region number already exist.'
                             ''.format(str(zoneNumber), str(regionNumber))
                             )

    def deleteZone(self, zoneNumber, regionNumber=0):
        key = (zoneNumber, regionNumber)
        if self.__debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: Call deleteZone')
            print('Debug output: From deleteZone: (ZoneNumber, regionNumber)=({},{})'.format(str(zoneNumber), str(regionNumber)))

        if key in self.__zoneModelTable:
            del self.__zoneModelTable[key]

        # Check if the zone number, region number pair is in the selected list
        if key in self.__selectedZoneAndRegionNumberTable:
            del self.__selectedZoneAndRegionNumberTable[key]

    # Set facies table to refer to the input facies table object
    def setMainFaciesTable(self, faciesTableObj):
        self.__faciesTable = faciesTableObj

    # Set gauss field job to refer to the input gauss field job object
    def setGaussFieldJobs(self, gfJobObject):
        self.__rmsGFJobs = copy.deepcopy(gfJobObject)

    def getGaussFieldJobs(self):
        return copy.copy(self.__rmsGFJobs)

    def createSimGaussFieldIPL(self):
        print('Call createSimGaussFieldIPL')
        print('Write file: {}'.format(self.__rmsGaussFieldScriptName))
        outputFileName = self.__rmsGaussFieldScriptName
        gridModelName = self.__rmsGridModelName
        zoneNumberList = self.getZoneNumberList()
        nZones = len(zoneNumberList)
        jobObject = self.__rmsGFJobs
        nJobs = jobObject.getNumberOfGFJobs()
        jobNames = jobObject.getGaussFieldJobNames()

        with open(outputFileName, 'w') as file:
            file.write('// IPL: {}\n'.format(outputFileName))
            file.write('// IPL:  Run RMS jobs to create gaussian fields for the APS method\n')
            file.write('// Created by: Python script APSModel.py\n')

            d = datetime.datetime.today().strftime("%d/%m/%y")
            t = datetime.datetime.now().strftime("%H.%M.%S")
            file.write('// Date: {} Clock: {}\n'.format(d, t))

            file.write('// --- Declarations ---\n')
            file.write('Job job\n')
            file.write('String gridModelName\n')
            file.write('String jobName,fullJobName\n')
            file.write('String varioType\n')
            file.write('String scriptName\n')
            file.write('String paramName\n')
            file.write('Int    nZones\n')
            file.write('Float    value\n')
            file.write('GridModel gm\n')
            file.write(' \n')
            file.write('// --- Assignments  ---\n')
            file.write('scriptName    = "{}"\n'.format(outputFileName))
            file.write('gridModelName = "{}"\n'.format(gridModelName))
            file.write('nZones        = {}\n'.format(nZones))

            file.write(' \n')
            file.write('// --- Executable code ---\n')
            file.write('GetGridModel(gridModelName,gm)\n')
            file.write(' \n')
            file.write(' \n')

            updateJob = []
            for j in range(nJobs):
                updateJob.append(0)

            for key, zoneModel in self.__zoneModelTable.items():
                zoneNumber = key[0]
                regionNumber = key[1]
                print('In createSimGaussFieldIPL: Write IPL commands to generate model for (zoneNumber, regionNumber)=({},{})'
                      ''.format(str(zoneNumber), str(regionNumber)))
                currentZoneModel = zoneModel
                if not self.isSelected(zoneNumber, regionNumber):
                    continue
                file.write('// --- RMS gauss simulation settings for zone and region number ({},{}) ---\n'.format(str(zoneNumber),str(regionNumber)))
                gaussFieldNamesInZoneModel = currentZoneModel.getUsedGaussFieldNames()
                nGFParamUsed = len(gaussFieldNamesInZoneModel)

                for i in range(nGFParamUsed):
                    gfNameUsed = gaussFieldNamesInZoneModel[i]
                    if self.__rmsSingleZoneGrid:
                        if regionNumber > 0:
                            file.write('Print("Update Gauss field: ","{}"," for single zone grid for region number: {}")\n'
                                       ''.format(gfNameUsed, str(regionNumber)))
                        else:
                            file.write('Print("Update Gauss field: ","{}"," for single zone grid")\n'.format(gfNameUsed))
                    else:
                        if regionNumber > 0:
                            file.write('Print("Update Gauss field: ","{}"," for zone, region pair: ({},{})")\n'
                                       ''.format(gfNameUsed, str(zoneNumber), str(regionNumber)))
                        else:
                            file.write('Print("Update Gauss field: ","{}"," for zone: ",{})\n'.format(gfNameUsed, str(zoneNumber)))

                    # Check which rms job this gauss field parameter belongs to
                    for j in range(nJobs):

                        currentJobName = jobNames[j]
                        if jobObject.checkGaussFieldNameInJob(currentJobName, gfNameUsed):
                            updateJob[j] = 1
                            # This job must be updated with variogram parameters
                            # for current zone number
                            gfIndx = jobObject.getGaussFieldIndx(currentJobName, gfNameUsed)
                            variogramType = currentZoneModel.getVariogramType(gfNameUsed)
                            variogramName = variogramType.name
                            range1 = currentZoneModel.getMainRange(gfNameUsed)
                            range2 = currentZoneModel.getPerpRange(gfNameUsed)
                            range3 = currentZoneModel.getVertRange(gfNameUsed)
                            # TODO: power is UNUSED
                            power = 1.0
                            if variogramType == 'GEN_EXPONENTIAL':
                                power = currentZoneModel.getPower(gfNameUsed)

                            file.write('job = "{}"\n'.format(currentJobName))
                            if self.__rmsSingleZoneGrid:
                                file.write(
                                    'paramName = "Group[{}].VariogramType"\n'.format(gfIndx + 1)
                                )
                                file.write('ModifyJob(job,paramName,"{}")\n'.format(variogramName))

                                file.write(
                                    'paramName = "Group[{}].VariogramStdDev"\n'.format(gfIndx + 1)
                                )
                                file.write('value = {}\n'.format(1.0))
                                file.write('ModifyJob(job,paramName,value)\n')

                                file.write(
                                    'paramName = "Group[{}].VariogramMainRange"\n'.format(gfIndx + 1)
                                )
                                file.write('value = {}\n'.format(range1))
                                file.write('ModifyJob(job,paramName,value)\n')

                                file.write(
                                    'paramName = "Group[{}].VariogramPerpRange"\n'.format(gfIndx + 1)
                                )
                                file.write('value = {}\n'.format(range2))
                                file.write('ModifyJob(job,paramName,value)\n')

                                file.write(
                                    'paramName = "Group[{}].VariogramVertRange"\n'.format(gfIndx + 1)
                                )
                                file.write('value = {}\n'.format(range3))
                                file.write('ModifyJob(job,paramName,value)\n')

                            else:
                                file.write(
                                    'paramName = "Zone[{}].Group[{}].VariogramType"\n'.format(zoneNumber, gfIndx + 1)
                                )
                                file.write('ModifyJob(job,paramName,"{}")\n'.format(variogramName))

                                file.write(
                                    'paramName = "Zone[{}].Group[{}].VariogramStdDev"\n'.format(zoneNumber, gfIndx + 1)
                                )
                                file.write('value = {}\n'.format(1.0))
                                file.write('ModifyJob(job,paramName,value)\n')

                                file.write(
                                    'paramName = "Zone[{}].Group[{}].VariogramMainRange"\n'.format(zoneNumber, gfIndx + 1)
                                )
                                file.write('value = {}\n'.format(range1))
                                file.write('ModifyJob(job,paramName,value)\n')

                                file.write(
                                    'paramName = "Zone[{}].Group[{}].VariogramPerpRange"\n'.format(zoneNumber, gfIndx + 1)
                                )
                                file.write('value = {}\n'.format(range2))
                                file.write('ModifyJob(job,paramName,value)\n')

                                file.write(
                                    'paramName = "Zone[{}].Group[{}].VariogramVertRange"\n'.format(zoneNumber, gfIndx + 1)
                                )
                                file.write('value = {}\n'.format(range3))
                                file.write('ModifyJob(job,paramName,value)\n')

                            file.write('ApplyJob(job)\n')
                            file.write('\n')
                            break
            # End for zone
            file.write('// --- Execute jobs ---\n')
            for j in range(nJobs):
                if updateJob[j] == 1:
                    currentJobName = jobNames[j]
                    file.write('fullJobName = gridModelName + ".Grid." + "{}"\n'.format(currentJobName))
                    file.write('job = "{}"\n'.format(currentJobName))
                    file.write('Print("Start running job: ",fullJobName)\n')
                    file.write('ExecuteJob(job)\n')

            file.write('\n')
            file.write('Print("Finished IPL script: ","{}")\n'.format(outputFileName))
            file.write('// --------------- End script -----------------\n')

    def XMLAddElement(self, root):
        """
        Add a command specifying which zone to use in for preview
        :param root:
        :type root:
        :return:
        :rtype:
        """
        # TODO: This is temporary solution
        if self.__debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: call XMLADDElement from ' + self.__className)

        if self.__previewZone > 0:
            tag = 'Preview'
            attribute = {
                'zoneNumber': str(self.__previewZone),
                'regionNumber': str(self.__previewRegion),
                'crossSectionType': str(self.__previewCrossSectionType),
                'crossSectionRelativePos': str(self.__previewCrossSectionRelativePos),
                'scale': str(self.__previewScale)
            }
            elem = Element(tag, attribute)
            root.append(elem)

        # If selected zone list is defined (has elements) write them to a keyword
        selectedZoneNumberList = self.getSelectedZoneNumberList()
        if len(selectedZoneNumberList) > 0:
            sortedSelectedZoneAndRegionNumberTable = collections.OrderedDict(sorted(self.__selectedZoneAndRegionNumberTable.items()))
            tag = 'SelectedZonesAndRegions'
            elemSelectedZoneAndRegion = Element(tag)
            root.append(elemSelectedZoneAndRegion)
            for key, selected in sortedSelectedZoneAndRegionNumberTable.items():
                zNumber = key[0]
                rNumber = key[1]
                tag = 'SelectedZoneWithRegions'
                attributes= {'zone':str(zNumber)}
                text = ''
                elemZoneRegion = Element(tag,attributes)

                rList = self.getSelectedRegionNumberListForSpecifiedZoneNumber(zNumber)
                text = ' '
                useRegion = 1
                if len(rList) == 1:
                    if rList[0] == 0:
                        useRegion =0
                if useRegion == 1:
                    for j in range(len(rList)):
                        rNumber = rList[j]
                        text = text + ' ' + str(rNumber) + ' '
                elemZoneRegion.text= text
                elemSelectedZoneAndRegion.append(elemZoneRegion)



        # Add all main commands to the root APSModel
        tag = 'RMSProjectName'
        elem = Element(tag)
        elem.text = ' ' + self.__rmsProjectName.strip() + ' '
        root.append(elem)

        tag = 'RMSWorkflowName'
        elem = Element(tag)
        elem.text = ' ' + self.__rmsWorkflowName.strip() + ' '
        root.append(elem)

        tag = 'RMSGaussFieldScriptName'
        elem = Element(tag)
        elem.text = ' ' + self.__rmsGaussFieldScriptName.strip() + ' '
        root.append(elem)

        tag = 'GridModelName'
        elem = Element(tag)
        elem.text = ' ' + self.__rmsGridModelName.strip() + ' '
        root.append(elem)

        tag = 'ZoneParamName'
        elem = Element(tag)
        elem.text = ' ' + self.__rmsZoneParamName.strip() + ' '
        root.append(elem)

        tag = 'RegionParamName'
        elem = Element(tag)
        if self.__rmsRegionParamName != '':
            elem.text = ' ' + self.__rmsRegionParamName.strip() + ' '
            root.append(elem)

        tag = 'ResultFaciesParamName'
        elem = Element(tag)
        elem.text = ' ' + self.__rmsFaciesParamName.strip() + ' '
        root.append(elem)

        tag = 'PrintInfo'
        elem = Element(tag)
        elem.text = ' ' + str(self.__debug_level.value) + ' '
        root.append(elem)

        tag = 'SeedFile'
        elem = Element(tag)
        elem.text = ' ' + str(self.__seedFileName) + ' '
        root.append(elem)

        tag = 'WriteSeeds'
        elem = Element(tag)
        if self.writeSeeds:
            elem.text = ' ' + 'yes' + ' '
        else:
            elem.text = ' ' + 'no' + ' '

        root.append(elem)

        # Add command MainFaciesTable
        self.__faciesTable.XMLAddElement(root)

        # Add command GaussFieldJobNames
        self.__rmsGFJobs.XMLAddElement(root)

        # Add command ZoneModels
        tag = 'ZoneModels'
        zoneListElement = Element(tag)

        if len(self.__zoneModelTable.items()) > 0 and len(self.__sortedZoneModelTable.items()) == 0:
            # Define sorted sequence of the zone models
            self.__sortedZoneModelTable = collections.OrderedDict(sorted(self.__zoneModelTable.items()))

        for key, zoneModel in self.__sortedZoneModelTable.items():
            # Add command Zone
            zoneModel.XMLAddElement(zoneListElement)
        root.append(zoneListElement)
        rootReformatted = prettify(root)
        return rootReformatted

    def writeModel(self, modelFileName, debug_level=Debug.OFF):
        top = Element('APSModel', {'version': self.__apsModelVersion})
        rootUpdated = self.XMLAddElement(top)
        with open(modelFileName, 'w') as file:
            file.write(rootUpdated)
        if debug_level >= Debug.VERY_VERBOSE:
            print('Write file: ' + modelFileName)

    @staticmethod
    def writeModelFromXMLRoot(inputETree, outputModelFileName):
        print('Write file: ' + outputModelFileName)
        root = inputETree.getroot()
        rootReformatted = prettify(root)
        with open(outputModelFileName, 'w') as file:
            file.write(rootReformatted)

