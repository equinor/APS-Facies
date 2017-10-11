#!/bin/env python
import filecmp
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element

from src.APSMainFaciesTable import APSMainFaciesTable
from src.Trunc2D_Angle_xml import Trunc2D_Angle
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
    #    print('Number of gauss fields required for truncation rule: ' + str(nGaussFields))

    mainFaciesTable = APSMainFaciesTable()
    mainFaciesTable.initialize(fTable)

    # Create truncation rule object from input data, not read from file
    truncRuleOut = Trunc2D_Angle(
        trRule, mainFaciesTable, faciesInZone, nGaussFields, printInfo, modelFileName
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
        outputModelFileName, fTable, faciesInZone, truncStructure, backGroundFacies,
        overlayFacies, overlayTruncCenter, useConstTruncParam, printInfo
):
    mainFaciesTable = APSMainFaciesTable()
    mainFaciesTable.initialize(fTable)

    # Create an object and initialize it
    truncRuleOut = Trunc2D_Angle()
    truncRuleOut.initialize(
        mainFaciesTable, faciesInZone, truncStructure, backGroundFacies,
        overlayFacies, overlayTruncCenter, useConstTruncParam, printInfo
    )

    #    truncRuleOut.initialize(mainFaciesTable,faciesInZone,truncStructure,
    #                            backGroundFacies,overlayFacies,overlayTruncCenter,printInfo)

    # Build an xml tree with the data and write it to file
    createXMLTreeAndWriteFile(truncRuleOut, outputModelFileName)
    return truncRuleOut


def initialize_write_read(
        outputModelFileName1, outputModelFileName2, fTable, faciesInZone,
        truncStructure, backGroundFacies, overlayFacies, overlayTruncCenter,
        useConstTruncParam, printInfo
):
    file1 = outputModelFileName1
    file2 = outputModelFileName2
    # Create an object for truncation rule and write to file
    # Global variable truncRule
    truncRuleA = createTrunc(
        file1, fTable, faciesInZone, truncStructure, backGroundFacies,
        overlayFacies, overlayTruncCenter, useConstTruncParam, printInfo
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
    # TODO: Define these as external constants
    outputModelFileName1 = 'test_Trunc_output1.xml'
    outputModelFileName2 = 'test_Trunc_output2.xml'
    outPolyFile1 = 'test_Trunc_polygons1.dat'
    outPolyFile2 = 'test_Trunc_polygons2.dat'
    gaussFieldFiles = [
        'testData_Angle/a1.dat', 'testData_Angle/a2.dat', 'testData_Angle/a3.dat', 'testData_Angle/a4.dat',
        'testData_Angle/a5.dat', 'testData_Angle/a6.dat'
    ]

    nGaussFields = 3
    printInfo = 0
    useConstTruncParam = 1
    nCase = 7
    start = 1
    end = 7
    for testCase in range(start, end + 1):
        print('Case number: ' + str(testCase))
        faciesReferenceFile = 'testData_Angle/test_case_' + str(testCase) + '.dat'
        #    faciesOutputFile  = 'testData_Angle/test_case_' + str(testCase) + '.dat'
        faciesOutputFile = 'facies2D.dat'
        if testCase == 1:
            fTable = {2: 'F2', 1: 'F1', 3: 'F3'}
            faciesInZone = ['F1', 'F2', 'F3']
            truncStructure = [['F3', -90.0, 1.0], ['F2', +45.0, 1.0], ['F1', +45.0, 1.0]]
            faciesInTruncRule = ['F3', 'F2', 'F1']
            overlayFacies = []
            backGroundFacies = []
            overlayTruncCenter = []
            faciesProb = [0.5, 0.3, 0.2]
            nGaussFields = 2
            run(
                backGroundFacies, fTable, faciesInTruncRule, faciesInZone, faciesOutputFile, faciesProb,
                faciesReferenceFile, gaussFieldFiles, nGaussFields, outPolyFile1, outPolyFile2, outputModelFileName1,
                outputModelFileName2, overlayFacies, overlayTruncCenter, printInfo, truncStructure, useConstTruncParam
            )

        elif testCase == 2:
            fTable = {2: 'F2', 1: 'F1', 3: 'F3'}
            faciesInZone = ['F2', 'F3', 'F1']
            truncStructure = [['F1', +135.0, 1.0], ['F2', +45.0, 1.0], ['F3', +45.0, 1.0]]
            faciesInTruncRule = ['F1', 'F2', 'F3']
            overlayFacies = []
            backGroundFacies = []
            overlayTruncCenter = []
            faciesProb = [0.01, 0.8, 0.19]
            nGaussFields = 2
            run(
                backGroundFacies, fTable, faciesInTruncRule, faciesInZone, faciesOutputFile, faciesProb,
                faciesReferenceFile, gaussFieldFiles, nGaussFields, outPolyFile1, outPolyFile2, outputModelFileName1,
                outputModelFileName2, overlayFacies, overlayTruncCenter, printInfo, truncStructure, useConstTruncParam
            )

        elif testCase == 3:
            fTable = {1: 'F1', 2: 'F2', 3: 'F3', 4: 'F4', 5: 'F5'}
            faciesInZone = ['F2', 'F3', 'F1', 'F5', 'F4']
            truncStructure = [['F1', +135.0, 1.0], ['F2', +45.0, 1.0], ['F3', +45.0, 1.0]]
            faciesInTruncRule = ['F1', 'F2', 'F3', 'F5', 'F4']
            overlayFacies = ['F5', 'F4']
            backGroundFacies = [['F1'], ['F3']]
            overlayTruncCenter = [0.9, 0.0]
            faciesProb = [0.3, 0.2, 0.3, 0.1, 0.1]
            nGaussFields = 4
            run(
                backGroundFacies, fTable, faciesInTruncRule, faciesInZone, faciesOutputFile, faciesProb,
                faciesReferenceFile, gaussFieldFiles, nGaussFields, outPolyFile1, outPolyFile2, outputModelFileName1,
                outputModelFileName2, overlayFacies, overlayTruncCenter, printInfo, truncStructure, useConstTruncParam
            )

        elif testCase == 4:
            fTable = {1: 'F1', 2: 'F2', 3: 'F3', 4: 'F4', 5: 'F5'}
            faciesInZone = ['F2', 'F3', 'F1', 'F5', 'F4']
            truncStructure = [['F1', -135.0, 1.0], ['F3', +90.0, 1.0], ['F2', +45.0, 1.0]]
            faciesInTruncRule = ['F1', 'F3', 'F2', 'F5', 'F4']
            overlayFacies = ['F5', 'F4']
            backGroundFacies = [['F2', 'F1'], ['F3']]
            overlayTruncCenter = [0.0, 1.0]
            faciesProb = [0.3, 0.2, 0.3, 0.1, 0.1]
            nGaussFields = 4
            run(
                backGroundFacies, fTable, faciesInTruncRule, faciesInZone, faciesOutputFile, faciesProb,
                faciesReferenceFile, gaussFieldFiles, nGaussFields, outPolyFile1, outPolyFile2, outputModelFileName1,
                outputModelFileName2, overlayFacies, overlayTruncCenter, printInfo, truncStructure, useConstTruncParam
            )

        elif testCase == 5:
            fTable = {1: 'F1', 2: 'F2', 3: 'F3', 4: 'F4', 5: 'F5'}
            faciesInZone = ['F2', 'F3', 'F1', 'F5', 'F4']
            truncStructure = [['F1', -180.0, 0.5], ['F3', +180.0, 1.0], ['F1', 0.0, 0.5], ['F2', 35.0, 0.7],
                              ['F2', -35.0, 0.3]]
            faciesInTruncRule = ['F1', 'F3', 'F2', 'F5', 'F4']
            overlayFacies = ['F5', 'F4']
            backGroundFacies = [['F3', 'F2'], ['F1']]
            overlayTruncCenter = [0.0, 0.0]
            faciesProb = [0.2, 0.3, 0.3, 0.1, 0.1]
            nGaussFields = 4
            run(
                backGroundFacies, fTable, faciesInTruncRule, faciesInZone, faciesOutputFile, faciesProb,
                faciesReferenceFile, gaussFieldFiles, nGaussFields, outPolyFile1, outPolyFile2, outputModelFileName1,
                outputModelFileName2, overlayFacies, overlayTruncCenter, printInfo, truncStructure, useConstTruncParam
            )

        elif testCase == 6:
            fTable = {1: 'F1', 2: 'F2', 3: 'F3', 4: 'F4', 5: 'F5'}
            faciesInZone = ['F2', 'F3', 'F1', 'F5', 'F4']
            truncStructure = [['F1', -180.0, 1.0], ['F3', -170.0, 0.5], ['F3', -160.0, 0.5], ['F2', -150.0, 0.7],
                              ['F2', -140.0, 0.3]]
            faciesInTruncRule = ['F1', 'F3', 'F2', 'F5', 'F4']
            overlayFacies = ['F5', 'F4']
            backGroundFacies = [['F3', 'F2'], ['F1']]
            overlayTruncCenter = [0.0, 0.0]
            faciesProb = [0.2, 0.3, 0.3, 0.1, 0.1]
            nGaussFields = 4
            run(
                backGroundFacies, fTable, faciesInTruncRule, faciesInZone, faciesOutputFile, faciesProb,
                faciesReferenceFile, gaussFieldFiles, nGaussFields, outPolyFile1, outPolyFile2, outputModelFileName1,
                outputModelFileName2, overlayFacies, overlayTruncCenter, printInfo, truncStructure, useConstTruncParam
            )

        elif testCase == 7:
            fTable = {1: 'F1', 2: 'F2', 3: 'F3', 4: 'F4', 5: 'F5', 6: 'F6', 7: 'F7', 8: 'F8'}
            faciesInZone = ['F2', 'F3', 'F1', 'F5', 'F4', 'F6', 'F7', 'F8']
            truncStructure = [['F1', -180.0, 0.5], ['F3', -170.0, 0.5], ['F7', 10.0, 1.0], ['F1', -60.0, 0.5],
                              ['F3', -160.0, 0.5], ['F2', -150.0, 0.05], ['F2', +140.0, 0.95], ['F6', 120.0, 1.0]]
            faciesInTruncRule = ['F1', 'F3', 'F7', 'F2', 'F6', 'F5', 'F4', 'F8']
            overlayFacies = ['F5', 'F4', 'F8']
            backGroundFacies = [['F3', 'F2'], ['F1'], ['F7']]
            overlayTruncCenter = [0.0, 0.0, 1.0]
            faciesProb = [0.15, 0.3, 0.2, 0.1, 0.1, 0.05, 0.05, 0.05]
            nGaussFields = 5
            run(
                backGroundFacies, fTable, faciesInTruncRule, faciesInZone, faciesOutputFile, faciesProb,
                faciesReferenceFile, gaussFieldFiles, nGaussFields, outPolyFile1, outPolyFile2, outputModelFileName1,
                outputModelFileName2, overlayFacies, overlayTruncCenter, printInfo, truncStructure, useConstTruncParam
            )

        elif testCase == 8:
            fTable = {1: 'F1', 2: 'F2', 3: 'F3', 4: 'F4', 5: 'F5'}
            faciesInZone = ['F2', 'F3', 'F1', 'F5', 'F4']
            truncStructure = [['F1', -180.0, 1.0], ['F3', -170.0, 0.5], ['F3', -160.0, 0.5], ['F2', -150.0, 0.7],
                              ['F2', -140.0, 0.3]]
            faciesInTruncRule = ['F1', 'F3', 'F2', 'F5', 'F4']
            overlayFacies = ['F5', 'F4']
            backGroundFacies = [['F3', 'F2'], ['F1']]
            overlayTruncCenter = [0.0, 0.0]
            faciesProb = [0.2, 0.3, 0.3, 0.1, 0.1]
            nGaussFields = 4
            run(
                backGroundFacies, fTable, faciesInTruncRule, faciesInZone, faciesOutputFile, faciesProb,
                faciesReferenceFile, gaussFieldFiles, nGaussFields, outPolyFile1, outPolyFile2, outputModelFileName1,
                outputModelFileName2, overlayFacies, overlayTruncCenter, printInfo, truncStructure, useConstTruncParam
            )

        elif testCase == 9:
            fTable = {1: 'F1', 2: 'F2', 3: 'F3', 4: 'F4', 5: 'F5'}
            faciesInZone = ['F2', 'F3', 'F1', 'F5', 'F4']
            truncStructure = [['F1', -180.0, 1.0], ['F3', -170.0, 0.5], ['F3', -160.0, 0.5], ['F2', -150.0, 0.7],
                              ['F2', -140.0, 0.3]]
            faciesInTruncRule = ['F1', 'F3', 'F2', 'F5', 'F4']
            overlayFacies = ['F5', 'F4']
            backGroundFacies = [['F3', 'F2'], ['F1']]
            overlayTruncCenter = [0.0, 0.0]
            faciesProb = [0.2, 0.3, 0.3, 0.1, 0.1]
            nGaussFields = 4
            run(
                backGroundFacies, fTable, faciesInTruncRule, faciesInZone, faciesOutputFile, faciesProb,
                faciesReferenceFile, gaussFieldFiles, nGaussFields, outPolyFile1, outPolyFile2, outputModelFileName1,
                outputModelFileName2, overlayFacies, overlayTruncCenter, printInfo, truncStructure, useConstTruncParam
            )

        elif testCase == 10:
            fTable = {1: 'F1', 2: 'F2', 3: 'F3', 4: 'F4', 5: 'F5'}
            faciesInZone = ['F2', 'F3', 'F1', 'F5', 'F4']
            truncStructure = [['F1', -180.0, 1.0], ['F3', -170.0, 0.5], ['F3', -160.0, 0.5], ['F2', -150.0, 0.7],
                              ['F2', -140.0, 0.3]]
            faciesInTruncRule = ['F1', 'F3', 'F2', 'F5', 'F4']
            overlayFacies = ['F5', 'F4']
            backGroundFacies = [['F3', 'F2'], ['F1']]
            overlayTruncCenter = [0.0, 0.0]
            faciesProb = [0.2, 0.3, 0.3, 0.1, 0.1]
            nGaussFields = 4
            run(
                backGroundFacies, fTable, faciesInTruncRule, faciesInZone, faciesOutputFile, faciesProb,
                faciesReferenceFile, gaussFieldFiles, nGaussFields, outPolyFile1, outPolyFile2, outputModelFileName1,
                outputModelFileName2, overlayFacies, overlayTruncCenter, printInfo, truncStructure, useConstTruncParam
            )

        elif testCase == 11:
            fTable = {1: 'F1', 2: 'F2', 3: 'F3', 4: 'F4', 5: 'F5'}
            faciesInZone = ['F2', 'F3', 'F1', 'F5', 'F4']
            truncStructure = [['F1', -180.0, 1.0], ['F3', -170.0, 0.5], ['F3', -160.0, 0.5], ['F2', -150.0, 0.7],
                              ['F2', -140.0, 0.3]]
            faciesInTruncRule = ['F1', 'F3', 'F2', 'F5', 'F4']
            overlayFacies = ['F5', 'F4']
            backGroundFacies = [['F3', 'F2'], ['F1']]
            overlayTruncCenter = [0.0, 0.0]
            faciesProb = [0.2, 0.3, 0.3, 0.1, 0.1]
            nGaussFields = 4
            run(
                backGroundFacies, fTable, faciesInTruncRule, faciesInZone, faciesOutputFile, faciesProb,
                faciesReferenceFile, gaussFieldFiles, nGaussFields, outPolyFile1, outPolyFile2, outputModelFileName1,
                outputModelFileName2, overlayFacies, overlayTruncCenter, printInfo, truncStructure, useConstTruncParam
            )

        elif testCase == 12:
            fTable = {1: 'F1', 2: 'F2', 3: 'F3', 4: 'F4', 5: 'F5'}
            faciesInZone = ['F2', 'F3', 'F1', 'F5', 'F4']
            truncStructure = [['F1', -180.0, 1.0], ['F3', -170.0, 0.5], ['F3', -160.0, 0.5], ['F2', -150.0, 0.7],
                              ['F2', -140.0, 0.3]]
            faciesInTruncRule = ['F1', 'F3', 'F2', 'F5', 'F4']
            overlayFacies = ['F5', 'F4']
            backGroundFacies = [['F3', 'F2'], ['F1']]
            overlayTruncCenter = [0.0, 0.0]
            faciesProb = [0.2, 0.3, 0.3, 0.1, 0.1]
            nGaussFields = 4
            run(
                backGroundFacies, fTable, faciesInTruncRule, faciesInZone, faciesOutputFile, faciesProb,
                faciesReferenceFile, gaussFieldFiles, nGaussFields, outPolyFile1, outPolyFile2, outputModelFileName1,
                outputModelFileName2, overlayFacies, overlayTruncCenter, printInfo, truncStructure, useConstTruncParam
            )

        elif testCase == 13:
            fTable = {1: 'F1', 2: 'F2', 3: 'F3', 4: 'F4', 5: 'F5'}
            faciesInZone = ['F2', 'F3', 'F1', 'F5', 'F4']
            truncStructure = [['F1', -180.0, 1.0], ['F3', -170.0, 0.5], ['F3', -160.0, 0.5], ['F2', -150.0, 0.7],
                              ['F2', -140.0, 0.3]]
            faciesInTruncRule = ['F1', 'F3', 'F2', 'F5', 'F4']
            overlayFacies = ['F5', 'F4']
            backGroundFacies = [['F3', 'F2'], ['F1']]
            overlayTruncCenter = [0.0, 0.0]
            faciesProb = [0.2, 0.3, 0.3, 0.1, 0.1]
            nGaussFields = 4
            run(
                backGroundFacies, fTable, faciesInTruncRule, faciesInZone, faciesOutputFile, faciesProb,
                faciesReferenceFile, gaussFieldFiles, nGaussFields, outPolyFile1, outPolyFile2, outputModelFileName1,
                outputModelFileName2, overlayFacies, overlayTruncCenter, printInfo, truncStructure, useConstTruncParam
            )


def run(backGroundFacies, fTable, faciesInTruncRule, faciesInZone, faciesOutputFile, faciesProb, faciesReferenceFile,
        gaussFieldFiles, nGaussFields, outPolyFile1, outPolyFile2, outputModelFileName1, outputModelFileName2,
        overlayFacies, overlayTruncCenter, printInfo, truncStructure, useConstTruncParam):
    [truncRule, truncRule2] = initialize_write_read(
        outputModelFileName1, outputModelFileName2, fTable, faciesInZone, truncStructure,
        backGroundFacies, overlayFacies, overlayTruncCenter, useConstTruncParam, printInfo
    )
    getClassName(truncRule)
    getFaciesInTruncRule(truncRule, truncRule2, faciesInTruncRule)
    truncMapPolygons(truncRule, truncRule2, faciesProb, outPolyFile1, outPolyFile2)
    apply_truncations(truncRule, faciesReferenceFile, nGaussFields, gaussFieldFiles, faciesOutputFile)


if __name__ == '__main__':
    test_Trunc2DAngle()
