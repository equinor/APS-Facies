#!/bin/env python
# -*- coding: utf-8 -*-
# Python3 script to update APS model file from global IPL include file

from src.algorithms.APSModel import APSModel
from src.utils.constants.simple import Debug, VariogramType, TrendType


def get_list_of_aps_uncertainty_parameters(project, workflow_name):
    wf = project.workflows[workflow_name]
    param_list = []
    for param in wf.uncertainty_parameters:
        name = param.name
        words = name.split('_')
        if words[0] == 'APS':
            param_list.append(param.name)
    return param_list


def read_selected_fmu_variables(input_selected_fmu_variable_file):
    fmu_variables = []
    with open(input_selected_fmu_variable_file, 'r') as file:
        finished = False
        while not finished:
            line = file.readline()
            if line == '':
                finished = True
            else:
                words = line.split('_')
                zone = int(words[1])
                region = int(words[2])
                keyword = words[3]
                if keyword == 'GF':
                    gauss_name = words[4].strip()
                elif keyword == 'TRUNC':
                    trunc_name = words[4].strip()

                keyword2 = words[5]
                if keyword2 in ['RESIDUAL', 'TREND']:
                    var_name = words[6].strip()
                elif keyword2 == 'POLYNUMBER':
                    poly_number = int(words[6])

                if keyword2 == 'RESIDUAL':
                    fmu_var = ('RESIDUAL', zone, region, gauss_name, var_name)
                elif keyword2 == 'TREND':
                    fmu_var = ('TREND', zone, region, gauss_name, var_name)
                elif keyword == 'TRUNC' and keyword2 == 'POLYNUMBER':
                    fmu_var = ('TRUNC', zone, region, trunc_name, poly_number)
                elif keyword == 'TRUNC':
                    fmu_var = ('TRUNC', zone, region, trunc_name, var_name)
                else:
                    raise ValueError('Invalid FMU parameter')
                fmu_variables.append(fmu_var)
    return fmu_variables


def set_all_as_fmu_updatable(input_model_file, output_model_file, tagged_variable_file=None):
    aps_model = APSModel(input_model_file)
    value = True
    all_zone_models = aps_model.sorted_zone_models
    for key, zone_model in all_zone_models.items():
        zone_number = key[0]
        region_number = key[1]
        if aps_model.isSelected(zone_number, region_number):
            gauss_names_for_zone = zone_model.used_gaussian_field_names
            for i in range(len(gauss_names_for_zone)):
                gauss_name = gauss_names_for_zone[i]

                # - Set FMU tag
                zone_model.setMainRangeFmuUpdatable(gauss_name, value)
                zone_model.setPerpRangeFmuUpdatable(gauss_name, value)
                zone_model.setVertRangeFmuUpdatable(gauss_name, value)
                zone_model.setAzimuthAngleFmuUpdatable(gauss_name, value)
                zone_model.setDipAngleFmuUpdatable(gauss_name, value)
                variogram_type = zone_model.getVariogramType(gauss_name)
                if variogram_type == VariogramType.GENERAL_EXPONENTIAL:
                    zone_model.setPowerFmuUpdatable(gauss_name, value)

                useTrend, trendModelObj, relStdDev, relStdDevFMU = zone_model.getTrendModel(gauss_name)
                if useTrend:
                    zone_model.setRelStdDevFmuUpdatable(gauss_name, value)
                    trendModelObj.setAzimuthFmuUpdatable(value)
                    trendModelObj.setStackingAngleFmuUpdatable(value)
                    _type = trendModelObj.type
                    if _type in [TrendType.ELLIPTIC, TrendType.HYPERBOLIC, TrendType.ELLIPTIC_CONE]:
                        trendModelObj.setCurvatureFmuUpdatable(value)
                        trendModelObj.setOriginXFmuUpdatable(value)
                        trendModelObj.setOriginYFmuUpdatable(value)
                        if _type in [TrendType.ELLIPTIC, TrendType.HYPERBOLIC]:
                            trendModelObj.setOriginZFmuUpdatable(value)
                        if _type in [TrendType.HYPERBOLIC, TrendType.ELLIPTIC_CONE]:
                            trendModelObj.setMigrationAngleFmuUpdatable(value)
                        if _type == TrendType.ELLIPTIC_CONE:
                            trendModelObj.setRelativeSizeOfEllipseFmuUpdatable(value)

            trunc_rule = zone_model.truncation_rule
            if trunc_rule._className == 'Trunc2D_Angle':
                nPoly = trunc_rule.getNumberOfPolygonsInTruncationMap()
                for polygon_number in range(nPoly):
                    trunc_rule.setAngleFmuUpdatable(polygon_number, value)
            elif trunc_rule._className == 'Trunc3D_bayfill':
                trunc_rule.setSFParamFmuUpdatable(value)
                trunc_rule.setYSFParamFmuUpdatable(value)
                trunc_rule.setSBHDParamFmuUpdatable(value)

    aps_model.writeModel(output_model_file, attributesFileName=tagged_variable_file, debug_level=Debug.VERY_VERBOSE)


def set_selected_as_fmu_updatable(input_model_file, output_model_file, selected_variables, tagged_variable_file=None):
    aps_model = APSModel(input_model_file)
    updatable = True
    for words in selected_variables:
        if isinstance(words, str):
            words = words.split('_')
        zone_number = int(words[1])
        region_number = int(words[2])

        gauss_name = None
        var_name = None
        trunc_name = None
        poly_number = None
        var_type2 = None
        var_type1 = words[3]
        if var_type1 == 'GF':
            gauss_name = words[4]
            var_type2 = words[5]
            if var_type2 == 'RESIDUAL':
                var_name = words[6]
            elif var_type2 == 'TREND':
                if len(words[6:]) == 1:
                    var_name = words[6]
                else:
                    var_name = words[6]
                    for s in words[7:]:
                        var_name = var_name + '_' + s
        elif var_type1 == 'TRUNC':
            trunc_name = words[4]
            if trunc_name == 'NONCUBIC':
                poly_number = int(words[6])
            elif trunc_name == 'BAYFILL':
                var_name = words[5]

        zone_model = aps_model.getZoneModel(zoneNumber=zone_number, regionNumber=region_number)
        if aps_model.isSelected(zone_number, region_number):
            if var_type1 == 'GF' and var_type2 == 'RESIDUAL':
                if var_name == 'MAINRANGE':
                    zone_model.setMainRangeFmuUpdatable(gauss_name, updatable)
                elif var_name == 'PERPRANGE':
                    zone_model.setPerpRangeFmuUpdatable(gauss_name, updatable)
                elif var_name == 'VERTRANGE':
                    zone_model.setVertRangeFmuUpdatable(gauss_name, updatable)
                elif var_name == 'AZIMUTHANGLE':
                    zone_model.setAzimuthAngleFmuUpdatable(gauss_name, updatable)
                elif var_name == 'DIPANGLE':
                    zone_model.setDipAngleFmuUpdatable(gauss_name, updatable)
                elif var_name == 'POWER':
                    variogram_type = zone_model.getVariogramType(gauss_name)
                    if variogram_type == VariogramType.GENERAL_EXPONENTIAL:
                        zone_model.setPowerFmuUpdatable(gauss_name, updatable)
            elif var_type1 == 'GF' and var_type2 == 'TREND':
                useTrend, trendModelObj, relStdDev, relStdDevFMU = zone_model.getTrendModel(gauss_name)
                if useTrend:
                    if var_name == 'AZIMUTH':
                        trendModelObj.setAzimuthFmuUpdatable(updatable)
                    elif var_name == 'STACKANGLE':
                        trendModelObj.setStackingAngleFmuUpdatable(updatable)

                    if trendModelObj.type == TrendType.ELLIPTIC:
                        if var_name == 'CURVATURE':
                            trendModelObj.setCurvatureFmuUpdatable(updatable)
                        elif var_name == 'ORIGIN_X':
                            trendModelObj.setOriginXFmuUpdatable(updatable)
                        elif var_name == 'ORIGIN_Y':
                            trendModelObj.setOriginYFmuUpdatable(updatable)
                        elif var_name == 'ORIGIN_Z_SIMBOX':
                            trendModelObj.setOriginZFmuUpdatable(updatable)
                    elif trendModelObj.type == TrendType.HYPERBOLIC:
                        if var_name == 'CURVATURE':
                            trendModelObj.setCurvatureFmuUpdatable(updatable)
                        elif var_name == 'MIGRATIONANGLE':
                            trendModelObj.setMigrationAngleFmuUpdatable(updatable)
                        elif var_name == 'ORIGIN_X':
                            trendModelObj.setOriginXFmuUpdatable(updatable)
                        elif var_name == 'ORIGIN_Y':
                            trendModelObj.setOriginYFmuUpdatable(updatable)
                        elif var_name == 'ORIGIN_Z_SIMBOX':
                            trendModelObj.setOriginZFmuUpdatable(updatable)
                    elif trendModelObj.type == TrendType.ELLIPTIC_CONE:
                        if var_name == 'CURVATURE':
                            trendModelObj.setCurvatureFmuUpdatable(updatable)
                        elif var_name == 'MIGRATIONANGLE':
                            trendModelObj.setMigrationAngleFmuUpdatable(updatable)
                        elif var_name == 'ORIGIN_X':
                            trendModelObj.setOriginXFmuUpdatable(updatable)
                        elif var_name == 'ORIGIN_Y':
                            trendModelObj.setOriginYFmuUpdatable(updatable)
                        elif var_name == 'RELATIVESIZE':
                            trendModelObj.setRelativeSizeOfEllipseFmuUpdatable(updatable)
                    if var_name =='RELSTDDEV':
                        zone_model.setRelStdDevFmuUpdatable(gauss_name, updatable)

            if var_type1 == 'TRUNC':
                trunc_rule = zone_model.truncation_rule
                if trunc_name == 'NONCUBIC':
                    # setAnglwFMUUpdatable take polygon_number counting from 0
                    trunc_rule.setAngleFmuUpdatable(poly_number-1, updatable)
                elif trunc_name == 'BAYFILL':
                    if var_name == 'SF':
                        trunc_rule.setSFParamFmuUpdatable(updatable)
                    elif var_name == 'YSF':
                        trunc_rule.setYSFParamFmuUpdatable(updatable)
                    elif var_name == 'SBHD':
                        trunc_rule.setSBHDParamFmuUpdatable(updatable)

    aps_model.writeModel(output_model_file, attributesFileName=tagged_variable_file, debug_level=Debug.VERY_VERBOSE)
