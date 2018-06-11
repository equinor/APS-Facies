#!/bin/env python
# -*- coding: utf-8 -*-
from src.algorithms.defineTruncationRule import DefineTruncationRule
from src.utils.numeric import isNumber

def getInteger(text,minVal=0):
    ok = False
    n = 0
    while not ok:
        n_string = input(text)
        ok = isNumber(n_string)
        if ok:
            n = int(n_string)
            if n < minVal:
                print('Must be >= {}'.format(str(minVal)))
                ok = False
    return n

def addCommandCubic(rules):
    name = input('Give a name for the new Cubic truncation setting: ')
    direction = input('Split direction for level 1  (H/V): ')

    while direction != 'H' and direction != 'V' and direction != 'h' and direction != 'v':
        direction = input('Split direction for level 1  (H/V): ')

    nLevel1 = getInteger('Number of L1 polygons: ',minVal=2)
    nLevel2 = []
    nLevel3 = []
    for i in range(nLevel1):
        m = getInteger('Number of L2 polygons this L1 polygon ({}, {}, {}) is split into:'.format(str(i+1), 0, 0), minVal=0)
        if m == 0:
            m = 1
        nLevel2.append(m)        
        nLevel3.append([])
    for i in range(nLevel1):
        for j in range(nLevel2[i]):
            if nLevel2[i] <= 1:
                k = 1
            elif nLevel2[i] > 1:
                k = getInteger('Number of L3 polygons this L2 polygon ({}, {}, {}) is split into:'.format(str(i+1),str(j+1), 0),minVal=0)
                if k == 0:
                    k = 1
            nLevel3[i].append(k)

    truncStructureCubic = rules.initNewTruncationRuleSettingsCubic(direction)
    polygon_list = []
    for i in range(nLevel1):
        for j in range(nLevel2[i]):
            for k in range(nLevel3[i][j]):
                L1 = i+1
                L2 = j+1
                if nLevel2[i] == 1:
                    L2 = 0
                L3 = k+1
                if nLevel3[i][j] == 1:
                    L3 = 0

                fName = input('Facies name for polygon ({}, {}, {}): '
                              ''. format(str(L1), str(L2), str(L3)))
                ok = False
                while not ok:
                    probFrac_string = input('Probability fraction of facies {} in polygon ({}, {}, {}): '
                                     ''. format(fName, str(L1), str(L2), str(L3)))
                    probFrac = float(probFrac_string)
                    if probFrac >= 0.0 and probFrac <= 1.0:
                        ok = True

                rules.addPolygonToTruncationRuleSettingsCubic(truncStructureCubic, fName, probFrac, L1, L2, L3)

    rules.addTruncationRuleSettingsCubic(name, truncStructureCubic)


def addCommandNonCubic(rules):
    name = input('Give a name for the new Non-Cubic truncation setting: ')
    text = 'Number of polygons: '
    nPolygons = getInteger(text,minVal=2)

    truncStructureNonCubic = rules.initNewTruncationRuleSettingsNonCubic()
    polygon_list = []
    for i in range(nPolygons):
        fName = input('Facies name for polygon number {}: '
                              ''. format(str(i+1)))

        angle = 0.0
        probFrac = 1.0
        ok = False
        while not ok:
            tmp_string = input('Angle: ')
            try:
                angle = float(tmp_string)
                if angle < -180.0 or angle > 180.0:
                    print('Angle must be in interval [-180.0, 180.0] degrees')
                else:
                    ok = True
            except:
                ok = False

        ok = False
        while not ok:
            tmp_string = input('Probability fraction: ')
            try:
                probFrac = float(tmp_string)
                if probFrac < 0.0 or probFrac> 1.0:
                    print('Probability fraction must be in interval [0.0, 1.0]')
                else:
                    ok = True
            except:
                ok = False


        poly = [fName, angle, probFrac]
        rules.addPolygonToTruncationRuleSettingsNonCubic(truncStructureNonCubic, fName, angle, probFrac)
        
    rules.addTruncationRuleSettingsNonCubic(name, truncStructureNonCubic)

def addCommandOverlay(rules):
    name = input('Give a name for the new Overlay truncation setting: ')
    text = 'Number of overlay groups'
    nGroups = getInteger(text,minVal=1)
    group_list = []
    for groupIndx in range(nGroups):
        text = 'Number of polygons for group {}: '.format(str(groupIndx+1))
        nPoly = getInteger(text,minVal=1)
        alphaList = []
        bgFaciesList = []
        for i in range(nPoly):
            faciesName = input('Facies name for {} and polygon {}...............: '.format(str(groupIndx+1), str(i+1)))
            alphaName  = input('GRF name for {} and polygon {}..................: '.format(str(groupIndx+1), str(i+1)))
            text       = input('Probability fraction for {} and polygon {}......: '.format(str(groupIndx+1), str(i+1)))
            probFrac = float(text)
            text       = input('Center point of interval for {} and polygon {}..: '.format(str(groupIndx+1), str(i+1)))
            centerPoint = float(text)
            alphaList = rules.addPolygonToAlphaList(alphaName, faciesName, probFrac=probFrac, centerPoint=centerPoint, alphaList=alphaList)
        text = ' Number of background facies for group {}'.format(str(groupIndx+1)) 
        nBackgroundFacies = getInteger(text,minVal=1)
        bgFacies = input('Background facies for group {} : '.format(str(groupIndx+1)))
        bgFaciesList.append(bgFacies)
        group_list = rules.addOverlayGroupSettings(alphaList, bgFaciesList, overlayGroups=group_list)

    rules.addTruncationRuleSettingsOverlay(name, group_list)


def addCommandCubicAndOverlay(rules):
    name = input('Give a name for the new Cubic truncation setting with overlay facies: ')
    cubicName = input('Name of Cubic setting: ')
    
    list_overlay_settings = rules.getListOfOverlaySettings(cubicName)
    print('Overlay settings consistent with specified background facies setting.')
    for i in range(len(list_overlay_settings)):
        nameOverlay = list_overlay_settings[i]
        print(nameOverlay)

    finished = False
    while not finished:
        overlayName = input('Name of Overlay setting: ')
        if overlayName in list_overlay_settings:
            finished = True
            
    rules.addTruncationRuleSettingsCubicWithOverlay(name, cubicName, overlayName)

def addCommandNonCubicAndOverlay(rules):
    name = input('Give a name for the new NonCubic truncation setting with overlay facies: ')
    nonCubicName = input('Name of NonCubic setting: ')
    list_overlay_settings = rules.getListOfOverlaySettings(nonCubicName)
    print('Overlay settings consistent with specified background facies setting.')
    for i in range(len(list_overlay_settings)):
        nameOverlay = list_overlay_settings[i]
        print(nameOverlay)

    finished = False
    while not finished:
        overlayName = input('Name of Overlay setting: ')
        if overlayName in list_overlay_settings:
            finished = True
            
    rules.addTruncationRuleSettingsNonCubicWithOverlay(name, nonCubicName, overlayName)


def addCommand(rules):
    finished = False
    while not finished:
        typeTrunc = input('Add truncation setting for:\n'
                          '  Cubic (C)\n'
                          '  NonCubic (N)\n'
                          '  Overlay (A)\n'
                          '  CubicAndOverlay (CA)\n'
                          '  NonCubicAndOverlay (NA)\n'
                          '  :')
        if typeTrunc == 'Cubic' or typeTrunc == 'C' or typeTrunc == 'c':
            addCommandCubic(rules)
            finished = True
        elif typeTrunc == 'NonCubic' or typeTrunc == 'N' or typeTrunc == 'n':
            addCommandNonCubic(rules)
            finished = True
        elif typeTrunc == 'Overlay' or typeTrunc == 'A' or typeTrunc == 'a':
            addCommandOverlay(rules)
            finished = True
        elif typeTrunc == 'CubicAndOverlay' or typeTrunc == 'CA' or typeTrunc == 'ca':
            addCommandCubicAndOverlay(rules)
            finished = True
        elif typeTrunc == 'NonCubicAndOverlay' or typeTrunc == 'NA' or typeTrunc == 'na':
            addCommandNonCubicAndOverlay(rules)
            finished = True

def readCommand(rules):
    finished = False
    while not finished:
        try:
            inputFileName = input('Specify filename or quit (q): ')
            if inputFileName == 'q':
                finished = True
            else:
                rules.readFile(inputFileName)
                print('')
                finished = True
        except:
            print('Can not open or read the file {}'. format(inputFileName))
    
def printListOfSettings(settings_list):
    for i in range(len(settings_list)):
        item = settings_list[i]
        key = item[0]
        print('{}'.format(key))
    print('')


def listCommand(rules):
    finished = False
    while not finished:
        typeTrunc = input('Type of truncation settings to list to screen:\n'
                          '  Cubic (C)\n'
                          '  NonCubic (N)\n'
                          '  Cubic with overlay (CA)\n'
                          '  NonCubic with overlay (NA)\n'
                          '  Overlay (A)\n'
                          '  Background with N facies and overlay with M facies  (B)\n'
                          '  :')
        if typeTrunc == 'Cubic' or typeTrunc == 'C' or typeTrunc == 'c':
            typeTrunc = 'Cubic'
            settings_list = rules.getListOfSettings(typeTrunc)

            print('Cubic truncation settings:')
            printListOfSettings(settings_list)
            finished = True

        elif typeTrunc == 'NonCubic' or typeTrunc == 'N' or typeTrunc == 'n':
            typeTrunc = 'NonCubic'
            settings_list = rules.getListOfSettings(typeTrunc)

            print('NonCubic truncation settings:')
            printListOfSettings(settings_list)
            finished = True

        elif typeTrunc == 'CubicAndOverlay' or typeTrunc == 'CA' or typeTrunc == 'ca':
            typeTrunc = 'CubicAndOverlay'
            settings_list = rules.getListOfSettings(typeTrunc)

            print('Cubic truncation settings with overlay facies:')
            printListOfSettings(settings_list)
            finished = True

        elif typeTrunc == 'NonCubicAndOverlay' or typeTrunc == 'NA' or typeTrunc == 'na':
            typeTrunc = 'NonCubicAndOverlay'
            settings_list = rules.getListOfSettings(typeTrunc)

            print('NonCubic truncation settings with overlay facies:')
            printListOfSettings(settings_list)
            finished = True

        elif typeTrunc == 'Overlay' or typeTrunc == 'A' or typeTrunc == 'a':
            typeTrunc = 'Overlay'
            settings_list = rules.getListOfSettings(typeTrunc)

            print('Overlay truncation settings:')
            printListOfSettings(settings_list)
            finished = True

        elif typeTrunc == 'B' or typeTrunc == 'b':
            ok = False
            nBG = 0
            nOL = 0
            while not ok:
                tmp_string = input('Number of background facies:')
                try:
                    nBG = int(tmp_string)
                    if nBG > 0:
                        ok = True
                except:
                    ok = False

            ok = False
            while not ok:
                tmp_string = input('Number of overlay facies:')
                try:
                    nOL = int(tmp_string)
                    if nOL >= 0:
                        ok = True
                except:
                    ok = False

            settings_list_cubic = []
            settings_list_noncubic = []
            settings_list_cubic_overlay = []
            settings_list_noncubic_overlay = []
            if nOL == 0:
                typeTrunc = 'Cubic'
                settings_list_cubic = rules.getListOfSettings(typeTrunc, nBG)

                typeTrunc = 'NonCubic'
                settings_list_noncubic = rules.getListOfSettings(typeTrunc, nBG)
            else:
                typeTrunc = 'CubicAndOverlay'
                settings_list_cubic_overlay = rules.getListOfSettings(typeTrunc, nBG, nOL)

                typeTrunc = 'NonCubicAndOverlay'
                settings_list_noncubic_overlay = rules.getListOfSettings(typeTrunc, nBG, nOL)

            print('\nLists of truncation settings with {} background facies and {} overlay facies'
                  ''.format(str(nBG), str(nOL)))
            if len(settings_list_cubic) > 0:
                printListOfSettings(settings_list_cubic)
            if len(settings_list_noncubic) > 0:
                printListOfSettings(settings_list_noncubic)
            if len(settings_list_cubic_overlay) > 0:
                printListOfSettings(settings_list_cubic_overlay)
            if len(settings_list_noncubic_overlay) > 0:
                printListOfSettings(settings_list_noncubic_overlay)
            finished = True

        else:
            finished = True


def mapCommand(rules):
    finished = False
    while not finished:
        name = input('Plot all settings (A)\n'
                     'Plot specific setting, give name\n'
                     'Quit (Q) : ')
        
        if name == 'Q' or name == 'q' or name == 'Quit' or name == 'quit':
            finished = True
        elif name == 'A' or name == 'a':
            rules.createAllCubicPlots()
            rules.createAllNonCubicPlots()
            rules.createAllCubicWithOverlayPlots()
            rules.createAllNonCubicWithOverlayPlots()
        else:
            rules.makeTruncationMapPlot(name, writePngFile=False)
        
def removeCommand(rules):
    finished = False
    while not finished:
        name = input('Name of rule to remove: \n'
                     'Quit (Q): ')
        
        if name == 'Q' or name == 'q' or name == 'Quit' or name == 'quit':
            finished = True
        else:
            try:
                rules.removeTruncationRuleSettings(name, removeDependentBG=True, removeDependentOL=True)
                finished = True
            except:
                finished = False

def run():

    rules = DefineTruncationRule()

    finished = False
    while not finished:
        command = input('Specify command:\n'
                        '  Read from file (R)\n'
                        '  Write file (W)\n'
                        '  List rules (L)\n'
                        '  Show truncation map (M)\n'
                        '  Add new setting (N)\n'
                        '  Remove setting (Del)\n'
                        '  Quit\n'
                        '  :') 
        if command == 'Quit' or command == 'Q' or command == 'q':
            finished = True
        elif command == 'New' or command == 'N' or command == 'n':
            addCommand(rules)
        elif command == 'Read' or command == 'R' or command == 'r':
            readCommand(rules)
        elif command == 'Del':
            removeCommand(rules)
        elif command == 'Map'or command == 'M' or command == 'm':
            mapCommand(rules)
        elif command == 'List' or command == 'L' or command == 'l':
            listCommand(rules)
        elif command == 'Write' or command == 'W' or command == 'w':
            outputFile = input('Name of file to save/update truncation settings: ')
            rules.writeFile(outputFile)
                

if __name__ == '__main__':
    run()
