#!/bin/env python

from aps.toolbox import create_redefined_blocked_facies_log
from aps.utils.constants.simple import Debug

print(f"Run script: {create_redefined_blocked_facies_log.__file__}  ")

new_code_names = {
    1: "A",
    2: "B",
    3: "C",
}
# Original facies log has facies names F1, F2, F3, F4, F5, F6
# New facies log has facies names A,B,C
mapping = {
    "F1": "A",
    "F2": "A",
    "F3": "B",
    "F4": "B",
    "F5": "C",
    "F6": "C",
}

params = {
    "project": project,
    "debug_level": Debug.VERBOSE,
    "grid_model_name": "GridModelFine",
    "bw_name": "BW3",
    "original_facies_log_name": "FaciesEx1",
    "new_facies_log_name": "TestMergedFacies1",
    "new_code_names": new_code_names,
    "mapping_between_original_and_new": mapping,
    "realization_number": project.current_realisation,
}
create_redefined_blocked_facies_log.run(params)
