#!/bin/env python

from aps.toolbox import create_redefined_blocked_facies_log
from aps.utils.constants.simple import Debug

print(f"Run script: {create_redefined_blocked_facies_log.__file__}  ")

params = {
    "project": project,
    "debug_level": Debug.VERBOSE,
    "model_file_name": "examples/test_redefine_blocked_facies_log.xml",
    "realization_number": project.current_realisation,
}
create_redefined_blocked_facies_log.run(params)

