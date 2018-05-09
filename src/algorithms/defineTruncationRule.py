#!/bin/env python
# -*- coding: utf-8 -*-
# --------------------------------------------------------
# class DefineTruncationRule
# Description: Handle truncation rule settings
# --------------------------------------------------------
import copy
import numpy as np
import matplotlib
from matplotlib import pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Polygon

from src.utils.constants.simple import Debug
from src.algorithms.Trunc2D_Angle_xml import Trunc2D_Angle
from src.algorithms.Trunc2D_Cubic_xml import Trunc2D_Cubic
from src.algorithms.APSMainFaciesTable import APSMainFaciesTable
from src.utils.methods import get_colors
from src.utils.xmlUtils import prettify

from xml.etree.ElementTree import Element

class DefineTruncationRule:
    """
    This class read truncation rule settings for Cubic or NonCubic truncation rules 
    from file and can create objects of type Trunc2D_Cubic_xml or Trunc2D_Angle_xml.
    The purpose of the class is to:
    - enable GUI to read predefined truncation rule settings from file 
    - enable GUI to write user defined truncation rule settings to file
    - enable GUI to create mini pictures (icons) for truncation rule settings
    """
    def __init__(self, directory=''):
        self.__tableCubic = {}
        self.__tableNonCubic = {}
        self.__inputFileName = None
        self.debug_level = Debug.OFF
        self.__directory = directory

    def readFile(self, inputFileName):
        ''' Read ascii file with definition of truncation rule settings'''
        
        self.__inputFileName = copy.copy(inputFileName)
        finished = False
        print('Read file with truncation rules: {}'.format(inputFileName))
        if self.__directory != '':
            inputFile = self.__directory + '/' + self.__inputFileName
        else:
            inputFile = self.__inputFileName
        with open(inputFile, 'r') as file:
            while not finished:
                try:
                    line = file.readline()
                    if line == '':
                        finished = True
                    words = line.split()
                    if len(words) > 0:
                        if words[0] != '#':
                            ruleType = words[0]
                            name = words[1]
                            if ruleType == 'Cubic':
                                truncStructureCubic = self.__getTruncSettingsCubicFromFile(words)
                                self.__tableCubic[name] = truncStructureCubic
                            elif ruleType == 'NonCubic':
                                truncStructureNonCubic = self.__getTruncSettingsNonCubicFromFile(words)
                                self.__tableNonCubic[name] = truncStructureNonCubic
                            else:
                                raise IOError('File format error in  {}'.format(inputFile))

                except:
                    finished = True

    def writeFile(self, outputFileName):
        ''' Write dictionaries with truncation rule settings to file.'''
        if self.__directory != '':
            outputFile = self.__directory + '/' + outputFileName
        else:
            outputFile = outputFileName
        if self.debug_level >= Debug.VERBOSE:
            print('Debug output: Write file with truncation rules: {}'.format(outputFile))
            
        with open(outputFile, 'w') as file:
            
            for name, truncStructItem in self.__tableCubic.items():
                nPoly = len(truncStructItem)-1
                outString = 'Cubic ' + name + ' ' + str(nPoly) +' '
                outString = outString + "['" + truncStructItem[0] + "', "
                for i in range(nPoly-1):
                    polyItem = truncStructItem[i+1]
                    outString = outString + "['"+ polyItem[0] + "', " + str(polyItem[1]) + ', '
                    outString = outString + str(polyItem[2]) + ', ' + str(polyItem[3]) + ', ' + str(polyItem[4]) +'], '

                polyItem = truncStructItem[nPoly]
                outString = outString + "['"+ polyItem[0] + "', " + str(polyItem[1]) + ', '
                outString = outString + str(polyItem[2]) + ', ' + str(polyItem[3]) + ', ' + str(polyItem[4]) +']]'
                file.write(outString)
                file.write('\n')

            for name, truncStructItem in self.__tableNonCubic.items():
                nPoly = len(truncStructItem)
                outString = 'NonCubic ' + name + ' ' + str(nPoly) +' '
                outString = outString + '['
                for i in range(nPoly-1):
                    polyItem = truncStructItem[i]
                    outString = outString + "['"+ polyItem[0] + "', " + str(polyItem[1]) + ', '
                    outString = outString + str(polyItem[2]) + '], '

                polyItem = truncStructItem[nPoly-1]
                outString = outString + "['"+ polyItem[0] + "', " + str(polyItem[1]) + ', '
                outString = outString + str(polyItem[2]) +']]'
                file.write(outString)
                file.write('\n')
                
                
                       
    def __getTruncSettingsCubicFromFile(self,words):
        ''' Read details about Cubic truncation rule settings. Is used in function to read settings'''
        nPoly = int(words[2])
        if words[3][2] == 'H':
            direction = 'H'
        elif words[3][2] == 'V':
            direction = 'V'
        else:
            raise IOError('Format error for word number 4 in file {}'.format(self.__inputFileName))

        
        truncItem = []
        truncItem.append(direction)
        m = 4
        for i in range(nPoly):
            faciesName = copy.copy(words[m][2:5])

            n = len(words[m+1])
            probFrac = float(words[m+1][:n-1])
            
            n = len(words[m+2])
            L1 = int(words[m+2][:n-1])
            
            n = len(words[m+3])
            L2 = int(words[m+3][:n-1])
            
            n = len(words[m+4])
            L3 = int(words[m+4][:n-2])

            m = m+5
            polygonItem = [faciesName, probFrac, L1, L2, L3]
            truncItem.append(polygonItem)

        return truncItem

    def __getTruncSettingsNonCubicFromFile(self,words):
        ''' Read details about NonCubic truncation rule settings. Is used in function to read settings'''
        nPoly = int(words[2])
        truncItem = []

        m = 3
        for i in range(nPoly):
            if i==0:
                faciesName = copy.copy(words[m][3:6])
            else:
                faciesName = copy.copy(words[m][2:5])
            n = len(words[m+1])
            angle = float(words[m+1][:n-1])
            
            n = len(words[m+2])
            probFrac = float(words[m+2][:n-2])

            m = m+3
            polygonItem = [faciesName, angle, probFrac]
            truncItem.append(polygonItem)

        return truncItem

    def getTruncationRuleObject(self, name):
        ''' Get truncation rule settings with given name. 
            Create an truncation rule object with correct type.
            Facies names and Gauss field names are given default values. 
            The default facies names are those specified in the settings for the truncation rule.
            No overlay facies information used.
        '''
        itemCubic = None
        itemNonCubic = None
        try:
            itemCubic = self.__tableCubic[name]
        except:
            try:
                itemNonCubic = self.__tableNonCubic[name]
            except:
                return None

        if itemCubic != None:
            if self.debug_level >= Debug.VERBOSE:
                print('Debug output: Create truncation object of type Cubic from truncation setting with name: {}'.format(name))
                
            # Cubic truncation rule where each polygon is specified as [faciesName, probFraction, L1, L2, L3]
            truncStructureList = itemCubic
            nPolygons = len(truncStructureList)-1
            fNameList = []
            fTable = {}
            for i in range(1,nPolygons+1):
                polyItem = truncStructureList[i]
                fName = polyItem[0]
                # Add the facies name only if it is not already within the list
                if fName not in fNameList:
                    fNameList.append(fName)
                    fTable[i] = fName
                    
            # Define default values for name of gauss fields, facies
            faciesInZone = fNameList
            mainFaciesTable = APSMainFaciesTable(fTable=fTable)                
            gaussFieldsInZone = ['GRF01','GRF02']
            alphaFieldNameForBackGroundFacies = ['GRF01','GRF02']
            overlayGroups = None
            truncObj = Trunc2D_Cubic()
            truncObj.initialize(mainFaciesTable, faciesInZone, gaussFieldsInZone,alphaFieldNameForBackGroundFacies,
                                truncStructureList, overlayGroups=overlayGroups, debug_level=self.debug_level)
        if itemNonCubic != None:
            if self.debug_level >= Debug.VERBOSE:
                print('Debug output: Create truncation object of type NonCubic from truncation setting with name: {}'.format(name))
            # NonCubic truncation rule where each polygon is specified as [faciesName, angle, probFraction]
            truncStructureList = itemNonCubic
            nPolygons = len(truncStructureList)
            fNameList = []
            fTable = {}
            for i in range(nPolygons):
                polyItem = truncStructureList[i]
                fName = polyItem[0]
                # Add the facies name only if it is not already within the list
                if fName not in fNameList:
                    fNameList.append(fName)
                    fTable[i+1] = fName
                    
            # Define default values for name of gauss fields, facies
            faciesInZone = fNameList
            mainFaciesTable = APSMainFaciesTable(fTable=fTable)                
            gaussFieldsInZone = ['GRF01','GRF02']
            alphaFieldNameForBackGroundFacies = ['GRF01','GRF02']
            truncObj = Trunc2D_Angle()
            truncObj.initialize(mainFaciesTable, faciesInZone, gaussFieldsInZone,alphaFieldNameForBackGroundFacies,
                                truncStructureList, debug_level=self.debug_level)
        
        return truncObj

    def writeTruncRuleToXmlFile(self, name, outputFileName):
        ''' Build an XML tree with top as root from truncation object and write it'''
        truncRuleObj = self.getTruncationRuleObject(name)
        assert truncRuleObj is not None
        top = Element('TOP')
        truncRuleObj.XMLAddElement(top)
        rootReformatted = prettify(top)
        print('Write file:  {}'.format(outputFileName))
        with open(outputFileName, 'w') as file:
            file.write(rootReformatted)

    def writeTruncRuleToXmlFileWithOverlayFacies(self, name, outputFileName, nGroups=2, nPolyPerGroup=2):
        ''' Build an XML tree with top as root from truncation object and write it.
            Create some default overlay facies.  '''
        truncRuleObj = self.getTruncationRuleObjectAddOverLay(name, nGroups, nPolyPerGroup)
        assert truncRuleObj is not None
        top = Element('Example')
        truncRuleObj.XMLAddElement(top)
        rootReformatted = prettify(top)
        print('Write file:  {}'.format(outputFileName))
        with open(outputFileName, 'w') as file:
            file.write(rootReformatted)


    def initNewTruncationRuleSettingsCubic(self, direction):
        ''' Initialize new truncation rule settings.
            Call this function as the first function when creating an new settings for Cubic rules.'''
        if direction == 'H':
            truncStructureCubic = ['H']
        else:
            truncStructureCubic = ['V']
        return truncStructureCubic
    
    def initNewTruncationRuleSettingsNonCubic(self):
        ''' Initialize new truncation rule settings.
            Call this function as the first function when creating an new settings for NonCubic rules.'''
        truncStructureNonCubic = []
        return truncStructureNonCubic
    
    def addPolygonToTruncationRuleSettingsCubic(self, truncStructureCubic, faciesName, probFrac, L1, L2, L3):
        ''' Add one polygon settings for Cubic rules. 
            Use this function repeatedly to add the polygons for one Cubic settings.
            NOTE: Add polygons in correct order sorted by first L1, then L2 then L3.'''

        polyItem = [faciesName, probFrac, L1 ,L2, L3]
        truncStructureCubic.append(polyItem)

    def addPolygonToTruncationRuleSettingsNonCubic(self, truncStructureCubic, faciesName, angle, probFrac):
        ''' Add one polygon settings for NonCubic rules. 
            Use this function repeatedly to add the polygons for one NonCubic settings.
            NOTE: Add polygons in the correct order as specified by user.'''

        polyItem = [faciesName, angle, probFrac]
        truncStructureCubic.append(polyItem)

    def addTruncationRuleSettings(self, name, truncType, truncStructureSetting):
        ''' Add a truncation rule settings to the truncation rule settings dictionary
            using name as key.'''
        if truncType == 'Cubic':
            self.__tableCubic[name] = truncStructureSetting
        elif truncType == 'NonCubic':
            self.__tableNonCubic[name] = truncStructureSetting
        else:
            raise ValueError('Truncation rule of type {} is not defined.'.format(truncType))
        

    def getTruncationRuleObjectAddOverLay(self, name, nGroups, nPolyPerGroup):
        ''' Get truncation rule settings with given name. 
            Create an truncation rule object with correct type.
            Facies names and Gauss field names are given default values. 
            The default facies names are those specified in the settings for the truncation rule.
        '''
        itemCubic = None
        itemNonCubic = None
        try:
            itemCubic = self.__tableCubic[name]
        except:
            try:
                itemNonCubic = self.__tableNonCubic[name]
            except:
                return None

        startPolygonIndx = 0
        endPolygonIndx = 0
        truncObj = None
        if itemCubic != None:
            if self.debug_level >= Debug.VERBOSE:
                print('Debug output: Create truncation object of type Cubic from truncation setting with name: {}'.format(name))
                
            # Cubic truncation rule where each polygon is specified as [faciesName, probFraction, L1, L2, L3]
            truncStructureList = itemCubic
            nPolygons = len(truncStructureList)-1
            startPolygonIndx = 1
            endPolygonIndx = nPolygons+1
            truncObj = Trunc2D_Cubic()
        if itemNonCubic != None:
            if self.debug_level >= Debug.VERBOSE:
                print('Debug output: Create truncation object of type NonCubic from truncation setting with name: {}'.format(name))

            # NonCubic truncation rule where each polygon is specified as [faciesName, angle, probFraction]
            truncStructureList = itemNonCubic
            nPolygons = len(truncStructureList)
            startPolygonIndx = 0
            endPolygonIndx = nPolygons
            truncObj = Trunc2D_Angle()

        fNameList = []
        fTable = {}
        for i in range(startPolygonIndx,endPolygonIndx):
            polyItem = truncStructureList[i]
            fName = polyItem[0]
            # Add the facies name only if it is not already within the list
            if fName not in fNameList:
                fNameList.append(fName)
                fTable[i] = fName
                    
        # Define default values for name of gauss fields, facies from background model
        faciesInZone = fNameList
        mainFaciesTable = APSMainFaciesTable(fTable=fTable)                
        gaussFieldsInZone = ['GRF01','GRF02']
        alphaFieldNameForBackGroundFacies = ['GRF01','GRF02']

        # Create overlay truncation rules with default values
        nFacies = len(faciesInZone)
        overlayGroups = []
        for groupIndx in range(nGroups):
            # Choose as default that one background facies is used per group
            # This means that the max number of groups is equal to the number of background facies
            if groupIndx < nFacies:
                backGroundFacies = fNameList[groupIndx]
                backGroundFaciesList =[backGroundFacies]
                alphaFieldNumber = 3
                alphaList = []
                for polyIndx in range(nPolyPerGroup):
                    # Define new facies as overlay facies
                    if nFacies < 9:
                        fName = 'F0' + str(nFacies+1)
                    elif nFacies >= 9:
                        fName = 'F' + str(nFacies+1)
                    fNameList.append(fName)
                    nFacies = nFacies  + 1
                    fTable[nFacies] = fName
                    if alphaFieldNumber >= 9:
                        alphaFieldName = 'GRF' + str(alphaFieldNumber)
                    else:
                        alphaFieldName = 'GRF0' + str(alphaFieldNumber)
                    gaussFieldsInZone.append(alphaFieldName)
                    alphaItem = [alphaFieldName, fName, 1.0, 0.0]
                    alphaList.append(alphaItem)
                    alphaFieldNumber = alphaFieldNumber + 1
#                        print(alphaList)
#                        print(backGroundFaciesList)
#                        print(faciesInZone)
#                        print(fTable)
                overlayGroups.append([alphaList,backGroundFaciesList])

        # Update facies in zone to include also overlay facies
        # Update main facies table to also be defined for all facies
        faciesInZone = fNameList
        mainFaciesTable = APSMainFaciesTable(fTable=fTable)                

        # Initialize truncation object with both background facies (in truncStructureList) and overlay facies (in overlayGroups)
        truncObj.initialize(mainFaciesTable, faciesInZone, gaussFieldsInZone,alphaFieldNameForBackGroundFacies,
                            truncStructureList, overlayGroups=overlayGroups, debug_level=self.debug_level)

        # Create equal facies probabilities for all defined facies.
        # NOTE: If truncation map is created when overlay facies in included, what is shown is the sum of probabilities 
        #       for background facies and overlay facies belonging to the group corresponding to the background facies that is shown.
        faciesProb = np.zeros(nFacies, np.float32)
        for i in range(nFacies):
            faciesProb[i] = 1.0/float(nFacies)
        truncObj.setTruncRule(faciesProb)
        return truncObj

        
    def removeTruncationRuleSettings(self,name):
        ''' Remove a truncation setting from dictionary'''
        try:
            del self.__tableCubic[name]
        except:
            try:
                del self.__tableNonCubic[name]
            except:
                raise KeyError('No truncation rule setting with name: {}'.format(name))

    def makeTruncationMapPlot(self, name):
        ''' Create truncation map plot using same probability for each facies'''
        truncObj = self.getTruncationRuleObject(name)
        faciesNames = truncObj.getFaciesInTruncRule()
        faciesProb = []
        nFacies = len(faciesNames)
        for i in range(nFacies):
            faciesProb.append(1.0/float(nFacies))
        truncObj.setTruncRule(faciesProb)
        faciesPolygons =  truncObj.truncMapPolygons()
        faciesIndxPerPolygon = truncObj.faciesIndxPerPolygon()
        faciesOrdering = truncObj.getFaciesOrderIndexList()


        # Truncation map is plotted
        fig = plt.figure(figsize=[2.0, 2.0],frameon=False)
        plt.axis('off')
        axTrunc = plt.subplot(1,1,1)
        colors = get_colors(nFacies)
        cmap_name = 'Colormap'

        # Create the colormap
        cm = matplotlib.colors.ListedColormap(colors, name=cmap_name, N=nFacies)
        bounds = np.linspace(0.5, 0.5 + nFacies, nFacies + 1)
        ticks = bounds
        labels = faciesNames
        colorNumberPerPolygon = []
        patches = []
        if self.debug_level >= Debug.VERBOSE:
            print('Debug output: Number of facies:          ' + str(nFacies))
            print('Debug output:Number of facies polygons: ' + str(len(faciesPolygons)))
        maxfIndx = 0
        colorForFacies = []
        for i in range(len(faciesPolygons)):
            indx = faciesIndxPerPolygon[i]
            fIndx = faciesOrdering[indx]
            poly = faciesPolygons[i]
            polygon = Polygon(poly, closed=True, facecolor=colors[fIndx])
            axTrunc.add_patch(polygon)
            fName = faciesNames[fIndx]
        axTrunc.set_title(name)
        axTrunc.set_aspect('equal', 'box')
        plotFileName = name + '.png'
        if self.__directory != '':
            plotFileName = self.__directory + '/' + name + '.png'
        print('Write file: {}'.format(plotFileName))
        fig.savefig(plotFileName)
        plt.close(fig)

    def __makeTruncationMapSubPlot(self, name, fig, Nrow, Ncol, indx):
        ''' Create truncation map plot using same probability for each facies'''
        truncObj = self.getTruncationRuleObject(name)
        faciesNames = truncObj.getFaciesInTruncRule()
        faciesProb = []
        nFacies = len(faciesNames)
        for i in range(nFacies):
            faciesProb.append(1.0/float(nFacies))
        truncObj.setTruncRule(faciesProb)
        faciesPolygons =  truncObj.truncMapPolygons()
        faciesIndxPerPolygon = truncObj.faciesIndxPerPolygon()
        faciesOrdering = truncObj.getFaciesOrderIndexList()


        # Truncation map is plotted
        plt.axis('off')
        axTrunc = plt.subplot(Nrow, Ncol, indx)
        colors = get_colors(nFacies)
        cmap_name = 'Colormap'

        # Create the colormap
        cm = matplotlib.colors.ListedColormap(colors, name=cmap_name, N=nFacies)
        bounds = np.linspace(0.5, 0.5 + nFacies, nFacies + 1)
        ticks = bounds
        labels = faciesNames
        colorNumberPerPolygon = []
        patches = []
        if self.debug_level >= Debug.SOMEWHAT_VERBOSE:
            print('Debug output: Number of facies:          ' + str(nFacies))
            print('Debug output: Number of facies polygons: ' + str(len(faciesPolygons)))
        maxfIndx = 0
        colorForFacies = []
        for i in range(len(faciesPolygons)):
            indx = faciesIndxPerPolygon[i]
            fIndx = faciesOrdering[indx]
            poly = faciesPolygons[i]
            polygon = Polygon(poly, closed=True, facecolor=colors[fIndx])
            axTrunc.add_patch(polygon)
            fName = faciesNames[fIndx]
        axTrunc.set_title(name)
#        axTrunc.set_aspect('equal', 'box')
#        plotFileName = name + '.png'
#        print('Write file: {}'.format(plotFileName))
#        fig.savefig(plotFileName)
#        plt.close(fig)

    def createAllCubicPlots(self):
        ''' Make truncation map plots for all specified settings for Cubic truncation rule in dictionarly'''
        for name, truncStructItem in self.__tableCubic.items():
            self.makeTruncationMapPlot(name)

    def createAllNonCubicPlots(self):
        ''' Make truncation map plots for all specified settings for NonCubic truncation rule in dictionarly'''
        for name, truncStructItem in self.__tableNonCubic.items():
            self.makeTruncationMapPlot(name)

    def createAllCubicXMLTemplates(self):
        ''' Make template xml files containing all Cubic truncation rule settings.'''
        for name, truncStructItem in self.__tableCubic.items():
            outputFileName = name + '.xml'
            if self.__directory != '':
                outputFileName = self.__directory + '/' + name + '.xml'
            self.writeTruncRuleToXmlFile(name, outputFileName)

    def createAllNonCubicXMLTemplates(self):
        ''' Make template xml files containing all NonCubic truncation rule settings.'''
        for name, truncStructItem in self.__tableNonCubic.items():
            outputFileName = name + '.xml'
            if self.__directory != '':
                outputFileName = self.__directory + '/' + name + '.xml'
            self.writeTruncRuleToXmlFile(name, outputFileName)


    def createAllCubicXMLTemplatesWithOverlayFacies(self):
        ''' Make template xml files containing all Cubic truncation rule settings with some default for overlay facies included.'''
        for name, truncStructItem in self.__tableCubic.items():
            outputFileName = name + '.xml'
            if self.__directory != '':
                outputFileName = self.__directory + '/' + name + '.xml'
            self.writeTruncRuleToXmlFileWithOverlayFacies(name, outputFileName)

    def createAllNonCubicXMLTemplatesWithOverlayFacies(self):
        ''' Make template xml files containing all NonCubic truncation rule settings with some default for overlay facies included.'''
        for name, truncStructItem in self.__tableNonCubic.items():
            outputFileName = name + '.xml'
            if self.__directory != '':
                outputFileName = self.__directory + '/' + name + '.xml'
            self.writeTruncRuleToXmlFileWithOverlayFacies(name, outputFileName)

            

    def createOverviewPlotCubic(self,plotName):
        ''' Create plots of all specified Cubic settings in one common plot'''
        Nrow = 5
        Ncol = 10
        indx = 1
        fig = plt.figure(figsize=[20.0, 10.0],frameon=False)
        for name, truncStructItem in self.__tableCubic.items():
            self.__makeTruncationMapSubPlot(name, fig, Nrow, Ncol, indx)
            indx = indx +1

        plotFileName = plotName + '.png'
        if self.__directory != '':
            plotFileName = self.__directory + '/' + plotName + '.png'
        print('Write file: {}'.format(plotFileName))
        plt.axis('off')
        fig.savefig(plotFileName)
        plt.close(fig)

    def createOverviewPlotNonCubic(self,plotName):
        ''' Create plots of all specified NonCubic settings in one common plot'''
        Nrow = 5
        Ncol = 10
        indx = 1
        fig = plt.figure(figsize=[20.0, 10.0],frameon=False)
        for name, truncStructItem in self.__tableNonCubic.items():
            self.__makeTruncationMapSubPlot(name, fig, Nrow, Ncol, indx)
            indx = indx +1
        
        plotFileName = plotName + '.png'
        if self.__directory != '':
            plotFileName = self.__directory + '/' + plotName + '.png'
            
        print('Write file: {}'.format(plotFileName))
        plt.axis('off')
        fig.savefig(plotFileName)
        plt.close(fig)

if __name__ == '__main__':
    truncRuleDir = 'truncRuleSettings'
    rules = DefineTruncationRule(truncRuleDir)
    rules.readFile('truncation_settings.dat')
    rules.writeFile('out1.dat')
#    name = 'C20H'
#    rules.makeTruncationMapPlot(name)
#    if rules.debug_level >= Debug.VERY_VERBOSE:
#        obj1.writeContentsInDataStructure()

#    print('')
#    name = 'N06'
#    rules.makeTruncationMapPlot(name)
#    if rules.debug_level >= Debug.VERY_VERBOSE:
#        obj2.writeContentsInDataStructure()

    # Create an new truncation rule settings
    direction = 'H'
    truncStructureCubic = rules.initNewTruncationRuleSettingsCubic(direction)
    faciesName='F01'
    probFrac = 1.0
    L1 = 1
    L2 = 1
    L3 = 0
    rules.addPolygonToTruncationRuleSettingsCubic(truncStructureCubic, faciesName, probFrac, L1, L2, L3)
    faciesName='F02'
    probFrac = 1.0
    L1 = 1
    L2 = 2
    L3 = 0
    rules.addPolygonToTruncationRuleSettingsCubic(truncStructureCubic, faciesName, probFrac, L1, L2, L3)
    faciesName='F03'
    probFrac = 1.0
    L1 = 1
    L2 = 3
    L3 = 0
    rules.addPolygonToTruncationRuleSettingsCubic(truncStructureCubic, faciesName, probFrac, L1, L2, L3)
    faciesName='F04'
    probFrac = 0.5
    L1 = 2
    L2 = 0
    L3 = 0
    rules.addPolygonToTruncationRuleSettingsCubic(truncStructureCubic, faciesName, probFrac, L1, L2, L3)
    faciesName='F05'
    probFrac = 0.8
    L1 = 3
    L2 = 1
    L3 = 1
    rules.addPolygonToTruncationRuleSettingsCubic(truncStructureCubic, faciesName, probFrac, L1, L2, L3)
    faciesName='F04'
    probFrac = 0.2
    L1 = 3
    L2 = 1
    L3 = 2
    rules.addPolygonToTruncationRuleSettingsCubic(truncStructureCubic, faciesName, probFrac, L1, L2, L3)
    faciesName='F05'
    probFrac = 0.2
    L1 = 3
    L2 = 1
    L3 = 3
    rules.addPolygonToTruncationRuleSettingsCubic(truncStructureCubic, faciesName, probFrac, L1, L2, L3)
    faciesName='F04'
    probFrac = 0.3
    L1 = 3
    L2 = 2
    L3 = 0
    rules.addPolygonToTruncationRuleSettingsCubic(truncStructureCubic, faciesName, probFrac, L1, L2, L3)

    name = 'C_test'
    rules.addTruncationRuleSettings(name, 'Cubic', truncStructureCubic)
    rules.writeFile('out2.dat')
    rules.makeTruncationMapPlot(name)

    truncStructureNonCubic = rules.initNewTruncationRuleSettingsNonCubic()
    faciesName='F01'
    probFrac = 0.5
    angle = 45.0
    rules.addPolygonToTruncationRuleSettingsNonCubic(truncStructureNonCubic, faciesName, angle, probFrac)
    
    faciesName='F02'
    probFrac = 1.0
    angle = -65.0
    rules.addPolygonToTruncationRuleSettingsNonCubic(truncStructureNonCubic, faciesName, angle, probFrac)

    faciesName='F01'
    probFrac = 0.5
    angle = -120.0
    rules.addPolygonToTruncationRuleSettingsNonCubic(truncStructureNonCubic, faciesName, angle, probFrac)
    
    faciesName='F03'
    probFrac = 1.0
    angle = 0.0
    rules.addPolygonToTruncationRuleSettingsNonCubic(truncStructureNonCubic, faciesName, angle, probFrac)

    name = 'N_test'
    rules.addTruncationRuleSettings(name, 'NonCubic', truncStructureNonCubic)
    rules.writeFile('out3.dat')
    rules.makeTruncationMapPlot(name)

    
#    rules.removeTruncationRuleSettings('C_test')
#    rules.removeTruncationRuleSettings('N_test')
#    rules.writeFile('out4.dat')

    # Create plots for all truncation settings
    rules.createAllCubicPlots()
    rules.createAllNonCubicPlots()
    rules.createOverviewPlotCubic('Cubic_rules')
    rules.createOverviewPlotNonCubic('NonCubic_rules')


#    rules.createAllNonCubicXMLTemplates()
    nGroups = 2
    nPolyPerGroup = 2
    rules.createAllCubicXMLTemplatesWithOverlayFacies()
    rules.createAllNonCubicXMLTemplatesWithOverlayFacies()
