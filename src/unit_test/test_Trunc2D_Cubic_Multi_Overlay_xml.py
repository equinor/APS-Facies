#!/bin/env python
import filecmp
import sys
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element

from src.APSMainFaciesTable import APSMainFaciesTable
from src.Trunc2D_Cubic_Multi_Overlay_xml import Trunc2D_Cubic_Multi_Overlay
from src.unit_test.helpers import apply_truncations, getFaciesInTruncRule, truncMapPolygons
from src.utils.methods import prettify


def interpretXMLModelFileAndWrite(modelFileName, outputModelFileName, fTable, faciesInZone, printInfo):
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
    print('Number of gauss fields required for truncation rule: ' + str(nGaussFields))

    mainFaciesTable = APSMainFaciesTable()
    mainFaciesTable.initialize(fTable)

    # Create truncation rule object from input data, not read from file
    truncRuleOut = Trunc2D_Cubic_Multi_Overlay(
        trRule, mainFaciesTable, faciesInZone,
        nGaussFields, printInfo, modelFileName
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
        outputModelFileName, fTable, faciesInZone, truncStructure,
        backGroundFacies, overlayFacies, overlayTruncCenter, printInfo
):
    mainFaciesTable = APSMainFaciesTable()
    mainFaciesTable.initialize(fTable)

    # Create an object and initialize it
    truncRuleOut = Trunc2D_Cubic_Multi_Overlay()
    truncRuleOut.initialize(
        mainFaciesTable, faciesInZone, truncStructure,
        backGroundFacies, overlayFacies, overlayTruncCenter, printInfo
    )

    # Build an xml tree with the data and write it to file
    createXMLTreeAndWriteFile(truncRuleOut, outputModelFileName)
    return truncRuleOut


def initialize_write_read(
        outputModelFileName1, outputModelFileName2, fTable, faciesInZone, truncStructure,
        backGroundFacies, overlayFacies, overlayTruncCenter, printInfo
):
    file1 = outputModelFileName1
    file2 = outputModelFileName2
    # Create an object for truncation rule and write to file
    # Global variable truncRule
    truncRuleA = createTrunc(
        file1, fTable, faciesInZone, truncStructure,
        backGroundFacies, overlayFacies, overlayTruncCenter, printInfo
    )
    inputFile = file1

    # Write datastructure:
    #    truncRule.writeContentsInDataStructure()
    # Read the previously written file as and XML file and write it out again to a new file
    # Global variable truncRule2
    truncRuleB = interpretXMLModelFileAndWrite(inputFile, file2, fTable, faciesInZone, printInfo)

    # Compare the original xml file created in createTrunc and the xml file written by interpretXMLModelFileAndWrite
    check = filecmp.cmp(file1, file2)
    print('Compare file: ' + file1 + ' and file: ' + file2)
    assert check is True
    if check is False:
        print('Error: Files are different')
        sys.exit()
    else:
        print('Files are equal: OK')
    return [truncRuleA, truncRuleB]


def getClassName(truncRule):
    assert truncRule is not None
    name = truncRule.getClassName()
    assert name == 'Trunc2D_Cubic_Multi_Overlay'


def test_Trunc2DCubicMultiOverlay():
    outputModelFileName1 = 'test_Trunc_output1.xml'
    outputModelFileName2 = 'test_Trunc_output2.xml'
    outPolyFile1 = 'test_Trunc_polygons1.dat'
    outPolyFile2 = 'test_Trunc_polygons2.dat'
    gaussFieldFiles = ['testData_Cubic/a1.dat', 'testData_Cubic/a2.dat', 'testData_Cubic/a3.dat',
                       'testData_Cubic/a4.dat',
                       'testData_Cubic/a5.dat', 'testData_Cubic/a6.dat']

    nGaussFields = 3
    printInfo = 0
    nCase = 23
    start = 1
    end = 23
    for testCase in range(start, end + 1):
        print('Case number: ' + str(testCase))
        faciesReferenceFile = 'testData_Cubic/test_case_' + str(testCase) + '.dat'
        faciesOutputFile = 'facies2D.dat'
        if testCase == 1:
            fTable = {2: 'F2', 1: 'F1'}
            faciesInZone = ['F1', 'F2']
            truncStructure = ['H', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0]]
            faciesInTruncRule = ['F1', 'F2']
            overlayFacies = []
            backGroundFacies = []
            overlayTruncCenter = []
            faciesProb = [0.5, 0.5]
            nGaussFields = 2
            run(
                backGroundFacies, fTable, faciesInTruncRule, faciesInZone, faciesOutputFile, faciesProb,
                faciesReferenceFile, gaussFieldFiles, nGaussFields, outPolyFile1, outPolyFile2, outputModelFileName1,
                outputModelFileName2, overlayFacies, overlayTruncCenter, printInfo, truncStructure
            )

        elif testCase == 2:
            fTable = {2: 'F2', 1: 'F1'}
            faciesInZone = ['F1', 'F2']
            truncStructure = ['V', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0]]
            faciesInTruncRule = ['F1', 'F2']
            overlayFacies = []
            backGroundFacies = []
            overlayTruncCenter = []
            faciesProb = [0.5, 0.5]
            nGaussFields = 2
            run(
                backGroundFacies, fTable, faciesInTruncRule, faciesInZone, faciesOutputFile, faciesProb,
                faciesReferenceFile, gaussFieldFiles, nGaussFields, outPolyFile1, outPolyFile2, outputModelFileName1,
                outputModelFileName2, overlayFacies, overlayTruncCenter, printInfo, truncStructure
            )

        elif testCase == 3:
            fTable = {3: 'F3', 2: 'F2', 1: 'F1'}
            faciesInZone = ['F1', 'F2', 'F3']
            truncStructure = ['H', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0], ['F3', 1.0, 3, 0, 0]]
            faciesInTruncRule = ['F1', 'F2', 'F3']
            overlayFacies = []
            backGroundFacies = []
            overlayTruncCenter = []
            faciesProb = [0.5, 0.2, 0.3]
            nGaussFields = 2
            run(
                backGroundFacies, fTable, faciesInTruncRule, faciesInZone, faciesOutputFile, faciesProb,
                faciesReferenceFile, gaussFieldFiles, nGaussFields, outPolyFile1, outPolyFile2, outputModelFileName1,
                outputModelFileName2, overlayFacies, overlayTruncCenter, printInfo, truncStructure
            )

        elif testCase == 4:
            fTable = {3: 'F3', 2: 'F2', 1: 'F1'}
            faciesInZone = ['F1', 'F2', 'F3']
            truncStructure = ['V', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0], ['F3', 1.0, 3, 0, 0]]
            faciesInTruncRule = ['F1', 'F2', 'F3']
            overlayFacies = []
            backGroundFacies = []
            overlayTruncCenter = []
            faciesProb = [0.5, 0.2, 0.3]
            nGaussFields = 2
            run(
                backGroundFacies, fTable, faciesInTruncRule, faciesInZone, faciesOutputFile, faciesProb,
                faciesReferenceFile, gaussFieldFiles, nGaussFields, outPolyFile1, outPolyFile2, outputModelFileName1,
                outputModelFileName2, overlayFacies, overlayTruncCenter, printInfo, truncStructure
            )

        elif testCase == 5:
            fTable = {3: 'F3', 2: 'F2', 1: 'F1', 4: 'F4'}
            faciesInZone = ['F1', 'F2', 'F3', 'F4']
            truncStructure = ['V', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0], ['F3', 1.0, 3, 0, 0]]
            faciesInTruncRule = ['F1', 'F2', 'F3', 'F4']
            overlayFacies = ['F4']
            backGroundFacies = [['F2', 'F3']]
            overlayTruncCenter = [0.5]
            faciesProb = [0.3, 0.2, 0.3, 0.2]
            nGaussFields = 3
            run(
                backGroundFacies, fTable, faciesInTruncRule, faciesInZone, faciesOutputFile, faciesProb,
                faciesReferenceFile, gaussFieldFiles, nGaussFields, outPolyFile1, outPolyFile2, outputModelFileName1,
                outputModelFileName2, overlayFacies, overlayTruncCenter, printInfo, truncStructure
            )

        elif testCase == 6:
            fTable = {3: 'F3', 2: 'F2', 1: 'F1', 4: 'F4'}
            faciesInZone = ['F1', 'F2', 'F3', 'F4']
            truncStructure = ['H', ['F1', 1.0, 1, 0, 0], ['F4', 1.0, 2, 1, 0], ['F3', 1.0, 2, 2, 0]]
            faciesInTruncRule = ['F1', 'F4', 'F3', 'F2']
            overlayFacies = ['F2']
            backGroundFacies = [['F4', 'F1']]
            overlayTruncCenter = [1.0]
            faciesProb = [0.4, 0.1, 0.3, 0.2]
            nGaussFields = 3
            run(
                backGroundFacies, fTable, faciesInTruncRule, faciesInZone, faciesOutputFile, faciesProb,
                faciesReferenceFile, gaussFieldFiles, nGaussFields, outPolyFile1, outPolyFile2, outputModelFileName1,
                outputModelFileName2, overlayFacies, overlayTruncCenter, printInfo, truncStructure
            )

        elif testCase == 7:
            fTable = {3: 'F3', 2: 'F2', 1: 'F1', 4: 'F4'}
            faciesInZone = ['F1', 'F2', 'F3', 'F4']
            truncStructure = ['H', ['F1', 1.0, 1, 1, 0], ['F2', 1.0, 1, 2, 0], ['F4', 1.0, 2, 0, 0]]
            faciesInTruncRule = ['F1', 'F2', 'F4', 'F3']
            overlayFacies = ['F3']
            backGroundFacies = [['F2', 'F1']]
            overlayTruncCenter = [0.5]
            faciesProb = [0.4, 0.1, 0.3, 0.2]
            nGaussFields = 3
            run(
                backGroundFacies, fTable, faciesInTruncRule, faciesInZone, faciesOutputFile, faciesProb,
                faciesReferenceFile, gaussFieldFiles, nGaussFields, outPolyFile1, outPolyFile2, outputModelFileName1,
                outputModelFileName2, overlayFacies, overlayTruncCenter, printInfo, truncStructure
            )

        elif testCase == 8:
            fTable = {6: 'F6', 4: 'F4', 3: 'F3', 2: 'F2', 5: 'F5', 1: 'F1'}
            faciesInZone = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6']
            truncStructure = ['H', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0], ['F3', 1.0, 3, 0, 0]]
            faciesInTruncRule = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6']
            overlayFacies = ['F4', 'F5', 'F6']
            backGroundFacies = [['F1'], ['F2'], ['F3']]
            overlayTruncCenter = [0.0, 0.5, 1.0]
            faciesProb = [0.2, 0.3, 0.1, 0.1, 0.1, 0.2]
            nGaussFields = 5
            run(
                backGroundFacies, fTable, faciesInTruncRule, faciesInZone, faciesOutputFile, faciesProb,
                faciesReferenceFile, gaussFieldFiles, nGaussFields, outPolyFile1, outPolyFile2, outputModelFileName1,
                outputModelFileName2, overlayFacies, overlayTruncCenter, printInfo, truncStructure
            )

        elif testCase == 9:
            fTable = {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2'}
            faciesInZone = ['F2', 'F1', 'F4', 'F3']
            truncStructure = ['V', ['F1', 0.6, 1, 0, 0], ['F2', 1.0, 2, 1, 0], ['F1', 0.4, 2, 2, 0]]
            faciesInTruncRule = ['F1', 'F2', 'F4', 'F3']
            overlayFacies = ['F4', 'F3']
            backGroundFacies = [['F1'], ['F2']]
            overlayTruncCenter = [0.5, 0.8]
            faciesProb = [0.4, 0.1, 0.3, 0.2]
            nGaussFields = 4
            run(
                backGroundFacies, fTable, faciesInTruncRule, faciesInZone, faciesOutputFile, faciesProb,
                faciesReferenceFile, gaussFieldFiles, nGaussFields, outPolyFile1, outPolyFile2, outputModelFileName1,
                outputModelFileName2, overlayFacies, overlayTruncCenter, printInfo, truncStructure
            )

        elif testCase == 10:
            fTable = {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2'}
            faciesInZone = ['F2', 'F1', 'F4', 'F3']
            truncStructure = ['V', ['F1', 1.0, 1, 1, 0], ['F3', 0.3, 1, 2, 0], ['F3', 0.7, 2, 0, 0]]
            faciesInTruncRule = ['F1', 'F3', 'F4', 'F2']
            overlayFacies = ['F4', 'F2']
            backGroundFacies = [['F1'], ['F3']]
            overlayTruncCenter = [0.5, 0.8]
            faciesProb = [0.4, 0.1, 0.3, 0.2]
            nGaussFields = 4
            run(
                backGroundFacies, fTable, faciesInTruncRule, faciesInZone, faciesOutputFile, faciesProb,
                faciesReferenceFile, gaussFieldFiles, nGaussFields, outPolyFile1, outPolyFile2, outputModelFileName1,
                outputModelFileName2, overlayFacies, overlayTruncCenter, printInfo, truncStructure
            )

        elif testCase == 11:
            fTable = {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5', 6: 'F6'}
            faciesInZone = ['F2', 'F1', 'F4', 'F3', 'F6', 'F5']
            truncStructure = ['H', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0], ['F3', 1.0, 3, 0, 0],
                              ['F4', 1.0, 4, 0, 0]]
            faciesInTruncRule = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6']
            overlayFacies = ['F5', 'F6']
            backGroundFacies = [['F1', 'F2', 'F3'], ['F4']]
            overlayTruncCenter = [0.5, 0.8]
            faciesProb = [0.3, 0.1, 0.2, 0.2, 0.1, 0.1]
            nGaussFields = 4
            run(
                backGroundFacies, fTable, faciesInTruncRule, faciesInZone, faciesOutputFile, faciesProb,
                faciesReferenceFile, gaussFieldFiles, nGaussFields, outPolyFile1, outPolyFile2, outputModelFileName1,
                outputModelFileName2, overlayFacies, overlayTruncCenter, printInfo, truncStructure
            )

        elif testCase == 12:
            fTable = {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2'}
            faciesInZone = ['F2', 'F1', 'F4', 'F3']
            truncStructure = ['H', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0], ['F3', 1.0, 3, 0, 0],
                              ['F4', 1.0, 4, 0, 0]]
            faciesInTruncRule = ['F1', 'F2', 'F3', 'F4']
            overlayFacies = []
            backGroundFacies = []
            overlayTruncCenter = []
            faciesProb = [0.3, 0.1, 0.3, 0.3]
            nGaussFields = 2
            run(
                backGroundFacies, fTable, faciesInTruncRule, faciesInZone, faciesOutputFile, faciesProb,
                faciesReferenceFile, gaussFieldFiles, nGaussFields, outPolyFile1, outPolyFile2, outputModelFileName1,
                outputModelFileName2, overlayFacies, overlayTruncCenter, printInfo, truncStructure
            )

        elif testCase == 13:
            fTable = {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5', 6: 'F6'}
            faciesInZone = ['F2', 'F1', 'F4', 'F3', 'F6', 'F5']
            truncStructure = ['V', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0], ['F3', 1.0, 3, 0, 0],
                              ['F4', 1.0, 4, 0, 0]]
            faciesInTruncRule = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6']
            overlayFacies = ['F5', 'F6']
            backGroundFacies = [['F1', 'F3'], ['F4', 'F2']]
            overlayTruncCenter = [0.3, 0.7]
            faciesProb = [0.3, 0.1, 0.2, 0.2, 0.1, 0.1]
            nGaussFields = 4
            run(
                backGroundFacies, fTable, faciesInTruncRule, faciesInZone, faciesOutputFile, faciesProb,
                faciesReferenceFile, gaussFieldFiles, nGaussFields, outPolyFile1, outPolyFile2, outputModelFileName1,
                outputModelFileName2, overlayFacies, overlayTruncCenter, printInfo, truncStructure
            )

        elif testCase == 14:
            fTable = {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5', 6: 'F6'}
            faciesInZone = ['F2', 'F1', 'F4', 'F3', 'F6', 'F5']
            truncStructure = ['H', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0], ['F3', 1.0, 3, 1, 0],
                              ['F4', 1.0, 3, 2, 0]]
            faciesInTruncRule = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6']
            overlayFacies = ['F5', 'F6']
            backGroundFacies = [['F1', 'F3'], ['F4', 'F2']]
            overlayTruncCenter = [0.3, 0.7]
            faciesProb = [0.3, 0.1, 0.2, 0.2, 0.1, 0.1]
            nGaussFields = 4
            run(
                backGroundFacies, fTable, faciesInTruncRule, faciesInZone, faciesOutputFile, faciesProb,
                faciesReferenceFile, gaussFieldFiles, nGaussFields, outPolyFile1, outPolyFile2, outputModelFileName1,
                outputModelFileName2, overlayFacies, overlayTruncCenter, printInfo, truncStructure
            )

        elif testCase == 15:
            fTable = {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5', 6: 'F6'}
            faciesInZone = ['F2', 'F1', 'F4', 'F3', 'F6', 'F5']
            truncStructure = ['V', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0], ['F3', 1.0, 3, 1, 0],
                              ['F4', 1.0, 3, 2, 0]]
            faciesInTruncRule = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6']
            overlayFacies = ['F5', 'F6']
            backGroundFacies = [['F1', 'F3'], ['F4', 'F2']]
            overlayTruncCenter = [0.3, 0.7]
            faciesProb = [0.3, 0.1, 0.2, 0.2, 0.1, 0.1]
            nGaussFields = 4
            run(
                backGroundFacies, fTable, faciesInTruncRule, faciesInZone, faciesOutputFile, faciesProb,
                faciesReferenceFile, gaussFieldFiles, nGaussFields, outPolyFile1, outPolyFile2, outputModelFileName1,
                outputModelFileName2, overlayFacies, overlayTruncCenter, printInfo, truncStructure
            )

        elif testCase == 16:
            fTable = {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2'}
            faciesInZone = ['F2', 'F1', 'F4', 'F3']
            truncStructure = ['V', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0], ['F3', 1.0, 3, 1, 0],
                              ['F4', 1.0, 3, 2, 0]]
            faciesInTruncRule = ['F1', 'F2', 'F3', 'F4']
            overlayFacies = []
            backGroundFacies = []
            overlayTruncCenter = []
            faciesProb = [0.3, 0.2, 0.2, 0.3]
            nGaussFields = 2
            run(
                backGroundFacies, fTable, faciesInTruncRule, faciesInZone, faciesOutputFile, faciesProb,
                faciesReferenceFile, gaussFieldFiles, nGaussFields, outPolyFile1, outPolyFile2, outputModelFileName1,
                outputModelFileName2, overlayFacies, overlayTruncCenter, printInfo, truncStructure
            )

        elif testCase == 17:
            fTable = {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5', 6: 'F6'}
            faciesInZone = ['F2', 'F1', 'F4', 'F3', 'F6', 'F5']
            truncStructure = ['H', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0], ['F3', 1.0, 3, 0, 0],
                              ['F4', 1.0, 4, 0, 0],
                              ['F5', 1.0, 5, 0, 0]]
            faciesInTruncRule = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6']
            overlayFacies = ['F6']
            backGroundFacies = [['F1', 'F3', 'F4', 'F2']]
            overlayTruncCenter = [0.3]
            faciesProb = [0.3, 0.1, 0.2, 0.2, 0.1, 0.1]
            nGaussFields = 3
            run(
                backGroundFacies, fTable, faciesInTruncRule, faciesInZone, faciesOutputFile, faciesProb,
                faciesReferenceFile, gaussFieldFiles, nGaussFields, outPolyFile1, outPolyFile2, outputModelFileName1,
                outputModelFileName2, overlayFacies, overlayTruncCenter, printInfo, truncStructure
            )

        elif testCase == 18:
            fTable = {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5', 6: 'F6', 7: 'F7'}
            faciesInZone = ['F2', 'F1', 'F4', 'F3', 'F6', 'F5', 'F7']
            truncStructure = ['H', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 0, 0], ['F3', 1.0, 3, 0, 0],
                              ['F4', 1.0, 4, 0, 0],
                              ['F5', 1.0, 5, 0, 0]]
            faciesInTruncRule = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7']
            overlayFacies = ['F6', 'F7']
            backGroundFacies = [['F1', 'F3', 'F4', 'F2'], ['F5']]
            overlayTruncCenter = [0.3, 0.9]
            faciesProb = [0.2, 0.1, 0.2, 0.2, 0.1, 0.1, 0.1]
            nGaussFields = 4
            run(
                backGroundFacies, fTable, faciesInTruncRule, faciesInZone, faciesOutputFile, faciesProb,
                faciesReferenceFile, gaussFieldFiles, nGaussFields, outPolyFile1, outPolyFile2, outputModelFileName1,
                outputModelFileName2, overlayFacies, overlayTruncCenter, printInfo, truncStructure
            )

        elif testCase == 19:
            fTable = {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5', 6: 'F6', 7: 'F7'}
            faciesInZone = ['F2', 'F1', 'F4', 'F3', 'F6', 'F5', 'F7']
            truncStructure = ['H', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 1, 1], ['F3', 1.0, 2, 1, 2],
                              ['F4', 1.0, 2, 2, 1],
                              ['F5', 1.0, 2, 2, 2]]
            faciesInTruncRule = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7']
            overlayFacies = ['F6', 'F7']
            backGroundFacies = [['F1', 'F3', 'F4', 'F2'], ['F5']]
            overlayTruncCenter = [0.3, 0.9]
            faciesProb = [0.2, 0.1, 0.2, 0.2, 0.1, 0.1, 0.1]
            nGaussFields = 4
            run(
                backGroundFacies, fTable, faciesInTruncRule, faciesInZone, faciesOutputFile, faciesProb,
                faciesReferenceFile, gaussFieldFiles, nGaussFields, outPolyFile1, outPolyFile2, outputModelFileName1,
                outputModelFileName2, overlayFacies, overlayTruncCenter, printInfo, truncStructure
            )

        elif testCase == 20:
            fTable = {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5', 6: 'F6'}
            faciesInZone = ['F2', 'F1', 'F4', 'F3', 'F6', 'F5']
            truncStructure = ['V', ['F4', 0.4, 1, 0, 0], ['F2', 1.0, 2, 1, 0], ['F3', 1.0, 2, 2, 1],
                              ['F4', 0.3, 2, 2, 2],
                              ['F4', 0.3, 2, 3, 0]]
            faciesInTruncRule = ['F4', 'F2', 'F3', 'F1', 'F5', 'F6']
            overlayFacies = ['F1', 'F5', 'F6']
            backGroundFacies = [['F2'], ['F3'], ['F4']]
            overlayTruncCenter = [0.3, 0.9, 0.0]
            faciesProb = [0.3, 0.1, 0.2, 0.2, 0.1, 0.1]
            nGaussFields = 5
            run(
                backGroundFacies, fTable, faciesInTruncRule, faciesInZone, faciesOutputFile, faciesProb,
                faciesReferenceFile, gaussFieldFiles, nGaussFields, outPolyFile1, outPolyFile2, outputModelFileName1,
                outputModelFileName2, overlayFacies, overlayTruncCenter, printInfo, truncStructure
            )

        elif testCase == 21:
            fTable = {3: 'F1', 2: 'F3', 1: 'F4'}
            faciesInZone = ['F1', 'F4', 'F3']
            truncStructure = ['V', ['F4', 0.2, 1, 0, 0], ['F4', 0.2, 2, 1, 0], ['F3', 1.0, 2, 2, 1],
                              ['F4', 0.3, 2, 2, 2],
                              ['F4', 0.3, 2, 3, 0]]
            faciesInTruncRule = ['F4', 'F3', 'F1']
            overlayFacies = ['F1']
            backGroundFacies = [['F4']]
            overlayTruncCenter = [0.3]
            faciesProb = [0.3, 0.3, 0.4]
            nGaussFields = 3
            run(
                backGroundFacies, fTable, faciesInTruncRule, faciesInZone, faciesOutputFile, faciesProb,
                faciesReferenceFile, gaussFieldFiles, nGaussFields, outPolyFile1, outPolyFile2, outputModelFileName1,
                outputModelFileName2, overlayFacies, overlayTruncCenter, printInfo, truncStructure
            )

        elif testCase == 22:
            fTable = {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5'}
            faciesInZone = ['F1', 'F4', 'F3', 'F5', 'F2']
            truncStructure = ['H', ['F1', 1.0, 1, 0, 0], ['F2', 1.0, 2, 1, 0], ['F3', 0.5, 2, 2, 1],
                              ['F4', 1.0, 2, 2, 2],
                              ['F3', 0.5, 2, 3, 1], ['F5', 1.0, 2, 3, 2]]
            faciesInTruncRule = ['F1', 'F2', 'F3', 'F4', 'F5']
            overlayFacies = []
            backGroundFacies = []
            overlayTruncCenter = []
            faciesProb = [0.3, 0.1, 0.2, 0.2, 0.2]
            nGaussFields = 2
            run(
                backGroundFacies, fTable, faciesInTruncRule, faciesInZone, faciesOutputFile, faciesProb,
                faciesReferenceFile, gaussFieldFiles, nGaussFields, outPolyFile1, outPolyFile2, outputModelFileName1,
                outputModelFileName2, overlayFacies, overlayTruncCenter, printInfo, truncStructure
            )

        elif testCase == 23:
            fTable = {3: 'F1', 2: 'F3', 1: 'F4', 4: 'F2', 5: 'F5'}
            faciesInZone = ['F1', 'F4', 'F3', 'F5', 'F2']
            truncStructure = ['H', ['F1', 1.0, 1, 0, 0], ['F5', 0.5, 2, 1, 0], ['F3', 0.5, 2, 2, 1],
                              ['F4', 1.0, 2, 2, 2],
                              ['F3', 0.5, 2, 3, 1], ['F5', 0.5, 2, 3, 2]]
            faciesInTruncRule = ['F1', 'F5', 'F3', 'F4', 'F2']
            overlayFacies = ['F2']
            backGroundFacies = [['F5', 'F3']]
            overlayTruncCenter = [0.4]
            faciesProb = [0.3, 0.1, 0.2, 0.2, 0.2]
            nGaussFields = 3
            run(
                backGroundFacies, fTable, faciesInTruncRule, faciesInZone, faciesOutputFile, faciesProb,
                faciesReferenceFile, gaussFieldFiles, nGaussFields, outPolyFile1, outPolyFile2, outputModelFileName1,
                outputModelFileName2, overlayFacies, overlayTruncCenter, printInfo, truncStructure
            )


def run(
        backGroundFacies, fTable, faciesInTruncRule, faciesInZone, faciesOutputFile, faciesProb, faciesReferenceFile,
        gaussFieldFiles, nGaussFields, outPolyFile1, outPolyFile2, outputModelFileName1, outputModelFileName2,
        overlayFacies, overlayTruncCenter, printInfo, truncStructure
):
    [truncRule, truncRule2] = initialize_write_read(
        outputModelFileName1, outputModelFileName2, fTable, faciesInZone, truncStructure,
        backGroundFacies, overlayFacies, overlayTruncCenter, printInfo
    )
    getClassName(truncRule)
    getFaciesInTruncRule(truncRule, truncRule2, faciesInTruncRule)
    truncMapPolygons(truncRule, truncRule2, faciesProb, outPolyFile1, outPolyFile2)
    apply_truncations(truncRule, faciesReferenceFile, nGaussFields, gaussFieldFiles, faciesOutputFile)


if __name__ == '__main__':
    test_Trunc2DCubicMultiOverlay()
