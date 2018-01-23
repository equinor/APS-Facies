#!/bin/env python
import filecmp
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element

from src.APSMainFaciesTable import APSMainFaciesTable
from src.Trunc2D_Cubic_xml import Trunc2D_Cubic
from src.unit_test.constants import (
    CUBIC_GAUSS_FIELD_FILES, FACIES_OUTPUT_FILE, OUTPUT_MODEL_FILE_NAME1,
    OUTPUT_MODEL_FILE_NAME2, OUT_POLY_FILE1, OUT_POLY_FILE2,
)
from src.unit_test.helpers import (
    apply_truncations, getFaciesInTruncRule, get_cubic_facies_reference_file_path,
    truncMapPolygons,
)
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
        truncStructure, overlayGroups, debug_level=Debug.OFF
):
    mainFaciesTable = APSMainFaciesTable(fTable=fTable)

    # Create an object and initialize it
    truncRuleOut = Trunc2D_Cubic()
    truncRuleOut.initialize(
        mainFaciesTable, faciesInZone, gaussFieldsInZone, gaussFieldsForBGFacies,
        truncStructure, overlayGroups, debug_level
    )

    # Build an xml tree with the data and write it to file
    createXMLTreeAndWriteFile(truncRuleOut, outputModelFileName)
    return truncRuleOut


def initialize_write_read(
        outputModelFileName1, outputModelFileName2, fTable, faciesInZone, gaussFieldsInZone,
        gaussFieldsForBGFacies, truncStructure, overlayGroups, debug_level=Debug.OFF
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
    return truncRuleA, truncRuleB


def getClassName(truncRule):
    assert truncRule is not None
    name = truncRule.getClassName()
    assert name == 'Trunc2D_Cubic'


def test_Trunc2DCubic():
    nCase = 24
    start = 1
    end = 24
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
    run(
        fTable={2: 'F2', 1: 'F1'},
        faciesInZone=['F1', 'F2'],
        truncStructure=['H', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0]],
        faciesInTruncRule=['F1', 'F2'],
        gaussFieldsInZone=['GF1', 'GF2', 'GF3', 'GF4'],
        gaussFieldsForBGFacies=['GF1', 'GF2'],
        overlayGroups=[],
        faciesProb=[0.5, 0.5],
        faciesReferenceFile=get_cubic_facies_reference_file_path(1),
    )


def test_case_2():
    run(
        fTable={2: 'F2', 1: 'F1'},
        faciesInZone=['F1', 'F2'],
        truncStructure=['V', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0]],
        faciesInTruncRule=['F1', 'F2'],
        gaussFieldsInZone=['GF1', 'GF2', 'GF3', 'GF4'],
        gaussFieldsForBGFacies=['GF1', 'GF2'],
        overlayGroups=[],
        faciesProb=[0.5, 0.5],
        faciesReferenceFile=get_cubic_facies_reference_file_path(2),
    )


def test_case_3():
    run(
        fTable={3: 'F3', 2: 'F2', 1: 'F1'},
        faciesInZone=['F1', 'F2', 'F3'],
        truncStructure=['H', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0], ['F3', 1.0, 3, 0, 0]],
        faciesInTruncRule=['F1', 'F2', 'F3'],
        gaussFieldsInZone=['GF1', 'GF2', 'GF3', 'GF4'],
        gaussFieldsForBGFacies=['GF1', 'GF2'],
        overlayGroups=[],
        faciesProb=[0.5, 0.2, 0.3],
        faciesReferenceFile=get_cubic_facies_reference_file_path(3),
    )


def test_case_4():
    run(
        fTable={3: 'F3', 2: 'F2', 1: 'F1'},
        faciesInZone=['F1', 'F2', 'F3'],
        truncStructure=['V', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0], ['F3', 1.0, 3, 0, 0]],
        faciesInTruncRule=['F1', 'F2', 'F3'],
        gaussFieldsInZone=['GF1', 'GF2', 'GF3', 'GF4'],
        gaussFieldsForBGFacies=['GF1', 'GF2'],
        overlayGroups=[],
        faciesProb=[0.5, 0.2, 0.3],
        faciesReferenceFile=get_cubic_facies_reference_file_path(4),
    )


def test_case_5():
    overlayGroups = []

    # Group 1
    alphaList1 = [['GF3', 'F4', 1.0, 0.5]]
    backgroundList = ['F2', 'F3']
    overlayGroup = [alphaList1, backgroundList]
    overlayGroups.append(overlayGroup)

    run(
        fTable={3: 'F3', 2: 'F2', 1: 'F1', 4: 'F4'},
        faciesInZone=['F1', 'F2', 'F3', 'F4'],
        truncStructure=['V', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0], ['F3', 1.0, 3, 0, 0]],
        faciesInTruncRule=['F1', 'F2', 'F3', 'F4'],
        gaussFieldsInZone=['GF1', 'GF2', 'GF3', 'GF4'],
        gaussFieldsForBGFacies=['GF1', 'GF2'],
        overlayGroups=overlayGroups,
        faciesProb=[0.3, 0.2, 0.3, 0.2],
        faciesReferenceFile=get_cubic_facies_reference_file_path(5),
    )


def test_case_6():
    overlayGroups = []

    # Group 1
    alphaList1 = [['GF3', 'F2', 1.0, 1.0]]
    backgroundList = ['F4', 'F1']
    overlayGroup = [alphaList1, backgroundList]
    overlayGroups.append(overlayGroup)

    run(
        fTable={3: 'F3', 2: 'F2', 1: 'F1', 4: 'F4'},
        faciesInZone=['F1', 'F2', 'F3', 'F4'],
        truncStructure=['H', ['F1', 1.0, 1, 0, 0], ['F4', 1.0, 2, 1, 0], ['F3', 1.0, 2, 2, 0]],
        faciesInTruncRule=['F1', 'F4', 'F3', 'F2'],
        gaussFieldsInZone=['GF1', 'GF2', 'GF3', 'GF4'],
        gaussFieldsForBGFacies=['GF1', 'GF2'],
        overlayGroups=overlayGroups,
        faciesProb=[0.4, 0.1, 0.3, 0.2],
        faciesReferenceFile=get_cubic_facies_reference_file_path(6),
    )


def test_case_7():
    overlayGroups = []

    # Group 1
    alphaList1 = [['GF3', 'F3', 1.0, 0.5]]
    backgroundList = ['F2', 'F1']
    overlayGroup = [alphaList1, backgroundList]
    overlayGroups.append(overlayGroup)

    run(
        fTable={3: 'F3', 2: 'F2', 1: 'F1', 4: 'F4'},
        faciesInZone=['F1', 'F2', 'F3', 'F4'],
        truncStructure=['H', ['F1', 1.0, 1, 1, 0], ['F2', 1.0, 1, 2, 0], ['F4', 1.0, 2, 0, 0]],
        faciesInTruncRule=['F1', 'F2', 'F4', 'F3'],
        gaussFieldsInZone=['GF1', 'GF2', 'GF3', 'GF4'],
        gaussFieldsForBGFacies=['GF1', 'GF2'],
        overlayGroups=overlayGroups,
        faciesProb=[0.4, 0.1, 0.3, 0.2],
        faciesReferenceFile=get_cubic_facies_reference_file_path(7),
    )


def test_case_8():
    overlayGroups = []

    # Group 1
    alphaList = [['GF3', 'F4', 1.0, 0.0]]
    backgroundList = ['F1']
    overlayGroup = [alphaList, backgroundList]
    overlayGroups.append(overlayGroup)

    # Group 2
    alphaList = [['GF4', 'F5', 1.0, 0.5]]
    backgroundList = ['F2']
    overlayGroup = [alphaList, backgroundList]
    overlayGroups.append(overlayGroup)

    # Group 3
    alphaList = [['GF5', 'F6', 1.0, 1.0]]
    backgroundList = ['F3']
    overlayGroup = [alphaList, backgroundList]
    overlayGroups.append(overlayGroup)

    run(
        fTable={6: 'F6', 4: 'F4', 3: 'F3', 2: 'F2', 5: 'F5', 1: 'F1'},
        faciesInZone=['F1', 'F2', 'F3', 'F4', 'F5', 'F6'],
        truncStructure=['H', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0], ['F3', 1.0, 3, 0, 0]],
        faciesInTruncRule=['F1', 'F2', 'F3', 'F4', 'F5', 'F6'],
        gaussFieldsInZone=['GF1', 'GF2', 'GF3', 'GF4', 'GF5'],
        gaussFieldsForBGFacies=['GF1', 'GF2'],
        overlayGroups=overlayGroups,
        faciesProb=[0.2, 0.3, 0.1, 0.1, 0.1, 0.2],
        faciesReferenceFile=get_cubic_facies_reference_file_path(8),
    )


def test_case_9():
    overlayGroups = []

    # Group 1
    alphaList = [['GF3', 'F4', 1.0, 0.5]]
    backgroundList = ['F1']
    overlayGroup = [alphaList, backgroundList]
    overlayGroups.append(overlayGroup)

    # Group 2
    alphaList = [['GF4', 'F3', 1.0, 0.8]]
    backgroundList = ['F2']
    overlayGroup = [alphaList, backgroundList]
    overlayGroups.append(overlayGroup)

    run(
        fTable={3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2'},
        faciesInZone=['F2', 'F1', 'F4', 'F3'],
        truncStructure=['V', ['F1', 0.6, 1, 0, 0], ['F2', 1.0, 2, 1, 0], ['F1', 0.4, 2, 2, 0]],
        faciesInTruncRule=['F1', 'F2', 'F4', 'F3'],
        gaussFieldsInZone=['GF1', 'GF2', 'GF3', 'GF4'],
        gaussFieldsForBGFacies=['GF1', 'GF2'],
        overlayGroups=overlayGroups,
        faciesProb=[0.4, 0.1, 0.3, 0.2],
        faciesReferenceFile=get_cubic_facies_reference_file_path(9),
    )


def test_case_10():
    overlayGroups = []

    # Group 1
    alphaList = [['GF3', 'F4', 1.0, 0.5]]
    backgroundList = ['F1']
    overlayGroup = [alphaList, backgroundList]
    overlayGroups.append(overlayGroup)

    # Group 2
    alphaList = [['GF4', 'F2', 1.0, 0.8]]
    backgroundList = ['F3']
    overlayGroup = [alphaList, backgroundList]
    overlayGroups.append(overlayGroup)

    run(
        fTable={3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2'},
        faciesInZone=['F2', 'F1', 'F4', 'F3'],
        truncStructure=['V', ['F1', 1.0, 1, 1, 0], ['F3', 0.3, 1, 2, 0], ['F3', 0.7, 2, 0, 0]],
        faciesInTruncRule=['F1', 'F3', 'F4', 'F2'],
        gaussFieldsInZone=['GF1', 'GF2', 'GF3', 'GF4'],
        gaussFieldsForBGFacies=['GF1', 'GF2'],
        overlayGroups=overlayGroups,
        faciesProb=[0.4, 0.1, 0.3, 0.2],
        faciesReferenceFile=get_cubic_facies_reference_file_path(10),
    )


def test_case_11():
    overlayGroups = []

    # Group 1
    alphaList = [['GF3', 'F5', 1.0, 0.5]]
    backgroundList = ['F1', 'F2', 'F3']
    overlayGroup = [alphaList, backgroundList]
    overlayGroups.append(overlayGroup)

    # Group 2
    alphaList = [['GF4', 'F6', 1.0, 0.8]]
    backgroundList = ['F4']
    overlayGroup = [alphaList, backgroundList]
    overlayGroups.append(overlayGroup)

    run(
        fTable={3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5', 6: 'F6'},
        faciesInZone=['F2', 'F1', 'F4', 'F3', 'F6', 'F5'],
        truncStructure=[
            'H', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0], ['F3', 1.0, 3, 0, 0], ['F4', 1.0, 4, 0, 0]
        ],
        faciesInTruncRule=['F1', 'F2', 'F3', 'F4', 'F5', 'F6'],
        gaussFieldsInZone=['GF1', 'GF2', 'GF3', 'GF4'],
        gaussFieldsForBGFacies=['GF1', 'GF2'],
        overlayGroups=overlayGroups,
        faciesProb=[0.3, 0.1, 0.2, 0.2, 0.1, 0.1],
        faciesReferenceFile=get_cubic_facies_reference_file_path(11),
    )


def test_case_12():
    run(
        fTable={3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2'},
        faciesInZone=['F2', 'F1', 'F4', 'F3'],
        truncStructure=[
            'H', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0], ['F3', 1.0, 3, 0, 0], ['F4', 1.0, 4, 0, 0]
        ],
        faciesInTruncRule=['F1', 'F2', 'F3', 'F4'],
        gaussFieldsInZone=['GF1', 'GF2', 'GF3', 'GF4'],
        gaussFieldsForBGFacies=['GF1', 'GF2'],
        overlayGroups=[],
        faciesProb=[0.3, 0.1, 0.3, 0.3],
        faciesReferenceFile=get_cubic_facies_reference_file_path(12),
    )


def test_case_13():
    overlayGroups = []

    # Group 1
    alphaList = [['GF3', 'F5', 1.0, 0.3]]
    backgroundList = ['F1', 'F3']
    overlayGroup = [alphaList, backgroundList]
    overlayGroups.append(overlayGroup)

    # Group 2
    alphaList = [['GF4', 'F6', 1.0, 0.7]]
    backgroundList = ['F4', 'F2']
    overlayGroup = [alphaList, backgroundList]
    overlayGroups.append(overlayGroup)

    run(
        fTable={3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5', 6: 'F6'},
        faciesInZone=['F2', 'F1', 'F4', 'F3', 'F6', 'F5'],
        truncStructure=[
            'V', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0], ['F3', 1.0, 3, 0, 0], ['F4', 1.0, 4, 0, 0]
        ],
        faciesInTruncRule=['F1', 'F2', 'F3', 'F4', 'F5', 'F6'],
        gaussFieldsInZone=['GF1', 'GF2', 'GF3', 'GF4'],
        gaussFieldsForBGFacies=['GF1', 'GF2'],
        overlayGroups=overlayGroups,
        faciesProb=[0.3, 0.1, 0.2, 0.2, 0.1, 0.1],
        faciesReferenceFile=get_cubic_facies_reference_file_path(13),
    )


def test_case_14():
    overlayGroups = []

    # Group 1
    alphaList = [['GF3', 'F5', 1.0, 0.3]]
    backgroundList = ['F1', 'F3']
    overlayGroup = [alphaList, backgroundList]
    overlayGroups.append(overlayGroup)

    # Group 2
    alphaList = [['GF4', 'F6', 1.0, 0.7]]
    backgroundList = ['F4', 'F2']
    overlayGroup = [alphaList, backgroundList]
    overlayGroups.append(overlayGroup)

    run(
        fTable={3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5', 6: 'F6'},
        faciesInZone=['F2', 'F1', 'F4', 'F3', 'F6', 'F5'],
        truncStructure=[
            'H', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0], ['F3', 1.0, 3, 1, 0], ['F4', 1.0, 3, 2, 0]
        ],
        faciesInTruncRule=['F1', 'F2', 'F3', 'F4', 'F5', 'F6'],
        gaussFieldsInZone=['GF1', 'GF2', 'GF3', 'GF4'],
        gaussFieldsForBGFacies=['GF1', 'GF2'],
        overlayGroups=overlayGroups,
        faciesProb=[0.3, 0.1, 0.2, 0.2, 0.1, 0.1],
        faciesReferenceFile=get_cubic_facies_reference_file_path(14),
    )


def test_case_15():
    overlayGroups = []

    # Group 1
    alphaList = [['GF3', 'F5', 1.0, 0.3]]
    backgroundList = ['F1', 'F3']
    overlayGroup = [alphaList, backgroundList]
    overlayGroups.append(overlayGroup)

    # Group 2
    alphaList = [['GF4', 'F6', 1.0, 0.7]]
    backgroundList = ['F4', 'F2']
    overlayGroup = [alphaList, backgroundList]
    overlayGroups.append(overlayGroup)

    run(
        fTable={3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5', 6: 'F6'},
        faciesInZone=['F2', 'F1', 'F4', 'F3', 'F6', 'F5'],
        truncStructure=[
            'V', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0], ['F3', 1.0, 3, 1, 0], ['F4', 1.0, 3, 2, 0]
        ],
        faciesInTruncRule=['F1', 'F2', 'F3', 'F4', 'F5', 'F6'],
        gaussFieldsInZone=['GF1', 'GF2', 'GF3', 'GF4'],
        gaussFieldsForBGFacies=['GF1', 'GF2'],
        overlayGroups=overlayGroups,
        faciesProb=[0.3, 0.1, 0.2, 0.2, 0.1, 0.1],
        faciesReferenceFile=get_cubic_facies_reference_file_path(15),
    )


def test_case_16():
    run(
        fTable={3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2'},
        faciesInZone=['F2', 'F1', 'F4', 'F3'],
        truncStructure=[
            'V', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0], ['F3', 1.0, 3, 1, 0], ['F4', 1.0, 3, 2, 0]
        ],
        faciesInTruncRule=['F1', 'F2', 'F3', 'F4'],
        gaussFieldsInZone=['GF1', 'GF2', 'GF3', 'GF4'],
        gaussFieldsForBGFacies=['GF1', 'GF2'],
        overlayGroups=[],
        faciesProb=[0.3, 0.2, 0.2, 0.3],
        faciesReferenceFile=get_cubic_facies_reference_file_path(16),
    )


def test_case_17():
    overlayGroups = []

    # Group 1
    alphaList = [['GF3', 'F6', 1.0, 0.3]]
    backgroundList = ['F1', 'F3', 'F4', 'F2']
    overlayGroup = [alphaList, backgroundList]
    overlayGroups.append(overlayGroup)

    run(
        fTable={3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5', 6: 'F6'},
        faciesInZone=['F2', 'F1', 'F4', 'F3', 'F6', 'F5'],
        truncStructure=[
            'H', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0],
            ['F3', 1.0, 3, 0, 0], ['F4', 1.0, 4, 0, 0], ['F5', 1.0, 5, 0, 0]
        ],
        faciesInTruncRule=['F1', 'F2', 'F3', 'F4', 'F5', 'F6'],
        gaussFieldsInZone=['GF1', 'GF2', 'GF3', 'GF4'],
        gaussFieldsForBGFacies=['GF1', 'GF2'],
        overlayGroups=overlayGroups,
        faciesProb=[0.3, 0.1, 0.2, 0.2, 0.1, 0.1],
        faciesReferenceFile=get_cubic_facies_reference_file_path(17),
    )


def test_case_18():
    overlayGroups = []

    # Group 1
    alphaList = [['GF3', 'F6', 1.0, 0.3]]
    backgroundList = ['F1', 'F3', 'F4', 'F2']
    overlayGroup = [alphaList, backgroundList]
    overlayGroups.append(overlayGroup)

    # Group 2
    alphaList = [['GF4', 'F7', 1.0, 0.9]]
    backgroundList = ['F5']
    overlayGroup = [alphaList, backgroundList]
    overlayGroups.append(overlayGroup)

    run(
        fTable={3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5', 6: 'F6', 7: 'F7'},
        faciesInZone=['F2', 'F1', 'F4', 'F3', 'F6', 'F5', 'F7'],
        truncStructure=[
            'H', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0],
            ['F3', 1.0, 3, 0, 0], ['F4', 1.0, 4, 0, 0], ['F5', 1.0, 5, 0, 0]
        ],
        faciesInTruncRule=['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7'],
        gaussFieldsInZone=['GF1', 'GF2', 'GF3', 'GF4'],
        gaussFieldsForBGFacies=['GF1', 'GF2'],
        overlayGroups=overlayGroups,
        faciesProb=[0.2, 0.1, 0.2, 0.2, 0.1, 0.1, 0.1],
        faciesReferenceFile=get_cubic_facies_reference_file_path(18),
    )


def test_case_19():
    overlayGroups = []

    # Group 1
    alphaList = [['GF3', 'F6', 1.0, 0.3]]
    backgroundList = ['F1', 'F3', 'F4', 'F2']
    overlayGroup = [alphaList, backgroundList]
    overlayGroups.append(overlayGroup)

    # Group 2
    alphaList = [['GF4', 'F7', 1.0, 0.9]]
    backgroundList = ['F5']
    overlayGroup = [alphaList, backgroundList]
    overlayGroups.append(overlayGroup)

    run(
        fTable={3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5', 6: 'F6', 7: 'F7'},
        faciesInZone=['F2', 'F1', 'F4', 'F3', 'F6', 'F5', 'F7'],
        truncStructure=[
            'H', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 1, 1],
            ['F3', 1.0, 2, 1, 2], ['F4', 1.0, 2, 2, 1], ['F5', 1.0, 2, 2, 2]
        ],
        faciesInTruncRule=['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7'],
        gaussFieldsInZone=['GF1', 'GF2', 'GF3', 'GF4'],
        gaussFieldsForBGFacies=['GF1', 'GF2'],
        overlayGroups=overlayGroups,
        faciesProb=[0.2, 0.1, 0.2, 0.2, 0.1, 0.1, 0.1],
        faciesReferenceFile=get_cubic_facies_reference_file_path(19),
    )


def test_case_20():
    overlayGroups = []

    # Group 1
    alphaList = [['GF3', 'F1', 1.0, 0.3]]
    backgroundList = ['F2']
    overlayGroup = [alphaList, backgroundList]
    overlayGroups.append(overlayGroup)

    # Group 2
    alphaList = [['GF4', 'F5', 1.0, 0.9]]
    backgroundList = ['F3']
    overlayGroup = [alphaList, backgroundList]
    overlayGroups.append(overlayGroup)

    # Group 3
    alphaList = [['GF5', 'F6', 1.0, 0.0]]
    backgroundList = ['F4']
    overlayGroup = [alphaList, backgroundList]
    overlayGroups.append(overlayGroup)

    run(
        fTable={3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5', 6: 'F6'},
        faciesInZone=['F2', 'F1', 'F4', 'F3', 'F6', 'F5'],
        truncStructure=[
            'V', ['F4', 0.4, 1, 0, 0], ['F2', 1.0, 2, 1, 0],
            ['F3', 1.0, 2, 2, 1], ['F4', 0.3, 2, 2, 2], ['F4', 0.3, 2, 3, 0]
        ],
        faciesInTruncRule=['F4', 'F2', 'F3', 'F1', 'F5', 'F6'],
        gaussFieldsInZone=['GF1', 'GF2', 'GF3', 'GF4', 'GF5'],
        gaussFieldsForBGFacies=['GF1', 'GF2'],
        overlayGroups=overlayGroups,
        faciesProb=[0.3, 0.1, 0.2, 0.2, 0.1, 0.1],
        faciesReferenceFile=get_cubic_facies_reference_file_path(20),
    )


def test_case_21():
    overlayGroups = []

    # Group 1
    alphaList = [['GF3', 'F1', 1.0, 0.3]]
    backgroundList = ['F4']
    overlayGroup = [alphaList, backgroundList]
    overlayGroups.append(overlayGroup)

    run(
        fTable={3: 'F1', 2: 'F3', 1: 'F4'},
        faciesInZone=['F1', 'F4', 'F3'],
        truncStructure=[
            'V', ['F4', 0.2, 1, 0, 0], ['F4', 0.2, 2, 1, 0],
            ['F3', 1.0, 2, 2, 1], ['F4', 0.3, 2, 2, 2], ['F4', 0.3, 2, 3, 0]
        ],
        faciesInTruncRule=['F4', 'F3', 'F1'],
        gaussFieldsInZone=['GF1', 'GF2', 'GF3', 'GF4'],
        gaussFieldsForBGFacies=['GF1', 'GF2'],
        overlayGroups=overlayGroups,
        faciesProb=[0.3, 0.3, 0.4],
        faciesReferenceFile=get_cubic_facies_reference_file_path(21),
    )


def test_case_22():
    run(
        fTable={3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5'},
        faciesInZone=['F1', 'F4', 'F3', 'F5', 'F2'],
        truncStructure=[
            'H', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 1, 0], ['F3', 0.5, 2, 2, 1],
            ['F4', 1.0, 2, 2, 2], ['F3', 0.5, 2, 3, 1], ['F5', 1.0, 2, 3, 2]
        ],
        faciesInTruncRule=['F1', 'F2', 'F3', 'F4', 'F5'],
        gaussFieldsInZone=['GF1', 'GF2', 'GF3', 'GF4'],
        gaussFieldsForBGFacies=['GF1', 'GF2'],
        overlayGroups=[],
        faciesProb=[0.3, 0.1, 0.2, 0.2, 0.2],
        faciesReferenceFile=get_cubic_facies_reference_file_path(22),
    )


def test_case_23():
    overlayGroups = []

    # Group 1
    alphaList = [['GF3', 'F2', 1.0, 0.4]]
    backgroundList = ['F5', 'F3']
    overlayGroup = [alphaList, backgroundList]
    overlayGroups.append(overlayGroup)

    run(
        fTable={3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5'},
        faciesInZone=['F1', 'F4', 'F3', 'F5', 'F2'],
        truncStructure=[
            'H', ['F1', 1.0, 1, 0, 0], ['F5', 0.5, 2, 1, 0], ['F3', 0.5, 2, 2, 1],
            ['F4', 1.0, 2, 2, 2], ['F3', 0.5, 2, 3, 1], ['F5', 0.5, 2, 3, 2]
        ],
        faciesInTruncRule=['F1', 'F5', 'F3', 'F4', 'F2'],
        gaussFieldsInZone=['GF1', 'GF2', 'GF3', 'GF4'],
        gaussFieldsForBGFacies=['GF1', 'GF2'],
        overlayGroups=overlayGroups,
        faciesProb=[0.3, 0.1, 0.2, 0.2, 0.2],
        faciesReferenceFile=get_cubic_facies_reference_file_path(23),
    )


def test_case_24():
    overlayGroups = []

    # Group 1
    alphaList = [
        ['GF3', 'F2', 0.4, 0.4],
        ['GF4', 'F2', 0.3, 0.4],
        ['GF5', 'F2', 0.3, 0.4]
    ]
    backgroundList = ['F5', 'F3']
    overlayGroup = [alphaList, backgroundList]
    overlayGroups.append(overlayGroup)

    run(
        fTable={3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5'},
        faciesInZone=['F1', 'F4', 'F3', 'F5', 'F2'],
        truncStructure=[
            'H', ['F1', 1.0, 1, 0, 0], ['F5', 0.5, 2, 1, 0], ['F3', 0.5, 2, 2, 1],
            ['F4', 1.0, 2, 2, 2], ['F3', 0.5, 2, 3, 1], ['F5', 0.5, 2, 3, 2]
        ],
        faciesInTruncRule=['F1', 'F5', 'F3', 'F4', 'F2'],
        gaussFieldsInZone=['GF1', 'GF2', 'GF3', 'GF4', 'GF5'],
        gaussFieldsForBGFacies=['GF1', 'GF2'],
        overlayGroups=overlayGroups,
        faciesProb=[0.3, 0.1, 0.2, 0.2, 0.2],
        faciesReferenceFile=get_cubic_facies_reference_file_path(24),
    )


def run(
        fTable, faciesInTruncRule, faciesInZone, faciesProb, faciesReferenceFile,
        gaussFieldsInZone, gaussFieldsForBGFacies, overlayGroups, truncStructure
):
    truncRule, truncRule2 = initialize_write_read(
        outputModelFileName1=OUTPUT_MODEL_FILE_NAME1,
        outputModelFileName2=OUTPUT_MODEL_FILE_NAME2,
        fTable=fTable,
        faciesInZone=faciesInZone,
        gaussFieldsInZone=gaussFieldsInZone,
        gaussFieldsForBGFacies=gaussFieldsForBGFacies,
        truncStructure=truncStructure,
        overlayGroups=overlayGroups,
        debug_level=Debug.OFF
    )
    nGaussFields = truncRule.getNGaussFieldsInModel()
    getClassName(truncRule)
    getFaciesInTruncRule(truncRule, truncRule2, faciesInTruncRule)
    truncMapPolygons(
        truncRule=truncRule,
        truncRule2=truncRule2,
        faciesProb=faciesProb,
        outPolyFile1=OUT_POLY_FILE1,
        outPolyFile2=OUT_POLY_FILE2
    )
    apply_truncations(
        truncRule=truncRule,
        faciesReferenceFile=faciesReferenceFile,
        nGaussFields=nGaussFields,
        gaussFieldFiles=CUBIC_GAUSS_FIELD_FILES,
        faciesOutputFile=FACIES_OUTPUT_FILE
    )


if __name__ == '__main__':
    test_Trunc2DCubic()
