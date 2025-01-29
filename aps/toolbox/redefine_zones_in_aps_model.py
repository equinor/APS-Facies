#!/bin/env python
"""
Description:
    This script can be used to update an APS model if the original grid model is changed such that the zones are redefined.
    A mapping between the new and old zonation is defined and the updated APS model will use existing APS model specification
    for selected zones in the original APS model in the updated APS model.

Input:  A dictionary with specification of the remapping or alternatively specified as a model file in YAML format.

Output: New version of the APS model file.

"""

import copy

from pathlib import Path
from aps.algorithms.APSModel import APSModel
from aps.utils.constants.simple import Debug
from aps.utils.methods import check_missing_keywords_list
from aps.utils.ymlUtils import get_text_value, get_dict, readYml


def run(params):
    """
    Make new APS model file adapted to new version of the grid model based on the original APS model file.
    Note that neither the new or the old APS model can use regions. This script assume region_number = 0
    Usage alternatives:
    - Specify a dictionary with name of model file containing all input information. Example 1.
    - Specify a dictionary with all input information. Example 2.

    Example 1:

    from aps.toolbox import redefine_zones_in_aps_model
    from aps.utils.constants.simple import Debug


    params = {
        "debug_level": Debug.VERBOSE,
        "model_file_name": "examples/test_redefine_aps_zone_models.yml",
    }
    redefine_zones_in_aps_model.run(params)

    Example 2:

    from aps.toolbox import redefine_zones_in_aps_model
    from aps.utils.constants.simple import Debug
    new_zones = {
        1: "Zone_A",
        2: "Zone_B",
        3: "Zone_C2",
        4: "Zone_C1",
        5: "Zone_D",
    }
    old_zones = {
        1: "Zone_A3_orig",
        2: "Zone_A2_orig",
        3: "Zone_A1_orig",
        4: "Zone_B2_orig",
        5: "Zone_B1_orig",
        6: "Zone_C_orig",
        7: "Zone_D_orig",
    }

    # For each new zone, specify a list of which old zones to merge together.
    # The first old zone in the list is used as the APS model for the new zone.
    # A requirement is that the old zones in the list are neighbours so that they can be merged.
    # A split of old zone into multipl new zones is done by specifying the same old zone name
    # for each of the new zones.
    zone_mapping = {
        "Zone_A":  ["Zone_A3_orig", "Zone_A2_orig", "Zone_A1_orig"],
        "Zone_B":  ["Zone_B1_orig", "Zone_B2_orig"],
        "Zone_C2": ["Zone_C_orig"],
        "Zone_C1": ["Zone_C_orig"],
        "Zone_D":  ["Zone_D_orig"],
    }

    params = {
        "debug_level": Debug.VERBOSE,   # Optional
        "input_aps_model_file": "examples/APS_original_zones.xml",
        "output_aps_model_file": "APS_remapped.xml",
        "grid_model_for_output_aps_model": "Test_remap_modified",  # Optional
        "new_zones": new_zones,
        "old_zones": old_zones,
        "zone_mapping": zone_mapping,
    }
    redefine_zones_in_aps_model.run(params)

    """
    model_file_name = params.get('model_file_name', None)
    debug_level = params.get('debug_level', Debug.OFF)
    grid_model_name_for_output_model = params.get('output_grid_model_name', None)
    if model_file_name:
        params = read_model_file(model_file_name)
        params['debug_level'] = debug_level
        params['output_grid_model_name'] = grid_model_name_for_output_model

    required_kw = [
        'input_aps_model_file',
        'output_aps_model_file',
        'new_zones',
        'old_zones',
        'zone_mapping',
    ]
    check_missing_keywords_list(params, required_kw)

    if debug_level >= Debug.VERBOSE:
        print(f'-- Input APS model file  : {params["input_aps_model_file"]}')
        print(f'-- Output APS model file : {params["output_aps_model_file"]}')
        print('-- New zones: ')
        for key, item in params['new_zones'].items():
            print(f'   {key}  {item}')
        print(f'-- Old zones: ')
        for key, item in params['old_zones'].items():
            print(f'   {key}  {item}')
        print(f'-- Zone mapping          : ')
        for key, zone_list in params['zone_mapping'].items():
            print(f'   {key}  {zone_list}')
        if grid_model_name_for_output_model is not None:
            print(
                f'-- Grid model for output APS model:  {grid_model_name_for_output_model} '
            )
        else:
            print(
                f'-- Grid model for output APS model:  The same as for input APS model.'
            )
        print(' ')

    redefine_zones(params)


def read_model_file(model_file_name):
    # YAML file format
    model_file = Path(model_file_name)
    extension = model_file.suffix.lower().strip('.')
    if extension in ['yaml', 'yml']:
        return _read_model_file_yml(model_file_name)
    else:
        raise ValueError(
            f"Model file name: {model_file_name}  must be in YAML format with file extension 'yml' or 'yaml' "
        )


def _read_model_file_yml(model_file_name):
    # Read model file and overwrite model parameters
    print(f'Read model file: {model_file_name}  ')
    assert model_file_name
    spec_all = readYml(model_file_name)

    parent_kw = 'RemapZoneModels'
    spec = spec_all[parent_kw] if parent_kw in spec_all else None
    if spec is None:
        raise ValueError(f'Missing keyword: {parent_kw} ')

    input_aps_model_file_name = get_text_value(spec, parent_kw, 'InputAPSModelFile')
    output_aps_model_file_name = get_text_value(spec, parent_kw, 'OutputAPSModelFile')
    output_grid_model_name = get_text_value(
        spec, parent_kw, 'OutputGridModel', default=''
    )
    new_zones_dict = get_dict(spec, parent_kw, 'NewZones')
    old_zones_dict = get_dict(spec, parent_kw, 'OldZones')
    zone_mapping_dict_input = get_dict(spec, parent_kw, 'ZoneMapping')
    zone_mapping_dict = {}
    for key, value in zone_mapping_dict_input.items():
        list_of_zone_names = value.split()
        zone_mapping_dict[key] = list_of_zone_names

    model_param_dict = {
        'input_aps_model_file': input_aps_model_file_name,
        'output_aps_model_file': output_aps_model_file_name,
        'output_grid_model_name': output_grid_model_name,
        'new_zones': new_zones_dict,
        'old_zones': old_zones_dict,
        'zone_mapping': zone_mapping_dict,
    }
    return model_param_dict


def redefine_zones(params):
    debug_level = params['debug_level']
    aps_input_model = APSModel(params['input_aps_model_file'])
    grid_model_name_for_input_model = aps_input_model.grid_model_name

    # Start by making a copy
    aps_output_model = APSModel(params['input_aps_model_file'])
    if (
        'output_grid_model_name' in params
        and params['output_grid_model_name'] is not None
        and len(params['output_grid_model_name']) > 0
    ):
        grid_model_name_for_output_model = params['output_grid_model_name']
    else:
        grid_model_name_for_output_model = grid_model_name_for_input_model

    # Get the dict of original zone models Key is (zone_number, region_number) and value is a APSZoneModel
    original_zone_models = aps_input_model.sorted_zone_models

    zone_mapping = params['zone_mapping']
    new_zones = params['new_zones']
    old_zones = params['old_zones']

    # Unique zone_names so invert the dict
    orig_zones_per_name = {name: zone_number for zone_number, name in old_zones.items()}

    # The remapping
    new_zone_models = {}
    for zone_number, zone_name in new_zones.items():
        orig_zones = zone_mapping[zone_name]
        first_orig_zone_name = orig_zones[0]
        orig_zone_number = orig_zones_per_name[first_orig_zone_name]
        key = (orig_zone_number, 0)
        zone_model = copy.deepcopy(original_zone_models[key])

        zone_model.zone_number = zone_number
        zone_model.region_number = 0
        newkey = (zone_number, 0)
        new_zone_models[newkey] = zone_model
        if debug_level >= Debug.VERBOSE:
            print(
                f'-- New zone: {zone_number} {zone_name}  use old zone: {orig_zone_number} {first_orig_zone_name} '
            )

    aps_output_model.set_zone_models(new_zone_models)
    aps_output_model.grid_model_name = grid_model_name_for_output_model
    aps_output_model.fmu_mode = 'OFF'

    print(f'Write file: {params["output_aps_model_file"]}')
    aps_output_model.write_model(
        params['output_aps_model_file'], debug_level=debug_level
    )
