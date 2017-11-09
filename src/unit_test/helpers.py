import filecmp

import numpy as np

from src.utils.constants.simple import Debug
from src.utils.io import writeFile, readFile


def getFaciesInTruncRule(truncRule, truncRule2, faciesInTruncRule):
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
        truncRule, faciesReferenceFile, nGaussFields, gaussFieldFiles, faciesOutputFile, debug_level=Debug.OFF
):
    assert truncRule is not None
    assert faciesReferenceFile != ''
    nGaussFieldsInModel = truncRule.getNGaussFieldsInModel()
    if debug_level >= Debug.SOMEWHAT_VERBOSE:
        print('nGaussFieldsInModel: ' + str(nGaussFieldsInModel))
        print('nGaussFields: ' + str(nGaussFields))
    assert nGaussFieldsInModel == nGaussFields
    alphaFields = []
    fileName = gaussFieldFiles[0]
    [a, nx, ny] = readFile(fileName)
    nValues = len(a)
    for n in range(nGaussFields):
        fileName = gaussFieldFiles[n]
        [a, nx, ny] = readFile(fileName)
        alphaFields.append(a)
        assert nValues == len(alphaFields[n])
    if debug_level >= Debug.SOMEWHAT_VERBOSE:
        print('nValues: ' + str(nValues))
        print('nx,ny,nx*ny: ' + str(nx) + ' ' + str(ny) + ' ' + str(nx * ny))
    alphaCoord = np.zeros(nGaussFields, np.float32)
    faciesReal = []
    # Loop through the gaussfield array in c-index ordering
    for i in range(nValues):
        for n in range(nGaussFields):
            alpha = alphaFields[n]
            alphaCoord[n] = alpha[i]
        [faciesCode, fIndx] = truncRule.defineFaciesByTruncRule(alphaCoord)
        faciesReal.append(faciesCode)
    if debug_level >= Debug.SOMEWHAT_VERBOSE:
        print('Number of shifts in alpha values for numerical reasons: ' + str(truncRule.getNCountShiftAlpha()))
    writeFile(faciesOutputFile, faciesReal, nx, ny)

    # Compare the generated facies realization with the reference for this case
    check = filecmp.cmp(faciesReferenceFile, faciesOutputFile)
    print('Compare file: ' + faciesReferenceFile + ' and file: ' + faciesOutputFile)
    assert check is True
    if check is False:
        raise ValueError('Error: Files are different')
    else:
        print('Files are equal: OK')


def truncMapPolygons(truncRule, truncRule2, faciesProb, outPolyFile1, outPolyFile2):
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


def writePolygons(fileName, polygons, debug_level=Debug.OFF):
    if debug_level >= Debug.SOMEWHAT_VERBOSE:
        print('Write file: ' + fileName)
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


def get_cubic_facies_reference_file_path(testCase):
    faciesReferenceFile = 'testData_Cubic/test_case_' + str(testCase) + '.dat'
    return faciesReferenceFile
