#!/bin/env python
import sys
import numpy as np
from APSMainFaciesTable import APSMainFaciesTable
from Trunc2D_Angle_xml import Trunc2D_Angle
from Trunc2D_Base_xml import Trunc2D_Base

import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
from xml.dom import minidom
import filecmp
import sys

def prettify(elem):
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ", newl="\n")

def interpretXMLModelFileAndWrite(modelFileName,outputModelFileName):
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
    truncRuleOut =  Trunc2D_Angle(trRule, mainFaciesTable, faciesInZone, nGaussFields,
                                  printInfo,modelFileName)
    # Create and write XML tree 
    createXMLTreeAndWriteFile(truncRuleOut,outputModelFileName)
    
    return truncRuleOut

def createXMLTreeAndWriteFile(truncRuleInput,outputModelFileName):
    # Build an XML tree with top as root
    # from truncation object and write it
    assert truncRuleInput != None
    top = Element('TEST_TruncationRule')
    truncRuleInput.XMLAddElement(top)
    rootReformatted = prettify(top)
    print('Write file: ' + outputModelFileName)
    with open(outputModelFileName, 'w') as file:
        file.write(rootReformatted)

def createTrunc(outputModelFileName):
    mainFaciesTable = APSMainFaciesTable()
    mainFaciesTable.initialize(fTable)

    # Create an object and initialize it
    truncRuleOut =  Trunc2D_Angle()
    truncRuleOut.initialize(mainFaciesTable, faciesInZone, truncStructure,
                            backGroundFacies, overlayFacies, overlayTruncCenter,
                            useConstTruncParam, printInfo)

#    truncRuleOut.initialize(mainFaciesTable,faciesInZone,truncStructure,
#                            backGroundFacies,overlayFacies,overlayTruncCenter,printInfo)

    # Build an xml tree with the data and write it to file
    createXMLTreeAndWriteFile(truncRuleOut,outputModelFileName)
    return truncRuleOut

def test_initialize_write_read():
    file1 = outputModelFileName1
    file2 = outputModelFileName2
    # Create an object for truncation rule and write to file
    # Global variable truncRule
    truncRuleA = createTrunc(file1)
    inputFile = file1

    # Write datastructure:
#    truncRule.writeContentsInDataStructure()
    # Read the previously written file as and XML file and write it out again to a new file
    # Global variable truncRule2
    truncRuleB = interpretXMLModelFileAndWrite(inputFile,file2)

    # Compare the original xml file created in createTrunc and the xml file written by interpretXMLModelFileAndWrite
    check = filecmp.cmp(file1,file2)
    print('Compare file: ' + file1 + ' and file: ' + file2)
    assert check == True
    if check == False:
        print('Error: Files are different')
        sys.exit()
    else:
        print('Files are equal: OK')
    return [truncRuleA,truncRuleB]

def test_getClassName():
    assert truncRule != None
    name = truncRule.getClassName()
    assert name == 'Trunc2D_Angle'

def test_getFaciesInTruncRule():
    # Global variable truncRule
    assert truncRule != None
    list = truncRule.getFaciesInTruncRule()
    assert len(list) == len(faciesInTruncRule)
    for i in range(len(list)):
        fName = list[i]
        assert fName == faciesInTruncRule[i]

    assert truncRule2 != None
    list = truncRule2.getFaciesInTruncRule()
    assert len(list) == len(faciesInTruncRule)
    for i in range(len(list)):
        fName = list[i]
        assert fName == faciesInTruncRule[i]

def test_truncMapPolygons():
    assert faciesProb != None
    assert truncRule != None
    assert truncRule2 != None
    truncRule.setTruncRule(faciesProb)
    [polygons] = truncRule.truncMapPolygons()
    # Write polygons to file
    # Global variable outPolyFile1
    writePolygons(outPolyFile1,polygons)

    truncRule2.setTruncRule(faciesProb)
    [polygons] = truncRule2.truncMapPolygons()
    # Write polygons to file
    # Global variable outPolyFile2
    writePolygons(outPolyFile2,polygons)

    # Compare the original xml file created in createTrunc and the xml file written by interpretXMLModelFileAndWrite
    check = filecmp.cmp(outPolyFile1,outPolyFile2)
    print('Compare file: ' + outPolyFile1 + ' and file: ' + outPolyFile2)
    assert check == True
    if check == False:
        print('Error: Files are different')
        sys.exit()
    else:
        print('Files are equal: OK')

def writePolygons(fileName,polygons):
    print('Write file: ' + fileName)
    with open(fileName, 'w') as file:
        for n in range(len(polygons)):
            poly = polygons[n]
            file.write('Polygon number: ' + str(n) + '\n')
            for j in range(len(poly)):
                pt = poly[j]
                x = int(1000*pt[0] + 0.5)
                y = int(1000*pt[1] + 0.5)
                pt[0] = x/1000.0
                pt[1] = y/1000.0
#                print('x,y: ' + str(pt[0]) + ' '  + str(pt[1]))
                file.write(str(pt))
                file.write('\n')

def test_apply_truncations():
    assert truncRule != None
    assert faciesReferenceFile != ''
    nGaussFieldsInModel = truncRule.getNGaussFieldsInModel()
#    print('nGaussFieldsInModel: ' + str(nGaussFieldsInModel))
#    print('nGaussFields: ' + str(nGaussFields))
    # nGaussFields is a global variable
    assert nGaussFieldsInModel == nGaussFields
    alphaFields = []
    fileName = gaussFieldFiles[0]
    [a,nx,ny] = readFile(fileName)
    nValues = len(a)
    for n in range(nGaussFields):
        fileName = gaussFieldFiles[n]
        [a,nx,ny] = readFile(fileName)
        alphaFields.append(a)
        assert nValues == len(alphaFields[n])
#    print('nValues: ' + str(nValues))
#    print('nx,ny,nx*ny: ' + str(nx) + ' '  + str(ny) + ' ' + str(nx*ny))
    alphaCoord = np.zeros(nGaussFields,np.float32)
    faciesReal = []
    # Loop through the gaussfield array in c-index ordering
    for i in range(nValues):
        for n in range(nGaussFields):    
            alpha = alphaFields[n]
            alphaCoord[n] = alpha[i]
        [faciesCode,fIndx] = truncRule.defineFaciesByTruncRule(alphaCoord)
        faciesReal.append(faciesCode)

    print('Number of shifts in alpha values for numerical reasons: ' + str(truncRule.getNCountShiftAlpha()))
    writeFile(faciesOutputFile,faciesReal,nx,ny)

    # Compare the generated facies realization with the reference for this case
    check = filecmp.cmp(faciesReferenceFile,faciesOutputFile)
    print('Compare file: ' + faciesReferenceFile + ' and file: ' + faciesOutputFile)
    assert check == True
    if check == False:
        print('Error: Files are different')
        sys.exit()
    else:
        print('Files are equal: OK')

def writeFile(fileName,a,nx,ny):
    with open(fileName,'w') as file:
        # Choose an arbitary heading
        outstring = '-996  ' + str(ny) + '  50.000000     50.000000\n'
        outstring = outstring + '637943.187500   678043.187500  4334008.000000  4375108.000000\n'
        outstring = outstring + ' ' + str(nx) + ' ' + ' 0.000000   637943.187500  4334008.000000\n'
        outstring = outstring + '0     0     0     0     0     0     0\n'
        count = 0
        text = ''
#        print('len(a): ' + str(len(a)))
        for j in range(len(a)):
            text = text + str(a[j]) + '  '
            count += 1
            if count>=5:
                text = text + '\n'
                outstring += text
                count = 0
                text = ''
        if count > 0:
            outstring += text +'\n'
        file.write(outstring)
    print('Write file: ' + fileName)
    return

def readFile(fileName):
    print('Read file: ' + fileName)
    with open(fileName,'r') as file:
        inString = file.read()
        words = inString.split()
        n = len(words)
#        print('Number of words: ' + str(n))

        ny = int(words[1])
        nx = int(words[8])
#        print('nx,ny: ' + str(nx) + ' '  + str(ny))
#        print('Number of values: ' + str(len(words)-19))
        a = np.zeros(nx*ny,float)
        for i in range(19,len(words)):
            a[i-19] = float(words[i])

    return [a,nx,ny]



# --------- Main ---------------
outputModelFileName1 = 'test_Trunc_output1.xml'
outputModelFileName2 = 'test_Trunc_output2.xml'
outPolyFile1 = 'test_Trunc_polygons1.dat'
outPolyFile2 = 'test_Trunc_polygons2.dat'
gaussFieldFiles = ['testData_Angle/a1.dat','testData_Angle/a2.dat','testData_Angle/a3.dat','testData_Angle/a4.dat','testData_Angle/a5.dat','testData_Angle/a6.dat']

nGaussFields = 3
printInfo = 0
useConstTruncParam = 1
nCase = 7
start = 1
end = 7
for testCase in range(start,end+1):
    print('Case number: ' + str(testCase))
    faciesReferenceFile = 'testData_Angle/test_case_' + str(testCase) + '.dat'
#    faciesOutputFile  = 'testData_Angle/test_case_' + str(testCase) + '.dat'
    faciesOutputFile = 'facies2D.dat'
    if testCase == 1:
        fTable = {2:'F2',1:'F1',3:'F3'}
        faciesInZone = ['F1','F2','F3']
        truncStructure = [['F3', -90.0, 1.0],['F2', +45.0, 1.0],['F1', +45.0, 1.0]]
        faciesInTruncRule = ['F3','F2','F1']
        overlayFacies  = []
        backGroundFacies = []
        overlayTruncCenter = []
        faciesProb = [0.5,0.3,0.2]
        nGaussFields = 2
        [truncRule,truncRule2] = test_initialize_write_read()
        test_getClassName()
        test_getFaciesInTruncRule()
        test_truncMapPolygons()
        test_apply_truncations()

    elif testCase == 2:
        fTable = {2:'F2',1:'F1',3:'F3'}
        faciesInZone = ['F2','F3','F1']
        truncStructure = [['F1', +135.0, 1.0],['F2', +45.0, 1.0],['F3', +45.0, 1.0]]
        faciesInTruncRule = ['F1','F2','F3']
        overlayFacies  = []
        backGroundFacies = []
        overlayTruncCenter = []
        faciesProb = [0.01,0.8,0.19]
        nGaussFields = 2
        [truncRule,truncRule2] = test_initialize_write_read()
        test_getClassName()
        test_getFaciesInTruncRule()
        test_truncMapPolygons()
        test_apply_truncations()

    elif testCase == 3:
        fTable = {1:'F1',2:'F2',3:'F3',4:'F4',5:'F5'}
        faciesInZone = ['F2','F3','F1','F5','F4']
        truncStructure = [['F1', +135.0, 1.0],['F2', +45.0, 1.0],['F3', +45.0, 1.0]]
        faciesInTruncRule = ['F1','F2','F3','F5','F4']
        overlayFacies  = ['F5','F4']
        backGroundFacies = [['F1'],['F3']]
        overlayTruncCenter = [0.9,0.0]
        faciesProb = [0.3,0.2,0.3,0.1,0.1]
        nGaussFields = 4
        [truncRule,truncRule2] = test_initialize_write_read()
        test_getClassName()
        test_getFaciesInTruncRule()
        test_truncMapPolygons()
        test_apply_truncations()

    elif testCase == 4:
        fTable = {1:'F1',2:'F2',3:'F3',4:'F4',5:'F5'}
        faciesInZone = ['F2','F3','F1','F5','F4']
        truncStructure = [['F1', -135.0, 1.0],['F3', +90.0, 1.0],['F2', +45.0, 1.0]]
        faciesInTruncRule = ['F1','F3','F2','F5','F4']
        overlayFacies  = ['F5','F4']
        backGroundFacies = [['F2','F1'],['F3']]
        overlayTruncCenter = [0.0,1.0]
        faciesProb = [0.3,0.2,0.3,0.1,0.1]
        nGaussFields = 4
        [truncRule,truncRule2] = test_initialize_write_read()
        test_getClassName()
        test_getFaciesInTruncRule()
        test_truncMapPolygons()
        test_apply_truncations()


    elif testCase == 5:
        fTable = {1:'F1',2:'F2',3:'F3',4:'F4',5:'F5'}
        faciesInZone = ['F2','F3','F1','F5','F4']
        truncStructure = [['F1', -180.0, 0.5],['F3', +180.0, 1.0],['F1', 0.0, 0.5],['F2', 35.0, 0.7],['F2', -35.0, 0.3]]
        faciesInTruncRule = ['F1','F3','F2','F5','F4']
        overlayFacies  = ['F5','F4']
        backGroundFacies = [['F3','F2'],['F1']]
        overlayTruncCenter = [0.0,0.0]
        faciesProb = [0.2,0.3,0.3,0.1,0.1]
        nGaussFields = 4
        [truncRule,truncRule2] = test_initialize_write_read()
        test_getClassName()
        test_getFaciesInTruncRule()
        test_truncMapPolygons()
        test_apply_truncations()

    elif testCase == 6:
        fTable = {1:'F1',2:'F2',3:'F3',4:'F4',5:'F5'}
        faciesInZone = ['F2','F3','F1','F5','F4']
        truncStructure = [['F1', -180.0, 1.0],['F3', -170.0, 0.5],['F3', -160.0, 0.5],['F2', -150.0, 0.7],['F2', -140.0, 0.3]]
        faciesInTruncRule = ['F1','F3','F2','F5','F4']
        overlayFacies  = ['F5','F4']
        backGroundFacies = [['F3','F2'],['F1']]
        overlayTruncCenter = [0.0,0.0]
        faciesProb = [0.2,0.3,0.3,0.1,0.1]
        nGaussFields = 4
        [truncRule,truncRule2] = test_initialize_write_read()
        test_getClassName()
        test_getFaciesInTruncRule()
        test_truncMapPolygons()
        test_apply_truncations()

    elif testCase == 7:
        fTable = {1:'F1',2:'F2',3:'F3',4:'F4',5:'F5',6:'F6',7:'F7',8:'F8'}
        faciesInZone = ['F2','F3','F1','F5','F4','F6','F7','F8']
        truncStructure = [['F1', -180.0, 0.5],['F3', -170.0, 0.5],['F7', 10.0,1.0],['F1',-60.0,0.5],['F3', -160.0, 0.5],['F2', -150.0, 0.05],['F2', +140.0, 0.95],['F6',120.0,1.0]]
        faciesInTruncRule = ['F1','F3','F7','F2','F6','F5','F4','F8']
        overlayFacies  = ['F5','F4','F8']
        backGroundFacies = [['F3','F2'],['F1'],['F7']]
        overlayTruncCenter = [0.0,0.0,1.0]
        faciesProb = [0.15,0.3,0.2,0.1,0.1,0.05,0.05,0.05]
        nGaussFields = 5
        [truncRule,truncRule2] = test_initialize_write_read()
        test_getClassName()
        test_getFaciesInTruncRule()
        test_truncMapPolygons()
        test_apply_truncations()

    elif testCase == 8:
        fTable = {1:'F1',2:'F2',3:'F3',4:'F4',5:'F5'}
        faciesInZone = ['F2','F3','F1','F5','F4']
        truncStructure = [['F1', -180.0, 1.0],['F3', -170.0, 0.5],['F3', -160.0, 0.5],['F2', -150.0, 0.7],['F2', -140.0, 0.3]]
        faciesInTruncRule = ['F1','F3','F2','F5','F4']
        overlayFacies  = ['F5','F4']
        backGroundFacies = [['F3','F2'],['F1']]
        overlayTruncCenter = [0.0,0.0]
        faciesProb = [0.2,0.3,0.3,0.1,0.1]
        nGaussFields = 4
        [truncRule,truncRule2] = test_initialize_write_read()
        test_getClassName()
        test_getFaciesInTruncRule()
        test_truncMapPolygons()
        test_apply_truncations()

    elif testCase == 9:
        fTable = {1:'F1',2:'F2',3:'F3',4:'F4',5:'F5'}
        faciesInZone = ['F2','F3','F1','F5','F4']
        truncStructure = [['F1', -180.0, 1.0],['F3', -170.0, 0.5],['F3', -160.0, 0.5],['F2', -150.0, 0.7],['F2', -140.0, 0.3]]
        faciesInTruncRule = ['F1','F3','F2','F5','F4']
        overlayFacies  = ['F5','F4']
        backGroundFacies = [['F3','F2'],['F1']]
        overlayTruncCenter = [0.0,0.0]
        faciesProb = [0.2,0.3,0.3,0.1,0.1]
        nGaussFields = 4
        [truncRule,truncRule2] = test_initialize_write_read()
        test_getClassName()
        test_getFaciesInTruncRule()
        test_truncMapPolygons()
        test_apply_truncations()

    elif testCase == 10:
        fTable = {1:'F1',2:'F2',3:'F3',4:'F4',5:'F5'}
        faciesInZone = ['F2','F3','F1','F5','F4']
        truncStructure = [['F1', -180.0, 1.0],['F3', -170.0, 0.5],['F3', -160.0, 0.5],['F2', -150.0, 0.7],['F2', -140.0, 0.3]]
        faciesInTruncRule = ['F1','F3','F2','F5','F4']
        overlayFacies  = ['F5','F4']
        backGroundFacies = [['F3','F2'],['F1']]
        overlayTruncCenter = [0.0,0.0]
        faciesProb = [0.2,0.3,0.3,0.1,0.1]
        nGaussFields = 4
        [truncRule,truncRule2] = test_initialize_write_read()
        test_getClassName()
        test_getFaciesInTruncRule()
        test_truncMapPolygons()
        test_apply_truncations()

    elif testCase == 11:
        fTable = {1:'F1',2:'F2',3:'F3',4:'F4',5:'F5'}
        faciesInZone = ['F2','F3','F1','F5','F4']
        truncStructure = [['F1', -180.0, 1.0],['F3', -170.0, 0.5],['F3', -160.0, 0.5],['F2', -150.0, 0.7],['F2', -140.0, 0.3]]
        faciesInTruncRule = ['F1','F3','F2','F5','F4']
        overlayFacies  = ['F5','F4']
        backGroundFacies = [['F3','F2'],['F1']]
        overlayTruncCenter = [0.0,0.0]
        faciesProb = [0.2,0.3,0.3,0.1,0.1]
        nGaussFields = 4
        [truncRule,truncRule2] = test_initialize_write_read()
        test_getClassName()
        test_getFaciesInTruncRule()
        test_truncMapPolygons()
        test_apply_truncations()

    elif testCase == 12:
        fTable = {1:'F1',2:'F2',3:'F3',4:'F4',5:'F5'}
        faciesInZone = ['F2','F3','F1','F5','F4']
        truncStructure = [['F1', -180.0, 1.0],['F3', -170.0, 0.5],['F3', -160.0, 0.5],['F2', -150.0, 0.7],['F2', -140.0, 0.3]]
        faciesInTruncRule = ['F1','F3','F2','F5','F4']
        overlayFacies  = ['F5','F4']
        backGroundFacies = [['F3','F2'],['F1']]
        overlayTruncCenter = [0.0,0.0]
        faciesProb = [0.2,0.3,0.3,0.1,0.1]
        nGaussFields = 4
        [truncRule,truncRule2] = test_initialize_write_read()
        test_getClassName()
        test_getFaciesInTruncRule()
        test_truncMapPolygons()
        test_apply_truncations()

    elif testCase == 13:
        fTable = {1:'F1',2:'F2',3:'F3',4:'F4',5:'F5'}
        faciesInZone = ['F2','F3','F1','F5','F4']
        truncStructure = [['F1', -180.0, 1.0],['F3', -170.0, 0.5],['F3', -160.0, 0.5],['F2', -150.0, 0.7],['F2', -140.0, 0.3]]
        faciesInTruncRule = ['F1','F3','F2','F5','F4']
        overlayFacies  = ['F5','F4']
        backGroundFacies = [['F3','F2'],['F1']]
        overlayTruncCenter = [0.0,0.0]
        faciesProb = [0.2,0.3,0.3,0.1,0.1]
        nGaussFields = 4
        [truncRule,truncRule2] = test_initialize_write_read()
        test_getClassName()
        test_getFaciesInTruncRule()
        test_truncMapPolygons()
        test_apply_truncations()


