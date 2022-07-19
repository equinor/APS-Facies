#!/bin/env python
# -*- coding: utf-8 -*-
''' This module is used in FMU workflows to copy a continuous 3D parameter
    from geomodel grid to ERTBOX grid and extrapolate values that are undefined
    in ERTBOX grid. This functionality is used when the user wants to
    use FIELD keywords for petrophysical properties in ERT in Assisted History Matching.
'''

from aps.utils.constants.simple import (
    Debug, Conform, ExtrapolationMethod,
)
from aps.rms_jobs.copy_rms_param_trend_to_fmu_grid import (
        get_grid_model,
        copy_from_geo_to_ertbox_grid)
import xml.etree.ElementTree as ET
from aps.utils.xmlUtils import getKeyword, getTextCommand, getBoolCommand
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
    method_text = getTextCommand(root, keyword, **kwargs)
    method = None
    valid_methods = [
        ExtrapolationMethod.ZERO.value,
        ExtrapolationMethod.MEAN.value,
        ExtrapolationMethod.EXTEND_LAYER_MEAN.value,
        ExtrapolationMethod.REPEAT_LAYER_MEAN.value,
        ExtrapolationMethod.EXTEND.value,
        ExtrapolationMethod.REPEAT.value,
    ]
    if method_text in valid_methods:
        method = ExtrapolationMethod(method_text)
    else:
        raise ValueError(
            f"Extrapolation method: {method_text} is unknown. Valid methods are:\n"
            f"{valid_methods}"
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
    save_active_param = getBoolCommand(root, keyword, required=False)


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
    debug_level = get_debug_level(**kwargs)

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
    zone_names_used =[] 
    for zone_number, zone_name in zone_code_names.items():
        if zone_number in param_names_dict and zone_number in conformity_dict:
            zone_dict[zone_name] = \
            (zone_number, 0, conformity_dict[zone_number], param_names_dict[zone_number])
            zone_names_used.append(zone_name)
    print(
        f"\nCopy RMS 3D parameters from {grid_model_name} "
        f"to {ertbox_grid_model_name} for zones: {zone_names_used} "
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

