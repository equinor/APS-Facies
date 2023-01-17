#!/bin/env python
# -*- coding: utf-8 -*-

from aps.algorithms.APSModel import APSModel
from aps.utils.methods import get_specification_file, get_debug_level
from aps.utils.fmu import get_top_location
from aps.utils.constants.simple import GridModelConstants, Debug
from aps.utils.io import write_string_to_file, GlobalVariables
from warnings import warn
from pathlib import Path


def run(project, **kwargs):
    model_file = get_specification_file(**kwargs)
    aps_model = APSModel(model_file)
    export_fmu_files = kwargs.get('export_fmu_config_files', False)
    default_job_name = 'apsgui_job_name'
    job_name = kwargs.get('current_job_name', default_job_name)
    debug_level = get_debug_level(**kwargs)
    global_variables_file = "global_variables.yml"

    if export_fmu_files:
        # Use default file name equal to job name if this is defined and a default name if not
        # Job name will not exist if this script is run from APSGUI interactively, but only
        # when the running from workflow or batch
        if debug_level >= Debug.ON:
            print(f"- Write FMU and ERT related template config files:")
        if job_name is None:
            job_name = default_job_name
            print(
                '-- NOTE: A default name of the created FMU config files will be used when running interactively.\n'
                '         If you run from a workflow, the APS GUI job name will be used when creating the FMU config files.\n'
            )
        model_name = job_name + '.xml'
        att_name = job_name + '_aps_fmu_config.yml'
        prob_name = job_name + '_aps_ert_config_dist.txt'
        ert_field_name = job_name + '_aps_ert_config_fields.txt'
        aps_fmuconfig_name = job_name + '_aps_params.yml'

        relative_dir_rms_model = "rms/model"
        relative_dir_fmuconfig_input = "fmuconfig/input"
        relative_dir_fmuconfig_output = "fmuconfig/output"
        relative_dir_ert_dist = "ert/input/distributions"
        relative_dir_ert_model = "ert/model"
        global_variables_file_path = get_top_location() / relative_dir_fmuconfig_output / global_variables_file

        # APS model file
        model_file_name = get_top_location() / relative_dir_rms_model / model_name
        param_file_name = None
        param_file_name_alternative = None
        param_dir_path = get_top_location() / relative_dir_fmuconfig_input
        param_dir_path_alternative = get_top_location() / relative_dir_fmuconfig_output
        if not Path(param_dir_path).is_dir():
            if Path(param_dir_path_alternative).is_dir():
                # APS param file the user can copy into global_variables.yml file
                # for FMU projects not using global_master_config.yml file
                param_file_name_alternative = param_dir_path_alternative / att_name
            else:
                raise IOError(f"Directory {param_dir_path_alternative} does not exist.")
        else:
            # APS param file to include into global_master_config.yml file
            param_file_name = param_dir_path / aps_fmuconfig_name

        probability_distribution_file_name = get_top_location() / relative_dir_ert_dist / prob_name
        ert_field_keyword_file_name = get_top_location() / relative_dir_ert_model / ert_field_name


        # Check that using current APS job in the FMU global master config file is possible
        # e.g. that the job name is unique and not equal to any existing job name in
        # the global master config file (when comparing the job names after transforming
        # the names to upper case letters. Note the check is done on the output file global_variables.yml file
        # since this is an ordinary yaml file in contrast to the global_master_config.yml file which need special treatment.
        if not GlobalVariables.check_global_variables_yaml(global_variables_file_path, job_name):
            # Do not write ERT config files for attributes and prob dist
            param_file_name = None
            param_file_name_alternative = None
            probability_distribution_file_name = None
            warn(
                f"The job name {job_name} converted to capital letters is already used in {global_variables_file_path}. "
                "No APS parameter files are created for FMU configuration."
            )

        if debug_level >= Debug.VERBOSE:
            print(f"-- Main directory:   {get_top_location()}")
            if param_file_name:
                print(f"-- Use in FMU global_master_config.yml:  {param_file_name}")
            if param_file_name_alternative:
                print(f"-- Use in FMU global_variables.yml:      {param_file_name_alternative}")
            if probability_distribution_file_name:
                print(f"-- Use in ERT distribution config:       {probability_distribution_file_name}")
            if aps_model.fmu_mode == "FIELDS":
                print(f"-- Use in ERT main config:               {ert_field_keyword_file_name}")

        # Write model file and ERT template config files
        aps_model.write_model(
            model_file_name,
            attributes_file_name=param_file_name_alternative,
            param_file_name=param_file_name,
            probability_distribution_file_name=probability_distribution_file_name,
            current_job_name=job_name,
            debug_level=debug_level,
        )

        if aps_model.fmu_mode == "FIELDS":
            ertbox_grid_file_name = aps_model.fmu_ertbox_name + ".EGRID"
            ertbox_grid_file_path = "../../rms/output/aps/" + ertbox_grid_file_name
            grid_model = project.grid_models[aps_model.grid_model_name]
            zone_names = grid_model.properties[GridModelConstants.ZONE_NAME].code_names
            region_names = None
            if aps_model.use_regions:
                region_names = grid_model.properties[aps_model.region_parameter].code_names

            content = "-- ERT keywords related to fields used by APS.\n"
            content += f"GRID {ertbox_grid_file_path}\n"
            for key, zone_model in aps_model.sorted_zone_models.items():
                zone_number, region_number = key
                if not aps_model.isSelected(zone_number, region_number):
                    continue
                zone_name = zone_names[zone_number]
                if aps_model.use_regions:
                    region_name = region_names[region_number]
                for name in zone_model.used_gaussian_field_names:
                    fmu_field_name = 'aps_' + zone_name + '_'
                    if aps_model.use_regions:
                        fmu_field_name = fmu_field_name + region_name + '_'
                    fmu_field_name = fmu_field_name + name
                    if zone_model.hasTrendModel(name) and aps_model.fmu_use_residual_fields:
                        fmu_field_name = fmu_field_name + '_residual'
                    fmu_field_name_file = fmu_field_name + "." + aps_model.fmu_field_file_format
                    content += f"FIELD {fmu_field_name}   "
                    content += f"PARAMETER {fmu_field_name_file}   "
                    content += f"INIT_FILES:rms/output/aps/{fmu_field_name_file}   "
                    content += f"MIN:-5.5  MAX:5.5  FORWARD_INIT:True\n"

            write_string_to_file(ert_field_keyword_file_name, content, debug_level=debug_level)
