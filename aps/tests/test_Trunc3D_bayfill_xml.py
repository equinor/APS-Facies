#!/bin/env python
# -*- coding: utf-8 -*-
import filecmp
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List

import pytest

from aps.algorithms.APSMainFaciesTable import APSMainFaciesTable
from aps.algorithms.truncation_rules import Trunc3D_bayfill
from aps.tests.constants import (
    NO_VERBOSE_DEBUG,
)
from aps.tests.helpers import (
    apply_truncations,
    apply_truncations_vectorized,
    getFaciesInTruncRule,
    truncMapPolygons,
    writePolygons,
)
from aps.tests.types import FaciesListType, FaciesTableType, GaussianFieldsListType
from aps.utils.constants.simple import Debug
from aps.utils.xmlUtils import prettify


def interpretXMLModelFileAndWrite(
    modelFileName,
    outputModelFileName,
    fTable,
    faciesInZone,
    gaussFieldsInZone,
    debug_level=Debug.OFF,
):
    # Read test model file with truncation rule into xml tree
    ET_Tree = ET.parse(modelFileName)
    root = ET_Tree.getroot()
    # Read TruncationRule keyword
    trRule = root.find('TruncationRule')

    # Get name of truncation rule
    # truncRuleName = trRule.get('name')
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
        debug_level=debug_level,
    )
    # Create and write XML tree
    createXMLTreeAndWriteFile(truncRuleOut, outputModelFileName)

    return truncRuleOut


def createXMLTreeAndWriteFile(truncRuleInput, outputModelFileName):
    # Build an XML tree with top as root
    # from truncation object and write it
    assert truncRuleInput is not None
    top = ET.Element('TEST_TruncationRule')
    fmu_attributes = []
    truncRuleInput.XMLAddElement(top, 1, 1, fmu_attributes)
    rootReformatted = prettify(top)
    print(f'Write file: {outputModelFileName}')
    with open(outputModelFileName, 'w', encoding='utf-8') as file:
        file.write(rootReformatted)


def createTrunc(
    outputModelFileName,
    fTable,
    faciesInZone,
    faciesInTruncRule,
    gaussFieldsInZone,
    gaussFieldsForBGFacies,
    sf_value,
    sf_name,
    sf_fmu_updatable,
    ysf,
    ysf_fmu_updatable,
    sbhd,
    sbhd_fmu_updatable,
    useConstTruncParam,
    debug_level,
):
    mainFaciesTable = APSMainFaciesTable(facies_table=fTable)

    # Create an object and initialize it
    # Global variables in test script: faciesInZone, faciesInTruncRule, sf_value, sf_name, ysf, sbhd, useConstTruncParam
    # debug_level
    truncRuleOut = Trunc3D_bayfill()
    truncRuleOut.initialize(
        mainFaciesTable,
        faciesInZone,
        faciesInTruncRule,
        gaussFieldsInZone,
        gaussFieldsForBGFacies,
        sf_value,
        sf_name,
        sf_fmu_updatable,
        ysf,
        ysf_fmu_updatable,
        sbhd,
        sbhd_fmu_updatable,
        useConstTruncParam,
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
    faciesInTruncRule,
    gaussFieldsInZone,
    gaussFieldsForBGFacies,
    sf_value,
    sf_name,
    sf_fmu_updatable,
    ysf,
    ysf_fmu_updatable,
    sbhd,
    sbhd_fmu_updatable,
    useConstTruncParam,
    debug_level,
):
    file1 = outputModelFileName1
    file2 = outputModelFileName2
    # Create an object for truncation rule and write to file
    # Global variable truncRule
    truncRuleA = createTrunc(
        file1,
        fTable,
        faciesInZone,
        faciesInTruncRule,
        gaussFieldsInZone,
        gaussFieldsForBGFacies,
        sf_value,
        sf_name,
        sf_fmu_updatable,
        ysf,
        ysf_fmu_updatable,
        sbhd,
        sbhd_fmu_updatable,
        useConstTruncParam,
        debug_level,
    )
    inputFile = file1

    # Write datastructure:
    #    truncRule.writeContentsInDataStructure()
    # Read the previously written file as and XML file and write it out again to a new file
    # Global variable truncRule2
    truncRuleB = interpretXMLModelFileAndWrite(
        inputFile, file2, fTable, faciesInZone, gaussFieldsInZone, debug_level
    )

    # Compare the original xml file created in createTrunc and the xml file written by interpretXMLModelFileAndWrite
    check = filecmp.cmp(file1, file2)
    print(f'Compare file: {file1} and file: {file2}')
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


def truncMapsystemPolygons(
    truncRule, truncRule2, faciesProb, outPolyFile1, outPolyFile2
):
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
    print(f'Compare file: {outPolyFile1} and file: {outPolyFile2}')
    assert check is True
    if check is False:
        raise ValueError('Error: Files are different')
    else:
        print('Files are equal: OK')


@pytest.mark.parametrize('kind', ['bayfill'])
@pytest.mark.parametrize(
    [
        'case_number',
        'facies_table',
        'facies_in_zone',
        'facies_in_truncation_rule',
        'facies_probabilities',
        'sf_value',
        'sf_name',
        'sf_fmu_updatable',
        'ysf',
        'ysf_fmu_updatable',
        'sbhd',
        'sbhd_fmu_updatable',
        'gaussian_fields_in_zone',
        'gaussian_fields_for_background_facies',
        'use_constant_truncation_param',
    ],
    [
        (
            1,
            {1: 'F1', 2: 'F2', 3: 'F3', 4: 'F4', 5: 'F5'},
            ['F3', 'F2', 'F1', 'F4', 'F5'],
            ['F1', 'F2', 'F3', 'F4', 'F5'],
            [0.2, 0.2, 0.2, 0.2, 0.2],
            0.0,
            '',
            True,
            0.0,
            True,
            0.0,
            True,
            ['GRF1', 'GRF2', 'GRF3', 'GRF4'],
            ['GRF1', 'GRF2', 'GRF3'],
            True,
        ),
        (
            2,
            {1: 'F1', 2: 'F2', 3: 'F3', 4: 'F4', 5: 'F5'},
            ['F2', 'F5', 'F4', 'F1', 'F3'],
            ['F1', 'F2', 'F3', 'F4', 'F5'],
            [0.01, 0.19, 0.4, 0.2, 0.2],
            0.5,
            '',
            False,
            0.0,
            False,
            0.0,
            False,
            ['GRF1', 'GRF2', 'GRF3', 'GRF4'],
            ['GRF1', 'GRF2', 'GRF3'],
            True,
        ),
        (
            3,
            {1: 'F2', 2: 'F1', 3: 'F3', 4: 'F5', 5: 'F4'},
            ['F3', 'F2', 'F1', 'F4', 'F5'],
            ['F1', 'F2', 'F3', 'F4', 'F5'],
            [0.8, 0.02, 0.0, 0.08, 0.1],
            1.0,
            '',
            True,
            0.0,
            True,
            0.0,
            True,
            ['GRF1', 'GRF2', 'GRF3', 'GRF4'],
            ['GRF1', 'GRF2', 'GRF3'],
            True,
        ),
        (
            4,
            {1: 'F2', 2: 'F1', 3: 'F3', 4: 'F5', 5: 'F4'},
            ['F3', 'F2', 'F1', 'F4', 'F5'],
            ['F1', 'F2', 'F3', 'F4', 'F5'],
            [0.1, 0.8, 0.05, 0.05, 0.0],
            1.0,
            '',
            False,
            1.0,
            False,
            0.0,
            False,
            ['GRF1', 'GRF2', 'GRF3', 'GRF4'],
            ['GRF1', 'GRF2', 'GRF3'],
            True,
        ),
        (
            5,
            {1: 'F2', 2: 'F1', 3: 'F3', 4: 'F5', 5: 'F4'},
            ['F3', 'F2', 'F1', 'F4', 'F5'],
            ['F1', 'F2', 'F3', 'F4', 'F5'],
            [0.1, 0.1, 0.15, 0.75, 0.0],
            0.1,
            '',
            True,
            1.0,
            True,
            1.0,
            True,
            ['GRF1', 'GRF2', 'GRF3', 'GRF4'],
            ['GRF1', 'GRF2', 'GRF3'],
            True,
        ),
    ],
)
def test_bayfill_truncation_rule(
    case_number: int,
    facies_table: FaciesTableType,
    facies_in_zone: FaciesListType,
    facies_in_truncation_rule: FaciesListType,
    facies_probabilities: List[float | str],
    sf_value: float,
    sf_name: str,
    sf_fmu_updatable: bool,
    ysf: float,
    ysf_fmu_updatable: bool,
    sbhd: float,
    sbhd_fmu_updatable: bool,
    gaussian_fields_in_zone: GaussianFieldsListType,
    gaussian_fields_for_background_facies: GaussianFieldsListType,
    use_constant_truncation_param: bool,
    facies_reference_file: Path,
    bayfill_gauss_field_files: List[Path],
    output_model_file_name_1: Path,
    output_model_file_name_2: Path,
    out_poly_file_1: Path,
    out_poly_file_2: Path,
    cubic_gauss_field_files: List[Path],
    facies_output_file_vectorized: Path,
    facies_output_file: Path,
):
    truncRule, truncRule2 = initialize_write_read(
        outputModelFileName1=output_model_file_name_1,
        outputModelFileName2=output_model_file_name_2,
        fTable=facies_table,
        faciesInZone=facies_in_zone,
        faciesInTruncRule=facies_in_truncation_rule,
        gaussFieldsInZone=gaussian_fields_in_zone,
        gaussFieldsForBGFacies=gaussian_fields_for_background_facies,
        sf_value=sf_value,
        sf_name=sf_name,
        sf_fmu_updatable=sf_fmu_updatable,
        ysf=ysf,
        ysf_fmu_updatable=ysf_fmu_updatable,
        sbhd=sbhd,
        sbhd_fmu_updatable=sbhd_fmu_updatable,
        useConstTruncParam=use_constant_truncation_param,
        debug_level=NO_VERBOSE_DEBUG,
    )
    nGaussFields = truncRule.getNGaussFieldsInModel()
    getClassName(truncRule)
    getFaciesInTruncRule(truncRule, truncRule2, facies_in_truncation_rule)
    truncMapPolygons(
        truncRule=truncRule,
        truncRule2=truncRule2,
        faciesProb=facies_probabilities,
        outPolyFile1=out_poly_file_1,
        outPolyFile2=out_poly_file_2,
    )
    apply_truncations(
        truncRule=truncRule,
        faciesReferenceFile=facies_reference_file,
        nGaussFields=nGaussFields,
        gaussFieldFiles=bayfill_gauss_field_files,
        faciesOutputFile=facies_output_file,
        debug_level=NO_VERBOSE_DEBUG,
    )

    apply_truncations_vectorized(
        truncRule=truncRule,
        faciesReferenceFile=facies_reference_file,
        nGaussFields=nGaussFields,
        gaussFieldFiles=bayfill_gauss_field_files,
        faciesOutputFile=facies_output_file_vectorized,
        debug_level=NO_VERBOSE_DEBUG,
    )


if __name__ == '__main__':
    pytest.main([__file__])
