#!/bin/env python
# -*- coding: utf-8 -*-
from aps.utils.methods import get_debug_level, get_specification_file, SpecificationType, get_model_file_format
from aps.toolbox.create_probability_logs import run as run_create_prob_logs
from aps.utils.constants.simple import Debug

def run(roxar=None, project=None, **kwargs):
    model_file_format = get_model_file_format(**kwargs)
    params = {
        'project': project,
        'model_file_name': get_specification_file(_type=SpecificationType.PROBABILITY_LOG, _format=model_file_format, **kwargs),
        'debug_level': get_debug_level(**kwargs)
    }
    run_create_prob_logs(params)


if __name__ == '__main__':
    import roxar
    run(roxar, project=project, debug_level=Debug.VERBOSE)
