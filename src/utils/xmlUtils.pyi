# -*- coding: utf-8 -*-
from typing import Optional, Union
from xml.etree.ElementTree import Element


def getBoolCommand(
    parent: Element,
    keyword: str,
    parent_keyword: str = '',
    default: bool = False,
    model_file_name: Optional[str] = None,
    required: bool = True
) -> bool: ...


def getFloatCommand(
    parent: Element,
    keyword: str,
    parentKeyword: str = '',
    minValue: Optional[float] = None,
    maxValue: Optional[float] = None,
    defaultValue: Optional[Union[int, float]] = None,
    modelFile: Optional[str] = None,
    required: bool = True
) -> float: ...


def getIntCommand(
    parent: Element,
    keyword: str,
    parentKeyword: str = '',
    minValue: Optional[int] = None,
    maxValue: Optional[int] = None,
    defaultValue: Optional[int] = None,
    modelFile: Optional[str] = None,
    required: bool = True
) -> int: ...


def getKeyword(
    parent: Element,
    keyword: str,
    parentKeyword: str = '',
    modelFile: Optional[str] = None,
    required: bool = True
) -> Optional[Element]: ...


def getTextCommand(
    parent: Element,
    keyword: str,
    parentKeyword: str = '',
    defaultText: Optional[str] = None,
    modelFile: Optional[str] = None,
    required: bool = True
) -> Optional[str]: ...


def prettify(elem: Element, indent: str = " ", new_line: str = "\n") -> str: ...

def minify(elem: Element) -> str: ...


def isFMUUpdatable(
    parent:Element,
    keyword: str
) -> bool: ...

def createFMUvariableNameForTrend(
    keyword: str,
    grf_name: str,
    zone_number: str,
    region_number: Optional[int] = None,
) -> str: ...

def createFMUvariableNameForResidual(
    keyword: str,
    grf_name: str,
    zone_number: int,
    region_number: Optional[int] = None,
) -> str: ...

def createFMUvariableNameForBayfillTruncation(
        keyword: str,
        zone_number: int,
        region_number: Optional[int] = None,
) -> str: ...

def createFMUvariableNameForNonCubicTruncation(
        index: int,
        zone_number: int,
        region_number: Optional[int] = None,
) -> str: ...