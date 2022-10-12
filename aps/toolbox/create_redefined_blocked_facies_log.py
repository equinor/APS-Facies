#!/bin/env python
"""
Description:
    This script can be used to create new facies log from a specified (original) facies log for blocked wells.
    The new facies logs can be defined by combining facies existing in the original logs such that two or more
    facies in the original facies log are combined into one new facies in the new log.

Input:  Name of model file in xml format.

Output: New facies log with redefined and merged facies.

Example model file in xml format:

        <?xml version="1.0" ?>
        <!-- This model specification is used in the script createRedefinedBlockedFaciesLog.py -->

        <MergeFaciesLog>
          <GridModelName>GridModelFine</GridModelName>
          <BlockedWells> BW  </BlockedWells>
          <OriginalFaciesLogName> Facies_case2 </OriginalFaciesLogName>
          <NewFaciesLogName> Facies_case2_combined </NewFaciesLogName>
          <NewFaciesCodes>
            <Facies code="1"> New_F01   </Facies>
            <Facies code="2"> New_F02   </Facies>
            <Facies code="3"> New_F03   </Facies>
          </NewFaciesCodes>

          <FromOldToNewFacies>
            <Line> F1 New_F01   </Line>
            <Line> F2 New_F01   </Line>
            <Line> F3 New_F02   </Line>
            <Line> F4 New_F02   </Line>
            <Line> F5 New_F03   </Line>
          </FromOldToNewFacies>
        </MergeFaciesLog>

"""
import xml.etree.ElementTree as ET
import os
from pathlib import Path
from aps.utils.xmlUtils import getKeyword, getTextCommand
from aps.utils.roxar.modifyBlockedWellData import createCombinedFaciesLogForBlockedWells
from aps.utils.exceptions.xml import MissingKeyword
from aps.utils.constants.simple import Debug
from aps.utils.methods import check_missing_keywords_list
from aps.utils.ymlUtils import get_text_value, get_dict, readYml


def run(params):
    """
        Make new blocked well facies log from existing facies log by combining/changing facies names.

        Usage alternatives:
        - Specify a dictionary with name of model file containing all input information. Example 1.
        - Specify a dictionary with all input information. Example 2.

Example 1:

from aps.toolbox import create_redefined_blocked_facies_log
from aps.utils.constants.simple import Debug


params = {
    "project": project,
    "debug_level": Debug.VERBOSE,
    "model_file_name": "examples/test_redefine_blocked_facies_log.xml",
    "realization_number": project.current_realisation,
}
create_redefined_blocked_facies_log.run(params)

Example 2:

from aps.toolbox import create_redefined_blocked_facies_log
from aps.utils.constants.simple import Debug


new_code_names = {
    1: "A",
    2: "B",
    3: "C",
}
# Original facies log has facies names F1, F2, F3, F4, F5, F6
# New facies log has facies names A,B,C
mapping = {
    "F1": "A",
    "F2": "A",
    "F3": "B",
    "F4": "B",
    "F5": "C",
    "F6": "C",
}

params = {
    "project": project,
    "debug_level": Debug.VERBOSE,
    "grid_model_name": "GridModelFine",
    "bw_name": "BW3",
    "original_facies_log_name": "FaciesEx1",
    "new_facies_log_name": "TestMergedFacies1",
    "new_code_names": new_code_names,
    "mapping_between_original_and_new": mapping,
    "realization_number": project.current_realisation,
}
create_redefined_blocked_facies_log.run(params)

    """
    project = params['project']
    realization_number = project.current_realisation
    model_file_name = params.get('model_file_name', None)
    debug_level = params.get('debug_level', Debug.OFF)
    if model_file_name:
        params = read_model_file(model_file_name)
        params['project'] = project
        params['debug_level'] = debug_level,
        params['realization_number'] = realization_number

    required_kw = [
        "grid_model_name", "bw_name", "original_facies_log_name",
        "new_facies_log_name", "new_code_names",
        "mapping_between_original_and_new", "realization_number",
    ]
    check_missing_keywords_list(params, required_kw)

    if debug_level >= Debug.VERBOSE:
        print(f"Grid model       : {params['grid_model_name']}")
        print(f"BW               : {params['bw_name']}")
        print(f"Input Facies log : {params['original_facies_log_name']}")
        print(f"Output Facies log: {params['new_facies_log_name']}")
        print(f"Output facies    : {params['new_code_names']}")
        print("Correspondence between original facies and new facies:")
        print(f" {params['mapping_between_original_and_new']}")
        print(f"Realization number: {realization_number + 1}")
    params.pop("debug_level")
    createCombinedFaciesLogForBlockedWells(params)

def read_model_file(model_file_name):
    # Check suffix of file for file type
    model_file = Path(model_file_name)
    suffix = model_file.suffix.lower().strip('.')
    if suffix in ['yaml', 'yml']:
        return _read_model_file_yml(model_file_name)
    elif suffix == 'xml':
        return _read_model_file_xml(model_file_name)
    else:
        raise ValueError(f"Model file name: {model_file_name}  must be either 'xml' or 'yml' format")

def _read_model_file_xml(model_file_name):
    print(f'Read model file: {model_file_name}')
    if not os.path.exists(model_file_name):
        raise IOError(f"File {model_file_name} does not exist")

    root = ET.parse(model_file_name).getroot()
    main_keyword = 'MergeFaciesLog'
    if root is None:
        raise MissingKeyword(main_keyword, model_file_name)

    kwargs = dict(parentKeyword=main_keyword, modelFile=model_file_name, required=True)
    grid_model_name = getTextCommand(root, 'GridModelName', **kwargs)

    text = getTextCommand(root, 'BlockedWells', **kwargs)
    blocked_wells_name = text.strip()

    text = getTextCommand(root, 'OriginalFaciesLogName', **kwargs)
    original_facies_log_name = text.strip()

    text = getTextCommand(root, 'NewFaciesLogName', **kwargs)
    new_facies_log_name = text.strip()

    kw = 'NewFaciesCodes'
    new_facies_codes_obj = getKeyword(root, kw, **kwargs)
    new_code_names = {}
    if new_facies_codes_obj is None:
        raise ValueError(f"Missing keyword {kw} in {model_file_name}")
    else:

        for facies_obj in new_facies_codes_obj.findall('Facies'):
            facies_code = int(facies_obj.get('code'))
            facies_name = facies_obj.text.strip()
            new_code_names[facies_code] = facies_name

    kw = 'FromOldToNewFacies'
    mapping_obj = getKeyword(root, kw, **kwargs)
    mapping = {}
    if mapping_obj is None:
        raise ValueError(f"Missing keyword {kw} in {model_file_name}")
    else:

        for line_obj in mapping_obj.findall('Line'):
            text = line_obj.text
            words = text.split()
            old_name = words[0].strip()
            new_name = words[1].strip()
            mapping[old_name] = new_name

    param_dict = {
        'grid_model_name': grid_model_name,
        'bw_name': blocked_wells_name,
        'original_facies_log_name': original_facies_log_name,
        'new_facies_log_name': new_facies_log_name,
        'new_code_names': new_code_names,
        'mapping_between_original_and_new':  mapping,
    }
    return param_dict




def _read_model_file_yml(model_file_name):
    # Read model file and overwrite model parameters
    print(f"Read model file: {model_file_name}  ")
    assert model_file_name
    spec_all = readYml(model_file_name)

    parent_kw = 'MergeFaciesLog'
    spec = spec_all[parent_kw] if parent_kw in spec_all else None
    if spec is None:
        raise ValueError(f"Missing keyword: {parent_kw} ")

    grid_model_name = get_text_value(spec, parent_kw, 'GridModelName')
    blocked_wells_name = get_text_value(spec, parent_kw, 'BlockedWells')
    original_facies_log_name = get_text_value(spec, parent_kw, 'OriginalFaciesLogName')
    new_facies_log_name = get_text_value(spec, parent_kw, 'NewFaciesLogName')
    new_code_names = get_dict(spec, parent_kw, 'NewFaciesCodes')
    mapping = get_dict(spec, parent_kw, 'FromOldToNewFacies')


    model_param_dict = {
        "grid_model_name": grid_model_name,
        "bw_name": blocked_wells_name,
        "original_facies_log_name": original_facies_log_name,
        "new_facies_log_name": new_facies_log_name,
        "new_code_names": new_code_names,
        "mapping_between_original_and_new":  mapping,
    }
    return model_param_dict

