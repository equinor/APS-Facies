#!/bin/env python

from aps.toolbox import redefine_zones_in_aps_model
from aps.utils.constants.simple import Debug

print(f'Run script: {redefine_zones_in_aps_model.__file__}  ')

params = {
    'debug_level': Debug.VERBOSE,
    'model_file_name': 'examples/test_redefine_aps_zone_models.yml',
}
redefine_zones_in_aps_model.run(params)
