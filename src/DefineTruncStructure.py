#!/bin/env python
import copy

from src import Trunc2D_Angle_Overlay_xml, Trunc2D_Cubic_Overlay_xml, Trunc3D_bayfill_xml


# import importlib

# importlib.reload(Trunc2D_Cubic_Overlay_xml)
# importlib.reload(Trunc2D_Angle_Overlay_xml)
# importlib.reload(APSMainFaciesTable)

# -----------------------------------------------------------------------
# class DefineTruncStructure
# Description:
# -------------------------------------------------------------


class DefineTruncStructure:
    """
    Description: This class keep data to define cubic truncation rules.
   
    """

    def __init__(self):

        self.__table = []
        self.__nRules = 31

        # -----   Cubic truncation rules  ---------------------------
        nPolygons = 2
        nFacies = 3
        nGF = 3
        OPFacies = 'P3'
        BGFacies = ['P1', 'P2']
        trOPCenter = 1.0
        truncStructure = ['H', ['P1', 1.0, 1, 0, 0], ['P2', 1.0, 2, 0, 0]]
        item = ['C01', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        truncStructure = ['V', ['P1', 1.0, 1, 0, 0], ['P2', 1.0, 2, 0, 0]]
        item = ['C02', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        # --------------------------------

        nPolygons = 3
        nFacies = 4
        nGF = 3
        OPFacies = 'P4'
        BGFacies = ['P1', 'P2', 'P3']
        trOPCenter = 1.0
        truncStructure = ['H', ['P1', 1.0, 1, 0, 0], ['P2', 1.0, 2, 0, 0], ['P3', 1.0, 3, 0, 0]]
        item = ['C03', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        truncStructure = ['V', ['P1', 1.0, 1, 0, 0], ['P2', 1.0, 2, 0, 0], ['P3', 1.0, 3, 0, 0]]
        item = ['C04', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        truncStructure = ['H', ['P1', 1.0, 1, 0, 0], ['P2', 1.0, 2, 1, 0], ['P3', 1.0, 2, 2, 0]]
        item = ['C05', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        truncStructure = ['H', ['P1', 1.0, 1, 1, 0], ['P2', 1.0, 1, 2, 0], ['P3', 1.0, 2, 0, 0]]
        item = ['C06', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        truncStructure = ['V', ['P1', 1.0, 1, 0, 0], ['P2', 1.0, 2, 1, 0], ['P3', 1.0, 2, 2, 0]]
        item = ['C07', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        truncStructure = ['V', ['P1', 1.0, 1, 1, 0], ['P2', 1.0, 1, 2, 0], ['P3', 1.0, 2, 0, 0]]
        item = ['C08', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        # --------------------------------


        nPolygons = 4
        nFacies = 5
        nGF = 3
        OPFacies = 'P5'
        BGFacies = ['P1', 'P2', 'P3', 'P4']
        trOPCenter = 1.0
        truncStructure = ['H', ['P1', 1.0, 1, 0, 0], ['P2', 1.0, 2, 0, 0], ['P3', 1.0, 3, 0, 0], ['P4', 1.0, 4, 0, 0]]
        item = ['C09', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        truncStructure = ['V', ['P1', 1.0, 1, 0, 0], ['P2', 1.0, 2, 0, 0], ['P3', 1.0, 3, 0, 0], ['P4', 1.0, 4, 0, 0]]
        item = ['C10', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        truncStructure = ['H', ['P1', 1.0, 1, 0, 0], ['P2', 1.0, 2, 0, 0], ['P3', 1.0, 3, 1, 0], ['P4', 1.0, 3, 2, 0]]
        item = ['C11', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        truncStructure = ['V', ['P1', 1.0, 1, 0, 0], ['P2', 1.0, 2, 0, 0], ['P3', 1.0, 3, 1, 0], ['P4', 1.0, 3, 2, 0]]
        item = ['C12', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        truncStructure = ['H', ['P1', 1.0, 1, 0, 0], ['P2', 1.0, 2, 1, 0], ['P3', 1.0, 2, 2, 0], ['P4', 1.0, 3, 0, 0]]
        item = ['C13', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        truncStructure = ['V', ['P1', 1.0, 1, 0, 0], ['P2', 1.0, 2, 1, 0], ['P3', 1.0, 2, 2, 0], ['P4', 1.0, 3, 0, 0]]
        item = ['C14', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        truncStructure = ['H', ['P1', 1.0, 1, 1, 0], ['P2', 1.0, 1, 2, 0], ['P3', 1.0, 2, 1, 0], ['P4', 1.0, 2, 2, 0]]
        item = ['C15', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        truncStructure = ['V', ['P1', 1.0, 1, 1, 0], ['P2', 1.0, 1, 2, 0], ['P3', 1.0, 2, 1, 0], ['P4', 1.0, 2, 2, 0]]
        item = ['C16', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        truncStructure = ['H', ['P1', 1.0, 1, 1, 0], ['P2', 1.0, 1, 2, 1], ['P3', 1.0, 1, 2, 2], ['P4', 1.0, 2, 0, 0]]
        item = ['C17', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        truncStructure = ['V', ['P1', 1.0, 1, 1, 0], ['P2', 1.0, 1, 2, 1], ['P3', 1.0, 1, 2, 2], ['P4', 1.0, 2, 0, 0]]
        item = ['C18', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        truncStructure = ['H', ['P1', 1.0, 1, 0, 0], ['P2', 1.0, 2, 1, 0], ['P3', 1.0, 2, 2, 1], ['P4', 1.0, 2, 2, 2]]
        item = ['C19', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        truncStructure = ['V', ['P1', 1.0, 1, 0, 0], ['P2', 1.0, 2, 1, 1], ['P3', 1.0, 2, 1, 2], ['P4', 1.0, 2, 2, 0]]
        item = ['C20', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        # --------------------------------

        nPolygons = 5
        nFacies = 6
        nGF = 3
        OPFacies = 'P6'
        BGFacies = ['P1', 'P2', 'P3', 'P4', 'P5']
        trOPCenter = 1.0
        truncStructure = ['H', ['P1', 1.0, 1, 0, 0], ['P2', 1.0, 2, 0, 0], ['P3', 1.0, 3, 0, 0], ['P4', 1.0, 4, 0, 0], ['P5', 1.0, 5, 0, 0]]
        item = ['C21', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        truncStructure = ['V', ['P1', 1.0, 1, 0, 0], ['P2', 1.0, 2, 0, 0], ['P3', 1.0, 3, 0, 0], ['P4', 1.0, 4, 0, 0], ['P5', 1.0, 5, 0, 0]]
        item = ['C22', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        truncStructure = ['H', ['P1', 1.0, 1, 0, 0], ['P2', 1.0, 2, 1, 0], ['P3', 1.0, 2, 2, 0], ['P4', 1.0, 2, 3, 1], ['P5', 1.0, 2, 3, 2]]
        item = ['C23', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        truncStructure = ['V', ['P1', 1.0, 1, 0, 0], ['P2', 1.0, 2, 1, 0], ['P3', 1.0, 2, 2, 0], ['P4', 1.0, 2, 3, 1], ['P5', 1.0, 2, 3, 2]]
        item = ['C24', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        truncStructure = ['H', ['P1', 1.0, 1, 0, 0], ['P2', 1.0, 2, 1, 1], ['P3', 1.0, 2, 1, 2], ['P4', 1.0, 2, 2, 1], ['P5', 1.0, 2, 2, 2]]
        item = ['C25', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        truncStructure = ['V', ['P1', 1.0, 1, 0, 0], ['P2', 1.0, 2, 1, 1], ['P3', 1.0, 2, 1, 2], ['P4', 1.0, 2, 2, 1], ['P5', 1.0, 2, 2, 2]]
        item = ['C26', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        truncStructure = ['H', ['P1', 1.0, 1, 0, 0], ['P2', 1.0, 2, 1, 0], ['P3', 1.0, 2, 2, 1], ['P4', 1.0, 2, 2, 2], ['P5', 1.0, 2, 3, 0]]
        item = ['C27', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        truncStructure = ['V', ['P1', 1.0, 1, 0, 0], ['P2', 1.0, 2, 1, 0], ['P3', 1.0, 2, 2, 1], ['P4', 1.0, 2, 2, 2], ['P5', 1.0, 2, 3, 0]]
        item = ['C28', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        # --------------------------------

        # Multiple polygons with same facies
        nPolygons = 6
        nFacies = 6
        nGF = 3
        OPFacies = 'P6'
        BGFacies = ['P1', 'P2', 'P3', 'P4', 'P5']
        trOPCenter = 1.0
        truncStructure = ['H', ['P1', 1.0, 1, 0, 0], ['P2', 1.0, 2, 1, 0], ['P3', 0.5, 2, 2, 1], ['P4', 1.0, 2, 2, 2], ['P3', 0.5, 2, 3, 1], ['P5', 1.0, 2, 3, 2]]
        item = ['C29', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        truncStructure = ['V', ['P1', 1.0, 1, 0, 0], ['P2', 1.0, 2, 1, 0], ['P3', 1.0, 2, 2, 1], ['P5', 0.5, 2, 2, 2], ['P4', 1.0, 2, 3, 1], ['P5', 0.5, 2, 3, 2]]
        item = ['C30', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        # --------------------------------

        nFacies = 5
        nPolygons = 6
        nGF = 3
        OPFacies = 'P5'
        BGFacies = ['P1', 'P2', 'P3', 'P4']
        trOPCenter = 1.0
        truncStructure = ['V', ['P1', 1.0, 1, 0, 0], ['P2', 1.0, 2, 1, 0], ['P3', 0.2, 2, 2, 1], ['P4', 1.0, 2, 2, 2], ['P3', 0.4, 2, 3, 1], ['P3', 0.4, 2, 3, 2]]
        item = ['C31', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        # -----   Non-cubic truncation rules  ---------------------------
        nPolygons = 2
        nFacies = 3
        nGF = 3
        OPFacies = 'P3'
        BGFacies = ['P1', 'P2']
        trOPCenter = 1.0
        truncStructure = [['P1', '45.0', 1.0], ['P2', '-45.0', 1.0]]
        item = ['A01', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        truncStructure = [['P1', '135.0', 1.0], ['P2', '-45.0', 1.0]]
        item = ['A02', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        # --------------------------------

        nPolygons = 3
        nFacies = 4
        nGF = 3
        OPFacies = 'P4'
        BGFacies = ['P1', 'P2', 'P3']
        trOPCenter = 1.0
        truncStructure = [['P1', '45.0', 1.0], ['P2', '75.0', 1.0], ['P3', '-180.0', 1.0]]
        item = ['A03', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        truncStructure = [['P1', '135.0', 1.0], ['P3', '-45.0', 1.0], ['P2', '45.0', 1.0]]
        item = ['A04', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        # --------------------------------

        nPolygons = 4
        nFacies = 5
        nGF = 3
        OPFacies = 'P5'
        BGFacies = ['P1', 'P2', 'P3', 'P4']
        trOPCenter = 1.0
        truncStructure = [['P1', '30.0', 1.0], ['P2', '60.0', 1.0], ['P3', '-120.0', 1.0], ['P4', '0.0', 1.0]]
        item = ['A05', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        truncStructure = [['P1', '45.0', 1.0], ['P4', '-135.0', 1.0], ['P2', '135.0', 1.0], ['P3', '-45.0', 1.0]]
        item = ['A06', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        truncStructure = [['P1', '60.0', 1.0], ['P2', '135.0', 1.0], ['P4', '-135.0', 1.0], ['P3', '-45.0', 1.0]]
        item = ['A07', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        truncStructure = [['P1', '135.0', 1.0], ['P2', '135.0', 1.0], ['P3', '135.0', 1.0], ['P4', '-45.0', 1.0]]
        item = ['A08', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        truncStructure = [['P4', '-90.0', 1.0], ['P3', '-135.0', 1.0], ['P1', '90.0', 1.0], ['P2', '0.0', 1.0]]
        item = ['A09', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        # --------------------------------

        nPolygons = 6
        nFacies = 6
        nGF = 3
        OPFacies = 'P6'
        BGFacies = ['P1', 'P2', 'P3', 'P4', 'P5']
        trOPCenter = 1.0
        truncStructure = [['P1', '30.0', 1.0], ['P2', '20.0', 1.0], ['P5', '180.0', 1.0], ['P3', '180.0', 0.5], ['P4', '45.0', 1.0], ['P3', '0.0', 0.5]]
        item = ['A10', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        # --------- Bayfill rule -------
        nPolygons = 5
        nFacies = 5
        nGF = 3
        OPFacies = ''
        BGFacies = []
        trOPCenter = 1.0
        truncStructure = [0.5, 0.5, 0.5]
        item = ['B01', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        return

    def getTruncStructure(self, faciesList, name):
        trStruct = None
        for trItem in self.__table:
            trRuleName = trItem[0]
            trStruct = trItem[3]
            if name == trRuleName:
                if trRuleName[0] == 'A':
                    for i in range(len(trStruct)):
                        item = trStruct[i]
                        polyName = item[0]
                        # print('PolyName: ' +polyName)
                        indx = int(polyName[1:]) - 1
                        item[0] = copy.copy(faciesList[indx])
                    # print('polyName: ' + polyName + ' Facies name: ' + item[0])
                elif trRuleName[0] == 'C':
                    for i in range(1, len(trStruct)):
                        item = trStruct[i]
                        polyName = item[0]
                        # print('PolyName: ' +polyName)
                        indx = int(polyName[1:]) - 1
                        item[0] = copy.copy(faciesList[indx])
                    # print('polyName: ' + polyName + ' Facies name: ' + item[0])
                break
        return trStruct

    def getTruncRuleNPoly(self, name):
        trStruct = None
        nPoly = -999
        for trItem in self.__table:
            trRuleName = trItem[0]
            trNPoly = trItem[1]
            trNFacies = trItem[2]
            trStruct = trItem[3]
            if name == trRuleName:
                nPoly = trNPoly
                break
        return nPoly

    def getTruncRuleNFacies(self, name):
        trStruct = None
        nFac = -999
        for trItem in self.__table:
            trRuleName = trItem[0]
            trNPoly = trItem[1]
            trNFacies = trItem[2]
            trStruct = trItem[3]
            if name == trRuleName:
                nFac = trNFacies
                break
        return nFac

    def getTruncRuleBackgroundFacies(self, faciesList, name):
        trStruct = None
        BGFaciesList = []
        found = 0
        for trItem in self.__table:
            trRuleName = trItem[0]
            bgFaciesList = trItem[5]
            if name == trRuleName:
                found = 1
                for i in range(len(bgFaciesList)):
                    polyName = bgFaciesList[i]
                    indx = int(polyName[1:]) - 1
                    # print('polyName: ' + polyName + ' indx: ' + str(indx))
                    bgFname = copy.copy(faciesList[indx])
                    BGFaciesList.append(bgFname)
                # print('polyName: ' + polyName + ' Background facies name: ' +bgFname)
                break
        if found:
            return BGFaciesList
        else:
            return None

    def getTruncRuleOverPrintFacies(self, faciesList, name):
        found = 0
        for trItem in self.__table:
            trRuleName = trItem[0]
            if name == trRuleName:
                found = 1
                polyName = trItem[4]
                # print('Overprint: ' + polyName)
                indx = int(polyName[1:]) - 1
                # print('Overprint indx: ' + str(indx))
                OPFacies = copy.copy(faciesList[indx])
        if found == 1:
            return OPFacies
        else:
            return None

    def getTruncRuleNames(self, nPolygonsInput, nFaciesInput):
        trStruct = None
        names = []
        for trItem in self.__table:
            trRuleName = trItem[0]
            trNPoly = trItem[1]
            trNFacies = trItem[2]
            trStruct = trItem[3]
            if trNPoly == nPolygonsInput and trNFacies == nFaciesInput:
                names.append(trRuleName)
        return names

    def getTruncRuleOverPrintCenter(self, name):
        found = 0
        for trItem in self.__table:
            trRuleName = trItem[0]
            if name == trRuleName:
                found = 1
                center = trItem[6]
        if found == 1:
            return center
        else:
            return None

        return

    def getTruncRuleNGaussFields(self, name):
        trStruct = None
        nFac = -999
        for trItem in self.__table:
            trRuleName = trItem[0]
            nGF = trItem[7]
            if name == trRuleName:
                break

        return nGF

    def getTruncRuleObject(self, mainFaciesTable, faciesList, printInfo, name):
        if name[0] == 'A':
            truncStructure = self.getTruncStructure(faciesList, name)
            overlayFacies = self.getTruncRuleOverPrintFacies(faciesList, name)
            backgroundFacies = self.getTruncRuleBackgroundFacies(faciesList, name)
            overlayTruncCenter = self.getTruncRuleOverPrintCenter(name)
            # print('Facies list:')
            # print(repr(faciesList))
            # print('Background facies list:')
            # print(repr(backgroundFacies))
            # print('Overlay facies: ' + overlayFacies)
            # print('Overlay trunc center: ' + str(overlayTruncCenter))
            # print('truncStructure:')
            # print(repr(truncStructure))
            useConstTruncParam = 1
            trRuleObj = Trunc2D_Angle_Overlay_xml.Trunc2D_Angle_Overlay()
            # print(repr(faciesList))
            # print('Overlay facies: ' + overlayFacies)
            trRuleObj.initialize(mainFaciesTable, faciesList, truncStructure,
                                 backgroundFacies, overlayFacies, overlayTruncCenter,
                                 useConstTruncParam, printInfo)
        elif name[0] == 'C':
            truncStructure = self.getTruncStructure(faciesList, name)
            overlayFacies = self.getTruncRuleOverPrintFacies(faciesList, name)
            backgroundFacies = self.getTruncRuleBackgroundFacies(faciesList, name)
            overlayTruncCenter = self.getTruncRuleOverPrintCenter(name)
            # print('Facies list:')
            # print(repr(faciesList))
            # print('Background facies list:')
            # print(repr(backgroundFacies))
            # print('Overlay facies: ' + overlayFacies)
            # print('Overlay trunc center: ' + str(overlayTruncCenter))
            # print('truncStructure:')
            # print(repr(truncStructure))
            useConstTruncParam = 1
            trRuleObj = Trunc2D_Angle_Overlay_xml.Trunc2D_Angle_Overlay()
            # print(repr(faciesList))
            # print('Overlay facies: ' + overlayFacies)

            trRuleObj = Trunc2D_Cubic_Overlay_xml.Trunc2D_Cubic_Overlay()
            trRuleObj.initialize(mainFaciesTable, faciesList, truncStructure,
                                 backgroundFacies, overlayFacies, overlayTruncCenter, printInfo)
        elif name.strip() == 'B01':
            useConstTruncParam = 1
            truncStructure = self.getTruncStructure(faciesList, name)
            # print('TruncStruct:')
            # print(repr(truncStructure))
            sf = truncStructure[0]
            ysf = truncStructure[1]
            sbhd = truncStructure[2]
            trRuleObj = Trunc3D_bayfill_xml.Trunc3D_bayfill()
            # print('B01: faciesList:')
            # print(repr(faciesList))
            trRuleObj.initialize(
                mainFaciesTable, faciesList, faciesList,
                sf, ' ', ysf, sbhd, useConstTruncParam, printInfo
            )

        else:
            print('Truncation rule: ' + name + ' is not implemented.')
            return None
        return trRuleObj


class DefineAngleTruncStructure:
    """
    Description: This class keep data to define truncation rules based on rule with non-cubic polygons
    defined by class Trunc2D_Angle_Overlay.
    """

    def __init__(self):

        self.__table = []
        self.__nRules = 5

        # --------------------------------

        nPolygons = 2
        nFacies = 2
        OPFacies = 'P3'
        BGFacies = ['P1', 'P2']
        trOPCenter = 1.0
        truncStructure = [['P1', '45.0', 1.0], ['P2', '-45.0', 1.0]]
        item = ['A01', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        truncStructure = [['P1', '135.0', 1.0], ['P2', '-45.0', 1.0]]
        item = ['A02', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        # --------------------------------

        nPolygons = 3
        nFacies = 3
        OPFacies = 'P4'
        BGFacies = ['P1', 'P2', 'P3']
        trOPCenter = 1.0
        truncStructure = [['P1', '45.0', 1.0], ['P2', '75.0', 1.0], ['P3', '-180.0', 1.0]]
        item = ['A03', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        truncStructure = [['P1', '135.0', 1.0], ['P3', '-45.0', 1.0], ['P2', '45.0', 1.0]]
        item = ['A04', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        # --------------------------------

        nPolygons = 4
        nFacies = 4
        OPFacies = 'P5'
        BGFacies = ['P1', 'P2', 'P3', 'P4']
        trOPCenter = 1.0
        truncStructure = [['P1', '30.0', 1.0], ['P2', '60.0', 1.0], ['P3', '-120.0', 1.0], ['P4', '0.0', 1.0]]
        item = ['A05', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        truncStructure = [['P1', '45.0', 1.0], ['P4', '-135.0', 1.0], ['P2', '135.0', 1.0], ['P3', '-45.0', 1.0]]
        item = ['A06', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        truncStructure = [['P1', '60.0', 1.0], ['P2', '135.0', 1.0], ['P4', '-135.0', 1.0], ['P3', '-45.0', 1.0]]
        item = ['A07', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        truncStructure = [['P1', '135.0', 1.0], ['P2', '135.0', 1.0], ['P3', '135.0', 1.0], ['P4', '-45.0', 1.0]]
        item = ['A08', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        truncStructure = [['P4', '-90.0', 1.0], ['P3', '-135.0', 1.0], ['P1', '90.0', 1.0], ['P2', '0.0', 1.0]]
        item = ['A09', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        # --------------------------------

        nPolygons = 6
        nFacies = 5
        OPFacies = 'P6'
        BGFacies = ['P1', 'P2', 'P3', 'P4', 'P5']
        trOPCenter = 1.0
        truncStructure = [['P1', '30.0', 1.0], ['P2', '20.0', 1.0], ['P5', '180.0', 1.0], ['P3', '180.0', 1.0], ['P4', '45.0', 1.0], ['P3', '0.0', 1.0]]
        item = ['A10', nPolygons, nFacies, truncStructure, OPFacies, BGFacies, trOPCenter, nGF]
        self.__table.append(item)

        # --------------------------------

        return

    def getTruncStructure(self, faciesList, name):
        trStruct = None
        for trItem in self.__table:
            trRuleName = trItem[0]
            trStruct = trItem[3]
            if name == trRuleName:
                for i in range(1, len(trStruct)):
                    item = trStruct[i]
                    polyName = item[0]
                    indx = int(polyName[1:]) - 1
                    print('polyName: ' + polyName + ' indx: ' + str(indx))
                    item[0] = copy.copy(faciesList[indx])
                    print('polyName: ' + polyName + ' Facies name: ' + item[0])
                    break
        return trStruct

    def getTruncRuleNPoly(self, name):
        trStruct = None
        nPoly = -999
        for trItem in self.__table:
            trRuleName = trItem[0]
            trNPoly = trItem[1]
            if name == trRuleName:
                nPoly = trNPoly
                break
        return nPoly

    def getTruncRuleNFacies(self, name):
        trStruct = None
        nFac = -999
        for trItem in self.__table:
            trRuleName = trItem[0]
            trNFacies = trItem[2]
            if name == trRuleName:
                nFac = trNFacies
                break
        return nFac

    def getTruncRuleBackgroundFacies(self, name):
        trStruct = None
        BGFaciesList = []
        found = 0
        for trItem in self.__table:
            trRuleName = trItem[0]
            bgFaciesList = trItem[5]
            if name == trRuleName:
                found = 1
                for i in range(len(bgFaciesList)):
                    polyName = bgFaciesList[i]
                    indx = int(polyName[1:]) - 1
                    # print('polyName: ' + polyName + ' indx: ' + str(indx))
                    bgFname = copy.copy(bgFaciesList[indx])
                    BGFaciesList.append(bgFname)
                    print('polyName: ' + polyName + ' Background facies name: ' + bgFname)
                break
        if found:
            return BGFaciesList
        else:
            return None

    def getTruncRuleOverPrintFacies(self, name):
        found = 0
        for trItem in self.__table:
            trRuleName = trItem[0]
            if name == trRuleName:
                found = 1
                OPFacies = copy.copy(trItem[4])
        if found == 1:
            return OPFacies
        else:
            return None

    def getTruncRuleNames(self, nPolygonsInput, nFaciesInput):
        trStruct = None
        names = []
        for trItem in self.__table:
            trRuleName = trItem[0]
            trNPoly = trItem[1]
            trNFacies = trItem[2]
            trStruct = trItem[3]
            if trNPoly == nPolygonsInput and trNFacies == nFaciesInput:
                names.append(trRuleName)
        return names
  
