#!/bin/env python
# -*- coding: utf-8 -*-
"""Description:
This script is the same as run by pushing the RUN button in the APSGUI, except for the way it get the model file.
In this script the model file must exist as a file on dist prior to running and should have name APS.xml
All model parameters that are not specified within the model file but is expected to come directly from the GUI,
are specified with their default values that are used in the GUI.

The main purpose of this script is to run a job that is equvalent to running the RMS plugin job for APSGUI, but
without the need for the GUI. Main application is to test new functionality not yet made avaiable through the GUI.
"""

import json
from base64 import b64decode
from functools import wraps
from warnings import warn

from typing import Dict

from aps.algorithms.APSModel import APSModel
from aps.utils.constants.simple import (
    Debug,
    ProbabilityTolerances,
    TransformType,
    ExtrapolationMethod,
)
from aps.utils.decorators import cached
from aps.utils.fmu import get_export_location
from aps.utils.roxar._config_getters import get_debug_level
from aps.utils.roxar.migrations import Migration
from aps.utils.roxar.rms_project_data import RMSData
from aps.utils.methods import get_specification_file, get_debug_level

from aps.rms_jobs.APS_main import run as run_truncation
from aps.rms_jobs.APS_normalize_prob_cubes import run as run_normalization
from aps.rms_jobs.APS_simulate_gauss_singleprocessing import run as run_simulation
from aps.rms_jobs.updateAPSModelFromFMU import (
    run as run_update_fmu_variables_in_model_file,
)
from aps.rms_jobs.import_fields_from_disk import run as run_import_fields
from aps.rms_jobs.export_fields_to_disk import run as run_export_fields
from aps.rms_jobs.export_simbox_grid_to_disk import run as run_export_aps_grid
from aps.rms_jobs.create_simulation_grid import run as run_create_simulation_grid
from aps.rms_jobs.create_zone_parameter import run as run_create_zone_parameter
from aps.rms_jobs.check_grid_index_origin import run as run_check_grid_index_origin
from aps.rms_jobs.export_fmu_config_files import run as run_export_fmu_config_files
from aps.rms_jobs.copy_rms_param_trend_to_fmu_grid import (
    run as run_copy_rms_param_trend_to_fmu_grid,
)
from aps.utils.decorators import loggable, output_version_information
from aps.utils.fmu import fmu_aware_model_file
from aps.utils.io import create_temporary_model_file
from aps.utils.roxar.job import JobConfig, classify_job_configuration
from aps.utils.aps_config import APSConfig
import roxar.rms


def read_fmu_param_settings(fmu_dict, fmu_settings_file):
    with open(fmu_settings_file, encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines:
            if len(line) <= 1 or line == '' or line == '\n':
                continue
            words = line.split(':')
            key = words[0].strip()
            if key not in fmu_dict:
                raise KeyError(
                    f'Undefined key: {key} for fmu parameter settings in file '
                    f'{fmu_settings_file}\n '
                    f'Available keywords: {fmu_dict.keys()} '
                )
            if key in [
                'fmu_mode',
                'fmu_mode_only_param',
                'create_fmu_grid',
                'fmu_simulate_fields',
                'export_fmu_config_files',
                'write_rms_parameters_for_qc_purpose',
            ]:
                fmu_dict[key] = words[1].strip().upper() == 'TRUE'
            if key in ['max_fmu_grid_layers']:
                fmu_dict[key] = int(words[1].strip())
            if key in [
                'fmu_simulation_grid_name',
                'global_variables',
                'field_file_format',
            ]:
                fmu_dict[key] = words[1].strip()
            print(f'FMU settings: {key}:  {fmu_dict[key]}')

    return fmu_dict


def get_parameters(**kwargs):
    # Variables set by default from the startup script APS_run_workflow
    project = kwargs['project']
    debug_level = Debug.VERY_VERBOSE
    model_file = get_specification_file(**kwargs)

    # Some other default values
    max_allowed_fraction_tolerance = (
        ProbabilityTolerances.MAX_ALLOWED_FRACTION_OF_VALUES_OUTSIDE_TOLERANCE
    )
    tolerance_of_probability_normalisation = (
        ProbabilityTolerances.MAX_ALLOWED_DEVIATION_BEFORE_ERROR
    )
    transformation_type_for_grf = TransformType.EMPIRIC
    rms_param_trend_extrapolation_method = ExtrapolationMethod.EXTEND_LAYER_MEAN

    # FMU workflow related parameters
    read_fmu_settings_from_file = True

    # default settings
    fmu_dict = {}
    fmu_dict['fmu_mode'] = False
    fmu_dict['fmu_mode_only_param'] = False
    fmu_dict['create_fmu_grid'] = False
    fmu_dict['fmu_simulate_fields'] = True
    fmu_dict['max_fmu_grid_layers'] = 0
    fmu_dict['fmu_simulation_grid_name'] = None
    fmu_dict['export_fmu_config_files'] = False
    fmu_dict['field_file_format'] = 'roff'
    fmu_dict['write_rms_parameters_for_qc_purpose'] = False
    fmu_dict['use_aps_config_file'] = True
    fmu_dict['create_aps_config_file'] = True

    # Ensure that existing config file is read and make one if non exists
    APSConfig.init(
        project,
        use_available_config_file=fmu_dict['use_aps_config_file'],
        must_read_existing_config_file=True,
    )

    if read_fmu_settings_from_file:
        fmu_settings_file = APSConfig.rms_model_dir() + '/' + 'APS_fmu_settings.txt'
        fmu_dict = read_fmu_param_settings(fmu_dict, fmu_settings_file)

    # APS model instance with default check
    print(f'APS model file: {model_file} ')
    aps_model = APSModel(model_file, debug_level=debug_level)

    # Check that zone parameter exists and if not, then create it
    aps_model.check_or_create_zone_parameter(project, debug_level=debug_level)

    # Keep only models for (zone,region) pairs with active cells
    aps_model.check_active_cells(project, debug_level=debug_level)
    global_variables_file = APSConfig.global_variables_file()

    return {
        'project': project,
        'model_file': model_file,
        'output_model_file': model_file,
        'global_variables': global_variables_file,
        'max_fmu_grid_layers': int(fmu_dict['max_fmu_grid_layers']),
        'fmu_mode': bool(fmu_dict['fmu_mode']),
        'fmu_mode_only_param': bool(fmu_dict['fmu_mode_only_param']),
        'fmu_simulate_fields': bool(fmu_dict['fmu_simulate_fields']),
        'fmu_simulation_grid_name': fmu_dict['fmu_simulation_grid_name'],
        'rms_grid_name': aps_model.grid_model_name,
        'fmu_export_location': get_export_location(),
        'aps_model': aps_model,
        'use_constant_probabilities': aps_model.use_constant_probability,
        'workflow_name': roxar.rms.get_running_workflow_name(),
        'seed_log_file': None,
        'write_rms_parameters_for_qc_purpose': fmu_dict[
            'write_rms_parameters_for_qc_purpose'
        ],
        'debug_level': aps_model.log_setting,
        'max_allowed_fraction_of_values_outside_tolerance': max_allowed_fraction_tolerance,
        'tolerance_of_probability_normalisation': tolerance_of_probability_normalisation,
        'field_file_format': fmu_dict['field_file_format'],
        'transform_type_grf': transformation_type_for_grf,
        'current_job_name': roxar.rms.get_running_job_name(),
        'export_fmu_config_files': fmu_dict['export_fmu_config_files'],
        'extrapolation_method': rms_param_trend_extrapolation_method,
        'create_fmu_grid': bool(fmu_dict['create_fmu_grid']),
    }


def run(**kwargs_input):
    kwargs = get_parameters(**kwargs_input)
    project = kwargs['project']
    debug_level = kwargs['debug_level']
    model_file = kwargs['model_file']
    aps_model = kwargs['aps_model']

    aps_model.write_model(model_file)
    if kwargs['export_fmu_config_files']:
        run_export_fmu_config_files(**kwargs)
    if kwargs['fmu_mode'] and kwargs['create_fmu_grid']:
        run_create_simulation_grid(**kwargs)
    run_check_grid_index_origin(**kwargs)
    run_create_zone_parameter(**kwargs)
    if not kwargs['use_constant_probabilities']:
        run_normalization(**kwargs)
    if kwargs['fmu_mode'] or kwargs['fmu_mode_only_param']:
        run_update_fmu_variables_in_model_file(**kwargs)
    if kwargs['fmu_mode']:
        run_copy_rms_param_trend_to_fmu_grid(**kwargs)
    with fmu_aware_model_file(**kwargs):
        if kwargs['fmu_simulate_fields']:
            run_simulation(**kwargs)
            if kwargs['fmu_mode']:
                run_export_aps_grid(**kwargs)
                run_export_fields(**kwargs)

                run_import_fields(
                    load_dir=kwargs['fmu_export_location'],
                    geo_grid_name=kwargs['rms_grid_name'],
                    **kwargs,
                )
        else:
            run_import_fields(geo_grid_name=kwargs['rms_grid_name'], **kwargs)

    run_truncation(**kwargs)
    print('Finished')


# if __name__ == "__main__":
#    model_file = "APS.xml"
#    run(project, model_file)
