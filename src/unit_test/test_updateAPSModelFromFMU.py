#!/bin/env python
# -*- coding: utf-8 -*-
from bin.updateAPSModelFromFMU import updateAPSModelFromFMU
from src.utils.constants.simple import Debug
from src.unit_test.helpers import assert_identical_files

def test_update_aps_model():
    input_aps_model_file = 'testData_updateAPSModel/APS.xml'
    global_ipl_file = 'testData_updateAPSModel/global_include.ipl'
    output_aps_model_file = 'APS_modified.xml'
    reference_output_file = 'testData_updateAPSModel/APS_modified.xml'
    updateAPSModelFromFMU(global_ipl_file, input_aps_model_file, output_aps_model_file, debug_level=Debug.OFF)

    # Compare with reference data
    assert_identical_files(output_aps_model_file, reference_output_file)


