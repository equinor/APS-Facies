#!/bin/env python
# -*- coding: utf-8 -*-
import collections
import copy
import xml.etree.ElementTree as ET

from src.algorithms.APSMainFaciesTable import APSMainFaciesTable
from src.algorithms.APSZoneModel import APSZoneModel
from src.algorithms.properties import CrossSection
from src.utils.constants.simple import Debug
from src.utils.exceptions.xml import MissingAttributeInKeyword
from src.utils.numeric import isNumber
from src.utils.xmlUtils import getKeyword, getTextCommand, prettify, minify, get_region_number
from src.utils.io import GlobalVariables


class APSModel:
    """
    Class APSModel  - contains the data structure for data read from model file

    Class member variables:

    Public member functions:
      def __init__(
            self, modelFileName=None,  apsmodelversion='1.0', rmsProjectName='', rmsWorkflowName='',
            rmsGridModelName='', rmsZoneParameterName='', rmsRegionParameterName='',
            rmsFaciesParameterName='', seedFileName='seed.dat', write_seeds=True,
            mainFaciesTable=None, zoneModelTable=None,
            previewZone=0, previewRegion=0, previewCrossSectionType='IJ', previewCrossSectionRelativePos=0.5,
            previewScale=1.0, previewResolution='Normal', debug_level=Debug.OFF):


      def updateXMLModelFile(self, modelFileName, parameter_file_name, debug_level=Debug.OFF)
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

      Properties:
        debug_level
        seed_file_name
        preview_scale
        preview_cross_section
        preview_cross_section_type
        preview_cross_section_relative_position
        preview_resolution

      Get data from data structure:

       def getXmlTree(self)
       def getRoot(self)
       def isAllZoneRegionModelsSelected(self)
       def getSelectedZoneNumberList(self)
       def getSelectedRegionNumberListForSpecifiedZoneNumber(self,zoneNumber)
       def isSelected(self, zoneNumber, regionNumber)
       def getZoneModel(self,zoneNumber,regionNumber=0)
       def getAllZoneModels(self)
       def sorted_zone_models(self)
       def getGridModelName(self)
       def getResultFaciesParamName(self)
       def getZoneNumberList(self)
       def getRegionNumberListForSpecifiedZoneNumber(self,zoneNumber)
       def getPreviewZoneNumber(self)
       def getPreviewRegionNumber(self)
       def getAllGaussFieldNamesUsed(self)
       def getZoneParamName(self)
       def getRegionParamName(self)
       def getSeedFileName(self)
       def getMainFaciesTable(self)
       def getRMSProjectName(self)
       def getAllProbParam(self)

      Set data and update data structure:

       def setRmsProjectName(self,name)
       def setRmsWorkflowName(self,name)
       def setRmsGridModelName(self,name)
       def setRmsZoneParamName(self,name)
       def setRmsResultFaciesParamName(self,name)
       def setSelectedZoneAndRegionNumber(self, selectedZoneNumber,selectedRegionNumber=0)
       def setPreviewZoneAndRegionNumber(self, zoneNumber,regionNumber=0)
       def addNewZone(self,zoneObject)
       def deleteZone(self,zoneNumber)
       def setMainFaciesTable(self,faciesTableObj)


    Private member functions:
     def __interpretXMLModelFile(self,modelFileName, debug_level)
                 - Read xml file and put the data into data structure
     def __checkZoneModels(self)
                 - Check that an APSModel does not have specifications of zone models for (zone,region) pairs that are overlapping.
                   Hence, it is not allowed to specify (zone=1, region=0) and (zone=1, region=0).
                   The first (zone=1, region=0) means that the zone  model specification is defined for all grid cells in zone=1.
                   The second (zone=1, region=1) means that the zone model is defined for those grid cells belonging to zone=1
                   and at the same time to region=1. It follows that all grid cells belonging to zone=1 and region=1
                   have two different models which is not unique and not allowed.

     def __readParamFromFile(self,inputFile,debug_level)
                 - Read IPL include file to get updated model parameters from FMU

    -----------------------------------------------------------------------------
    """

    def __init__(
            self,
            model_file_name=None,
            aps_model_version='1.0',
            rms_project_name=None,
            rms_workflow_name=None,
            rms_grid_model_name=None,
            rms_zone_parameter_name=None,
            rms_region_parameter_name=None,
            rms_facies_parameter_name=None,
            seed_file_name='seed.dat',
            write_seeds=True,
            main_facies_table=None,
            zone_model_table=None,
            preview_zone=0,
            preview_region=0,
            preview_cross_section_type='IJ',
            preview_cross_section_relative_pos=0.5,
            preview_scale=1.0,
            preview_resolution='Normal',
            debug_level=Debug.OFF
    ):
        """
         The following parameters are necessary to define a model:
         If a model is created from a model file, the only necessary input is modelFileName

         If the model is created from e.g APSGUI, these parameters must be specified:
         rmsProjectName - Name of RMS project which will run a workflow using the APS method (Now Optional)
         rmsWorkflowName - Name of RMS workflow for APS model (Now Optional)
         rmsGridModelName - Name of grid model in RMS project.
         rmsZoneParameterName - Zone parameter for the grid model in the RMS project.
         rmsRegionParameterName - Region parameter for the grid model in the RMS project (Optional if there are no zones
             with regions.
         rmsFaciesParameterName - Facies parameter to be updated in the grid model in the RMS project by the APS model.
         seedFileName - Name of seed file to be used. Used by scripts for simulation of gaussian fields.
         write_seeds - Boolean variable. True if the seed is to be written to seed file, False if the seed file is to be read.
                      Used by scripts simulating gaussian fields.
         mainFaciesTable - Object containing the global facies table with facies names an associated
                           facies code common for the RMS project. All facies to be modelled must be defined
                           in the mainFaciesTable.
         zoneModelTable - Dictionary with key = (zoneNumber, regionNumber) containing zoneModels as values.
                          Each zoneModel will be associated with the grid cells in the grid model that belongs to
                          a specified zoneNumber and regionNumber. If regionNumber is not used (is equal to 0),
                          the facies realization will be calculated for the grid cells belonging to the specified zone number.
                          The maximum possible zoneModels will be the sum over all defined (zoneNumber,regionNumber) pairs
                          that exist in the grid model. It is possible (but not very useful) that an APS model is defined for
                          only one (zoneNumber,regionNumber) pair and there does not exist any grid cells satisfying
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
         previewResolution - Define  whether the testPreview program should use higher resolution or not compared with
                             default resolution taken from the grid model.
         debugLevel - Define amount of output to the screen during runs

        """
        # Local variables
        self.__class_name = self.__class__.__name__

        self.__aps_model_version = aps_model_version

        self.__ET_Tree = None

        self.__rmsProjectName = rms_project_name
        self.__rmsWorkflowName = rms_workflow_name
        self.__rmsGridModelName = rms_grid_model_name
        self.__rmsZoneParamName = rms_zone_parameter_name
        self.__rmsRegionParamName = rms_region_parameter_name
        self.__rmsFaciesParamName = rms_facies_parameter_name
        self.__seed_file_name = seed_file_name
        self.write_seeds = write_seeds

        self.__faciesTable = main_facies_table
        self.__zoneModelTable = zone_model_table if zone_model_table else {}
        self.__sortedZoneModelTable = {}
        self.__zoneNumberList = []
        self.__selectedZoneAndRegionNumberTable = {}
        self.__selectAllZonesAndRegions = True
        self.__previewZone = preview_zone
        self.__previewRegion = preview_region
        self.__preview_cross_section = CrossSection(preview_cross_section_type, preview_cross_section_relative_pos)
        self.__previewScale = preview_scale
        self.__previewResolution = preview_resolution
        self.__debug_level = debug_level

        # Read model if it is defined
        if model_file_name is not None:
            self.__interpretXMLModelFile(model_file_name, debug_level=debug_level)

    @property
    def use_constant_probability(self):
        return all([model.useConstProb() for model in self.__zoneModelTable.values()])

    def __interpretXMLModelFile(self, modelFileName, debug_level=Debug.OFF):
        root = ET.parse(modelFileName).getroot()
        self.__interpretTree(root, debug_level, modelFileName)

    @classmethod
    def from_string(cls, xml_content):
        root = ET.fromstring(xml_content)
        return cls().__interpretTree(root, Debug.VERY_VERBOSE)

    def __interpretTree(self, root, debug_level=Debug.OFF, modelFileName=None):
        self.__ET_Tree = ET.ElementTree(root)
        if root.tag != 'APSModel':
            raise ValueError(
                'The root element must be APSModel'
            )
        apsmodel_version = root.get('version')
        if apsmodel_version is None:
            raise ValueError('attribute version is not defined in root element')
        elif apsmodel_version != "1.0":
            raise ValueError(
                'Illegal value ( {} ) specified for apsmodelversion (only 1.0 is supported)'
                ''.format(apsmodel_version)
            )
        self.__aps_model_version = apsmodel_version

        # --- PrintInfo ---
        kw = 'PrintInfo'
        obj = root.find(kw)
        if obj is None:
            # Default value is set
            self.__debug_level = debug_level
        else:
            text = obj.text
            self.debug_level = text
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
            self.__preview_cross_section.type = text

            text = obj.get('crossSectionRelativePos')
            if text is None:
                raise MissingAttributeInKeyword(kw, 'crossSectionRelativePos')
            self.__preview_cross_section.relative_position = float(text.strip())

            text = obj.get('scale')
            if text is None:
                raise MissingAttributeInKeyword(kw, 'scale')
            self.__previewScale = float(text.strip())

            text = obj.get('resolution')
            if text is None:
                self.__previewResolution = "Normal"
            else:
                self.__previewResolution = text.strip()
                if not (self.__previewResolution == "Normal" or self.__previewResolution == "High"):
                    raise ValueError('Preview resolution must be specified to be either Normal orr High\n'
                                     'Default value is Normal if resolution is not specified')

        placement = [
            ('RMSProjectName', '__rmsProjectName', False),
            ('RMSWorkflowName', '__rmsWorkflowName', False),
            ('GridModelName', '__rmsGridModelName', True),
            ('ZoneParamName', '__rmsZoneParamName', True),
            ('ResultFaciesParamName', '__rmsFaciesParamName', True),
        ]
        for keyword, variable, required in placement:
            prefix = '_' + self.__class__.__name__
            value = getTextCommand(root, keyword, parentKeyword='APSModel', modelFile=modelFileName, required=required)
            setattr(self, prefix + variable, value)

        # Read keyword for region parameter
        # Note that the keyword is required if there are zones in the zone model where the zone has
        # attribute regionNumber, otherwise not.
        zones_with_region_attr = self.__ET_Tree.findall('.//Zone[@regionNumber]')
        keyword = 'RegionParamName'
        value = getTextCommand(
            root, keyword,
            parentKeyword='APSModel',
            defaultText=None,
            modelFile=modelFileName,
            required=len(zones_with_region_attr) > 0
        )
        if value is not None:
            self.__rmsRegionParamName = value

        # Read optional keyword to specify name of seed file
        keyword = 'SeedFile'
        value = getTextCommand(root, keyword, parentKeyword='APSModel', defaultText='seed.dat', modelFile=modelFileName, required=False)
        self.__seed_file_name = value

        # Read optional keyword to specify the boolean variable write_seeds
        keyword = 'WriteSeeds'
        value = getTextCommand(root, keyword, parentKeyword='APSModel', defaultText='yes', modelFile=modelFileName, required=False)
        if value.upper() == 'YES':
            self.write_seeds = True
        else:
            self.write_seeds = False

        # Read all facies names available
        self.__faciesTable = APSMainFaciesTable(ET_Tree=self.__ET_Tree, modelFileName=modelFileName)

        if self.__debug_level >= Debug.VERY_VERBOSE:
            print(
                'Debug output: RMSGridModel:                       {}\n'
                'Debug output: RMSZoneParamName:                   {}\n'
                'Debug output: RMSFaciesParamName:                 {}\n'
                'Debug output: RMSRegionParamName:                 {}\n'
                'Debug output: Name of RMS project read:           {}\n'
                'Debug output: Name of RMS workflow read:          {}'
                ''.format(
                    self.__rmsGridModelName, self.__rmsZoneParamName, self.__rmsFaciesParamName,
                    self.__rmsRegionParamName, self.__rmsProjectName, self.__rmsWorkflowName
                )
            )

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
        if self.__debug_level >= Debug.VERY_VERBOSE:
            print('')
            print('--- Number of specified zone models: {}'.format(len(zModels.findall('Zone'))))
            print('')

        for zone in zModels.findall('Zone'):
            if zone is None:
                raise IOError(
                    'Error when reading model file: {}\n'
                    'Error: Missing keyword Zone in keyword ZoneModels'
                    ''.format(modelFileName)
                )
            zone_number = int(zone.get('number'))
            if zone_number <= 0:
                raise ValueError(
                    'Zone number must be a positive integer. '
                    'Can not have zone number: {}'.format(zone_number)
                )
            region_number = get_region_number(zone)

            # The model is identified by the combination (zoneNumber, regionNumber)
            zoneModelKey = (zone_number, region_number)
            if zoneModelKey not in self.__zoneModelTable:

                if self.__debug_level >= Debug.VERY_VERBOSE:
                    print('')
                    print('')
                    if region_number <= 0:
                        print('Debug output: ---- Read zone model for zone number: {}'.format(zone_number))
                    else:
                        print(
                            'Debug output: ---- Read zone model for (zone,region) number: ({},{})'
                            ''.format(zone_number, region_number)
                        )

                zone_model = APSZoneModel(
                    ET_Tree=self.__ET_Tree,
                    zoneNumber=zone_number,
                    regionNumber=region_number,
                    modelFileName=modelFileName
                )
                # This zoneNumber, regionNumber combination is not defined previously
                # and must be added to the dictionary
                self.__zoneModelTable[zoneModelKey] = zone_model
            else:
                raise ValueError(
                    'Can not have two or more entries of  keyword Zone with the same '
                    'zoneNumber and regionNumber.\n'
                    'Can not have multiple specification of (zoneNumber, regionNumber) = ({},{})'
                    ''.format(zone_number, region_number)
                )

        # --- SelectedZones ---
        kw = 'SelectedZonesAndRegions'
        obj = getKeyword(root, kw, modelFile=modelFileName, required=False)
        if obj is not None:
            # The keyword is specified. This means that in general a subset of
            # all zones and region combinations are selected.
            # Read this sub set of zone and region combinations.
            self.__selectAllZonesAndRegions = False
            kw2 = 'SelectedZoneWithRegions'
            objSelectedZone = None
            for objSelectedZone in obj.findall(kw2):
                text = objSelectedZone.get('zone')
                zone_number = int(text.strip())

                text = objSelectedZone.text
                if len(text.strip()) == 0:
                    region_number = 0
                    # Empty list of region numbers
                    zone_model = self.getZoneModel(zoneNumber=zone_number, regionNumber=region_number)
                    if zone_model is None:
                        raise ValueError(
                            'Can not select to use zone model with zone number: {} and region number: {} '
                            'This zone model is not defined'
                            ''.format(zone_number, region_number)
                        )
                    # A model for (zoneNumber,regionNumber=0) is defined
                    selected_key = (zone_number, region_number)
                    self.__selectedZoneAndRegionNumberTable[selected_key] = 1
                else:
                    words = text.split()
                    for w in words:
                        w2 = w.strip()
                        if isNumber(w2):
                            region_number = int(w2)
                            zone_model = self.getZoneModel(zoneNumber=zone_number, regionNumber=region_number)
                            if zone_model is None:
                                raise ValueError(
                                    'Can not select to use zone model with zone number: {} and region number: {} '
                                    'This zone model is not defined'
                                    ''.format(str(zone_number), str(region_number))
                                )
                            # A model for this (zoneNumber,regionNumber) pair is defined
                            selected_key = (zone_number, region_number)
                            self.__selectedZoneAndRegionNumberTable[selected_key] = 1

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

        if self.__debug_level >= Debug.SOMEWHAT_VERBOSE:
            if self.__debug_level >= Debug.SOMEWHAT_VERBOSE:
                print('- Zone models are defined for the following combination '
                      'of zone and region numbers:')
                for key, value in self.sorted_zone_models.items():
                    zone_number = key[0]
                    region_number = key[1]
                    if region_number == 0:
                        print('    Zone: {}'.format(zone_number))
                    else:
                        print('    Zone: {}  Region: {}'.format(zone_number, region_number))
            print('')
            print('------------ End reading model file in APSModel ------------------')
            print('')

    def updateXMLModelFile(
            self,
            model_file_name=None,
            parameter_file_name=None,
            project=None,
            workflow_name=None,
            uncertainty_variable_names=None,
            realisation_number=0,
            debug_level=Debug.OFF,
    ):
        # Read XML model file
        tree = ET.parse(model_file_name)
        root = tree.getroot()

        # Scan XML model file for variables that can be updated by FMU/ERT
        # These variables belongs to xml keywords with attribute 'kw'.
        # So search for attribute 'kw' to find all these variables. The attribute value is a keyword
        # name that will be used as identifier.
        if debug_level > Debug.SOMEWHAT_VERBOSE:
            print('')
            print('-- Model parameters marked as possible to update when running in batch mode')
            print('Keyword:                        Tag:                Value:')
        keywords_defined_for_updating = []
        for obj in root.findall(".//*[@kw]"):
            key_word = obj.get('kw')
            tag = obj.tag
            value = obj.text
            keywords_defined_for_updating.append([key_word.strip(), value.strip()])
            if debug_level > Debug.SOMEWHAT_VERBOSE:
                print('{0:30} {1:20}  {2:10}'.format(key_word, tag, value))

        # Read keywords from parameter_file_name (Global IPL include file with variables updated by FMU/ERT)
        if parameter_file_name is not None:
            keywords_read = self.__readParamFromFile(parameter_file_name, debug_level)
        else:
            assert project
            assert workflow_name
            assert uncertainty_variable_names
            keywords_read = self.__getParamFromRMSTable(
                project, workflow_name, uncertainty_variable_names, realisation_number,
            )
        # keywordsRead = [name,value]

        # Set new values
        for i in range(len(keywords_defined_for_updating)):
            item = keywords_defined_for_updating[i]
            keyword = item[0]
            old_value = item[1]
            for j in range(len(keywords_read)):
                kw, value = keywords_read[j]
                if kw == keyword:
                    # set new value
                    item[1] = ' ' + value.strip() + ' '
        if debug_level >= Debug.VERY_VERBOSE:
            print('Debug output:  Keywords and values that is updated in xml tree:')

        for obj in root.findall(".//*[@kw]"):
            key_word = obj.get('kw')
            old_value = obj.text

            found = False
            for i in range(len(keywords_defined_for_updating)):
                item = keywords_defined_for_updating[i]
                kw = item[0]
                val = item[1]
                if kw == key_word:
                    # Update value in XML tree for this keyword
                    obj.text = val
                    found = True
                    break
            if found:
                if debug_level >= Debug.VERY_VERBOSE:
                    print('{0:30} {1:20}  {2:10}'.format(key_word, old_value, obj.text))
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
    def __readParamFromFile(global_variables_file, debug_level=Debug.OFF):
        # Search through the file line for line and skip lines commented out with '//'
        # Collect all variables that are assigned value as the three first words on a line
        # like e.g VARIABLE_NAME = 10
        if debug_level >= Debug.SOMEWHAT_VERBOSE:
            print('- Read file: ' + global_variables_file)
        keywords = GlobalVariables.parse(global_variables_file)
        if debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: Keywords and values found in parameter file:  ' + global_variables_file)
            for item in keywords:
                kw = item[0]
                val = item[1]
                print('  {0:30} {1:20}'.format(kw, val))
            print('')
        # End read file

        return keywords

    # ----- Properties ----
    @property
    def debug_level(self):
        return self.__debug_level

    @debug_level.setter
    def debug_level(self, debug_level):
        if isinstance(debug_level, str):
            debug_level = int(debug_level.strip())
        if isinstance(debug_level, int):
            debug_level = Debug(debug_level)
        if debug_level not in Debug:
            debug_level = Debug.OFF
        self.__debug_level = debug_level

    @property
    def seed_file_name(self):
        return self.__seed_file_name

    @seed_file_name.setter
    def seed_file_name(self, name):
        self.__seed_file_name = copy.copy(name)

    @property
    def preview_scale(self):
        return self.__previewScale

    @preview_scale.setter
    def preview_scale(self, scale):
        if not (scale > 0.0):
            raise ValueError(
                'Error in {} in setPreviewScale\n'
                'Error:  Scale factor must be > 0'
            )
        else:
            self.__previewScale = scale
    @property
    def preview_resolution(self):
        return self.__previewResolution

    @property
    def preview_cross_section(self):
        return self.__preview_cross_section

    @property
    def preview_cross_section_type(self):
        return self.__preview_cross_section.type

    @preview_cross_section_type.setter
    def preview_cross_section_type(self, type):
        if not (type in ['IJ', 'IK', 'JK']):
            raise ValueError(
                'Error in preview_cross_section_type\n'
                'Error:  Cross section is not IJ, IK or JK.'
            )
        else:
            self.__preview_cross_section.type = type

    @property
    def preview_cross_section_relative_position(self):
        return self.__preview_cross_section.relative_position

    @preview_cross_section_relative_position.setter
    def preview_cross_section_relative_position(self, relative_position):
        self.__preview_cross_section.relative_position = relative_position

    @staticmethod
    def __getParamFromRMSTable(project, workflow_name, uncertainty_variable_names, realisation_number, debug_level=Debug.OFF):
        """ Get values from RMS uncertainty table"""
        wf = project.workflows[workflow_name]
        rms_table_name = wf.report_table_name
        parametersUncertainty = []
        for name in uncertainty_variable_names:
            value = project.workflows.get_uncertainty(
                table_name=rms_table_name,
                uncertainty_name=name,
                realisation=realisation_number
            )
            item = (name, str(value))
            parametersUncertainty.append(item)
        return parametersUncertainty

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
    # Get pointer to zone model object

    def getSelectedZoneNumberList(self):
        selectedZoneNumberList = []
        keyList = list(self.__selectedZoneAndRegionNumberTable.keys())
        for i in range(len(keyList)):
            item = keyList[i]
            zNumber = item[0]
            if zNumber not in selectedZoneNumberList:
                selectedZoneNumberList.append(zNumber)
        return copy.copy(selectedZoneNumberList)

    def getSelectedRegionNumberListForSpecifiedZoneNumber(self, zoneNumber):
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

    def getZoneModel(self, zoneNumber, regionNumber=0):
        key = (zoneNumber, regionNumber)
        try:
            foundZoneModel = self.__zoneModelTable[key]
            return foundZoneModel
        except KeyError:
            return None

    def getAllZoneModels(self):
        return self.__zoneModelTable

    @property
    def sorted_zone_models(self):
        # Define sorted sequence of the zone models
        return collections.OrderedDict(sorted(self.__zoneModelTable.items()))

    @property
    def zone_models(self):
        return self.sorted_zone_models.values()

    @property
    def grid_model_name(self):
        return self.__rmsGridModelName

    @grid_model_name.setter
    def grid_model_name(self, name):
        self.__rmsGridModelName = name

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

    def getRegionNumberListForSpecifiedZoneNumber(self, zoneNumber):
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

    @property
    def gaussian_field_names(self):
        return self.getAllGaussFieldNamesUsed()

    def getAllGaussFieldNamesUsed(self):
        gfAllZones = []
        for key, zoneModel in self.__zoneModelTable.items():
            print('In getAllGaussFieldNamesUsed: key=({},{})'.format(key[0], key[1]))
            gfNames = zoneModel.used_gaussian_field_names
            for gf in gfNames:
                # Add the gauss field name to the list if it not already is in the list
                print('Gauss field name: {}'.format(gf))
                if gf not in gfAllZones:
                    gfAllZones.append(gf)
        return copy.copy(gfAllZones)

    @property
    def zone_parameter(self):
        return self.getZoneParamName()

    @property
    def region_parameter(self):
        return self.getRegionParamName()

    @property
    def use_regions(self):
        return bool(self.region_parameter)

    def getZoneParamName(self):
        return self.__rmsZoneParamName

    def getRegionParamName(self):
        if self.__rmsRegionParamName:
            return self.__rmsRegionParamName
        else:
            return ''

    def getMainFaciesTable(self):
        return self.__faciesTable

    def getRMSProjectName(self):
        return copy.copy(self.__rmsProjectName)

    def getRMSWorkflowName(self):
        return copy.copy(self.__rmsWorkflowName)

    def getAllProbParam(self):
        allProbList = []
        for key, zoneModel in self.__zoneModelTable.items():
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

    def setRmsGridModelName(self, name):
        self.__rmsGridModelName = copy.copy(name)

    def setRmsZoneParamName(self, name):
        self.__rmsZoneParamName = copy.copy(name)

    def setRmsRegionParamName(self, name):
        if not name:
            for key, zoneModel in self.__zoneModelTable.items():
                region_number = key[1]
                current_zone_has_at_least_one_region = 0 < region_number
                if current_zone_has_at_least_one_region:
                    raise ValueError(
                        'RegionParamName must be given when there is at least one zone in the model with region Number)'
                    )
        self.__rmsRegionParamName = copy.copy(name)

    def setRmsResultFaciesParamName(self, name):
        self.__rmsFaciesParamName = copy.copy(name)

    def setSelectedZoneAndRegionNumber(self, selectedZoneNumber, selectedRegionNumber=0):
        """
        Description: Select a new pair of (zoneNumber, regionNumber) which has not been already selected.
        """
        # Check that the specified pair (selectedZoneNumber, selectedRegionNumber) is an existing zone model
        key = (selectedZoneNumber, selectedRegionNumber)
        if key in self.__zoneModelTable:
            if key not in self.__selectedZoneAndRegionNumberTable:
                self.__selectedZoneAndRegionNumberTable[key] = 1
        else:
            raise ValueError(
                'Can not select (zoneNumber, regionNumber) = ({},{}) since the zone model does not exist'
                ''.format(str(selectedZoneNumber), str(selectedRegionNumber))
            )

    def setPreviewZoneAndRegionNumber(self, zoneNumber, regionNumber=0):
        key = (zoneNumber, regionNumber)
        if key in self.__zoneModelTable:
            self.__previewZoneNumber = zoneNumber
            self.__previewRegionNumber = regionNumber
        else:
            raise ValueError(
                'Error in {} in setPreviewZoneNumber\n'
                'Error:  (zoneNumber, regionNumber) = ({},{}) is not defined in the model'
                ''.format(self.__class_name, str(zoneNumber), str(regionNumber))
            )

    def addNewZone(self, zoneObject):
        zoneNumber = zoneObject.zone_number
        regionNumber = zoneObject.region_number
        if regionNumber > 0 and not self.__rmsRegionParamName:
            raise ValueError('Cannot add zone with region number into a model where regionParamName is not specified')
        if self.debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: Call addNewZone')
            print('Debug output: From addNewZone: (ZoneNumber, regionNumber)=({},{})'.format(zoneNumber, regionNumber))
        key = (zoneNumber, regionNumber)
        if key not in self.__zoneModelTable:
            self.__zoneModelTable[key] = zoneObject
        else:
            raise ValueError(
                'Can not add zone with (zoneNumber,regionNumber)=({},{})to the APSModel\n'
                'A zone with this zone and region number already exist.'
                ''.format(zoneNumber, regionNumber)
            )

    def deleteZone(self, zoneNumber, regionNumber=0):
        key = (zoneNumber, regionNumber)
        if self.debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: Call deleteZone')
            print('Debug output: From deleteZone: (ZoneNumber, regionNumber)=({},{})'.format(zoneNumber, regionNumber))

        if key in self.__zoneModelTable:
            del self.__zoneModelTable[key]

        # Check if the zone number, region number pair is in the selected list
        if key in self.__selectedZoneAndRegionNumberTable:
            del self.__selectedZoneAndRegionNumberTable[key]

    # Set facies table to refer to the input facies table object
    def setMainFaciesTable(self, faciesTableObj):
        self.__faciesTable = faciesTableObj

    def XMLAddElement(self, root, fmu_attributes):
        """
        Add a command specifying which zone to use in for preview
        :param root:
        :type root:
        :return:
        :rtype:
        """
        # TODO: This is temporary solution
        if self.debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: call XMLADDElement from ' + self.__class_name)

        if self.__previewZone > 0:
            tag = 'Preview'
            attribute = {
                'zoneNumber': str(self.__previewZone),
                'regionNumber': str(self.__previewRegion),
                'crossSectionType': str(self.preview_cross_section_type.name),
                'crossSectionRelativePos': str(self.preview_cross_section_relative_position),
                'scale': str(self.__previewScale),
                'resolution': str(self.__previewResolution)
            }
            elem = ET.Element(tag, attribute)
            root.append(elem)

        # If selected zone list is defined (has elements) write them to a keyword
        selectedZoneNumberList = self.getSelectedZoneNumberList()
        if len(selectedZoneNumberList) > 0:
            sortedSelectedZoneAndRegionNumberTable = collections.OrderedDict(sorted(self.__selectedZoneAndRegionNumberTable.items()))
            tag = 'SelectedZonesAndRegions'
            elemSelectedZoneAndRegion = ET.Element(tag)
            root.append(elemSelectedZoneAndRegion)
            for key, selected in sortedSelectedZoneAndRegionNumberTable.items():
                zNumber = key[0]
                rNumber = key[1]
                tag = 'SelectedZoneWithRegions'
                attributes = {'zone': str(zNumber)}
                text = ''
                elemZoneRegion = ET.Element(tag, attributes)

                rList = self.getSelectedRegionNumberListForSpecifiedZoneNumber(zNumber)
                text = ''
                useRegion = True
                if len(rList) == 1 and rList[0] == 0:
                    useRegion = False
                    text += ' ' + str(0) + ' '
                if useRegion:
                    for j in range(len(rList)):
                        rNumber = rList[j]
                        text += ' ' + str(rNumber) + ' '
                elemZoneRegion.text = text
                elemSelectedZoneAndRegion.append(elemZoneRegion)

        # Add all main commands to the root APSModel
        tags = [
            ('RMSProjectName', self.__rmsProjectName),
            ('RMSWorkflowName', self.__rmsWorkflowName),
            ('GridModelName', self.__rmsGridModelName),
            ('ZoneParamName', self.__rmsZoneParamName),
            ('RegionParamName', self.__rmsRegionParamName),
            ('ResultFaciesParamName', self.__rmsFaciesParamName),
            ('PrintInfo', str(self.debug_level.value)),
            ('SeedFile', self.seed_file_name),
            ('WriteSeeds', 'yes' if self.write_seeds else 'no'),
        ]

        for tag, value in tags:
            if value:
                elem = ET.Element(tag)
                elem.text = ' ' + value.strip() + ' '
                root.append(elem)

        # Add command MainFaciesTable
        self.__faciesTable.XMLAddElement(root)

        # Add command ZoneModels
        tag = 'ZoneModels'
        zoneListElement = ET.Element(tag)

        for key, zoneModel in self.sorted_zone_models.items():
            # Add command Zone
            zoneModel.XMLAddElement(zoneListElement, fmu_attributes)
        root.append(zoneListElement)
        rootReformatted = prettify(root)
        return rootReformatted

    def dump(self, name, attributes_file_name=None, debug_level=Debug.OFF):
        """Writes the representation of this APS model to a model file"""
        self.writeModel(name, attributes_file_name, debug_level)

    def writeModel(self, modelFileName, attributesFileName=None, debug_level=Debug.OFF):
        fmu_attributes = list()
        top = ET.Element('APSModel', {'version': self.__aps_model_version})
        root_updated = self.XMLAddElement(top, fmu_attributes)
        with open(modelFileName, 'w') as file:
            file.write(root_updated)
        if debug_level >= Debug.VERY_VERBOSE:
            print('Write file: ' + modelFileName)
        if attributesFileName is not None:
            with open(attributesFileName, 'w') as attributes_file:
                for fmu_attribute in fmu_attributes:
                    attributes_file.write("%s\n" % fmu_attribute)
                if debug_level >= Debug.VERY_VERBOSE:
                    print('Write file: ' + attributesFileName)

    @staticmethod
    def writeModelFromXMLRoot(inputETree, outputModelFileName):
        print('Write file: ' + outputModelFileName)
        root = inputETree.getroot()
        rootReformatted = minify(root)
        with open(outputModelFileName, 'w', encoding='utf-8') as file:
            file.write(rootReformatted)
            file.write('\n')


ApsModel = APSModel
