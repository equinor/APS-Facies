# -*- coding: utf-8 -*-
from numpy import ndarray
from src.utils.constants.simple import Debug
from typing import List, Tuple, Union


def readFile(
    fileName: str,
    debug_level: Debug = Debug.OFF
) -> Tuple[ndarray, int, int]: ...


def writeFile(
    fileName: str,
    a: Union[List[int], ndarray],
    nx: int,
    ny: int,
    debug_level: Debug = Debug.OFF
) -> None: ...

def writeFileRTF(
    file_name: str,
    data: Union[List[int], ndarray],
    dimensions: Tuple[int, int],
    increments: Tuple[float, float],
    x0: float,
    y0: float,
    debug_level=Debug.OFF
) -> None: ...

def print_debug_information(function_name: str, text: str) -> None: ...
def print_error(function_name: str, text: str) -> None: ...