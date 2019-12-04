# -*- coding: utf-8 -*-
from PIL import Image

from src.algorithms.Trunc2D_Angle_xml import Trunc2D_Angle
from src.algorithms.Trunc2D_Cubic_xml import Trunc2D_Cubic
from src.algorithms.Trunc3D_bayfill_xml import Trunc3D_bayfill
from src.utils.constants.simple import Debug
from typing import (
    Any,
    List,
    Union,
    Callable)

TruncationRule = Union[Trunc2D_Angle, Trunc3D_bayfill, Trunc2D_Cubic]

def apply_truncations(
    truncRule: TruncationRule,
    faciesReferenceFile: str,
    nGaussFields: int,
    gaussFieldFiles: List[str],
    faciesOutputFile: str,
    debug_level: Debug = Debug.OFF
) -> None: ...


def apply_truncations_vectorized(
    truncRule:              TruncationRule,
    faciesReferenceFile:    str,
    nGaussFields:           int,
    gaussFieldFiles:        List[str],
    faciesOutputFile:       str,
    debug_level:            Debug = Debug.OFF
) -> None: ...

def compare_image(source: Union[str, Image], reference: Union[str, Image]) -> bool: ...

def assert_identical_files(source: str, reference: str) -> None: ...
def assert_equal_image_content_files(source: str, reference: str) -> None: ...

def _assert_compare_files(source: str, reference: str, func: Callable[[str, str], bool]): ...


def getFaciesInTruncRule(
    truncRule: TruncationRule,
    truncRule2: TruncationRule,
    faciesInTruncRule: List[str]
) -> None: ...


def get_cubic_facies_reference_file_path(testCase: int) -> str: ...


def get_model_file_path(modelFile: str) -> str: ...


def truncMapPolygons(
    truncRule: TruncationRule,
    truncRule2: TruncationRule,
    faciesProb: List[float],
    outPolyFile1: str,
    outPolyFile2: str
) -> None: ...


def writePolygons(fileName: str, polygons: Any, debug_level: Debug = Debug.OFF) -> None: ...
