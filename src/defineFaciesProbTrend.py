#!/bin/env python
import roxar
import copy
import sys
import xml.etree.ElementTree as ET
import numpy as np
import src.generalFunctionsUsingRoxAPI as gf
from src.utils.constants.simple import Debug

class DefineFaciesProb:
    def __init__(self,modelFileName,project, debug_level=Debug.OFF):
        
        self.__gridModelName=None
        self.__zoneParamName= None
        self.__faciesParamName= None
        self.__probDefinitionMatrix=None

        self.__probParamNamePrefix= None
        self.__project = project
        self.__selectedZoneNumbers=None
        self.__debug_level=debug_level
        assert(modelFileName)
        assert(project)

        self.__interpretXMLModelFile(modelFileName,project, debug_level=self.__debug_level)

    def __interpretXMLModelFile(self, modelFileName,project,debug_level=Debug.OFF):
        print('Read model file: ' + modelFileName)
        tree = ET.parse(modelFileName)
        self.__ET_Tree = tree
        root = tree.getroot()

        kw = 'FaciesProbTrend'
        obj = root.find(kw)
        if obj is not None:
            kw = 'GridModelName'
            obj2 = obj.find(kw)
            if obj2 is not None:
                text = obj2.text
                self.__gridModelName = copy.copy(text.strip())
            else:
                raise IOError(
                    'Error reading {}'
                    'Error missing command: {}'.format(modelFileName,kw)
                    )

            kw = 'ZoneParamName'
            obj2 = obj.find(kw)
            if obj2 is not None:
                text = obj2.text
                self.__zoneParamName = copy.copy(text.strip())
            else:
                raise IOError(
                    'Error reading {}'
                    'Error missing command: {}'.format(modelFileName,kw)
                    )

            kw = 'FaciesParamName'
            obj2 = obj.find(kw)
            if obj2 is not None:
                text = obj2.text
                self.__faciesParamName = copy.copy(text.strip())
            else:
                raise IOError(
                    'Error reading {}'
                    'Error missing command: {}'.format(modelFileName,kw)
                    )

            kw = 'ProbParamNamePrefix'
            obj2 = obj.find(kw)
            if obj2 is not None:
                text = obj2.text
                self.__probParamNamePrefix = copy.copy(text.strip())
            else:
                raise IOError(
                    'Error reading {}'
                    'Error missing command: {}'.format(modelFileName,kw)
                    )
            kw = 'SelectedZones'
            self.__selectedZoneNumbers = []
            zoneList = []
            obj2 = obj.find(kw)
            if obj2 is not None:
                text = obj2.text
                textList = text.split()
                for s in textList:
                    zoneList.append(int(s.strip()))
                for i in range(len(zoneList)):
                    zNr = zoneList[i]
                    # Zone numbers are specified from 1, but need them numbered from 0 
                    self.__selectedZoneNumbers.append(zNr-1)
            else:
                raise IOError(
                    'Error reading {}'
                    'Error missing command: {}'.format(modelFileName,kw)
                    )

            kw = 'CondProbMatrix'
            self.__probDefinitionMatrix = []
            obj2= obj.find(kw)
            if obj2 is not None:
                kw = 'Line'
                for objLine in obj2.findall(kw):
                    if objLine is not None:
                        text = objLine.text
                        [text1,text2,text3] = text.split()
                        fName = copy.copy(text1.strip())
                        fNameInReal = copy.copy(text2.strip())
                        prob = float(text3.strip())
                        if debug_level == Debug.VERBOSE:
                            print('fname, fnameInReal,prob: ' + fName + ' ' + fNameInReal + ' '  + str(prob))
                        line = [fName, fNameInReal,prob]
                        self.__probDefinitionMatrix.append(line)
                    else:
                        raise IOError(
                            'Error reading {}'
                            'Error missing command: {}'.format(modelFileName,kw)
                            )

            else:
                raise IOError(
                    'Error reading {}'
                    'Error missing command: {}'.format(modelFileName,kw)
                    )

        else:
            raise IOError(
                'Error reading {}'
                'Error missing command: {}'.format(modelFileName,kw)
                )
        

    def calculateFaciesProbParam(self):
        # Get grid model and grid model parameter
        eps = 0.00001
        debug_level = self.__debug_level
        realNumber = 0
        gridModel = self.__project.grid_models[self.__gridModelName]
        [zoneValues,codeNamesZone] = gf.getDiscrete3DParameterValues(gridModel,self.__zoneParamName,realNumber,debug_level)
        [faciesRealValues,codeNamesFacies] = gf.getDiscrete3DParameterValues(gridModel,self.__faciesParamName,realNumber,debug_level)
        minimum = np.min(faciesRealValues)
        maximum = np.max(faciesRealValues)

        # Find facies
        faciesNames = []
        faciesNamesInReal = []
        for item in self.__probDefinitionMatrix:
            fName = item[0]
            fNameInReal = item[1]
            if fName not in faciesNames:
                faciesNames.append(copy.copy(fName))

            if fNameInReal not in faciesNamesInReal:
                faciesNamesInReal.append(copy.copy(fNameInReal))

        if debug_level == Debug.VERBOSE:
            print('Facies names:')
            print(repr(faciesNames))

            print('Facies names in input:')
            print(repr(faciesNamesInReal))

            print('CodeNamesFacies:')
            print(repr(codeNamesFacies))

        probIndx = np.zeros(maximum+1,np.int)
        for i in range(maximum):
            probIndx[i] = -1

        for  i in range(len(faciesNamesInReal)):
            fN = faciesNamesInReal[i]
            for codeVal in range(minimum,maximum+1):
                if codeVal in codeNamesFacies:
                    fN2 = codeNamesFacies[codeVal]
                    if fN == fN2:
                        probIndx[codeVal] = i

        # probability matrix using indices corresponding to the lists faciesNames and faciesNamesInReal
        nFacies = len(faciesNames)
        nFacInReal = len(faciesNamesInReal)
        probabilities = np.zeros((nFacies,nFacInReal),dtype=np.float32)
        indx1 = -1
        indx2 = -1
        for item in self.__probDefinitionMatrix:
            fName = item[0]
            fNameInReal = item[1]
            prob = item[2]
            for i in range(nFacies):
                fN = faciesNames[i]
                if fName == fN:
                    indx1 = i
                    break

            for i in range(nFacInReal):
                fN = faciesNamesInReal[i]
                if fNameInReal == fN:
                    indx2 = i
                    break

            if indx1 < 0 or indx2 < 0:
                raise ValueError('Error: Inconsistency in program.')

            probabilities[indx1,indx2] = prob

        # Check that probabilites specified are normalized
        for j in range(nFacInReal):
            sumProb = 0.0
            for i in range(nFacies):
                sumProb += probabilities[i,j]
            if abs(sumProb-1.0)> eps:
                raise ValueError('Error: Specified probabilities for facies in regions with name: ' +
                                 faciesNamesInReal[j] + ' does not sum up to 1.0'
                                 )
        if debug_level == Debug.VERBOSE:
            print('Probability matrix')
            print(repr(probabilities))
        if debug_level == Debug.ON:
            print('Start calculate new probabilities for selected zones for each specified facies')
        sumProbValues = np.zeros(len(zoneValues),np.float32)
        for f in range(nFacies):
            fName = faciesNames[f]
            if debug_level == Debug.ON:
                print('Facies name: ' + fName)

            parameterName = self.__probParamNamePrefix + '_' +fName
            if debug_level == Debug.ON:
                print('Parameter: ' + parameterName)

            parameterNameCum = self.__probParamNamePrefix + '_cum_' +fName
            if debug_level == Debug.ON:
                print('Parameter for cum prob: ' + parameterNameCum)

            # Create new array with 0 probabilities for this facies
            probValues = np.zeros(len(zoneValues),np.float32)
            n=0
            for zoneNumber in self.__selectedZoneNumbers:
                # Filter out cells with selected zone numbers
#                print('Zone number: ' + str(zoneNumber+1))
                [nDefinedCells,cellIndexDefined] = gf.getCellValuesFilteredOnDiscreteParam(zoneNumber+1,zoneValues)
                for i in range(nDefinedCells):
                    indx = cellIndexDefined[i]
                    codeVal = faciesRealValues[indx]
                    pIndx = probIndx[codeVal]
                    probValues[indx] = probabilities[f,pIndx]

            # Calculate cumulative prob of all previously processed facies including current
            sumProbValues += probValues

            # Write the calculated probabilities for the selected zones to 3D parameter
            # If the 3D parameter exist in advance, only the specified zones will be altered
            # while grid cell values for other zones are unchanged. 
            if not gf.setContinuous3DParameterValues(gridModel,parameterName,probValues,
                                                     self.__selectedZoneNumbers,realNumber,debug_level=debug_level):
                raise ValueError('Error: Grid model is empty or can not be updated.')
                
            # Write cumulative prob
            if not gf.setContinuous3DParameterValues(gridModel,parameterNameCum,sumProbValues,
                                                     self.__selectedZoneNumbers,realNumber,debug_level=debug_level):
                raise ValueError('Error: Grid model is empty or can not be updated.')

# ---------------------------- Main -----------------------------------------------
if __name__ == "__main__":
    modelFileName = 'defineProbTrend.xml'
    defineFaciesTrend = DefineFaciesProb(modelFileName,project, debug_level=Debug.ON)
    defineFaciesTrend.calculateFaciesProbParam()
    print('Finished running defineFaciesProbTrend')
