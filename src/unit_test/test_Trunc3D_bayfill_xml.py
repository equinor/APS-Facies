#!/bin/env python
import filecmp
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element

from src.APSMainFaciesTable import APSMainFaciesTable
from src.Trunc3D_bayfill_xml import Trunc3D_bayfill
from src.unit_test.helpers import apply_truncations, getFaciesInTruncRule, truncMapPolygons, writePolygons
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
    # faciesInZone printInfo are global variables in test script
    truncRuleOut = Trunc3D_bayfill(
        trRule, mainFaciesTable, faciesInZone, nGaussFields, printInfo, modelFileName)
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
        outputModelFileName, fTable, faciesInZone, faciesInTruncRule,
        sf_value, sf_name, ysf, sbhd, useConstTruncParam, printInfo
):
    mainFaciesTable = APSMainFaciesTable()
    mainFaciesTable.initialize(fTable)

    # Create an object and initialize it
    # Global variables in test script: faciesInZone, faciesInTruncRule, sf_value, sf_name, ysf, sbhd, useConstTruncParam
    # printInfo
    truncRuleOut = Trunc3D_bayfill()
    truncRuleOut.initialize(
        mainFaciesTable, faciesInZone, faciesInTruncRule,
        sf_value, sf_name, ysf, sbhd, useConstTruncParam, printInfo
    )

    # Build an xml tree with the data and write it to file
    createXMLTreeAndWriteFile(truncRuleOut, outputModelFileName)
    return truncRuleOut


def initialize_write_read(
        outputModelFileName1, outputModelFileName2, fTable, faciesInZone,
        faciesInTruncRule, sf_value, sf_name, ysf, sbhd, useConstTruncParam, printInfo
):
    file1 = outputModelFileName1
    file2 = outputModelFileName2
    # Create an object for truncation rule and write to file
    # Global variable truncRule
    truncRuleA = createTrunc(
        file1, fTable, faciesInZone, faciesInTruncRule,
        sf_value, sf_name, ysf, sbhd, useConstTruncParam, printInfo
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
        raise ValueError('Error: Files are different')
    else:
        print('Files are equal: OK')
    return [truncRuleA, truncRuleB]


def getClassName(truncRule):
    assert truncRule is not None
    name = truncRule.getClassName()
    assert name == 'Trunc3D_Bayfill'


def truncMapsystemPolygons(truncRule, truncRule2, faciesProb, outPolyFile1, outPolyFile2):
    assert faciesProb is not None
    assert truncRule is not None
    assert truncRule2 is not None
    truncRule.setTruncRule(faciesProb)
    [polygons] = truncRule.truncMapPolygons()
    # Write polygons to file
    # Global variable outPolyFile1
    writePolygons(outPolyFile1, polygons)

    truncRule2.setTruncRule(faciesProb)
    [polygons] = truncRule2.truncMapPolygons()
    # Write polygons to file
    # Global variable outPolyFile2
    writePolygons(outPolyFile2, polygons)

    # Compare the original xml file created in createTrunc and the xml file written by interpretXMLModelFileAndWrite
    check = filecmp.cmp(outPolyFile1, outPolyFile2)
    print('Compare file: ' + outPolyFile1 + ' and file: ' + outPolyFile2)
    assert check is True
    if check is False:
        raise ValueError('Error: Files are different')
    else:
        print('Files are equal: OK')


def test_Trunc3DBayfill():
    outputModelFileName1 = 'test_Trunc_output1.xml'
    outputModelFileName2 = 'test_Trunc_output2.xml'
    outPolyFile1 = 'test_Trunc_polygons1.dat'
    outPolyFile2 = 'test_Trunc_polygons2.dat'
    gaussFieldFiles = ['testData_Bayfill/a1.dat', 'testData_Bayfill/a2.dat', 'testData_Bayfill/a3.dat']

    nGaussFields = 3
    printInfo = 0
    nCase = 5
    start = 1
    end = 5
    for testCase in range(start, end + 1):
        print('Case number: ' + str(testCase))
        faciesReferenceFile = 'testData_Bayfill/test_case_' + str(testCase) + '.dat'
        #    faciesOutputFile    = 'testData_Bayfill/test_case_' + str(testCase) + '.dat'
        faciesOutputFile = 'facies2D.dat'

        if testCase == 1:
            fTable = {1: 'F1', 2: 'F2', 3: 'F3', 4: 'F4', 5: 'F5'}
            faciesInZone = ['F3', 'F2', 'F1', 'F4', 'F5']
            faciesInTruncRule = ['F1', 'F2', 'F3', 'F4', 'F5']
            faciesProb = [0.2, 0.2, 0.2, 0.2, 0.2]
            sf_value = 0.0
            sf_name = ''
            ysf = 0.0
            sbhd = 0.0
            useConstTruncParam = True
            run(
                fTable, faciesInTruncRule, faciesInZone, faciesOutputFile, faciesProb, faciesReferenceFile,
                gaussFieldFiles, nGaussFields, outPolyFile1, outPolyFile2, outputModelFileName1, outputModelFileName2,
                printInfo, sbhd, sf_name, sf_value, useConstTruncParam, ysf
            )

        elif testCase == 2:
            fTable = {1: 'F1', 2: 'F2', 3: 'F3', 4: 'F4', 5: 'F5'}
            faciesInZone = ['F2', 'F5', 'F4', 'F1', 'F3']
            faciesInTruncRule = ['F1', 'F2', 'F3', 'F4', 'F5']
            faciesProb = [0.01, 0.19, 0.4, 0.2, 0.2]
            sf_value = 0.5
            sf_name = ''
            ysf = 0.0
            sbhd = 0.0
            useConstTruncParam = True
            run(
                fTable, faciesInTruncRule, faciesInZone, faciesOutputFile, faciesProb, faciesReferenceFile,
                gaussFieldFiles, nGaussFields, outPolyFile1, outPolyFile2, outputModelFileName1, outputModelFileName2,
                printInfo, sbhd, sf_name, sf_value, useConstTruncParam, ysf
            )

        elif testCase == 3:
            fTable = {1: 'F2', 2: 'F1', 3: 'F3', 4: 'F5', 5: 'F4'}
            faciesInZone = ['F3', 'F2', 'F1', 'F4', 'F5']
            faciesInTruncRule = ['F1', 'F2', 'F3', 'F4', 'F5']
            faciesProb = [0.8, 0.02, 0.0, 0.08, 0.1]
            sf_value = 1.0
            sf_name = ''
            ysf = 0.0
            sbhd = 0.0
            useConstTruncParam = True
            run(
                fTable, faciesInTruncRule, faciesInZone, faciesOutputFile, faciesProb, faciesReferenceFile,
                gaussFieldFiles, nGaussFields, outPolyFile1, outPolyFile2, outputModelFileName1, outputModelFileName2,
                printInfo, sbhd, sf_name, sf_value, useConstTruncParam, ysf
            )

        elif testCase == 4:
            fTable = {1: 'F2', 2: 'F1', 3: 'F3', 4: 'F5', 5: 'F4'}
            faciesInZone = ['F3', 'F2', 'F1', 'F4', 'F5']
            faciesInTruncRule = ['F1', 'F2', 'F3', 'F4', 'F5']
            faciesProb = [0.1, 0.8, 0.05, 0.05, 0.0]
            sf_value = 1.0
            sf_name = ''
            ysf = 1.0
            sbhd = 0.0
            useConstTruncParam = True
            run(
                fTable, faciesInTruncRule, faciesInZone, faciesOutputFile, faciesProb, faciesReferenceFile,
                gaussFieldFiles, nGaussFields, outPolyFile1, outPolyFile2, outputModelFileName1, outputModelFileName2,
                printInfo, sbhd, sf_name, sf_value, useConstTruncParam, ysf
            )

        elif testCase == 5:
            fTable = {1: 'F2', 2: 'F1', 3: 'F3', 4: 'F5', 5: 'F4'}
            faciesInZone = ['F3', 'F2', 'F1', 'F4', 'F5']
            faciesInTruncRule = ['F1', 'F2', 'F3', 'F4', 'F5']
            faciesProb = [0.1, 0.1, 0.15, 0.75, 0.0]
            sf_value = 0.1
            sf_name = ''
            ysf = 1.0
            sbhd = 1.0
            useConstTruncParam = True
            run(
                fTable, faciesInTruncRule, faciesInZone, faciesOutputFile, faciesProb, faciesReferenceFile,
                gaussFieldFiles, nGaussFields, outPolyFile1, outPolyFile2, outputModelFileName1, outputModelFileName2,
                printInfo, sbhd, sf_name, sf_value, useConstTruncParam, ysf
            )


def run(fTable, faciesInTruncRule, faciesInZone, faciesOutputFile, faciesProb, faciesReferenceFile, gaussFieldFiles,
        nGaussFields, outPolyFile1, outPolyFile2, outputModelFileName1, outputModelFileName2, printInfo, sbhd, sf_name,
        sf_value, useConstTruncParam, ysf):
    [truncRule, truncRule2] = initialize_write_read(
        outputModelFileName1, outputModelFileName2, fTable, faciesInZone,
        faciesInTruncRule, sf_value, sf_name, ysf, sbhd, useConstTruncParam, printInfo
    )
    getClassName(truncRule)
    getFaciesInTruncRule(truncRule, truncRule2, faciesInTruncRule)
    truncMapPolygons(truncRule, truncRule2, faciesProb, outPolyFile1, outPolyFile2)
    apply_truncations(
        truncRule, faciesReferenceFile, nGaussFields, gaussFieldFiles, faciesOutputFile, printInfo
    )


if __name__ == '__main__':
    test_Trunc3DBayfill()
