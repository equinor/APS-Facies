#!/bin/env python
# -*- coding: utf-8 -*-
''' This module is used in FMU workflows to copy a continuous 3D parameter
    from geomodel grid to ERTBOX grid and extrapolate values that are undefined
    in ERTBOX grid. This functionality is used when the user wants to
    use FIELD keywords for petrophysical properties in ERT in Assisted History Matching.
'''
import roxar
import xml.etree.ElementTree as ET

from pathlib import Path
from aps.utils.constants.simple import (
    Debug, Conform, ExtrapolationMethod,
)
from aps.rms_jobs.copy_rms_param_trend_to_fmu_grid import (
        get_grid_model,
        copy_from_geo_to_ertbox_grid)

from aps.utils.ymlUtils import get_text_value, get_dict, get_bool_value, readYml
from aps.utils.methods import check_missing_keywords_list
from aps.utils.roxar.grid_model import get_zone_layer_numbering
from aps.utils.roxar.generalFunctionsUsingRoxAPI import  set_continuous_3d_parameter_values_in_zone_region

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
# NOTE: In the example below the geo grid has 6 zones while Ertbox grid has 1 zone
#       The parameter names for geogrid is the same for each zone since it is a multizone grid
#       and zone number + parameter name uniquely identify the field parameter.
#       The key (integer numbers) in the two dicts refer to zone number in geogrid
#       so for zone number 1 the Perm1 and Poro1 values in the Ertbox grid corresponds to
#       the Perm and Poro values for zone number 1 in the geogrid.
#
#       When copying from geo to Ertbox grid there can be grid cells in Ertbox that does not
#       correspond to any active grid cell value in the geo grid. To fill in some values for
#       those grid cells, an extrapolation method is used. The reason for extrapolating is to
#       avoid having undefined values in Ertbox since all cell values are used in ERT when updating
#       field values. It is an advantage to avoid unrealistic values in ERT ensemble vector due to the 
#       calculation of updated (analysis step in ERT) ensemble vectors to avoid making linear combinations
#       of values for grid cells that may correspond to active grid cell in geogrid in one realization,
#       but not for another realisation due to 3D grids varying from realisation to realisation.
#
#       When copying from Ertbox grid to geo grid, all grid cells in specified zones in the geo grid
#       will correspond to a value in the Ertbox grid.
params ={
    "project": project,
    "debug_level": Debug.ON,
    "Mode": "from_geo_to_ertbox",
    "GeoGridParameters": {
        1: ["Perm", "Poro"],
        2: ["Perm", "Poro"],
        3: ["Perm", "Poro"],
        4: ["Perm", "Poro"],
        5: ["Perm", "Poro"],
        6: ["Perm", "Poro"],
    },
    "ErtboxParameters": {
        1: ["Perm1", "Poro1"],
        2: ["Perm2", "Poro2"],
        3: ["Perm3", "Poro3"],
        4: ["Perm4", "Poro4"],
        5: ["Perm5", "Poro5"],
        6: ["Perm6", "Poro6"],
    },
    "Conformity": {
        1: "TopConform",
        2: "Proportional",
        3: "BaseConform",
        4: "TopConform",
        5: "BaseConform",
        6: "BaseConform",
    },

    "GridModelName": "GridModelFine",
    "ZoneParam": "Zone",
    "ERTBoxGridName": "ERTBOX",
    "ExtrapolationMethod": "repeat",
    "SaveActiveParam": True,
}
copy_rms_param_to_ertbox_grid.run(params)

    """
    project = params['project']
    model_file_name = params.get('model_file_name',None)
    if model_file_name is not None:
        # Read model file
        params = read_model_file(model_file_name, debug_level=params.get('debug_level', Debug.OFF))
    # Check that necessary params are specified
    required_kw_list = [
        "Mode",
        "GridModelName", "ERTBoxGridName",
        "ZoneParam", "Conformity",
    ]
    check_missing_keywords_list(params, required_kw_list)
    mode = params['Mode']

    if mode == 'from_geo_to_ertbox':
        # The names of the parameters in ertbox is automatically set to
        # <zone_name>_<param_name_from_geomodel> since it follows
        # the standard used in APS and therefore no need to specify
        # parameter names in ertbox.
        required_kw_list.append("ExtrapolationMethod")
        required_kw_list.append("GeoGridParameters")
        check_missing_keywords_list(params, required_kw_list)
        from_geogrid_to_ertbox(project, params)
    elif mode == 'from_ertbox_to_geo':
        # The name both in ertbox and in geogrid is required
        # here since no standard naming convention is required here.
        required_kw_list.append('ErtboxParameters')
        required_kw_list.append("GeoGridParameters")
        check_missing_keywords_list(params, required_kw_list)
        from_ertbox_to_geogrid(project, params)


def from_geogrid_to_ertbox(project, params):
    # Assign user specified parameters
    grid_model_name = params['GridModelName']
    zone_param_name = params['ZoneParam']
    ertbox_grid_model_name = params['ERTBoxGridName']
    method = params.get('ExtrapolationMethod', 'extend_layer_mean')
    param_names_geogrid_dict = params['GeoGridParameters']

    conformity_dict_input = params['Conformity']
    debug_level = params['debug_level']

    # Optional parameter
    save_active_param = params.get('SaveActiveParam', False)

    # Some conversion
    conformity_dict = {}
    for znr, conform_text in conformity_dict_input.items():
        conformity_dict[znr] = Conform(conform_text)
    method = ExtrapolationMethod(method)


    geogrid_model, geogrid3D = get_grid_model(project, grid_model_name)
    if not zone_param_name in geogrid_model.properties:
        raise ValueError(f"The parameter {zone_param_name} does not exist in {grid_model_name} .")
    zone_param = geogrid_model.properties[zone_param_name]
    zone_code_names = zone_param.code_names

    _, ertboxgrid3D = get_grid_model(project, ertbox_grid_model_name)

    # Check grid index origin
    geogrid_handedness = geogrid3D.grid_indexer.ijk_handedness
    ertboxgrid_handedness = ertboxgrid3D.grid_indexer.ijk_handedness

    if geogrid_handedness != ertboxgrid_handedness:
        raise ValueError(
            f"Grid model for geomodel '{grid_model_name}' and "
            f"grid model for ERTBOX grid '{ertbox_grid_model_name}'  "
            "have different grid index origin.\n"
            "Use 'Eclipse grid standard' (upper left corner) as "
            "common grid index origin (right-handed grid) in FMU projects using ERT."
        )
    if ertboxgrid_handedness != roxar.Direction.right:
        print("WARNING: ERTBOX grid should have 'Eclipse grid index origin'.")
        print("         Use the grid index origin job in RMS to set this.")


    zone_dict = {}
    zone_names_used =[] 
    if debug_level >= Debug.ON:
        print(
            f"\nCopy RMS 3D parameters from {grid_model_name} "
            f"to {ertbox_grid_model_name} for zones:"
        )
    for zone_number, zone_name in zone_code_names.items():
        if zone_number in param_names_geogrid_dict and zone_number in conformity_dict:
            zone_dict[zone_name] = \
                (zone_number, 0, conformity_dict[zone_number], param_names_geogrid_dict[zone_number])
            zone_names_used.append(zone_name)
            if debug_level >= Debug.ON:
                print(f"  {zone_name}: {param_names_geogrid_dict[zone_number]} ")

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
        print(f"- Finished copy rms parameters from {grid_model_name} to {ertbox_grid_model_name} ")


def from_ertbox_to_geogrid(project, params):
    # Assign user specified parameters
    grid_model_name = params['GridModelName']
    ertbox_grid_model_name = params['ERTBoxGridName']
    param_names_geogrid_dict = params['GeoGridParameters']
    param_names_ertbox_dict = params['ErtboxParameters']
    conformity_dict_input = params['Conformity']
    debug_level = params['debug_level']

    # Some conversion
    conformity_dict = {}
    for znr, conform_text in conformity_dict_input.items():
        conformity_dict[znr] = Conform(conform_text)


    # Create
    geogrid_model, grid3D = get_grid_model(project, grid_model_name)
    ertbox_grid_model, ertbox3D = get_grid_model(project, ertbox_grid_model_name)

    # Check grid index origin
    geogrid_handedness = grid3D.grid_indexer.ijk_handedness
    ertboxgrid_handedness = ertbox3D.grid_indexer.ijk_handedness
    if geogrid_handedness != ertboxgrid_handedness:
        raise ValueError(
            f"Grid model for geomodel '{grid_model_name}' and "
            f"grid model for ERTBOX grid '{ertbox_grid_model_name}'  "
            "have different grid index origin.\n"
            "Use 'Eclipse grid standard' (upper left corner) as "
            "common grid index origin (right-handed grid) in FMU projects using ERT."
        )
    if ertboxgrid_handedness != roxar.Direction.right:
        print("WARNING: ERTBOX grid should have 'Eclipse grid index origin'.")
        print("         Use the grid index origin job in RMS to set this.")



    number_of_layers_per_zone_in_geo_grid, _, _ = get_zone_layer_numbering(grid3D)
    nx, ny, nz_ertbox = ertbox3D.simbox_indexer.dimensions
    for zone_number in param_names_geogrid_dict:
        zone_index = zone_number - 1
        conformity = conformity_dict[zone_number]
        param_names_geogrid_list = param_names_geogrid_dict[zone_number]
        param_names_ertbox_list = param_names_ertbox_dict[zone_number]
        if debug_level >= Debug.VERBOSE:
            print(f"-- Zone number:  {zone_number}")
            print(f"-- Conformity: {conformity}  ")
            print(f"-- Copy from:  {param_names_ertbox_list}")
            print(f"-- Copy to:    {param_names_geogrid_list}")
        nz_for_zone = number_of_layers_per_zone_in_geo_grid[zone_index]
        parameter_names_geo_grid = []
        parameter_values_geo_grid = []

        for index, param_name in enumerate(param_names_ertbox_list):
            try:
                rms_property = ertbox_grid_model.properties[param_name]
            except KeyError:
                raise ValueError(f"The parameter: {param_name} does not exist or is empty for grid model: {ertbox_grid_model_name}")
            values = rms_property.get_values()
            field_values = values.reshape(nx, ny, nz_ertbox)
            if conformity in [Conform.Proportional, Conform.TopConform]:
                # Only get the top n cells of field_values
                field_values = field_values[:, :, :nz_for_zone]
            elif conformity in [Conform.BaseConform]:
                # Get the bottom n cells of field_values
                field_values = field_values[:, :, -nz_for_zone:]
            else:
                raise NotImplementedError(f'{conformity.value} is not supported')

            # Field names and corresponding values to update the geo grid with
            param_name_geo = param_names_geogrid_list[index]
            parameter_names_geo_grid.append(param_name_geo)
            parameter_values_geo_grid.append(field_values)

        # Update geogrid. Has often multiple zones
        if debug_level >= Debug.VERY_VERBOSE:
            for name in  parameter_names_geo_grid:
                print(f'--- Update parameter {name} for zone number {zone_number} in {geogrid_model}')

        set_continuous_3d_parameter_values_in_zone_region(
            geogrid_model,
            parameter_names_geo_grid,
            parameter_values_geo_grid,
            zone_number,
            realisation_number=project.current_realisation,
            is_shared=geogrid_model.shared,
            switch_handedness=True,
        )
    if debug_level >= Debug.ON:
        print(f"- Finished copy rms parameters from {ertbox_grid_model_name}  to {grid_model_name}.")

def read_model_file(model_file_name, debug_level=Debug.OFF):
    # Check suffix of file for file type
    model_file = Path(model_file_name)
    suffix = model_file.suffix.lower().strip('.')
    if suffix in ['yaml', 'yml']:
        param_dict = _read_model_file_yml(model_file_name, debug_level=debug_level)
    elif suffix == 'xml':
            raise ValueError(f"No xml file format implemented for {__name__}   ")
    else:
        raise ValueError(f"Model file name: {model_file_name}  must be 'yml' format")
    return param_dict

def _read_model_file_yml(model_file_name, debug_level=Debug.OFF):
    print(f'Read model file: {model_file_name}')
    spec_all = readYml(model_file_name)

    kw_parent = 'Resample'
    spec = spec_all[kw_parent] if kw_parent in spec_all else None
    if spec is None:
        raise ValueError(f"Missing keyword: {kw_parent} ")
    valid_strings = ['from_geo_to_ertbox', 'from_ertbox_to_geo']
    mode = get_text_value(spec, kw_parent, 'Mode', default='from_geo_to_ertbox')
    if mode not in valid_strings:
        raise ValueError(f"The keyword 'Mode' must be followed by one of the keywords {valid_strings}  ") 
    grid_model_name = get_text_value(spec, kw_parent, 'GridModelName')
    ertbox_grid_model_name = get_text_value(spec, kw_parent, 'ERTBoxGridName')
    zone_param_name = get_text_value(spec, kw_parent, 'ZoneParam')
    method = None
    param_names_geo_per_zone = None
    param_names_ertbox_per_zone = None
    if mode == 'from_geo_to_ertbox':
        method_text = get_text_value(spec, kw_parent, 'ExtrapolationMethod')
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

    param_list_geogrid_dict = get_dict(spec, kw_parent, 'GeoGridParameters')
    param_names_geo_per_zone = {}
    for key in param_list_geogrid_dict:
        text = str(param_list_geogrid_dict[key])
        param_names_geo_per_zone[key] = text.split()

    if mode == 'from_ertbox_to_geo':
        param_list_ertbox_dict = get_dict(spec, kw_parent, 'ErtboxParameters')
        param_names_ertbox_per_zone = {}
        for key in param_list_ertbox_dict:
            text = str(param_list_ertbox_dict[key])
            param_names_ertbox_per_zone[key] = text.split()

    conformity_text =  get_dict(spec, kw_parent, 'Conformity')
    valid_conformities_list = ["Proportional", "TopConform", "BaseConform"]
    conformity_per_zone = {}
    for key in conformity_text:
        text_value = conformity_text[key]
        if text_value not in valid_conformities_list:
            raise ValueError(
                f"Unknown comformity: {text_value}\n"
                f"Valid specifications are: {valid_conformities_list} "
            )
        conformity_per_zone[key] = Conform(text_value)


    save_active_param = get_bool_value(spec, 'SaveActiveParam', False)

    param_dict ={
        'Mode': mode,
        'GridModelName': grid_model_name,
        'ERTBoxGridName':  ertbox_grid_model_name,
        'ZoneParam':    zone_param_name,
        'ExtrapolationMethod':    method,
        'GeoGridParameters':  param_names_geo_per_zone,
        'ErtboxParameters':  param_names_ertbox_per_zone,
        'Conformity':    conformity_per_zone,
        'SaveActiveParam': save_active_param,
        'debug_level': debug_level,
    }
    return param_dict