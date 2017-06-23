#x!/bin/env python
# Python 3 script to read data from xml file with RMS information.

import sys
import copy
import numpy as np
import xml.etree.ElementTree as ET
from  xml.etree.ElementTree import Element, SubElement, dump
from xml.dom import minidom
#import importlib

import APSMainFaciesTable

#importlib.reload(APSMainFaciesTable)



def prettify(elem):
    rough_string = ET.tostring(elem,'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

# ----------------------------------------------------------------------------------
# APSDataFromRMS:
# Description: This class contain RMS data to be made available for the GUI script etc. RMS project data is collected
#              for both 3D grid model and for horizon data and facies data from wells.
#              NOTE: To limit and simplify this data collection, the user specify an XML file with a few keywords
#              specifying which grid model to scan and which well and log to scan to get facies data. 
#             
#
# Functions:
#     readRMSDataFromXMLFile(inputFileName)  - Read an already written XML with the RMS data. 
#                                              The input XML file is previously written by the function
#                                              scanRMSProjectAndWriteXMLFile.
#                                              This function is to be used e.g in the GUI script.
#     getFaciesTable()   - Get facies table which is defined in the RMS project by a selected facies log.
#     getGridModelName() - Get name of grid model to use.
#     getHorizonNames()  - Get list of all horizon names in the RMS project.
#     getGridSize()      - Get grid size and dimension for the 3D grid in the grid model.
#     getSurfaceSize()   - Get dimension and size of the 2D horizon maps.
#     getGridZoneNames() - Get list of zone names for the grid model.
#     getContinuousGridParamNames()  - Get list of all 3D parameters of continuous type belonging to the grid model.
#     getDiscreteGridParamNames()    - Get list of all 3D parameters of discrete type belonging to the grid model.
# --------------------------------------------------------------------------------------------                                             
class APSDataFromRMS:

    def __init__(self,printInfo=0):
        self.__propertyListContinuous = []
        self.__propertyListDiscrete   = []
        self.__projectName = ' '
        self.__projectSeed = 0
        self.__projectRealNumber = 0
        self.__gridModelName = ' '
        self.__zones = []
        self.__horizonNames = []
        self.__faciesTable = None

        self.__surf_nx = 0
        self.__surf_ny = 0
        self.__surf_xmin = 0
        self.__surf_xmax = 0
        self.__surf_ymin = 0
        self.__surf_ymax = 0
        self.__surf_xinc = 0
        self.__surf_yinc = 0
        self.__surf_rotation = 0

        self.__grid_nx = 0
        self.__grid_ny = 0
        self.__grid_x0 = 0
        self.__grid_y0 = 0
        self.__grid_xSize = 0
        self.__grid_ySize = 0
        self.__grid_xinc = 0
        self.__grid_yinc = 0
        self.__grid_asimuth = 0

        self.__printInfo = printInfo

        return


    def getFaciesTable(self):
        return copy.copy(self.__faciesTable)


    def getProjectName(self):
        return copy.copy(self.__projectName)


    def getProjectSeed(self):
        return self.__projectSeed

    def getProjectRealNumber(self):
        return self.__projectRealNumber

    def getGridModelName(self):
        return copy.copy(self.__gridModelName)

    def getHorizonNames(self):
        return copy.copy(self.__horizonNames)

    def getGridSize(self):
        return [self.__grid_nx, self.__grid_ny, self.__grid_x0, self.__grid_y0,
                self.__grid_xSize, self.__grid_ySize, self.__grid_xinc, self.__grid_yinc,
                self.__grid_asimuth]

    def getSurfaceSize(self):
        return [self.__surf_nx, self.__surf_ny, self.__surf_xmin, self.__surf_xmax,
                self.__surf_ymin, self.__surf_ymax, self.__surf_xinc, self.__surf_yinc,
                self.__surf_rotation]

    def getGridZoneNames(self):
        zoneNames = []
        for item in self.__zones:
            name = item[1]
            zoneNames.append(name)
        return zoneNames

    def getContinuousGridParamNames(self):
        return copy.copy(self.__propertyListContinuous)

    def getDiscreteGridParamNames(self):
        return copy.copy(self.__propertyListDiscrete)


    def readRMSDataFromXMLFile(self,inputFileName):
        tree = ET.parse(inputFileName)
        root = tree.getroot()

        kw = 'Project'
        prObj = root.find(kw)
        if prObj == None:
            print('Error: Missing keyword ' + kw)
            sys.exit()
        text = prObj.get('name')
        projectName = text.strip()
        self.__projectName = projectName

        kw = 'Seed'
        seedObj = prObj.find(kw)
        if seedObj == None:
            print('Error: Missing keyword ' + kw)
            sys.exit()
        text = seedObj.text
        projectSeed = int(text.strip())
        self.__projectSeed = projectSeed

        kw = 'RealisationNumber'
        realObj = prObj.find(kw)
        if realObj == None:
            print('Error: Missing keyword ' + kw)
            sys.exit()
        text = realObj.text
        projectRealNumber = int(text.strip())
        self.__projectRealNumber = projectRealNumber

            
        kw = 'GridModel'
        gmObj = root.find(kw)
        if gmObj == None:
            print('Error: Missing keyword ' + kw)
            sys.exit()
        text = gmObj.get('name')
        gridModelName = text.strip()
        self.__gridModelName = gridModelName

        propertyListContinuous = []
        propertyListDiscrete = []
        
        kw = 'Property'
        for probObj in gmObj.findall(kw):
            text = probObj.get('type')
            propType = text.strip()
            text = probObj.text
            propName = text.strip()
            if propType == 'Continuous':
                propertyListContinuous.append(propName)
            else:
                propertyListDiscrete.append(propName)

        self.__propertyListContinuous = propertyListContinuous
        self.__propertyListDiscrete   = propertyListDiscrete

        kw = 'ZoneName'
        zones = []
        for zNameObj in gmObj.findall(kw):
            text = zNameObj.get('number')
            zoneNumber = int(text.strip())
            text = zNameObj.text
            zoneName = text.strip()
            zones.append([zoneNumber,zoneName])
        self.__zones = zones

        kw2 = 'XSize'
        xsObj = gmObj.find(kw2)
        text = xsObj.text
        xSize = float(text.strip())
        self.__grid_xSize = xSize 

        kw2 = 'YSize'
        ysObj = gmObj.find(kw2)
        text = ysObj.text
        ySize = float(text.strip())
        self.__grid_ySize = ySize 
        
        kw2 = 'AsimuthAngle'
        asimuthObj = gmObj.find(kw2)
        text = asimuthObj.text
        asimuth = float(text.strip())
        self.__grid_asimuth = asimuth

        kw2 = 'OrigoX'
        origoXObj = gmObj.find(kw2)
        text = origoXObj.text
        origoX = float(text.strip())
        self.__grid_x0 = origoX

        kw2 = 'OrigoY'
        origoYObj = gmObj.find(kw2)
        text = origoYObj.text
        origoY = float(text.strip())
        self.__grid_y0 = origoY
        
        kw2 = 'NX'
        nxObj = gmObj.find(kw2)
        text = nxObj.text
        nx = int(text.strip())
        self.__grid_nx = nx
        
        kw2= 'NY'
        nyObj = gmObj.find(kw2)
        text = nyObj.text
        ny = int(text.strip())
        self.__grid_ny = ny
        
        kw2= 'Xinc'
        xincObj = gmObj.find(kw2)
        text = xincObj.text
        xinc = float(text.strip())
        self.__grid_xinc = xinc

        kw2= 'Yinc'
        yincObj = gmObj.find(kw2)
        text = yincObj.text
        yinc = float(text.strip())
        self.__grid_yinc = yinc
        

        kw = 'HorizonReference'
        hrObj = root.find(kw)
        if hrObj != None:
            text = hrObj.get('name')
            horizonRefName = text.strip()
            text = hrObj.get('type')
            horizonRefType = text.strip()


        kw = 'SurfaceTrendDimensions'
        surfObj = root.find(kw)
        if surfObj != None:
            kw2 = 'Xmin'
            xminObj = surfObj.find(kw2)
            text = xminObj.text
            xminSurface = float(text.strip())
            self.__surf_xmin =xminSurface

            kw2 = 'Xmax'
            xmaxObj = surfObj.find(kw2)
            text = xmaxObj.text
            xmaxSurface = float(text.strip())
            self.__surf_xmax =xmaxSurface

            kw2 = 'Ymin'
            yminObj = surfObj.find(kw2)
            text = yminObj.text
            yminSurface = float(text.strip())
            self.__surf_ymin =yminSurface

            kw2 = 'Ymax'
            ymaxObj = surfObj.find(kw2)
            text = ymaxObj.text
            ymaxSurface = float(text.strip())
            self.__surf_ymax =ymaxSurface

            kw2 = 'Rotation'
            rotObj = surfObj.find(kw2)
            text = rotObj.text
            rotationSurface = float(text.strip())
            self.__surf_rotation = rotationSurface

            kw2 = 'NX'
            nxSurfObj = surfObj.find(kw2)
            text = nxSurfObj.text
            nxSurface = int(text.strip())
            self.__surf_nx =nxSurface

            kw2 = 'NY'
            nySurfObj = surfObj.find(kw2)
            text = nySurfObj.text
            nySurface = int(text.strip())
            self.__surf_ny =nySurface

            kw2 = 'Xinc'
            xincSurfObj = surfObj.find(kw2)
            text = xincSurfObj.text
            xincSurface = float(text.strip())
            self.__surf_xinc =xincSurface

            kw2 = 'Yinc'
            yincSurfObj = surfObj.find(kw2)
            text = yincSurfObj.text
            yincSurface = float(text.strip())
            self.__surf_yinc =yincSurface

            kw = 'Horizon'
            horizonNames = []
            for hObj in root.findall(kw):
                text = hObj.text
                horizonNames.append(text.strip())
            self.__horizonNames = horizonNames
        faciesCodes = {}
        faciesTable = APSMainFaciesTable.APSMainFaciesTable(tree,inputFileName,self.__printInfo)
        self.__faciesTable = faciesTable


        return

    def printData(self):
        print('Project name: ' + self.__projectName)
        print('Project seed: ' + str(self.__projectSeed))
        print('Project realisation number: ' + str(self.__projectRealNumber))
        print('Grid model name: ' + self.__gridModelName)
        print('Grid zones: ')
        for item in self.__zones:
            zoneName   = item[1]
            zoneNumber = item[0]
            print('  ' + str(zoneNumber) + '  ' + zoneName)
        print(' ')
        print('Grid dimensions:')
        print('  NX:       ' +  str(self.__grid_nx))
        print('  NY:       ' +  str(self.__grid_ny))
        print('  XSize:    ' +  str(self.__grid_xSize))
        print('  YSize:    ' +  str(self.__grid_ySize))
        print('  Xinc:     ' +  str(self.__grid_xinc))
        print('  Yinc:     ' +  str(self.__grid_yinc))
        print('  Rotation: ' +  str(self.__grid_asimuth))
        print(' ')
        print('Property parameters: ')
        for propName in self.__propertyListContinuous:
            print('  ' + propName)
        for propName in self.__propertyListDiscrete:
            print('  ' + propName)
        print(' ')
        print('Horizon names: ')
        for hName in self.__horizonNames:
            print('  ' + hName)
        print(' ')
        print('Surface grid dimension:')
        print('  NX:       ' +  str(self.__surf_nx))
        print('  NY:       ' +  str(self.__surf_ny))
        print('  xmin:     ' +  str(self.__surf_xmin))
        print('  xmax:     ' +  str(self.__surf_xmax))
        print('  ymin:     ' +  str(self.__surf_ymin))
        print('  ymax:     ' +  str(self.__surf_ymax))
        print('  xinc:     ' +  str(self.__surf_xinc))
        print('  yinc:     ' +  str(self.__surf_yinc))
        print('  Rotation: ' +  str(self.__surf_rotation))
        print(' ')
        print('Facies table:')
        fTable = self.__faciesTable.getFaciesTable()
        for item in fTable:
            name = item[0]
            code = item[1]
            print('  ' + name + '  ' + str(code))


        return

