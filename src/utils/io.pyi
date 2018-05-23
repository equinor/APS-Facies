# -*- coding: utf-8 -*-
from numpy import ndarray
from src.utils.constants.simple import Debug
from typing import List, Tuple


def readFile(
    fileName: str,
    debug_level: Debug = Debug.OFF
) -> Tuple[ndarray, int, int]: ...


def writeFile(
    fileName: str,
    a: List[int],
    nx: int,
    ny: int,
    dx = 50.0,
    dy = 50.0,
    debug_level: Debug = Debug.OFF
) -> None: ...
