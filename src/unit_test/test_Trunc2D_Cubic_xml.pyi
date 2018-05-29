from src.algorithms.Trunc2D_Cubic_xml import Trunc2D_Cubic
from src.utils.constants.simple import Debug
from typing import (
    Dict,
    List,
    Tuple,
    Union,
)


def createTrunc(
    outputModelFileName: str,
    fTable: Dict[int, str],
    faciesInZone: List[str],
    gaussFieldsInZone: List[str],
    gaussFieldsForBGFacies: List[str],
    truncStructure: List[Union[str, List[Union[str, float, int]]]],
    overlayGroups: List[List[Union[List[List[Union[str, float]]], List[str]]]],
    debug_level: Debug = Debug.OFF
) -> Trunc2D_Cubic: ...


def createXMLTreeAndWriteFile(
    truncRuleInput: Trunc2D_Cubic,
    outputModelFileName: str
) -> None: ...


def getClassName(truncRule: Trunc2D_Cubic) -> None: ...


def initialize_write_read(
    outputModelFileName1: str,
    outputModelFileName2: str,
    fTable: Dict[int, str],
    faciesInZone: List[str],
    gaussFieldsInZone: List[str],
    gaussFieldsForBGFacies: List[str],
    truncStructure: List[Union[str, List[Union[str, float, int]]]],
    overlayGroups: List[List[Union[List[List[Union[str, float]]], List[str]]]],
    debug_level: Debug = Debug.OFF
) -> Tuple[Trunc2D_Cubic, Trunc2D_Cubic]: ...


def interpretXMLModelFileAndWrite(
    modelFileName: str,
    outputModelFileName: str,
    fTable: Dict[int, str],
    faciesInZone: List[str],
    gaussFieldsInZone: List[str],
    debug_level: Debug = Debug.OFF
) -> Trunc2D_Cubic: ...


def run(
    fTable: Dict[int, str],
    faciesInTruncRule: List[str],
    faciesInZone: List[str],
    faciesProb: List[float],
    faciesReferenceFile: str,
    gaussFieldsInZone: List[str],
    gaussFieldsForBGFacies: List[str],
    overlayGroups: List[List[Union[List[List[Union[str, float]]], List[str]]]],
    truncStructure: List[Union[str, List[Union[str, float, int]]]]
) -> None: ...


def test_Trunc2DCubic(
    case_number: int,
    data: Dict[str, Union[Dict[int, str], List[str], List[Union[str, List[Union[str, float, int]]]], List[List[Union[List[List[Union[str, float]]], List[str]]]], List[float]]]
) -> None: ...
