#!/bin/env python
# -*- coding: utf-8 -*-
import collections
import copy
import xml.etree.ElementTree as ET
from typing import List, Optional, Tuple, Union, Dict, TYPE_CHECKING
from warnings import warn

from aps.algorithms.APSMainFaciesTable import APSMainFaciesTable
from aps.algorithms.APSZoneModel import APSZoneModel
from aps.algorithms.properties import CrossSection
from aps.utils.constants.simple import Debug, TransformType, CrossSectionType, GridModelConstants, ExtrapolationMethod, ProbabilityTolerances
from aps.utils.exceptions.xml import MissingAttributeInKeyword
from aps.utils.containers import FmuAttribute
from aps.utils.numeric import isNumber
from aps.utils.types import FilePath
from aps.utils.xmlUtils import getKeyword, getTextCommand, prettify, minify, get_region_number, create_node
from aps.utils.io import GlobalVariables, write_string_to_file
from aps.utils.roxar.grid_model import check_active_cells_in_zone_region, create_zone_parameter

if TYPE_CHECKING:
    from roxar import Project


class APSModel:
    """
    Class APSModel  - contains the data structure for data read from model file

    Class member variables:

    Public member functions:
      def __init__(.....)

      def createSimGaussFieldIPL()
                - Write IPL file to simulate gaussian fields

      def XMLAddElement(self,root)
                - Add data to xml tree

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
       def grid_model_name(self)
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
       def getAllProbParam(self)

      Set data and update data structure:

       def setRmsWorkflowName(self,name)
       def setRmsGridModelName(self,name)
       def setRmsZoneParamName(self,name)
       def setRmsResultFaciesParamName(self,name)
       def setSelectedZoneAndRegionNumber(self, zone_number,region_number=0)
       def setPreviewZoneAndRegionNumber(self, zoneNumber,regionNumber=0)
       def addNewZone(self,zoneObject)
       def deleteZone(self,zoneNumber)
       def setMainFaciesTable(self,faciesTableObj)


    Private member functions:
     def __checkZoneModels(self)
                 - Check that an APSModel does not have specifications of zone models for (zone,region) pairs that are overlapping.
                   Hence, it is not allowed to specify (zone=1, region=0) and (zone=1, region=0).
                   The first (zone=1, region=0) means that the zone  model specification is defined for all grid cells in zone=1.
                   The second (zone=1, region=1) means that the zone model is defined for those grid cells belonging to zone=1
                   and at the same time to region=1. It follows that all grid cells belonging to zone=1 and region=1
                   have two different models which is not unique and not allowed.

    -----------------------------------------------------------------------------
    """

    def __init__(
            self,
            model_file_name: Optional[str] = None,
            aps_model_version: str = '1.1',
            rms_project_name: Optional[str] = None,
            rms_workflow_name: Optional[str] = None,
            rms_grid_model_name: Optional[str] = None,
            rms_zone_parameter_name: Optional[str] = None,
            rms_region_parameter_name: Optional[str] = None,
            rms_facies_parameter_name: Optional[str] = None,
            seed_file_name: str = 'seed.dat',
            write_seeds: bool = True,
            main_facies_table: Optional[APSMainFaciesTable] = None,
            zone_model_table: Optional[APSZoneModel] = None,
            preview_zone: int = 0,
            preview_region: int = 0,
            preview_cross_section_type: CrossSectionType = CrossSectionType.IJ,
            preview_cross_section_relative_pos: float = 0.5,
            preview_scale: float = 1.0,
            preview_resolution: str = 'Normal',
            debug_level: Optional[Debug] = Debug.OFF,
            log_setting: Debug = Debug.OFF,
            fmu_mode: str  = 'OFF',
            fmu_ertbox_name: str = 'ERTBOX',
            fmu_exchange_mode: str  = 'AUTO',
            fmu_file_format: str  = 'roff',
            fmu_trend_param_extrapolation: int = ExtrapolationMethod.EXTEND_LAYER_MEAN,
            fmu_export_config_files: bool = False,
            prob_settings_fraction: float = ProbabilityTolerances.MAX_ALLOWED_FRACTION_OF_VALUES_OUTSIDE_TOLERANCE,
            prob_settings_tolerance: float = ProbabilityTolerances.MAX_ALLOWED_DEVIATION_BEFORE_ERROR,
            transform_type: TransformType = TransformType.EMPIRIC,


    ):
        """
         The following parameters are necessary to define a model:
         If a model is created from a model file, the only necessary input is model_file_name

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
         debug_level - Define amount of output to the screen during runs
         transform_type - Define whether Empiric transformation based on GRF (with trend) values within the (zone,region)
                          is used or the cumulative normal distribution is to be used to transform GRF
                          to a uniform distribution (alpha field)
         Job settings parameters - Common settings for the APS model.

        """
        # Local variables
        if debug_level is None:
            debug_level = Debug.OFF

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
        self.__log_setting = log_setting

        # Job settings for APS GUI
        self.__fmu_mode = fmu_mode
        self.__fmu_ertbox_name = fmu_ertbox_name
        self.__fmu_exchange_mode = fmu_exchange_mode
        self.__fmu_file_format = fmu_file_format
        self.__fmu_trend_param_extrapolation = fmu_trend_param_extrapolation
        self.__fmu_export_config_files = fmu_export_config_files
        self.__prob_settings_fraction = prob_settings_fraction
        self.__prob_settings_tolerance = prob_settings_tolerance
        self.__transform_type = transform_type


        # Read model if it is defined
        if model_file_name is not None:
            self.__parse_model_file(model_file_name, debug_level=debug_level)

    @property
    def use_constant_probability(self) -> bool:
        return all(model.use_constant_probabilities for model in self.__zoneModelTable.values())

    def __parse_model_file(self, model_file_name: FilePath, debug_level: Debug = Debug.OFF) -> None:
        """ Read xml file and put the data into data structure """
        root = ET.parse(model_file_name).getroot()
        self.__interpretTree(root, debug_level, model_file_name)

    @classmethod
    def from_string(cls, xml_content: str, debug_level: Debug = Debug.OFF) -> 'APSModel':
        root = ET.fromstring(xml_content)
        model = cls()
        model.__interpretTree(root, debug_level)
        return model

    def __interpretTree(
            self,
            root: ET.Element,
            debug_level_input: Debug = Debug.OFF,
            model_file_name: Optional[str] = None,
    ) -> None:
        self.__ET_Tree = ET.ElementTree(root)
        if root.tag != 'APSModel':
            raise ValueError('The root element must be APSModel')
        apsmodel_version_input = root.get('version')
        if apsmodel_version_input is None:
            raise ValueError('attribute version is not defined in root element')
        elif apsmodel_version_input not in ["1.0", "1.1"]:
            raise ValueError(
                f'Illegal value ( {apsmodel_version_input} ) specified for apsmodelversion (only 1.0 and 1.1 is supported)'
            )
        self.__aps_model_version_from_file = apsmodel_version_input

        # Debug level used when reading model file
        self.debug_level = debug_level_input

        if self.__aps_model_version_from_file == "1.0" and self.debug_level >= Debug.VERBOSE:
            print(
                "NOTE: The model file that is imported has file format version 1.0.\n"
                "This format is used for APSGUI versions less than 1.4\n"
                "When importing model file using file format 1.0, the 'Job Settings' is not \n"
                "part of the data saved in the model file. Therefore the user must \n"
                "go into the 'Job Settings panel' and specify the 'Job settings' again after\n"
                "the model file is imported."
            )

        if self.debug_level >= Debug.VERBOSE:
            print(f"-- Read APS model file with version: {self.__aps_model_version_from_file}")

        if self.debug_level >= Debug.VERY_VERBOSE:
            print('')
            print('------------ Start reading model file in APSModel ------------------')
            print('')

        if self.__aps_model_version_from_file == "1.1":
            # Read Job settings
            self.read_job_settings(root, model_file_name)
            if self.debug_level >= Debug.VERY_VERBOSE:
                self.print_job_settings()

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
            try:
                self.__preview_cross_section.type = CrossSectionType[text.strip()]
            except KeyError:
                raise ValueError('Wrong specification of preview cross section')

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
                if self.__previewResolution not in ["Normal", "High"]:
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
            value = getTextCommand(root, keyword, parentKeyword='APSModel', modelFile=model_file_name,
                                   required=required)
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
            modelFile=model_file_name,
            required=len(zones_with_region_attr) > 0
        )
        if value is not None:
            self.__rmsRegionParamName = value

        if self.__aps_model_version_from_file == "1.0":
            # --- PrintInfo ---
            # Debug level is specified in the APSModel constructor.
            # The only case when debug level specified in model file is used, is
            # when debug level is set to Debug.READ. In that case the model file
            # keyword setting in 'PrintInfo' is used.
            if debug_level_input == Debug.READ:
                kw = 'PrintInfo'
                obj = root.find(kw)
                if obj is not None:
                    self.debug_level = obj.text
                else:
                    self.debug_level = Debug.OFF
            else:
                self.debug_level = debug_level_input

            # Read optional keyword to specify name of seed file
            keyword = 'SeedFile'
            value = getTextCommand(root, keyword, parentKeyword='APSModel', defaultText='seed.dat',
                    modelFile=model_file_name, required=False)
            self.__seed_file_name = value

            # Read optional keyword to specify the boolean variable write_seeds
            keyword = 'WriteSeeds'
            value = getTextCommand(root, keyword, parentKeyword='APSModel', defaultText='yes', modelFile=model_file_name,
                    required=False)
            self.write_seeds = True if value.upper() == 'YES' else False

            # Read optional keyword to specify which transformation to use for Gaussian Fields
            keyword = 'TransformationType'
            text = getTextCommand(root, keyword, parentKeyword='APSModel', defaultText='Empiric', modelFile=model_file_name,
                    required=False)
            if text.upper() == 'EMPIRIC' or text.upper() == '0':
                self.__transform_type = TransformType.EMPIRIC
            elif text.upper() == 'CDF' or text.upper() == '1':
                self.__transform_type = TransformType.CUMNORM
            else:
                raise ValueError(
                    f'Illegal value ( {text} ) specified for keyword {keyword}.\n'
                    'Legal values are either  Empiric (or alternatively 0)  or CDF (or alternatively 1)'
                )

        # Read all facies names available
        self.__faciesTable = APSMainFaciesTable(ET_Tree=self.__ET_Tree, modelFileName=model_file_name)

        if self.__debug_level >= Debug.VERY_VERBOSE:
            print(
                f'--- RMSGridModel:                       {self.__rmsGridModelName}\n'
                f'--- RMSZoneParamName:                   {self.__rmsZoneParamName}\n'
                f'--- RMSFaciesParamName:                 {self.__rmsFaciesParamName}\n'
                f'--- RMSRegionParamName:                 {self.__rmsRegionParamName}\n'
                f'--- Name of RMS project read:           {self.__rmsProjectName}\n'
                f'--- Name of RMS workflow read:          {self.__rmsWorkflowName}'
            )


        # Read all zones for models specifying main level facies
        # --- ZoneModels ---
        zModels = root.find('ZoneModels')
        if zModels is None:
            raise IOError(
                f'Error when reading model file: {model_file_name}\n'
                'Error: Missing keyword ZoneModels'
            )

        # --- Zone ---
        if self.__debug_level >= Debug.VERY_VERBOSE:
            print(f"\n--- Number of specified zone models: {len(zModels.findall('Zone'))}\n")

        for zone in zModels.findall('Zone'):
            if zone is None:
                raise IOError(
                    f'Error when reading model file: {model_file_name}\n'
                    'Error: Missing keyword Zone in keyword ZoneModels'
                )
            zone_number = int(zone.get('number'))
            if zone_number <= 0:
                raise ValueError(
                    'Zone number must be a positive integer. '
                    f'Can not have zone number: {zone_number}'
                )
            region_number = get_region_number(zone)

            # The model is identified by the combination (zoneNumber, regionNumber)
            zoneModelKey = (zone_number, region_number)
            if zoneModelKey not in self.__zoneModelTable:

                if self.__debug_level >= Debug.VERY_VERBOSE:
                    print('')
                    print('')
                    if region_number <= 0:
                        print(f'--- Read zone model for zone number: {zone_number}')
                    else:
                        print(
                            f'--- Read zone model for (zone, region) number: '
                            f'({zone_number}, {region_number})'
                        )

                zone_model = APSZoneModel(
                    ET_Tree=self.__ET_Tree,
                    zoneNumber=zone_number,
                    regionNumber=region_number,
                    modelFileName=model_file_name,
                    debug_level=self.__debug_level 
                )
                # This zoneNumber, regionNumber combination is not defined previously
                # and must be added to the dictionary
                self.__zoneModelTable[zoneModelKey] = zone_model
            else:
                raise ValueError(
                    'Can not have two or more entries of keyword Zone with the same zoneNumber and regionNumber.\n'
                    f'Can not have multiple specification of '
                    f'(zoneNumber, regionNumber) = ({zone_number}, {region_number})'
                )

        # --- SelectedZones ---
        kw = 'SelectedZonesAndRegions'
        obj = getKeyword(root, kw, modelFile=model_file_name, required=False)
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
                    zone_model = self.getZoneModel(zone_number=zone_number, region_number=region_number)
                    if zone_model is None:
                        raise ValueError(
                            f'Can not select to use zone model with zone number: {zone_number} '
                            f'and region number: {region_number} '
                            'This zone model is not defined'
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
                            zone_model = self.getZoneModel(zone_number=zone_number, region_number=region_number)
                            if zone_model is None:
                                raise ValueError(
                                    'Can not select to use zone model with '
                                    f'zone number: {zone_number} and region number: {region_number} '
                                    'This zone model is not defined'
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

        if self.__debug_level >= Debug.VERY_VERBOSE:
            print('--- Zone models are defined for the following combination '
                  'of zone and region numbers:')
            for key, value in self.sorted_zone_models.items():
                zone_number = key[0]
                region_number = key[1]
                if region_number == 0:
                    print(f'    Zone: {zone_number}')
                else:
                    print(f'    Zone: {zone_number}  Region: {region_number}')
            print('\n------------ End reading model file in APSModel ------------------\n')

    def update_model_file(
            self,
            model_file_name: Optional[FilePath] = None,
            parameter_file_name: Optional[FilePath] = None,
            project: 'Optional[Project]' = None,
            workflow_name: Optional[str] = None,
            uncertainty_variable_names: Optional[List[str]] = None,
            realisation_number: int = 0,
            debug_level: Debug = Debug.OFF,
            current_job_name: Optional[str] = None,
            use_rms_uncertainty_table: bool = False,
    ) -> ET.ElementTree:
        """
        Read xml model file and IPL parameter file and write updated xml model file
        without putting any data into the data structure.
        """
        # Read XML model file
        tree = ET.parse(model_file_name)
        root = tree.getroot()

        # Scan XML model file for variables that can be updated by FMU/ERT
        # These variables belongs to xml keywords with attribute 'kw'.
        # So search for attribute 'kw' to find all these variables. The attribute value is a keyword
        # name that will be used as identifier.
        if debug_level >= Debug.VERY_VERBOSE:
            print('')
            print(f'--- Model parameters marked as possible to update in model file {model_file_name}')
            print('Keyword:                                           Value:')
        keywords_defined_for_updating = []
        for obj in root.findall(".//*[@kw]"):
            key_word = obj.get('kw')
            value = obj.text
            keywords_defined_for_updating.append([key_word.strip(), value.strip()])
            if debug_level >= Debug.VERY_VERBOSE:
                print('{0:30} {1:10}'.format(key_word, value))

        # Read keywords from parameter_file_name (global_variables.yml with variables updated by FMU/ERT)
        keywords_read = None
        if not use_rms_uncertainty_table:
            if parameter_file_name is not None:
                # keywords_read is a list of items where each item is [name, value]
                keywords_read = self.__parse_global_variables(model_file_name,
                                                              parameter_file_name,
                                                              current_job_name,
                                                              debug_level)

                if current_job_name is None:
                    print(f'NOTE: The APS parameters are not updated when running interactively')
                else:
                    if len(keywords_defined_for_updating) > 0:
                        if keywords_read is None:
                            print(' ')
                            text = '\nWARNING:\n'
                            text += f'-- The APS parameters selected to be updated by FMU in APS job: {current_job_name}\n'
                            text += f'   will not be updated since no APS parameters are specified in \n'
                            text += f'   {parameter_file_name} for the current job.\n'
                            text += f'   Ensure that APS parameters to be updated are specified both in \n'
                            text += f'   the APS job and the FMU global_variables file.\n'
                            warn(text)
                            print(' ')
                    else:
                        if keywords_read is not None:
                            print(' ')
                            text = '\nWARNING:\n'
                            text += f'-- No APS parameters are selected to be updated by FMU in APS job: {current_job_name}\n'
                            text += f'   There are defined APS parameters for this APS job in: {parameter_file_name}\n'
                            text += f'   Ensure that APS parameters to be updated are specified both in \n'
                            text += f'   the APS job and the FMU global_variables file.\n'
                            warn(text)
                            print(' ')

                if debug_level >= Debug.VERY_VERBOSE:
                    if keywords_read is not None:
                        print(' ')
                        print(f'-- Keyword read from {parameter_file_name}:')
                        for item in keywords_read:
                            name = item[0]
                            value = item[1]
                            print(f' {name}     {value}')
        else:
            assert project
            assert workflow_name
            assert uncertainty_variable_names
            keywords_read = self.__getParamFromRMSTable(
                project, workflow_name, uncertainty_variable_names, realisation_number,
            )

        # Set new values if keyword in global_variables file and in fmu tag in model file match
        if (len(keywords_defined_for_updating) > 0) and (keywords_read != None):
            # Update the list of keywords in the model file with new values from FMU global_variables
            found_an_update = False
            for item in keywords_defined_for_updating:
                keyword = item[0]
                for item_from_fmu in keywords_read:
                    kw, value = item_from_fmu
                    if kw == keyword:
                        # update the keywords_defined_for_updating list
                        found_an_update = True
                        item[1] = value
                        break

            if found_an_update:
                print(f'The APS parameters are updated for the job: {current_job_name}')
                if debug_level >= Debug.VERBOSE:
                    print(f'   Parameter name                                   Original value   New value')
            else:
                # Should never occur
                raise ValueError(
                    f"Internal error: APS parameters selected to be updated by FMU "
                    f"does not match parameters specified in {parameter_file_name}"
                )

            # Update the model file fmu tags with updated values
            for obj in root.findall(".//*[@kw]"):
                key_word_from_model = obj.get('kw')
                old_value = obj.text

                found = False
                for kw, val in keywords_defined_for_updating:
                    if kw == key_word_from_model:
                        # Found the correct item in the list and correct value to use
                        for item_from_fmu in keywords_read:
                            kw_from_fmu, value = item_from_fmu
                            if kw == kw_from_fmu:
                                # Found the keyword also in the FMU parameter list from global_variables

                                # Update value in XML tree for this keyword
                                if isinstance(val, str):
                                    val = val.strip()
                                obj.text = str(val)
                                found = True
                                break
                        if found:
                            break
                if found:
                    if debug_level >= Debug.VERBOSE:
                        print(f'   {key_word_from_model:42}    {old_value:12}  {obj.text:12}')

        return tree

    def __checkZoneModels(self) -> None:
        """
        Description: Run through all zone models and check that:
           If a zone model is specified with region number 0, it is not allowed to specify zone models for the same
           zone which is individual for regions > 0 as well. The reason is that a zone model with region 0 (which means not using regions)
           and zone models for the same zone but specified for individual regions will change facies code in a set of cells in the grid that
           is common and hence "overwrite" each other.
        """
        zoneNumbers = []
        for key, _ in self.__zoneModelTable.items():
            zone_number, region_number = key
            if zone_number in zoneNumbers and region_number == 0:
                raise ValueError(f'There exists more than one zone model for zone: {zone_number}')
            else:
                # This is a model for a new region for an existing zone number that has several regions
                zoneNumbers.append(zone_number)

    def __parse_global_variables(
            self,
            model_file_name: str,
            global_variables_file: FilePath,
            current_job_name: Optional[str] = None,
            debug_level: Debug = Debug.OFF,
    ) -> List[Tuple[str, Union[str, float]]]:
        """ Read the global variables file (IPL, or YAML) to get updated model parameters from FMU """
        # Search through the file line for line and skip lines commented out with '//'
        # Collect all variables that are assigned value as the three first words on a line
        # like e.g VARIABLE_NAME = 10
        keywords = []
        if GlobalVariables.check_file_format(global_variables_file) == 'ipl':
            keywords = GlobalVariables.parse(global_variables_file)
            if debug_level >= Debug.ON:
                print(f'- Keywords and values found in parameter file:  {global_variables_file}')
                for item in keywords:
                    kw, val = item
                    print(f'  {kw:30} {val:20}')
                print('')
        else:
            # YAML file with more general possibility for parameter specification
            aps_dict = GlobalVariables.parse(global_variables_file)

            # Find the model parameters for the current aps job
            try:
                param_dict = aps_dict[current_job_name]
                for key, value in param_dict.items():
                    item = [key, value]
                    keywords.append(item)
                return keywords

            except:
                # No parameter specified to be updated for the current APS job
                return None

        # End read file
        return keywords

    # ----- Properties ----
    @property
    def debug_level(self) -> Debug:
        return self.__debug_level

    @property
    def log_setting(self) -> Debug:
        return self.__log_setting

    @debug_level.setter
    def debug_level(self, debug_level_input):
        if isinstance(debug_level_input, str):
            debug_level_input = int(debug_level_input.strip())
        if isinstance(debug_level_input, int):
            debug_level_input = Debug(debug_level_input)
        if debug_level_input not in Debug:
            debug_level_input = Debug.OFF
        self.__debug_level = debug_level_input

    @property
    def seed_file_name(self) -> str:
        return self.__seed_file_name

    @seed_file_name.setter
    def seed_file_name(self, name):
        self.__seed_file_name = copy.copy(name)

    @property
    def preview_scale(self) -> float:
        return self.__previewScale

    @preview_scale.setter
    def preview_scale(self, scale: float):
        if not (scale > 0.0):
            raise ValueError(
                'Error in {} in setPreviewScale\n'
                'Error:  Scale factor must be > 0'
            )
        else:
            self.__previewScale = scale

    @property
    def preview_resolution(self) -> str:
        return self.__previewResolution

    @property
    def preview_cross_section(self) -> CrossSection:
        return self.__preview_cross_section

    @property
    def preview_cross_section_type(self) -> CrossSectionType:
        return self.__preview_cross_section.type

    @preview_cross_section_type.setter
    def preview_cross_section_type(self, type):
        if isinstance(type, CrossSectionType):
            self.__preview_cross_section.type = type
        else:
            try:
                self.__preview_cross_section.type = CrossSectionType[type]
            except KeyError:
                raise ValueError(
                    'Error in preview_cross_section_type\n'
                    'Error:  Cross section is not IJ, IK or JK.'
                )

    @property
    def preview_cross_section_relative_position(self) -> float:
        return self.__preview_cross_section.relative_position

    @preview_cross_section_relative_position.setter
    def preview_cross_section_relative_position(self, relative_position):
        self.__preview_cross_section.relative_position = relative_position

    @staticmethod
    def __getParamFromRMSTable(
            project: 'Project',
            workflow_name: str,
            uncertainty_variable_names,
            realisation_number: int,
    ) -> List[Tuple[str, str]]:
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
            item = (name, value)
            parametersUncertainty.append(item)
        return parametersUncertainty

    #  ---- Get functions -----
    def getXmlTree(self):
        return self.__ET_Tree

    def getRoot(self):
        tree = self.getXmlTree()
        return tree.getroot()

    def isAllZoneRegionModelsSelected(self):
        return self.__selectAllZonesAndRegions

    # Get pointer to zone model object

    def getSelectedZoneNumberList(self) -> List[int]:
        selectedZoneNumberList = []
        keyList = list(self.__selectedZoneAndRegionNumberTable.keys())
        for item in keyList:
            zNumber = item[0]
            if zNumber not in selectedZoneNumberList:
                selectedZoneNumberList.append(zNumber)
        return copy.copy(selectedZoneNumberList)

    def getSelectedRegionNumberListForSpecifiedZoneNumber(self, zoneNumber: int) -> List[int]:
        selectedRegionNumberList = []
        keyList = sorted(list(self.__selectedZoneAndRegionNumberTable.keys()))
        for item in keyList:
            zNumber, rNumber = item
            if zNumber == zoneNumber and rNumber not in selectedRegionNumberList:
                selectedRegionNumberList.append(rNumber)
        return selectedRegionNumberList

    def isSelected(self, zone_number: int, region_number: int) -> bool:
        if self.isAllZoneRegionModelsSelected():
            return True
        key = (zone_number, region_number)
        return key in self.__selectedZoneAndRegionNumberTable

    def getZoneModel(self, zone_number: int, region_number: int = 0) -> APSZoneModel:
        key = (zone_number, region_number)
        try:
            return self.__zoneModelTable[key]
        except KeyError:
            return None

    def getAllZoneModels(self):
        return self.__zoneModelTable

    @property
    def sorted_zone_models(self) -> Dict[Tuple[int, int], APSZoneModel]:
        # Define sorted sequence of the zone models
        return collections.OrderedDict(sorted(self.__zoneModelTable.items()))

    @property
    def zone_models(self) -> List[APSZoneModel]:
        return self.sorted_zone_models.values()

    @property
    def grid_model_name(self) -> str:
        return self.__rmsGridModelName

    @grid_model_name.setter
    def grid_model_name(self, name):
        self.__rmsGridModelName = name

    def getResultFaciesParamName(self):
        return copy.copy(self.__rmsFaciesParamName)

    def getZoneNumberList(self) -> List[int]:
        zoneNumberList = []
        keyList = list(self.__zoneModelTable.keys())
        for item in keyList:
            zNumber = item[0]
            if zNumber not in zoneNumberList:
                zoneNumberList.append(zNumber)
        return zoneNumberList

    def getRegionNumberListForSpecifiedZoneNumber(self, zoneNumber: int) -> List[int]:
        regionNumberList = []
        keyList = list(self.__zoneModelTable.keys())
        for zNumber, rNumber in keyList:
            if zNumber == zoneNumber and rNumber not in regionNumberList:
                regionNumberList.append(rNumber)
        return regionNumberList

    def getPreviewZoneNumber(self) -> int:
        return self.__previewZone

    def getPreviewRegionNumber(self) -> int:
        return self.__previewRegion

    @property
    def gaussian_field_names(self) -> List[str]:
        return self.getAllGaussFieldNamesUsed()

    def getAllGaussFieldNamesUsed(self) -> List[str]:
        gfAllZones = []
        for key, zoneModel in self.__zoneModelTable.items():
            if self.__debug_level >= Debug.ON:
                region_number = key[1]
                zone_number = key[0]
                if region_number == 0:
                    print(f'- Gaussian field names used for zone {zone_number}:')
                else:
                    print(f'- Gaussian field names used for zone {zone_number} and region {region_number}:')
            gfNames = zoneModel.used_gaussian_field_names
            for gf in gfNames:
                # Add the gauss field name to the list if it not already is in the list
                if self.__debug_level >= Debug.ON:
                    print(f'   Gauss field name: {gf}')
                if gf not in gfAllZones:
                    gfAllZones.append(gf)
        return copy.copy(gfAllZones)

    @property
    def zone_parameter(self) -> str:
        return self.getZoneParamName()

    @property
    def region_parameter(self) -> str:
        return self.getRegionParamName()

    @property
    def use_regions(self) -> bool:
        return bool(self.region_parameter)

    @property
    def rms_project_name(self) -> Optional[str]:
        return self.__rmsProjectName

    @rms_project_name.setter
    def rms_project_name(self, name):
        self.__rmsProjectName = name

    def getZoneParamName(self) -> str:
        return self.__rmsZoneParamName

    def getRegionParamName(self) -> str:
        if self.__rmsRegionParamName:
            return self.__rmsRegionParamName
        else:
            return ''

    def getMainFaciesTable(self) -> APSMainFaciesTable:
        return self.__faciesTable

    def getRMSWorkflowName(self):
        return copy.copy(self.__rmsWorkflowName)

    def getAllProbParam(self):
        all_probabilities = []
        for _, zoneModel in self.__zoneModelTable.items():
            probability_parameters = zoneModel.getAllProbParamForZone()
            for name in probability_parameters:
                if name not in all_probabilities:
                    all_probabilities.append(name)
        return all_probabilities

    @property
    def transform_type(self) -> TransformType:
        return self.__transform_type

    @transform_type.setter
    def transform_type(self, name: Union[str, int]):
        if isinstance(name, str):
            if name.strip() == 'EMPIRIC' or name.strip() == 'Empiric':
                transf_number = TransformType.EMPIRIC
            elif name.strip() == 'CDF' or name.strip() == 'cdf':
                transf_number = TransformType.CUMNORM
        if isinstance(name, int):
            transf_number = TransformType(name)
        if name not in TransformType:
            transf_number = TransformType.EMPIRIC
        self.__transform_type = transf_number

    # ----- Set functions -----
    def setRmsWorkflowName(self, name: str) -> None:
        self.__rmsWorkflowName = name

    def setRmsGridModelName(self, name: str) -> None:
        self.__rmsGridModelName = name

    def setRmsZoneParamName(self, name: str) -> None:
        self.__rmsZoneParamName = name

    def setRmsRegionParamName(self, name: str) -> None:
        if not name:
            for key, _ in self.__zoneModelTable.items():
                region_number = key[1]
                current_zone_has_at_least_one_region = region_number > 0
                if current_zone_has_at_least_one_region:
                    raise ValueError(
                        'RegionParamName must be given when there is at least one zone in the model with region Number)'
                    )
        self.__rmsRegionParamName = copy.copy(name)

    def setRmsResultFaciesParamName(self, name: str) -> None:
        self.__rmsFaciesParamName = copy.copy(name)

    def setSelectedZoneAndRegionNumber(self, zone_number: int, region_number: int = 0) -> None:
        """
        Description: Select a new pair of (zoneNumber, regionNumber) which has not been already selected.
        """
        # Check that the specified pair (zone_number, region_number) is an existing zone model
        key = (zone_number, region_number)
        if key in self.__zoneModelTable:
            if key not in self.__selectedZoneAndRegionNumberTable:
                self.__selectedZoneAndRegionNumberTable[key] = 1
        else:
            raise ValueError(
                f'Can not select (zoneNumber, regionNumber) = ({zone_number}, {region_number}) '
                'since the zone model does not exist'
            )

    def deSelectedZoneAndRegionNumber(self, zone_number: int, region_number: int = 0) -> None:
        """
        Description: Remove selection a pair of (zone_number, region_number).
        """
        # De-select a specified pair (zone_number, region_number)
        input_key = (zone_number, region_number)
        if input_key in self.__zoneModelTable:
            if self.__selectAllZonesAndRegions:
                self.__selectAllZonesAndRegions = False
                for key,_ in self.__zoneModelTable.items():
                    self.__selectedZoneAndRegionNumberTable[key] = 1
            if input_key in self.__selectedZoneAndRegionNumberTable:
                del self.__selectedZoneAndRegionNumberTable[input_key]
        else:
            raise ValueError(
                f'Can not select (zoneNumber, regionNumber) = ({zone_number}, {region_number}) '
                'since the zone model does not exist'
            )


    def setPreviewZoneAndRegionNumber(self, zone_number: int, region_number: int = 0) -> None:
        key = (zone_number, region_number)
        if key in self.__zoneModelTable:
            self.__previewZoneNumber = zone_number
            self.__previewRegionNumber = region_number
        else:
            raise ValueError(
                f'Error in {self.__class_name} in setPreviewZoneNumber\n'
                f'Error:  (zoneNumber, regionNumber) = ({zone_number}, {region_number}) is not defined in the model'
            )

    def addNewZone(self, zoneObject: APSZoneModel) -> None:
        zone_number = zoneObject.zone_number
        region_number = zoneObject.region_number
        if region_number > 0 and not self.__rmsRegionParamName:
            raise ValueError('Cannot add zone with region number into a model where regionParamName is not specified')
        if self.debug_level >= Debug.VERY_VERBOSE:
            print('--- Call addNewZone')
            print(f'--- From addNewZone: (Zone number, Region number)=({zone_number}, {region_number})')
        key = (zone_number, region_number)
        if key not in self.__zoneModelTable:
            self.__zoneModelTable[key] = zoneObject
        else:
            raise ValueError(
                f'Can not add zone with (Zone number, Region number)=({zone_number}, {region_number})to the APSModel\n'
                'A zone with this zone and region number already exist.'
            )

    def deleteZone(self, zone_number: int, region_number: int = 0) -> None:
        key = (zone_number, region_number)
        if self.debug_level >= Debug.VERY_VERBOSE:
            print('--- Call deleteZone')
            print(f'--- From deleteZone: (ZoneNumber, regionNumber)=({zone_number}, {region_number})')

        if key in self.__zoneModelTable:
            del self.__zoneModelTable[key]

        # Check if the zone number, region number pair is in the selected list
        if key in self.__selectedZoneAndRegionNumberTable:
            del self.__selectedZoneAndRegionNumberTable[key]

    # Set facies table to refer to the input facies table object
    def setMainFaciesTable(self, faciesTableObj: APSMainFaciesTable) -> None:
        self.__faciesTable = faciesTableObj

    def XMLAddElement(self, root: ET.Element, fmu_attributes: List[FmuAttribute]) -> str:
        """
        Add a command specifying which zone to use in for preview
        :param root:
        :type root:
        :return:
        :rtype:
        """
        # TODO: This is temporary solution
        if self.debug_level >= Debug.VERY_VERBOSE:
            print('--- call XMLADDElement from ' + self.__class_name)

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
        selected_zone_numbers = self.getSelectedZoneNumberList()
        if selected_zone_numbers:
            selected_zone_numbers = collections.OrderedDict(sorted(self.__selectedZoneAndRegionNumberTable.items()))
            tag = 'SelectedZonesAndRegions'
            selected_zone_and_region_element = ET.Element(tag)
            root.append(selected_zone_and_region_element)
            zone_numbers_added = [] 
            for key, _ in selected_zone_numbers.items():
                zone_number, region_number = key
                tag = 'SelectedZoneWithRegions'
                if zone_number in zone_numbers_added:
                    continue
                attributes = {'zone': str(zone_number)}
                element_zone_region = ET.Element(tag, attributes)

                regions = self.getSelectedRegionNumberListForSpecifiedZoneNumber(zone_number)
                text = ''
                use_region = True
                if len(regions) == 1 and regions[0] == 0:
                    use_region = False
                    text += ' 0 '
                if use_region:
                    for region_number in regions:
                        text += f' {region_number} '
                element_zone_region.text = text
                selected_zone_and_region_element.append(element_zone_region)
                zone_numbers_added.append(zone_number)

        # Add all main commands to the root APSModel
        # Note if APSModel is created from version 1.0, but read by reader for 1.1,
        # it will be converted to version 1.1
        tags = [
            ('RMSProjectName', self.__rmsProjectName),
            ('RMSWorkflowName', self.__rmsWorkflowName),
            ('GridModelName', self.__rmsGridModelName),
            ('ZoneParamName', self.__rmsZoneParamName),
            ('RegionParamName', self.__rmsRegionParamName),
            ('ResultFaciesParamName', self.__rmsFaciesParamName),

        ]
        for tag, value in tags:
            if value:
                elem = ET.Element(tag)
                elem.text = ' ' + value.strip() + ' '
                root.append(elem)

        if self.__aps_model_version == "1.0":
            write_seeds_text = "YES" if self.write_seeds else "NO"
            tags = [
                ('SeedFile', self.__seed_file_name),
                ('WriteSeeds', write_seeds_text),
                ('TransformationType', str(self.__transform_type.value)),
                ('PrintInfo', str(self.debug_level.value)),
            ]
            for tag, value in tags:
                if value:
                    elem = ET.Element(tag)
                    elem.text = ' ' + value.strip() + ' '
                    root.append(elem)

        elif self.__aps_model_version == "1.1":
            # Add command JobSettings
            self.job_settings_xml_add_elements(root)

        # Add command MainFaciesTable
        self.__faciesTable.XMLAddElement(root)

        # Add command ZoneModels
        tag = 'ZoneModels'
        zone_elements = ET.Element(tag)

        for key, zoneModel in self.sorted_zone_models.items():
            # Add command Zone
            zoneModel.XMLAddElement(zone_elements, fmu_attributes)
        root.append(zone_elements)
        return prettify(root)

    def dump(
            self,
            name: FilePath,
            attributes_file_name: Optional[FilePath] = None,
            probability_distribution_file_name: Optional[FilePath] = None,
            debug_level: Debug = Debug.OFF,
    ) -> None:
        """Writes the representation of this APS model to a model file"""
        self.write_model(name,
                         attributes_file_name=attributes_file_name,
                         probability_distribution_file_name=probability_distribution_file_name,
                         current_job_name=None,
                         debug_level=debug_level)

    def write_model(
            self,
            model_file_name: FilePath,
            attributes_file_name: Optional[FilePath] = None,
            probability_distribution_file_name: Optional[FilePath] = None,
            current_job_name: Optional[str] = None,
            debug_level: Debug = Debug.OFF,
    ) -> None:
        """ - Create xml tree with model specification by calling XMLAddElement
            - Write xml tree with model specification to file
        """

        fmu_attributes: List[FmuAttribute] = []
        top = ET.Element('APSModel', {'version': self.__aps_model_version})
        root_updated = self.XMLAddElement(top, fmu_attributes)
        write_string_to_file(model_file_name, root_updated, debug_level=debug_level)

        if attributes_file_name is not None:
            aps_model = APSModel(model_file_name)
            grid_model_name = aps_model.grid_model_name

            if current_job_name is None:
                current_job_name = 'apsgui_job_name'
            write_string_to_file(attributes_file_name, 
                fmu_configuration(fmu_attributes, current_job_name),
                debug_level=debug_level)

        if probability_distribution_file_name is not None:
            if current_job_name is None:
                current_job_name = 'apsgui_job_name'
            write_string_to_file(probability_distribution_file_name,
                probability_distribution_configuration(fmu_attributes, current_job_name),
                debug_level=debug_level)

    @property
    def has_fmu_updatable_values(self) -> bool:
        fmu_attributes: List[FmuAttribute] = []
        top = ET.Element('APSModel', {'version': self.__aps_model_version})
        self.XMLAddElement(top, fmu_attributes)
        return len(fmu_attributes) > 0
    @property
    def fmu_mode(self) -> str:
        return self.__fmu_mode

    @property
    def fmu_ertbox_name(self) -> str:
        return self.__fmu_ertbox_name

    @property
    def fmu_field_file_format(self) -> str:
        return self.__fmu_file_format

    def check_or_create_zone_parameter(self, project, debug_level=Debug.OFF):
        """
        Check if zone parameter exist and create it if not existing or empty
        """
        grid_model = project.grid_models[self.grid_model_name]
        realization_number = project.current_realisation
        create_zone_parameter(grid_model,
            name=GridModelConstants.ZONE_NAME,
            realization_number=realization_number,
            debug_level=debug_level
        )

    def check_active_cells(self, project, debug_level=Debug.OFF):
        """
        Check if all specified models, for all (zone_number, region_number)
        have active grid cells and remove the models for the (zone_number, region_number)
        combinations that has 0 active cells from the list of selected models.
        """
        grid_model = project.grid_models[self.grid_model_name]
        realisation_number = project.current_realisation
        all_zone_models = self.sorted_zone_models
        region_param_name = self.getRegionParamName()
        for key, _ in all_zone_models.items():
            zone_number, region_number = key
            if not self.isSelected(zone_number, region_number):
                continue
            check = check_active_cells_in_zone_region(grid_model,
                zone_number, region_number, realisation_number, 
                region_param_name, debug_level=debug_level)
            if not check:
                if debug_level >= Debug.ON:
                    print(
                        f"- Skip (zone,region) = ({zone_number} {region_number}). No active cells."
                    )
                self.deSelectedZoneAndRegionNumber(zone_number,region_number)

    @staticmethod
    def write_model_from_xml_root(
            input_tree: ET.Element, 
            output_model_file_name: FilePath,
            debug_level: Debug = Debug.OFF) -> None:
        if debug_level >= Debug.ON:
            print(f'- Write file: {output_model_file_name}')
        root = input_tree.getroot()
        root = minify(root)
        with open(output_model_file_name, 'w', encoding='utf-8') as file:
            file.write(root)
            file.write('\n')

    def read_job_settings(self, root, model_file_name):
        job_settings = getKeyword(root, 'JobSettings', modelFile=model_file_name, required=False)
        if job_settings is not None:
            fmu_settings = getKeyword(job_settings, 'FmuSettings', modelFile=model_file_name, required=False)
            run_settings = getKeyword(job_settings, 'RunSettings', modelFile=model_file_name, required=False)
            transform_settings = getKeyword(job_settings, 'TransformationSettings', modelFile=model_file_name, required=False)
            log_settings = getKeyword(job_settings, 'LogSetting', modelFile= model_file_name, required=False)
            if fmu_settings is not None:
                kw_fmu_mode = 'FmuMode'
                fmu_mode_setting = getKeyword(fmu_settings, kw_fmu_mode, modelFile=model_file_name, required=False)
                if fmu_mode_setting is not None:
                    value = fmu_mode_setting.text.strip().upper()
                    legal_values = ['OFF', 'NOFIELDS', 'FIELDS']
                    if value not in legal_values:
                        raise ValueError(
                            f"Job Setting parameter for {kw_fmu_mode} must be one of {legal_values}"
                        )
                    self.__fmu_mode = value
                if self.__fmu_mode == 'FIELDS':
                    update_grf_settings = getKeyword(fmu_settings, 'UpdateGRF', modelFile=model_file_name, required=True)
                    if update_grf_settings is not None:
                        kw_ertbox = 'ErtBoxGrid'
                        ertbox_grid_settings = getKeyword(update_grf_settings, kw_ertbox, modelFile=model_file_name, required=True)
                        value = ertbox_grid_settings.text.strip()
                        if len(value) > 0:
                            self.__fmu_ertbox_name = value
                        else:
                            raise ValueError(
                                f"Job Settings parameter for {kw_ertbox} must be a name of a grid model."
                            )
                        kw_exchange = 'ExchangeMode'
                        exchange_settings = getKeyword(update_grf_settings,  kw_exchange, modelFile=model_file_name, required=False)
                        if exchange_settings is not None:
                            value = exchange_settings.text.strip().upper()
                            legal_values = ['SIMULATE', 'AUTO']
                            if value not in legal_values:
                                raise ValueError(
                                    f"Job Setting parameter for {kw_exchange} must be one of {legal_values}"
                                )
                            self.__fmu_exchange_mode = value

                        kw_extrapolation = 'ExtrapolationMethod'
                        extrapolate_settings = getKeyword(update_grf_settings, kw_extrapolation, modelFile=model_file_name, required=False)
                        if extrapolate_settings is not None:
                            value = extrapolate_settings.text.strip()
                            legal_values =[
                                ExtrapolationMethod.ZERO.value,
                                ExtrapolationMethod.MEAN.value,
                                ExtrapolationMethod.EXTEND_LAYER_MEAN.value,
                                ExtrapolationMethod.REPEAT_LAYER_MEAN.value,
                                ExtrapolationMethod.EXTEND.value,
                                ExtrapolationMethod.REPEAT.value,
                            ]
                            if value not in legal_values:
                                raise ValueError(
                                    f"Job settings parameter for {kw_extrapolation} was set to {value} "
                                    f"but must be one of the values {legal_values} "
                                )
                            self.__fmu_trend_param_extrapolation = value

                        kw_fileformat = 'FileFormat'
                        fileformat_settings = getKeyword(update_grf_settings, kw_fileformat, modelFile=model_file_name, required=False)
                        if fileformat_settings is not None:
                            value = fileformat_settings.text.strip().lower()
                            legal_values = ['roff', 'grdecl']
                            if value in legal_values:
                                self.__fmu_file_format = value
                            else:
                                raise ValueError(
                                    f"Job settings parameter for {kw_fileformat} "
                                    f"must be one of {legal_values}"
                                )

                if self.__fmu_mode in ['NOFIELDS', 'FIELDS']:
                    kw_export = 'ExportConfigFiles'
                    export_settings = getKeyword(fmu_settings, kw_export, modelFile=model_file_name, required=False)
                    if export_settings is not None:
                        value = export_settings.text.strip().upper()
                        legal_values = ['YES', 'NO']
                        if value not in legal_values:
                            raise ValueError(
                                f"Job settings for keyword {kw_export} must be one of {legal_values}. "
                            )
                        if value == 'YES':
                            self.__fmu_export_config_files = True
            if run_settings is not None:
                kw_fraction = 'MaxFractionNotNormalised'
                fraction_settings = getKeyword(run_settings, kw_fraction, modelFile=model_file_name, required=False)
                if fraction_settings is not None:
                    value = float(fraction_settings.text.strip())
                    if value >= 0 and value <= 1.0:
                        self.__prob_settings_fraction = value
                    else:
                        raise ValueError(
                            f"Job settings for max probability fraction is {value}. "
                            "Should be in interval [0.0, 1.0]"
                        )
                kw_tolerance = 'ToleranceLimitProbability'
                tolerance_settings = getKeyword(run_settings, kw_tolerance, modelFile=model_file_name, required=False)
                if tolerance_settings is not None:
                    value = float(tolerance_settings.text.strip())
                    if value >= 0 and value <= 1.0:
                        self.__prob_settings_tolerance = value
                    else:
                        raise ValueError(
                            f"Job settings for max probability tolerance (fraction between 0 and 1) is {value}. "
                            "Should be in interval [0.0, 1.0]"
                        )
            if transform_settings is not None:
                value = transform_settings.text.strip().upper()
                if value in ['0', 'EMPIRIC']:
                    self.__transform_type = TransformType.EMPIRIC
                elif value in ['1', 'CDF']:
                    self.__transform_type = TransformType.CUMNORM
                else:
                    raise ValueError(
                        f"Job settings for transformation type was set to: {value}. "
                        "Should be either Empiric (or alternatively 0) "
                        "or CDF (or alternatively 1)."
                    )
            if log_settings is not None:
                value = int(log_settings.text.strip())
                legal_values = [
                        Debug.OFF.value,
                        Debug.ON.value,
                        Debug.VERBOSE.value,
                        Debug.VERY_VERBOSE.value,
                        Debug.VERY_VERY_VERBOSE.value
                        ]
                if value in legal_values:
                    self.__log_setting = Debug(value)
                else:
                    self.__log_setting = Debug.OFF

    def print_job_settings(self):
        print(
            "--- Job settings parameters:\n"
            "    FMU settings:\n"
            f"     FMU mode: {self.__fmu_mode}"
        )
        if self.__fmu_mode == 'FIELDS':
            print(
                "     Update fields in ERT:\n"
                f"      ERTBOX: {self.__fmu_ertbox_name}\n"
                f"      Exchange mode: {self.__fmu_exchange_mode}\n"
                f"      File format: {self.__fmu_file_format}\n"
                f"      Trend param extrapolation:  {self.__fmu_trend_param_extrapolation}"
            )
        if self.__fmu_mode != 'OFF':
            print(f"     Export config files: {self.__fmu_export_config_files} ")
        print(
            "    Prob check criteria:\n"
            f"     Fraction:  {self.__prob_settings_fraction}\n"
            f"     Tolerance: {self.__prob_settings_tolerance}\n"
            f"    Transform type: {self.__transform_type.value}\n"
            f"    Log setting: {self.__log_setting.name}\n\n"
        )

    def job_settings_xml_add_elements(self, root):
        if self.debug_level >= Debug.VERY_VERBOSE:
            print("--- call XMLADDElement from Job settings")

        job_settings_element = ET.Element('JobSettings')
        root.append(job_settings_element)

        fmu_settings_element = ET.Element('FmuSettings')
        job_settings_element.append(fmu_settings_element)

        fmu_settings_element.append(create_node('FmuMode',
                text=self.__fmu_mode))

        if self.__fmu_mode == 'FIELDS':
            fmu_update_grf_element = ET.Element('UpdateGRF')
            fmu_settings_element.append(fmu_update_grf_element)

            fmu_update_grf_element.append(create_node('ErtBoxGrid',
                text=self.__fmu_ertbox_name))

            fmu_update_grf_element.append(create_node('ExchangeMode',
                text=self.__fmu_exchange_mode))

            fmu_update_grf_element.append(create_node('FileFormat',
                text=self.__fmu_file_format))

            fmu_update_grf_element.append(create_node('ExtrapolationMethod',
                text=self.__fmu_trend_param_extrapolation))

        if self.__fmu_mode in ['NOFIELDS', 'FIELDS']:
            if self.__fmu_export_config_files:
                fmu_settings_element.append(create_node('ExportConfigFiles', text='YES'))

        run_settings_element = ET.Element('RunSettings')
        job_settings_element.append(run_settings_element)

        run_settings_element.append(create_node('MaxFractionNotNormalised',
            text=self.__prob_settings_fraction))

        run_settings_element.append(create_node('ToleranceLimitProbability',
            text=self.__prob_settings_tolerance))

        job_settings_element.append(create_node('TransformationSettings',
            text=self.__transform_type.value))

        job_settings_element.append(create_node('LogSetting',
            text=self.__log_setting.value))



def _max_name_length(fmu_attributes: List[FmuAttribute]) -> int:
    return max(len(fmu_attribute.name) for fmu_attribute in fmu_attributes)


def _max_value_length(fmu_attributes: List[FmuAttribute]) -> int:
    return max(len(str(fmu_attribute.value)) for fmu_attribute in fmu_attributes)


def probability_distribution_configuration(fmu_attributes: List[FmuAttribute], current_job_name: str) -> str:
    if not fmu_attributes:
        return ''
    content = ''
    max_length = _max_name_length(fmu_attributes) + len(current_job_name)
    for fmu_attribute in fmu_attributes:
        symbolic_name = current_job_name.upper() + '_' + fmu_attribute.name
        content += f'{symbolic_name:<{max_length}} <prob_dist>\n'
    return content


def fmu_configuration(fmu_attributes: List[FmuAttribute], current_job_name: str) -> str:
    if not fmu_attributes:
        return ''
    content = '# Note: Check that job name specified under keyword APS below is correct.\n'
    content += '#       It should be the same as the APS job these parameters belongs to.\n'
    content += '#       The job name must be used only once and the job name must be case insensitive\n'
    content += '#       (e.g Jobname and JOBNAME is treated as the same name).\n'
    content += '# Note: This file should be copied into the "global:" section of the global_master_config.yml file\n'
    content += '#       which is located per default under the "fmuconfig/input" directory in the FMU project.\n' 
    content += '  APS:\n'
    content += f'    {current_job_name}:\n'
    max_length = _max_name_length(fmu_attributes)
    max_number_length = _max_value_length(fmu_attributes)
    for fmu_attribute in fmu_attributes:
        key_word_spacing = max_length - len(fmu_attribute.name) + 1
        symbolic_name = current_job_name.upper() + '_' + fmu_attribute.name
        formatted_value = f'{fmu_attribute.value:{max_number_length}.10{"g" if isinstance(fmu_attribute.value, int) else ""}}'
        content += f'        {fmu_attribute.name}:{" ":<{key_word_spacing}}{formatted_value} ~ <{symbolic_name}>\n'
    return content


ApsModel = APSModel
