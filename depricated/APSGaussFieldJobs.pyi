# -*- coding: utf-8 -*-
from src.utils.constants.simple import Debug
from typing import List, Optional
from xml.etree.ElementTree import Element, ElementTree


class APSGaussFieldJobs:
    def __init__(
        self,
        ET_Tree: Optional[ElementTree] = None,
        modelFileName: Optional[str] = None,
        debug_level: Debug = Debug.OFF
    ) -> None: ...
    def XMLAddElement(self, root: Element) -> None: ...
    def checkGaussFieldName(self, gfName: str) -> bool: ...
    def getNumberOfGFJobs(self) -> int: ...
    def initialize(
        self,
        gfJobNames: List[str],
        gfNamesPerJob: List[List[str]],
        debug_level: Debug = Debug.OFF
    ) -> None: ...
