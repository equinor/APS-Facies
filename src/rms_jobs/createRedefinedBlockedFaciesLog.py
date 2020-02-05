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
from src.utils.xmlUtils import getKeyword, getTextCommand
from src.utils.roxar.modifyBlockedWellData import createCombinedFaciesLogForBlockedWells
from src.utils.exceptions.xml import MissingKeyword
from src.utils.methods import get_debug_level, get_specification_file, SpecificationType
from src.utils.constants.simple import Debug


def run(roxar=None, project=None, **kwargs):
    model_file_name = get_specification_file(_type=SpecificationType.FACIES_LOG, **kwargs)
    debug_level = get_debug_level(**kwargs)

    _file = read_model_file(model_file_name)

    if debug_level >= Debug.VERBOSE:
        print('Grid model       : {}'.format(_file.grid_model_name))
        print('BW               : {}'.format(_file.blocked_wells_set_name))
        print('Input Facies log : {}'.format(_file.original_facies_log_name))
        print('Output Facies log: {}'.format(_file.new_facies_log_name))
        print('Output facies    :')
        print(_file.new_code_names)
        print('Correspondence between original facies and new facies:')
        print(_file.mapping)

    realization_number = project.current_realisation
    if debug_level >= Debug.VERBOSE:
        print('Realization number: {}'.format(realization_number + 1))

    createCombinedFaciesLogForBlockedWells(
        project,
        _file.grid_model_name,
        _file.blocked_wells_set_name,
        _file.original_facies_log_name,
        _file.new_facies_log_name,
        _file.new_code_names,
        _file.mapping,
    )


def read_model_file(model_file_name):
    print(f'Read model file: {model_file_name}')
    root = ET.parse(model_file_name).getroot()
    main_keyword = 'MergeFaciesLog'
    if root is None:
        raise MissingKeyword(main_keyword, model_file_name)

    kwargs = dict(parentKeyword=main_keyword, modelFile=model_file_name, required=True)
    keyword = 'GridModelName'
    grid_model_name = getTextCommand(root, keyword, **kwargs)

    keyword = 'BlockedWells'
    text = getTextCommand(root, keyword, **kwargs)
    blocked_wells_name = text.strip()

    keyword = 'OriginalFaciesLogName'
    text = getTextCommand(root, keyword, **kwargs)
    original_facies_log_name = text.strip()

    keyword = 'NewFaciesLogName'
    text = getTextCommand(root, keyword, **kwargs)
    new_facies_log_name = text.strip()

    keyword = 'NewFaciesCodes'
    new_facies_codes_obj = getKeyword(root, keyword, **kwargs)
    new_code_names = {}
    if new_facies_codes_obj is None:
        raise ValueError(
            'Missing keyword {} in {}'.format(keyword, model_file_name)
        )
    else:

        for facies_obj in new_facies_codes_obj.findall('Facies'):
            facies_code = int(facies_obj.get('code'))
            facies_name = facies_obj.text.strip()
            new_code_names[facies_code] = facies_name

    keyword = 'FromOldToNewFacies'
    mapping_obj = getKeyword(root, keyword, **kwargs)
    mapping = {}
    if mapping_obj is None:
        raise ValueError(
            'Missing keyword {} in {}'.format(keyword, model_file_name)
        )
    else:

        for line_obj in mapping_obj.findall('Line'):
            text = line_obj.text
            words = text.split()
            old_name = words[0].strip()
            new_name = words[1].strip()
            mapping[old_name] = new_name

    return _ModelFile(
        grid_model_name, blocked_wells_name, original_facies_log_name, new_facies_log_name, new_code_names, mapping,
    )


class _ModelFile:
    __slots__ = (
        'grid_model_name', 'blocked_wells_set_name', 'original_facies_log_name',
        'new_facies_log_name', 'new_code_names', 'mapping',
    )

    def __init__(
            self,
            grid_model_name,
            blocked_wells_name,
            original_facies_log_name,
            new_facies_log_name,
            new_code_names,
            mapping,
    ):
        self.grid_model_name = grid_model_name
        self.blocked_wells_set_name = blocked_wells_name
        self.original_facies_log_name = original_facies_log_name
        self.new_facies_log_name = new_facies_log_name
        self.new_code_names = new_code_names
        self.mapping = mapping


if __name__ == '__main__':
    import roxar

    run(roxar, project, debug_level=Debug.VERBOSE)
