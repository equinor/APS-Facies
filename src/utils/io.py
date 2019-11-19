# -*- coding: utf-8 -*-
import os
from base64 import b64decode
from os.path import exists
from pathlib import Path
from tempfile import NamedTemporaryFile

import numpy as np

from src.utils.constants.simple import Debug
from src.utils.roxar import running_in_batch_mode
from src.utils.methods import get_workflow_name


def write_status_file(status, always=False):
    if running_in_batch_mode() or always:
        file_name = 'statusfile_{workflow_name}.dat'.format(workflow_name=get_workflow_name())
        with open(file_name, 'w') as f:
            f.write('{status}\n'.format(status=int(status)))


def writeFile(fileName, a, nx, ny, debug_level=Debug.SOMEWHAT_VERBOSE):
    print('Write file: {}'.format(fileName))
    with open(fileName, 'w') as file:
        # Choose an arbitrary heading
        outstring = '''-996  {ny}  50.000000     50.000000
637943.187500   678043.187500  4334008.000000  4375108.000000
 {nx}  0.000000   637943.187500  4334008.000000
0     0     0     0     0     0     0
'''.format(ny=ny, nx=nx)
        count = 0
        text = ''
        if debug_level >= Debug.SOMEWHAT_VERBOSE:
            print('len(a): ' + str(len(a)))
        for j in range(len(a)):
            text = text + str(a[j]) + '  '
            count += 1
            if count >= 5:
                text += '\n'
                outstring += text
                count = 0
                text = ''
        if count > 0:
            outstring += text + '\n'
        file.write(outstring)
    if debug_level >= Debug.SOMEWHAT_VERBOSE:
        print('Write file: ' + fileName)


def readFile(fileName, debug_level=Debug.OFF):
    if debug_level >= Debug.SOMEWHAT_VERBOSE:
        print('Read file: ' + fileName)
    if not exists(fileName):
        file_location = 'src/unit_test/'
        fileName = file_location + fileName
    with open(fileName, 'r') as file:
        inString = file.read()
        words = inString.split()
        ny = int(words[1])
        nx = int(words[8])
        if debug_level >= Debug.SOMEWHAT_VERBOSE:
            n = len(words)
            print('Number of words: ' + str(n))
            print('nx,ny: ' + str(nx) + ' ' + str(ny))
            print('Number of values: ' + str(len(words) - 19))
        a = np.zeros(nx * ny, float)
        for i in range(19, len(words)):
            a[i - 19] = float(words[i])
    return a, nx, ny


def writeFileRTF(file_name, data, dimensions, increments, x0, y0, debug_level=Debug.OFF):
    nx, ny = dimensions
    dx, dy = increments
    # Write in Roxar text format
    with open(file_name, 'w') as file:
        outstring = '-996  ' + str(ny) + '  ' + str(dx) + ' ' + str(dy) + '\n'
        outstring += str(x0) + ' ' + str(x0 + nx * dx) + ' ' + str(y0) + ' ' + str(y0 + ny * dy) + '\n'
        outstring += ' ' + str(nx) + ' ' + ' 0.000000  ' + str(x0) + ' ' + str(y0) + '\n'
        outstring += '0     0     0     0     0     0     0\n'
        count = 0
        text = ''
        if debug_level >= Debug.SOMEWHAT_VERBOSE:
            print('len(data): ' + str(len(data)))
        for j in range(len(data)):
            text = text + str(data[j]) + '  '
            count += 1
            if count >= 5:
                text += '\n'
                outstring += text
                count = 0
                text = ''
        if count > 0:
            outstring += text + '\n'
        file.write(outstring)
    if debug_level >= Debug.SOMEWHAT_VERBOSE:
        print('Write file: ' + file_name)


def print_debug_information(function_name, text):
    if function_name in [' ', '']:
        print('Debug output: {text}\n'.format(text=text))
    else:
        print('Debug output in {function_name}: {text}\n'.format(function_name=function_name, text=text))


def print_error(function_name, text):
    print('Error in {function_name}: {text}'.format(function_name=function_name, text=text))


class TemporaryFile:
    def __init__(self, file):
        self._file = file

    def __repr__(self):
        return 'TemporaryFile(name="{name}")'.format(name=str(self))

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
        file.write(b64decode(model))
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
