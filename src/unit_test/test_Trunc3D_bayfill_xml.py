#!/bin/env python
import filecmp
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element

from src.APSMainFaciesTable import APSMainFaciesTable
from src.Trunc3D_bayfill_xml import Trunc3D_bayfill
from src.unit_test.constants import (
    BAYFILL_GAUSS_FIELD_FILES, FACIES_OUTPUT_FILE, NO_VERBOSE_DEBUG,
    OUTPUT_MODEL_FILE_NAME1, OUTPUT_MODEL_FILE_NAME2, OUT_POLY_FILE1, OUT_POLY_FILE2,
)
from src.unit_test.helpers import apply_truncations, getFaciesInTruncRule, truncMapPolygons, writePolygons
from src.utils.constants import Debug
from src.utils.methods import prettify


def interpretXMLModelFileAndWrite(modelFileName, outputModelFileName, fTable, faciesInZone, debug_level=Debug.OFF):
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
    truncRuleOut = Trunc3D_bayfill(
        trRule, mainFaciesTable, faciesInZone, nGaussFields,
        debug_level, modelFileName
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
        outputModelFileName, fTable, faciesInZone, faciesInTruncRule,
        sf_value, sf_name, ysf, sbhd, useConstTruncParam, debug_level=Debug.OFF
):
    mainFaciesTable = APSMainFaciesTable()
    mainFaciesTable.initialize(fTable)

    # Create an object and initialize it
    # get_debug_level
    truncRuleOut = Trunc3D_bayfill()
    truncRuleOut.initialize(
        mainFaciesTable, faciesInZone, faciesInTruncRule,
        sf_value, sf_name, ysf, sbhd, useConstTruncParam, debug_level
    )

    # Build an xml tree with the data and write it to file
    createXMLTreeAndWriteFile(truncRuleOut, outputModelFileName)
    return truncRuleOut


def initialize_write_read(
        outputModelFileName1, outputModelFileName2, fTable, faciesInZone,
        faciesInTruncRule, sf_value, sf_name, ysf, sbhd, useConstTruncParam, debug_level=Debug.OFF
):
    file1 = outputModelFileName1
    file2 = outputModelFileName2
    # Create an object for truncation rule and write to file
    truncRuleA = createTrunc(
        file1, fTable, faciesInZone, faciesInTruncRule,
        sf_value, sf_name, ysf, sbhd, useConstTruncParam, debug_level
    )
    inputFile = file1

    # Write datastructure:
    # truncRule.writeContentsInDataStructure()
    # Read the previously written file as and XML file and write it out again to a new file
    truncRuleB = interpretXMLModelFileAndWrite(inputFile, file2, fTable, faciesInZone, debug_level)

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
    writePolygons(outPolyFile1, polygons)

    truncRule2.setTruncRule(faciesProb)
    [polygons] = truncRule2.truncMapPolygons()
    # Write polygons to file
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
    nCase = 5
    start = 1
    end = 5
    for testCase in range(start, end + 1):
        print('Case number: ' + str(testCase))

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


def test_case_1():
    fTable = {1: 'F1', 2: 'F2', 3: 'F3', 4: 'F4', 5: 'F5'}
    faciesInZone = ['F3', 'F2', 'F1', 'F4', 'F5']
    faciesInTruncRule = ['F1', 'F2', 'F3', 'F4', 'F5']
    faciesProb = [0.2, 0.2, 0.2, 0.2, 0.2]
    sf_value = 0.0
    sf_name = ''
    ysf = 0.0
    sbhd = 0.0
    nGaussFields = 3
    useConstTruncParam = True
    faciesReferenceFile = get_facies_reference_file_path(1)
    run(
        fTable, faciesInTruncRule, faciesInZone, faciesProb, faciesReferenceFile,
        nGaussFields, sbhd, sf_name, sf_value, useConstTruncParam, ysf
    )


def test_case_2():
    fTable = {1: 'F1', 2: 'F2', 3: 'F3', 4: 'F4', 5: 'F5'}
    faciesInZone = ['F2', 'F5', 'F4', 'F1', 'F3']
    faciesInTruncRule = ['F1', 'F2', 'F3', 'F4', 'F5']
    faciesProb = [0.01, 0.19, 0.4, 0.2, 0.2]
    sf_value = 0.5
    sf_name = ''
    ysf = 0.0
    sbhd = 0.0
    nGaussFields = 3
    useConstTruncParam = True
    faciesReferenceFile = get_facies_reference_file_path(2)
    run(
        fTable, faciesInTruncRule, faciesInZone, faciesProb, faciesReferenceFile,
        nGaussFields, sbhd, sf_name, sf_value, useConstTruncParam, ysf
    )


def test_case_3():
    fTable = {1: 'F2', 2: 'F1', 3: 'F3', 4: 'F5', 5: 'F4'}
    faciesInZone = ['F3', 'F2', 'F1', 'F4', 'F5']
    faciesInTruncRule = ['F1', 'F2', 'F3', 'F4', 'F5']
    faciesProb = [0.8, 0.02, 0.0, 0.08, 0.1]
    sf_value = 1.0
    sf_name = ''
    ysf = 0.0
    sbhd = 0.0
    nGaussFields = 3
    useConstTruncParam = True
    faciesReferenceFile = get_facies_reference_file_path(3)
    run(
        fTable, faciesInTruncRule, faciesInZone, faciesProb, faciesReferenceFile,
        nGaussFields, sbhd, sf_name, sf_value, useConstTruncParam, ysf
    )


def test_case_4():
    fTable = {1: 'F2', 2: 'F1', 3: 'F3', 4: 'F5', 5: 'F4'}
    faciesInZone = ['F3', 'F2', 'F1', 'F4', 'F5']
    faciesInTruncRule = ['F1', 'F2', 'F3', 'F4', 'F5']
    faciesProb = [0.1, 0.8, 0.05, 0.05, 0.0]
    sf_value = 1.0
    sf_name = ''
    ysf = 1.0
    sbhd = 0.0
    nGaussFields = 3
    useConstTruncParam = True
    faciesReferenceFile = get_facies_reference_file_path(4)
    run(
        fTable, faciesInTruncRule, faciesInZone, faciesProb, faciesReferenceFile,
        nGaussFields, sbhd, sf_name, sf_value, useConstTruncParam, ysf
    )


def test_case_5():
    fTable = {1: 'F2', 2: 'F1', 3: 'F3', 4: 'F5', 5: 'F4'}
    faciesInZone = ['F3', 'F2', 'F1', 'F4', 'F5']
    faciesInTruncRule = ['F1', 'F2', 'F3', 'F4', 'F5']
    faciesProb = [0.1, 0.1, 0.15, 0.75, 0.0]
    sf_value = 0.1
    sf_name = ''
    ysf = 1.0
    sbhd = 1.0
    nGaussFields = 3
    useConstTruncParam = True
    faciesReferenceFile = get_facies_reference_file_path(5)
    run(
        fTable, faciesInTruncRule, faciesInZone, faciesProb, faciesReferenceFile,
        nGaussFields, sbhd, sf_name, sf_value, useConstTruncParam, ysf
    )


def get_facies_reference_file_path(testCase):
    faciesReferenceFile = 'testData_Bayfill/test_case_' + str(testCase) + '.dat'
    return faciesReferenceFile


def run(fTable, faciesInTruncRule, faciesInZone, faciesProb, faciesReferenceFile,
        nGaussFields, sbhd, sf_name, sf_value, useConstTruncParam, ysf):
    [truncRule, truncRule2] = initialize_write_read(
        OUTPUT_MODEL_FILE_NAME1, OUTPUT_MODEL_FILE_NAME2, fTable, faciesInZone,
        faciesInTruncRule, sf_value, sf_name, ysf, sbhd, useConstTruncParam, NO_VERBOSE_DEBUG
    )
    getClassName(truncRule)
    getFaciesInTruncRule(truncRule, truncRule2, faciesInTruncRule)
    truncMapPolygons(truncRule, truncRule2, faciesProb, OUT_POLY_FILE1, OUT_POLY_FILE2)
    apply_truncations(
        truncRule, faciesReferenceFile, nGaussFields, BAYFILL_GAUSS_FIELD_FILES, FACIES_OUTPUT_FILE, NO_VERBOSE_DEBUG
    )


if __name__ == '__main__':
    test_Trunc3DBayfill()
