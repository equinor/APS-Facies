#!/bin/env python
# -*- coding: utf-8 -*-
import os
from aps.algorithms.defineTruncationRule import DefineTruncationRule
from aps.utils.numeric import isNumber


def getInteger(text, minVal=0):
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


def get_numeric_value_from_user(prompt, min=0, max=1):
    has_number = False
    value = None

    while not has_number:
        try:
            value = int(input(prompt))
        except ValueError:
            print('That is not a valid number')
        if min <= value <= max:
            has_number = True
        else:
            print('The number given, has to be between {}, and {}'.format(min, max))
    return value


def addCommandBayfill(rules):
    name = input('Give a name for the new Bayfill truncation setting: ')
    spec = [name]
    for key, prompt in [
        ('SF', 'Please give SF (between 0, and 1): '),
        ('YSF', 'Please give YSF (between 0, and 1): '),
        (None, None),
        ('SBHD', 'Please give SBHD (between 0, and 1): '),
        (None, None),
    ]:
        facies = input('Please provide the name of a facies')
        if key and prompt:
            spec.append([facies, key, get_numeric_value_from_user(prompt)])
    rules.addTruncationRuleSettingsBayfill(name, spec)


def addCommandCubic(rules):
    name = input('Give a name for the new Cubic truncation setting: ')
    direction = input('Split direction for level 1  (H/V): ')

    while direction != 'H' and direction != 'V' and direction != 'h' and direction != 'v':
        direction = input('Split direction for level 1  (H/V): ')

    nLevel1 = getInteger('Number of L1 polygons: ', minVal=2)
    nLevel2 = []
    nLevel3 = []
    for i in range(nLevel1):
        m = getInteger('Number of L2 polygons this L1 polygon ({}, {}, {}) is split into:'.format(i + 1, 0, 0), minVal=0)
        if m == 0:
            m = 1
        nLevel2.append(m)
        nLevel3.append([])
    for i in range(nLevel1):
        for j in range(nLevel2[i]):
            if nLevel2[i] <= 1:
                k = 1
            elif nLevel2[i] > 1:
                k = getInteger('Number of L3 polygons this L2 polygon ({}, {}, {}) is split into:'.format(i + 1, j + 1, 0), minVal=0)
                if k == 0:
                    k = 1
            nLevel3[i].append(k)

    truncStructureCubic = rules.initNewTruncationRuleSettingsCubic(direction)
    for i in range(nLevel1):
        for j in range(nLevel2[i]):
            for k in range(nLevel3[i][j]):
                L1 = i + 1
                L2 = j + 1
                if nLevel2[i] == 1:
                    L2 = 0
                L3 = k + 1
                if nLevel3[i][j] == 1:
                    L3 = 0

                fName = input('Facies name for polygon ({}, {}, {}): '. format(L1, L2, L3))
                ok = False
                while not ok:
                    probFrac_string = input(
                        'Probability fraction of facies {} in polygon ({}, {}, {}): '
                        ''. format(fName, L1, L2, L3))
                    probFrac = float(probFrac_string)
                    if 0.0 <= probFrac <= 1.0:
                        ok = True

                rules.addPolygonToTruncationRuleSettingsCubic(truncStructureCubic, fName, probFrac, L1, L2, L3)

    rules.addTruncationRuleSettingsCubic(name, truncStructureCubic)


def addCommandNonCubic(rules):
    name = input('Give a name for the new Non-Cubic truncation setting: ')
    text = 'Number of polygons: '
    nPolygons = getInteger(text,minVal=2)

    truncStructureNonCubic = rules.initNewTruncationRuleSettingsNonCubic()
    for i in range(nPolygons):
        fName = input('Facies name for polygon number {}: '. format(i + 1))

        angle = 0.0
        probFrac = 1.0
        ok = False
        while not ok:
            tmp_string = input('Angle: ')
            try:
                angle = float(tmp_string)
                if not (-180.0 <= angle <= 180.0):
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
                if not (0.0 <= probFrac <= 1.0):
                    print('Probability fraction must be in interval [0.0, 1.0]')
                else:
                    ok = True
            except:
                ok = False

        rules.addPolygonToTruncationRuleSettingsNonCubic(truncStructureNonCubic, fName, angle, probFrac)

    rules.addTruncationRuleSettingsNonCubic(name, truncStructureNonCubic)


def addCommandOverlay(rules):
    name = input('Give a name for the new Overlay truncation setting: ')
    text = 'Number of overlay groups'
    nGroups = getInteger(text, minVal=1)
    group_list = []
    for groupIndx in range(nGroups):
        text = 'Number of polygons for group {}: '.format(str(groupIndx+1))
        nPoly = getInteger(text, minVal=1)
        alphaList = []
        bgFaciesList = []
        for i in range(nPoly):
            faciesName = input('Facies name for {} and polygon {}...............: '.format(groupIndx + 1, i + 1))
            alphaName  = input('GRF name for {} and polygon {}..................: '.format(groupIndx + 1, i + 1))
            text       = input('Probability fraction for {} and polygon {}......: '.format(groupIndx + 1, i + 1))
            probFrac = float(text)
            text       = input('Center point of interval for {} and polygon {}..: '.format(groupIndx + 1, i + 1))
            centerPoint = float(text)
            alphaList = rules.addPolygonToAlphaList(
                alphaName, faciesName, probFrac=probFrac, centerPoint=centerPoint, alphaList=alphaList
            )
        text = ' Number of background facies for group {}'.format(groupIndx + 1)
        bgFacies = input('Background facies for group {} : '.format(groupIndx + 1))
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
        typeTrunc = input(
            'Add truncation setting for:\n'
            '  Bayfill (B)\n'
            '  Cubic (C)\n'
            '  NonCubic (N)\n'
            '  Overlay (A)\n'
            '  CubicAndOverlay (CA)\n'
            '  NonCubicAndOverlay (NA)\n'
            '  :'
        )
        if typeTrunc.lower() in ['bayfill', 'b']:
            addCommandBayfill(rules)
            finished = True
        elif typeTrunc in ['Cubic', 'C', 'c']:
            addCommandCubic(rules)
            finished = True
        elif typeTrunc in ['NonCubic', 'N', 'n']:
            addCommandNonCubic(rules)
            finished = True
        elif typeTrunc in ['Overlay', 'A', 'a']:
            addCommandOverlay(rules)
            finished = True
        elif typeTrunc in ['CubicAndOverlay', 'CA', 'ca']:
            addCommandCubicAndOverlay(rules)
            finished = True
        elif typeTrunc in ['NonCubicAndOverlay', 'NA', 'na']:
            addCommandNonCubicAndOverlay(rules)
            finished = True


def readCommand(rules):
    finished = False
    while not finished:
            input_file_name = input('Specify filename or quit (q): ')
            if input_file_name == 'q':
                finished = True
            else:
                try:
                    rules.readFile(input_file_name)
                    print('')
                    finished = True
                except (FileNotFoundError, IOError):
                    print('Can not open or read the file {}'. format(input_file_name))


def printListOfSettings(settings_list):
    for i in range(len(settings_list)):
        item = settings_list[i]
        key = item[0]
        print('{}'.format(key))
    print('')


def listCommand(rules):
    finished = False
    while not finished:
        typeTrunc = input(
            'Type of truncation settings to list to screen:\n'
            '  Bayfill (B)\n'
            '  Cubic (C)\n'
            '  NonCubic (N)\n'
            '  Cubic with overlay (CA)\n'
            '  NonCubic with overlay (NA)\n'
            '  Overlay (A)\n'
            '  Background with N facies and overlay with M facies  (B)\n'
            '  :'
        )
        if typeTrunc.lower() in ['bayfill', 'b']:
            typeTrunc = 'Bayfill'
            settings_list = rules.getListOfOverlaySettings(typeTrunc)

        if typeTrunc in ['Cubic', 'C', 'c']:
            typeTrunc = 'Cubic'
            settings_list = rules.getListOfSettings(typeTrunc)

            print('Cubic truncation settings:')
            printListOfSettings(settings_list)
            finished = True

        elif typeTrunc in ['NonCubic', 'N', 'n']:
            typeTrunc = 'NonCubic'
            settings_list = rules.getListOfSettings(typeTrunc)

            print('NonCubic truncation settings:')
            printListOfSettings(settings_list)
            finished = True

        elif typeTrunc in ['CubicAndOverlay', 'CA', 'ca']:
            typeTrunc = 'CubicAndOverlay'
            settings_list = rules.getListOfSettings(typeTrunc)

            print('Cubic truncation settings with overlay facies:')
            printListOfSettings(settings_list)
            finished = True

        elif typeTrunc in ['NonCubicAndOverlay', 'NA', 'na']:
            typeTrunc = 'NonCubicAndOverlay'
            settings_list = rules.getListOfSettings(typeTrunc)

            print('NonCubic truncation settings with overlay facies:')
            printListOfSettings(settings_list)
            finished = True

        elif typeTrunc in ['Overlay', 'A', 'a']:
            typeTrunc = 'Overlay'
            settings_list = rules.getListOfSettings(typeTrunc)

            print('Overlay truncation settings:')
            printListOfSettings(settings_list)
            finished = True

        elif typeTrunc in ['B', 'b']:
            ok = False
            nBG = 0
            nOL = 0
            while not ok:
                tmp_string = input('Number of background facies:')
                try:
                    nBG = int(tmp_string)
                    if nBG > 0:
                        ok = True
                except ValueError:
                    ok = False

            ok = False
            while not ok:
                tmp_string = input('Number of overlay facies:')
                try:
                    nOL = int(tmp_string)
                    if nOL >= 0:
                        ok = True
                except ValueError:
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
        name = input(
            'Plot all settings (A)\n'
            'Plot specific setting, give name\n'
            'Quit (Q) : '
        )

        if name in ['Q', 'q', 'Quit', 'quit']:
            finished = True
        elif name in ['A', 'a']:
            rules.createAllBayfillPlots()
            rules.createAllCubicPlots()
            rules.createAllNonCubicPlots()
            if rules.write_overlay:
                rules.createAllCubicWithOverlayPlots()
                rules.createAllNonCubicWithOverlayPlots()
            if rules.write_overview:
                rules.createOverviewPlotCubic('Cubic_overview')
                rules.createOverviewPlotNonCubic('NonCubic_overview')

        else:
            rules.makeTruncationMapPlot(name, writePngFile=False)


def removeCommand(rules):
    finished = False
    while not finished:
        name = input(
            'Name of rule to remove: \n'
            'Quit (Q): '
        )

        if name in ['Q', 'q', 'Quit', 'quit']:
            finished = True
        else:
            try:
                rules.removeTruncationRuleSettings(name, removeDependentBG=True, removeDependentOL=True)
                finished = True
            except:
                finished = False


def run():
    show_title = not is_affirmative('HIDE_TITLE')
    write_overlay = not is_affirmative('DONT_WRITE_OVERLAY')
    write_overview = not is_affirmative('DONT_WRITE_OVERVIEW')
    write_to_directories = is_affirmative('WRITE_TO_DIRECTORIES')

    rules = DefineTruncationRule(
        show_title=show_title,
        write_overlay=write_overlay,
        write_overview=write_overview,
        write_to_directories=write_to_directories,
    )

    finished = False
    while not finished:
        command = input(
            'Specify command:\n'
            '  Read from file (R)\n'
            '  Write file (W)\n'
            '  List rules (L)\n'
            '  Show truncation map (M)\n'
            '  Add new setting (N)\n'
            '  Remove setting (Del)\n'
            '  Quit\n'
            '  :'
        )
        if command in ['Quit', 'Q', 'q']:
            finished = True
        elif command in ['New', 'N', 'n']:
            addCommand(rules)
        elif command in ['Read', 'R', 'r']:
            readCommand(rules)
        elif command == 'Del':
            removeCommand(rules)
        elif command in ['Map', 'M', 'm']:
            mapCommand(rules)
        elif command in ['List', 'L', 'l']:
            listCommand(rules)
        elif command in ['Write', 'W', 'w']:
            outputFile = input('Name of file to save/update truncation settings: ')
            rules.writeFile(outputFile)


def is_affirmative(name):
    return os.environ.get(name, '').lower() in ['1', 'y', 'yes', 'true']


if __name__ == '__main__':
    run()
