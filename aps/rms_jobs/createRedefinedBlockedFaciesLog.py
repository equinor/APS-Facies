#!/bin/env python
from aps.toolbox.create_redefined_blocked_facies_log import run as run_redefine_blocked_facies_logs
from aps.utils.methods import get_debug_level, get_specification_file, SpecificationType
from aps.utils.constants.simple import Debug


def run(roxar=None, project=None, **kwargs):
    model_file_name = get_specification_file(_type=SpecificationType.FACIES_LOG, **kwargs)
    debug_level = get_debug_level(**kwargs)
    params = {
        "project": project,
        "model_file_name": model_file_name,
        "debug_level": debug_level,
    }
    run_redefine_blocked_facies_logs(params)

if __name__ == '__main__':
    import roxar
    run(roxar, project, debug_level=Debug.VERBOSE)
