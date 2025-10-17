#!/bin/env python
# -*- coding: utf-8 -*-
from aps.rms_jobs.updateAPSModelFromFMU import update_aps_model_from_fmu
from aps.utils.constants.simple import Debug
from tests.helpers import assert_identical_files


def test_update_aps_model(data_directory, output_directory):
    model_folder = data_directory / 'update_aps_model'

    input_aps_model_file = model_folder / 'APS.xml'
    global_ipl_file = model_folder / 'global_include.ipl'
    output_aps_model_file = output_directory / 'APS_modified.xml'
    reference_output_file = model_folder / 'APS_modified.xml'
    update_aps_model_from_fmu(
        global_ipl_file,
        input_aps_model_file,
        output_aps_model_file,
        debug_level=Debug.OFF,
    )

    # Compare with reference data
    assert_identical_files(output_aps_model_file, reference_output_file)
