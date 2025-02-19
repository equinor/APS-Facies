#!/bin/env python
# -*- coding: utf-8 -*-
# Python 3 script to read data from xml file with RMS information.

import copy
import xml.etree.ElementTree as ET

from aps.algorithms.APSMainFaciesTable import APSMainFaciesTable
from aps.utils.constants.simple import Debug


class APSDataFromRMS:
    """
    This class contain RMS data to be made available for the GUI script etc. RMS project data is collected
    for both 3D grid model and for horizon data and facies data from wells.
    NOTE: To limit and simplify this data collection, the user specify an XML file with a few keywords
    specifying which grid model to scan and which well and log to scan to get facies data.

    Functions:
        readRMSDataFromXMLFile(inputFileName)  - Read an already written XML with the RMS data.
                                                 The input XML file is previously written by the function
                                                 scanRMSProjectAndWriteXMLFile.
                                                 This function is to be used e.g in the GUI script.
        getFaciesTable()   - Get facies table which is defined in the RMS project by a selected facies log.
        getHorizonNames()  - Get list of all horizon names in the RMS project.
        getGridSize()      - Get grid size and dimension for the 3D grid in the grid model.
        getSurfaceSize()   - Get dimension and size of the 2D horizon maps.
        getGridZoneNames() - Get list of zone names for the grid model.
        getContinuousGridParamNames()  - Get list of all 3D parameters of continuous type belonging to the grid model.
        getDiscreteGridParamNames()    - Get list of all 3D parameters of discrete type belonging to the grid model.
    """

    def __init__(self, debug_level=Debug.OFF):
        self.__data = {
            'Property list continuous': [],
            'Property list discrete': [],
            'Project name': '',
            'Project seed': 0,
            'Project realization number': 0,
            'Grid model name': '',
            'Zones': [],
            'Gauss field names': [],
            'Zone and region pairs': {},
            'Horizon names': [],
        }

        self.__keyword_mapping = {
            # The keys are the tags in the XML file, while the values are the names used internally in this class
            'Project': 'Project name',
            'Seed': 'Project seed',
            'RealisationNumber': 'Project realisation number',
            'GridModel': 'Grid model name',
            'ZoneName': 'Zones',
            'GaussFieldNames': 'Gauss field names',
            'ZoneAndRegionNumbers': 'Zone and region pairs',
            'Horizon': 'Horizon names',
            'NX': 'nx',
            'NY': 'ny',
            'Xmin': 'x min',
            'Xmax': 'x max',
            'Ymin': 'y min',
            'Ymax': 'y max',
            'Xinc': 'x inc',
            'Yinc': 'y inc',
            'Rotation': 'rotation',
            'OrigoX': 'x_0',
            'OrigoY': 'y_0',
            'XSize': 'x size',
            'YSize': 'y size',
            'AzimuthAngle': 'azimuth angle',
        }

        self.__faciesTable = None

        self.__surf = {
            'nx': 0,
            'ny': 0,
            'x min': 0,
            'x max': 0,
            'y min': 0,
            'y max': 0,
            'x inc': 0,
            'y inc': 0,
            'rotation': 0,
        }

        self.__grid = {
            'nx': 0,
            'ny': 0,
            'x_0': 0,
            'y_0': 0,
            'x size': 0,
            'y size': 0,
            'x inc': 0,
            'y inc': 0,
            'azimuth angle': 0,
        }

        self.__debug_level = debug_level

    def getFaciesTable(self):
        return copy.copy(self.__faciesTable)

    def getProjectName(self):
        return copy.copy(self.__data['Project name'])

    def getProjectSeed(self):
        return self.__data['Project seed']

    def getProjectRealNumber(self):
        return self.__data['Project realization number']

    @property
    def grid_model_name(self):
        """Get name of grid model to use."""
        return copy.copy(self.__data['Grid model name'])

    def getHorizonNames(self):
        return copy.copy(self.__data['Horizon names'])

    def getGridSize(self):
        order = [
            'nx',
            'ny',
            'x_0',
            'y_0',
            'x size',
            'y size',
            'x inc',
            'y inc',
            'azimuth angle',
        ]
        return [self.__grid[key] for key in order]

    def getSurfaceSize(self):
        order = [
            'nx',
            'ny',
            'x min',
            'x max',
            'y min',
            'y max',
            'x inc',
            'y inc',
            'rotation',
        ]
        return [self.__surf[key] for key in order]

    def getGridZoneNames(self):
        zoneNames = []
        for item in self.__data['Zones']:
            name = item[1]
            zoneNames.append(name)
        return zoneNames

    def getGaussFieldNames(self):
        return copy.copy(self.__data['Gauss field names'])

    def getZoneAndRegionNumbers(self):
        return self.__data['Zone and region pairs']

    def getNumberOfLayersInZone(self, zoneNumber):
        number_of_layer = 0
        for item in self.__data['Zones']:
            number = item[0]
            if number == zoneNumber:
                number_of_layer = item[2]
                break
        if number_of_layer == 0:
            raise ValueError(
                f'Zone number {zoneNumber} does not exist in grid model {self.grid_model_name()}'
            )
        return number_of_layer

    def getStartAndEndLayerInZone(self, zoneNumber):
        start_layer = 0
        end_layer = 0
        for item in self.__data['Zones']:
            number = item[0]
            if number == zoneNumber:
                start_layer = item[3]
                end_layer = item[4]
                break
        return [start_layer, end_layer]

    def getContinuousGridParamNames(self):
        return copy.copy(self.__data['Property list continuous'])

    def getDiscreteGridParamNames(self):
        return copy.copy(self.__data['Property list discrete'])

    def readRMSDataFromXMLFile(self, inputFileName):
        tree = ET.parse(inputFileName)
        root = tree.getroot()

        kw = 'Project'
        prObj = root.find(kw)
        projectName = None
        if prObj is None:
            if self.__debug_level >= Debug.VERBOSE:
                print('Keyword {} is not read'.format(kw))
        else:
            text = prObj.get('name')
            projectName = text.strip()
        self.__data[self.__keyword_mapping[kw]] = projectName

        if prObj is not None:
            kw = 'Seed'
            seedObj = prObj.find(kw)
            projectSeed = 0
            if seedObj is None:
                if self.__debug_level >= Debug.VERBOSE:
                    print('Keyword {} is not read'.format(kw))
            else:
                text = seedObj.text
                projectSeed = int(text.strip())
            self.__data['Project seed'] = projectSeed

            kw = 'RealisationNumber'
            realObj = prObj.find(kw)
            projectRealNumber = 0
            if realObj is None:
                if self.__debug_level >= Debug.VERBOSE:
                    print('Keyword {} is not read'.format(kw))
            else:
                text = realObj.text
                projectRealNumber = int(text.strip())
            self.__data['Project realization number'] = projectRealNumber

        kw = 'GridModel'
        gmObj = root.find(kw)
        if gmObj is None:
            raise ValueError('Error: Missing keyword {}'.format(kw))
        text = gmObj.get('name')
        gridModelName = text.strip()
        self.__data['Grid model name'] = gridModelName

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

        self.__data['Property list continuous'] = propertyListContinuous
        self.__data['Property list discrete'] = propertyListDiscrete

        kw = 'ZoneName'
        zones = []
        for zNameObj in gmObj.findall(kw):
            text = zNameObj.get('number')
            zoneNumber = int(text.strip())
            text = zNameObj.get('nLayers')
            nLayers = int(text.strip())
            text = zNameObj.get('start')
            start = int(text.strip())
            text = zNameObj.get('end')
            end = int(text.strip())
            text = zNameObj.text
            zoneName = text.strip()
            zones.append([zoneNumber, zoneName, nLayers, start, end])
        self.__data['Zones'] = zones

        kw = 'GaussFieldNames'
        gfNames = []
        for gfNameObj in gmObj.findall(kw):
            text = gfNameObj.text
            gfNames.append(text.strip())
        self.__data['Gauss field names'] = gfNames

        kw = 'ZoneAndRegionNumbers'
        zoneAndRegionNumbers = {}
        for zrNumbersObj in gmObj.findall(kw):
            text = zrNumbersObj.get('zoneNumber')
            zoneNumber = int(text.strip())
            text = zrNumbersObj.get('regionNumber')
            regionNumber = int(text.strip())
            # The dictionary contain keys that are zone and region pairs
            key = (zoneNumber, regionNumber)
            zoneAndRegionNumbers[key] = 1
        self.__data['Zone and region pairs'] = zoneAndRegionNumbers

        # Get keywords for variables that are float
        keywords = [
            'XSize',
            'YSize',
            'AzimuthAngle',
            'OrigoX',
            'OrigoY',
            'Xinc',
            'Yinc',
        ]
        for key in keywords:
            self.__add_grid(key, 'float', gmObj)

        # Get keywords for variables that are int
        keywords = ['NX', 'NY']
        for key in keywords:
            self.__add_grid(key, 'int', gmObj)

        kw = 'HorizonReference'
        hrObj = root.find(kw)
        horizonRefName = None
        horizonRefType = None
        if hrObj is not None:
            text = hrObj.get('name')
            horizonRefName = text.strip()
            text = hrObj.get('type')
            horizonRefType = text.strip()

        kw = 'SurfaceTrendDimensions'
        surfObj = root.find(kw)
        if surfObj is not None:
            # Add keywords for variables of type float
            keywords = ['Xmin', 'Xmax', 'Ymin', 'Ymax', 'Rotation', 'Xinc', 'Yinc']
            for key in keywords:
                self.__add_surfaces(key, 'float', surfObj)

            # Add keywords for variables of type int
            keywords = ['NX', 'NY']
            for key in keywords:
                self.__add_surfaces(key, 'int', surfObj)

            kw = 'Horizon'
            horizonNames = []
            for hObj in root.findall(kw):
                text = hObj.text
                horizonNames.append(text.strip())
            self.__data['Horizon names'] = horizonNames

        fTableObj = root.find('MainFaciesTable')
        faciesTable = None
        if fTableObj is not None:
            faciesTable = APSMainFaciesTable(
                tree, modelFileName=inputFileName, debug_level=self.__debug_level
            )
        self.__faciesTable = faciesTable

    def __add_surfaces(self, kw, value_type, surface):
        self.__add_to_object(kw, value_type, surface, self.__surf)

    def __add_grid(self, kw, value_type, grid):
        self.__add_to_object(kw, value_type, grid, self.__grid)

    def __add_to_object(self, keyword, value_type, root, storage_object):
        item = root.find(keyword)
        if item is None:
            raise ValueError('Missing keyword {}'.format(keyword))
        text = item.text
        if value_type == 'float':
            value = float(text.strip())
        elif value_type == 'int':
            value = int(text.strip())
        key = self.__keyword_mapping[keyword]
        storage_object[key] = value

    def printData(self):
        print('Project name: ' + self.__data['Project name'])
        print('Project seed: ' + str(self.__data['Project seed']))
        print(
            'Project realisation number: '
            + str(self.__data['Project realization number'])
        )
        print('Grid model name: ' + self.__data['Grid model name'])
        print('Grid zones:')
        for item in self.__data['Zones']:
            zoneName = item[1]
            zoneNumber = item[0]
            nLayers = item[2]
            print(
                '  Zone number: {0} Zone name: {1}  Number of layers: {2}'.format(
                    str(zoneNumber), zoneName, str(nLayers)
                )
            )
        print('')
        print('Grid dimensions:')
        print('  NX:       ' + str(self.__grid['nx']))
        print('  NY:       ' + str(self.__grid['ny']))
        print('  XSize:    ' + str(self.__grid['x size']))
        print('  YSize:    ' + str(self.__grid['y size']))
        print('  Xinc:     ' + str(self.__grid['x inc']))
        print('  Yinc:     ' + str(self.__grid['y inc']))
        print('  Rotation: ' + str(self.__grid['azimuth angle']))
        print('')
        print('Property parameters:')
        for propName in self.__data['Property list continuous']:
            print('  ' + propName)
        for propName in self.__data['Property list discrete']:
            print('  ' + propName)
        print('')
        print('Horizon names:')
        for hName in self.__data['Horizon names']:
            print('  ' + hName)
        print('')
        print('Surface grid dimension:')
        print('  NX:       ' + str(self.__surf['nx']))
        print('  NY:       ' + str(self.__surf['ny']))
        print('  xmin:     ' + str(self.__surf['x min']))
        print('  xmax:     ' + str(self.__surf['x max']))
        print('  ymin:     ' + str(self.__surf['y min']))
        print('  ymax:     ' + str(self.__surf['y max']))
        print('  xinc:     ' + str(self.__surf['x inc']))
        print('  yinc:     ' + str(self.__surf['y inc']))
        print('  Rotation: ' + str(self.__surf['rotation']))
        print('')
        print('Facies table:')
        fTable = self.__faciesTable.getFaciesTable()
        for item in fTable:
            name = item[0]
            code = item[1]
            print('  ' + name + '  ' + str(code))
