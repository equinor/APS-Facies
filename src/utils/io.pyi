# -*- coding: utf-8 -*-
from pathlib import Path
from tempfile import NamedTemporaryFile

from numpy import ndarray
from src.utils.constants.simple import Debug
from typing import List, Tuple, Union


def write_status_file(status: bool, always: bool=False) -> None: ...

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

class TemporaryFile:
    _file: NamedTemporaryFile

    def __init__(self, file: NamedTemporaryFile): ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def __enter__(self) -> str: ...
    def __exit__(self, exc_type, exc_val, exc_tb): ...

def create_temporary_model_file(model: str) -> TemporaryFile: ...
def ensure_folder_exists(seed_file_log: Path) -> None: ...

_GlobalVariables = List[Tuple[str, float]]

class GlobalVariables:
    @classmethod
    def parse(cls, global_variables_file: Path) -> _GlobalVariables: ...
    @staticmethod
    def _read_ipl(global_variables_file: Path) -> _GlobalVariables: ...
    @staticmethod
    def _read_yaml(global_variables_file: Path) -> _GlobalVariables: ...
