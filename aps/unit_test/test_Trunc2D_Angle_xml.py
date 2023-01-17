#!/bin/env python
# -*- coding: utf-8 -*-
import filecmp
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
import numpy as np

from aps.algorithms.APSMainFaciesTable import APSMainFaciesTable
from aps.algorithms.truncation_rules import Trunc2D_Angle
from aps.unit_test.constants import (
    ANGLE_GAUSS_FIELD_FILES, FACIES_OUTPUT_FILE, FACIES_OUTPUT_FILE_VECTORIZED, OUTPUT_MODEL_FILE_NAME1,
    OUTPUT_MODEL_FILE_NAME2, OUT_POLY_FILE1, OUT_POLY_FILE2, USE_CONST_TRUNC_PARAM, KEYRESOLUTION
)
from aps.unit_test.helpers import apply_truncations, getFaciesInTruncRule, truncMapPolygons, apply_truncations_vectorized
from aps.utils.constants.simple import Debug
from aps.utils.xmlUtils import prettify


def interpretXMLModelFileAndWrite(
        modelFileName, outputModelFileName, fTable, faciesInZone, gaussFieldsInZone, keyResolution, debug_level=Debug.OFF
):
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
    # print('Number of gauss fields required for truncation rule: ' + str(nGaussFields))

    mainFaciesTable = APSMainFaciesTable(facies_table=fTable)

    # Create truncation rule object from input data, not read from file
    truncRuleOut = Trunc2D_Angle(
        trRule, mainFaciesTable, faciesInZone, gaussFieldsInZone, keyResolution,
        debug_level=debug_level, modelFileName=modelFileName
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
        outputModelFileName, fTable, faciesInZone, gaussFieldsInZone, gaussFieldsForBGFacies,
        truncStructure, overlayGroups, useConstTruncParam, keyResolution, debug_level=Debug.OFF
):
    mainFaciesTable = APSMainFaciesTable(facies_table=fTable)

    # Create an object and initialize it
    truncRuleOut = Trunc2D_Angle()
    truncRuleOut.initialize(
        mainFaciesTable, faciesInZone, gaussFieldsInZone, gaussFieldsForBGFacies,
        truncStructure, overlayGroups, useConstTruncParam, keyResolution, debug_level
    )

    # Build an xml tree with the data and write it to file
    createXMLTreeAndWriteFile(truncRuleOut, outputModelFileName)
    return truncRuleOut


def initialize_write_read(
        outputModelFileName1, outputModelFileName2, fTable, faciesInZone, gaussFieldsInZone,
        gaussFieldsForBGFacies, truncStructure, overlayGroups, useConstTruncParam, keyResolution, debug_level=Debug.OFF
):
    file1 = outputModelFileName1
    file2 = outputModelFileName2
    # Create an object for truncation rule and write to file
    # Global variable truncRule
    truncRuleA = createTrunc(
        file1, fTable, faciesInZone, gaussFieldsInZone, gaussFieldsForBGFacies,
        truncStructure, overlayGroups, useConstTruncParam, keyResolution, debug_level
    )
    inputFile = file1

    # Write datastructure:
    #    truncRule.writeContentsInDataStructure()
    # Read the previously written file as and XML file and write it out again to a new file
    # Global variable truncRule2
    truncRuleB = interpretXMLModelFileAndWrite(inputFile, file2, fTable, faciesInZone, gaussFieldsInZone, keyResolution, debug_level)

    # Compare the original xml file created in createTrunc and the xml file written by interpretXMLModelFileAndWrite
    check = filecmp.cmp(file1, file2)
    print('Compare file: {} and file: {}'.format(file1, file2))
    assert check is True
    if not check:
        raise ValueError('Error: Files are different')
    else:
        print('Files are equal: OK')
    return truncRuleA, truncRuleB


def getClassName(truncRule):
    # TODO: Generalize
    assert truncRule is not None
    name = truncRule.getClassName()
    assert name == 'Trunc2D_Angle'


def test_Trunc2DAngle():
    nCase = 9
    start = 1
    end = 9
    for testCase in range(start, end + 1):
        print('')
        print('********* Case number: ' + str(testCase) + ' **********')

        if testCase == 1:
            test_case_1()

        elif testCase == 2:
            test_case_2()

        elif testCase == 3:
            test_case_3()

        elif testCase == 4:
            test_case_4()

        elif testCase == 5:
            test_case_5()

        elif testCase == 6:
            test_case_6()

        elif testCase == 7:
            test_case_7()

        elif testCase == 8:
            test_case_8()

        elif testCase == 9:
            test_case_9()

            # elif testCase == 10:
            #     test_case_10()
            #
            # elif testCase == 11:
            #     test_case_11()
            #
            # elif testCase == 12:
            #     test_case_12()
            #
            # elif testCase == 13:
            #     test_case_13()


def test_case_1():
    run(
        fTable={2: 'F2', 1: 'F1', 3: 'F3'},
        faciesInZone=['F1', 'F2', 'F3'],
        truncStructure=[['F3', -90.0, 1.0, True], ['F2', +45.0, 1.0, False], ['F1', +45.0, 1.0, True]],
        faciesInTruncRule=['F3', 'F2', 'F1'],
        gaussFieldsInZone=['GF1', 'GF2', 'GF3', 'GF4'],
        gaussFieldsForBGFacies=['GF1', 'GF2'],
        overlayGroups=[],
        faciesProb=[0.5, 0.3, 0.2],
        faciesReferenceFile=get_facies_reference_file_path(1),
    )


def test_case_2():
    run(
        fTable={2: 'F2', 1: 'F1', 3: 'F3'},
        faciesInZone=['F2', 'F3', 'F1'],
        truncStructure=[['F1', +135.0, 1.0, True], ['F2', +45.0, 1.0, True], ['F3', +45.0, 1.0, False]],
        faciesInTruncRule=['F1', 'F2', 'F3'],
        gaussFieldsInZone=['GF1', 'GF2', 'GF3', 'GF4'],
        gaussFieldsForBGFacies=['GF1', 'GF2'],
        overlayGroups=[],
        faciesProb=[0.01, 0.8, 0.19],
        faciesReferenceFile=get_facies_reference_file_path(2),
    )


def test_case_3():
    overlayGroups = []

    # Group1
    alphaList = [['GF3', 'F5', 1.0, 0.9]]
    backgroundList = ['F1']
    overlayGroup = [alphaList, backgroundList]
    overlayGroups.append(overlayGroup)

    # Group2
    alphaList = [['GF4', 'F4', 1.0, 0.0]]
    backgroundList = ['F3']
    overlayGroup = [alphaList, backgroundList]
    overlayGroups.append(overlayGroup)

    faciesProb = [0.3, 0.2, 0.3, 0.1, 0.1]
    faciesReferenceFile = get_facies_reference_file_path(3)
    run(
        fTable={1: 'F1', 2: 'F2', 3: 'F3', 4: 'F4', 5: 'F5'},
        faciesInZone=['F2', 'F3', 'F1', 'F5', 'F4'],
        truncStructure=[['F1', +135.0, 1.0, False], ['F2', +45.0, 1.0, True], ['F3', +45.0, 1.0, True]],
        faciesInTruncRule=['F1', 'F2', 'F3', 'F5', 'F4'],
        gaussFieldsInZone=['GF1', 'GF2', 'GF3', 'GF4', 'GF5', 'GF6'],
        gaussFieldsForBGFacies=['GF1', 'GF2'],
        overlayGroups=overlayGroups,
        faciesProb=[0.3, 0.2, 0.3, 0.1, 0.1],
        faciesReferenceFile=get_facies_reference_file_path(3),
    )


def test_case_4():
    overlayGroups = []

    # Group1
    alphaList = [['GF3', 'F5', 1.0, 0.0]]
    backgroundList = ['F2', 'F1']
    overlayGroup = [alphaList, backgroundList]
    overlayGroups.append(overlayGroup)

    # Group2
    alphaList = [['GF4', 'F4', 1.0, 1.0]]
    backgroundList = ['F3']
    overlayGroup = [alphaList, backgroundList]
    overlayGroups.append(overlayGroup)

    run(
        fTable={1: 'F1', 2: 'F2', 3: 'F3', 4: 'F4', 5: 'F5'},
        faciesInZone=['F2', 'F3', 'F1', 'F5', 'F4'],
        truncStructure=[['F1', -135.0, 1.0, True], ['F3', +90.0, 1.0, False], ['F2', +45.0, 1.0, True]],
        faciesInTruncRule=['F1', 'F3', 'F2', 'F5', 'F4'],
        gaussFieldsInZone=['GF1', 'GF2', 'GF3', 'GF4', 'GF5', 'GF6'],
        gaussFieldsForBGFacies=['GF1', 'GF2'],
        overlayGroups=overlayGroups,
        faciesProb=[0.3, 0.2, 0.3, 0.1, 0.1],
        faciesReferenceFile=get_facies_reference_file_path(4),
    )


def test_case_5():
    overlayGroups = []

    # Group1
    alphaList = [['GF3', 'F5', 1.0, 0.0]]
    backgroundList = ['F3', 'F2']
    overlayGroup = [alphaList, backgroundList]
    overlayGroups.append(overlayGroup)

    # Group2
    alphaList = [['GF4', 'F4', 1.0, 0.0]]
    backgroundList = ['F1']
    overlayGroup = [alphaList, backgroundList]
    overlayGroups.append(overlayGroup)

    run(
        fTable={1: 'F1', 2: 'F2', 3: 'F3', 4: 'F4', 5: 'F5'},
        faciesInZone=['F2', 'F3', 'F1', 'F5', 'F4'],
        truncStructure=[
            ['F1', -180.0, 0.5, False], ['F3', +180.0, 1.0, True], ['F1', 0.0, 0.5, True], ['F2', 35.0, 0.7, False], ['F2', -35.0, 0.3, True]
        ],
        faciesInTruncRule=['F1', 'F3', 'F2', 'F5', 'F4'],
        gaussFieldsInZone=['GF1', 'GF2', 'GF3', 'GF4'],
        gaussFieldsForBGFacies=['GF1', 'GF2'],
        overlayGroups=overlayGroups,
        faciesProb=[0.2, 0.3, 0.3, 0.1, 0.1],
        faciesReferenceFile=get_facies_reference_file_path(5),
    )


def test_case_6():
    overlayGroups = []

    # Group1
    alphaList = [['GF3', 'F5', 1.0, 0.0]]
    backgroundList = ['F3', 'F2']
    overlayGroup = [alphaList, backgroundList]
    overlayGroups.append(overlayGroup)

    # Group2
    alphaList = [['GF4', 'F4', 1.0, 0.0]]
    backgroundList = ['F1']
    overlayGroup = [alphaList, backgroundList]
    overlayGroups.append(overlayGroup)

    run(
        fTable={1: 'F1', 2: 'F2', 3: 'F3', 4: 'F4', 5: 'F5'},
        faciesInZone=['F2', 'F3', 'F1', 'F5', 'F4'],
        truncStructure=[
            ['F1', -180.0, 1.0, True], ['F3', -170.0, 0.5, True], ['F3', -160.0, 0.5, True], ['F2', -150.0, 0.7, False], ['F2', -140.0, 0.3, True]
        ],
        faciesInTruncRule=['F1', 'F3', 'F2', 'F5', 'F4'],
        gaussFieldsInZone=['GF1', 'GF2', 'GF3', 'GF4'],
        gaussFieldsForBGFacies=['GF1', 'GF2'],
        overlayGroups=overlayGroups,
        faciesProb=[0.2, 0.3, 0.3, 0.1, 0.1],
        faciesReferenceFile=get_facies_reference_file_path(6),
    )


def test_case_7():
    overlayGroups = []

    # Group1
    alphaList = [['GF3', 'F5', 1.0, 0.0]]
    backgroundList = ['F3', 'F2']
    overlayGroup = [alphaList, backgroundList]
    overlayGroups.append(overlayGroup)

    # Group2
    alphaList = [['GF4', 'F4', 1.0, 0.0]]
    backgroundList = ['F1']
    overlayGroup = [alphaList, backgroundList]
    overlayGroups.append(overlayGroup)

    # Group3
    alphaList = [['GF5', 'F8', 1.0, 1.0]]
    backgroundList = ['F7']
    overlayGroup = [alphaList, backgroundList]
    overlayGroups.append(overlayGroup)

    run(
        fTable={1: 'F1', 2: 'F2', 3: 'F3', 4: 'F4', 5: 'F5', 6: 'F6', 7: 'F7', 8: 'F8'},
        faciesInZone=['F2', 'F3', 'F1', 'F5', 'F4', 'F6', 'F7', 'F8'],
        truncStructure=[
            ['F1', -180.0, 0.5, True], ['F3', -170.0, 0.5, True], ['F7', 10.0, 1.0, True], ['F1', -60.0, 0.5, True],
            ['F3', -160.0, 0.5, False], ['F2', -150.0, 0.05, False], ['F2', +140.0, 0.95, False], ['F6', 120.0, 1.0, True]
        ],
        faciesInTruncRule=['F1', 'F3', 'F7', 'F2', 'F6', 'F5', 'F4', 'F8'],
        gaussFieldsInZone=['GF1', 'GF2', 'GF3', 'GF4', 'GF5', 'GF6'],
        gaussFieldsForBGFacies=['GF1', 'GF2'],
        overlayGroups=overlayGroups,
        faciesProb=[0.15, 0.3, 0.2, 0.1, 0.1, 0.05, 0.05, 0.05],
        faciesReferenceFile=get_facies_reference_file_path(7),
    )


def test_case_8():
    overlayGroups = []

    # Group1
    alphaList = [['GF3', 'F5', 1.0, 0.0]]
    backgroundList = ['F3', 'F2']
    overlayGroup = [alphaList, backgroundList]
    overlayGroups.append(overlayGroup)

    # Group2
    alphaList = [
        ['GF4', 'F4', 0.3, 0.0],
        ['GF5', 'F8', 0.3, 0.0],
        ['GF6', 'F4', 0.4, 0.0]
    ]
    backgroundList = ['F1']
    overlayGroup = [alphaList, backgroundList]
    overlayGroups.append(overlayGroup)

    # Group3
    alphaList = [
        ['GF5', 'F8', 0.7, 1.0],
        ['GF4', 'F4', 0.3, 1.0]
    ]
    backgroundList = ['F7']
    overlayGroup = [alphaList, backgroundList]
    overlayGroups.append(overlayGroup)

    run(
        fTable={1: 'F1', 2: 'F2', 3: 'F3', 4: 'F4', 5: 'F5', 6: 'F6', 7: 'F7', 8: 'F8'},
        faciesInZone=['F2', 'F3', 'F1', 'F5', 'F4', 'F6', 'F7', 'F8'],
        truncStructure=[
            ['F1', -180.0, 0.5, True], ['F3', -170.0, 0.5, False], ['F7', 10.0, 1.0, True], ['F1', -60.0, 0.5, True],
            ['F3', -160.0, 0.5, False], ['F2', -150.0, 0.05, True], ['F2', +140.0, 0.95, False], ['F6', 120.0, 1.0, True]
        ],
        faciesInTruncRule=['F1', 'F3', 'F7', 'F2', 'F6', 'F5', 'F4', 'F8'],
        gaussFieldsInZone=['GF1', 'GF2', 'GF3', 'GF4', 'GF5', 'GF6'],
        gaussFieldsForBGFacies=['GF1', 'GF2'],
        overlayGroups=overlayGroups,
        faciesProb=[0.15, 0.3, 0.2, 0.1, 0.1, 0.05, 0.05, 0.05],
        faciesReferenceFile=get_facies_reference_file_path(8),
    )


def test_case_9():
    overlayGroups = []

    # Group1
    alphaList = [['GF3', 'F5', 1.0, 0.0]]
    backgroundList = ['F3', 'F2']
    overlayGroup = [alphaList, backgroundList]
    overlayGroups.append(overlayGroup)

    # Group2
    alphaList = [
        ['GF4', 'F4', 0.3, 0.0],
        ['GF5', 'F8', 0.3, 0.0],
        ['GF6', 'F4', 0.4, 0.0]
    ]
    backgroundList = ['F1']
    overlayGroup = [alphaList, backgroundList]
    overlayGroups.append(overlayGroup)

    # Group3
    alphaList = [
        ['GF5', 'F8', 0.7, 1.0],
        ['GF4', 'F4', 0.3, 1.0]
    ]
    backgroundList = ['F7']
    overlayGroup = [alphaList, backgroundList]
    overlayGroups.append(overlayGroup)

    run(
        fTable={1: 'F1', 2: 'F2', 3: 'F3', 4: 'F4', 5: 'F5', 6: 'F6', 7: 'F7', 8: 'F8'},
        faciesInZone=['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8'],
        truncStructure=[
            ['F1', -180.0, 0.5, False], ['F3', -170.0, 0.5, True], ['F7', 10.0, 1.0, True], ['F1', -60.0, 0.5, True],
            ['F3', -160.0, 0.5, True], ['F2', -150.0, 0.05, False], ['F2', +140.0, 0.95, True], ['F6', 120.0, 1.0, True]
        ],
        faciesInTruncRule=['F1', 'F3', 'F7', 'F2', 'F6', 'F5', 'F4', 'F8'],
        gaussFieldsInZone=['GF1', 'GF2', 'GF3', 'GF4', 'GF5', 'GF6'],
        gaussFieldsForBGFacies=['GF1', 'GF2'],
        overlayGroups=overlayGroups,
        faciesProb=[0.0, 0.0, 0.0, 0.01, 0.0, 0.0, 0.0, 0.99],
        faciesReferenceFile=get_facies_reference_file_path(9),
    )


def get_facies_reference_file_path(testCase):
    return f'testData_Angle/test_case_{testCase}.dat'


def run(
        fTable, faciesInTruncRule, faciesInZone, faciesProb,
        faciesReferenceFile, gaussFieldsInZone, gaussFieldsForBGFacies, overlayGroups, truncStructure
):
    truncRule, truncRule2 = initialize_write_read(
        outputModelFileName1=OUTPUT_MODEL_FILE_NAME1,
        outputModelFileName2=OUTPUT_MODEL_FILE_NAME2,
        fTable=fTable, faciesInZone=faciesInZone,
        gaussFieldsInZone=gaussFieldsInZone,
        gaussFieldsForBGFacies=gaussFieldsForBGFacies,
        truncStructure=truncStructure,
        overlayGroups=overlayGroups,
        useConstTruncParam=USE_CONST_TRUNC_PARAM,
        keyResolution=KEYRESOLUTION,
        debug_level=Debug.OFF
    )
    nGaussFields = truncRule.getNGaussFieldsInModel()
    getClassName(truncRule)
    getFaciesInTruncRule(truncRule=truncRule, truncRule2=truncRule2, faciesInTruncRule=faciesInTruncRule)
    facies_prob_numpy = np.asarray(faciesProb)
    truncMapPolygons(
        truncRule=truncRule,
        truncRule2=truncRule2,
        faciesProb=facies_prob_numpy,
        outPolyFile1=OUT_POLY_FILE1,
        outPolyFile2=OUT_POLY_FILE2
    )
    apply_truncations(
        truncRule=truncRule,
        faciesReferenceFile=faciesReferenceFile,
        nGaussFields=nGaussFields,
        gaussFieldFiles=ANGLE_GAUSS_FIELD_FILES,
        faciesOutputFile=FACIES_OUTPUT_FILE
    )

    apply_truncations_vectorized(
        truncRule=truncRule,
        faciesReferenceFile=faciesReferenceFile,
        nGaussFields=nGaussFields,
        gaussFieldFiles=ANGLE_GAUSS_FIELD_FILES,
        faciesOutputFile=FACIES_OUTPUT_FILE_VECTORIZED
    )


if __name__ == '__main__':
    test_Trunc2DAngle()
