# -*- coding: utf-8 -*-
from depricated.APSGaussFieldJobs import APSGaussFieldJobs
from src.algorithms.APSMainFaciesTable import APSMainFaciesTable
from src.algorithms.APSZoneModel import APSZoneModel
from src.utils.constants.simple import Debug
from typing import List, Optional, Union
from xml.etree.ElementTree import Element


class APSModel:
    def __init__(
        self,
        modelFileName: Optional[str] = None,
        rmsProjectName: str = '',
        rmsWorkflowName: str = '',
        rmsGaussFieldScriptName: str = '',
        rmsGridModelName: str = '',
        rmsSingleZoneGrid: str = 'False',
        rmsZoneParameterName: str = '',
        rmsRegionParameterName: str = '',
        rmsFaciesParameterName: str = '',
        seedFileName: str = 'seed.dat',
        writeSeeds: bool = True,
        rmsGFJobs: None = None,
        rmsHorizonRefName: str = '',
        rmsHorizonRefNameDataType: str = '',
        mainFaciesTable: None = None,
        zoneModelTable: None = None,
        previewZone: int = 0,
        previewRegion: int = 0,
        previewCrossSectionType: str = 'IJ',
        previewCrossSectionRelativePos: float = 0.5,
        previewScale: float = 1.0,
        debug_level: Debug = Debug.OFF
    ) -> None: ...
    def XMLAddElement(self, root: Element) -> str: ...
    def addNewZone(self, zoneObject: APSZoneModel) -> None: ...
    def debug_level(self) -> Debug: ...
    def deleteZone(self, zoneNumber: int, regionNumber: int = 0) -> None: ...
    def getGaussFieldJobs(self) -> APSGaussFieldJobs: ...
    def getMainFaciesTable(self) -> APSMainFaciesTable: ...
    def getSelectedRegionNumberListForSpecifiedZoneNumber(self, zoneNumber: int) -> List[int]: ...
    def getSelectedZoneNumberList(self) -> List[int]: ...
    def getZoneModel(self, zoneNumber: int, regionNumber: int = 0) -> APSZoneModel: ...
    def getZoneNumberList(self) -> List[int]: ...
    def setGaussFieldJobs(self, gfJobObject: APSGaussFieldJobs) -> None: ...
    def setGaussFieldScriptName(self, name: str) -> None: ...
    def setMainFaciesTable(self, faciesTableObj: APSMainFaciesTable) -> None: ...
    def setPreviewZoneAndRegionNumber(self, zoneNumber: int, regionNumber: int = 0) -> None: ...
    def setRmsGridModelName(self, name: str) -> None: ...
    def setRmsProjectName(self, name: str) -> None: ...
    def setRmsResultFaciesParamName(self, name: str) -> None: ...
    def setRmsWorkflowName(self, name: str) -> None: ...
    def setRmsZoneParamName(self, name: str) -> None: ...
    def setSeedFileName(self, name: str) -> None: ...
    def setSelectedZoneAndRegionNumber(self, selectedZoneNumber: int, selectedRegionNumber: int = 0) -> None: ...
    def set_debug_level(self, debug_level: Union[str, Debug]) -> None: ...
    def writeModel(self, modelFileName: str, debug_level: Debug = Debug.OFF) -> None: ...