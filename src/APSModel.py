#!/bin/env python
import datetime
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element

import copy

from src.APSGaussFieldJobs import APSGaussFieldJobs
from src.APSMainFaciesTable import APSMainFaciesTable
from src.APSZoneModel import APSZoneModel
from src.utils.methods import prettify
from src.xmlFunctions import getTextCommand
from src.utils.constants import Debug


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
       def getZoneModel(self,zoneNumber,mainLevelFacies=None)
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
       def setPrintInfo(self,debug_level)
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
            self, modelFileName=None, rmsProjectName='', rmsWorkflowName='', rmsGaussFieldScriptName='',
            rmsGridModelName='', rmsZoneParameterName='', rmsFaciesParameterName='', rmsGFJobs=None,
            rmsHorizonRefName='', rmsHorizonRefNameDataType='', mainFaciesTable=None,
            zoneModelListMainLevel=None, zoneModelListSecondLevel=None,
            previewZone=0, previewCrossSection='IJ', previewScale=1.0, debug_level=Debug.OFF):
        # Local variables
        self.__className = self.__class__.__name__
        self.__rmsProjectName = rmsProjectName
        self.__rmsWorkflowName = rmsWorkflowName
        self.__rmsGaussFieldScriptName = rmsGaussFieldScriptName

        self.__rmsGridModelName = rmsGridModelName
        self.__rmsZoneParamName = rmsZoneParameterName
        self.__rmsFaciesParamName = rmsFaciesParameterName
        self.__rmsGFJobs = rmsGFJobs

        self.__refHorizonNameForVariogramTrend = rmsHorizonRefName
        self.__refHorizonReprNameForVariogramTrend = rmsHorizonRefNameDataType

        self.__faciesTable = mainFaciesTable
        self.__zoneModelsMainLevel = zoneModelListMainLevel if zoneModelListMainLevel else []
        self.__zoneNumberList = []
        self.__zoneModelsSecondLevel = zoneModelListSecondLevel if zoneModelListSecondLevel else []
        self.__selectedZoneNumberList = []
        self.__previewZone = previewZone
        self.__previewCrossSection = previewCrossSection
        self.__previewScale = previewScale
        self.__debug_level = debug_level

        # self.__previewGridNx = 300
        # self.__previewGridNy = 300
        # self.__previewGridXSize = 1000.0
        # self.__previewGridYSize = 1000.0
        # self.__previewGridOrientation = 0.0
        # Read model if it is defined
        if modelFileName is None:
            return
        self.__interpretXMLModelFile(modelFileName, debug_level=debug_level)

    def __interpretXMLModelFile(self, modelFileName, debug_level=Debug.OFF):
        tree = ET.parse(modelFileName)
        self.__ET_Tree = tree
        root = tree.getroot()

        # --- PrintInfo ---
        kw = 'PrintInfo'
        obj = root.find(kw)
        if obj is None:
            # Default value is set
            self.__debug_level = Debug.SOMEWHAT_VERBOSE
        else:
            text = obj.text
            self.__debug_level = int(text.strip())
        if self.__debug_level >= Debug.VERY_VERBOSE:
            print(' ')
            print('Debug output: ------------ Start reading model file in APSModel ------------------')
            print(' ')

        # --- Preview ---
        kw = 'Preview'
        obj = root.find(kw)
        if obj is not None:
            text = obj.get('zoneNumber')
            if text is None:
                raise ValueError('Must specify zoneNumber attribute in keyword {}'.format(kw))
            self.__previewZone = int(text)

            text = obj.get('crossSection')
            if text is None:
                raise ValueError('Must specify crossSection attribute in keyword {}'.format(kw))
            self.__previewCrossSection = text

            text = obj.get('scale')
            if text is None:
                raise ValueError('Must specify scale attribute in keyword {}'.format(kw))
            self.__previewScale = float(text)

        # --- SelectedZones ---
        kw = 'SelectedZones'
        obj = root.find(kw)
        if obj is not None:
            text = obj.text
            words = text.split()
            for w in words:
                w2 = w.strip()
                self.__selectedZoneNumberList.append(int(w2))

        placement = {
            'RMSProjectName':          '__rmsProjectName',
            'RMSWorkflowName':         '__rmsWorkflowName',
            'RMSGaussFieldScriptName': '__rmsGaussFieldScriptName',
            'GridModelName':           '__rmsGridModelName',
            'ZoneParamName':           '__rmsZoneParamName',
            'ResultFaciesParamName':   '__rmsFaciesParamName',
        }
        for keyword, variable in placement.items():
            prefix = '_' + self.__class__.__name__
            value = getTextCommand(root, keyword, modelFile=modelFileName)
            self.__setattr__(prefix + variable, value)

        # Read all gauss field jobs and their gauss field 3D parameter names
        self.__rmsGFJobs = APSGaussFieldJobs(self.__ET_Tree, modelFileName)

        # Read all facies names available
        self.__faciesTable = APSMainFaciesTable(self.__ET_Tree, modelFileName)

        if self.__debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: RMSGridModel: ' + self.__rmsGridModelName)
            print('Debug output: RMSZoneParamName: ' + self.__rmsZoneParamName)
            print('Debug output: RMSFaciesParamName: ' + self.__rmsFaciesParamName)
            print('Debug output: Name of RMS project read:  ' + self.__rmsProjectName)
            print('Debug output: Name of RMS workflow read: ' + self.__rmsWorkflowName)
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
        for zone in zModels.findall('Zone'):
            if zone is None:
                raise IOError(
                    'Error when reading model file: {}\n'
                    'Error: Missing keyword Zone in keyword ZoneModels'
                    ''.format(modelFileName)
                )

            zoneNumber = int(zone.get('number'))
            mainLevelFacies = zone.get('mainLevelFacies')
            if mainLevelFacies is None:
                if zoneNumber not in self.__zoneNumberList:
                    # List of zone numbers
                    self.__zoneNumberList.append(zoneNumber)

                    if self.__debug_level >= Debug.VERY_VERBOSE:
                        print(' ')
                        print(' ')
                        print('Debug output: ---- Read zone model for zone number: ' + str(zoneNumber))

                    # List of main level facies models for each zone
                    zoneModel = APSZoneModel(self.__ET_Tree, zoneNumber, mainLevelFacies, modelFileName)
                    self.__zoneModelsMainLevel.append(zoneModel)

                    # Allocate space for list of list of secondary models.
                    # This is just to allocate length of the list.
                    # The content will be overwritten. The length of the list must be equal to
                    # the length of self.__zoneModelsMainLevel list.
                    # Each element of the zoneModelsSecondLevel is a list of all models for
                    # second level facies for one realisation of main level facies. If the
                    # main level facies realisation contain n facies, there can be up to n facies models
                    # for the second level facies.
                    self.__zoneModelsSecondLevel.append(zoneModel)
                else:
                    raise ValueError('Error: Multiple specification of models for zone number: {}'.format(zoneNumber))

        for i in range(len(self.__zoneModelsSecondLevel)):
            # Entry number i corresponds to the zoneModelsMainLevel[i]
            # Each entry is a list of secondLevel zoneModels initialized to empty
            self.__zoneModelsSecondLevel[i] = []

        for zone in zModels.findall('Zone'):
            zoneNumber = int(zone.get('number'))
            mainLevelFacies = zone.get('mainLevelFacies')
            if mainLevelFacies is not None:
                # Now read only second level facies models
                for i in range(self.__nZones()):
                    zM = self.__zoneModelsMainLevel[i]
                    sNr = zM.getZoneNumber()
                    if sNr == zoneNumber:
                        if zM.hasFacies(mainLevelFacies):
                            # This second level model belongs to an existing first level facies
                            # model for this zone
                            if self.__debug_level >= Debug.VERY_VERBOSE:
                                text = 'Second level facies model defined for zone: ' + str(zoneNumber)
                                text = text + ' for main level facies: ' + mainLevelFacies
                                print(text)
                            secondLevelModel = APSZoneModel(self.__ET_Tree, zoneNumber, mainLevelFacies, modelFileName)
                            self.__zoneModelsSecondLevel[i].append(secondLevelModel)

        # Check that second level models are not duplicated
        for i in range(self.__nZones()):
            for j in range(len(self.__zoneModelsSecondLevel[i])):
                zM1 = self.__zoneModelsSecondLevel[i][j]
                f1 = zM1.getMainLevelFacies()
                for k in range(len(self.__zoneModelsSecondLevel[i])):
                    if j != k:
                        zM2 = self.__zoneModelsSecondLevel[i][k]
                        f2 = zM2.getMainLevelFacies()
                        if f1 == f2:
                            zoneNumber = zM2.getZoneNumber()
                            raise ValueError(
                                'Error: There are multiple specification of second level facies\n'
                                ' models for the main level facies: {}'
                                ' for zone number: {}'.format(f1, zoneNumber)
                            )

        if self.__printInfo >= 3:
            print(' ')
            print('------------ End reading model file in APSModel ------------------')
            print(' ')

    def updateXMLModelFile(self, modelFileName, parameterFileName, debug_level=Debug.OFF):
        # Read XML model file
        tree = ET.parse(modelFileName)
        root = tree.getroot()

        # Scan XML model file for variables that can be updated by FMU/ERT
        # These variables belongs to xml keywords with attribute 'kw'.
        # So search for attribute 'kw' to find all these variables. The attribute value is a keyword
        # name that will be used as identifier.
        if debug_level > Debug.SOMEWHAT_VERBOSE:
            print(' ')
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
        if debug_level > Debug.VERY_VERBOSE:
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
                if debug_level > Debug.VERY_VERBOSE:
                    print('{0:30} {1:20}  {2:10}'.format(keyWord, oldValue, obj.text))
            else:
                raise ValueError(
                    'Error: Inconsistency. Programming error in function updateXMLModelFile in class APSModel'
                )

        if debug_level > Debug.VERY_VERBOSE:
            print(' ')

        return tree

    def __nZones(self):
        if self.__zoneModelsMainLevel:
            return len(self.__zoneModelsMainLevel)
        else:
            return 0

    def __readParamFromFile(self, inputFile, debug_level=Debug-OFF):
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
                    # Skip line (searcing for an assignment like keyword = value with at least 3 words
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
            print(' ')
        # End read file

        return keywordsFMU

    #  ---- Get functions -----
    def getXmlTree(self):
        tree = self.__ET_Tree
        return tree

    def getRoot(self):
        tree = self.__ET_Tree
        root = tree.getroot()
        return root

    def getSelectedZoneNumberList(self):
        return copy.copy(self.__selectedZoneNumberList)

    # Get pointer to zone model object
    def getZoneModel(self, zoneNumber, mainLevelFacies=None):
        foundModel = None
        for i in range(len(self.__zoneNumberList)):
            if self.__zoneNumberList[i] == zoneNumber:
                if mainLevelFacies is None:
                    foundModel = self.__zoneModelsMainLevel[i]
                else:
                    for j in range(len(self.__zoneModelsSecondLevel[i])):
                        zM = self.__zoneModelsSecondLevel[i][j]
                        fName = zM.getMainLevelFacies()
                        if fName == mainLevelFacies:
                            foundModel = zM
        return foundModel

    def getGridModelName(self):
        return copy.copy(self.__rmsGridModelName)

    def getResultFaciesParamName(self):
        return copy.copy(self.__rmsFaciesParamName)

    def getZoneNumberList(self):
        return copy.copy(self.__zoneNumberList)

    #    def getPreviewZone(self):
    #        return [self.__previewZone,self.__previewGridNx,self.__previewGridNy,
    #                self.__previewGridXSize, self.__previewGridYSize,
    #                self.__previewGridOrientation]

    def getPreviewZoneNumber(self):
        return self.__previewZone

    def getPreviewCrossSection(self):
        return self.__previewCrossSection

    def getPreviewScale(self):
        return self.__previewScale

    def getAllGaussFieldNamesUsed(self):
        gfAllZones = []
        for zone in self.__zoneModelsMainLevel:
            gfNames = zone.getUsedGaussFieldNames()
            for z in gfNames:
                if z not in gfAllZones:
                    gfAllZones.append(z)
        return copy.copy(gfAllZones)

    def getZoneParamName(self):
        return copy.copy(self.__rmsZoneParamName)

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
        for zone in self.__zoneModelsMainLevel:
            probParamList = zone.getAllProbParamForZone()
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

    def setPrintInfo(self, printInfo):
        if printInfo < 0:
            printInfo = 0
        self.__printInfo = printInfo
        return

    def setSelectedZoneNumberList(self, selectedZoneNumbers):
        self.__selectedZoneNumberList = []
        for i in range(len(selectedZoneNumbers)):
            number = selectedZoneNumbers[i]
            if not (number in self.__zoneNumberList):
                raise ValueError(
                    'Error in {} in setSelectedZoneNumberList\n'
                    'Error:  Selected zone number: {} is not among the possible zone numbers.'
                    ''.format(self.__className, number)
                )
            self.__selectedZoneNumberList.append(number)

    def setPreviewZoneNumber(self, zoneNumber):
        if not (zoneNumber in self.__zoneNumberList):
            raise ValueError(
                'Error in {} in setPreviewZoneNumber\n'
                'Error:  Zone number: {} is not among the possible zone numbers.'
                ''.format(self.__className, zoneNumber)
            )
        else:
            self.__previewZone = zoneNumber

    def setPreviewCrossSection(self, crossSection):
        if not (crossSection == 'IJ' or crossSection == 'IK' or crossSection == 'JK'):
            raise ValueError(
                'Error in {} in setPreviewCrossSection\n'
                'Error:  Cross section is not IJ, IK or JK.')
        else:
            self.__previewCrossSection = crossSection

    def setPreviewScale(self, scale):
        if not (scale > 0.0):
            raise ValueError(
                'Error in {} in setPreviewScale\n'
                'Error:  Scale factor must be > 0'
            )
        else:
            self.__previewScale = scale

    # Add the pointer to the new zone object into the zone list
    def addNewZone(self, zoneObject):
        zoneNumber = zoneObject.getZoneNumber()
        self.__zoneModelsMainLevel.append(zoneObject)
        self.__zoneNumberList.append(zoneNumber)

    def deleteZone(self, zoneNumber):
        for i in range(len(self.__zoneModelsMainLevel)):
            zone = self.__zoneModelsMainLevel[i]
            zNr = zone.getZoneNumber()
            if zNr == zoneNumber:
                # Remove zone object from list (and forget it)
                self.__zoneModelsMainLevel.pop(i)

                # Remove zone number from zoneNumber list
                self.__zoneNumberList.pop(i)
                # Check if the zone number is in the selected list
                if zoneNumber in self.__selectedZoneNumberList:
                    for j in range(len(self.__selectedZoneNumberList)):
                        zNr = self.__selectedZoneNumberList[j]
                        if zNr == zoneNumber:
                            # Remove zone number from selected zoneNumber list
                            self.__selectedZoneNumberList.pop(j)
                            break
                break

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
        zoneNumberList = self.__zoneNumberList
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

            for zIndx in range(nZones):
                zoneNumber = zoneNumberList[zIndx]
                if zoneNumber not in self.__selectedZoneNumberList:
                    continue
                file.write('// --- RMS zone number {} parameter settings ---\n'.format(zoneNumber))
                currentZoneModel = self.__zoneModelsMainLevel[zIndx]
                gaussFieldNamesInZoneModel = currentZoneModel.getUsedGaussFieldNames()
                nGFParamUsed = len(gaussFieldNamesInZoneModel)

                for i in range(nGFParamUsed):
                    gfNameUsed = gaussFieldNamesInZoneModel[i]
                    file.write('Print("Update Gauss field: ","{}"," for zone: ",{})\n'.format(gfNameUsed, zoneNumber))

                    # Check which rms job this gauss field parameter belongs to
                    for j in range(nJobs):

                        currentJobName = jobNames[j]
                        if jobObject.checkGaussFieldNameInJob(currentJobName, gfNameUsed):
                            updateJob[j] = 1
                            # This job must be updated with variogram parameters
                            # for current zone number
                            gfIndx = jobObject.getGaussFieldIndx(currentJobName, gfNameUsed)
                            varioType = currentZoneModel.getVarioType(gfNameUsed)
                            range1 = currentZoneModel.getMainRange(gfNameUsed)
                            range2 = currentZoneModel.getPerpRange(gfNameUsed)
                            range3 = currentZoneModel.getVertRange(gfNameUsed)
                            # TODO: power is UNUSED
                            power = 1.0
                            if varioType == 'GEN_EXPONENTIAL':
                                power = currentZoneModel.getPower(gfNameUsed)

                            file.write('job = "{}"\n'.format(currentJobName))

                            file.write(
                                'paramName = "Zone[{}].Group[{}].VariogramType"\n'.format(zoneNumber, gfIndx + 1)
                            )

                            file.write('ModifyJob(job,paramName,"{}")\n'.format(varioType))
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

        # Add a command specifying which zone to use in for preview
        # This is temporary solution
        if self.__printInfo >= 3:
            print('Debug output: call XMLADDElement from ' + self.__className)

        if self.__previewZone > 0:
            tag = 'Preview'
            attribute = {
                'zoneNumber':   str(self.__previewZone),
                'crossSection': str(self.__previewCrossSection),
                'scale':        str(self.__previewScale)
            }
            elem = Element(tag, attribute)
            root.append(elem)
        # If selected zone list is defined (has elements) write them to a keyword
        if len(self.__selectedZoneNumberList) > 0:
            selectedZoneString = ' '
            for i in range(len(self.__selectedZoneNumberList)):
                sNr = self.__selectedZoneNumberList[i]
                selectedZoneString = selectedZoneString + str(sNr) + ' '
            tag = 'SelectedZones'
            elem = Element(tag)
            elem.text = selectedZoneString
            root.append(elem)

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

        tag = 'ResultFaciesParamName'
        elem = Element(tag)
        elem.text = ' ' + self.__rmsFaciesParamName.strip() + ' '
        root.append(elem)

        tag = 'PrintInfo'
        elem = Element(tag)
        elem.text = ' ' + str(self.__debug_level) + ' '
        root.append(elem)

        # Add command MainFaciesTable
        self.__faciesTable.XMLAddElement(root)

        # Add command GaussFieldJobNames
        self.__rmsGFJobs.XMLAddElement(root)

        # Add command ZoneModels
        tag = 'ZoneModels'
        elem = Element(tag)
        root.append(elem)
        zoneListElement = elem
        for i in range(len(self.__zoneModelsMainLevel)):
            zoneObject = self.__zoneModelsMainLevel[i]
            # Add command Zone
            zoneObject.XMLAddElement(zoneListElement)

        # Add command ZoneModels for secondLevel facies models
        if self.__zoneModelsSecondLevel is not None:
            for i in range(len(self.__zoneModelsSecondLevel)):
                for j in range(len(self.__zoneModelsSecondLevel[i])):
                    zoneObject = self.__zoneModelsSecondLevel[i][j]
                    # Add command Zone
                    zoneObject.XMLAddElement(zoneListElement)

        rootReformatted = prettify(root)
        return rootReformatted

    def writeModel(self, modelFileName, debug_level=Debug.OFF):
        print('Write file: ' + modelFileName)
        top = Element('APSModel')
        rootUpdated = self.XMLAddElement(top)
        with open(modelFileName, 'w') as file:
            file.write(rootUpdated)
        return

    def writeModelFromXMLRoot(self, inputETree, outputModelFileName):
        print('Write file: ' + outputModelFileName)
        root = inputETree.getroot()
        rootReformatted = prettify(root)
        with open(outputModelFileName, 'w') as file:
            file.write(rootReformatted)

# def get2DMapRefHorizonName(self):
#        return copy.copy(self.__refHorizonNameForVarioTrend)
#
#    def get2DMapRefHorizonType(self):
#        return copy.copy(self.__refHorizonReprNameForVarioTrend)
#
#
#    def getCellForPreview(self):
#        if len(self.__previewCell) == 0:
#            text = 'Error: Must specify indices (I,J,K) for grid cell '
#            text = text + 'whose probability should be used in previewer as constant probabilities'
#            sys.exit()
#        return copy.copy(self.__previewCell)
