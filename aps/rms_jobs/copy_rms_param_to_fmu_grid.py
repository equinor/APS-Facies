#!/bin/env python
# -*- coding: utf-8 -*-
''' This module is used in FMU workflows to copy a continuous 3D parameter
    from geomodel grid to ERTBOX grid and extrapolate values that are undefined
    in ERTBOX grid. This functionality is used when the user wants to
    use FIELD keywords for petrophysical properties in ERT in Assisted History Matching.
'''

import numpy as np
import numpy.ma as ma
import roxar

from roxar import Direction
from aps.utils.constants.simple import (
    Debug, TrendType, Conform,
    ExtrapolationMethod, GridModelConstants,
)
from aps.utils.roxar.grid_model import get_zone_layer_numbering, get_zone_names
from aps.rms_jobs.copy_rms_param_trend_to_fmu_grid import (
        get_grid_model,
        check_and_get_grid_dimensions,
        assign_undefined_constant,
        fill_remaining_masked_values_within_colum,
        assign_undefined_vertical,
        assign_undefined_lateral,
        get_param_values,
        get_grid_indices,
        copy_from_geo_to_ertbox_grid)
import xml.etree.ElementTree as ET
from aps.utils.xmlUtils import getKeyword, getTextCommand, getIntCommand
from aps.utils.methods import get_debug_level, get_specification_file, SpecificationType


def read_model_file(model_file_name):
    print(f'Read model file: {model_file_name}')
    root = ET.parse(model_file_name).getroot()
    main_keyword = 'Resample'
    if root is None:
        raise ValueError(f"Missing keyword {main_keyword}")

    kwargs = dict(parentKeyword=main_keyword, modelFile=model_file_name, required=True)
    keyword = 'GridModelName'
    grid_model_name = getTextCommand(root, keyword, **kwargs)

    keyword = 'ERTBoxGridName'
    ertbox_grid_model_name = getTextCommand(root, keyword, **kwargs)

    keyword = 'ZoneParam'
    zone_param_name = getTextCommand(root, keyword, **kwargs)

    keyword = 'ExtrapolationMethod'
    valid_methods_dict = {
        0:'ZERO', 1:'MEAN',
        2:'EXTEND_LAYER_MEAN', 3:'REPEAT_LAYER_MEAN',
        4:'EXTEND', 5:'REPEAT'
    }
    method_text = getTextCommand(root, keyword, **kwargs)
    method = None
    try:
        method = int(method_text)
    except:
        values_allowed = valid_methods_dict.values()
        if method_text not in values_allowed:
            raise ValueError(
                f"Extrapolation method: {method_text} is unknown. Valid methods are:\n"
                f"{valid_methods_dict}\n"
                f"Specify either the number of the method or the name of the method."
            )
        for key, name in valid_methods_dict.items():
            if method_text == name:
                method = key
                break

    if method not in valid_methods_dict:
        raise ValueError(
            f"Extrapolation method: {method} is unknown. Valid methods are:\n"
            f"{valid_methods_dict}\n"
            f"Specify either the number of the method or the name of the method."
        )



    keyword_param = 'Parameters'
    param_names_per_zone_obj = getKeyword(root, keyword_param, **kwargs)
    param_names_per_zone = {}
    if param_names_per_zone_obj is None:
        raise ValueError(
            f'Missing keyword {keyword_param} in {model_file_name}'
        )
    else:
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
    else:
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

    keyword = 'SaveActiveParam'
    save_active_param = getIntCommand(root, keyword, minValue=0, maxValue=1, defaultValue=0, **kwargs)


    return (grid_model_name,
            ertbox_grid_model_name,
            zone_param_name,
            method,
            param_names_per_zone,
            conformity_per_zone,
            save_active_param)






def run(project, **kwargs):
    """
    Read model file and copy the specified parameters for each zone
    from geomodel to ertbox model.
    The undefined grid cell values in ertbox grid is assigned values. The method
    for assigning values to undefined grid cell values is choosen by the user,
    and the implemented methods are the same as in copy_rms_param_trend_to_fmu_grid.py.
    """

    if project.current_realisation > 0:
        raise ValueError(f'In RMS models to be used with a FMU loop in ERT,'
                         'the grid and parameters should be shared and realisation = 1'
        )
    model_file_name = get_specification_file(_type=SpecificationType.RESAMPLE, **kwargs)
    debug_level = Debug.VERBOSE

    # Read model file
    (grid_model_name, ertbox_grid_model_name,
    zone_param_name, method, param_names_dict,
    conformity_dict, save_active_param) = read_model_file(model_file_name)

    # Create
    geogrid_model, _ = get_grid_model(project, grid_model_name)
    if not zone_param_name in geogrid_model.properties:
        raise ValueError(f"The parameter {zone_param_name} does not exist in {grid_model_name} .")
    zone_param = geogrid_model.properties[zone_param_name]
    zone_code_names = zone_param.code_names

    zone_dict = {}
    for zone_number, zone_name in zone_code_names.items():
        zone_dict[zone_name] = \
        (zone_number, 0, conformity_dict[zone_number], param_names_dict[zone_number])

    print(
        f"\nCopy RMS 3D parameters from {grid_model_name} "
        f"to {ertbox_grid_model_name}"
    )
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

if __name__ == "__main__":
    kwargs ={}
    kwargs['model_file'] = "resample.xml"
    kwargs['debug_level'] = Debug.VERBOSE
    kwargs['save_active_param'] = True
    run(project,**kwargs)

