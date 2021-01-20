#!/bin/env python
# -*- coding: utf-8 -*-
# This script use both nrlib and ROXAR API functions and run simulations sequentially and not in parallel
import os
from pathlib import Path
from aps.algorithms.APSModel import APSModel
from aps.utils.methods import get_run_parameters
from aps.utils.constants.simple import Debug


def run(roxar=None, project=None, **kwargs):
    params = get_run_parameters(**kwargs)
    model_file = params['model_file']
    real_number = project.current_realisation
    apsModel = APSModel(model_file)
    debug_level = apsModel.debug_level
    seedFileName = apsModel.seed_file_name
    writeSeedFile = apsModel.write_seeds

    # Set seed file to point to seed file for this realisation
    seedFileNameNew = 'seed_list_' + str(real_number + 1) + '.dat'
    command = 'ln -sf ' + seedFileNameNew + ' ' + seedFileName
    os.system(command)

    if writeSeedFile:
        if debug_level >= Debug.ON:
            print(f'Random seeds for this realisation is written to: {seedFileNameNew}')
    else:
        # Check that the file can be opened for reading
        seedFile = Path(seedFileNameNew)
        if not seedFile.is_file():
            raise IOError(f'Can not open and read seed file: {seedFileNameNew}')
        if debug_level >= Debug.ON:
            print(f'Random seeds for this realisation read from: {seedFileNameNew}')


if __name__ == '__main__':
    import roxar
    run(roxar, project)
