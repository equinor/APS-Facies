#!/bin/env python
from aps.toolbox.redefine_zones_in_aps_model import run as run_redefine_zones_in_aps_model
from aps.utils.methods import get_debug_level, get_specification_file, SpecificationType
from aps.utils.constants.simple import Debug, ModelFileFormat


def run(roxar=None, project=None, **kwargs):
    params = {
        "project": project,
        "model_file_name": get_specification_file(_type=SpecificationType.REMAP_ZONE_MODELS, _format=ModelFileFormat.YML, **kwargs),
        "debug_level": Debug.VERBOSE,
    }
    run_redefine_zones_in_aps_model(params)

if __name__ == '__main__':
    import roxar
    run(roxar, project, debug_level=Debug.VERBOSE)
