#!/bin/env python
import sys
import copy
from xml.etree.ElementTree import Element


class APSMainFaciesTable:
    """
    Class APSMainFaciesTable
    Description: Keeps the global facies table. All facies used in the APS model
                 must exist in this table before being used.

     Public member functions:
       Constructor:  def __init__(self,ET_Tree=None,modelFileName=None,printInfo =0)

       def initialize(self,fTable)
                  - Initialize the object from a facies/code dictionary object

      --- Get functions ---
       def getNFacies(self)
       def getClassName(self)
       def getFaciesTable(self)
       def getFaciesName(self,fIndx)
       def getFaciesCode(self,fIndx)
       def getFaciesCodeForFaciesName(self,fName)
       def getFaciesIndx(self,fName)

       --- Set functions ---
       def addFacies(self,faciesName, code)
       def removeFacies(self,faciesName):

       --- Check functions ---
       def checkWithFaciesTable(self,fName)

       --- Write ---
       def XMLAddElement(self,root)
                - Add data to xml tree

     Private member functions:

       def __checkUniqueFaciesNamesAndCodes(self)

    --------------------------------------------------------------------
    """
    def __init__(self, ET_Tree=None, modelFileName=None, printInfo=0):
        self.__nFacies = 0
        self.__faciesTable = []
        self.__printInfo = printInfo
        self.__className = 'APSMainFaciesTable'
        self.__NAME = 0
        self.__CODE = 1
        self.__modelFileName = modelFileName

        #assert ET_Tree is not None
        if ET_Tree is None:
            # Create an empty object which will at a later stage be filled by using 
            # the initialize function.
            return

        # Search xml tree for model file to find the specified Main facies table
        self.__interpretXMLTree(ET_Tree)
        if self.__printInfo >= 3:
            print('Debug output: Call APSMainFaciesTable init')
        return

    # End __init__

    def __interpretXMLTree(self, ET_Tree):
        root = ET_Tree.getroot()

        # Read main facies table for the model
        kw = 'MainFaciesTable'
        obj = root.find(kw)
        if obj == None:
            print('Error when reading model file: ' + self.__modelFileName)
            print('Error: Missing keyword ' + kw)
            sys.exit()
        else:
            fTable = obj
            for fItem in fTable.findall('Facies'):
                fName = fItem.get('name')
                text = fItem.find('Code').text
                fCode = int(text.strip())
                self.__faciesTable.append([fName, fCode])
            if self.__faciesTable == None:
                print('Error when reading model file: ' + self.__modelFileName)
                print('Error: Missing keyword Facies when reading specification of MainFaciesTable')
                sys.exit()
        self.__nFacies = len(self.__faciesTable)
        if not self.__checkUniqueFaciesNamesAndCodes():
            sys.exit()
        return

    def initialize(self, fTable):
        # Input fTable must be a dictionary
        codeList = fTable.keys()
        for c in codeList:
            fName = fTable.get(c)
            fCode = int(c)
            self.__faciesTable.append([fName, fCode])
        self.__nFacies = len(self.__faciesTable)
        return

    def getNFacies(self):
        return self.__nFacies

    def getClassName(self):
        return copy.copy(self.__className)

    def getFaciesTable(self):
        return copy.copy(self.__faciesTable)

    def getFaciesName(self, fIndx):
        return self.__faciesTable[fIndx][self.__NAME]

    def getFaciesCode(self, fIndx):
        return int(self.__faciesTable[fIndx][self.__CODE])

    def getFaciesCodeForFaciesName(self, fName):
        code = -999
        for item in self.__faciesTable:
            if item[self.__NAME] == fName:
                code = item[self.__CODE]
                break
        return code

    def getFaciesIndx(self, fName):
        found = 0
        for i in range(self.__nFacies):
            fItem = self.__faciesTable[i]
            facName = fItem[self.__NAME]
            if fName == facName:
                fIndx = i
                found = 1
                break
        if found == 0:
            return -999
        else:
            return fIndx

    def addFacies(self, faciesName, code):
        # Check that the faciesName and code is not already used
        err = 0
        for i in range(len(self.__faciesTable)):
            item = self.__faciesTable[i]
            fName = item[0]
            fCode = item[1]
            if faciesName == fName or code == fCode:
                err = 1
                break
        if err == 1:
            print('Error in ' + self.__className)
            print('Error: Try to add new facies with a name or code that is already used.')

        item = [faciesName, code]
        self.__faciesTable.append(item)
        self.__nFacies += 1
        return err

    def removeFacies(self, faciesName):
        for i in range(len(self.__faciesTable)):
            item = self.__faciesTable[i]
            fName = item[0]
            fCode = int(item[1])
            if faciesName == fName:
                self.__faciesTable.pop(i)
                self.__nFacies -= 1
                break


    def checkWithFaciesTable(self, fName):
        found = 0
        for fItem in self.__faciesTable:
            name = fItem[self.__NAME]
            if fName == name:
                found = 1
                break
        if found == 0:
#            print('Error: Facies name: ' + fName + ' is not found among specified facies names.')
#            print('Specified facies names and codes are: \n')
#            print(repr(self.__faciesTable))
            return False
        else:
            return True

    # -- End of function checkWithFaciesTable


    def XMLAddElement(self, root):
        tag = 'MainFaciesTable'
        elem = Element(tag)
        root.append(elem)
        ftElement = elem
        for i in range(self.__nFacies):
            fName = self.__faciesTable[i][0]
            fCode = self.__faciesTable[i][1]
            tag = 'Facies'
            attribute = {'name': fName}
            elem = Element(tag, attribute)
            ftElement.append(elem)
            fElement = elem
            tag = 'Code'
            elem = Element(tag)
            elem.text = ' ' + str(fCode) + ' '
            fElement.append(elem)

        return

    def __checkUniqueFaciesNamesAndCodes(self):
        found = 0
        for i in range(self.__nFacies):
            f1 = self.__faciesTable[i][self.__NAME]
            for j in range(i + 1, self.__nFacies):
                f2 = self.__faciesTable[j][self.__NAME]
                if f1 == f2:
                    found = 1
                    print('Error: In ' + self.__className)
                    print('Error: Facies name: ' + f1 + ' is specified multiple times')
                    break
        for i in range(self.__nFacies):
            c1 = self.__faciesTable[i][self.__CODE]
            for j in range(i + 1, self.__nFacies):
                c2 = self.__faciesTable[j][self.__CODE]
                if c1 == c2:
                    found = 1
                    print('Error: In ' + self.__className)
                    print('Error: Facies code: ' + str(c1) + ' is specified multiple times')
                    break
        if found == 1:
            return False
        else:
            return True
            # -- End of function checkUniqueFaciesNamesAndCodes
