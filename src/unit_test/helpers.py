import filecmp

import numpy as np

from src.utils.methods import writeFile, readFile


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


def apply_truncations(truncRule, faciesReferenceFile, nGaussFields, gaussFieldFiles, faciesOutputFile, printInfo=0):
    assert truncRule is not None
    assert faciesReferenceFile != ''
    nGaussFieldsInModel = truncRule.getNGaussFieldsInModel()
    if printInfo >= 1:
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
    if printInfo >= 0:
        print('nValues: ' + str(nValues))
        print('nx,ny,nx*ny: ' + str(nx) + ' ' + str(ny) + ' ' + str(nx*ny))
    alphaCoord = np.zeros(nGaussFields, np.float32)
    faciesReal = []
    # Loop through the gaussfield array in c-index ordering
    for i in range(nValues):
        for n in range(nGaussFields):
            alpha = alphaFields[n]
            alphaCoord[n] = alpha[i]
        [faciesCode, fIndx] = truncRule.defineFaciesByTruncRule(alphaCoord)
        faciesReal.append(faciesCode)
    if printInfo >= 1:
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


def writePolygons(fileName, polygons, printInfo=0):
    if printInfo >= 1:
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
                if printInfo >= 1:
                    print('x,y: ' + str(pt[0]) + ' ' + str(pt[1]))
                file.write(str(pt))
                file.write('\n')
