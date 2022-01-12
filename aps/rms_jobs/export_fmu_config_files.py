#!/bin/env python
# -*- coding: utf-8 -*-

from aps.algorithms.APSModel import APSModel
from aps.utils.methods import get_specification_file, get_debug_level
from aps.utils.fmu import get_top_location
from warnings import warn


def run(project, **kwargs):
    model_file = get_specification_file(**kwargs)
    aps_model = APSModel(model_file)
    export_fmu_files = kwargs.get('export_fmu_config_files', False)
    fmu_mode = kwargs.get('fmu_mode', False)
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
        model_file_name = get_top_location() / 'rms' / 'model' / model_name
        attributes_file_name = get_top_location() / 'fmuconfig' / 'input' / att_name
        probability_distribution_file_name = get_top_location() / 'ert' / 'input' / 'distributions' / prob_name

        aps_model.write_model(
            model_file_name,
            attributes_file_name=attributes_file_name,
            probability_distribution_file_name=probability_distribution_file_name,
            current_job_name=job_name,
            debug_level=debug_level,
        )
