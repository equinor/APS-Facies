#!/bin/env python
# -*- coding: utf-8 -*-
import filecmp
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Tuple
from xml.etree.ElementTree import Element

import pytest

from aps.algorithms.APSMainFaciesTable import APSMainFaciesTable
from aps.algorithms.truncation_rules import Trunc2D_Cubic
from aps.utils.constants.simple import Debug
from aps.utils.types import (
    CubicTruncationRuleStructureType,
    FaciesTableType,
    OverlayGroupType,
)
from aps.utils.xmlUtils import prettify
from tests.constants import (
    KEYRESOLUTION,
)
from tests.helpers import (
    apply_truncations,
    apply_truncations_vectorized,
    getFaciesInTruncRule,
    truncMapPolygons,
)


def interpretXMLModelFileAndWrite(
    modelFileName: str,
    outputModelFileName: str,
    fTable: Dict[int, str],
    faciesInZone: List[str],
    gaussFieldsInZone: List[str],
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
    truncStructure: CubicTruncationRuleStructureType,
    overlayGroups: OverlayGroupType,
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
        debug_level=debug_level,
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
    truncStructure: CubicTruncationRuleStructureType,
    overlayGroups: OverlayGroupType,
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


@pytest.mark.parametrize('kind', ['cubic'])
@pytest.mark.parametrize(
    [
        'case_number',
        'facies_table',
        'facies_in_zone',
        'truncation_rule',
        'facies_in_truncation_rule',
        'gaussian_fields_in_zone',
        'gaussian_fields_for_background_facies',
        'overlay_groups',
        'facies_probabilities',
    ],
    [
        (
            1,
            {2: 'F2', 1: 'F1'},
            ['F1', 'F2'],
            ['H', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0]],
            ['F1', 'F2'],
            ['GF1', 'GF2', 'GF3', 'GF4'],
            ['GF1', 'GF2'],
            [],
            [0.5, 0.5],
        ),
        (
            2,
            {2: 'F2', 1: 'F1'},
            ['F1', 'F2'],
            ['V', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0]],
            ['F1', 'F2'],
            ['GF1', 'GF2', 'GF3', 'GF4'],
            ['GF1', 'GF2'],
            [],
            [0.5, 0.5],
        ),
        (
            3,
            {3: 'F3', 2: 'F2', 1: 'F1'},
            ['F1', 'F2', 'F3'],
            [
                'H',
                ['F1', 1.0, 1, 0, 0],
                ['F2', 1.0, 2, 0, 0],
                ['F3', 1.0, 3, 0, 0],
            ],
            ['F1', 'F2', 'F3'],
            ['GF1', 'GF2', 'GF3', 'GF4'],
            ['GF1', 'GF2'],
            [],
            [0.5, 0.2, 0.3],
        ),
        (
            4,
            {3: 'F3', 2: 'F2', 1: 'F1'},
            ['F1', 'F2', 'F3'],
            [
                'V',
                ['F1', 1.0, 1, 0, 0],
                ['F2', 1.0, 2, 0, 0],
                ['F3', 1.0, 3, 0, 0],
            ],
            ['F1', 'F2', 'F3'],
            ['GF1', 'GF2', 'GF3', 'GF4'],
            ['GF1', 'GF2'],
            [],
            [0.5, 0.2, 0.3],
        ),
        (
            5,
            {3: 'F3', 2: 'F2', 1: 'F1', 4: 'F4'},
            ['F1', 'F2', 'F3', 'F4'],
            [
                'V',
                ['F1', 1.0, 1, 0, 0],
                ['F2', 1.0, 2, 0, 0],
                ['F3', 1.0, 3, 0, 0],
            ],
            ['F1', 'F2', 'F3', 'F4'],
            ['GF1', 'GF2', 'GF3', 'GF4'],
            ['GF1', 'GF2'],
            [
                [
                    [['GF3', 'F4', 1.0, 0.5]],  # alpha list
                    ['F2', 'F3'],  # background list
                ]
            ],
            [0.3, 0.2, 0.3, 0.2],
        ),
        (
            6,
            {3: 'F3', 2: 'F2', 1: 'F1', 4: 'F4'},
            ['F1', 'F2', 'F3', 'F4'],
            [
                'H',
                ['F1', 1.0, 1, 0, 0],
                ['F4', 1.0, 2, 1, 0],
                ['F3', 1.0, 2, 2, 0],
            ],
            ['F1', 'F4', 'F3', 'F2'],
            ['GF1', 'GF2', 'GF3', 'GF4'],
            ['GF1', 'GF2'],
            [
                [  # Group 1
                    [['GF3', 'F2', 1.0, 1.0]],  # alpha list
                    ['F4', 'F1'],  # background list
                ]
            ],
            [0.4, 0.1, 0.3, 0.2],
        ),
        (
            7,
            {3: 'F3', 2: 'F2', 1: 'F1', 4: 'F4'},
            ['F1', 'F2', 'F3', 'F4'],
            [
                'H',
                ['F1', 1.0, 1, 1, 0],
                ['F2', 1.0, 1, 2, 0],
                ['F4', 1.0, 2, 0, 0],
            ],
            ['F1', 'F2', 'F4', 'F3'],
            ['GF1', 'GF2', 'GF3', 'GF4'],
            ['GF1', 'GF2'],
            [
                [  # Group 1
                    [['GF3', 'F3', 1.0, 0.5]],  # alpha list
                    ['F2', 'F1'],  # background list
                ]
            ],
            [0.4, 0.1, 0.3, 0.2],
        ),
        (
            8,
            {6: 'F6', 4: 'F4', 3: 'F3', 2: 'F2', 5: 'F5', 1: 'F1'},
            ['F1', 'F2', 'F3', 'F4', 'F5', 'F6'],
            [
                'H',
                ['F1', 1.0, 1, 0, 0],
                ['F2', 1.0, 2, 0, 0],
                ['F3', 1.0, 3, 0, 0],
            ],
            ['F1', 'F2', 'F3', 'F4', 'F5', 'F6'],
            ['GF1', 'GF2', 'GF3', 'GF4', 'GF5'],
            ['GF1', 'GF2'],
            [
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
            [0.2, 0.3, 0.1, 0.1, 0.1, 0.2],
        ),
        (
            9,
            {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2'},
            ['F2', 'F1', 'F4', 'F3'],
            [
                'V',
                ['F1', 0.6, 1, 0, 0],
                ['F2', 1.0, 2, 1, 0],
                ['F1', 0.4, 2, 2, 0],
            ],
            ['F1', 'F2', 'F4', 'F3'],
            ['GF1', 'GF2', 'GF3', 'GF4'],
            ['GF1', 'GF2'],
            [
                [  # Group 1
                    [['GF3', 'F4', 1.0, 0.5]],  # alpha list
                    ['F1'],  # background list
                ],
                [  # Group 2
                    [['GF4', 'F3', 1.0, 0.8]],  # alpha list
                    ['F2'],  # background list
                ],
            ],
            [0.38, 0.11, 0.31, 0.2],
        ),
        (
            10,
            {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2'},
            ['F2', 'F1', 'F4', 'F3'],
            [
                'V',
                ['F1', 1.0, 1, 1, 0],
                ['F3', 0.3, 1, 2, 0],
                ['F3', 0.7, 2, 0, 0],
            ],
            ['F1', 'F3', 'F4', 'F2'],
            ['GF1', 'GF2', 'GF3', 'GF4'],
            ['GF1', 'GF2'],
            [
                [  # Group 1
                    [['GF3', 'F4', 1.0, 0.5]],  # alpha list
                    ['F1'],  # background list
                ],
                [  # Group 2
                    [['GF4', 'F2', 1.0, 0.8]],  # alpha list
                    ['F3'],  # background list
                ],
            ],
            [0.4, 0.1, 0.3, 0.2],
        ),
        (
            11,
            {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5', 6: 'F6'},
            ['F2', 'F1', 'F4', 'F3', 'F6', 'F5'],
            [
                'H',
                ['F1', 1.0, 1, 0, 0],
                ['F2', 1.0, 2, 0, 0],
                ['F3', 1.0, 3, 0, 0],
                ['F4', 1.0, 4, 0, 0],
            ],
            ['F1', 'F2', 'F3', 'F4', 'F5', 'F6'],
            ['GF1', 'GF2', 'GF3', 'GF4'],
            ['GF1', 'GF2'],
            [
                [  # Group 1
                    [['GF3', 'F5', 1.0, 0.5]],  # alpha list
                    ['F1', 'F2', 'F3'],  # background list
                ],
                [  # Group 2
                    [['GF4', 'F6', 1.0, 0.8]],  # alpha list
                    ['F4'],  # background list
                ],
            ],
            [0.3, 0.1, 0.2, 0.2, 0.1, 0.1],
        ),
        (
            12,
            {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2'},
            ['F2', 'F1', 'F4', 'F3'],
            [
                'H',
                ['F1', 1.0, 1, 0, 0],
                ['F2', 1.0, 2, 0, 0],
                ['F3', 1.0, 3, 0, 0],
                ['F4', 1.0, 4, 0, 0],
            ],
            ['F1', 'F2', 'F3', 'F4'],
            ['GF1', 'GF2', 'GF3', 'GF4'],
            ['GF1', 'GF2'],
            [],
            [0.3, 0.1, 0.3, 0.3],
        ),
        (
            13,
            {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5', 6: 'F6'},
            ['F2', 'F1', 'F4', 'F3', 'F6', 'F5'],
            [
                'V',
                ['F1', 1.0, 1, 0, 0],
                ['F2', 1.0, 2, 0, 0],
                ['F3', 1.0, 3, 0, 0],
                ['F4', 1.0, 4, 0, 0],
            ],
            ['F1', 'F2', 'F3', 'F4', 'F5', 'F6'],
            ['GF1', 'GF2', 'GF3', 'GF4'],
            ['GF1', 'GF2'],
            [
                [  # Group 1
                    [['GF3', 'F5', 1.0, 0.3]],  # alpha list
                    ['F1', 'F3'],  # background list
                ],
                [  # Group 2
                    [['GF4', 'F6', 1.0, 0.7]],  # alpha list
                    ['F4', 'F2'],  # background list
                ],
            ],
            [0.3, 0.1, 0.2, 0.2, 0.1, 0.1],
        ),
        (
            14,
            {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5', 6: 'F6'},
            ['F2', 'F1', 'F4', 'F3', 'F6', 'F5'],
            [
                'H',
                ['F1', 1.0, 1, 0, 0],
                ['F2', 1.0, 2, 0, 0],
                ['F3', 1.0, 3, 1, 0],
                ['F4', 1.0, 3, 2, 0],
            ],
            ['F1', 'F2', 'F3', 'F4', 'F5', 'F6'],
            ['GF1', 'GF2', 'GF3', 'GF4'],
            ['GF1', 'GF2'],
            [
                [  # Group 1
                    [['GF3', 'F5', 1.0, 0.3]],  # alpha list
                    ['F1', 'F3'],  # background list
                ],
                [  # Group 2
                    [['GF4', 'F6', 1.0, 0.7]],  # alpha list
                    ['F4', 'F2'],  # background list
                ],
            ],
            [0.3, 0.1, 0.2, 0.2, 0.1, 0.1],
        ),
        (
            15,
            {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5', 6: 'F6'},
            ['F2', 'F1', 'F4', 'F3', 'F6', 'F5'],
            [
                'V',
                ['F1', 1.0, 1, 0, 0],
                ['F2', 1.0, 2, 0, 0],
                ['F3', 1.0, 3, 1, 0],
                ['F4', 1.0, 3, 2, 0],
            ],
            ['F1', 'F2', 'F3', 'F4', 'F5', 'F6'],
            ['GF1', 'GF2', 'GF3', 'GF4'],
            ['GF1', 'GF2'],
            [
                [  # Group 1
                    [['GF3', 'F5', 1.0, 0.3]],  # alpha list
                    ['F1', 'F3'],  # background list
                ],
                [  # Group 2
                    [['GF4', 'F6', 1.0, 0.7]],  # alpha list
                    ['F4', 'F2'],  # background list
                ],
            ],
            [0.3, 0.1, 0.2, 0.2, 0.1, 0.1],
        ),
        (
            16,
            {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2'},
            ['F2', 'F1', 'F4', 'F3'],
            [
                'V',
                ['F1', 1.0, 1, 0, 0],
                ['F2', 1.0, 2, 0, 0],
                ['F3', 1.0, 3, 1, 0],
                ['F4', 1.0, 3, 2, 0],
            ],
            ['F1', 'F2', 'F3', 'F4'],
            ['GF1', 'GF2', 'GF3', 'GF4'],
            ['GF1', 'GF2'],
            [],
            [0.3, 0.2, 0.2, 0.3],
        ),
        (
            17,
            {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5', 6: 'F6'},
            ['F2', 'F1', 'F4', 'F3', 'F6', 'F5'],
            [
                'H',
                ['F1', 1.0, 1, 0, 0],
                ['F2', 1.0, 2, 0, 0],
                ['F3', 1.0, 3, 0, 0],
                ['F4', 1.0, 4, 0, 0],
                ['F5', 1.0, 5, 0, 0],
            ],
            ['F1', 'F2', 'F3', 'F4', 'F5', 'F6'],
            ['GF1', 'GF2', 'GF3', 'GF4'],
            ['GF1', 'GF2'],
            [
                [  # Group 1
                    [['GF3', 'F6', 1.0, 0.3]],  # alpha list
                    ['F1', 'F3', 'F4', 'F2'],  # background list
                ]
            ],
            [0.3, 0.1, 0.2, 0.2, 0.1, 0.1],
        ),
        (
            18,
            {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5', 6: 'F6', 7: 'F7'},
            ['F2', 'F1', 'F4', 'F3', 'F6', 'F5', 'F7'],
            [
                'H',
                ['F1', 1.0, 1, 0, 0],
                ['F2', 1.0, 2, 0, 0],
                ['F3', 1.0, 3, 0, 0],
                ['F4', 1.0, 4, 0, 0],
                ['F5', 1.0, 5, 0, 0],
            ],
            ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7'],
            ['GF1', 'GF2', 'GF3', 'GF4'],
            ['GF1', 'GF2'],
            [
                [  # Group 1
                    [['GF3', 'F6', 1.0, 0.3]],  # alpha list
                    ['F1', 'F3', 'F4', 'F2'],  # background list
                ],
                [  # Group 2
                    [['GF4', 'F7', 1.0, 0.9]],  # alpha list
                    ['F5'],  # background list
                ],
            ],
            [0.2, 0.1, 0.2, 0.2, 0.1, 0.1, 0.1],
        ),
        (
            19,
            {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5', 6: 'F6', 7: 'F7'},
            ['F2', 'F1', 'F4', 'F3', 'F6', 'F5', 'F7'],
            [
                'H',
                ['F1', 1.0, 1, 0, 0],
                ['F2', 1.0, 2, 1, 1],
                ['F3', 1.0, 2, 1, 2],
                ['F4', 1.0, 2, 2, 1],
                ['F5', 1.0, 2, 2, 2],
            ],
            ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7'],
            ['GF1', 'GF2', 'GF3', 'GF4'],
            ['GF1', 'GF2'],
            [
                [  # Group 1
                    [['GF3', 'F6', 1.0, 0.3]],  # alpha list
                    ['F1', 'F3', 'F4', 'F2'],  # background list
                ],
                [  # Group 2
                    [['GF4', 'F7', 1.0, 0.9]],  # alpha list
                    ['F5'],  # background list
                ],
            ],
            [0.2, 0.1, 0.2, 0.2, 0.1, 0.1, 0.1],
        ),
        (
            20,
            {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5', 6: 'F6'},
            ['F2', 'F1', 'F4', 'F3', 'F6', 'F5'],
            [
                'V',
                ['F4', 0.4, 1, 0, 0],
                ['F2', 1.0, 2, 1, 0],
                ['F3', 1.0, 2, 2, 1],
                ['F4', 0.3, 2, 2, 2],
                ['F4', 0.3, 2, 3, 0],
            ],
            ['F4', 'F2', 'F3', 'F1', 'F5', 'F6'],
            ['GF1', 'GF2', 'GF3', 'GF4', 'GF5'],
            ['GF1', 'GF2'],
            [
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
            [0.3, 0.1, 0.2, 0.2, 0.1, 0.1],
        ),
        (
            21,
            {3: 'F1', 2: 'F3', 1: 'F4'},
            ['F1', 'F4', 'F3'],
            [
                'V',
                ['F4', 0.2, 1, 0, 0],
                ['F4', 0.2, 2, 1, 0],
                ['F3', 1.0, 2, 2, 1],
                ['F4', 0.3, 2, 2, 2],
                ['F4', 0.3, 2, 3, 0],
            ],
            ['F4', 'F3', 'F1'],
            ['GF1', 'GF2', 'GF3', 'GF4'],
            ['GF1', 'GF2'],
            [
                [  # Group 1
                    [['GF3', 'F1', 1.0, 0.3]],  # alpha list
                    ['F4'],  # background list
                ],
            ],
            [0.3, 0.3, 0.4],
        ),
        (
            22,
            {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5'},
            ['F1', 'F4', 'F3', 'F5', 'F2'],
            [
                'H',
                ['F1', 1.0, 1, 0, 0],
                ['F2', 1.0, 2, 1, 0],
                ['F3', 0.5, 2, 2, 1],
                ['F4', 1.0, 2, 2, 2],
                ['F3', 0.5, 2, 3, 1],
                ['F5', 1.0, 2, 3, 2],
            ],
            ['F1', 'F2', 'F3', 'F4', 'F5'],
            ['GF1', 'GF2', 'GF3', 'GF4'],
            ['GF1', 'GF2'],
            [],
            [0.3, 0.1, 0.2, 0.2, 0.2],
        ),
        (
            23,
            {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5'},
            ['F1', 'F4', 'F3', 'F5', 'F2'],
            [
                'H',
                ['F1', 1.0, 1, 0, 0],
                ['F5', 0.5, 2, 1, 0],
                ['F3', 0.5, 2, 2, 1],
                ['F4', 1.0, 2, 2, 2],
                ['F3', 0.5, 2, 3, 1],
                ['F5', 0.5, 2, 3, 2],
            ],
            ['F1', 'F5', 'F3', 'F4', 'F2'],
            ['GF1', 'GF2', 'GF3', 'GF4'],
            ['GF1', 'GF2'],
            [
                [  # Group 1
                    [['GF3', 'F2', 1.0, 0.4]],  # alpha list
                    ['F5', 'F3'],  # background list
                ],
            ],
            [0.3, 0.1, 0.2, 0.2, 0.2],
        ),
        (
            24,
            {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5'},
            ['F1', 'F4', 'F3', 'F5', 'F2'],
            [
                'H',
                ['F1', 1.0, 1, 0, 0],
                ['F5', 0.5, 2, 1, 0],
                ['F3', 0.5, 2, 2, 1],
                ['F4', 1.0, 2, 2, 2],
                ['F3', 0.5, 2, 3, 1],
                ['F5', 0.5, 2, 3, 2],
            ],
            ['F1', 'F5', 'F3', 'F4', 'F2'],
            ['GF1', 'GF2', 'GF3', 'GF4', 'GF5'],
            ['GF1', 'GF2'],
            [
                [  # Group 1
                    [  # alpha list
                        ['GF3', 'F2', 0.4, 0.4],
                        ['GF4', 'F2', 0.3, 0.4],
                        ['GF5', 'F2', 0.3, 0.4],
                    ],
                    ['F5', 'F3'],  # background list
                ]
            ],
            [0.3, 0.1, 0.2, 0.2, 0.2],
        ),
    ],
)
def test_Trunc2DCubic(
    case_number: int,
    facies_table: FaciesTableType,
    facies_in_zone: List[str],
    truncation_rule: CubicTruncationRuleStructureType,
    facies_in_truncation_rule: List[str],
    gaussian_fields_in_zone: List[str],
    gaussian_fields_for_background_facies: List[str],
    overlay_groups: OverlayGroupType,
    facies_probabilities: List[float],
    facies_reference_file: Path,
    output_model_file_name_1: Path,
    output_model_file_name_2: Path,
    out_poly_file_1: Path,
    out_poly_file_2: Path,
    cubic_gauss_field_files: List[Path],
    facies_output_file_vectorized: Path,
    facies_output_file: Path,
) -> None:
    print('')
    print('******** Case number: ' + str(case_number) + ' *********')
    truncRule, truncRule2 = initialize_write_read(
        outputModelFileName1=output_model_file_name_1,
        outputModelFileName2=output_model_file_name_2,
        fTable=facies_table,
        faciesInZone=facies_in_zone,
        gaussFieldsInZone=gaussian_fields_in_zone,
        gaussFieldsForBGFacies=gaussian_fields_for_background_facies,
        truncStructure=truncation_rule,
        overlayGroups=overlay_groups,
        debug_level=Debug.OFF,
    )
    nGaussFields = truncRule.getNGaussFieldsInModel()
    getClassName(truncRule)
    getFaciesInTruncRule(truncRule, truncRule2, facies_in_truncation_rule)
    truncMapPolygons(
        truncRule=truncRule,
        truncRule2=truncRule2,
        faciesProb=facies_probabilities,
        outPolyFile1=out_poly_file_1,
        outPolyFile2=out_poly_file_2,
    )
    apply_truncations(
        truncRule=truncRule,
        faciesReferenceFile=facies_reference_file,
        nGaussFields=nGaussFields,
        gaussFieldFiles=cubic_gauss_field_files,
        faciesOutputFile=facies_output_file,
    )

    apply_truncations_vectorized(
        truncRule=truncRule,
        faciesReferenceFile=facies_reference_file,
        nGaussFields=nGaussFields,
        gaussFieldFiles=cubic_gauss_field_files,
        faciesOutputFile=facies_output_file_vectorized,
    )


if __name__ == '__main__':
    pytest.main([__file__])
