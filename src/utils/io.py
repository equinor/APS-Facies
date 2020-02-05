# -*- coding: utf-8 -*-
import os
from os.path import exists
from pathlib import Path
from tempfile import NamedTemporaryFile

import numpy as np

from src.utils.constants.simple import Debug
from src.utils.roxar import running_in_batch_mode
from src.utils.methods import get_workflow_name


def write_status_file(status, always=False):
    if running_in_batch_mode() or always:
        file_name = f'statusfile_{get_workflow_name()}.dat'
        with open(file_name, 'w') as f:
            f.write(f'{status}\n')


def writeFile(file_name, a, nx, ny, debug_level=Debug.SOMEWHAT_VERBOSE):
    print(f'Write file: {file_name}')
    # Choose an arbitrary heading
    heading = f'''-996  {ny}  50.000000     50.000000
637943.187500   678043.187500  4334008.000000  4375108.000000
 {nx}  0.000000   637943.187500  4334008.000000
0     0     0     0     0     0     0
'''
    _write_file(file_name, a, heading, debug_level)


def readFile(fileName, debug_level=Debug.OFF):
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


def writeFileRTF(file_name, data, dimensions, increments, x0, y0, debug_level=Debug.OFF):
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


def print_debug_information(function_name, text):
    if function_name in [' ', '']:
        print(f'Debug output: {text}\n')
    else:
        print(f'Debug output in {function_name}: {text}\n')


def print_error(function_name, text):
    print(f'Error in {function_name}: {text}')


class TemporaryFile:
    def __init__(self, file):
        self._file = file

    def __repr__(self):
        return f'{self.__class__.__name__}(name="{self!s}")'

    def __str__(self):
        return self._file.name

    def __enter__(self):
        return str(Path(self._file.name).absolute())

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.unlink(str(self._file.name))


def create_temporary_model_file(model):
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


def ensure_folder_exists(seed_file_log):
    if not seed_file_log.is_dir():
        seed_file_log = seed_file_log.parent
    if not seed_file_log.exists():
        from os import makedirs
        makedirs(seed_file_log)


class GlobalVariables:
    @classmethod
    def parse(cls, global_variables_file):
        global_variables_file = Path(global_variables_file)
        suffix = global_variables_file.suffix.lower().strip('.')
        if suffix == 'ipl':
            return cls._read_ipl(global_variables_file)
        elif suffix in ['yaml', 'yml']:
            return cls._read_yaml(global_variables_file)
        else:
            raise NotImplementedError('{} is an unknown suffix, which cannot be read'.format(suffix))

    @staticmethod
    def _read_ipl(global_variables_file):
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
    def _read_yaml(cls, global_variables_file):
        try:
            import yaml
        except ImportError:
            raise NotImplementedError('PyYaml is required')
        with open(global_variables_file, 'r') as file:
            global_variables = yaml.safe_load(file)

        global_variables = list(global_variables.get('rms', {}).items())
        return [
            (key, val) for key, val in global_variables
            if cls.is_numeric(val)
        ]

    @staticmethod
    def is_numeric(val):
        try:
            float(val)
        except (ValueError, TypeError):
            return False
        return True
