#!/bin/env python
import filecmp
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element

from src.APSMainFaciesTable import APSMainFaciesTable
from src.Trunc2D_Cubic_xml import Trunc2D_Cubic
from src.unit_test.helpers import apply_truncations, getFaciesInTruncRule, truncMapPolygons
from src.utils.constants import Debug
from src.utils.methods import prettify
from src.unit_test.helpers import get_cubic_facies_reference_file_path
from src.unit_test.constants import (
    CUBIC_GAUSS_FIELD_FILES, NO_VERBOSE_DEBUG, OUTPUT_MODEL_FILE_NAME1,
    OUTPUT_MODEL_FILE_NAME2, OUT_POLY_FILE1, OUT_POLY_FILE2,
    FACIES_OUTPUT_FILE,
)


def interpretXMLModelFileAndWrite(modelFileName, outputModelFileName, fTable, faciesInZone, gaussFieldsInZone, debug_level):
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
    #    print('Number of gauss fields required for truncation rule: ' + str(nGaussFields))

    mainFaciesTable = APSMainFaciesTable(fTable=fTable)

    # Create truncation rule object from input data, not read from file
    truncRuleOut = Trunc2D_Cubic(
        trRule, mainFaciesTable, faciesInZone, gaussFieldsInZone, keyResolution=100, debug_level=debug_level,
        modelFileName=modelFileName
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
        truncStructure, overlayGroups, debug_level
):
    mainFaciesTable = APSMainFaciesTable(fTable=fTable)

    # Create an object and initialize it
    truncRuleOut = Trunc2D_Cubic()
    truncRuleOut.initialize(
        mainFaciesTable, faciesInZone, gaussFieldsInZone, gaussFieldsForBGFacies,
        truncStructure,  overlayGroups, debug_level
    )

    # Build an xml tree with the data and write it to file
    createXMLTreeAndWriteFile(truncRuleOut, outputModelFileName)
    return truncRuleOut


def initialize_write_read(
        outputModelFileName1, outputModelFileName2, fTable, faciesInZone,
        gaussFieldsInZone, gaussFieldsForBGFacies,
        truncStructure, overlayGroups, debug_level
):
    file1 = outputModelFileName1
    file2 = outputModelFileName2
    # Create an object for truncation rule and write to file
    # Global variable truncRule
    truncRuleA = createTrunc(
        file1, fTable, faciesInZone, gaussFieldsInZone, gaussFieldsForBGFacies,
        truncStructure, overlayGroups, debug_level
    )
    inputFile = file1

    # Write data structure:
    #    truncRule.writeContentsInDataStructure()
    # Read the previously written file as and XML file and write it out again to a new file
    # Global variable truncRule2
    truncRuleB = interpretXMLModelFileAndWrite(inputFile, file2, fTable, faciesInZone, gaussFieldsInZone, debug_level)

    # Compare the original xml file created in createTrunc and the xml file written by interpretXMLModelFileAndWrite
    check = filecmp.cmp(file1, file2)
    print('Compare file: ' + file1 + ' and file: ' + file2)
    assert check is True
    if check is False:
        raise ValueError('Error: Files are different')
    else:
        print('Files are equal: OK')
    return [truncRuleA, truncRuleB]


def getClassName(truncRule):
    assert truncRule is not None
    name = truncRule.getClassName()
    assert name == 'Trunc2D_Cubic'


def test_Trunc2DCubic():
    nCase = 24
    start = 1
    end =24
    for testCase in range(start, end + 1):
        print(' ')
        print('******** Case number: ' + str(testCase) + ' *********')
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

        elif testCase == 10:
            test_case_10()

        elif testCase == 11:
            test_case_11()

        elif testCase == 12:
            test_case_12()

        elif testCase == 13:
            test_case_13()

        elif testCase == 14:
            test_case_14()

        elif testCase == 15:
            test_case_15()

        elif testCase == 16:
            test_case_16()

        elif testCase == 17:
            test_case_17()

        elif testCase == 18:
            test_case_18()

        elif testCase == 19:
            test_case_19()

        elif testCase == 20:
            test_case_20()

        elif testCase == 21:
            test_case_21()

        elif testCase == 22:
            test_case_22()

        elif testCase == 23:
            test_case_23()

        elif testCase == 24:
            test_case_24()


def test_case_1():
    fTable = {2: 'F2', 1: 'F1'}
    faciesInZone = ['F1', 'F2']
    truncStructure = ['H', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0]]
    faciesInTruncRule = ['F1', 'F2']
    gaussFieldsInZone = ['GF1', 'GF2', 'GF3', 'GF4']
    gaussFieldsForBGFacies = ['GF1', 'GF2']
    overlayGroups = []

    faciesProb = [0.5, 0.5]
    faciesReferenceFile = get_cubic_facies_reference_file_path(1)
    run(
        fTable, faciesInTruncRule, faciesInZone, faciesProb,
        faciesReferenceFile, gaussFieldsInZone,  gaussFieldsForBGFacies, overlayGroups, truncStructure
    )


def test_case_2():
    fTable = {2: 'F2', 1: 'F1'}
    faciesInZone = ['F1', 'F2']
    truncStructure = ['V', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0]]
    faciesInTruncRule = ['F1', 'F2']
    gaussFieldsInZone = ['GF1', 'GF2', 'GF3', 'GF4']
    gaussFieldsForBGFacies = ['GF1', 'GF2']
    overlayGroups = []

    faciesProb = [0.5, 0.5]
    faciesReferenceFile = get_cubic_facies_reference_file_path(2)
    run(
        fTable, faciesInTruncRule, faciesInZone, faciesProb,
        faciesReferenceFile, gaussFieldsInZone,  gaussFieldsForBGFacies, overlayGroups, truncStructure
    )


def test_case_3():
    fTable = {3: 'F3', 2: 'F2', 1: 'F1'}
    faciesInZone = ['F1', 'F2', 'F3']
    truncStructure = ['H', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0], ['F3', 1.0, 3, 0, 0]]
    faciesInTruncRule = ['F1', 'F2', 'F3']
    gaussFieldsInZone = ['GF1', 'GF2', 'GF3', 'GF4']
    gaussFieldsForBGFacies = ['GF1', 'GF2']
    overlayGroups = []

    faciesProb = [0.5, 0.2, 0.3]
    faciesReferenceFile = get_cubic_facies_reference_file_path(3)
    run(
        fTable, faciesInTruncRule, faciesInZone, faciesProb,
        faciesReferenceFile, gaussFieldsInZone,  gaussFieldsForBGFacies, overlayGroups, truncStructure
    )


def test_case_4():
    fTable = {3: 'F3', 2: 'F2', 1: 'F1'}
    faciesInZone = ['F1', 'F2', 'F3']
    truncStructure = ['V', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0], ['F3', 1.0, 3, 0, 0]]
    faciesInTruncRule = ['F1', 'F2', 'F3']
    gaussFieldsInZone = ['GF1', 'GF2', 'GF3', 'GF4']
    gaussFieldsForBGFacies = ['GF1', 'GF2']
    overlayGroups = []

    faciesProb = [0.5, 0.2, 0.3]
    faciesReferenceFile = get_cubic_facies_reference_file_path(4)
    run(
        fTable, faciesInTruncRule, faciesInZone, faciesProb,
        faciesReferenceFile, gaussFieldsInZone,  gaussFieldsForBGFacies, overlayGroups, truncStructure
    )


def test_case_5():
    fTable = {3: 'F3', 2: 'F2', 1: 'F1', 4: 'F4'}
    faciesInZone = ['F1', 'F2', 'F3', 'F4']
    truncStructure = ['V', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0], ['F3', 1.0, 3, 0, 0]]
    faciesInTruncRule = ['F1', 'F2', 'F3', 'F4']
    gaussFieldsInZone = ['GF1', 'GF2', 'GF3', 'GF4']
    gaussFieldsForBGFacies = ['GF1', 'GF2']
    overlayGroups = []
    # Group1
    alphaList1 = [['GF3', 'F4', 1.0, 0.5]]
    backgroundList1 =  ['F2', 'F3']
    overlayGroup1 = [alphaList1, backgroundList1]
    overlayGroups.append(overlayGroup1)
    
#    overlayFacies = ['F4']
#    backGroundFacies = [['F2', 'F3']]
#    overlayTruncCenter = [0.5]
    faciesProb = [0.3, 0.2, 0.3, 0.2]
#    nGaussFields = 3
    faciesReferenceFile = get_cubic_facies_reference_file_path(5)
    run(
        fTable, faciesInTruncRule, faciesInZone, faciesProb,
        faciesReferenceFile, gaussFieldsInZone,  gaussFieldsForBGFacies, overlayGroups, truncStructure
    )


def test_case_6():
    fTable = {3: 'F3', 2: 'F2', 1: 'F1', 4: 'F4'}
    faciesInZone = ['F1', 'F2', 'F3', 'F4']
    truncStructure = ['H', ['F1', 1.0, 1, 0, 0], ['F4', 1.0, 2, 1, 0], ['F3', 1.0, 2, 2, 0]]
    faciesInTruncRule = ['F1', 'F4', 'F3', 'F2']
    gaussFieldsInZone = ['GF1', 'GF2', 'GF3', 'GF4']
    gaussFieldsForBGFacies = ['GF1', 'GF2']
    overlayGroups = []
    #Group1
    alphaList1 = [['GF3', 'F2', 1.0, 1.0]]
    backgroundList1 =  ['F4', 'F1']
    overlayGroup1 = [alphaList1, backgroundList1]
    overlayGroups.append(overlayGroup1)

#    overlayFacies = ['F2']
#    backGroundFacies = [['F4', 'F1']]
#    overlayTruncCenter = [1.0]
    faciesProb = [0.4, 0.1, 0.3, 0.2]
#    nGaussFields = 3
    faciesReferenceFile = get_cubic_facies_reference_file_path(6)
    run(
        fTable, faciesInTruncRule, faciesInZone, faciesProb,
        faciesReferenceFile, gaussFieldsInZone,  gaussFieldsForBGFacies, overlayGroups, truncStructure
    )


def test_case_7():
    fTable = {3: 'F3', 2: 'F2', 1: 'F1', 4: 'F4'}
    faciesInZone = ['F1', 'F2', 'F3', 'F4']
    truncStructure = ['H', ['F1', 1.0, 1, 1, 0], ['F2', 1.0, 1, 2, 0], ['F4', 1.0, 2, 0, 0]]
    faciesInTruncRule = ['F1', 'F2', 'F4', 'F3']
    gaussFieldsInZone = ['GF1', 'GF2', 'GF3', 'GF4']
    gaussFieldsForBGFacies = ['GF1', 'GF2']
    overlayGroups = []
    #Group1
    alphaList1 = [['GF3', 'F3', 1.0, 0.5]]
    backgroundList1 =  ['F2', 'F1']
    overlayGroup1 = [alphaList1, backgroundList1]
    overlayGroups.append(overlayGroup1)

#    overlayFacies = ['F3']
#    backGroundFacies = [['F2', 'F1']]
#    overlayTruncCenter = [0.5]
    faciesProb = [0.4, 0.1, 0.3, 0.2]
#    nGaussFields = 3
    faciesReferenceFile = get_cubic_facies_reference_file_path(7)
    run(
        fTable, faciesInTruncRule, faciesInZone, faciesProb,
        faciesReferenceFile, gaussFieldsInZone,  gaussFieldsForBGFacies, overlayGroups, truncStructure
    )


def test_case_8():
    fTable = {6: 'F6', 4: 'F4', 3: 'F3', 2: 'F2', 5: 'F5', 1: 'F1'}
    faciesInZone = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6']
    truncStructure = ['H', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0], ['F3', 1.0, 3, 0, 0]]
    faciesInTruncRule = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6']
    gaussFieldsInZone = ['GF1', 'GF2', 'GF3', 'GF4', 'GF5']
    gaussFieldsForBGFacies = ['GF1', 'GF2']
    overlayGroups = []
    # Group1
    alphaList11 = [['GF3', 'F4', 1.0, 0.0]]
    backgroundList1 =  ['F1']
    overlayGroup1 = [alphaList11, backgroundList1]
    overlayGroups.append(overlayGroup1)
    # Group2
    alphaList12 = [['GF4', 'F5', 1.0, 0.5]]
    backgroundList2 =  ['F2']
    overlayGroup2 = [alphaList12, backgroundList2]
    overlayGroups.append(overlayGroup2)
    # Group3
    alphaList13 = [['GF5', 'F6', 1.0, 1.0]]
    backgroundList3 =  ['F3']
    overlayGroup3 = [alphaList13, backgroundList3]
    overlayGroups.append(overlayGroup3)
    
#    overlayFacies = ['F4', 'F5', 'F6']
#    backGroundFacies = [['F1'], ['F2'], ['F3']]
#    overlayTruncCenter = [0.0, 0.5, 1.0]
    faciesProb = [0.2, 0.3, 0.1, 0.1, 0.1, 0.2]
#    nGaussFields = 5
    faciesReferenceFile = get_cubic_facies_reference_file_path(8)
    run(
        fTable, faciesInTruncRule, faciesInZone, faciesProb,
        faciesReferenceFile, gaussFieldsInZone,  gaussFieldsForBGFacies, overlayGroups, truncStructure
    )


def test_case_9():
    fTable = {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2'}
    faciesInZone = ['F2', 'F1', 'F4', 'F3']
    truncStructure = ['V', ['F1', 0.6, 1, 0, 0], ['F2', 1.0, 2, 1, 0], ['F1', 0.4, 2, 2, 0]]
    faciesInTruncRule = ['F1', 'F2', 'F4', 'F3']
    gaussFieldsInZone = ['GF1', 'GF2', 'GF3', 'GF4']
    gaussFieldsForBGFacies = ['GF1', 'GF2']
    overlayGroups = []
    # Group1
    alphaList11 = [['GF3', 'F4', 1.0, 0.5]]
    backgroundList1 =  ['F1']
    overlayGroup1 = [alphaList11, backgroundList1]
    overlayGroups.append(overlayGroup1)
    # Group2
    alphaList12 = [['GF4', 'F3', 1.0, 0.8]]
    backgroundList2 =  ['F2']
    overlayGroup2 = [alphaList12, backgroundList2]
    overlayGroups.append(overlayGroup2)

#    overlayFacies = ['F4', 'F3']
#    backGroundFacies = [['F1'], ['F2']]
#    overlayTruncCenter = [0.5, 0.8]
    faciesProb = [0.4, 0.1, 0.3, 0.2]
#    nGaussFields = 4
    faciesReferenceFile = get_cubic_facies_reference_file_path(9)
    run(
        fTable, faciesInTruncRule, faciesInZone, faciesProb,
        faciesReferenceFile, gaussFieldsInZone,  gaussFieldsForBGFacies, overlayGroups, truncStructure
    )


def test_case_10():
    fTable = {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2'}
    faciesInZone = ['F2', 'F1', 'F4', 'F3']
    truncStructure = ['V', ['F1', 1.0, 1, 1, 0], ['F3', 0.3, 1, 2, 0], ['F3', 0.7, 2, 0, 0]]
    faciesInTruncRule = ['F1', 'F3', 'F4', 'F2']
    gaussFieldsInZone = ['GF1', 'GF2', 'GF3', 'GF4']
    gaussFieldsForBGFacies = ['GF1', 'GF2']
    overlayGroups = []
    # Group1
    alphaList11 = [['GF3', 'F4', 1.0, 0.5]]
    backgroundList1 =  ['F1']
    overlayGroup1 = [alphaList11, backgroundList1]
    overlayGroups.append(overlayGroup1)
    # Group2
    alphaList12 = [['GF4', 'F2', 1.0, 0.8]]
    backgroundList2 =  ['F3']
    overlayGroup2 = [alphaList12, backgroundList2]
    overlayGroups.append(overlayGroup2)

#    overlayFacies = ['F4', 'F2']
#    backGroundFacies = [['F1'], ['F3']]
#    overlayTruncCenter = [0.5, 0.8]
    faciesProb = [0.4, 0.1, 0.3, 0.2]
#    nGaussFields = 4
    faciesReferenceFile = get_cubic_facies_reference_file_path(10)
    run(
        fTable, faciesInTruncRule, faciesInZone, faciesProb,
        faciesReferenceFile, gaussFieldsInZone,  gaussFieldsForBGFacies, overlayGroups, truncStructure
    )


def test_case_11():
    fTable = {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5', 6: 'F6'}
    faciesInZone = ['F2', 'F1', 'F4', 'F3', 'F6', 'F5']
    truncStructure = ['H', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0], ['F3', 1.0, 3, 0, 0],
                      ['F4', 1.0, 4, 0, 0]]
    faciesInTruncRule = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6']
    gaussFieldsInZone = ['GF1', 'GF2', 'GF3', 'GF4']
    gaussFieldsForBGFacies = ['GF1', 'GF2']
    overlayGroups = []
    # Group1
    alphaList11 = [['GF3', 'F5', 1.0, 0.5]]
    backgroundList1 =  ['F1', 'F2', 'F3']
    overlayGroup1 = [alphaList11, backgroundList1]
    overlayGroups.append(overlayGroup1)
    # Group2
    alphaList12 = [['GF4', 'F6', 1.0, 0.8]]
    backgroundList2 =  ['F4']
    overlayGroup2 = [alphaList12, backgroundList2]
    overlayGroups.append(overlayGroup2)

#    overlayFacies = ['F5', 'F6']
#    backGroundFacies = [['F1', 'F2', 'F3'], ['F4']]
#    overlayTruncCenter = [0.5, 0.8]
    faciesProb = [0.3, 0.1, 0.2, 0.2, 0.1, 0.1]
#    nGaussFields = 4
    faciesReferenceFile = get_cubic_facies_reference_file_path(11)
    run(
        fTable, faciesInTruncRule, faciesInZone, faciesProb,
        faciesReferenceFile, gaussFieldsInZone,  gaussFieldsForBGFacies, overlayGroups, truncStructure
    )


def test_case_12():
    fTable = {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2'}
    faciesInZone = ['F2', 'F1', 'F4', 'F3']
    truncStructure = ['H', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0], ['F3', 1.0, 3, 0, 0],
                      ['F4', 1.0, 4, 0, 0]]
    faciesInTruncRule = ['F1', 'F2', 'F3', 'F4']
    gaussFieldsInZone = ['GF1', 'GF2', 'GF3', 'GF4']
    gaussFieldsForBGFacies = ['GF1', 'GF2']
    overlayGroups = []

#    overlayFacies = []
#    backGroundFacies = []
#    overlayTruncCenter = []
    faciesProb = [0.3, 0.1, 0.3, 0.3]
#    nGaussFields = 2
    faciesReferenceFile = get_cubic_facies_reference_file_path(12)
    run(
        fTable, faciesInTruncRule, faciesInZone, faciesProb,
        faciesReferenceFile, gaussFieldsInZone,  gaussFieldsForBGFacies, overlayGroups, truncStructure
    )


def test_case_13():
    fTable = {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5', 6: 'F6'}
    faciesInZone = ['F2', 'F1', 'F4', 'F3', 'F6', 'F5']
    truncStructure = ['V', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0], ['F3', 1.0, 3, 0, 0],
                      ['F4', 1.0, 4, 0, 0]]
    faciesInTruncRule = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6']
    gaussFieldsInZone = ['GF1', 'GF2', 'GF3', 'GF4']
    gaussFieldsForBGFacies = ['GF1', 'GF2']
    overlayGroups = []
    # Group1
    alphaList11 = [['GF3', 'F5', 1.0, 0.3]]
    backgroundList1 =  ['F1', 'F3']
    overlayGroup1 = [alphaList11, backgroundList1]
    overlayGroups.append(overlayGroup1)
    # Group2
    alphaList12 = [['GF4', 'F6', 1.0, 0.7]]
    backgroundList2 =  ['F4', 'F2']
    overlayGroup2 = [alphaList12, backgroundList2]
    overlayGroups.append(overlayGroup2)

#    overlayFacies = ['F5', 'F6']
#    backGroundFacies = [['F1', 'F3'], ['F4', 'F2']]
#    overlayTruncCenter = [0.3, 0.7]
    faciesProb = [0.3, 0.1, 0.2, 0.2, 0.1, 0.1]
#    nGaussFields = 4
    faciesReferenceFile = get_cubic_facies_reference_file_path(13)
    run(
        fTable, faciesInTruncRule, faciesInZone, faciesProb,
        faciesReferenceFile, gaussFieldsInZone,  gaussFieldsForBGFacies, overlayGroups, truncStructure
    )


def test_case_14():
    fTable = {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5', 6: 'F6'}
    faciesInZone = ['F2', 'F1', 'F4', 'F3', 'F6', 'F5']
    truncStructure = ['H', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0], ['F3', 1.0, 3, 1, 0],
                      ['F4', 1.0, 3, 2, 0]]
    faciesInTruncRule = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6']
    gaussFieldsInZone = ['GF1', 'GF2', 'GF3', 'GF4']
    gaussFieldsForBGFacies = ['GF1', 'GF2']
    overlayGroups = []
    # Group1
    alphaList11 = [['GF3', 'F5', 1.0, 0.3]]
    backgroundList1 =  ['F1', 'F3']
    overlayGroup1 = [alphaList11, backgroundList1]
    overlayGroups.append(overlayGroup1)
    # Group2
    alphaList12 = [['GF4', 'F6', 1.0, 0.7]]
    backgroundList2 =  ['F4', 'F2']
    overlayGroup2 = [alphaList12, backgroundList2]
    overlayGroups.append(overlayGroup2)

#    overlayFacies = ['F5', 'F6']
#    backGroundFacies = [['F1', 'F3'], ['F4', 'F2']]
#    overlayTruncCenter = [0.3, 0.7]
    faciesProb = [0.3, 0.1, 0.2, 0.2, 0.1, 0.1]
#    nGaussFields = 4
    faciesReferenceFile = get_cubic_facies_reference_file_path(14)
    run(
        fTable, faciesInTruncRule, faciesInZone, faciesProb,
        faciesReferenceFile, gaussFieldsInZone,  gaussFieldsForBGFacies, overlayGroups, truncStructure
    )


def test_case_15():
    fTable = {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5', 6: 'F6'}
    faciesInZone = ['F2', 'F1', 'F4', 'F3', 'F6', 'F5']
    truncStructure = ['V', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0], ['F3', 1.0, 3, 1, 0],
                      ['F4', 1.0, 3, 2, 0]]
    faciesInTruncRule = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6']
    gaussFieldsInZone = ['GF1', 'GF2', 'GF3', 'GF4']
    gaussFieldsForBGFacies = ['GF1', 'GF2']
    overlayGroups = []
    # Group1
    alphaList11 = [['GF3', 'F5', 1.0, 0.3]]
    backgroundList1 =  ['F1', 'F3']
    overlayGroup1 = [alphaList11, backgroundList1]
    overlayGroups.append(overlayGroup1)
    # Group2
    alphaList12 = [['GF4', 'F6', 1.0, 0.7]]
    backgroundList2 =  ['F4', 'F2']
    overlayGroup2 = [alphaList12, backgroundList2]
    overlayGroups.append(overlayGroup2)

#    overlayFacies = ['F5', 'F6']
#    backGroundFacies = [['F1', 'F3'], ['F4', 'F2']]
#    overlayTruncCenter = [0.3, 0.7]
    faciesProb = [0.3, 0.1, 0.2, 0.2, 0.1, 0.1]
#    nGaussFields = 4
    faciesReferenceFile = get_cubic_facies_reference_file_path(15)
    run(
        fTable, faciesInTruncRule, faciesInZone, faciesProb,
        faciesReferenceFile, gaussFieldsInZone,  gaussFieldsForBGFacies, overlayGroups, truncStructure
    )


def test_case_16():
    fTable = {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2'}
    faciesInZone = ['F2', 'F1', 'F4', 'F3']
    truncStructure = ['V', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0], ['F3', 1.0, 3, 1, 0],
                      ['F4', 1.0, 3, 2, 0]]
    faciesInTruncRule = ['F1', 'F2', 'F3', 'F4']
    gaussFieldsInZone = ['GF1', 'GF2', 'GF3', 'GF4']
    gaussFieldsForBGFacies = ['GF1', 'GF2']
    overlayGroups = []

#    overlayFacies = []
#    backGroundFacies = []
#    overlayTruncCenter = []
    faciesProb = [0.3, 0.2, 0.2, 0.3]
#    nGaussFields = 2
    faciesReferenceFile = get_cubic_facies_reference_file_path(16)
    run(
        fTable, faciesInTruncRule, faciesInZone, faciesProb,
        faciesReferenceFile, gaussFieldsInZone,  gaussFieldsForBGFacies, overlayGroups, truncStructure
    )


def test_case_17():
    fTable = {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5', 6: 'F6'}
    faciesInZone = ['F2', 'F1', 'F4', 'F3', 'F6', 'F5']
    truncStructure = ['H', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0], ['F3', 1.0, 3, 0, 0],
                      ['F4', 1.0, 4, 0, 0],
                      ['F5', 1.0, 5, 0, 0]]
    faciesInTruncRule = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6']
    gaussFieldsInZone = ['GF1', 'GF2', 'GF3', 'GF4']
    gaussFieldsForBGFacies = ['GF1', 'GF2']
    overlayGroups = []
    # Group1
    alphaList11 = [['GF3', 'F6', 1.0, 0.3]]
    backgroundList1 =  ['F1', 'F3', 'F4', 'F2']
    overlayGroup1 = [alphaList11, backgroundList1]
    overlayGroups.append(overlayGroup1)

#    overlayFacies = ['F6']
#    backGroundFacies = [['F1', 'F3', 'F4', 'F2']]
#    overlayTruncCenter = [0.3]
    faciesProb = [0.3, 0.1, 0.2, 0.2, 0.1, 0.1]
#    nGaussFields = 3
    faciesReferenceFile = get_cubic_facies_reference_file_path(17)
    run(
        fTable, faciesInTruncRule, faciesInZone, faciesProb,
        faciesReferenceFile, gaussFieldsInZone,  gaussFieldsForBGFacies, overlayGroups, truncStructure
    )


def test_case_18():
    fTable = {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5', 6: 'F6', 7: 'F7'}
    faciesInZone = ['F2', 'F1', 'F4', 'F3', 'F6', 'F5', 'F7']
    truncStructure = ['H', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0], ['F3', 1.0, 3, 0, 0],
                      ['F4', 1.0, 4, 0, 0],
                      ['F5', 1.0, 5, 0, 0]]
    faciesInTruncRule = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7']
    gaussFieldsInZone = ['GF1', 'GF2', 'GF3', 'GF4']
    gaussFieldsForBGFacies = ['GF1', 'GF2']
    overlayGroups = []
    # Group1
    alphaList11 = [['GF3', 'F6', 1.0, 0.3]]
    backgroundList1 =  ['F1', 'F3', 'F4', 'F2']
    overlayGroup1 = [alphaList11, backgroundList1]
    overlayGroups.append(overlayGroup1)
    # Group2
    alphaList12 = [['GF4', 'F7', 1.0, 0.9]]
    backgroundList2 =  ['F5']
    overlayGroup2 = [alphaList12, backgroundList2]
    overlayGroups.append(overlayGroup2)

#    overlayFacies = ['F6', 'F7']
#    backGroundFacies = [['F1', 'F3', 'F4', 'F2'], ['F5']]
#    overlayTruncCenter = [0.3, 0.9]
    faciesProb = [0.2, 0.1, 0.2, 0.2, 0.1, 0.1, 0.1]
#    nGaussFields = 4
    faciesReferenceFile = get_cubic_facies_reference_file_path(18)
    run(
        fTable, faciesInTruncRule, faciesInZone, faciesProb,
        faciesReferenceFile, gaussFieldsInZone,  gaussFieldsForBGFacies, overlayGroups, truncStructure
    )


def test_case_19():
    fTable = {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5', 6: 'F6', 7: 'F7'}
    faciesInZone = ['F2', 'F1', 'F4', 'F3', 'F6', 'F5', 'F7']
    truncStructure = ['H', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 1, 1], ['F3', 1.0, 2, 1, 2],
                      ['F4', 1.0, 2, 2, 1],
                      ['F5', 1.0, 2, 2, 2]]
    faciesInTruncRule = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7']
    gaussFieldsInZone = ['GF1', 'GF2', 'GF3', 'GF4']
    gaussFieldsForBGFacies = ['GF1', 'GF2']
    overlayGroups = []
    # Group1
    alphaList11 = [['GF3', 'F6', 1.0, 0.3]]
    backgroundList1 =  ['F1', 'F3', 'F4', 'F2']
    overlayGroup1 = [alphaList11, backgroundList1]
    overlayGroups.append(overlayGroup1)
    # Group2
    alphaList12 = [['GF4', 'F7', 1.0, 0.9]]
    backgroundList2 =  ['F5']
    overlayGroup2 = [alphaList12, backgroundList2]
    overlayGroups.append(overlayGroup2)
    
#    overlayFacies = ['F6', 'F7']
#    backGroundFacies = [['F1', 'F3', 'F4', 'F2'], ['F5']]
#    overlayTruncCenter = [0.3, 0.9]
    faciesProb = [0.2, 0.1, 0.2, 0.2, 0.1, 0.1, 0.1]
#    nGaussFields = 4
    faciesReferenceFile = get_cubic_facies_reference_file_path(19)
    run(
        fTable, faciesInTruncRule, faciesInZone, faciesProb,
        faciesReferenceFile, gaussFieldsInZone,  gaussFieldsForBGFacies, overlayGroups, truncStructure
    )


def test_case_20():
    fTable = {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5', 6: 'F6'}
    faciesInZone = ['F2', 'F1', 'F4', 'F3', 'F6', 'F5']
    truncStructure = ['V', ['F4', 0.4, 1, 0, 0], ['F2', 1.0, 2, 1, 0], ['F3', 1.0, 2, 2, 1],
                      ['F4', 0.3, 2, 2, 2],
                      ['F4', 0.3, 2, 3, 0]]
    faciesInTruncRule = ['F4', 'F2', 'F3', 'F1', 'F5', 'F6']
    gaussFieldsInZone = ['GF1', 'GF2', 'GF3', 'GF4', 'GF5']
    gaussFieldsForBGFacies = ['GF1', 'GF2']
    overlayGroups = []
    # Group1
    alphaList11 = [['GF3', 'F1', 1.0, 0.3]]
    backgroundList1 =  ['F2']
    overlayGroup1 = [alphaList11, backgroundList1]
    overlayGroups.append(overlayGroup1)
    # Group2
    alphaList12 = [['GF4', 'F5', 1.0, 0.9]]
    backgroundList2 =  ['F3']
    overlayGroup2 = [alphaList12, backgroundList2]
    overlayGroups.append(overlayGroup2)
    # Group3
    alphaList13 = [['GF5', 'F6', 1.0, 0.0]]
    backgroundList3 =  ['F4']
    overlayGroup3 = [alphaList13, backgroundList3]
    overlayGroups.append(overlayGroup3)

#    overlayFacies = ['F1', 'F5', 'F6']
#    backGroundFacies = [['F2'], ['F3'], ['F4']]
#    overlayTruncCenter = [0.3, 0.9, 0.0]
    faciesProb = [0.3, 0.1, 0.2, 0.2, 0.1, 0.1]
#    nGaussFields = 5
    faciesReferenceFile = get_cubic_facies_reference_file_path(20)
    run(
        fTable, faciesInTruncRule, faciesInZone, faciesProb,
        faciesReferenceFile, gaussFieldsInZone,  gaussFieldsForBGFacies, overlayGroups, truncStructure
    )


def test_case_21():
    fTable = {3: 'F1', 2: 'F3', 1: 'F4'}
    faciesInZone = ['F1', 'F4', 'F3']
    truncStructure = ['V', ['F4', 0.2, 1, 0, 0], ['F4', 0.2, 2, 1, 0], ['F3', 1.0, 2, 2, 1],
                      ['F4', 0.3, 2, 2, 2],
                      ['F4', 0.3, 2, 3, 0]]
    faciesInTruncRule = ['F4', 'F3', 'F1']
    gaussFieldsInZone = ['GF1', 'GF2', 'GF3', 'GF4']
    gaussFieldsForBGFacies = ['GF1', 'GF2']
    overlayGroups = []
    # Group1
    alphaList11 = [['GF3', 'F1', 1.0, 0.3]]
    backgroundList1 =  ['F4']
    overlayGroup1 = [alphaList11, backgroundList1]
    overlayGroups.append(overlayGroup1)

#    overlayFacies = ['F1']
#    backGroundFacies = [['F4']]
#    overlayTruncCenter = [0.3]
    faciesProb = [0.3, 0.3, 0.4]
#    nGaussFields = 3
    faciesReferenceFile = get_cubic_facies_reference_file_path(21)
    run(
        fTable, faciesInTruncRule, faciesInZone, faciesProb,
        faciesReferenceFile, gaussFieldsInZone,  gaussFieldsForBGFacies, overlayGroups, truncStructure
    )


def test_case_22():
    fTable = {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5'}
    faciesInZone = ['F1', 'F4', 'F3', 'F5', 'F2']
    truncStructure = ['H', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 1, 0], ['F3', 0.5, 2, 2, 1],
                      ['F4', 1.0, 2, 2, 2],
                      ['F3', 0.5, 2, 3, 1], ['F5', 1.0, 2, 3, 2]]
    faciesInTruncRule = ['F1', 'F2', 'F3', 'F4', 'F5']
    gaussFieldsInZone = ['GF1', 'GF2', 'GF3', 'GF4']
    gaussFieldsForBGFacies = ['GF1', 'GF2']
    overlayGroups = []

#    overlayFacies = []
#    backGroundFacies = []
#    overlayTruncCenter = []
    faciesProb = [0.3, 0.1, 0.2, 0.2, 0.2]
#    nGaussFields = 2
    faciesReferenceFile = get_cubic_facies_reference_file_path(22)
    run(
        fTable, faciesInTruncRule, faciesInZone, faciesProb,
        faciesReferenceFile, gaussFieldsInZone,  gaussFieldsForBGFacies, overlayGroups, truncStructure
    )


def test_case_23():
    fTable = {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5'}
    faciesInZone = ['F1', 'F4', 'F3', 'F5', 'F2']
    truncStructure = ['H', ['F1', 1.0, 1, 0, 0], ['F5', 0.5, 2, 1, 0], ['F3', 0.5, 2, 2, 1],
                      ['F4', 1.0, 2, 2, 2],
                      ['F3', 0.5, 2, 3, 1], ['F5', 0.5, 2, 3, 2]]
    faciesInTruncRule = ['F1', 'F5', 'F3', 'F4', 'F2']
    gaussFieldsInZone = ['GF1', 'GF2', 'GF3', 'GF4']
    gaussFieldsForBGFacies = ['GF1', 'GF2']
    overlayGroups = []
    # Group1
    alphaList11 = [['GF3', 'F2', 1.0, 0.4]]
    backgroundList1 =  ['F5', 'F3']
    overlayGroup1 = [alphaList11, backgroundList1]
    overlayGroups.append(overlayGroup1)

#    overlayFacies = ['F2']
#    backGroundFacies = [['F5', 'F3']]
#    overlayTruncCenter = [0.4]
    faciesProb = [0.3, 0.1, 0.2, 0.2, 0.2]
#    nGaussFields = 3
    faciesReferenceFile = get_cubic_facies_reference_file_path(23)
    run(
        fTable, faciesInTruncRule, faciesInZone, faciesProb,
        faciesReferenceFile, gaussFieldsInZone,  gaussFieldsForBGFacies, overlayGroups, truncStructure
    )

def test_case_24():
    fTable = {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5'}
    faciesInZone = ['F1', 'F4', 'F3', 'F5', 'F2']
    truncStructure = ['H', ['F1', 1.0, 1, 0, 0], ['F5', 0.5, 2, 1, 0], ['F3', 0.5, 2, 2, 1],
                      ['F4', 1.0, 2, 2, 2],
                      ['F3', 0.5, 2, 3, 1], ['F5', 0.5, 2, 3, 2]]
    faciesInTruncRule = ['F1', 'F5', 'F3', 'F4', 'F2']
    gaussFieldsInZone = ['GF1', 'GF2', 'GF3', 'GF4','GF5']
    gaussFieldsForBGFacies = ['GF1', 'GF2']
    overlayGroups = []
    # Group1
    alphaList11 = [['GF3', 'F2', 0.4, 0.4],
                   ['GF4', 'F2', 0.3, 0.4],
                   ['GF5', 'F2', 0.3, 0.4]]
    backgroundList1 =  ['F5', 'F3']
    overlayGroup1 = [alphaList11, backgroundList1]
    overlayGroups.append(overlayGroup1)

#    overlayFacies = ['F2']
#    backGroundFacies = [['F5', 'F3']]
#    overlayTruncCenter = [0.4]
    faciesProb = [0.3, 0.1, 0.2, 0.2, 0.2]
#    nGaussFields = 3
    faciesReferenceFile = get_cubic_facies_reference_file_path(24)
    run(
        fTable, faciesInTruncRule, faciesInZone, faciesProb,
        faciesReferenceFile, gaussFieldsInZone,  gaussFieldsForBGFacies, overlayGroups, truncStructure
    )


def run(fTable, faciesInTruncRule, faciesInZone, faciesProb, faciesReferenceFile,
        gaussFieldsInZone, gaussFieldsForBGFacies, overlayGroups, truncStructure):
    [truncRule, truncRule2] = initialize_write_read(
        OUTPUT_MODEL_FILE_NAME1, OUTPUT_MODEL_FILE_NAME2, fTable, faciesInZone,
        gaussFieldsInZone, gaussFieldsForBGFacies, truncStructure, overlayGroups, Debug.OFF
    )
    nGaussFields = truncRule.getNGaussFieldsInModel()
    getClassName(truncRule)
    getFaciesInTruncRule(truncRule, truncRule2, faciesInTruncRule)
    truncMapPolygons(truncRule, truncRule2, faciesProb, OUT_POLY_FILE1, OUT_POLY_FILE2)
    apply_truncations(truncRule, faciesReferenceFile, nGaussFields, CUBIC_GAUSS_FIELD_FILES, FACIES_OUTPUT_FILE)


if __name__ == '__main__':
    test_Trunc2DCubic()
