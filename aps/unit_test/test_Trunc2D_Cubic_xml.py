#!/bin/env python
# -*- coding: utf-8 -*-
import filecmp
import xml.etree.ElementTree as ET
from typing import List, Dict, Union, Tuple
from xml.etree.ElementTree import Element

import pytest

from aps.algorithms.APSMainFaciesTable import APSMainFaciesTable
from aps.algorithms.truncation_rules import Trunc2D_Cubic
from aps.unit_test.constants import (
    CUBIC_GAUSS_FIELD_FILES,
    FACIES_OUTPUT_FILE,
    OUTPUT_MODEL_FILE_NAME1,
    OUTPUT_MODEL_FILE_NAME2,
    OUT_POLY_FILE1,
    OUT_POLY_FILE2,
    KEYRESOLUTION,
    FACIES_OUTPUT_FILE_VECTORIZED,
)
from aps.unit_test.helpers import (
    apply_truncations,
    apply_truncations_vectorized,
    getFaciesInTruncRule,
    get_cubic_facies_reference_file_path,
    truncMapPolygons,
)
from aps.utils.constants.simple import Debug
from aps.utils.xmlUtils import prettify


def interpretXMLModelFileAndWrite(
    modelFileName: str,
    outputModelFileName: str,
    fTable: Dict[int, str],
    faciesInZone: List[str],
    gaussFieldsInZone: List[str],
    keyResolution: int,
    debug_level: Debug = Debug.OFF,
) -> Trunc2D_Cubic:
    # Read test model file with truncation rule into xml tree
    ET_Tree = ET.parse(modelFileName)
    root = ET_Tree.getroot()
    # Read TruncationRule keyword
    trRule = root.find('TruncationRule')

    # Get name of truncation rule
    truncRuleName = trRule[0].tag
    print('Truncation rule: ' + truncRuleName)

    # Get number of required Gauss fields
    nGaussFields = int(trRule[0].get('nGFields'))
    #    print('Number of gauss fields required for truncation rule: ' + str(nGaussFields))

    mainFaciesTable = APSMainFaciesTable(facies_table=fTable)

    # Create truncation rule object from input data, not read from file
    truncRuleOut = Trunc2D_Cubic(
        trRule,
        mainFaciesTable,
        faciesInZone,
        gaussFieldsInZone,
        debug_level=debug_level,
        modelFileName=modelFileName,
    )
    # Create and write XML tree
    createXMLTreeAndWriteFile(truncRuleOut, outputModelFileName)

    return truncRuleOut


def createXMLTreeAndWriteFile(
    truncRuleInput: Trunc2D_Cubic, outputModelFileName: str
) -> None:
    # Build an XML tree with top as root
    # from truncation object and write it
    assert truncRuleInput is not None
    top = Element('TEST_TruncationRule')
    fmu_attributes = []
    truncRuleInput.XMLAddElement(top, 1, 1, fmu_attributes)
    rootReformatted = prettify(top)
    print(f'Write file: {outputModelFileName}')
    with open(outputModelFileName, 'w', encoding='utf-8') as file:
        file.write(rootReformatted)


def createTrunc(
    outputModelFileName: str,
    fTable: Dict[int, str],
    faciesInZone: List[str],
    gaussFieldsInZone: List[str],
    gaussFieldsForBGFacies: List[str],
    truncStructure: List[Union[str, List[Union[str, float, int]]]],
    overlayGroups: List[List[Union[List[List[Union[str, float]]], List[str]]]],
    keyResolution: int,
    debug_level: Debug = Debug.OFF,
) -> Trunc2D_Cubic:
    mainFaciesTable = APSMainFaciesTable(facies_table=fTable)

    # Create an object and initialize it
    truncRuleOut = Trunc2D_Cubic()
    truncRuleOut.initialize(
        mainFaciesTable,
        faciesInZone,
        gaussFieldsInZone,
        gaussFieldsForBGFacies,
        truncStructure,
        overlayGroups,
        debug_level,
    )

    # Build an xml tree with the data and write it to file
    createXMLTreeAndWriteFile(truncRuleOut, outputModelFileName)
    return truncRuleOut


def initialize_write_read(
    outputModelFileName1: str,
    outputModelFileName2: str,
    fTable: Dict[int, str],
    faciesInZone: List[str],
    gaussFieldsInZone: List[str],
    gaussFieldsForBGFacies: List[str],
    truncStructure: List[Union[str, List[Union[str, float, int]]]],
    overlayGroups: List[List[Union[List[List[Union[str, float]]], List[str]]]],
    keyResolution: int,
    debug_level: Debug = Debug.OFF,
) -> Tuple[Trunc2D_Cubic, Trunc2D_Cubic]:
    file1 = outputModelFileName1
    file2 = outputModelFileName2
    # Create an object for truncation rule and write to file
    # Global variable truncRule
    truncRuleA = createTrunc(
        file1,
        fTable,
        faciesInZone,
        gaussFieldsInZone,
        gaussFieldsForBGFacies,
        truncStructure,
        overlayGroups,
        keyResolution,
        debug_level,
    )
    inputFile = file1

    # Write data structure:
    # Read the previously written file as and XML file and write it out again to a new file
    # Global variable truncRule2
    truncRuleB = interpretXMLModelFileAndWrite(
        inputFile,
        file2,
        fTable,
        faciesInZone,
        gaussFieldsInZone,
        keyResolution,
        debug_level,
    )

    # Compare the original xml file created in createTrunc and the xml file written by interpretXMLModelFileAndWrite
    check = filecmp.cmp(file1, file2)
    print(f'Compare file: {file1} and file: {file2}')
    assert check is True
    if check is False:
        raise ValueError('Error: Files are different')
    else:
        print('Files are equal: OK')
    return truncRuleA, truncRuleB


def getClassName(truncRule: Trunc2D_Cubic) -> None:
    assert truncRule is not None
    name = truncRule.getClassName()
    assert name == 'Trunc2D_Cubic'


@pytest.mark.parametrize(
    'case_number,data',
    [
        (
            1,
            {
                'fTable': {2: 'F2', 1: 'F1'},
                'faciesInZone': ['F1', 'F2'],
                'truncStructure': ['H', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0]],
                'faciesInTruncRule': ['F1', 'F2'],
                'gaussFieldsInZone': ['GF1', 'GF2', 'GF3', 'GF4'],
                'gaussFieldsForBGFacies': ['GF1', 'GF2'],
                'overlayGroups': [],
                'faciesProb': [0.5, 0.5],
            },
        ),
        (
            2,
            {
                'fTable': {2: 'F2', 1: 'F1'},
                'faciesInZone': ['F1', 'F2'],
                'truncStructure': ['V', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0]],
                'faciesInTruncRule': ['F1', 'F2'],
                'gaussFieldsInZone': ['GF1', 'GF2', 'GF3', 'GF4'],
                'gaussFieldsForBGFacies': ['GF1', 'GF2'],
                'overlayGroups': [],
                'faciesProb': [0.5, 0.5],
            },
        ),
        (
            3,
            {
                'fTable': {3: 'F3', 2: 'F2', 1: 'F1'},
                'faciesInZone': ['F1', 'F2', 'F3'],
                'truncStructure': [
                    'H',
                    ['F1', 1.0, 1, 0, 0],
                    ['F2', 1.0, 2, 0, 0],
                    ['F3', 1.0, 3, 0, 0],
                ],
                'faciesInTruncRule': ['F1', 'F2', 'F3'],
                'gaussFieldsInZone': ['GF1', 'GF2', 'GF3', 'GF4'],
                'gaussFieldsForBGFacies': ['GF1', 'GF2'],
                'overlayGroups': [],
                'faciesProb': [0.5, 0.2, 0.3],
            },
        ),
        (
            4,
            {
                'fTable': {3: 'F3', 2: 'F2', 1: 'F1'},
                'faciesInZone': ['F1', 'F2', 'F3'],
                'truncStructure': [
                    'V',
                    ['F1', 1.0, 1, 0, 0],
                    ['F2', 1.0, 2, 0, 0],
                    ['F3', 1.0, 3, 0, 0],
                ],
                'faciesInTruncRule': ['F1', 'F2', 'F3'],
                'gaussFieldsInZone': ['GF1', 'GF2', 'GF3', 'GF4'],
                'gaussFieldsForBGFacies': ['GF1', 'GF2'],
                'overlayGroups': [],
                'faciesProb': [0.5, 0.2, 0.3],
            },
        ),
        (
            5,
            {
                'fTable': {3: 'F3', 2: 'F2', 1: 'F1', 4: 'F4'},
                'faciesInZone': ['F1', 'F2', 'F3', 'F4'],
                'truncStructure': [
                    'V',
                    ['F1', 1.0, 1, 0, 0],
                    ['F2', 1.0, 2, 0, 0],
                    ['F3', 1.0, 3, 0, 0],
                ],
                'faciesInTruncRule': ['F1', 'F2', 'F3', 'F4'],
                'gaussFieldsInZone': ['GF1', 'GF2', 'GF3', 'GF4'],
                'gaussFieldsForBGFacies': ['GF1', 'GF2'],
                'overlayGroups': [
                    [
                        [['GF3', 'F4', 1.0, 0.5]],  # alpha list
                        ['F2', 'F3'],  # background list
                    ]
                ],
                'faciesProb': [0.3, 0.2, 0.3, 0.2],
            },
        ),
        (
            6,
            {
                'fTable': {3: 'F3', 2: 'F2', 1: 'F1', 4: 'F4'},
                'faciesInZone': ['F1', 'F2', 'F3', 'F4'],
                'truncStructure': [
                    'H',
                    ['F1', 1.0, 1, 0, 0],
                    ['F4', 1.0, 2, 1, 0],
                    ['F3', 1.0, 2, 2, 0],
                ],
                'faciesInTruncRule': ['F1', 'F4', 'F3', 'F2'],
                'gaussFieldsInZone': ['GF1', 'GF2', 'GF3', 'GF4'],
                'gaussFieldsForBGFacies': ['GF1', 'GF2'],
                'overlayGroups': [
                    [  # Group 1
                        [['GF3', 'F2', 1.0, 1.0]],  # alpha list
                        ['F4', 'F1'],  # background list
                    ]
                ],
                'faciesProb': [0.4, 0.1, 0.3, 0.2],
            },
        ),
        (
            7,
            {
                'fTable': {3: 'F3', 2: 'F2', 1: 'F1', 4: 'F4'},
                'faciesInZone': ['F1', 'F2', 'F3', 'F4'],
                'truncStructure': [
                    'H',
                    ['F1', 1.0, 1, 1, 0],
                    ['F2', 1.0, 1, 2, 0],
                    ['F4', 1.0, 2, 0, 0],
                ],
                'faciesInTruncRule': ['F1', 'F2', 'F4', 'F3'],
                'gaussFieldsInZone': ['GF1', 'GF2', 'GF3', 'GF4'],
                'gaussFieldsForBGFacies': ['GF1', 'GF2'],
                'overlayGroups': [
                    [  # Group 1
                        [['GF3', 'F3', 1.0, 0.5]],  # alpha list
                        ['F2', 'F1'],  # background list
                    ]
                ],
                'faciesProb': [0.4, 0.1, 0.3, 0.2],
            },
        ),
        (
            8,
            {
                'fTable': {6: 'F6', 4: 'F4', 3: 'F3', 2: 'F2', 5: 'F5', 1: 'F1'},
                'faciesInZone': ['F1', 'F2', 'F3', 'F4', 'F5', 'F6'],
                'truncStructure': [
                    'H',
                    ['F1', 1.0, 1, 0, 0],
                    ['F2', 1.0, 2, 0, 0],
                    ['F3', 1.0, 3, 0, 0],
                ],
                'faciesInTruncRule': ['F1', 'F2', 'F3', 'F4', 'F5', 'F6'],
                'gaussFieldsInZone': ['GF1', 'GF2', 'GF3', 'GF4', 'GF5'],
                'gaussFieldsForBGFacies': ['GF1', 'GF2'],
                'overlayGroups': [
                    [  # Group 1
                        [['GF3', 'F4', 1.0, 0.0]],  # alpha list
                        ['F1'],  # background list
                    ],
                    [  # Group 2
                        [['GF4', 'F5', 1.0, 0.5]],  # alpha list
                        ['F2'],  # background list
                    ],
                    [  # Group 3
                        [['GF5', 'F6', 1.0, 1.0]],  # alpha list
                        ['F3'],  # background list
                    ],
                ],
                'faciesProb': [0.2, 0.3, 0.1, 0.1, 0.1, 0.2],
            },
        ),
        (
            9,
            {
                'fTable': {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2'},
                'faciesInZone': ['F2', 'F1', 'F4', 'F3'],
                'truncStructure': [
                    'V',
                    ['F1', 0.6, 1, 0, 0],
                    ['F2', 1.0, 2, 1, 0],
                    ['F1', 0.4, 2, 2, 0],
                ],
                'faciesInTruncRule': ['F1', 'F2', 'F4', 'F3'],
                'gaussFieldsInZone': ['GF1', 'GF2', 'GF3', 'GF4'],
                'gaussFieldsForBGFacies': ['GF1', 'GF2'],
                'overlayGroups': [
                    [  # Group 1
                        [['GF3', 'F4', 1.0, 0.5]],  # alpha list
                        ['F1'],  # background list
                    ],
                    [  # Group 2
                        [['GF4', 'F3', 1.0, 0.8]],  # alpha list
                        ['F2'],  # background list
                    ],
                ],
                'faciesProb': [0.38, 0.11, 0.31, 0.2],
            },
        ),
        (
            10,
            {
                'fTable': {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2'},
                'faciesInZone': ['F2', 'F1', 'F4', 'F3'],
                'truncStructure': [
                    'V',
                    ['F1', 1.0, 1, 1, 0],
                    ['F3', 0.3, 1, 2, 0],
                    ['F3', 0.7, 2, 0, 0],
                ],
                'faciesInTruncRule': ['F1', 'F3', 'F4', 'F2'],
                'gaussFieldsInZone': ['GF1', 'GF2', 'GF3', 'GF4'],
                'gaussFieldsForBGFacies': ['GF1', 'GF2'],
                'overlayGroups': [
                    [  # Group 1
                        [['GF3', 'F4', 1.0, 0.5]],  # alpha list
                        ['F1'],  # background list
                    ],
                    [  # Group 2
                        [['GF4', 'F2', 1.0, 0.8]],  # alpha list
                        ['F3'],  # background list
                    ],
                ],
                'faciesProb': [0.4, 0.1, 0.3, 0.2],
            },
        ),
        (
            11,
            {
                'fTable': {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5', 6: 'F6'},
                'faciesInZone': ['F2', 'F1', 'F4', 'F3', 'F6', 'F5'],
                'truncStructure': [
                    'H',
                    ['F1', 1.0, 1, 0, 0],
                    ['F2', 1.0, 2, 0, 0],
                    ['F3', 1.0, 3, 0, 0],
                    ['F4', 1.0, 4, 0, 0],
                ],
                'faciesInTruncRule': ['F1', 'F2', 'F3', 'F4', 'F5', 'F6'],
                'gaussFieldsInZone': ['GF1', 'GF2', 'GF3', 'GF4'],
                'gaussFieldsForBGFacies': ['GF1', 'GF2'],
                'overlayGroups': [
                    [  # Group 1
                        [['GF3', 'F5', 1.0, 0.5]],  # alpha list
                        ['F1', 'F2', 'F3'],  # background list
                    ],
                    [  # Group 2
                        [['GF4', 'F6', 1.0, 0.8]],  # alpha list
                        ['F4'],  # background list
                    ],
                ],
                'faciesProb': [0.3, 0.1, 0.2, 0.2, 0.1, 0.1],
            },
        ),
        (
            12,
            {
                'fTable': {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2'},
                'faciesInZone': ['F2', 'F1', 'F4', 'F3'],
                'truncStructure': [
                    'H',
                    ['F1', 1.0, 1, 0, 0],
                    ['F2', 1.0, 2, 0, 0],
                    ['F3', 1.0, 3, 0, 0],
                    ['F4', 1.0, 4, 0, 0],
                ],
                'faciesInTruncRule': ['F1', 'F2', 'F3', 'F4'],
                'gaussFieldsInZone': ['GF1', 'GF2', 'GF3', 'GF4'],
                'gaussFieldsForBGFacies': ['GF1', 'GF2'],
                'overlayGroups': [],
                'faciesProb': [0.3, 0.1, 0.3, 0.3],
            },
        ),
        (
            13,
            {
                'fTable': {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5', 6: 'F6'},
                'faciesInZone': ['F2', 'F1', 'F4', 'F3', 'F6', 'F5'],
                'truncStructure': [
                    'V',
                    ['F1', 1.0, 1, 0, 0],
                    ['F2', 1.0, 2, 0, 0],
                    ['F3', 1.0, 3, 0, 0],
                    ['F4', 1.0, 4, 0, 0],
                ],
                'faciesInTruncRule': ['F1', 'F2', 'F3', 'F4', 'F5', 'F6'],
                'gaussFieldsInZone': ['GF1', 'GF2', 'GF3', 'GF4'],
                'gaussFieldsForBGFacies': ['GF1', 'GF2'],
                'overlayGroups': [
                    [  # Group 1
                        [['GF3', 'F5', 1.0, 0.3]],  # alpha list
                        ['F1', 'F3'],  # background list
                    ],
                    [  # Group 2
                        [['GF4', 'F6', 1.0, 0.7]],  # alpha list
                        ['F4', 'F2'],  # background list
                    ],
                ],
                'faciesProb': [0.3, 0.1, 0.2, 0.2, 0.1, 0.1],
            },
        ),
        (
            14,
            {
                'fTable': {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5', 6: 'F6'},
                'faciesInZone': ['F2', 'F1', 'F4', 'F3', 'F6', 'F5'],
                'truncStructure': [
                    'H',
                    ['F1', 1.0, 1, 0, 0],
                    ['F2', 1.0, 2, 0, 0],
                    ['F3', 1.0, 3, 1, 0],
                    ['F4', 1.0, 3, 2, 0],
                ],
                'faciesInTruncRule': ['F1', 'F2', 'F3', 'F4', 'F5', 'F6'],
                'gaussFieldsInZone': ['GF1', 'GF2', 'GF3', 'GF4'],
                'gaussFieldsForBGFacies': ['GF1', 'GF2'],
                'overlayGroups': [
                    [  # Group 1
                        [['GF3', 'F5', 1.0, 0.3]],  # alpha list
                        ['F1', 'F3'],  # background list
                    ],
                    [  # Group 2
                        [['GF4', 'F6', 1.0, 0.7]],  # alpha list
                        ['F4', 'F2'],  # background list
                    ],
                ],
                'faciesProb': [0.3, 0.1, 0.2, 0.2, 0.1, 0.1],
            },
        ),
        (
            15,
            {
                'fTable': {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5', 6: 'F6'},
                'faciesInZone': ['F2', 'F1', 'F4', 'F3', 'F6', 'F5'],
                'truncStructure': [
                    'V',
                    ['F1', 1.0, 1, 0, 0],
                    ['F2', 1.0, 2, 0, 0],
                    ['F3', 1.0, 3, 1, 0],
                    ['F4', 1.0, 3, 2, 0],
                ],
                'faciesInTruncRule': ['F1', 'F2', 'F3', 'F4', 'F5', 'F6'],
                'gaussFieldsInZone': ['GF1', 'GF2', 'GF3', 'GF4'],
                'gaussFieldsForBGFacies': ['GF1', 'GF2'],
                'overlayGroups': [
                    [  # Group 1
                        [['GF3', 'F5', 1.0, 0.3]],  # alpha list
                        ['F1', 'F3'],  # background list
                    ],
                    [  # Group 2
                        [['GF4', 'F6', 1.0, 0.7]],  # alpha list
                        ['F4', 'F2'],  # background list
                    ],
                ],
                'faciesProb': [0.3, 0.1, 0.2, 0.2, 0.1, 0.1],
            },
        ),
        (
            16,
            {
                'fTable': {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2'},
                'faciesInZone': ['F2', 'F1', 'F4', 'F3'],
                'truncStructure': [
                    'V',
                    ['F1', 1.0, 1, 0, 0],
                    ['F2', 1.0, 2, 0, 0],
                    ['F3', 1.0, 3, 1, 0],
                    ['F4', 1.0, 3, 2, 0],
                ],
                'faciesInTruncRule': ['F1', 'F2', 'F3', 'F4'],
                'gaussFieldsInZone': ['GF1', 'GF2', 'GF3', 'GF4'],
                'gaussFieldsForBGFacies': ['GF1', 'GF2'],
                'overlayGroups': [],
                'faciesProb': [0.3, 0.2, 0.2, 0.3],
            },
        ),
        (
            17,
            {
                'fTable': {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5', 6: 'F6'},
                'faciesInZone': ['F2', 'F1', 'F4', 'F3', 'F6', 'F5'],
                'truncStructure': [
                    'H',
                    ['F1', 1.0, 1, 0, 0],
                    ['F2', 1.0, 2, 0, 0],
                    ['F3', 1.0, 3, 0, 0],
                    ['F4', 1.0, 4, 0, 0],
                    ['F5', 1.0, 5, 0, 0],
                ],
                'faciesInTruncRule': ['F1', 'F2', 'F3', 'F4', 'F5', 'F6'],
                'gaussFieldsInZone': ['GF1', 'GF2', 'GF3', 'GF4'],
                'gaussFieldsForBGFacies': ['GF1', 'GF2'],
                'overlayGroups': [
                    [  # Group 1
                        [['GF3', 'F6', 1.0, 0.3]],  # alpha list
                        ['F1', 'F3', 'F4', 'F2'],  # background list
                    ]
                ],
                'faciesProb': [0.3, 0.1, 0.2, 0.2, 0.1, 0.1],
            },
        ),
        (
            18,
            {
                'fTable': {
                    3: 'F1',
                    2: 'F3',
                    1: 'F4',
                    4: 'F2',
                    5: 'F5',
                    6: 'F6',
                    7: 'F7',
                },
                'faciesInZone': ['F2', 'F1', 'F4', 'F3', 'F6', 'F5', 'F7'],
                'truncStructure': [
                    'H',
                    ['F1', 1.0, 1, 0, 0],
                    ['F2', 1.0, 2, 0, 0],
                    ['F3', 1.0, 3, 0, 0],
                    ['F4', 1.0, 4, 0, 0],
                    ['F5', 1.0, 5, 0, 0],
                ],
                'faciesInTruncRule': ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7'],
                'gaussFieldsInZone': ['GF1', 'GF2', 'GF3', 'GF4'],
                'gaussFieldsForBGFacies': ['GF1', 'GF2'],
                'overlayGroups': [
                    [  # Group 1
                        [['GF3', 'F6', 1.0, 0.3]],  # alpha list
                        ['F1', 'F3', 'F4', 'F2'],  # background list
                    ],
                    [  # Group 2
                        [['GF4', 'F7', 1.0, 0.9]],  # alpha list
                        ['F5'],  # background list
                    ],
                ],
                'faciesProb': [0.2, 0.1, 0.2, 0.2, 0.1, 0.1, 0.1],
            },
        ),
        (
            19,
            {
                'fTable': {
                    3: 'F1',
                    2: 'F3',
                    1: 'F4',
                    4: 'F2',
                    5: 'F5',
                    6: 'F6',
                    7: 'F7',
                },
                'faciesInZone': ['F2', 'F1', 'F4', 'F3', 'F6', 'F5', 'F7'],
                'truncStructure': [
                    'H',
                    ['F1', 1.0, 1, 0, 0],
                    ['F2', 1.0, 2, 1, 1],
                    ['F3', 1.0, 2, 1, 2],
                    ['F4', 1.0, 2, 2, 1],
                    ['F5', 1.0, 2, 2, 2],
                ],
                'faciesInTruncRule': ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7'],
                'gaussFieldsInZone': ['GF1', 'GF2', 'GF3', 'GF4'],
                'gaussFieldsForBGFacies': ['GF1', 'GF2'],
                'overlayGroups': [
                    [  # Group 1
                        [['GF3', 'F6', 1.0, 0.3]],  # alpha list
                        ['F1', 'F3', 'F4', 'F2'],  # background list
                    ],
                    [  # Group 2
                        [['GF4', 'F7', 1.0, 0.9]],  # alpha list
                        ['F5'],  # background list
                    ],
                ],
                'faciesProb': [0.2, 0.1, 0.2, 0.2, 0.1, 0.1, 0.1],
            },
        ),
        (
            20,
            {
                'fTable': {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5', 6: 'F6'},
                'faciesInZone': ['F2', 'F1', 'F4', 'F3', 'F6', 'F5'],
                'truncStructure': [
                    'V',
                    ['F4', 0.4, 1, 0, 0],
                    ['F2', 1.0, 2, 1, 0],
                    ['F3', 1.0, 2, 2, 1],
                    ['F4', 0.3, 2, 2, 2],
                    ['F4', 0.3, 2, 3, 0],
                ],
                'faciesInTruncRule': ['F4', 'F2', 'F3', 'F1', 'F5', 'F6'],
                'gaussFieldsInZone': ['GF1', 'GF2', 'GF3', 'GF4', 'GF5'],
                'gaussFieldsForBGFacies': ['GF1', 'GF2'],
                'overlayGroups': [
                    [  # Group 1
                        [['GF3', 'F1', 1.0, 0.3]],  # alpha list
                        ['F2'],  # background list
                    ],
                    [  # Group 2
                        [['GF4', 'F5', 1.0, 0.9]],  # alpha list
                        ['F3'],  # background list
                    ],
                    [  # Group 3
                        [['GF5', 'F6', 1.0, 0.0]],  # alpha list
                        ['F4'],  # background list
                    ],
                ],
                'faciesProb': [0.3, 0.1, 0.2, 0.2, 0.1, 0.1],
            },
        ),
        (
            21,
            {
                'fTable': {3: 'F1', 2: 'F3', 1: 'F4'},
                'faciesInZone': ['F1', 'F4', 'F3'],
                'truncStructure': [
                    'V',
                    ['F4', 0.2, 1, 0, 0],
                    ['F4', 0.2, 2, 1, 0],
                    ['F3', 1.0, 2, 2, 1],
                    ['F4', 0.3, 2, 2, 2],
                    ['F4', 0.3, 2, 3, 0],
                ],
                'faciesInTruncRule': ['F4', 'F3', 'F1'],
                'gaussFieldsInZone': ['GF1', 'GF2', 'GF3', 'GF4'],
                'gaussFieldsForBGFacies': ['GF1', 'GF2'],
                'overlayGroups': [
                    [  # Group 1
                        [['GF3', 'F1', 1.0, 0.3]],  # alpha list
                        ['F4'],  # background list
                    ],
                ],
                'faciesProb': [0.3, 0.3, 0.4],
            },
        ),
        (
            22,
            {
                'fTable': {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5'},
                'faciesInZone': ['F1', 'F4', 'F3', 'F5', 'F2'],
                'truncStructure': [
                    'H',
                    ['F1', 1.0, 1, 0, 0],
                    ['F2', 1.0, 2, 1, 0],
                    ['F3', 0.5, 2, 2, 1],
                    ['F4', 1.0, 2, 2, 2],
                    ['F3', 0.5, 2, 3, 1],
                    ['F5', 1.0, 2, 3, 2],
                ],
                'faciesInTruncRule': ['F1', 'F2', 'F3', 'F4', 'F5'],
                'gaussFieldsInZone': ['GF1', 'GF2', 'GF3', 'GF4'],
                'gaussFieldsForBGFacies': ['GF1', 'GF2'],
                'overlayGroups': [],
                'faciesProb': [0.3, 0.1, 0.2, 0.2, 0.2],
            },
        ),
        (
            23,
            {
                'fTable': {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5'},
                'faciesInZone': ['F1', 'F4', 'F3', 'F5', 'F2'],
                'truncStructure': [
                    'H',
                    ['F1', 1.0, 1, 0, 0],
                    ['F5', 0.5, 2, 1, 0],
                    ['F3', 0.5, 2, 2, 1],
                    ['F4', 1.0, 2, 2, 2],
                    ['F3', 0.5, 2, 3, 1],
                    ['F5', 0.5, 2, 3, 2],
                ],
                'faciesInTruncRule': ['F1', 'F5', 'F3', 'F4', 'F2'],
                'gaussFieldsInZone': ['GF1', 'GF2', 'GF3', 'GF4'],
                'gaussFieldsForBGFacies': ['GF1', 'GF2'],
                'overlayGroups': [
                    [  # Group 1
                        [['GF3', 'F2', 1.0, 0.4]],  # alpha list
                        ['F5', 'F3'],  # background list
                    ],
                ],
                'faciesProb': [0.3, 0.1, 0.2, 0.2, 0.2],
            },
        ),
        (
            24,
            {
                'fTable': {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5'},
                'faciesInZone': ['F1', 'F4', 'F3', 'F5', 'F2'],
                'truncStructure': [
                    'H',
                    ['F1', 1.0, 1, 0, 0],
                    ['F5', 0.5, 2, 1, 0],
                    ['F3', 0.5, 2, 2, 1],
                    ['F4', 1.0, 2, 2, 2],
                    ['F3', 0.5, 2, 3, 1],
                    ['F5', 0.5, 2, 3, 2],
                ],
                'faciesInTruncRule': ['F1', 'F5', 'F3', 'F4', 'F2'],
                'gaussFieldsInZone': ['GF1', 'GF2', 'GF3', 'GF4', 'GF5'],
                'gaussFieldsForBGFacies': ['GF1', 'GF2'],
                'overlayGroups': [
                    [  # Group 1
                        [  # alpha list
                            ['GF3', 'F2', 0.4, 0.4],
                            ['GF4', 'F2', 0.3, 0.4],
                            ['GF5', 'F2', 0.3, 0.4],
                        ],
                        ['F5', 'F3'],  # background list
                    ]
                ],
                'faciesProb': [0.3, 0.1, 0.2, 0.2, 0.2],
            },
        ),
    ],
)
def test_Trunc2DCubic(
    case_number: int,
    data: Dict[
        str,
        Union[
            Dict[int, str],
            List[str],
            List[Union[str, List[Union[str, float, int]]]],
            List[List[Union[List[List[Union[str, float]]], List[str]]]],
            List[float],
        ],
    ],
) -> None:
    print('')
    print('******** Case number: ' + str(case_number) + ' *********')
    run(faciesReferenceFile=get_cubic_facies_reference_file_path(case_number), **data)


def run(
    fTable: Dict[int, str],
    faciesInTruncRule: List[str],
    faciesInZone: List[str],
    faciesProb: List[float],
    faciesReferenceFile: str,
    gaussFieldsInZone: List[str],
    gaussFieldsForBGFacies: List[str],
    overlayGroups: List[List[Union[List[List[Union[str, float]]], List[str]]]],
    truncStructure: List[Union[str, List[Union[str, float, int]]]],
) -> None:
    truncRule, truncRule2 = initialize_write_read(
        outputModelFileName1=OUTPUT_MODEL_FILE_NAME1,
        outputModelFileName2=OUTPUT_MODEL_FILE_NAME2,
        fTable=fTable,
        faciesInZone=faciesInZone,
        gaussFieldsInZone=gaussFieldsInZone,
        gaussFieldsForBGFacies=gaussFieldsForBGFacies,
        truncStructure=truncStructure,
        overlayGroups=overlayGroups,
        keyResolution=KEYRESOLUTION,
        debug_level=Debug.OFF,
    )
    nGaussFields = truncRule.getNGaussFieldsInModel()
    getClassName(truncRule)
    getFaciesInTruncRule(truncRule, truncRule2, faciesInTruncRule)
    truncMapPolygons(
        truncRule=truncRule,
        truncRule2=truncRule2,
        faciesProb=faciesProb,
        outPolyFile1=OUT_POLY_FILE1,
        outPolyFile2=OUT_POLY_FILE2,
    )
    apply_truncations(
        truncRule=truncRule,
        faciesReferenceFile=faciesReferenceFile,
        nGaussFields=nGaussFields,
        gaussFieldFiles=CUBIC_GAUSS_FIELD_FILES,
        faciesOutputFile=FACIES_OUTPUT_FILE,
    )

    apply_truncations_vectorized(
        truncRule=truncRule,
        faciesReferenceFile=faciesReferenceFile,
        nGaussFields=nGaussFields,
        gaussFieldFiles=CUBIC_GAUSS_FIELD_FILES,
        faciesOutputFile=FACIES_OUTPUT_FILE_VECTORIZED,
    )


if __name__ == '__main__':
    pytest.main([__file__])
