# -*- coding: utf-8 -*-
import os
from os.path import exists
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Tuple, Union, List

import numpy as np

from src.utils.constants.simple import Debug
from src.utils.roxar import running_in_batch_mode
from src.utils.methods import get_workflow_name


def write_status_file(status: bool, always: bool = False) -> None:
    if running_in_batch_mode() or always:
        file_name = f'statusfile_{get_workflow_name()}.dat'
        with open(file_name, 'w') as f:
            f.write(f'{status}\n')


def writeFile(
        file_name: str,
        a: Union[List[int], np.ndarray],
        nx: int,
        ny: int,
        debug_level: Debug = Debug.SOMEWHAT_VERBOSE,
):
    print(f'Write file: {file_name}')
    # Choose an arbitrary heading
    heading = f'''-996  {ny}  50.000000     50.000000
637943.187500   678043.187500  4334008.000000  4375108.000000
 {nx}  0.000000   637943.187500  4334008.000000
0     0     0     0     0     0     0
'''
    _write_file(file_name, a, heading, debug_level)


def readFile(
        fileName: str,
        debug_level: Debug = Debug.OFF
) -> Tuple[np.ndarray, int, int]:
    if debug_level >= Debug.SOMEWHAT_VERBOSE:
        print(f'Read file: {fileName}')
    if not exists(fileName):
        fileName = f'src/unit_test/{fileName}'
    with open(fileName, 'r') as file:
        inString = file.read()
        words = inString.split()
        ny = int(words[1])
        nx = int(words[8])
        if debug_level >= Debug.SOMEWHAT_VERBOSE:
            n = len(words)
            print(
                f'Number of words: {n}\n'
                f'nx,ny: {nx} {ny}\n'
                f'Number of values: {len(words) - 19}'
            )
        a = np.zeros(nx * ny, float)
        for i in range(19, len(words)):
            a[i - 19] = float(words[i])
    return a, nx, ny


def writeFileRTF(
        file_name: str,
        data: Union[List[int], np.ndarray],
        dimensions: Tuple[int, int],
        increments: Tuple[float, float],
        x0: float,
        y0: float,
        debug_level=Debug.OFF
) -> None:
    nx, ny = dimensions
    dx, dy = increments
    # Write in Roxar text format
    heading = f'''\
-996  {ny}  {dx} {dy}
{x0} {x0 + nx * dx} {y0} {y0 + ny * dy}
 {nx}  0.000000  {x0} {y0}
0     0     0     0     0     0     0
'''
    _write_file(file_name, data, heading, debug_level)


def _write_file(file_name, data, heading, debug_level):
    output = heading
    count = 0
    text = ''
    if debug_level >= Debug.SOMEWHAT_VERBOSE:
        print(f'len(data): {len(data)}')
    for point in data:
        text += str(point) + '  '
        count += 1
        if count >= 5:
            text += '\n'
            output += text
            count = 0
            text = ''
    if count > 0:
        output += text + '\n'
    with open(file_name, 'w') as file:
        file.write(output)
    if debug_level >= Debug.SOMEWHAT_VERBOSE:
        print(f'Write file: {file_name}')


def print_debug_information(function_name: str, text: str) -> None:
    if function_name in [' ', '']:
        print(f'Debug output: {text}\n')
    else:
        print(f'Debug output in {function_name}: {text}\n')


def print_error(function_name: str, text: str) -> None:
    print(f'Error in {function_name}: {text}')


class TemporaryFile:
    def __init__(self, file: NamedTemporaryFile):
        self._file: NamedTemporaryFile = file

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(name="{self!s}")'

    def __str__(self) -> str:
        return self._file.name

    def __enter__(self) -> str:
        return str(Path(self._file.name).absolute())

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.unlink(str(self._file.name))


def create_temporary_model_file(model: str) -> TemporaryFile:
    file = NamedTemporaryFile(
        suffix='.xml',
        delete=False,
    )
    try:
        file.write(model.encode('ascii'))
        file.seek(0)
    finally:
        file.close()
    return TemporaryFile(file)


def ensure_folder_exists(seed_file_log: Path) -> None:
    if not seed_file_log.is_dir():
        seed_file_log = seed_file_log.parent
    if not seed_file_log.exists():
        from os import makedirs
        makedirs(seed_file_log)


_GlobalVariables = List[Tuple[str, float]]


class GlobalVariables:
    @classmethod
    def check_file_format(cls, global_variables_file: Union[str, Path]) -> str:
        global_variables_file = Path(global_variables_file)
        suffix = global_variables_file.suffix.lower().strip('.')
        if suffix == 'ipl':
            return 'ipl'
        elif suffix in ['yaml', 'yml']:
            return 'yml'
        else:
            raise NotImplementedError('{} is an unknown suffix, which cannot be read'.format(suffix))

    @classmethod
    def parse(cls, global_variables_file: Path) -> _GlobalVariables:
        global_variables_file = Path(global_variables_file)
        suffix = global_variables_file.suffix.lower().strip('.')
        if suffix == 'ipl':
            return cls._read_ipl(global_variables_file)
        elif suffix in ['yaml', 'yml']:
            return cls._read_yaml(global_variables_file)
        else:
            raise NotImplementedError('{} is an unknown suffix, which cannot be read'.format(suffix))

    @staticmethod
    def _read_ipl(global_variables_file: Path) -> _GlobalVariables:
        ''' Read global variables for APS from global IPL file.
            Returns a list of aps parameter names and values.
            IPL format does only support RMS project with one grid model (multizone grid)
            with only one APS job.
        '''

        keywords = []
        with open(global_variables_file, 'r') as file:
            lines = file.readlines()

        for line in lines:
            words = line.split()
            if len(words) < 3:
                # Skip line (searching for an assignment like keyword = value with at least 3 words
                continue
            if words[0] == '//':
                # Skip line
                continue

            if words[1] == '=':
                # This is assumed to be an assignment
                keyword, _, value, *_ = words
                keywords.append([keyword, value])
        return keywords

    @classmethod
    def _read_yaml(cls, global_variables_file: Path) -> _GlobalVariables:
        ''' YAML format for global variables support RMS project with multiple grid models
            where the grid models can be single-zone grid models or multi-zone grid models
            and where each grid model may have multiple APS jobs where each job can have
            their own set of APS model parameters to be updated by FMU.
            Returns a dictionary of model parameter specification for each grid model
            and each job for each grid model.
            Example structure of the YAMLS file:
            global:
              APS:
                  APS_job_1:
                   APS_1_0_GF_GRF1_RESIDUAL_AZIMUTHANGLE: 100.0
                   APS_1_0_GF_GRF1_TREND_AZIMUTH: 0.0
                  APS_job_2:
                   APS_1_0_GF_GRF1_RESIDUAL_AZIMUTHANGLE: 200.0
                   APS_1_0_GF_GRF2_TREND_AZIMUTH: 80.0

                  APS_job_3:
                   APS_1_0_GF_GRF1_TREND_RELSTDDEV: 0.1
                   APS_2_0_GF_GRF1_TREND_AZIMUTH: 0.0
                   APS_3_0_GF_GRF1_RESIDUAL_MAINRANGE: 2000.0
                  APS_job_3:
                   APS_1_0_GF_GRF1_TREND_RELSTDDEV: 0.1
                   APS_1_0_GF_GRF1_TREND_AZIMUTH: 0.0
                   APS_2_0_GF_GRF1_RESIDUAL_AZIMUTHANGLE: 135.0
       '''
        try:
            import yaml
        except ImportError:
            raise NotImplementedError('PyYaml is required')
        with open(global_variables_file, 'r') as file:
            all_variables = yaml.safe_load(file)

        global_variables = all_variables['global']
        aps_variables = None
        if global_variables is not None:
            key = 'APS'
            if key in global_variables.keys():
                aps_variables = global_variables[key]
            else:
                key = 'aps'
                if key in global_variables.keys():
                    aps_variables = global_variables[key]

        # Returns a list of dictionaries for each specified grid model
        # with aps parameters for each specified job-id for each grid model
        return aps_variables

    @staticmethod
    def is_numeric(val) -> bool:
        try:
            float(val)
        except (ValueError, TypeError):
            return False
        return True
