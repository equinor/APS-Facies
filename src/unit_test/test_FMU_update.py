#!/bin/env python

import xml.etree.ElementTree as ET
import pytest
from src.utils.constants.simple import Debug, OriginType, TrendType
from bin.updateAPSModelFromFMU import updateAPSModelFromFMU
from src.algorithms.APSModel import APSModel
from src.unit_test.test_createXMLModelFiles import get_apsmodel_with_no_fmu_markers, get_apsmodel_with_all_fmu_markers, read_write_model


@pytest.fixture(scope='module')
def parsed_inputFile():
    return ET.parse('testData_models/APS.xml')


@pytest.fixture(scope='module')
def original_values(parsed_inputFile):
    return read_values_from_xml_tree(parsed_inputFile)


@pytest.fixture(scope='module')
def update_values():
    return read_key_values_from_file_as_dict('testData_FMU/test_global_include.ipl')


def read_key_values_from_file_as_dict(input_file):
    key_value_dict = {}
    with open(input_file, 'r') as f:
        for line in f:
            line_without_comment = line.partition('//')[0]
            if len(line_without_comment) > 0:
                parts = line_without_comment.partition('=')
                if len(parts) == 3:
                    key = parts[0].strip()
                    value = parts[2].strip()
                    if len(key) > 0 and len(value) > 0:
                        key_value_dict[key] = value
    return key_value_dict


def read_values_from_xml_tree(tree):
    values = {}
    for element in tree.findall('.//*[@kw]'):
        key = element.get('kw')
        value = element.text
        values[key] = value.strip()
    return values


def read_fmu_attributes_file(file):
    with open(file, 'r') as f:
        content = f.readlines()
        content = [x.strip() for x in content]
        return set(content)


def test_case_with_no_fmu_markers_set():

    aps_model = get_apsmodel_with_no_fmu_markers()

    out_file = 'aps_model_with_no_fmu_markers.xml'
    attributes_file = 'fmu_attributes.txt'

    aps_model.writeModel(out_file, attributes_file, debug_level=Debug.OFF)

    check_fmu_attributes_output_correlates_to_xml_output(out_file, attributes_file)


def test_case_with_all_fmu_markers_set():

    aps_model = get_apsmodel_with_all_fmu_markers()

    out_file = 'aps_model_with_all_fmu_markers.xml'
    attributes_file = 'fmu_attributes.txt'
    expected_key_value_set_file = 'testData_FMU/expected_key_value_set.txt'

    aps_model.writeModel(out_file, attributes_file, debug_level=Debug.OFF)

    check_fmu_attributes_output_correlates_to_xml_output(out_file, attributes_file)
    check_expected_key_value_set_correlates_to_xml_output(out_file, expected_key_value_set_file)


def check_fmu_attributes_output_correlates_to_xml_output(out_file, attributes_file):

    values_from_generated_xml = read_values_from_xml_tree(ET.parse(out_file))
    values_from_generated_attributes_file = read_fmu_attributes_file(attributes_file)
    key_set_from_xml = set(values_from_generated_xml.keys())
    assert len(key_set_from_xml.symmetric_difference(values_from_generated_attributes_file)) == 0


def check_expected_key_value_set_correlates_to_xml_output(out_file, expected_key_value_set_file):
    values_from_generated_xml = read_values_from_xml_tree(ET.parse(out_file))
    fasit_key_values = read_key_values_from_file_as_dict(expected_key_value_set_file)
    assert values_from_generated_xml == fasit_key_values


def test_global_include_file_has_all_necessary_update_values(original_values, update_values):

    # This is testing that all fmu attributes that we expect to test in this test is actually also represented in the test_global_include.ipl file
    assert set(original_values.keys()).issubset(set(update_values.keys()))


def test_all_element_values_are_correctly_updated(original_values, update_values):

    updateAPSModelFromFMU('testData_FMU/test_global_include.ipl', 'testData_models/APS.xml',
                          'testData_models/APS_FMUupdated.xml', Debug.VERBOSE)

    parsed_output_file = ET.parse('testData_models/APS_FMUupdated.xml')
    new_values = read_values_from_xml_tree(parsed_output_file)

    filtered_keys = original_values.keys() & update_values.keys()  # Filtering out keys not related to updatable FMU values in the model file
    for key in filtered_keys:
        original_value = original_values[key]
        expected_value = update_values[key]
        found_value = new_values[key]
        assert expected_value == found_value


