# -*- coding: utf-8 -*-
from genericpath import exists
from typing import List, Union, Callable, Any

from PIL import ImageChops, Image

import numpy as np
import os

from aps.utils.checks import compare
from aps.utils.constants.simple import Debug
from aps.utils.io import writeFile, readFile
from aps.algorithms.truncation_rules.types import TruncationRule


def getFaciesInTruncRule(
        truncRule: TruncationRule,
        truncRule2: TruncationRule,
        faciesInTruncRule: List[str]
) -> None:
    # Global variable truncRule
    assert truncRule is not None
    facies_list = truncRule.getFaciesInTruncRule()
    assert len(facies_list) == len(faciesInTruncRule)
    for i in range(len(facies_list)):
        fName = facies_list[i]
        assert fName == faciesInTruncRule[i]

    assert truncRule2 is not None
    facies_list = truncRule2.getFaciesInTruncRule()
    assert len(facies_list) == len(faciesInTruncRule)
    for i in range(len(facies_list)):
        fName = facies_list[i]
        assert fName == faciesInTruncRule[i]


def apply_truncations(
        truncRule: TruncationRule,
        faciesReferenceFile: str,
        nGaussFields: int,
        gaussFieldFiles: List[str],
        faciesOutputFile: str,
        debug_level: Debug = Debug.OFF
) -> None:
    assert truncRule is not None
    assert faciesReferenceFile != ''
    nGaussFieldsInModel = truncRule.getNGaussFieldsInModel()
    if debug_level >= Debug.SOMEWHAT_VERBOSE:
        print('nGaussFieldsInModel: ' + str(nGaussFieldsInModel))
        print('nGaussFields: ' + str(nGaussFields))
    assert nGaussFieldsInModel == nGaussFields
    alphaFields = []
    fileName = gaussFieldFiles[0]
    a, nx, ny = readFile(fileName)
    nValues = len(a)
    for n in range(nGaussFields):
        fileName = gaussFieldFiles[n]
        a, nx, ny = readFile(fileName)
        alphaFields.append(a)
        assert nValues == len(alphaFields[n])
    if debug_level >= Debug.SOMEWHAT_VERBOSE:
        print('nValues: ' + str(nValues))
        print('nx,ny,nx*ny: ' + str(nx) + ' ' + str(ny) + ' ' + str(nx * ny))
    alphaCoord = {}
    faciesReal = []
    # Loop through the Gaussian field array in c-index ordering
    for i in range(nValues):
        for n in range(nGaussFields):
            alpha = alphaFields[n]
            alphaCoord[truncRule._alphaIndxList[n]] = alpha[i]
        faciesCode, fIndx = truncRule.defineFaciesByTruncRule(alphaCoord)
        faciesReal.append(faciesCode)
    if debug_level >= Debug.SOMEWHAT_VERBOSE:
        print('Number of shifts in alpha values for numerical reasons: ' + str(truncRule.getNCountShiftAlpha()))
    writeFile(faciesOutputFile, faciesReal, nx, ny)

    # Compare the generated facies realization with the reference for this case
    check = compare(faciesOutputFile, faciesReferenceFile)
    print(f'Compare file: {faciesReferenceFile} and file: {faciesOutputFile}')
    if check is False:
        fileName = faciesReferenceFile + '_' + faciesOutputFile + '.tmp'
        os.rename(faciesOutputFile, fileName)
        print('Write file: {}'.format(fileName))
        raise ValueError('Error: Files are different')
    elif debug_level >= Debug.ON:
        print('Files are equal: OK')


def apply_truncations_vectorized(
        truncRule: TruncationRule,
        faciesReferenceFile: str,
        nGaussFields: int,
        gaussFieldFiles: List[str],
        faciesOutputFile: str,
        debug_level: Debug = Debug.OFF
) -> None:
    assert truncRule is not None
    assert faciesReferenceFile != ''
    nGaussFieldsInModel = truncRule.getNGaussFieldsInModel()
    if debug_level >= Debug.SOMEWHAT_VERBOSE:
        print('nGaussFieldsInModel: ' + str(nGaussFieldsInModel))
        print('nGaussFields: ' + str(nGaussFields))
    assert nGaussFieldsInModel == nGaussFields
    alphaFields = []
    fileName = gaussFieldFiles[0]
    a, nx, ny = readFile(fileName)
    nValues = len(a)
    for n in range(nGaussFields):
        fileName = gaussFieldFiles[n]
        a, nx, ny = readFile(fileName)
        alphaFields.append(a)
        assert nValues == len(alphaFields[n])
    if debug_level >= Debug.SOMEWHAT_VERBOSE:
        print('nValues: ' + str(nValues))
        print('nx,ny,nx*ny: ' + str(nx) + ' ' + str(ny) + ' ' + str(nx * ny))
    alphaCoord_vectors = np.zeros((nValues, nGaussFields), np.float32)
    # Loop through the Gaussian field array in c-index ordering
    for n in range(nGaussFields):
        alpha_vector = np.asarray(alphaFields[n])
        alphaCoord_vectors[:, n] = alpha_vector
    faciesCode_vector, fIndx_vector = truncRule.defineFaciesByTruncRule_vectorized(alphaCoord_vectors)

    if debug_level >= Debug.SOMEWHAT_VERBOSE:
        print('Number of shifts in alpha values for numerical reasons: ' + str(truncRule.getNCountShiftAlpha()))
        print('facies realization:')
        print(faciesCode_vector)
        print(len(faciesCode_vector))
    print(faciesOutputFile)
    writeFile(faciesOutputFile, faciesCode_vector, nx, ny)

    # Compare the generated facies realization with the reference for this case
    check = compare(faciesOutputFile, faciesReferenceFile)
    print(f'Compare file: {faciesReferenceFile} and file: {faciesOutputFile}')
    if check is False:
        fileName = f'{faciesReferenceFile}_{faciesOutputFile}.tmp'
        os.rename(faciesOutputFile, fileName)
        print(f'Write file: {fileName}')
        raise ValueError('Error: Files are different')
    elif debug_level >= Debug.ON:
        print('Files are equal: OK')


def truncMapPolygons(
        truncRule: TruncationRule,
        truncRule2: TruncationRule,
        faciesProb: List[float],
        outPolyFile1: str,
        outPolyFile2: str
) -> None:
    assert faciesProb is not None
    assert truncRule is not None
    assert truncRule2 is not None
    faciesProbArray = np.asarray(faciesProb, dtype=np.float32)
    truncRule.setTruncRule(faciesProbArray)
    polygons = truncRule.truncMapPolygons()
    # Write polygons to file
    writePolygons(outPolyFile1, polygons)

    truncRule2.setTruncRule(faciesProbArray)
    polygons = truncRule2.truncMapPolygons()
    # Write polygons to file
    writePolygons(outPolyFile2, polygons)

    # Compare the original xml file created in createTrunc and the xml file written by interpretXMLModelFileAndWrite
    check = compare(outPolyFile1, outPolyFile2)
    print(f'Compare file: {outPolyFile1} and file: {outPolyFile2}')
    assert check is True
    if check is False:
        raise ValueError('Error: Files are different')
    else:
        print('Files are equal: OK')


def writePolygons(fileName: str, polygons: Any, debug_level: Debug = Debug.OFF) -> None:
    if debug_level >= Debug.SOMEWHAT_VERBOSE:
        print(f'Write file: {fileName}')
    with open(fileName, 'w') as file:
        for n in range(len(polygons)):
            poly = polygons[n]
            file.write('Polygon number: ' + str(n) + '\n')
            for j in range(len(poly)):
                pt = poly[j]
                x = int(1000 * pt[0] + 0.5)
                y = int(1000 * pt[1] + 0.5)
                pt[0] = x / 1000.0
                pt[1] = y / 1000.0
                if debug_level >= Debug.SOMEWHAT_VERBOSE:
                    print('x,y: ' + str(pt[0]) + ' ' + str(pt[1]))
                file.write(str(pt))
                file.write('\n')


def get_cubic_facies_reference_file_path(testCase: int) -> str:
    faciesReferenceFile = 'testData_Cubic/test_case_' + str(testCase) + '.dat'
    return faciesReferenceFile


def get_model_file_path(modelFile: str) -> str:
    if not exists(modelFile):
        modelFile = 'aps/unit_test/' + modelFile
    return modelFile


def assert_identical_files(source: str, reference: str) -> None:
    _assert_compare_files(source, reference, compare)


def assert_equal_image_content_files(source: str, reference: str) -> None:
    _assert_compare_files(source, reference, compare_image)


def compare_image(source: Union[str, Image.Image], reference: Union[str, Image.Image]) -> bool:
    if isinstance(source, str):
        source = Image.open(source)
    if isinstance(reference, str):
        reference = Image.open(reference)
    return ImageChops.difference(source, reference).getbbox() is None


def _assert_compare_files(source: str, reference: str, func: Callable[[str, str], bool]) -> None:
    print(f'Compare file: {source} and {reference}')
    check = func(source, reference)
    if check:
        print('Files are equal. OK')
    else:
        print('Files are different. NOT OK')
    assert check is True
