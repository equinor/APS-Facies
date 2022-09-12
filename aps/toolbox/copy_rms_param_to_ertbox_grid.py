#!/bin/env python
# -*- coding: utf-8 -*-
''' This module is used in FMU workflows to copy a continuous 3D parameter
    from geomodel grid to ERTBOX grid and extrapolate values that are undefined
    in ERTBOX grid. This functionality is used when the user wants to
    use FIELD keywords for petrophysical properties in ERT in Assisted History Matching.
'''

import xml.etree.ElementTree as ET
from aps.utils.constants.simple import (
    Debug, Conform, ExtrapolationMethod,
)
from aps.rms_jobs.copy_rms_param_trend_to_fmu_grid import (
        get_grid_model,
        copy_from_geo_to_ertbox_grid)
from aps.utils.xmlUtils import getKeyword, getTextCommand, getBoolCommand
from aps.utils.methods import check_missing_keywords_list


def run(params):
    """
        Copy 3D RMS parameters from geogrid to ERTBOX grid and optionally extrapolate and fill all ERTBOX grid cells.
        Usage alternatives:
        - Specify input as dictionary with model file containing all input. See example 1.
        - Specify input as dictionary witl all input. See example 2.

Example 1:

from aps.toolbox import copy_rms_param_to_ertbox_grid
from aps.utils.constants.simple import Debug

params ={
    "project": project,
    "model_file_name": "examples/resample_properties_to_ertbox.xml",
    "debug_level": Debug.VERBOSE,
}
copy_rms_param_to_ertbox_grid.run(params)


Example 2:

from aps.toolbox import copy_rms_param_to_ertbox_grid
from aps.utils.constants.simple import Debug

params ={
    "project": project,
    "debug_level": Debug.ON,
    "parameter_names": {
        1: ["Perm", "Poro"],
        2: ["Perm", "Poro"],
        3: ["Perm", "Poro"],
        4: ["Perm", "Poro"],
        5: ["Perm", "Poro"],
        6: ["Perm", "Poro"],
    },
    "conformity": {
        1: "TopConform",
        2: "Proportional",
        3: "BaseConform",
        4: "TopConform",
        5: "BaseConform",
        6: "BaseConform",
    },
    "grid_model_name": "GridModelFine",
    "zone_param_name": "Zone",
    "ertbox_grid_name": "ERTBOX",
    "extrapolation_method": "repeat",
    "save_active": True,
}
copy_rms_param_to_ertbox_grid.run(params)

    """
    project = params['project']
    model_file_name = params.get('model_file_name',None)
    debug_level = params.get('debug_level', Debug.OFF)

    if model_file_name is not None:
        # Read model file
        (grid_model_name, ertbox_grid_model_name,
        zone_param_name, method, param_names_dict,
        conformity_dict, save_active_param) = _read_model_file(model_file_name)
    else:
        # Check that necessary params are specified
        required_kw_list = [
            "grid_model_name", "ertbox_grid_name",
            "zone_param_name", "parameter_names",
            "conformity", "extrapolation_method"
        ]
        check_missing_keywords_list(params, required_kw_list)

        # Assign user specified parameters
        grid_model_name = params['grid_model_name']
        zone_param_name = params['zone_param_name']
        ertbox_grid_model_name = params['ertbox_grid_name']
        method = params['extrapolation_method']
        param_names_dict = params['parameter_names']
        conformity_dict_input = params['conformity']

        # Optional parameter
        kw = 'save_active'
        save_active_param = params.get('save_active', False)

        # Some conversion
        conformity_dict = {}
        for znr, conform_text in conformity_dict_input.items():
            conformity_dict[znr] = Conform(conform_text)
        method = ExtrapolationMethod(method)

    # Create
    geogrid_model, _ = get_grid_model(project, grid_model_name)
    if not zone_param_name in geogrid_model.properties:
        raise ValueError(f"The parameter {zone_param_name} does not exist in {grid_model_name} .")
    zone_param = geogrid_model.properties[zone_param_name]
    zone_code_names = zone_param.code_names

    zone_dict = {}
    zone_names_used =[] 
    if debug_level >= Debug.ON:
        print(
            f"\nCopy RMS 3D parameters from {grid_model_name} "
            f"to {ertbox_grid_model_name} for zones:"
        )
    for zone_number, zone_name in zone_code_names.items():
        if zone_number in param_names_dict and zone_number in conformity_dict:
            zone_dict[zone_name] = \
                (zone_number, 0, conformity_dict[zone_number], param_names_dict[zone_number])
            zone_names_used.append(zone_name)
            if debug_level >= Debug.ON:
                print(f"  {zone_name}: {param_names_dict[zone_number]} ")

    copy_from_geo_to_ertbox_grid(
            project,
            grid_model_name,
            ertbox_grid_model_name,
            zone_dict,
            method,
            debug_level,
            save_active_param=save_active_param,
            normalize_trend=False,
            not_aps_workflow=True)

    if debug_level >= Debug.ON:
        print(f"- Finished copy rms parameters to {ertbox_grid_model_name} ")


def _read_model_file(model_file_name):
    print(f'Read model file: {model_file_name}')
    root = ET.parse(model_file_name).getroot()
    main_keyword = 'Resample'
    if root is None:
        raise ValueError(f"Missing keyword {main_keyword}")

    kwargs = dict(parentKeyword=main_keyword, modelFile=model_file_name, required=True)
    grid_model_name = getTextCommand(root, 'GridModelName', **kwargs)
    ertbox_grid_model_name = getTextCommand(root, 'ERTBoxGridName', **kwargs)
    zone_param_name = getTextCommand(root, 'ZoneParam', **kwargs)
    method_text = getTextCommand(root, 'ExtrapolationMethod', **kwargs)
    method = None
    valid_methods = [
        ExtrapolationMethod.ZERO.value,
        ExtrapolationMethod.MEAN.value,
        ExtrapolationMethod.EXTEND_LAYER_MEAN.value,
        ExtrapolationMethod.REPEAT_LAYER_MEAN.value,
        ExtrapolationMethod.EXTEND.value,
        ExtrapolationMethod.REPEAT.value,
    ]
    if method_text not in valid_methods:
        raise ValueError(
            f"Extrapolation method: {method_text} is unknown. Valid methods are:\n"
            f"{valid_methods}"
        )
    method = ExtrapolationMethod(method_text)

    keyword_param = 'Parameters'
    param_names_per_zone_obj = getKeyword(root, keyword_param, **kwargs)
    param_names_per_zone = {}
    if param_names_per_zone_obj is None:
        raise ValueError(
            f'Missing keyword {keyword_param} in {model_file_name}'
        )
    for zone_obj in param_names_per_zone_obj.findall('Zone'):
        zone_number = int(zone_obj.get('number'))
        text = zone_obj.text
        words = text.split()
        param_names = []
        for param_name in words:
            param_names.append(param_name)
            param_names_per_zone[zone_number] = param_names

    keyword_param = 'Conformity'
    valid_conformities_list = ["Proportional", "TopConform", "BaseConform"]
    conformity_per_zone_obj = getKeyword(root, keyword_param, **kwargs)
    conformity_per_zone = {}
    if conformity_per_zone_obj is None:
        raise ValueError(
            f'Missing keyword {keyword_param} in {model_file_name}'
        )

    for zone_obj in conformity_per_zone_obj.findall('Zone'):
        zone_number = int(zone_obj.get('number'))
        text = zone_obj.text
        text = text.strip()
        if text == "TopConform":
            conformity_type = Conform.TopConform
        elif text == "BaseConform":
            conformity_type = Conform.BaseConform
        elif text == "Proportional":
            conformity_type = Conform.Proportional
        else:
            raise ValueError(
                f"Unknown comformity: {text}\n"
                f"Valid specifications are: {valid_conformities_list} "
            )
        conformity_per_zone[zone_number] = conformity_type

    save_active_param = getBoolCommand(root, 'SaveActiveParam', required=False)


    return (grid_model_name,
            ertbox_grid_model_name,
            zone_param_name,
            method,
            param_names_per_zone,
            conformity_per_zone,
            save_active_param)

