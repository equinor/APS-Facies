#!/bin/env python
# -*- coding: utf-8 -*-
from aps.algorithms.defineTruncationRule import DefineTruncationRule
from aps.unit_test.helpers import assert_identical_files, assert_equal_image_content_files


def test_create_cubic_rules():
    list_dir = ['H', 'V', 'H', 'V', 'V', 'V', 'H', 'H']
    list_nPoly = [3, 4, 5, 5, 6, 4, 5, 5]
    list_level = [
        [[1, 0, 0], [2, 1, 0], [2, 2, 0]],
        [[1, 1, 0], [1, 2, 0], [2, 1, 0], [2, 2, 0]],
        [[1, 0, 0], [2, 1, 1], [2, 1, 2], [2, 2, 0], [3, 0, 0]],
        [[1, 1, 1], [1, 1, 2], [1, 1, 3], [1, 2, 0], [2, 0, 0]],
        [[1, 0, 0], [2, 1, 1], [2, 1, 2], [2, 2, 0], [2, 3, 0], [3, 0, 0]],
        [[1, 0, 0], [2, 0, 0], [3, 1, 0], [3, 2, 0]],
        [[1, 0, 0], [2, 1, 1], [2, 1, 2], [2, 1, 3], [2, 2, 0]],
        [[1, 1, 0], [1, 2, 0], [2, 1, 1], [2, 1, 2], [2, 2, 0]],
    ]
    list_facies_per_polygon = ['F01', 'F02', 'F03', 'F04', 'F05', 'F06']
    prob_frac_per_polygon = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

    truncRuleDir = ''
    rules = DefineTruncationRule(truncRuleDir)

    for i in range(len(list_nPoly)):
        direction = list_dir[i]
        truncStructureCubic = rules.initNewTruncationRuleSettingsCubic(direction)
        nPoly = list_nPoly[i]
        levels_per_setting = list_level[i]
        for j in range(nPoly):
            fName = list_facies_per_polygon[j]
            probFrac = prob_frac_per_polygon[j]
            levels_per_polygon = levels_per_setting[j]
            L1 = levels_per_polygon[0]
            L2 = levels_per_polygon[1]
            L3 = levels_per_polygon[2]
            rules.addPolygonToTruncationRuleSettingsCubic(truncStructureCubic, fName, probFrac, L1, L2, L3)
        nameBG = f'C0{i + 1}'
        rules.addTruncationRuleSettingsCubic(nameBG, truncStructureCubic)

    outFile = 'Cubic_out.dat'
    reference_file = 'testData_trunc_settings/Cubic_reference.dat'
    rules.writeFile(outFile)

    # Compare with reference data
    assert_identical_files(outFile, reference_file)


def test_create_non_cubic_rules():
    list_nPoly = [3, 4, 5, 5, 5, 6]
    list_angle = [
        [0.0, 45.0, -45.0],
        [50.0, -135.0, 120.0, 30.0],
        [45.0, -12.0, 67.0, -35.0, 145.0],
        [0.0, 10.0, 20.0, 30.0, 40.0],
        [-10.0, 25.0, 120.0, -130.0, 140.0],
        [10.0, -25.0, -120.0, -130.0, 140.0, 134.0],
    ]

    list_facies_per_polygon = ['F01', 'F02', 'F03', 'F04', 'F05', 'F06']
    prob_frac_per_polygon = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

    truncRuleDir = ''
    rules = DefineTruncationRule(truncRuleDir)

    for i in range(len(list_nPoly)):
        truncStructureNonCubic = rules.initNewTruncationRuleSettingsNonCubic()
        nPoly = list_nPoly[i]
        angles_per_setting = list_angle[i]
        for j in range(nPoly):
            fName = list_facies_per_polygon[j]
            probFrac = prob_frac_per_polygon[j]
            angle = angles_per_setting[j]
            rules.addPolygonToTruncationRuleSettingsNonCubic(truncStructureNonCubic, fName, angle, probFrac)
        nameBG = f'N0{i + 1}'
        rules.addTruncationRuleSettingsNonCubic(nameBG, truncStructureNonCubic)

    # rules.createOverviewPlotCubic('Cubic_rules_test')
    outFile = 'NonCubic_out.dat'
    reference_file = 'testData_trunc_settings/NonCubic_reference.dat'
    rules.writeFile(outFile)

    # Compare with reference data
    assert_identical_files(outFile, reference_file)


def test_create_cubic_rules_with_overlay():
    list_dir = ['H', 'V', 'H', 'V', 'V']
    list_nPoly = [3, 4, 5, 5, 6]
    list_level = [
        [[1, 0, 0], [2, 1, 0], [2, 2, 0]],
        [[1, 1, 0], [1, 2, 0], [2, 1, 0], [2, 2, 0]],
        [[1, 0, 0], [2, 1, 1], [2, 1, 2], [2, 2, 0], [3, 0, 0]],
        [[1, 1, 1], [1, 1, 2], [1, 1, 3], [1, 2, 0], [2, 0, 0]],
        [[1, 0, 0], [2, 1, 1], [2, 1, 2], [2, 2, 0], [2, 3, 0], [3, 0, 0]],
    ]
    list_facies_per_polygon = ['F01', 'F02', 'F03', 'F04', 'F05', 'F06']
    prob_frac_per_polygon = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

    truncRuleDir = ''
    rules = DefineTruncationRule(truncRuleDir)

    for i in range(len(list_nPoly)):
        direction = list_dir[i]
        truncStructureCubic = rules.initNewTruncationRuleSettingsCubic(direction)
        nPoly = list_nPoly[i]
        levels_per_setting = list_level[i]
        for j in range(nPoly):
            fName = list_facies_per_polygon[j]
            probFrac = prob_frac_per_polygon[j]
            levels_per_polygon = levels_per_setting[j]
            L1 = levels_per_polygon[0]
            L2 = levels_per_polygon[1]
            L3 = levels_per_polygon[2]
            rules.addPolygonToTruncationRuleSettingsCubic(truncStructureCubic, fName, probFrac, L1, L2, L3)
        nameBG = f'C0{i + 1}'
        rules.addTruncationRuleSettingsCubic(nameBG, truncStructureCubic)

    list_nGroups_per_setting = [1, 2, 1, 3]
    list_nPoly_per_group_per_setting = [[1], [1, 1], [1], [1, 2, 1]]
    list_bg_facies_per_group_per_setting = [[['F01']], [['F01'], ['F02']], [['F02']], [['F01'], ['F02'], ['F03']]]
    list_overlay_facies_per_polygon_per_group = [
        [['S01']], [['S01'], ['S02']], [['S03']],
        [['S01'], ['S01', 'S01'], ['S01']],
    ]
    list_probFrac_per_polygon_per_group = [[[1.0]], [[1.0], [1.0]], [[1.0]], [[0.35], [0.30, 0.20], [0.15]]]
    list_center_interval_per_polygon_per_group = [[[0.0]], [[0.0], [0.0]], [[0.5]], [[1.0], [0.0, 0.0], [0.0]]]

    for i in range(len(list_nGroups_per_setting)):
        nGroups = list_nGroups_per_setting[i]
        nPoly_per_group = list_nPoly_per_group_per_setting[i]
        overlay_facies_per_polygon_per_group = list_overlay_facies_per_polygon_per_group[i]
        probFrac_per_polygon_per_group = list_probFrac_per_polygon_per_group[i]
        center_interval_per_polygon_per_group = list_center_interval_per_polygon_per_group[i]
        bg_facies_per_group = list_bg_facies_per_group_per_setting[i]
        overlayGroups = []
        for j in range(nGroups):
            nPoly = nPoly_per_group[j]
            overlay_facies_per_polygon = overlay_facies_per_polygon_per_group[j]
            probFrac_per_polygon = probFrac_per_polygon_per_group[j]
            center_interval_per_polygon = center_interval_per_polygon_per_group[j]
            bg_facies_list = bg_facies_per_group[j]
            alphaList = []
            for k in range(nPoly):
                grfName = 'GRF0' + str(k + 3)
                fName = overlay_facies_per_polygon[k]
                probFrac = probFrac_per_polygon[k]
                center_interval = center_interval_per_polygon[k]
                alphaList = rules.addPolygonToAlphaList(grfName, fName, probFrac, center_interval, alphaList)

            overlayGroups = rules.addOverlayGroupSettings(alphaList, bg_facies_list, overlayGroups)
        nameOL = 'A0' + str(i + 1)
        rules.addTruncationRuleSettingsOverlay(nameOL, overlayGroups)

    for i in range(len(list_nPoly)):
        nameBG = 'C0' + str(i + 1)
        for j in range(len(list_nGroups_per_setting)):
            nameOL = 'A0' + str(j + 1)
            name = nameBG + '_' + nameOL
            rules.addTruncationRuleSettingsCubicWithOverlay(name, nameBG, nameOL, replace=False)

    outFile = 'Cubic_with_overlay_out.dat'
    reference_file = 'testData_trunc_settings/Cubic_with_overlay_reference.dat'
    rules.writeFile(outFile)

    # Compare with reference data
    assert_identical_files(outFile, reference_file)

    # Create plots and check them
    plotFileName = 'Created_truncation_maps_cubic'
    out_plot_file = plotFileName + '.png'
    ref_plot_file = 'testData_trunc_settings/Created_truncation_maps_cubic_reference.png'

    rules.createOverviewPlotCubic(plotFileName)

    # Compare with reference data


    plotFileName = 'Created_truncation_maps_cubic_overlay'
    out_plot_file = plotFileName + '.png'
    ref_plot_file = 'testData_trunc_settings/Created_truncation_maps_cubic_overlay_reference.png'

    rules.createOverviewPlotCubicWithOverlay(plotFileName)
    # Compare with reference data



def test_write_read():
    directory = 'testData_trunc_settings'
    outFile = 'trunc_rules_out.dat'
    refFile = 'truncation_settings_reference.dat'
    reference_file = directory + '/' + refFile
    out_file = directory + '/' + outFile
    rules = DefineTruncationRule(directory)
    rules.readFile(refFile)
    rules.writeFile(outFile)

    # Compare with reference data
    assert_identical_files(out_file, reference_file)


def test_create_plots():
    refFile = 'testData_trunc_settings/truncation_settings_reference.dat'
    rules = DefineTruncationRule('')
    rules.readFile(refFile)

    plotFileName = 'Overview_truncation_maps'
    out_plot_file = plotFileName + '.png'
    ref_plot_file = 'testData_trunc_settings/Overview_truncation_maps_reference.png'

    rules.createOverviewPlotCubic(plotFileName)

    # Compare with reference data



def run():
    # ---------  Main ----------
    print('Start test_defineTruncSetting')
    test_create_cubic_rules()
    test_create_non_cubic_rules()
    test_create_cubic_rules_with_overlay()
    test_write_read()



if __name__ == '__main__':
    run()
