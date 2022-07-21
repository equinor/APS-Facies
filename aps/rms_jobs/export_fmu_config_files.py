#!/bin/env python
# -*- coding: utf-8 -*-

from aps.algorithms.APSModel import APSModel
from aps.utils.methods import get_specification_file, get_debug_level
from aps.utils.fmu import get_top_location
from aps.utils.constants.simple import GridModelConstants
from aps.utils.io import write_string_to_file
from warnings import warn


def run(project, **kwargs):
    model_file = get_specification_file(**kwargs)
    aps_model = APSModel(model_file)
    export_fmu_files = kwargs.get('export_fmu_config_files', False)
    default_job_name = 'apsgui_job_name'
    job_name = kwargs.get('current_job_name', default_job_name)
    debug_level = get_debug_level(**kwargs)
    if export_fmu_files:
        # Use default file name equal to job name if this is defined and a default name if not
        # Job name will not exist if this script is run from APSGUI interactively, but only
        # when the running from workflow or batch
        if job_name is None:
            job_name = default_job_name
            print(
                '-- NOTE: A default name of the created FMU config files will be used when running interactively.\n'
                '         If you run from a workflow, the APS GUI job name will be used when creating the FMU config files.\n'
            )
        model_name = job_name + '.xml'
        att_name = job_name + '_aps.yml'
        prob_name = job_name + '_param_dist.txt'
        ert_field_name = job_name + '_ert_field_keyword.txt'
        model_file_name = get_top_location() / 'rms' / 'model' / model_name
        attributes_file_name = get_top_location() / 'fmuconfig' / 'input' / att_name
        probability_distribution_file_name = get_top_location() / 'ert' / 'input' / 'distributions' / prob_name
        ert_field_keyword_file_name = get_top_location() / 'ert' / 'input' / ert_field_name

        aps_model.write_model(
            model_file_name,
            attributes_file_name=attributes_file_name,
            probability_distribution_file_name=probability_distribution_file_name,
            current_job_name=job_name,
            debug_level=debug_level,
        )

        if aps_model.fmu_mode == "FIELDS":
            ertbox_grid_file_name = aps_model.fmu_ertbox_name + ".EGRID"
            ertbox_grid_file_path = "../../rms/output/aps/" + ertbox_grid_file_name
            grid_model = project.grid_models[aps_model.grid_model_name]
            zone_names = grid_model.properties[GridModelConstants.ZONE_NAME].code_names

            content = "-- ERT keywords related to fields used by APS.\n"
            content += f"GRID {ertbox_grid_file_path}\n"
            for key, zone_model in aps_model.sorted_zone_models.items():
                zone_number, region_number = key
                if not aps_model.isSelected(zone_number, region_number):
                    continue
                zone_name = zone_names[zone_number]
                for name in zone_model.used_gaussian_field_names:
                    fmu_field_name = 'aps_' + zone_name + '_' + name
                    fmu_field_name_file = fmu_field_name + "." + aps_model.fmu_field_file_format
                    content += f"FIELD {fmu_field_name}   "
                    content += f"PARAMETER {fmu_field_name_file}   "
                    content += f"INIT_FILES:rms/output/aps/{fmu_field_name_file}   "
                    content += f"MIN:-5.5  MAX:5.5  FORWARD_INIT:True\n"

            write_string_to_file(ert_field_keyword_file_name, content, debug_level=debug_level)