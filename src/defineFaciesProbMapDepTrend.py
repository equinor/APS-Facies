#!/bin/env python

import roxar
import copy
import sys
import xml.etree.ElementTree as ET
import numpy as np
import importlib

import src.generalFunctionsUsingRoxAPI as gf
from src.utils.constants.simple import Debug


importlib.reload(gf)

class DefineFaciesProbMapDep:
    def __init__(self,modelFileName,project):
        
        self.__gridModelName=None
        self.__zoneParamName= None
        self.__faciesParamName= None
        #kariself.__probDefinitionMatrix=None

        self.__probParamNamePrefix= None
        self.__project = project
        self.__selectedZoneNumbers=None
        self.__zoneAsimuthValues=None
        assert(modelFileName)
        assert(project)

        self.__interpretXMLModelFile(modelFileName,project)

    def __interpretXMLModelFile(self, modelFileName,project):
        print('Read model file: ' + modelFileName)
        tree = ET.parse(modelFileName)
        self.__ET_Tree = tree
        root = tree.getroot()

        kw = 'FaciesProbMapDepTrend'
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
            kw = 'ZoneDepositionAzimuthValues'
            self.__zoneAsimuthValues = []
            obj2 = obj.find(kw)
            if obj2 is not None:
                text = obj2.text
                textList = text.split()
                if len(textList)==1: # Same asimuth in all zones
                    az=float(textList[0])
                    if az < 0.0 or az > 360:
                        raise ValueError('Error: The asimuth value(s) must be between 0 and 360 degrees.')
                    self.__zoneAsimuthValues=len(self.__selectedZoneNumbers)*[az]
                elif len(textList)==len(self.__selectedZoneNumbers):
                    self.__zoneAsimuthValues=[float(x) for x in textList]
                else:
                    raise ValueError('Error: The number of asimuth values must be 1 or correspond to the number of selected zones.')

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
        import sys
        
        # Get facies map grid model and compute statistics per zone
        eps = 0.00001
        debug_level = Debug.ON
        realNumber = 0
        numStripes=100

        # Modelling Grid
        gridModel = self.__project.grid_models[self.__gridModelName]
        grid3D = gridModel.get_grid(realNumber)
        indexer = grid3D.simbox_indexer
        dimI,dimJ,dimK = indexer.dimensions
        [zoneValues,codeNamesZone] = gf.getDiscrete3DParameterValues(gridModel, self.__zoneParamName, realNumber, debug_level=debug_level)
        [mapFacies, faciesCodeNames] = gf.getDiscrete3DParameterValues(gridModel, self.__faciesParamName, realNumber, debug_level=debug_level)

        faciesVals=[]
        faciesNames=[]
        for elem in faciesCodeNames:
            faciesVals.append(elem)
            faciesNames.append(faciesCodeNames[elem])
        nFacies=len(faciesVals)
        probValues = np.zeros((len(zoneValues),nFacies),np.float32)
        stripeNumber=np.zeros(len(zoneValues),np.float32)

        # Go through zone by zone and compute deposition average
        for idx in range(len(self.__selectedZoneNumbers)):
            zoneIndx = self.__selectedZoneNumbers[idx]
            print("Zone: ", zoneIndx)
            if zoneIndx in indexer.zonation:
                layerRanges = indexer.zonation[zoneIndx]
                lr=layerRanges[0]

                cellNumbers = indexer.get_cell_numbers_in_range((0,0,lr.start),(dimI,dimJ,lr.stop)) # Only top layer
                cellCorners = grid3D.get_cell_corners(cellNumbers)
                cellCenters = grid3D.get_cell_centers(cellNumbers)
                cellIndices = indexer.get_indices(cellNumbers)

                # Normal vector to azimuth
                az=self.__zoneAsimuthValues[idx]
                alpha=az+90
                if alpha>360: alpha=alpha-360
                alpha=alpha/360.0*2.0*np.pi
                az=az/360.0*2.0*np.pi
                nvec=[np.sin(alpha), np.cos(alpha)]
                dvec=[np.sin(az), np.cos(az)]

                # Stripe data
                stripeWidth=min((np.amax(cellCenters[:,0])-np.amin(cellCenters[:,0])),(np.amax(cellCenters[:,1])-np.amin(cellCenters[:,1])))/numStripes

                A0=[0.0,0.0]
                if np.sign(dvec[0]*dvec[1]) > 0: 
                    A0[0]=np.amin(cellCorners[:,0:8,0])
                else:
                    A0[0]=np.amax(cellCorners[:,0:8,0])
                A0[1]=np.amin(cellCorners[:,0:4,1])  
                D = cellCenters[:,0:2]-A0
                Dn=D[:,1]*nvec[0]-D[:,0]*nvec[1]

                stripeNo=np.abs(np.ceil(Dn/(stripeWidth*(dvec[1]*nvec[0]-dvec[0]*nvec[1]))))
                stripeNumber[cellNumbers]=stripeNo
                
                searchIndices=[x for x in range(len(stripeNo))]
                for strip in range(int(np.amin(stripeNo)),int(np.amax(stripeNo))+1):
                    cellsInStripe = []
                    usedIndices=[]
                    i=0
                    while i<len(searchIndices):
                        index=searchIndices[i]
                        if stripeNo[index]==strip:
                            cellsInStripe.append(cellNumbers[index])
                            # Remove used cells, reduce runtime
                            del searchIndices[i]
                        else:
                            i+=1
                            
                    noCells=len(cellsInStripe)
                    if noCells>0:
                        for fIdx in range(len(faciesVals)):
                            facies=faciesVals[fIdx]
                            probValues[cellsInStripe,fIdx] = np.sum(mapFacies[cellsInStripe]==facies)/noCells


        #Write the calculated probabilities for the selected zones to 3D parameter
        #If the 3D parameter exist in advance, only the specified zones will be altered
        #while grid cell values for other zones are unchanged. 
        gf.setContinuous3DParameterValues(gridModel, "stripeNumber", stripeNumber,
                                          self.__selectedZoneNumbers, realNumber, debug_level=debug_level)
        for fIdx in range(len(faciesVals)):
            facies=faciesVals[fIdx]
            fName=faciesNames[fIdx]
            if fName:
                parameterName = self.__probParamNamePrefix + '_' +fName
                print (parameterName, facies)
                if not gf.setContinuous3DParameterValues(gridModel,parameterName,probValues[:,fIdx],
                                                         self.__selectedZoneNumbers,realNumber,debug_level=debug_level):
                    raise ValueError('Error: Grid model is empty or can not be updated.')
                        




# ---------------------------- Main -----------------------------------------------
modelFileName = 'APS_prob_mapdep.xml'
defineFaciesTrend = DefineFaciesProbMapDep(modelFileName,project)
defineFaciesTrend.calculateFaciesProbParam()
print('Finished running defineFaciesProbTrend')
