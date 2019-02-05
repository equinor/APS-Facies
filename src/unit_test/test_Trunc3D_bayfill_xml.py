#!/bin/env python
# -*- coding: utf-8 -*-
import filecmp
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element

from src.algorithms.APSMainFaciesTable import APSMainFaciesTable
from src.algorithms.Trunc3D_bayfill_xml import Trunc3D_bayfill
from src.unit_test.constants import (
    BAYFILL_GAUSS_FIELD_FILES, FACIES_OUTPUT_FILE, NO_VERBOSE_DEBUG,
    OUTPUT_MODEL_FILE_NAME1, OUTPUT_MODEL_FILE_NAME2, OUT_POLY_FILE1, OUT_POLY_FILE2, FACIES_OUTPUT_FILE_VECTORIZED
)
from src.unit_test.helpers import (
    apply_truncations,  apply_truncations_vectorized, 
    getFaciesInTruncRule, truncMapPolygons, writePolygons,
)
from src.utils.constants.simple import Debug
from src.utils.xmlUtils import prettify


def interpretXMLModelFileAndWrite(
        modelFileName, outputModelFileName, fTable, faciesInZone, gaussFieldsInZone, debug_level=Debug.OFF
):
    # Read test model file with truncation rule into xml tree
    ET_Tree = ET.parse(modelFileName)
    root = ET_Tree.getroot()
    # Read TruncationRule keyword
    trRule = root.find('TruncationRule')

    # Get name of truncation rule
    #truncRuleName = trRule.get('name')
    truncRuleName = trRule[0].tag
    print('Truncation rule: ' + truncRuleName)

    # Get number of required Gauss fields
    nGaussFields = int(trRule[0].get('nGFields'))
    print('Number of gauss fields required for truncation rule: ' + str(nGaussFields))

    mainFaciesTable = APSMainFaciesTable(facies_table=fTable)

    # Create truncation rule object from input data, not read from file
    # faciesInZone debug_level are global variables in test script
    truncRuleOut = Trunc3D_bayfill(
        trRuleXML=trRule,
        mainFaciesTable=mainFaciesTable,
        faciesInZone=faciesInZone,
        gaussFieldsInZone=gaussFieldsInZone,
        modelFileName=modelFileName,
        debug_level=debug_level
    )
    # Create and write XML tree
    createXMLTreeAndWriteFile(truncRuleOut, outputModelFileName)

    return truncRuleOut


def createXMLTreeAndWriteFile(truncRuleInput, outputModelFileName):
    # Build an XML tree with top as root
    # from truncation object and write it
    assert truncRuleInput is not None
    top = Element('TEST_TruncationRule')
    fmu_attributes = []
    truncRuleInput.XMLAddElement(top, 1, 1, fmu_attributes)
    rootReformatted = prettify(top)
    print('Write file: ' + outputModelFileName)
    with open(outputModelFileName, 'w') as file:
        file.write(rootReformatted)


def createTrunc(
        outputModelFileName, fTable, faciesInZone, faciesInTruncRule,
        gaussFieldsInZone, gaussFieldsForBGFacies,
        sf_value, sf_name, sf_fmu_updatable, ysf, ysf_fmu_updatable, sbhd, sbhd_fmu_updatable, useConstTruncParam, debug_level
):
    mainFaciesTable = APSMainFaciesTable(facies_table=fTable)

    # Create an object and initialize it
    # Global variables in test script: faciesInZone, faciesInTruncRule, sf_value, sf_name, ysf, sbhd, useConstTruncParam
    # debug_level
    truncRuleOut = Trunc3D_bayfill()
    truncRuleOut.initialize(
        mainFaciesTable, faciesInZone, faciesInTruncRule,
        gaussFieldsInZone, gaussFieldsForBGFacies,
        sf_value, sf_name, sf_fmu_updatable, ysf, ysf_fmu_updatable, sbhd, sbhd_fmu_updatable, useConstTruncParam, debug_level
    )

    # Build an xml tree with the data and write it to file
    createXMLTreeAndWriteFile(truncRuleOut, outputModelFileName)
    return truncRuleOut


def initialize_write_read(
        outputModelFileName1, outputModelFileName2, fTable, faciesInZone,
        faciesInTruncRule, gaussFieldsInZone, gaussFieldsForBGFacies,
        sf_value, sf_name, sf_fmu_updatable, ysf, ysf_fmu_updatable, sbhd, sbhd_fmu_updatable, useConstTruncParam, debug_level
):
    file1 = outputModelFileName1
    file2 = outputModelFileName2
    # Create an object for truncation rule and write to file
    # Global variable truncRule
    truncRuleA = createTrunc(
        file1, fTable, faciesInZone, faciesInTruncRule, gaussFieldsInZone, gaussFieldsForBGFacies,
        sf_value, sf_name, sf_fmu_updatable, ysf, ysf_fmu_updatable, sbhd, sbhd_fmu_updatable, useConstTruncParam, debug_level
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
    if check is False:
        raise ValueError('Error: Files are different')
    else:
        print('Files are equal: OK')
    return truncRuleA, truncRuleB


def getClassName(truncRule):
    assert truncRule is not None
    name = truncRule.getClassName()
    assert name == 'Trunc3D_bayfill'


def truncMapsystemPolygons(truncRule, truncRule2, faciesProb, outPolyFile1, outPolyFile2):
    assert faciesProb is not None
    assert truncRule is not None
    assert truncRule2 is not None
    truncRule.setTruncRule(faciesProb)
    polygons = truncRule.truncMapPolygons()
    # Write polygons to file
    writePolygons(outPolyFile1, polygons)

    truncRule2.setTruncRule(faciesProb)
    polygons = truncRule2.truncMapPolygons()
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
    run(
        fTable={1: 'F1', 2: 'F2', 3: 'F3', 4: 'F4', 5: 'F5'},
        faciesInZone=['F3', 'F2', 'F1', 'F4', 'F5'],
        faciesInTruncRule=['F1', 'F2', 'F3', 'F4', 'F5'],
        faciesProb=[0.2, 0.2, 0.2, 0.2, 0.2],
        sf_value=0.0,
        sf_name='',
        sf_fmu_updatable=True,
        ysf=0.0,
        ysf_fmu_updatable=True,
        sbhd=0.0,
        sbhd_fmu_updatable=True,
        gaussFieldsInZone=['GRF1', 'GRF2', 'GRF3', 'GRF4'],
        gaussFieldsForBGFacies=['GRF1', 'GRF2', 'GRF3'],
        useConstTruncParam=True,
        faciesReferenceFile=get_facies_reference_file_path(1),
    )


def test_case_2():
    run(
        fTable={1: 'F1', 2: 'F2', 3: 'F3', 4: 'F4', 5: 'F5'},
        faciesInZone=['F2', 'F5', 'F4', 'F1', 'F3'],
        faciesInTruncRule=['F1', 'F2', 'F3', 'F4', 'F5'],
        faciesProb=[0.01, 0.19, 0.4, 0.2, 0.2],
        sf_value=0.5,
        sf_name='',
        sf_fmu_updatable=False,
        ysf=0.0,
        ysf_fmu_updatable=False,
        sbhd=0.0,
        sbhd_fmu_updatable=False,
        gaussFieldsInZone=['GRF1', 'GRF2', 'GRF3', 'GRF4'],
        gaussFieldsForBGFacies=['GRF1', 'GRF2', 'GRF3'],
        useConstTruncParam=True,
        faciesReferenceFile=get_facies_reference_file_path(2),
    )


def test_case_3():
    run(
        fTable={1: 'F2', 2: 'F1', 3: 'F3', 4: 'F5', 5: 'F4'},
        faciesInZone=['F3', 'F2', 'F1', 'F4', 'F5'],
        faciesInTruncRule=['F1', 'F2', 'F3', 'F4', 'F5'],
        faciesProb=[0.8, 0.02, 0.0, 0.08, 0.1],
        sf_value=1.0,
        sf_name='',
        sf_fmu_updatable=True,
        ysf=0.0,
        ysf_fmu_updatable=True,
        sbhd=0.0,
        sbhd_fmu_updatable=True,
        gaussFieldsInZone=['GRF1', 'GRF2', 'GRF3', 'GRF4'],
        gaussFieldsForBGFacies=['GRF1', 'GRF2', 'GRF3'],
        useConstTruncParam=True,
        faciesReferenceFile=get_facies_reference_file_path(3),
    )


def test_case_4():
    run(
        fTable={1: 'F2', 2: 'F1', 3: 'F3', 4: 'F5', 5: 'F4'},
        faciesInZone=['F3', 'F2', 'F1', 'F4', 'F5'],
        faciesInTruncRule=['F1', 'F2', 'F3', 'F4', 'F5'],
        faciesProb=[0.1, 0.8, 0.05, 0.05, 0.0],
        sf_value=1.0,
        sf_name='',
        sf_fmu_updatable=False,
        ysf=1.0,
        ysf_fmu_updatable=False,
        sbhd=0.0,
        sbhd_fmu_updatable=False,
        gaussFieldsInZone=['GRF1', 'GRF2', 'GRF3', 'GRF4'],
        gaussFieldsForBGFacies=['GRF1', 'GRF2', 'GRF3'],
        useConstTruncParam=True,
        faciesReferenceFile=get_facies_reference_file_path(4),
    )


def test_case_5():
    run(
        fTable={1: 'F2', 2: 'F1', 3: 'F3', 4: 'F5', 5: 'F4'},
        faciesInZone=['F3', 'F2', 'F1', 'F4', 'F5'],
        faciesInTruncRule=['F1', 'F2', 'F3', 'F4', 'F5'],
        faciesProb=[0.1, 0.1, 0.15, 0.75, 0.0],
        sf_value=0.1,
        sf_name='',
        sf_fmu_updatable = True,
        ysf=1.0,
        ysf_fmu_updatable=True,
        sbhd=1.0,
        sbhd_fmu_updatable=True,
        gaussFieldsInZone=['GRF1', 'GRF2', 'GRF3', 'GRF4'],
        gaussFieldsForBGFacies=['GRF1', 'GRF2', 'GRF3'],
        useConstTruncParam=True,
        faciesReferenceFile=get_facies_reference_file_path(5),
    )


def get_facies_reference_file_path(testCase):
    faciesReferenceFile = 'testData_Bayfill/test_case_' + str(testCase) + '.dat'
    return faciesReferenceFile


def run(
        fTable, faciesInTruncRule, faciesInZone, faciesProb, faciesReferenceFile,
        gaussFieldsInZone, gaussFieldsForBGFacies, sbhd, sbhd_fmu_updatable, sf_name, sf_value, sf_fmu_updatable, useConstTruncParam, ysf, ysf_fmu_updatable
):
    truncRule, truncRule2 = initialize_write_read(
        outputModelFileName1=OUTPUT_MODEL_FILE_NAME1,
        outputModelFileName2=OUTPUT_MODEL_FILE_NAME2,
        fTable=fTable,
        faciesInZone=faciesInZone,
        faciesInTruncRule=faciesInTruncRule,
        gaussFieldsInZone=gaussFieldsInZone,
        gaussFieldsForBGFacies=gaussFieldsForBGFacies,
        sf_value=sf_value,
        sf_name=sf_name,
        sf_fmu_updatable=sf_fmu_updatable,
        ysf=ysf,
        ysf_fmu_updatable=ysf_fmu_updatable,
        sbhd=sbhd,
        sbhd_fmu_updatable=sbhd_fmu_updatable,
        useConstTruncParam=useConstTruncParam,
        debug_level=NO_VERBOSE_DEBUG
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
        gaussFieldFiles=BAYFILL_GAUSS_FIELD_FILES,
        faciesOutputFile=FACIES_OUTPUT_FILE,
        debug_level=NO_VERBOSE_DEBUG
    )

    apply_truncations_vectorized(
        truncRule=truncRule,
        faciesReferenceFile=faciesReferenceFile,
        nGaussFields=nGaussFields,
        gaussFieldFiles=BAYFILL_GAUSS_FIELD_FILES,
        faciesOutputFile=FACIES_OUTPUT_FILE_VECTORIZED,
        debug_level=NO_VERBOSE_DEBUG
    )


if __name__ == '__main__':
    test_Trunc3DBayfill()
