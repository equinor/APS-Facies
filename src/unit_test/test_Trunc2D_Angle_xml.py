#!/bin/env python
import filecmp
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element

from src.APSMainFaciesTable import APSMainFaciesTable
from src.Trunc2D_Angle_xml import Trunc2D_Angle
from src.unit_test.constants import (
    FACIES_OUTPUT_FILE, ANGLE_GAUSS_FIELD_FILES, OUTPUT_MODEL_FILE_NAME1,
    OUTPUT_MODEL_FILE_NAME2, OUT_POLY_FILE1, OUT_POLY_FILE2, USE_CONST_TRUNC_PARAM,
)
from src.unit_test.helpers import apply_truncations, getFaciesInTruncRule, truncMapPolygons
from src.utils.constants.simple import Debug
from src.utils.xml import prettify


def interpretXMLModelFileAndWrite(
        modelFileName, outputModelFileName, fTable, faciesInZone, gaussFieldsInZone, debug_level=Debug.OFF
):
    # Read test model file with truncation rule into xml tree
    ET_Tree = ET.parse(modelFileName)
    root = ET_Tree.getroot()
    # Read TruncationRule keyword
    trRule = root.find('TruncationRule')

    # Get name of truncation rule
    truncRuleName = trRule.get('name')
    print('Truncation rule: ' + truncRuleName)

    # Get number of required Gauss fields
    nGaussFields = int(trRule.get('nGFields'))
    # print('Number of gauss fields required for truncation rule: ' + str(nGaussFields))

    mainFaciesTable = APSMainFaciesTable(fTable=fTable)

    # Create truncation rule object from input data, not read from file
    truncRuleOut = Trunc2D_Angle(
        trRule, mainFaciesTable, faciesInZone, gaussFieldsInZone, keyResolution=100,
        debug_level=debug_level, modelFileName=modelFileName
    )
    # Create and write XML tree 
    createXMLTreeAndWriteFile(truncRuleOut, outputModelFileName)

    return truncRuleOut


def createXMLTreeAndWriteFile(truncRuleInput, outputModelFileName):
    # Build an XML tree with top as root
    # from truncation object and write it
    assert truncRuleInput is not None
    top = Element('TEST_TruncationRule')
    truncRuleInput.XMLAddElement(top)
    rootReformatted = prettify(top)
    print('Write file: ' + outputModelFileName)
    with open(outputModelFileName, 'w') as file:
        file.write(rootReformatted)


def createTrunc(
        outputModelFileName, fTable, faciesInZone, gaussFieldsInZone, gaussFieldsForBGFacies,
        truncStructure, overlayGroups, useConstTruncParam, debug_level=Debug.OFF
):
    mainFaciesTable = APSMainFaciesTable(fTable=fTable)

    # Create an object and initialize it
    truncRuleOut = Trunc2D_Angle()
    truncRuleOut.initialize(
        mainFaciesTable, faciesInZone, gaussFieldsInZone, gaussFieldsForBGFacies,
        truncStructure, overlayGroups, useConstTruncParam, debug_level
    )

    # Build an xml tree with the data and write it to file
    createXMLTreeAndWriteFile(truncRuleOut, outputModelFileName)
    return truncRuleOut


def initialize_write_read(
        outputModelFileName1, outputModelFileName2, fTable, faciesInZone, gaussFieldsInZone,
        gaussFieldsForBGFacies, truncStructure, overlayGroups, useConstTruncParam, debug_level=Debug.OFF
):
    file1 = outputModelFileName1
    file2 = outputModelFileName2
    # Create an object for truncation rule and write to file
    # Global variable truncRule
    truncRuleA = createTrunc(
        file1, fTable, faciesInZone, gaussFieldsInZone, gaussFieldsForBGFacies,
        truncStructure, overlayGroups, useConstTruncParam, debug_level
    )
    inputFile = file1

    # Write datastructure:
    #    truncRule.writeContentsInDataStructure()
    # Read the previously written file as and XML file and write it out again to a new file
    # Global variable truncRule2
    truncRuleB = interpretXMLModelFileAndWrite(inputFile, file2, fTable, faciesInZone, gaussFieldsInZone, debug_level)

    # Compare the original xml file created in createTrunc and the xml file written by interpretXMLModelFileAndWrite
    check = filecmp.cmp(file1, file2)
    print('Compare file: ' + file1 + ' and file: ' + file2)
    assert check is True
    if not check:
        raise ValueError('Error: Files are different')
    else:
        print('Files are equal: OK')
    return [truncRuleA, truncRuleB]


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
    fTable = {2: 'F2', 1: 'F1', 3: 'F3'}
    faciesInZone = ['F1', 'F2', 'F3']
    truncStructure = [['F3', -90.0, 1.0], ['F2', +45.0, 1.0], ['F1', +45.0, 1.0]]
    faciesInTruncRule = ['F3', 'F2', 'F1']
    gaussFieldsInZone = ['GF1', 'GF2', 'GF3', 'GF4']
    gaussFieldsForBGFacies = ['GF1', 'GF2']
    overlayGroups = []

    faciesProb = [0.5, 0.3, 0.2]
    faciesReferenceFile = get_facies_reference_file_path(1)
    run(
        fTable, faciesInTruncRule, faciesInZone, faciesProb,
        faciesReferenceFile, gaussFieldsInZone, gaussFieldsForBGFacies, overlayGroups, truncStructure
    )


def test_case_2():
    fTable = {2: 'F2', 1: 'F1', 3: 'F3'}
    faciesInZone = ['F2', 'F3', 'F1']
    truncStructure = [['F1', +135.0, 1.0], ['F2', +45.0, 1.0], ['F3', +45.0, 1.0]]
    faciesInTruncRule = ['F1', 'F2', 'F3']
    gaussFieldsInZone = ['GF1', 'GF2', 'GF3', 'GF4']
    gaussFieldsForBGFacies = ['GF1', 'GF2']
    overlayGroups = []

    faciesProb = [0.01, 0.8, 0.19]
    faciesReferenceFile = get_facies_reference_file_path(2)
    run(
        fTable, faciesInTruncRule, faciesInZone, faciesProb,
        faciesReferenceFile, gaussFieldsInZone, gaussFieldsForBGFacies, overlayGroups, truncStructure
    )


def test_case_3():
    fTable = {1: 'F1', 2: 'F2', 3: 'F3', 4: 'F4', 5: 'F5'}
    faciesInZone = ['F2', 'F3', 'F1', 'F5', 'F4']
    truncStructure = [['F1', +135.0, 1.0], ['F2', +45.0, 1.0], ['F3', +45.0, 1.0]]
    faciesInTruncRule = ['F1', 'F2', 'F3', 'F5', 'F4']
    gaussFieldsInZone = ['GF1', 'GF2', 'GF3', 'GF4', 'GF5', 'GF6']
    gaussFieldsForBGFacies = ['GF1', 'GF2']
    overlayGroups = []

    # Group1
    alphaList11 = [['GF3', 'F5', 1.0, 0.9]]
    backgroundList1 = ['F1']
    overlayGroup1 = [alphaList11, backgroundList1]
    overlayGroups.append(overlayGroup1)
    # Group2
    alphaList12 = [['GF4', 'F4', 1.0, 0.0]]
    backgroundList2 = ['F3']
    overlayGroup2 = [alphaList12, backgroundList2]
    overlayGroups.append(overlayGroup2)

    faciesProb = [0.3, 0.2, 0.3, 0.1, 0.1]
    faciesReferenceFile = get_facies_reference_file_path(3)
    run(
        fTable, faciesInTruncRule, faciesInZone, faciesProb,
        faciesReferenceFile, gaussFieldsInZone, gaussFieldsForBGFacies, overlayGroups, truncStructure
    )


def test_case_3():
    fTable = {1: 'F1', 2: 'F2', 3: 'F3', 4: 'F4', 5: 'F5'}
    faciesInZone = ['F2', 'F3', 'F1', 'F5', 'F4']
    truncStructure = [['F1', +135.0, 1.0], ['F2', +45.0, 1.0], ['F3', +45.0, 1.0]]
    faciesInTruncRule = ['F1', 'F2', 'F3', 'F5', 'F4']
    gaussFieldsInZone = ['GF1', 'GF2', 'GF3', 'GF4', 'GF5', 'GF6']
    gaussFieldsForBGFacies = ['GF1', 'GF2']
    overlayGroups = []
    # Group1
    alphaList1 = [['GF3', 'F5', 1.0, 0.9]]
    backgroundList1 = ['F1']
    overlayGroup1 = [alphaList1, backgroundList1]
    overlayGroups.append(overlayGroup1)
    # Group2
    alphaList2 = [['GF4', 'F4', 1.0, 0.0]]
    backgroundList2 = ['F3']
    overlayGroup2 = [alphaList2, backgroundList2]
    overlayGroups.append(overlayGroup2)
    faciesProb = [0.3, 0.2, 0.3, 0.1, 0.1]
    faciesReferenceFile = get_facies_reference_file_path(3)
    run(
        fTable, faciesInTruncRule, faciesInZone, faciesProb, faciesReferenceFile,
        gaussFieldsInZone, gaussFieldsForBGFacies, overlayGroups, truncStructure
    )


def test_case_4():
    fTable = {1: 'F1', 2: 'F2', 3: 'F3', 4: 'F4', 5: 'F5'}
    faciesInZone = ['F2', 'F3', 'F1', 'F5', 'F4']
    truncStructure = [['F1', -135.0, 1.0], ['F3', +90.0, 1.0], ['F2', +45.0, 1.0]]
    faciesInTruncRule = ['F1', 'F3', 'F2', 'F5', 'F4']
    gaussFieldsInZone = ['GF1', 'GF2', 'GF3', 'GF4', 'GF5', 'GF6']
    gaussFieldsForBGFacies = ['GF1', 'GF2']
    overlayGroups = []

    # Group1
    alphaList11 = [['GF3', 'F5', 1.0, 0.0]]
    backgroundList1 = ['F2', 'F1']
    overlayGroup1 = [alphaList11, backgroundList1]
    overlayGroups.append(overlayGroup1)
    # Group2
    alphaList12 = [['GF4', 'F4', 1.0, 1.0]]
    backgroundList2 = ['F3']
    overlayGroup2 = [alphaList12, backgroundList2]
    overlayGroups.append(overlayGroup2)

    faciesProb = [0.3, 0.2, 0.3, 0.1, 0.1]
    faciesReferenceFile = get_facies_reference_file_path(4)
    run(
        fTable, faciesInTruncRule, faciesInZone, faciesProb,
        faciesReferenceFile, gaussFieldsInZone, gaussFieldsForBGFacies, overlayGroups, truncStructure
    )


def test_case_5():
    fTable = {1: 'F1', 2: 'F2', 3: 'F3', 4: 'F4', 5: 'F5'}
    faciesInZone = ['F2', 'F3', 'F1', 'F5', 'F4']
    truncStructure = [['F1', -180.0, 0.5], ['F3', +180.0, 1.0], ['F1', 0.0, 0.5], ['F2', 35.0, 0.7],
                      ['F2', -35.0, 0.3]]
    faciesInTruncRule = ['F1', 'F3', 'F2', 'F5', 'F4']
    gaussFieldsInZone = ['GF1', 'GF2', 'GF3', 'GF4']
    gaussFieldsForBGFacies = ['GF1', 'GF2']
    overlayGroups = []

    # Group1
    alphaList11 = [['GF3', 'F5', 1.0, 0.0]]
    backgroundList1 = ['F3', 'F2']
    overlayGroup1 = [alphaList11, backgroundList1]
    overlayGroups.append(overlayGroup1)
    # Group2
    alphaList12 = [['GF4', 'F4', 1.0, 0.0]]
    backgroundList2 = ['F1']
    overlayGroup2 = [alphaList12, backgroundList2]
    overlayGroups.append(overlayGroup2)

    faciesProb = [0.2, 0.3, 0.3, 0.1, 0.1]
    faciesReferenceFile = get_facies_reference_file_path(5)
    run(
        fTable, faciesInTruncRule, faciesInZone, faciesProb,
        faciesReferenceFile, gaussFieldsInZone, gaussFieldsForBGFacies, overlayGroups, truncStructure
    )


def test_case_6():
    fTable = {1: 'F1', 2: 'F2', 3: 'F3', 4: 'F4', 5: 'F5'}
    faciesInZone = ['F2', 'F3', 'F1', 'F5', 'F4']
    truncStructure = [
        ['F1', -180.0, 1.0], ['F3', -170.0, 0.5], ['F3', -160.0, 0.5], ['F2', -150.0, 0.7], ['F2', -140.0, 0.3]
    ]
    faciesInTruncRule = ['F1', 'F3', 'F2', 'F5', 'F4']
    gaussFieldsInZone = ['GF1', 'GF2', 'GF3', 'GF4']
    gaussFieldsForBGFacies = ['GF1', 'GF2']
    overlayGroups = []

    # Group1
    alphaList11 = [['GF3', 'F5', 1.0, 0.0]]
    backgroundList1 = ['F3', 'F2']
    overlayGroup1 = [alphaList11, backgroundList1]
    overlayGroups.append(overlayGroup1)
    # Group2
    alphaList12 = [['GF4', 'F4', 1.0, 0.0]]
    backgroundList2 = ['F1']
    overlayGroup2 = [alphaList12, backgroundList2]
    overlayGroups.append(overlayGroup2)

    faciesProb = [0.2, 0.3, 0.3, 0.1, 0.1]
    faciesReferenceFile = get_facies_reference_file_path(6)
    run(
        fTable, faciesInTruncRule, faciesInZone, faciesProb,
        faciesReferenceFile, gaussFieldsInZone, gaussFieldsForBGFacies, overlayGroups, truncStructure
    )


def test_case_7():
    fTable = {1: 'F1', 2: 'F2', 3: 'F3', 4: 'F4', 5: 'F5', 6: 'F6', 7: 'F7', 8: 'F8'}
    faciesInZone = ['F2', 'F3', 'F1', 'F5', 'F4', 'F6', 'F7', 'F8']
    truncStructure = [
        ['F1', -180.0, 0.5], ['F3', -170.0, 0.5], ['F7', 10.0, 1.0], ['F1', -60.0, 0.5],
        ['F3', -160.0, 0.5], ['F2', -150.0, 0.05], ['F2', +140.0, 0.95], ['F6', 120.0, 1.0]
    ]
    faciesInTruncRule = ['F1', 'F3', 'F7', 'F2', 'F6', 'F5', 'F4', 'F8']
    gaussFieldsInZone = ['GF1', 'GF2', 'GF3', 'GF4', 'GF5', 'GF6']
    gaussFieldsForBGFacies = ['GF1', 'GF2']
    overlayGroups = []

    # Group1
    alphaList11 = [['GF3', 'F5', 1.0, 0.0]]
    backgroundList1 = ['F3', 'F2']
    overlayGroup1 = [alphaList11, backgroundList1]
    overlayGroups.append(overlayGroup1)
    # Group2
    alphaList12 = [['GF4', 'F4', 1.0, 0.0]]
    backgroundList2 = ['F1']
    overlayGroup2 = [alphaList12, backgroundList2]
    overlayGroups.append(overlayGroup2)
    # Group3
    alphaList13 = [['GF5', 'F8', 1.0, 1.0]]
    backgroundList3 = ['F7']
    overlayGroup3 = [alphaList13, backgroundList3]
    overlayGroups.append(overlayGroup3)

    faciesProb = [0.15, 0.3, 0.2, 0.1, 0.1, 0.05, 0.05, 0.05]
    faciesReferenceFile = get_facies_reference_file_path(7)
    run(
        fTable, faciesInTruncRule, faciesInZone, faciesProb,
        faciesReferenceFile, gaussFieldsInZone, gaussFieldsForBGFacies, overlayGroups, truncStructure
    )


def test_case_8():
    fTable = {1: 'F1', 2: 'F2', 3: 'F3', 4: 'F4', 5: 'F5', 6: 'F6', 7: 'F7', 8: 'F8'}
    faciesInZone = ['F2', 'F3', 'F1', 'F5', 'F4', 'F6', 'F7', 'F8']
    truncStructure = [
        ['F1', -180.0, 0.5], ['F3', -170.0, 0.5], ['F7', 10.0, 1.0], ['F1', -60.0, 0.5],
        ['F3', -160.0, 0.5], ['F2', -150.0, 0.05], ['F2', +140.0, 0.95], ['F6', 120.0, 1.0]
    ]
    faciesInTruncRule = ['F1', 'F3', 'F7', 'F2', 'F6', 'F5', 'F4', 'F8']
    gaussFieldsInZone = ['GF1', 'GF2', 'GF3', 'GF4', 'GF5', 'GF6']
    gaussFieldsForBGFacies = ['GF1', 'GF2']
    overlayGroups = []

    # Group1
    alphaList1 = [['GF3', 'F5', 1.0, 0.0]]
    backgroundList1 = ['F3', 'F2']
    overlayGroup1 = [alphaList1, backgroundList1]
    overlayGroups.append(overlayGroup1)
    # Group2
    alphaList2 = [
        ['GF4', 'F4', 0.3, 0.0],
        ['GF5', 'F8', 0.3, 0.0],
        ['GF6', 'F4', 0.4, 0.0]
    ]
    backgroundList2 = ['F1']
    overlayGroup2 = [alphaList2, backgroundList2]
    overlayGroups.append(overlayGroup2)
    # Group3
    alphaList3 = [
        ['GF5', 'F8', 0.7, 1.0],
        ['GF4', 'F4', 0.3, 1.0]
    ]
    backgroundList3 = ['F7']
    overlayGroup3 = [alphaList3, backgroundList3]
    overlayGroups.append(overlayGroup3)

    faciesProb = [0.15, 0.3, 0.2, 0.1, 0.1, 0.05, 0.05, 0.05]
    faciesReferenceFile = get_facies_reference_file_path(8)
    run(
        fTable, faciesInTruncRule, faciesInZone, faciesProb,
        faciesReferenceFile, gaussFieldsInZone, gaussFieldsForBGFacies, overlayGroups, truncStructure
    )


def test_case_9():
    fTable = {1: 'F1', 2: 'F2', 3: 'F3', 4: 'F4', 5: 'F5', 6: 'F6', 7: 'F7', 8: 'F8'}
    faciesInZone = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8']
    truncStructure = [
        ['F1', -180.0, 0.5], ['F3', -170.0, 0.5], ['F7', 10.0, 1.0], ['F1', -60.0, 0.5],
        ['F3', -160.0, 0.5], ['F2', -150.0, 0.05], ['F2', +140.0, 0.95], ['F6', 120.0, 1.0]
    ]
    faciesInTruncRule = ['F1', 'F3', 'F7', 'F2', 'F6', 'F5', 'F4', 'F8']
    gaussFieldsInZone = ['GF1', 'GF2', 'GF3', 'GF4', 'GF5', 'GF6']
    gaussFieldsForBGFacies = ['GF1', 'GF2']
    overlayGroups = []

    # Group1
    alphaList1 = [['GF3', 'F5', 1.0, 0.0]]
    backgroundList1 = ['F3', 'F2']
    overlayGroup1 = [alphaList1, backgroundList1]
    overlayGroups.append(overlayGroup1)
    # Group2
    alphaList2 = [
        ['GF4', 'F4', 0.3, 0.0],
        ['GF5', 'F8', 0.3, 0.0],
        ['GF6', 'F4', 0.4, 0.0]
    ]
    backgroundList2 = ['F1']
    overlayGroup2 = [alphaList2, backgroundList2]
    overlayGroups.append(overlayGroup2)
    # Group3
    alphaList3 = [
        ['GF5', 'F8', 0.7, 1.0],
        ['GF4', 'F4', 0.3, 1.0]
    ]
    backgroundList3 = ['F7']
    overlayGroup3 = [alphaList3, backgroundList3]
    overlayGroups.append(overlayGroup3)

    faciesProb = [0.0, 0.0, 0.0, 0.01, 0.0, 0.0, 0.0, 0.99]
    faciesReferenceFile = get_facies_reference_file_path(9)
    run(
        fTable, faciesInTruncRule, faciesInZone, faciesProb,
        faciesReferenceFile, gaussFieldsInZone, gaussFieldsForBGFacies, overlayGroups, truncStructure
    )


def get_facies_reference_file_path(testCase):
    faciesReferenceFile = 'testData_Angle/test_case_' + str(testCase) + '.dat'
    return faciesReferenceFile


def run(
        fTable, faciesInTruncRule, faciesInZone, faciesProb,
        faciesReferenceFile, gaussFieldsInZone, gaussFieldsForBGFacies, overlayGroups, truncStructure
):
    [truncRule, truncRule2] = initialize_write_read(
        OUTPUT_MODEL_FILE_NAME1, OUTPUT_MODEL_FILE_NAME2, fTable, faciesInZone, gaussFieldsInZone,
        gaussFieldsForBGFacies, truncStructure, overlayGroups, USE_CONST_TRUNC_PARAM, Debug.OFF
    )
    nGaussFields = truncRule.getNGaussFieldsInModel()
    getClassName(truncRule)
    getFaciesInTruncRule(truncRule, truncRule2, faciesInTruncRule)
    truncMapPolygons(truncRule, truncRule2, faciesProb, OUT_POLY_FILE1, OUT_POLY_FILE2)
    apply_truncations(truncRule, faciesReferenceFile, nGaussFields, ANGLE_GAUSS_FIELD_FILES, FACIES_OUTPUT_FILE)


if __name__ == '__main__':
    test_Trunc2DAngle()
