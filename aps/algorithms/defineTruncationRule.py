#!/bin/env python
# -*- coding: utf-8 -*-
# --------------------------------------------------------
# class DefineTruncationRule
# Description: Handle truncation rule settings
# --------------------------------------------------------
import os
from pathlib import Path
from sys import argv

import copy
import collections
import numpy as np

from matplotlib import pyplot as plt
from matplotlib.patches import Polygon

from aps.algorithms.truncation_rules import Trunc3D_bayfill, Trunc2D_Angle, Trunc2D_Cubic
from aps.utils.constants.simple import Debug
from aps.algorithms.APSMainFaciesTable import APSMainFaciesTable
from aps.algorithms.constants_truncation_rules import (
    OverlayGroupIndices, OverlayPolygonIndices, CubicPolygonIndices,
    NonCubicPolygonIndices, CubicAndOverlayIndices, NonCubicAndOverlayIndices
)
from aps.utils.methods import get_colors
from aps.utils.xmlUtils import prettify

from xml.etree.ElementTree import Element


def conditional_directory(name):
    path = Path(name)
    if not path.exists():
        os.mkdir(name)

    def wrapper(func):
        def inner_wrapper(self, *args, **kwargs):
            old = self._DefineTruncationRule__directory
            if self.write_to_directories:
                self._DefineTruncationRule__directory = name
            result = func(self, *args, **kwargs)
            self._DefineTruncationRule__directory = old
            return result
        return inner_wrapper
    return wrapper


class DefineTruncationRule:
    """
    This class read truncation rule settings for Cubic or NonCubic truncation rules
    from file and can create objects of type Trunc2D_Cubic_xml or Trunc2D_Angle_xml.
    The purpose of the class is to:
    - enable GUI to read predefined truncation rule settings from file
    - enable GUI to write user defined truncation rule settings to file
    - enable GUI to create mini pictures (icons) for truncation rule settings
    """

    def __init__(
            self,
            directory='',
            debug_level=Debug.VERBOSE,
            show_title=True,
            write_overlay=True,
            write_overview=True,
            write_to_directories=False,
    ):
        ''' Dictionaries for Cubic and NonCubic settings and Cubic and NonCubic with overlay truncation settings.
            Data structure:
            Background truncation model of type 'Cubic':
               truncStructBGCubic = [direction, polygon, polygon, polygon, ...]
               direction is 'V' or 'H'
               polygon = [faciesName, probabilityFraction, L1, L2, L3]
               where probability fraction summed over all polygons with same facies name must be 1.0
               L1, L2, L3 are integer values >= 0 and define hierarchical levels for subdivision
               of unit square into rectangular polygons.They are sorted in increasing order,
               first for L1 level, then for L2 level given L1 level and finally for L3 level given L1 and L2 level.

               Constants used for indexing:
               FACIES_NAME_INDX = CubicPolygonIndices.FACIES_NAME_INDX
               PROB_FRAC_INDX   = CubicPolygonIndices.PROB_FRAC_INDX
               L1_INDX          = CubicPolygonIndices.L1_INDX
               L2_INDX          = CubicPolygonIndices.L2_INDX
               L3_INDX          = CubicPolygonIndices.L3_INDX

               Accessing elements:
               faciesName  = polygon[FACIES_NAME_INDX]
               probFrac    = polygon[PROB_FRAC_INDX]
               L1          = polygon[L1_INDX]
               L2          = polygon[L2_INDX]
               L3          = polygon[L3_INDX]

            Background truncation model of type 'NonCubic':
               truncStructBGCubic = [polygon, polygon, polygon, ...]
               polygon = [faciesName, orientationAngle, probabilityFraction]
               where orientationAngle is in interval [0, 360.0] degrees,
               and probabilityFraction must sum up to 1.0 for all polygons with the same facies.

               Constants used for indexing:
               FACIES_NAME_INDX = NonCubicPolygonIndices.FACIES_NAME_INDX
               ANGLE_INDX       = NonCubicPolygonIndices.ANGLE_INDX
               PROB_FRAC_INDX   = NonCubicPolygonIndices.PROB_FRAC_INDX

               Accessing elements:
               faciesName  = polygon[FACIES_NAME_INDX]
               angle       = polygon[ANGLE_INDX]
               probFrac    = polygon[PROB_FRAC_INDX]

            Overlay truncation model:
               overlayGroups = [groupItem, groupItem, groupItem, ...]
               groupItem     = [alphaList, backgroundFaciesList]
               alphaList     = [overlayPolygon, overlayPolygon, ...]
               backgroundFaciesList = [backgroundFaciesName, backgroundFaciesName, ...]
               overlayPolygon = [alphaName, overlayFaciesName, probabilityFraction, centerInterval]
               where backgroundFaciesName is facies name of background model.
               The background facies define over which facies from the background model the
               overlay facies will be located.
               alphaName is name of alpha field to be used in truncation rule to define
               overlay facies for the group. The probabilityFraction must sum up to 1.0 over all
               overlayPolygons having the same overlay facies name. The variable centerInterval is a value in
               interval [0.0, 1.0] and define the centerpoint of the truncation interval which define
               that overlay facies is to be assigned.

               Constants used for indexing:
               ALPHA_LIST_INDX      = OverlayGroupIndices.ALPHA_LIST_INDX
               BACKGROUND_LIST_INDX = OverlayGroupIndices.BACKGROUND_LIST_INDX

               ALPHA_NAME_INDX      = OverlayPolygonIndices.ALPHA_NAME_INDX
               FACIES_NAME_INDX     = OverlayPolygonIndices.FACIES_NAME_INDX
               PROB_FRAC_INDX       = OverlayPolygonIndices.PROB_FRAC_INDX
               CENTER_INTERVAL_INDX = OverlayPolygonIndices.CENTER_INTERVAL_INDX

               Accessing elements:
               groupItem = overlayGroups[indx]
               alphaList            = groupItem[ALPHA_LIST_INDX]
               backgroundFaciesList = groupItem[BACKGROUND_LIST_INDX]
               overlayPolygon       = alphaList[indx]
               alphaName            = overlayPolygon[ALPHA_NAME_INDX]
               overlayFaciesName    = overlayPolygon[FACIES_NAME_INDX]
               probabilityFraction  = overlayPolygon[PROB_FRAC_INDX]
               centerInterval       = overlayPolygon[CENTER_INTERVAL_INDX]

            Truncationrule with both background model of type Cubic and Overlay truncation.
              itemCubicOverlay = [nameBG, nameOL, itemCubic, overlayGroups]
              where nameBG is name of settings for cubic background model, nameOL is name of overlay settings,
              itemCubic = self._tableCubic[nameBG], overlayGroups = self.__tableOverlay[nameOL].
              Constants uses for indexing:
              NAME_BG_INDX = CubicAndOverlayIndices.NAME_BG_INDX
              NAME_OL_INDX =  CubicAndOverlayIndices.NAME_OL_INDX
              STRUCT_CUBIC_INDX = CubicAndOverlayIndices.STRUCT_CUBIC_INDX
              OVERLAYGROUP_INDX = CubicAndOverlayIndices.OVERLAYGROUP_INDX

              Accessing elemenents:
              itemCubicOverlay = [ nameBG, nameOL,  itemCubic, overlayGroups]
              nameBG = itemCubicOverlay[NAME_BG_INDX]
              nameOL = itemCubicOverlay[NAME_OL_INDX]
              itemCubic = itemCubicOverlay[STRUCT_CUBIC_INDX]
              overlayGroups = itemCubicOverlay[OVERLAYGROUP_INDX]

            Truncationrule with both background model of type NonCubic and Overlay truncation.
              itemNonCubicOverlay = [nameBG, nameOL, itemNonCubic, overlayGroups]
              where nameBG is name of settings for cubic background model, nameOL is name of overlay settings,
              itemNonCubic = self._tableNonCubic[nameBG], overlayGroups = self.__tableOverlay[nameOL].
              Constants uses for indexing:
              NAME_BG_INDX = NonCubicAndOverlayIndices.NAME_BG_INDX
              NAME_OL_INDX =  NonCubicAndOverlayIndices.NAME_OL_INDX
              STRUCT_CUBIC_INDX = NonCubicAndOverlayIndices.STRUCT_NONCUBIC_INDX
              OVERLAYGROUP_INDX = NonCubicAndOverlayIndices.OVERLAYGROUP_INDX

              Accessing elemenents:
              itemNonCubicOverlay = [ nameBG, nameOL,  itemNonCubic, overlayGroups]
              nameBG = itemNonCubicOverlay[NAME_BG_INDX]
              nameOL = itemNonCubicOverlay[NAME_OL_INDX]
              itemNonCubic = itemNonCubicOverlay[STRUCT_NONCUBIC_INDX]
              overlayGroups = itemNonCubicOverlay[OVERLAYGROUP_INDX]
        '''
        self.__tableBayfill = {}

        # Table Cubic contains items of type Cubic which is a truncation model for background facies.
        # An item = [direction, polygon, polygon, polygon, ...]
        # where polygon = [faciesName, probabilityFraction, L1, L2, L3]
        # The key is name of the truncation rule setting.
        self.__tableCubic = {}

        # Table NonCubic contains elements of type NonCubic which is a truncation model for background facies.
        # An item = [polygon, polygon, ...]
        # where polygon = [faciesName, orientationAngle, probabilityFraction]
        # The key is name of the truncation rule setting.
        self.__tableNonCubic = {}

        # Table Overlay contains items of type Overlay which is a truncation model for overlay facies.
        # An item = overlayGroups = [groupItem, groupItem, ...] where
        # groupItem = [alphaList, backgroundFaciesList] where
        # alphaList = [ overlayPolygon, overlayPolygon, ...] where
        # overlayPolygon = [alphaName, overlayFaciesName, probabilityFraction, centerInterval]
        self.__tableOverlay = {}

        # Table CubicAndOverlay contains items for truncation models with Cubic background model and an Overlay model.
        # An item = [nameBG, nameOL, cubicTruncItem, overlayTruncItem] where
        # nameBG is name of Cubic type setting and refer to an item with key=nameBG in tableCubic.
        # nameOL is name of Overlay type setting and refer to an item with key=nameOL in tableOverlay.
        # cubicTruncItem = self.__tableCubic[nameBG]
        # overlayTruncItem = self.__tableOverlay[nameOL]
        self.__tableCubicAndOverlay = {}

        # Table NonCubicAndOverlay contains items for truncation models with NonCubic background model and an Overlay model.
        # An item = [nameBG, nameOL, nonCubicTruncItem, overlayTruncItem] where
        # nameBG is name of NonCubic type setting and refer to an item with key=nameBG in tableNonCubic.
        # nameOL is name of Overlay type setting and refer to an item with key=nameOL in tableOverlay.
        # nonCubicTruncItem = self.__tableNonCubic[nameBG]
        # overlayTruncItem = self.__tableOverlay[nameOL]
        self.__tableNonCubicAndOverlay = {}

        self.__inputFileName = None
        self.debug_level = debug_level
        self.__directory = directory
        self.show_title = show_title
        self.write_overlay = write_overlay
        self.write_overview = write_overview
        self.write_to_directories = write_to_directories

    def readFile(self, inputFileName):
        ''' Read ascii file with definition of truncation rule settings for background facies.'''

        self.__inputFileName = copy.copy(inputFileName)
        finished = False
        print('Read file with truncation rules: {}'.format(inputFileName))
        if self.__directory:
            inputFile = self.__directory + '/' + self.__inputFileName
        else:
            inputFile = self.__inputFileName
        with open(inputFile, 'r', encoding='utf-8') as file:
            while not finished:
                line = file.readline()
                if line == '':
                    finished = True
                else:
                    words = line.split()
                    if len(words) > 0 and words[0] != '#':
                        ruleType = words[0]

                        if ruleType == 'Bayfill':
                            name = words[1]
                            truncStructureBayfill = self.__getTruncSettingsBayfillFromFile(words)
                            self.__tableBayfill[name] = truncStructureBayfill
                        elif ruleType == 'Cubic':
                            name = words[1]
                            truncStructureCubic = self.__getTruncSettingsCubicFromFile(words)
                            self.__tableCubic[name] = truncStructureCubic
                        elif ruleType == 'NonCubic':
                            name = words[1]
                            truncStructureNonCubic = self.__getTruncSettingsNonCubicFromFile(words)
                            self.__tableNonCubic[name] = truncStructureNonCubic
                        elif ruleType == 'Overlay':
                            name = words[1]
                            overlayGroups = self.__getTruncSettingsOverlayFromFile(words)
                            self.__tableOverlay[name] = overlayGroups
                        elif ruleType == 'CubicAndOverlay':
                            name = words[1]
                            nameBG = words[2]
                            nameOL = words[3]
                            truncStructureCubic = self.__tableCubic[nameBG]
                            overlayGroups = self.__tableOverlay[nameOL]
                            item = [nameBG, nameOL, truncStructureCubic, overlayGroups]
                            self.__tableCubicAndOverlay[name] = item
                        elif ruleType == 'NonCubicAndOverlay':
                            name = words[1]
                            nameBG = words[2]
                            nameOL = words[3]
                            truncStructureNonCubic = self.__tableNonCubic[nameBG]
                            overlayGroups = self.__tableOverlay[nameOL]
                            item = [nameBG, nameOL, truncStructureNonCubic, overlayGroups]
                            self.__tableNonCubicAndOverlay[name] = item
                        else:
                            print('File format error in  {}'.format(inputFile))
                            raise IOError('File format error in  {}'.format(inputFile))

    def writeFile(self, outputFileName):
        ''' Write dictionaries with truncation rule settings to file for background facies and overlay facies.'''
        if self.__directory:
            outputFile = self.__directory + '/' + outputFileName
        else:
            outputFile = outputFileName
        if self.debug_level >= Debug.VERBOSE:
            print('Debug output: Write file with truncation rules: {}'.format(outputFile))

        with open(outputFile, 'w', encoding='utf-8') as file:

            sortedDictionaryCubic = collections.OrderedDict(sorted(self.__tableCubic.items()))

            # for name, truncStructItem in self.__tableCubic.items():
            for name, truncStructItem in sortedDictionaryCubic.items():
                nPoly = len(truncStructItem) - 1
                outString = 'Cubic ' + name + ' ' + str(nPoly) + ' '
                outString = outString + ' ' + str(truncStructItem)
                file.write(outString)
                file.write('\n')

            sortedDictionaryNonCubic = collections.OrderedDict(sorted(self.__tableNonCubic.items()))

            # for name, truncStructItem in self.__tableNonCubic.items():
            for name, truncStructItem in sortedDictionaryNonCubic.items():
                nPoly = len(truncStructItem)
                outString = 'NonCubic ' + name + ' ' + str(nPoly) + ' '
                outString = outString + ' ' + str(truncStructItem)
                file.write(outString)
                file.write('\n')

            ALPHA_LIST_INDX = OverlayGroupIndices.ALPHA_LIST_INDX
            BACKGROUND_LIST_INDX = OverlayGroupIndices.BACKGROUND_LIST_INDX
            sortedDictionaryOverlay = collections.OrderedDict(sorted(self.__tableOverlay.items()))
            # for name, overlayGroups in self.__tableOverlay.items():
            for name, overlayGroups in sortedDictionaryOverlay.items():
                nGroups = len(overlayGroups)
                outString = 'Overlay ' + name + ' ' + str(nGroups) + ' '
                for n in range(nGroups):
                    overlayGroupItem = overlayGroups[n]
                    alphaList = overlayGroupItem[ALPHA_LIST_INDX]
                    bgFaciesList = overlayGroupItem[BACKGROUND_LIST_INDX]
                    nPoly = len(alphaList)
                    nBGFacies = len(bgFaciesList)
                    outString = outString + ' ' + str(nPoly) + ' ' + str(nBGFacies)
                outString = outString + ' ' + str(overlayGroups)
                file.write(outString)
                file.write('\n')

            NAME_BG_INDX = CubicAndOverlayIndices.NAME_BG_INDX
            NAME_OL_INDX = CubicAndOverlayIndices.NAME_OL_INDX
            sortedDictionaryCubicAndOverlay = collections.OrderedDict(sorted(self.__tableCubicAndOverlay.items()))
            # for name, truncStructItemWithOverlay in self.__tableCubicAndOverlay.items():
            for name, truncStructItemWithOverlay in sortedDictionaryCubicAndOverlay.items():
                nameBG = truncStructItemWithOverlay[NAME_BG_INDX]
                nameOL = truncStructItemWithOverlay[NAME_OL_INDX]
                outString = 'CubicAndOverlay' + ' ' + name + '  ' + nameBG + ' ' + nameOL
                file.write(outString)
                file.write('\n')

            NAME_BG_INDX = NonCubicAndOverlayIndices.NAME_BG_INDX
            NAME_OL_INDX = NonCubicAndOverlayIndices.NAME_OL_INDX
            sortedDictionaryNonCubicAndOverlay = collections.OrderedDict(sorted(self.__tableNonCubicAndOverlay.items()))
            # for name, truncStructItemWithOverlay in self.__tableNonCubicAndOverlay.items():
            for name, truncStructItemWithOverlay in sortedDictionaryNonCubicAndOverlay.items():
                nameBG = truncStructItemWithOverlay[NAME_BG_INDX]
                nameOL = truncStructItemWithOverlay[NAME_OL_INDX]
                outString = 'NonCubicAndOverlay' + ' ' + name + '  ' + nameBG + ' ' + nameOL
                file.write(outString)
                file.write('\n')

    def __getTruncSettingsBayfillFromFile(self, words):
        print(words)
        num_polygons = int(words[2])
        truncItem = []
        offset = 3

        def strip(word):
            return word.strip(',').replace('[', '').replace(']', '').strip('\'"')

        for i in range(num_polygons):
            facies = words[offset + i]
            polygon = [strip(facies)]
            if ']' not in facies:
                # That is, a slant factor must be extracted
                factor = strip(words[offset + i + 1])
                value = float(strip(words[offset + i + 2]))
                polygon.extend([factor, value])
                offset += 2
            truncItem.append(polygon)
        return truncItem

    def __getTruncSettingsCubicFromFile(self, words):
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

            n = len(words[m + 1])
            probFrac = float(words[m + 1][:n - 1])

            n = len(words[m + 2])
            L1 = int(words[m + 2][:n - 1])

            n = len(words[m + 3])
            L2 = int(words[m + 3][:n - 1])

            n = len(words[m + 4])
            L3 = int(words[m + 4][:n - 2])

            m = m + 5
            polygonItem = [faciesName, probFrac, L1, L2, L3]
            truncItem.append(polygonItem)

        return truncItem

    def __getTruncSettingsNonCubicFromFile(self, words):
        ''' Read details about NonCubic truncation rule settings. Is used in function to read settings'''
        nPoly = int(words[2])
        truncItem = []

        m = 3
        for i in range(nPoly):
            if i == 0:
                faciesName = copy.copy(words[m][3:6])
            else:
                faciesName = copy.copy(words[m][2:5])
            n = len(words[m + 1])
            angle = float(words[m + 1][:n - 1])

            n = len(words[m + 2])
            probFrac = float(words[m + 2][:n - 2])

            m = m + 3
            polygonItem = [faciesName, angle, probFrac]
            truncItem.append(polygonItem)

        return truncItem

    def __getTruncSettingsOverlayFromFile(self, words):
        ''' Read details about overlay facies truncation rule settings. Is used in function to read settings'''
        nGroups = int(words[2])
        nPolyInGroup = []
        nBackgroundFaciesInGroup = []
        m = 3
        for n in range(nGroups):
            nPolyInGroup.append(int(words[m]))
            m = m + 1
            nBackgroundFaciesInGroup.append(int(words[m]))
            m = m + 1

        overlayGroups = []
        for n in range(nGroups):
            alphaList = []
            bgFaciesList = []
            for i in range(nPolyInGroup[n]):
                # Read facies, alpha field, probFrac and center point of truncation interval for each polygon in group
                if i > 0:
                    alphaFieldName = words[m][2:7]
                else:
                    if n == 0:
                        alphaFieldName = words[m][5:10]
                    else:
                        alphaFieldName = words[m][4:9]
                m = m + 1

                fName = words[m][1:4]
                m = m + 1

                wlen = len(words[m])
                probFrac = float(words[m][:wlen - 1])
                m = m + 1

                wlen = len(words[m])
                if i == (nPolyInGroup[n] - 1):
                    centerPoint = float(words[m][:wlen - 3])
                else:
                    centerPoint = float(words[m][:wlen - 2])
                m += 1

                alphaItem = [alphaFieldName, fName, probFrac, centerPoint]
                alphaList.append(alphaItem)

            # Read background facies for the group
            for k in range(nBackgroundFaciesInGroup[n]):
                if k == 0:
                    bgFaciesName = copy.copy(words[m][2:5])
                else:
                    bgFaciesName = copy.copy(words[m][1:4])
                m = m + 1
                bgFaciesList.append(bgFaciesName)

            overlayGroups.append([alphaList, bgFaciesList])

        return overlayGroups

    def getTruncationRuleObject(self, name):
        ''' Get truncation rule settings with given name.
            Create a truncation rule object with correct type.
            Facies names and Gauss field names are given default values.
            The default facies names are those specified in the settings for the truncation rule.
        '''
        itemBayfill = None
        itemCubic = None
        itemNonCubic = None
        itemCubicOverlay = None
        itemNonCubicOverlay = None
        try:
            itemCubic = self.__tableCubic[name]
        except KeyError:
            try:
                itemNonCubic = self.__tableNonCubic[name]
            except KeyError:
                try:
                    itemCubicOverlay = self.__tableCubicAndOverlay[name]
                except KeyError:
                    try:
                        itemNonCubicOverlay = self.__tableNonCubicAndOverlay[name]
                    except KeyError:
                        try:
                            itemBayfill = self.__tableBayfill[name]
                        except KeyError:
                            return None

        if itemBayfill is not None:
            truncObj = Trunc3D_bayfill()
            mainFaciesTable, faciesInZone, gaussFieldsInZone, alphaFieldNameForBackGroundFacies = self.__background(itemBayfill, 'Bayfill')
            truncObj.initialize(
                mainFaciesTable,
                faciesInZone,
                [polygon[0] for polygon in itemBayfill],
                gaussFieldsInZone,
                alphaFieldNameForBackGroundFacies,
                itemBayfill[0][2], '', False,
                itemBayfill[1][2], False,
                itemBayfill[3][2], False,
                1,
            )

        if itemCubic is not None:
            if self.debug_level >= Debug.VERBOSE:
                print('Debug output: Create truncation object of type Cubic from truncation setting with name: {}'.format(name))
            truncStructureList = itemCubic
            mainFaciesTable, faciesInZone, gaussFieldsInZone, alphaFieldNameForBackGroundFacies = self.__background(truncStructureList, 'Cubic')
            overlayGroups = None
            truncObj = Trunc2D_Cubic()
            truncObj.initialize(mainFaciesTable, faciesInZone, gaussFieldsInZone, alphaFieldNameForBackGroundFacies,
                                truncStructureList, overlayGroups=overlayGroups, debug_level=self.debug_level)

        if itemCubicOverlay is not None:
            if self.debug_level >= Debug.VERBOSE:
                print('Debug output: Create truncation object of type Cubic with overlay facies from truncation setting with name: {}'.format(name))

            NAME_BG_INDX = CubicAndOverlayIndices.NAME_BG_INDX
            NAME_OL_INDX = CubicAndOverlayIndices.NAME_OL_INDX
            STRUCT_CUBIC_INDX = CubicAndOverlayIndices.STRUCT_CUBIC_INDX
            OVERLAYGROUP_INDX = CubicAndOverlayIndices.OVERLAYGROUP_INDX

            truncStructureList = itemCubicOverlay[STRUCT_CUBIC_INDX]
            overlayGroups = itemCubicOverlay[OVERLAYGROUP_INDX]

            mainFaciesTable, faciesInZone, gaussFieldsInZone, alphaFieldNameForBackGroundFacies = self.__background(truncStructureList, 'Cubic')
            if self.__checkOverlayFacies(faciesInZone, overlayGroups):
                gaussFieldsInZone, faciesInZone = self.__updateGaussFieldNamesandFaciesInZoneForOverlay(overlayGroups, gaussFieldsInZone, faciesInZone)
                truncObj = Trunc2D_Cubic()
                truncObj.initialize(mainFaciesTable, faciesInZone, gaussFieldsInZone, alphaFieldNameForBackGroundFacies,
                                    truncStructureList, overlayGroups=overlayGroups, debug_level=self.debug_level)
            else:
                raise IOError(
                    'Inconsistent facies specification for truncation rulw with overlay facies.'
                    'Either: specified background facies for overlay facies groups is not defined in background facies truncation rule.'
                    'Or: specified overlay facies is equal to background facies'
                )

        if itemNonCubic is not None:
            if self.debug_level >= Debug.VERBOSE:
                print('Debug output: Create truncation object of type NonCubic from truncation setting with name: {}'.format(name))
            truncStructureList = itemNonCubic
            mainFaciesTable, faciesInZone, gaussFieldsInZone, alphaFieldNameForBackGroundFacies = self.__background(truncStructureList, 'NonCubic')
            overlayGroups = None
            truncObj = Trunc2D_Angle()
            truncObj.initialize(mainFaciesTable, faciesInZone, gaussFieldsInZone, alphaFieldNameForBackGroundFacies,
                                truncStructureList, overlayGroups=overlayGroups, debug_level=self.debug_level)

        if itemNonCubicOverlay is not None:
            if self.debug_level >= Debug.VERBOSE:
                print('Debug output: Create truncation object of type NonCubic with overlay facies from truncation setting with name: {}'.format(name))

            NAME_BG_INDX = NonCubicAndOverlayIndices.NAME_BG_INDX
            NAME_OL_INDX = NonCubicAndOverlayIndices.NAME_OL_INDX
            STRUCT_NONCUBIC_INDX = NonCubicAndOverlayIndices.STRUCT_NONCUBIC_INDX
            OVERLAYGROUP_INDX = NonCubicAndOverlayIndices.OVERLAYGROUP_INDX

            truncStructureList = itemNonCubicOverlay[STRUCT_NONCUBIC_INDX]
            overlayGroups = itemNonCubicOverlay[OVERLAYGROUP_INDX]

            mainFaciesTable, faciesInZone, gaussFieldsInZone, alphaFieldNameForBackGroundFacies = self.__background(truncStructureList, 'NonCubic')
            if self.__checkOverlayFacies(faciesInZone, overlayGroups):
                gaussFieldsInZone, faciesInZone = self.__updateGaussFieldNamesandFaciesInZoneForOverlay(overlayGroups, gaussFieldsInZone, faciesInZone)
                truncObj = Trunc2D_Angle()
                truncObj.initialize(mainFaciesTable, faciesInZone, gaussFieldsInZone, alphaFieldNameForBackGroundFacies,
                                    truncStructureList, overlayGroups=overlayGroups, debug_level=self.debug_level)
            else:
                raise IOError(
                    'Inconsistent facies specification for truncation rule with overlay facies.'
                    'Either: specified background facies for overlay facies groups is not defined '
                    'in background facies truncation rule.'
                    'Or: specified overlay facies is equal to background facies')

        return truncObj

    def __background(self, item, truncType):
        # Cubic truncation rule where each polygon is specified as [faciesName, probFraction, L1, L2, L3]
        truncStructureList = item
        startIndx = 0
        endIndx = 0
        FACIES_NAME_INDX = -999
        if truncType == 'Cubic':
            nPolygons = len(truncStructureList) - 1
            startIndx = 1
            endIndx = nPolygons + 1
            FACIES_NAME_INDX = CubicPolygonIndices.FACIES_NAME_INDX
        elif truncType == 'NonCubic':
            nPolygons = len(truncStructureList)
            startIndx = 0
            endIndx = nPolygons
            FACIES_NAME_INDX = NonCubicPolygonIndices.FACIES_NAME_INDX
        elif truncType == 'Bayfill':
            nPolygons = 5
            startIndx = 0
            endIndx = nPolygons
            FACIES_NAME_INDX = 0

        fNameList = []
        fTable = {}

        for i in range(startIndx, endIndx):
            polyItem = truncStructureList[i]
            fName = polyItem[FACIES_NAME_INDX]
            # Add the facies name only if it is not already within the list
            if fName not in fNameList:
                fNameList.append(fName)
                fTable[i - startIndx + 1] = fName

        # Define default values for name of gauss fields, facies
        faciesInZone = fNameList
        mainFaciesTable = APSMainFaciesTable(facies_table=fTable)
        gaussFieldsInZone = ['GRF01', 'GRF02']
        alphaFieldNameForBackGroundFacies = ['GRF01', 'GRF02']
        if truncType == 'Bayfill':
            for fields in [gaussFieldsInZone, alphaFieldNameForBackGroundFacies]:
                fields.append('GRF03')
        return mainFaciesTable, faciesInZone, gaussFieldsInZone, alphaFieldNameForBackGroundFacies

    def __checkOverlayFacies(self, backgroundFaciesList, overlayGroups):
        ALPHA_LIST_INDX = OverlayGroupIndices.ALPHA_LIST_INDX
        BACKGROUND_LIST_INDX = OverlayGroupIndices.BACKGROUND_LIST_INDX
        FACIES_NAME_INDX = OverlayPolygonIndices.FACIES_NAME_INDX
        if overlayGroups is not None:
            for n in range(len(overlayGroups)):
                groupItem = overlayGroups[n]
                alphaList = groupItem[ALPHA_LIST_INDX]
                backgroundListForGroup = groupItem[BACKGROUND_LIST_INDX]
                # Check that background facies for group are defined in background model
                for fName in backgroundListForGroup:
                    if fName not in backgroundFaciesList:
                        return False
                for i in range(len(alphaList)):
                    alphaItem = alphaList[i]
                    fNameOverlay = alphaItem[FACIES_NAME_INDX]
                    if fNameOverlay in backgroundFaciesList:
                        return False
        return True

    def __updateGaussFieldNamesandFaciesInZoneForOverlay(self, overlayGroups, gaussFieldNameList, faciesNameList):
        # groups = [ groupItem, groupItem, ...]
        # groupItem = [alphaList, backgroundListForGroup]
        # alphaList = [alphaItem, alphaItem ,...]
        # alphaItem = [alphaName, faciesName, probFrac, centerPoint]
        ALPHA_LIST_INDX = OverlayGroupIndices.ALPHA_LIST_INDX
        BACKGROUND_LIST_INDX = OverlayGroupIndices.BACKGROUND_LIST_INDX
        ALPHA_NAME_INDX = OverlayPolygonIndices.ALPHA_NAME_INDX
        FACIES_NAME_INDX = OverlayPolygonIndices.FACIES_NAME_INDX

        if overlayGroups is not None:
            for n in range(len(overlayGroups)):
                groupItem = overlayGroups[n]
                alphaList = groupItem[ALPHA_LIST_INDX]
                for i in range(len(alphaList)):
                    alphaItem = alphaList[i]
                    alphaName = alphaItem[ALPHA_NAME_INDX]
                    faciesName = alphaItem[FACIES_NAME_INDX]
                    if alphaName == gaussFieldNameList[0] or alphaName == gaussFieldNameList[1]:
                        raise ValueError('Can not have gauss field names for overlay facies equal to {} or {}.'
                                         ''.format(gaussFieldNameList[0], gaussFieldNameList[1]))
                    else:
                        if alphaName not in gaussFieldNameList:
                            gaussFieldNameList.append(alphaName)
                    if faciesName not in faciesNameList:
                        faciesNameList.append(faciesName)

        return gaussFieldNameList, faciesNameList

    def writeTruncRuleToXmlFile(self, name, outputFileName):
        ''' Build an XML tree with top as root from truncation object and write it'''
        truncRuleObj = self.getTruncationRuleObject(name)
        assert truncRuleObj is not None
        top = Element('TOP')
        truncRuleObj.XMLAddElement(top)
        rootReformatted = prettify(top)
        print('Write file:  {}'.format(outputFileName))
        with open(outputFileName, 'w', encoding='utf-8') as file:
            file.write(rootReformatted)

    def initNewTruncationRuleSettingsCubic(self, direction):
        ''' Initialize new truncation rule settings.
            Call this function as the first function when creating an new settings for Cubic rules.'''
        assert direction in ['H', 'V']
        truncStructureCubic = [direction]
        return truncStructureCubic

    def addPolygonToTruncationRuleSettingsCubic(self, truncStructureCubic, faciesName, probFrac, L1, L2, L3):
        ''' Add one polygon settings for Cubic rules.
            Use this function repeatedly to add the polygons for one Cubic settings.
            NOTE: Add polygons in correct order sorted by first L1, then L2 then L3.'''

        polyItem = [faciesName, probFrac, L1, L2, L3]
        truncStructureCubic.append(polyItem)

    def addTruncationRuleSettingsBayfill(self, name, settings):
        self.__tableBayfill[name] = settings

    def addTruncationRuleSettingsCubic(self, name, truncStructureSetting, replace=False):
        ''' Add a truncation rule settings for Cubic rule to the truncation rule settings dictionary
            using name as key. If replace is False, a new setting with a new name is allowed, but if the name already
            exists, nothing will be done.
            If the replace is True, the settings will be replaced if it already exists.
        '''
        if replace:
            self.__tableCubic[name] = truncStructureSetting
        else:
            # Check if the name is used
            if not name in self.__tableCubic:
                self.__tableCubic[name] = truncStructureSetting

    def initNewTruncationRuleSettingsNonCubic(self):
        ''' Initialize new truncation rule settings.
            Call this function as the first function when creating an new settings for NonCubic rules.'''
        truncStructureNonCubic = []
        return truncStructureNonCubic

    def addPolygonToTruncationRuleSettingsNonCubic(self, truncStructureCubic, faciesName, angle, probFrac):
        ''' Add one polygon settings for NonCubic rules.
            Use this function repeatedly to add the polygons for one NonCubic settings.
            NOTE: Add polygons in the correct order as specified by user.'''

        polyItem = [faciesName, angle, probFrac]
        truncStructureCubic.append(polyItem)

    def addTruncationRuleSettingsNonCubic(self, name, truncStructureSetting, replace=False):
        ''' Add a truncation rule settings for NonCubic truncation rule to the truncation rule settings dictionary
            using name as key. If replace is False, a new setting with a new name is allowed, but if the name already
            exists, nothing will be done.
            If the replace is True, the settings will be replaced if it already exists.
        '''
        if replace:
            self.__tableNonCubic[name] = truncStructureSetting
        else:
            # Check if the name is used
            if name not in self.__tableNonCubic:
                self.__tableNonCubic[name] = truncStructureSetting

    def addPolygonToAlphaList(self, alphaName, faciesName, probFrac=1.0, centerPoint=0.0, alphaList=None):
        ''' Function to add a polygon with associated alpha field name, facies name etc to list for one overlay group'''
        if alphaList is None:
            alphaList = []
            alphaList.append([alphaName, faciesName, probFrac, centerPoint])
        else:
            alphaList.append([alphaName, faciesName, probFrac, centerPoint])
        return alphaList

    def addOverlayGroupSettings(self, alphaList, backgroundFaciesListForGroup, overlayGroups=None):
        ''' Function to add a new overlay group to the list of overlay groups.'''
        if overlayGroups is None:
            overlayGroups = []
            overlayGroups.append([alphaList, backgroundFaciesListForGroup])
        else:
            overlayGroups.append([alphaList, backgroundFaciesListForGroup])
        return overlayGroups

    def addTruncationRuleSettingsOverlay(self, name, overlayGroups, replace=False):
        ''' Function to add a new overlay truncation settings.'''
        if replace:
            self.__tableOverlay[name] = overlayGroups
        else:
            # Check if the name is used
            if name not in self.__tableOverlay:
                self.__tableOverlay[name] = overlayGroups

    def addTruncationRuleSettingsCubicWithOverlay(self, name, nameBG, nameOL, replace=False):
        ''' Add a truncation rule settings to the truncation rule settings dictionary
            using name as key. Name of background truncation rule and overlay truncation rule are input.
            Note that if replace is False, nothing is done if the truncation settings already exists.
            It is a requirement that truncation rules for background facies and overlay facies already are defined, and that
            background facies truncation settings and overlay facies settings are consistent.
        '''
        try:
            truncStructBG = self.__tableCubic[nameBG]
        except KeyError:
            raise KeyError('Background facies truncation rule setting: {} is not defined'.format(nameBG))
        try:
            overlayGroups = self.__tableOverlay[nameOL]
        except KeyError:
            raise KeyError('Overlay facies truncation rule setting: {} is not defined'.format(nameOL))

        # Check consistency between chosen background truncation rule setting and overlay facies truncation rule setting.
        if not self.__checkConsistencyBetweenBackGroundCubicAndOverlay(truncStructBG, overlayGroups):
            raise ValueError(
                'Specified background facies truncation setting {} '
                'and overlay facies setting {} are not consistent with each other'
                ''.format(nameBG, nameOL)
            )

        # Create new Cubic setting with overlay
        truncStructCubicWithOverlay = [nameBG, nameOL, truncStructBG, overlayGroups]
        if replace:
            self.__tableCubicAndOverlay[name] = truncStructCubicWithOverlay
        else:
            if name not in self.__tableCubicAndOverlay:
                self.__tableCubicAndOverlay[name] = truncStructCubicWithOverlay

    def addTruncationRuleSettingsNonCubicWithOverlay(self, name, nameBG, nameOL, replace=False):
        ''' Add a truncation rule settings to the truncation rule settings dictionary
            using name as key. Name of background truncation rule and overlay truncation rule are input.
            Note that if replace is False, nothing is done if the truncation settings already exists.
            It is a requirement that truncation rules for background facies and overlay facies already are defined, and that
            background facies truncation settings and overlay facies settings are consistent.
        '''
        try:
            truncStructBG = self.__tableNonCubic[nameBG]
        except KeyError:
            raise KeyError('Background facies truncation rule setting: {} is not defined'.format(nameBG))
        try:
            overlayGroups = self.__tableOverlay[nameOL]
        except KeyError:
            raise KeyError('Overlay facies truncation rule setting: {} is not defined'.format(nameOL))

        # Check consistency between chosen background truncation rule setting and overlay facies truncation rule setting
        if not self.__checkConsistencyBetweenBackGroundNonCubicAndOverlay(truncStructBG, overlayGroups):
            raise ValueError(
                'Specified background facies truncation setting {} '
                'and overlay facies setting {} are not consistent with each other'
                ''.format(nameBG, nameOL)
            )

        # Create new NonCubic setting with overlay
        truncStructNonCubicWithOverlay = [nameBG, nameOL, truncStructBG, overlayGroups]
        if replace:
            self.__tableNonCubicAndOverlay[name] = truncStructNonCubicWithOverlay
        else:
            if name not in self.__tableNonCubicAndOverlay:
                self.__tableNonCubicAndOverlay[name] = truncStructNonCubicWithOverlay

    def __checkConsistencyBetweenBackGroundCubicAndOverlay(self, truncStructBG, overlayGroups):
        # Check consistency between chosen background truncation rule setting and overlay facies truncation rule setting
        bgFacies = []
        FACIES_NAME_INDX_BG = CubicPolygonIndices.FACIES_NAME_INDX
        ALPHA_LIST_INDX = OverlayGroupIndices.ALPHA_LIST_INDX
        BACKGROUND_LIST_INDX = OverlayGroupIndices.BACKGROUND_LIST_INDX
        ALPHA_NAME_INDX = OverlayPolygonIndices.ALPHA_NAME_INDX
        FACIES_NAME_INDX_OL = OverlayPolygonIndices.FACIES_NAME_INDX
        for i in range(len(truncStructBG)):
            poly = truncStructBG[i]
            fName = poly[FACIES_NAME_INDX_BG]
            if fName not in bgFacies:
                bgFacies.append(fName)

        for n in range(len(overlayGroups)):
            groupItem = overlayGroups[n]
            alphaList = groupItem[ALPHA_LIST_INDX]
            backgroundListForGroup = groupItem[BACKGROUND_LIST_INDX]
            for fName in backgroundListForGroup:
                if fName not in bgFacies:
                    return False
            for i in range(len(alphaList)):
                alphaItem = alphaList[i]
                alphaName = alphaItem[ALPHA_NAME_INDX]
                fName = alphaItem[FACIES_NAME_INDX_OL]
                if fName in bgFacies:
                    return False
                if alphaName == 'GRF01' or alphaName == 'GRF02':
                    return False
        return True

    def __checkConsistencyBetweenBackGroundCubicAndOverlayOld(self, nameBG, nameOL, truncStructBG, overlayGroups):
        # Check consistency between chosen background truncation rule setting and overlay facies truncation rule setting
        bgFacies = []
        FACIES_NAME_INDX_BG = CubicPolygonIndices.FACIES_NAME_INDX
        ALPHA_LIST_INDX = OverlayGroupIndices.ALPHA_LIST_INDX
        BACKGROUND_LIST_INDX = OverlayGroupIndices.BACKGROUND_LIST_INDX
        ALPHA_NAME_INDX = OverlayPolygonIndices.ALPHA_NAME_INDX
        FACIES_NAME_INDX_OL = OverlayPolygonIndices.FACIES_NAME_INDX
        for i in range(len(truncStructBG)):
            poly = truncStructBG[i]
            fName = poly[FACIES_NAME_INDX_BG]
            if fName not in bgFacies:
                bgFacies.append(fName)

        for n in range(len(overlayGroups)):
            groupItem = overlayGroups[n]
            alphaList = groupItem[ALPHA_LIST_INDX]
            backgroundListForGroup = groupItem[BACKGROUND_LIST_INDX]
            for fName in backgroundListForGroup:
                if fName not in bgFacies:
                    raise ValueError(
                        f'Specified background facies name {fName} in overlay facies rule {nameOL} '
                        f'does not exist as facies in Cubic rule with name {nameBG} '
                    )
            for i in range(len(alphaList)):
                alphaItem = alphaList[i]
                alphaName = alphaItem[ALPHA_NAME_INDX]
                fName = alphaItem[FACIES_NAME_INDX_OL]
                if fName in bgFacies:
                    raise ValueError(
                        f'Specified overlay facies name {fName} in overlay facies rule {nameOL} '
                        f'is already defined as background facies in Cubic rule with name {nameBG} '
                    )
                if alphaName == 'GRF01' or alphaName == 'GRF02':
                    raise ValueError(
                        f'Alpha field names can not be the same in overlay facies truncation settings in {nameOL} '
                        f'as for background facies truncation settings in {nameBG} '
                    )

    def __checkConsistencyBetweenBackGroundNonCubicAndOverlay(self, truncStructBG, overlayGroups):
        # Check consistency between chosen background truncation rule setting and overlay facies truncation rule setting
        bgFacies = []
        FACIES_NAME_INDX_BG = NonCubicPolygonIndices.FACIES_NAME_INDX
        ALPHA_LIST_INDX = OverlayGroupIndices.ALPHA_LIST_INDX
        BACKGROUND_LIST_INDX = OverlayGroupIndices.BACKGROUND_LIST_INDX
        ALPHA_NAME_INDX = OverlayPolygonIndices.ALPHA_NAME_INDX
        FACIES_NAME_INDX_OL = OverlayPolygonIndices.FACIES_NAME_INDX
        for i in range(len(truncStructBG)):
            poly = truncStructBG[i]
            fName = poly[FACIES_NAME_INDX_BG]
            if fName not in bgFacies:
                bgFacies.append(fName)

        for n in range(len(overlayGroups)):
            groupItem = overlayGroups[n]
            alphaList = groupItem[ALPHA_LIST_INDX]
            backgroundListForGroup = groupItem[BACKGROUND_LIST_INDX]
            for fName in backgroundListForGroup:
                if fName not in bgFacies:
                    return False
            for i in range(len(alphaList)):
                alphaItem = alphaList[i]
                alphaName = alphaItem[ALPHA_NAME_INDX]
                fName = alphaItem[FACIES_NAME_INDX_OL]
                if fName in bgFacies:
                    return False
                if alphaName == 'GRF01' or alphaName == 'GRF02':
                    return False
        return True

    def removeTruncationRuleSettings(self, name, removeDependentBG=False, removeDependentOL=False):
        """ Remove a truncation setting from the dictionary. If a truncation rule using overlay facies is removed,
        it will not remove the background settings which still will be available for truncation rule settings
        without overlay. """

        if name in self.__tableBayfill:
            print('Remove: {}'.format(name))
            del self.__tableBayfill[name]

        if name in self.__tableCubic:
            NAME_BG_INDX = CubicAndOverlayIndices.NAME_BG_INDX
            # Check that this setting is not used in settings with overlay facies
            isUsed = False
            for key, itemCubicOverlay in self.__tableCubicAndOverlay.items():
                nameBG = itemCubicOverlay[NAME_BG_INDX]
                if name == nameBG:
                    isUsed = True
                    break
            if not isUsed:
                print(f'Remove: {name}')
                del self.__tableCubic[name]

        if name in self.__tableNonCubic:
            NAME_BG_INDX = NonCubicAndOverlayIndices.NAME_BG_INDX
            # Check that this setting is not used in settings with overlay facies
            isUsed = False
            for key, itemNonCubicOvelay in self.__tableNonCubicAndOverlay.items():
                nameBG = itemNonCubicOvelay[NAME_BG_INDX]
                if name == nameBG:
                    isUsed = True
                    break
            if not isUsed:
                print(f'Remove: {name}')
                del self.__tableNonCubic[name]

        if name in self.__tableNonCubicAndOverlay:
            NAME_BG_INDX = NonCubicAndOverlayIndices.NAME_BG_INDX
            NAME_OL_INDX = NonCubicAndOverlayIndices.NAME_OL_INDX
            itemNonCubicOverlay = self.__tableNonCubicAndOverlay[name]
            nameBG = itemNonCubicOverlay[NAME_BG_INDX]
            nameOL = itemNonCubicOverlay[NAME_OL_INDX]
            # Check if background and overlay truncation settings are used in other rules
            isUsedBG = False
            isUsedOL = False
            for key, itemNonCubicOverlay in self.__tableNonCubicAndOverlay.items():
                if name != key:
                    nameBG2 = itemNonCubicOverlay[NAME_BG_INDX]
                    nameOL2 = itemNonCubicOverlay[NAME_OL_INDX]
                    if nameBG == nameBG2:
                        isUsedBG = True
                    if nameOL2 == nameOL:
                        isUsedOL = True

            print(f'Remove: {name}')
            del self.__tableNonCubicAndOverlay[name]
            if removeDependentBG and not isUsedBG:
                print('  Remove: {}'.format(nameBG))
                del self.__tableNonCubic[nameBG]

            if removeDependentOL and not isUsedOL:
                print(f'  Remove: {nameOL}')
                del self.__tableOverlay[nameOL]

        if name in self.__tableCubicAndOverlay:
            NAME_BG_INDX = CubicAndOverlayIndices.NAME_BG_INDX
            NAME_OL_INDX = CubicAndOverlayIndices.NAME_OL_INDX
            itemCubicOverlay = self.__tableCubicAndOverlay[name]
            nameBG = itemCubicOverlay[NAME_BG_INDX]
            nameOL = itemCubicOverlay[NAME_OL_INDX]
            # Check if background and overlay truncation settings are used in other rules
            isUsedBG = False
            isUsedOL = False
            for key, itemCubicOverlay in self.__tableCubicAndOverlay.items():
                if name != key:
                    nameBG2 = itemCubicOverlay[NAME_BG_INDX]
                    nameOL2 = itemCubicOverlay[NAME_OL_INDX]
                    if nameBG == nameBG2:
                        isUsedBG = True
                    if nameOL2 == nameOL:
                        isUsedOL = True

            print(f'Remove: {name}')
            del self.__tableCubicAndOverlay[name]
            if removeDependentBG and not isUsedBG:
                print(f'  Remove: {nameBG}')
                del self.__tableCubic[nameBG]

            if removeDependentOL and not isUsedOL:
                print(f'  Remove: {nameOL}')
                del self.__tableOverlay[nameOL]

    def __appendToList(self, dictionary, truncType, nBackgroundFacies, nOverlayFacies):
        settingsList = []
        for key, item in dictionary.items():
            nBG = self.__getNBackgroundFacies(truncType, item)
            nOL = self.__getNOverlayFacies(truncType, item)
            truncMapPlotFile = self.__directory + '/' + key + '.png'
            if nBackgroundFacies == 0:
                settingsList.append([key, item, truncMapPlotFile])
            elif nBackgroundFacies == nBG and nOverlayFacies == nOL:
                settingsList.append([key, item, truncMapPlotFile])
        return settingsList

    def getListOfSettings(self, truncType, nBackgroundFacies=0, nOverlayFacies=0):
        if truncType == 'Cubic':
            sortedDictionary = collections.OrderedDict(sorted(self.__tableCubic.items()))
            settingsList = self.__appendToList(sortedDictionary, truncType, nBackgroundFacies, nOverlayFacies)
        elif truncType == 'NonCubic':
            sortedDictionary = collections.OrderedDict(sorted(self.__tableNonCubic.items()))
            settingsList = self.__appendToList(sortedDictionary, truncType, nBackgroundFacies, nOverlayFacies)
        elif truncType == 'CubicAndOverlay':
            sortedDictionary = collections.OrderedDict(sorted(self.__tableCubicAndOverlay.items()))
            settingsList = self.__appendToList(sortedDictionary, truncType, nBackgroundFacies, nOverlayFacies)
        elif truncType == 'NonCubicAndOverlay':
            sortedDictionary = collections.OrderedDict(sorted(self.__tableNonCubicAndOverlay.items()))
            settingsList = self.__appendToList(sortedDictionary, truncType, nBackgroundFacies, nOverlayFacies)
        elif truncType == 'Overlay':
            sortedDictionary = collections.OrderedDict(sorted(self.__tableOverlay.items()))
            settingsList = []
            for key, item in sortedDictionary.items():
                settingsList.append([key, item, ''])
        else:
            raise ValueError(
                f'Truncation type {truncType} is not defined.')

        return settingsList

    def __getNBackgroundFacies(self, truncType, item):
        backgroundFaciesList = []
        if truncType == 'Cubic':
            FACIES_NAME_INDX = CubicPolygonIndices.FACIES_NAME_INDX
            itemCubic = item
            for i in range(1, len(itemCubic)):
                poly = itemCubic[i]
                fName = poly[FACIES_NAME_INDX]
                if fName not in backgroundFaciesList:
                    backgroundFaciesList.append(fName)
        elif truncType == 'NonCubic':
            FACIES_NAME_INDX = NonCubicPolygonIndices.FACIES_NAME_INDX
            itemNonCubic = item
            for i in range(len(itemNonCubic)):
                poly = itemNonCubic[i]
                fName = poly[FACIES_NAME_INDX]
                if fName not in backgroundFaciesList:
                    backgroundFaciesList.append(fName)
        elif truncType == 'CubicAndOverlay':
            FACIES_NAME_INDX = CubicPolygonIndices.FACIES_NAME_INDX
            STRUCT_CUBIC_INDX = CubicAndOverlayIndices.STRUCT_CUBIC_INDX
            itemCubicOverlay = item[STRUCT_CUBIC_INDX]
            for i in range(1, len(itemCubicOverlay)):
                poly = itemCubicOverlay[i]
                fName = poly[FACIES_NAME_INDX]
                if fName not in backgroundFaciesList:
                    backgroundFaciesList.append(fName)
        elif truncType == 'NonCubicAndOverlay':
            FACIES_NAME_INDX = NonCubicPolygonIndices.FACIES_NAME_INDX
            STRUCT_NONCUBIC_INDX = NonCubicAndOverlayIndices.STRUCT_NONCUBIC_INDX
            itemNonCubicOverlay = item[STRUCT_NONCUBIC_INDX]
            for i in range(len(itemNonCubicOverlay)):
                poly = itemNonCubicOverlay[i]
                fName = poly[FACIES_NAME_INDX]
                if fName not in backgroundFaciesList:
                    backgroundFaciesList.append(fName)
        else:
            raise ValueError('Truncation type {} is not defined.'.format(truncType))
        nBackgroundFacies = len(backgroundFaciesList)
        return nBackgroundFacies

    def __getNOverlayFacies(self, truncType, item):
        overlayFaciesList = []
        nOverlayFacies = 0

        if truncType == 'CubicAndOverlay' or truncType == 'NonCubicAndOverlay':
            OVERLAYGROUP_INDX = -999
            if truncType == 'CubicAndOverlay':
                OVERLAYGROUP_INDX = CubicAndOverlayIndices.OVERLAYGROUP_INDX
            elif truncType == 'NonCubicAndOverlay':
                OVERLAYGROUP_INDX = NonCubicAndOverlayIndices.OVERLAYGROUP_INDX
            ALPHA_LIST_INDX = OverlayGroupIndices.ALPHA_LIST_INDX
            FACIES_NAME_INDX = OverlayPolygonIndices.FACIES_NAME_INDX
            overlayGroups = item[OVERLAYGROUP_INDX]

            for i in range(len(overlayGroups)):
                groupItem = overlayGroups[i]
                alphaList = groupItem[ALPHA_LIST_INDX]
                for n in range(len(alphaList)):
                    alphaItem = alphaList[n]
                    fName = alphaItem[FACIES_NAME_INDX]
                    if fName not in overlayFaciesList:
                        overlayFaciesList.append(fName)

            nOverlayFacies = len(overlayFaciesList)
        return nOverlayFacies

    def getListOfOverlaySettings(self, name):
        """ Find truncation settings for background facies.
         Specified name is name of truncation setting of either type Cubic or NonCubic"""
        itemCubic = None
        itemNonCubic = None
        itemBayfill = None
        overlay_setting_list = []
        try:
            itemCubic = self.__tableCubic[name]
        except:
            try:
                itemNonCubic = self.__tableNonCubic[name]
            except:
                try:
                    itemBayfill = self.__tableBayfill[name]
                except KeyError:
                    raise KeyError(f'Truncation setting with name {name} is not defined.')

        if itemCubic is not None:
            # Search for all overlay settings that are consistent with background model
            sortedDictionary = collections.OrderedDict(sorted(self.__tableOverlay.items()))
            for key, itemOverlay in sortedDictionary.items():
                if self.__checkConsistencyBetweenBackGroundCubicAndOverlay(itemCubic, itemOverlay):
                    overlay_setting_list.append(key)
        elif itemNonCubic is not None:
            sortedDictionary = collections.OrderedDict(sorted(self.__tableOverlay.items()))
            for key, itemOverlay in sortedDictionary.items():
                if self.__checkConsistencyBetweenBackGroundNonCubicAndOverlay(itemNonCubic, itemOverlay):
                    overlay_setting_list.append(key)
        elif itemBayfill is not None:
            sortedDictionary = collections.OrderedDict(sorted(self.__tableBayfill.items()))
            for key, item in sortedDictionary.items():
                overlay_setting_list.append(key)
        else:
            raise ValueError(f'Specified truncation setting {name} is not defined.')

        return overlay_setting_list

    def makeTruncationMapPlot(self, name, writePngFile=True):
        # Truncation map is plotted
        fig = plt.figure(figsize=[2.0, 2.0], frameon=False)
        axTrunc = self.__makeTruncationMapSubPlot(name, fig, 1, 1, 1)
        axTrunc.set_aspect('equal', 'box')
        if not self.show_title:
            axTrunc.get_xaxis().set_visible(False)
            axTrunc.get_yaxis().set_visible(False)
            fig.patch.set_visible(False)
            axTrunc.axis('off')
            plt.autoscale(tight=True)
        if writePngFile:
            plotFileName = name + '.png'
            if self.__directory:
                plotFileName = self.__directory + '/' + plotFileName
            print('Write file: {}'.format(plotFileName))
            fig.savefig(plotFileName)
            plt.close(fig)
        else:
            plt.show()

    def __makeTruncationMapSubPlot(self, name, fig, Nrow, Ncol, indx):
        ''' Create truncation map plot using same probability for each facies'''
        truncObj = self.getTruncationRuleObject(name)
        faciesNames = truncObj.getFaciesInTruncRule()
        nFacies = len(faciesNames)
        faciesProb = np.zeros(nFacies, dtype=np.float32)
        f = -1.0
        for i in range(nFacies):
            f = -f
            faciesProb[i] = (1.0 / float(nFacies)) + 0.001*f
        truncObj.setTruncRule(faciesProb)
        faciesPolygons = truncObj.truncMapPolygons()
        faciesIndxPerPolygon = truncObj.faciesIndxPerPolygon()
        faciesOrdering = truncObj.getFaciesOrderIndexList()

        # Truncation map is plotted
        self.show_title = False
        plt.axis('off')
        if self.show_title:
            axTrunc = plt.subplot(Nrow, Ncol, indx)
        else:
            axTrunc = fig.add_axes([0, 0, 1, 1])
        colors = get_colors(nFacies)

        # Create the colormap
        if self.debug_level >= Debug.ON:
            print('Debug output: Number of facies:          ' + str(nFacies))
            print('Debug output: Number of facies polygons: ' + str(len(faciesPolygons)))
        # Add a background polygon (square) that is slightly larger than unit square to make a frame
        poly = np.zeros((5,2), dtype=np.float32)
        frame_size = 0.05
        poly[0,0] = -frame_size
        poly[0,1] = -frame_size
        poly[1,0] = 1 + frame_size
        poly[1,1] = -frame_size
        poly[2,0] = 1 + frame_size
        poly[2,1] = 1 + frame_size
        poly[3,0] = -frame_size
        poly[3,1] = 1 + frame_size
        poly[4,0] = -frame_size
        poly[4,1] = -frame_size
        if self.show_title:
            polygon = Polygon(poly, closed=True, facecolor='white')
            axTrunc.add_patch(polygon)
        for i in range(len(faciesPolygons)):
            indx = faciesIndxPerPolygon[i]
            fIndx = faciesOrdering[indx]
            poly = faciesPolygons[i]
            polygon = Polygon(poly, closed=True, facecolor=colors[fIndx])
            axTrunc.add_patch(polygon)
        if self.show_title:
            axTrunc.set_title(name)
        return axTrunc

    @conditional_directory('Bayfill')
    def createAllBayfillPlots(self):
        sortedDictionaryBayfill = collections.OrderedDict(sorted(self.__tableBayfill.items()))
        for name, spec in sortedDictionaryBayfill.items():
            self.makeTruncationMapPlot(name)

    @conditional_directory('Cubic')
    def createAllCubicPlots(self):
        ''' Make truncation map plots for all specified settings for Cubic truncation rule in dictionarly'''
        sortedDictionaryCubic = collections.OrderedDict(sorted(self.__tableCubic.items()))
        for name, truncStructItem in sortedDictionaryCubic.items():
            self.makeTruncationMapPlot(name)

    @conditional_directory('Cubic')
    def createAllCubicWithOverlayPlots(self):
        ''' Make truncation map plots for all specified settings for Cubic truncation rule with overlay facies in dictionarly'''
        sortedDictionaryCubic = collections.OrderedDict(sorted(self.__tableCubicAndOverlay.items()))
        for name, truncStructItem in sortedDictionaryCubic.items():
            self.makeTruncationMapPlot(name)

    @conditional_directory('Non-Cubic')
    def createAllNonCubicPlots(self):
        ''' Make truncation map plots for all specified settings for NonCubic truncation rule in dictionarly'''
        sortedDictionaryNonCubic = collections.OrderedDict(sorted(self.__tableNonCubic.items()))
        for name, truncStructItem in sortedDictionaryNonCubic.items():
            self.makeTruncationMapPlot(name)

    @conditional_directory('Non-Cubic')
    def createAllNonCubicWithOverlayPlots(self):
        ''' Make truncation map plots for all specified settings for NonCubic truncation rule with overlay facies in dictionarly'''
        sortedDictionaryNonCubic = collections.OrderedDict(sorted(self.__tableNonCubicAndOverlay.items()))
        for name, truncStructItem in sortedDictionaryNonCubic.items():
            self.makeTruncationMapPlot(name)

    def createAllCubicXMLTemplates(self):
        ''' Make template xml files containing all Cubic truncation rule settings.'''
        for name, truncStructItem in self.__tableCubic.items():
            outputFileName = name + '.xml'
            if self.__directory:
                outputFileName = self.__directory + '/' + name + '.xml'
            self.writeTruncRuleToXmlFile(name, outputFileName)

    def createAllNonCubicXMLTemplates(self):
        ''' Make template xml files containing all NonCubic truncation rule settings.'''
        for name, truncStructItem in self.__tableNonCubic.items():
            outputFileName = name + '.xml'
            if self.__directory:
                outputFileName = self.__directory + '/' + name + '.xml'
            self.writeTruncRuleToXmlFile(name, outputFileName)

    def createAllCubicXMLTemplatesWithOverlayFacies(self):
        ''' Make template xml files containing all Cubic truncation rule settings with overlay facies.'''
        for name, truncStructItem in self.__tableCubicAndOverlay.items():
            outputFileName = name + '.xml'
            if self.__directory:
                outputFileName = self.__directory + '/' + name + '.xml'
            self.writeTruncRuleToXmlFile(name, outputFileName)

    def createAllNonCubicXMLTemplatesWithOverlayFacies(self):
        ''' Make template xml files containing all NonCubic truncation rule settings with overlay facies.'''
        for name, truncStructItem in self.__tableNonCubicAndOverlay.items():
            outputFileName = name + '.xml'
            if self.__directory:
                outputFileName = self.__directory + '/' + name + '.xml'
            self.writeTruncRuleToXmlFile(name, outputFileName)

    def createOverviewPlotCubic(self, plotName):
        ''' Create plots of all specified Cubic settings in one common plot'''
        self._create_overview_plot(plotName, self.__tableCubic)

    def createOverviewPlotCubicWithOverlay(self, plotName):
        ''' Create plots of all specified Cubic settings with overlay facies in one common plot'''
        self._create_overview_plot(plotName, self.__tableCubicAndOverlay)

    def createOverviewPlotNonCubic(self, plotName):
        ''' Create plots of all specified NonCubic settings in one common plot'''
        self._create_overview_plot(plotName, self.__tableNonCubic)

    def createOverviewPlotNonCubicWithOverlay(self, plotName):
        ''' Create plots of all specified NonCubic settings with overlay facies in one common plot'''
        self._create_overview_plot(plotName, self.__tableNonCubicAndOverlay)

    def _create_overview_plot(self, plot_name, truncation_table):
        """Create plots of all specified settings with, or without overlay facies in one common plot"""
        rows = 5
        cols = 10
        indx = 1
        fig = plt.figure(figsize=[20.0, 10.0], frameon=False)
        sorted_truncation_rule = collections.OrderedDict(sorted(truncation_table.items()))
        for truncation_name, trunc_structure_item in sorted_truncation_rule.items():
            self.__makeTruncationMapSubPlot(truncation_name, fig, rows, cols, indx)
            indx += 1
        plot_file_name = plot_name + '.png'
        if self.__directory:
            plot_file_name = self.__directory + '/' + plot_name + '.png'
        print('Write file: {}'.format(plot_file_name))
        plt.axis('off')
        fig.savefig(plot_file_name)
        plt.close(fig)


def run_example():
    # Example how to use this class
    if len(argv) == 1:
        # Create new entries for truncation settings and add to file
        truncRuleDir = 'truncRuleSettings'
    else:
        truncRuleDir = argv[1]
    rules = DefineTruncationRule(truncRuleDir)
    # Create and add setting for Cubic truncation rule without overlay facies
    # This settings is for the case with 3 facies, one per polygon
    # Step 1: Initiate
    direction = 'H'
    truncStructureCubic = rules.initNewTruncationRuleSettingsCubic(direction)
    # Step 2: Add polygons with facies and probability fraction
    polygons = [
        ('F01', 1.0, 1, 1, 0),
        ('F02', 1.0, 1, 2, 0),
        ('F03', 1.0, 2, 0, 0),
    ]
    for faciesName, probFrac, L1, L2, L3 in polygons:
        rules.addPolygonToTruncationRuleSettingsCubic(truncStructureCubic, faciesName, probFrac, L1, L2, L3)
    # Step 3: Add the truncation setting to the object of type DefineTruncationRule
    nameBG = 'C_example_1'
    rules.addTruncationRuleSettingsCubic(nameBG, truncStructureCubic)

    # Optional step 4: Make an icon plot of the truncation setting
    rules.makeTruncationMapPlot(nameBG)

    # -----------

    # Create and add setting for NonCubic truncation rule with overlay facies
    # This settings is for the case with 4 polygons and 4 facies for background truncation rule of type NonCubic
    # and 2 overlay facies.
    # Step 1: Initiate
    truncStructureNonCubic = rules.initNewTruncationRuleSettingsNonCubic()

    # Step 2.1: Add polygons with facies and probability fraction
    polygons = [
        ('F01', 1.0, 45.0),
        ('F02', 1.0, -65.0),
        ('F03', 1.0, -120.0),
        ('F04', 1.0, 0.0),
    ]
    for faciesName, probFrac, angle in polygons:
        rules.addPolygonToTruncationRuleSettingsNonCubic(truncStructureNonCubic, faciesName, angle, probFrac)

    # Step 2.2: Add the truncation setting for the background facies to the object of type DefineTruncationRule
    nameBG = 'N_example_1'
    rules.addTruncationRuleSettingsNonCubic(nameBG, truncStructureNonCubic)
    # Optional step 2.3: Make an icon plot of the truncation setting
    rules.makeTruncationMapPlot(nameBG)

    # Step 3.1:
    # Define settings for one overlay group with two background facies and two polygons with the same overlay facies
    alphaList = rules.addPolygonToAlphaList('GRF03', 'F05', 0.5, 0.0)
    alphaList = rules.addPolygonToAlphaList('GRF04', 'F05', 0.5, 0.0, alphaList)
    backgroundFaciesListForGroup = ['F01', 'F02']
    overlayGroups = rules.addOverlayGroupSettings(alphaList, backgroundFaciesListForGroup)

    # Define settings for one overlay group with one background facies and one polygons with overlay facies
    alphaList = rules.addPolygonToAlphaList('GRF05', 'F06', 1.0, 0.0)
    backgroundFaciesListForGroup = ['F03']
    overlayGroups = rules.addOverlayGroupSettings(alphaList, backgroundFaciesListForGroup, overlayGroups)
    # Step 3.2: Add the overlayGroup list as a setting for overlay facies
    nameOL = 'A_example_1'
    rules.addTruncationRuleSettingsOverlay(nameOL, overlayGroups)

    # Step 4: Add a truncation rule using the background facies setting for NonCubic with name nameBG
    # and overlay facies setting with name nameOL as a new truncation rule settings
    name = 'NonCubic_1_with_overlay_1'
    rules.addTruncationRuleSettingsNonCubicWithOverlay(name, nameBG, nameOL)

    # Optional step 5: Make an icon plot of the truncation setting
    rules.makeTruncationMapPlot(name)
    # ------
    # Write rules to file
    rules.writeFile('out1.dat')

    # Read rules from file into new data object
    rulesRead = DefineTruncationRule(truncRuleDir)
    rulesRead.readFile('out1.dat')
    rulesRead.writeFile('out2.dat')

    # Add new truncation rule to the first truncation rule settings object

    # Create and add setting for Cubic truncation rule without overlay facies
    # This settings is for the case with 3 facies, one per polygon
    # Step 1: Initiate
    direction = 'V'
    truncStructureCubic = rules.initNewTruncationRuleSettingsCubic(direction)

    # Step 2: Add polygons with facies and probability fraction
    polygons = [
        ('F01', 0.5, 1, 1, 1),
        ('F02', 0.5, 1, 1, 2),
        ('F01', 0.5, 1, 2, 0),
        ('F03', 1.0, 2, 1, 0),
        ('F02', 0.5, 2, 2, 0),
    ]
    for faciesName, probFrac, L1, L2, L3 in polygons:
        rules.addPolygonToTruncationRuleSettingsCubic(truncStructureCubic, faciesName, probFrac, L1, L2, L3)
    # Step 3: Add the truncation setting to the object of type DefineTruncationRule
    nameBG = 'C_example_2'
    rules.addTruncationRuleSettingsCubic(nameBG, truncStructureCubic)
    # Optional step 4: Make an icon plot of the truncation setting
    rules.makeTruncationMapPlot(nameBG)

    rules.writeFile('out3.dat')

    # Create plots for all truncation settings
    rules.createOverviewPlotCubic('Cubic_rules')
    rules.createOverviewPlotNonCubic('NonCubic_rules')
    rules.createOverviewPlotCubicWithOverlay('Cubic_rules_with_overlay')
    rules.createOverviewPlotNonCubicWithOverlay('NonCubic_rules_with_overlay')

    rules.createAllNonCubicXMLTemplates()
    rules.createAllCubicXMLTemplatesWithOverlayFacies()
    rules.createAllNonCubicXMLTemplatesWithOverlayFacies()
    for nBackgroundFacies in range(1, 6):
        print('List of settings for Cubic with background facies: {}'
              ''.format(nBackgroundFacies))

        settingsList = rules.getListOfSettings('Cubic', nBackgroundFacies)
        for i in range(len(settingsList)):
            item = settingsList[i]
            key = item[0]
            fileName = item[2]
            print('{} {}'.format(key, fileName))

        for nOverlayFacies in range(5):
            print('List of settings for Cubic with background facies: {}   and overlay facies: {}'
                  ''.format(nBackgroundFacies, nOverlayFacies))

            settingsList = rules.getListOfSettings('CubicAndOverlay', nBackgroundFacies, nOverlayFacies)
            for i in range(len(settingsList)):
                item = settingsList[i]
                key = item[0]
                fileName = item[2]
                print('{} {}'.format(key, fileName))
    for nBackgroundFacies in range(1, 6):
        print('List of settings for NonCubic with background facies: {}'
              ''.format(nBackgroundFacies))

        settingsList = rules.getListOfSettings('NonCubic', nBackgroundFacies)
        for i in range(len(settingsList)):
            item = settingsList[i]
            key = item[0]
            fileName = item[2]
            print('{} {}'.format(key, fileName))

        for nOverlayFacies in range(5):
            print('List of settings for NonCubic with background facies: {}   and overlay facies: {}'
                  ''.format(nBackgroundFacies, nOverlayFacies))

            settingsList = rules.getListOfSettings('NonCubicAndOverlay', nBackgroundFacies, nOverlayFacies)
            for i in range(len(settingsList)):
                item = settingsList[i]
                key = item[0]
                fileName = item[2]
                print('{} {}'.format(key, fileName))

    # Remove a truncation setting
    # rules.removeTruncationRuleSettings('NonCubic_1_with_overlay_1')
    rules.removeTruncationRuleSettings('NonCubic_1_with_overlay_1', removeDependentBG=True, removeDependentOL=True)

    rules.writeFile('out4.dat')
    rulesFromFile = DefineTruncationRule(truncRuleDir)
    rulesFromFile.readFile("truncation_settings.dat")
    rulesFromFile.createAllCubicPlots()

    rules2 = DefineTruncationRule(truncRuleDir)
    rules2.readFile('truncation_settings.dat')
    rules2.createAllNonCubicXMLTemplatesWithOverlayFacies()


if __name__ == '__main__':
    run_example()
