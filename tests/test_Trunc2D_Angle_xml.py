#!/bin/env python
# -*- coding: utf-8 -*-
import filecmp
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List
from xml.etree.ElementTree import Element

import numpy as np
import pytest

from aps.algorithms.APSMainFaciesTable import APSMainFaciesTable
from aps.algorithms.truncation_rules import Trunc2D_Angle
from aps.utils.constants.simple import Debug
from aps.utils.types import (
    FaciesListType,
    FaciesTableType,
    GaussianFieldsListType,
    NonCubicTruncationRuleStructureType,
    OverlayGroupType,
)
from aps.utils.xmlUtils import prettify
from tests.constants import (
    KEYRESOLUTION,
    USE_CONST_TRUNC_PARAM,
)
from tests.helpers import (
    apply_truncations,
    apply_truncations_vectorized,
    getFaciesInTruncRule,
    truncMapPolygons,
)


def interpretXMLModelFileAndWrite(
    modelFileName,
    outputModelFileName,
    fTable,
    faciesInZone,
    gaussFieldsInZone,
    keyResolution,
    debug_level=Debug.OFF,
):
    # Read test model file with truncation rule into xml tree
    ET_Tree = ET.parse(modelFileName)
    root = ET_Tree.getroot()
    # Read TruncationRule keyword
    trRule = root.find('TruncationRule')

    # Get name of truncation rule
    truncRuleName = trRule[0].tag
    print('Truncation rule: ' + truncRuleName)

    mainFaciesTable = APSMainFaciesTable(facies_table=fTable)

    # Create truncation rule object from input data, not read from file
    truncRuleOut = Trunc2D_Angle(
        trRule,
        mainFaciesTable,
        faciesInZone,
        gaussFieldsInZone,
        keyResolution,
        debug_level=debug_level,
        modelFileName=modelFileName,
    )
    # Create and write XML tree
    createXMLTreeAndWriteFile(truncRuleOut, outputModelFileName)

    return truncRuleOut


def createXMLTreeAndWriteFile(truncRuleInput, outputModelFileName):
    # Build an XML tree with top as root
    # from truncation object and write it
    assert truncRuleInput is not None
    fmu_attributes = []
    top = Element('TEST_TruncationRule')
    truncRuleInput.XMLAddElement(top, 1, 1, fmu_attributes)
    rootReformatted = prettify(top)
    print(f'Write file: {outputModelFileName}')
    with open(outputModelFileName, 'w', encoding='utf-8') as file:
        file.write(rootReformatted)


def createTrunc(
    outputModelFileName,
    fTable,
    faciesInZone,
    gaussFieldsInZone,
    gaussFieldsForBGFacies,
    truncStructure,
    overlayGroups,
    useConstTruncParam,
    keyResolution,
    debug_level=Debug.OFF,
):
    mainFaciesTable = APSMainFaciesTable(facies_table=fTable)

    # Create an object and initialize it
    truncRuleOut = Trunc2D_Angle()
    truncRuleOut.initialize(
        mainFaciesTable,
        faciesInZone,
        gaussFieldsInZone,
        gaussFieldsForBGFacies,
        truncStructure,
        overlayGroups,
        useConstTruncParam,
        keyResolution,
        debug_level,
    )

    # Build an xml tree with the data and write it to file
    createXMLTreeAndWriteFile(truncRuleOut, outputModelFileName)
    return truncRuleOut


def initialize_write_read(
    outputModelFileName1,
    outputModelFileName2,
    fTable,
    faciesInZone,
    gaussFieldsInZone,
    gaussFieldsForBGFacies,
    truncStructure,
    overlayGroups,
    useConstTruncParam,
    keyResolution,
    debug_level=Debug.OFF,
):
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
        useConstTruncParam,
        keyResolution,
        debug_level,
    )
    inputFile = file1

    # Write datastructure:
    #    truncRule.writeContentsInDataStructure()
    # Read the previously written file as and XML file and write it out again to a new file
    # Global variable truncRule2
    print('In initialize_write_read')
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
    print('  Compare xml file created with xml written')
    check = filecmp.cmp(file1, file2)
    print(f'  Compare file: {file1} and file: {file2}')
    assert check is True
    if not check:
        raise ValueError('  Error: Files are different')
    else:
        print('  Files are equal: OK')
    return truncRuleA, truncRuleB


def getClassName(truncRule):
    # TODO: Generalize
    assert truncRule is not None
    name = truncRule.getClassName()
    assert name == 'Trunc2D_Angle'


@pytest.mark.parametrize('kind', ['angle'])
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
            {2: 'F2', 1: 'F1', 3: 'F3'},
            ['F1', 'F2', 'F3'],
            [
                ['F3', -90.0, 1.0, True],
                ['F2', +45.0, 1.0, False],
                ['F1', +45.0, 1.0, True],
            ],
            ['F3', 'F2', 'F1'],
            ['GF1', 'GF2', 'GF3', 'GF4'],
            ['GF1', 'GF2'],
            [],
            [0.5, 0.3, 0.2],
        ),
        (
            2,
            {2: 'F2', 1: 'F1', 3: 'F3'},
            ['F2', 'F3', 'F1'],
            [
                ['F1', +135.0, 1.0, True],
                ['F2', +45.0, 1.0, True],
                ['F3', +45.0, 1.0, False],
            ],
            ['F1', 'F2', 'F3'],
            ['GF1', 'GF2', 'GF3', 'GF4'],
            ['GF1', 'GF2'],
            [],
            [0.01, 0.8, 0.19],
        ),
        (
            3,
            {1: 'F1', 2: 'F2', 3: 'F3', 4: 'F4', 5: 'F5'},
            ['F2', 'F3', 'F1', 'F5', 'F4'],
            [
                ['F1', +135.0, 1.0, False],
                ['F2', +45.0, 1.0, True],
                ['F3', +45.0, 1.0, True],
            ],
            ['F1', 'F2', 'F3', 'F5', 'F4'],
            ['GF1', 'GF2', 'GF3', 'GF4', 'GF5', 'GF6'],
            ['GF1', 'GF2'],
            [
                # Group 1
                [[['GF3', 'F5', 1.0, 0.9]], ['F1']],
                # Group 2
                [[['GF4', 'F4', 1.0, 0.0]], ['F3']],
            ],
            [0.3, 0.2, 0.3, 0.1, 0.1],
        ),
        (
            4,
            {1: 'F1', 2: 'F2', 3: 'F3', 4: 'F4', 5: 'F5'},
            ['F2', 'F3', 'F1', 'F5', 'F4'],
            [
                ['F1', -135.0, 1.0, True],
                ['F3', +90.0, 1.0, False],
                ['F2', +45.0, 1.0, True],
            ],
            ['F1', 'F3', 'F2', 'F5', 'F4'],
            ['GF1', 'GF2', 'GF3', 'GF4', 'GF5', 'GF6'],
            ['GF1', 'GF2'],
            [
                # Group1
                [[['GF3', 'F5', 1.0, 0.0]], ['F2', 'F1']],
                # Group2
                [[['GF4', 'F4', 1.0, 1.0]], ['F3']],
            ],
            [0.3, 0.2, 0.3, 0.1, 0.1],
        ),
        (
            5,
            {1: 'F1', 2: 'F2', 3: 'F3', 4: 'F4', 5: 'F5'},
            ['F2', 'F3', 'F1', 'F5', 'F4'],
            [
                ['F1', -180.0, 0.5, False],
                ['F3', +180.0, 1.0, True],
                ['F1', 0.0, 0.5, True],
                ['F2', 35.0, 0.7, False],
                ['F2', -35.0, 0.3, True],
            ],
            ['F1', 'F3', 'F2', 'F5', 'F4'],
            ['GF1', 'GF2', 'GF3', 'GF4'],
            ['GF1', 'GF2'],
            [
                # Group1
                [[['GF3', 'F5', 1.0, 0.0]], ['F3', 'F2']],
                # Group2
                [[['GF4', 'F4', 1.0, 0.0]], ['F1']],
            ],
            [0.2, 0.3, 0.3, 0.1, 0.1],
        ),
        (
            6,
            {1: 'F1', 2: 'F2', 3: 'F3', 4: 'F4', 5: 'F5'},
            ['F2', 'F3', 'F1', 'F5', 'F4'],
            [
                ['F1', -180.0, 1.0, True],
                ['F3', -170.0, 0.5, True],
                ['F3', -160.0, 0.5, True],
                ['F2', -150.0, 0.7, False],
                ['F2', -140.0, 0.3, True],
            ],
            ['F1', 'F3', 'F2', 'F5', 'F4'],
            ['GF1', 'GF2', 'GF3', 'GF4'],
            ['GF1', 'GF2'],
            [
                # Group1
                [[['GF3', 'F5', 1.0, 0.0]], ['F3', 'F2']],
                # Group2
                [[['GF4', 'F4', 1.0, 0.0]], ['F1']],
            ],
            [0.2, 0.3, 0.3, 0.1, 0.1],
        ),
        (
            7,
            {1: 'F1', 2: 'F2', 3: 'F3', 4: 'F4', 5: 'F5', 6: 'F6', 7: 'F7', 8: 'F8'},
            ['F2', 'F3', 'F1', 'F5', 'F4', 'F6', 'F7', 'F8'],
            [
                ['F1', -180.0, 0.5, True],
                ['F3', -170.0, 0.5, True],
                ['F7', 10.0, 1.0, True],
                ['F1', -60.0, 0.5, True],
                ['F3', -160.0, 0.5, False],
                ['F2', -150.0, 0.05, False],
                ['F2', +140.0, 0.95, False],
                ['F6', 120.0, 1.0, True],
            ],
            ['F1', 'F3', 'F7', 'F2', 'F6', 'F5', 'F4', 'F8'],
            ['GF1', 'GF2', 'GF3', 'GF4', 'GF5', 'GF6'],
            ['GF1', 'GF2'],
            [
                # Group1
                [[['GF3', 'F5', 1.0, 0.0]], ['F3', 'F2']],
                # Group2
                [[['GF4', 'F4', 1.0, 0.0]], ['F1']],
                # Group3
                [[['GF5', 'F8', 1.0, 1.0]], ['F7']],
            ],
            [0.15, 0.3, 0.2, 0.1, 0.1, 0.05, 0.05, 0.05],
        ),
        (
            8,
            {1: 'F1', 2: 'F2', 3: 'F3', 4: 'F4', 5: 'F5', 6: 'F6', 7: 'F7', 8: 'F8'},
            ['F2', 'F3', 'F1', 'F5', 'F4', 'F6', 'F7', 'F8'],
            [
                ['F1', -180.0, 0.5, True],
                ['F3', -170.0, 0.5, False],
                ['F7', 10.0, 1.0, True],
                ['F1', -60.0, 0.5, True],
                ['F3', -160.0, 0.5, False],
                ['F2', -150.0, 0.05, True],
                ['F2', +140.0, 0.95, False],
                ['F6', 120.0, 1.0, True],
            ],
            ['F1', 'F3', 'F7', 'F2', 'F6', 'F5', 'F4', 'F8'],
            ['GF1', 'GF2', 'GF3', 'GF4', 'GF5', 'GF6'],
            ['GF1', 'GF2'],
            [
                # Group1
                [[['GF3', 'F5', 1.0, 0.0]], ['F3', 'F2']],
                # Group2
                [
                    [
                        ['GF4', 'F4', 0.3, 0.0],
                        ['GF5', 'F8', 0.3, 0.0],
                        ['GF6', 'F4', 0.4, 0.0],
                    ],
                    ['F1'],
                ],
                # Group3
                [[['GF5', 'F8', 0.7, 1.0], ['GF4', 'F4', 0.3, 1.0]], ['F7']],
            ],
            [0.15, 0.3, 0.2, 0.1, 0.1, 0.05, 0.05, 0.05],
        ),
        (
            9,
            {1: 'F1', 2: 'F2', 3: 'F3', 4: 'F4', 5: 'F5', 6: 'F6', 7: 'F7', 8: 'F8'},
            ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8'],
            [
                ['F1', -180.0, 0.5, False],
                ['F3', -170.0, 0.5, True],
                ['F7', 10.0, 1.0, True],
                ['F1', -60.0, 0.5, True],
                ['F3', -160.0, 0.5, True],
                ['F2', -150.0, 0.05, False],
                ['F2', +140.0, 0.95, True],
                ['F6', 120.0, 1.0, True],
            ],
            ['F1', 'F3', 'F7', 'F2', 'F6', 'F5', 'F4', 'F8'],
            ['GF1', 'GF2', 'GF3', 'GF4', 'GF5', 'GF6'],
            ['GF1', 'GF2'],
            [
                # Group1
                [[['GF3', 'F5', 1.0, 0.0]], ['F3', 'F2']],
                # Group2
                [
                    [
                        ['GF4', 'F4', 0.3, 0.0],
                        ['GF5', 'F8', 0.3, 0.0],
                        ['GF6', 'F4', 0.4, 0.0],
                    ],
                    ['F1'],
                ],
                # Group3
                [[['GF5', 'F8', 0.7, 1.0], ['GF4', 'F4', 0.3, 1.0]], ['F7']],
            ],
            [0.0, 0.0, 0.0, 0.01, 0.0, 0.0, 0.0, 0.99],
        ),
    ],
)
def test_non_cubic_truncation_rule(
    case_number: int,
    facies_table: FaciesTableType,
    facies_in_zone: FaciesListType,
    truncation_rule: NonCubicTruncationRuleStructureType,
    facies_in_truncation_rule: FaciesListType,
    gaussian_fields_in_zone: GaussianFieldsListType,
    gaussian_fields_for_background_facies: GaussianFieldsListType,
    overlay_groups: OverlayGroupType,
    facies_probabilities: List[float],
    facies_reference_file: Path,
    output_model_file_name_1,
    output_model_file_name_2,
    out_poly_file_1,
    out_poly_file_2,
    cubic_gauss_field_files,
    facies_output_file_vectorized,
    facies_output_file,
    non_cubic_gauss_field_files,
):
    truncRule, truncRule2 = initialize_write_read(
        outputModelFileName1=output_model_file_name_1,
        outputModelFileName2=output_model_file_name_2,
        fTable=facies_table,
        faciesInZone=facies_in_zone,
        gaussFieldsInZone=gaussian_fields_in_zone,
        gaussFieldsForBGFacies=gaussian_fields_for_background_facies,
        truncStructure=truncation_rule,
        overlayGroups=overlay_groups,
        useConstTruncParam=USE_CONST_TRUNC_PARAM,
        keyResolution=KEYRESOLUTION,
        debug_level=Debug.OFF,
    )
    nGaussFields = truncRule.getNGaussFieldsInModel()
    getClassName(truncRule)
    getFaciesInTruncRule(
        truncRule=truncRule,
        truncRule2=truncRule2,
        faciesInTruncRule=facies_in_truncation_rule,
    )
    facies_prob_numpy = np.asarray(facies_probabilities)
    truncMapPolygons(
        truncRule=truncRule,
        truncRule2=truncRule2,
        faciesProb=facies_prob_numpy,
        outPolyFile1=out_poly_file_1,
        outPolyFile2=out_poly_file_2,
    )
    apply_truncations(
        truncRule=truncRule,
        faciesReferenceFile=facies_reference_file,
        nGaussFields=nGaussFields,
        gaussFieldFiles=non_cubic_gauss_field_files,
        faciesOutputFile=facies_output_file,
    )

    apply_truncations_vectorized(
        truncRule=truncRule,
        faciesReferenceFile=facies_reference_file,
        nGaussFields=nGaussFields,
        gaussFieldFiles=non_cubic_gauss_field_files,
        faciesOutputFile=facies_output_file_vectorized,
    )


if __name__ == '__main__':
    pytest.main([__file__])
