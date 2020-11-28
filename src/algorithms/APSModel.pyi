# -*- coding: utf-8 -*-
from collections import OrderedDict

from src.algorithms.properties import CrossSection
from src.algorithms.APSMainFaciesTable import APSMainFaciesTable
from src.algorithms.APSZoneModel import APSZoneModel
from src.utils.constants.simple import Debug, CrossSectionType, TransformType
from typing import Any, List, Optional, Tuple, Dict, Type, Union
from xml.etree.ElementTree import Element, ElementTree

from src.utils.containers import FmuAttribute
from src.utils.types import FilePath

from roxar import Project


class APSModel:
    __aps_model_version: str
    __class_name: str
    __zoneModelTable: Dict[Tuple[int, int], APSZoneModel]
    __faciesTable: APSMainFaciesTable
    __previewZone: int
    __previewRegion: int
    __rmsProjectName: str
    __rmsWorkflowName: str
    __rmsGridModelName: str
    __rmsZoneParamName: str
    __rmsRegionParamName: str
    __rmsFaciesParamName: str
    __previewScale: float
    __previewResolution: int
    __selectedZoneAndRegionNumberTable: Dict[Tuple[int, int], int]
    __selectAllZonesAndRegions: bool
    def __init__(
            self,
            model_file_name: Optional[str] = None,
            aps_model_version: str = '1.0',
            rms_project_name: str = '',
            rms_workflow_name: str = '',
            rms_grid_model_name: str = '',
            rms_zone_parameter_name: str = '',
            rms_region_parameter_name: str = '',
            rms_facies_parameter_name: str = '',
            seed_file_name: str = 'seed.dat',
            write_seeds: bool = True,
            main_facies_table: Optional[APSMainFaciesTable] = None,
            zone_model_table: Optional[APSZoneModel] = None,
            preview_zone: int = 0,
            preview_region: int = 0,
            preview_cross_section_type: str = 'IJ',
            preview_cross_section_relative_pos: float = 0.5,
            preview_scale: float = 1.0,
            debug_level: Debug = Debug.OFF
    ) -> None: ...
    grid_model_name: str
    debug_level: Debug
    seed_file_name: str
    preview_scale: float
    preview_cross_section_type: CrossSectionType
    preview_cross_section_relative_position: float
    __preview_cross_section: CrossSection
    preview_cross_section: CrossSection
    preview_resolution: str
    sorted_zone_models: OrderedDict[Tuple[int, int], APSZoneModel]
    zone_models: List[APSZoneModel]
    use_constant_probability: bool
    write_seeds: bool
    zone_parameter: str
    region_parameter: str
    use_regions: bool
    rms_project_name: Optional[str]
    gaussian_field_names: List[str]
    has_fmu_updatable_values: bool
    transform_type: TransformType

    def __parse_model_file(self, model_file_name: FilePath, debug_level=Debug.OFF): ...
    @classmethod
    def from_string(
            cls,
            xml_content:                str,
            debug_level:                Optional[Debug]     = Debug.OFF,
    ) -> APSModel: ...
    def __interpretTree(
            self,
            root:                       Element,
            debug_level:                Optional[Debug]     = Debug.OFF,
            model_file_name:            Optional[str]       = None
    ) -> None: ...
    def update_model_file(
            self,
            model_file_name:            Optional[FilePath]  = None,
            parameter_file_name:        Optional[FilePath]  = None,
            project:                    Optional[Project]   = None,
            workflow_name:              Optional[str]       = None,
            uncertainty_variable_names: Optional[List[str]] = None,
            realisation_number:         int                 = 0,
            debug_level:                Debug               = Debug.OFF,
            current_job_name:           Optional[str]       = None,
            use_rms_uncertainty_table:  bool                = False,
    ) -> ElementTree: ...
    def __checkZoneModels(self) -> None: ...
    def getXmlTree(self): ...
    def getRoot(self): ...
    def XMLAddElement(self, root: Element, fmu_attributes: List[FmuAttribute]) -> str: ...
    def addNewZone(self, zoneObject: APSZoneModel) -> None: ...
    def deleteZone(self, zone_number: int, region_number: int = 0) -> None: ...
    def getAllZoneModels(self): ...
    def getMainFaciesTable(self) -> APSMainFaciesTable: ...
    def getRegionNumberListForSpecifiedZoneNumber(self, zoneNumber: int) -> List[int]: ...
    def getPreviewRegionNumber(self) -> int: ...
    def getPreviewZoneNumber(self) -> int: ...
    def getResultFaciesParamName(self): ...
    def getSelectedRegionNumberListForSpecifiedZoneNumber(self, zoneNumber: int) -> List[int]: ...
    def getSelectedZoneNumberList(self) -> List[int]: ...
    def isAllZoneRegionModelsSelected(self): ...
    def isSelected(self, zone_number: int, region_number: int) -> bool: ...
    def getZoneModel(self, zone_number: int, region_number: int = 0) -> APSZoneModel: ...
    def getAllGaussFieldNamesUsed(self) -> List[str]: ...
    def getZoneParamName(self): ...
    def getRegionParamName(self): ...
    def getZoneNumberList(self) -> List[int]: ...
    def setMainFaciesTable(self, faciesTableObj: APSMainFaciesTable) -> None: ...
    def getAllProbParam(self): ...
    def setPreviewZoneAndRegionNumber(self, zoneNumber: int, regionNumber: int = 0) -> None: ...
    def setRmsGridModelName(self, name: str) -> None: ...
    def setRmsResultFaciesParamName(self, name: str) -> None: ...
    def setRmsWorkflowName(self, name: str) -> None: ...
    def setRmsZoneParamName(self, name: str) -> None: ...
    def setRmsRegionParamName(self, name: str) -> None: ...
    def setSelectedZoneAndRegionNumber(self, selectedZoneNumber: int, selectedRegionNumber: int = 0) -> None: ...
    def dump(
            self,
            name:                               FilePath,
            attributes_file_name:               Optional[FilePath]  = None,
            probability_distribution_file_name: Optional[FilePath]  = None,
            debug_level:                        Debug               = Debug.OFF,
    ) -> None: ...
    def write_model(
            self,
            model_file_name:                    FilePath,
            attributes_file_name:               Optional[FilePath]  = None,
            probability_distribution_file_name: Optional[FilePath]  = None,
            current_job_name:                   Optional[str]       = None,
            debug_level:                        Debug               = Debug.OFF,
    ) -> None: ...
    def __parse_global_variables(
            self,
            model_file_name:            str,
            global_variables_file:      FilePath,
            current_job_name:           Optional[str]       = None,
            debug_level:                Debug               = Debug.OFF,
    ) -> List[Tuple[str, Union[str, float]]]: ...
    @staticmethod
    def __getParamFromRMSTable(
            project:                    Project,
            workflow_name: str,
            uncertainty_variable_names,
            realisation_number:         int,
    ) -> List[Tuple[str, str]]: ...
    @staticmethod
    def write_model_from_xml_root(
            input_tree,
            output_model_file_name:     FilePath,
    ): ...

def _max_name_length(fmu_attributes: List[FmuAttribute]) -> int: ...
def _max_value_length(fmu_attributes: List[FmuAttribute]) -> int: ...
def probability_distribution_configuration(fmu_attributes: List[FmuAttribute]) -> str: ...
def fmu_configuration(
        fmu_attributes:                 List[FmuAttribute],
        grid_model_name:                str,
        current_job_name:               str,
) -> str: ...


ApsModel: Type[APSModel]
