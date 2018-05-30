#!/bin/env python
# -*- coding: utf-8 -*-
from src.algorithms.APSModel import APSModel
from src.utils.constants.simple import Debug, VariogramType, TrendType
from src.algorithms.Trunc2D_Angle_xml import Trunc2D_Angle

def read_selected_fmu_variables(input_selected_FMU_variable_file):
    fmu_variables = []
    with open(input_selected_FMU_variable_file, 'r') as file:
        finished = False
        while not finished:
            line = file.readline()
            if line == '':
                finished = True
            else:
                print(line.strip())
                words = line.split('_')
                zone = int(words[1])
                region = int(words[2])
                keyword = words[3]
                if keyword == 'GF':
                    gauss_name = words[4].strip()
                elif keyword == 'TRUNC':
                    trunc_name = words[4].strip()

                keyword2 = words[5]
                if keyword2 == 'RESIDUAL':
                    var_name = words[6].strip()
                elif  keyword2 == 'TREND':
                    var_name = words[6].strip()
                elif keyword2 == 'POLYNUMBER':
                    poly_number = int(words[6])

                if keyword2 == 'RESIDUAL':
                    fmu_var = ['RESIDUAL', zone, region, gauss_name, var_name]
                elif keyword2 == 'TREND':
                    fmu_var = ['TREND', zone, region, gauss_name, var_name]
                elif keyword == 'TRUNC' and keyword2 == 'POLYNUMBER':
                    fmu_var = ['TRUNC', zone, region, trunc_name, poly_number] 
                elif keyword == 'TRUNC':
                    fmu_var = ['TRUNC', zone, region, trunc_name, var_name]
                fmu_variables.append(fmu_var)
    return fmu_variables

def setAllAsFmuUpdatable(input_model_file, output_model_file, tagged_variable_file):
    aps_model = APSModel(input_model_file)
    value = True
    all_zone_models = aps_model.getAllZoneModelsSorted()
    for key, zoneModel in all_zone_models.items():
        zone_number = key[0]
        region_number = key[1]
        if aps_model.isSelected(zone_number, region_number):
            gauss_names_for_zone = zoneModel.getUsedGaussFieldNames()
            for i in range(len(gauss_names_for_zone)):
                gauss_name = gauss_names_for_zone[i]

                # - Set FMU tag
                zoneModel.setMainRangeFmuUpdatable(gauss_name, value)
                zoneModel.setPerpRangeFmuUpdatable(gauss_name, value)
                zoneModel.setVertRangeFmuUpdatable(gauss_name, value)
                zoneModel.setAzimuthAngleFmuUpdatable(gauss_name, value)
                zoneModel.setDipAngleFmuUpdatable(gauss_name, value)
                variogramType = zoneModel.getVariogramType(gauss_name)
                if variogramType == VariogramType.GENERAL_EXPONENTIAL:
                    zoneModel.setPowerFmuUpdatable(gauss_name, value)

                useTrend, trendModelObj, relStdDev, relStdDevFMU = zoneModel.getTrendModel(gauss_name)
                if useTrend:
                    zoneModel.setRelStdDevFmuUpdatable(gauss_name, value)
                    trendModelObj.setAzimuthFmuUpdatable(value)
                    trendModelObj.setStackingAngleFmuUpdatable(value)
                    if trendModelObj.type == TrendType.ELLIPTIC:
                        trendModelObj.setCurvatureFmuUpdatable(value)
                        trendModelObj.setOriginXFmuUpdatable(value)
                        trendModelObj.setOriginYFmuUpdatable(value)
                        trendModelObj.setOriginZFmuUpdatable(value)
                    elif trendModelObj.type == TrendType.HYPERBOLIC:
                        trendModelObj.setCurvatureFmuUpdatable(value)
                        trendModelObj.setOriginXFmuUpdatable(value)
                        trendModelObj.setOriginYFmuUpdatable(value)
                        trendModelObj.setOriginZFmuUpdatable(value)
                        trendModelObj.setMigrationAngleFmuUpdatable(value)
                    elif  trendModelObj.type == TrendType.ELLIPTIC_CONE:
                        trendModelObj.setCurvatureFmuUpdatable(value)
                        trendModelObj.setOriginXFmuUpdatable(value)
                        trendModelObj.setOriginYFmuUpdatable(value)
                        trendModelObj.setMigrationAngleFmuUpdatable(value)
                        trendModelObj.setRelativeSizeOfEllipseFmuUpdatable(value)
                    
            trunc_rule = zoneModel.getTruncRule()
            if trunc_rule._className == 'Trunc2D_Angle':
                nPoly = trunc_rule.getNumberOfPolygonsInTruncationMap()
                for polygon_number in range(nPoly):
                    trunc_rule.setAngleFmuUpdatable(polygon_number, value)
            elif trunc_rule._className == 'Trunc3D_bayfill':
                trunc_rule.setSFParamFmuUpdatable(value)
                trunc_rule.setYSFParamFmuUpdatable(value)
                trunc_rule.setSBHDParamFmuUpdatable(value)

    aps_model.writeModel(output_model_file, tagged_variable_file, debug_level=Debug.VERY_VERBOSE)



def setSelectedAsFmuUpdatable(input_model_file, output_model_file, selected_variables, tagged_variable_file):
    aps_model = APSModel(input_model_file)
    value = True
    for i in range(len(selected_variables)):
        fmu_variable = selected_variables[i]
        zone_number = fmu_variable[1]
        region_number = fmu_variable[2]
        var_type = fmu_variable[0]
        gauss_name = None
        var_name = None
        trunc_name = None
        poly_number = None
        if var_type == 'RESIDUAL' or var_type == 'TREND':
            gauss_name = fmu_variable[3]
            var_name = fmu_variable[4]
        elif var_type == 'TRUNC':
            trunc_name = fmu_variable[3]
            if trunc_name == 'NONCUBIC':
                poly_number = int(fmu_variable[4])

        
        zoneModel = aps_model.getZoneModel(zoneNumber=zone_number, regionNumber=region_number)
        if aps_model.isSelected(zone_number, region_number):
            if var_type == 'RESIDUAL':
                if var_name == 'MAINRANGE':
                    zoneModel.setMainRangeFmuUpdatable(gauss_name, value)
                elif var_name == 'PERPRANGE':
                    zoneModel.setPerpRangeFmuUpdatable(gauss_name, value)
                elif var_name == 'VERTRANGE':
                    zoneModel.setVertRangeFmuUpdatable(gauss_name, value)
                elif var_name == 'AZIMUTHANGLE':
                    zoneModel.setAzimuthAngleFmuUpdatable(gauss_name, value)
                elif var_name == 'DIPANGLE':
                    zoneModel.setDipAngleFmuUpdatable(gauss_name, value)
                elif var_name == 'POWER':
                    variogramType = zoneModel.getVariogramType(gauss_name)
                    if variogramType == VariogramType.GENERAL_EXPONENTIAL:
                        zoneModel.setPowerFmuUpdatable(gauss_name, value)
            elif var_type == 'TREND':
                useTrend, trendModelObj, relStdDev, relStdDevFMU = zoneModel.getTrendModel(gauss_name)
                if useTrend:
                    if var_name == 'AZIMUTH':
                        trendModelObj.setAzimuthFmuUpdatable(value)
                    elif var_name == 'STACKANGLE':
                        trendModelObj.setStackingAngleFmuUpdatable(value)

                    if trendModelObj.type == TrendType.ELLIPTIC:
                        if var_name == 'CURVATURE':
                            trendModelObj.setCurvatureFmuUpdatable(value)
                        elif var_name == 'ORIGIN_X':
                            trendModelObj.setOriginXFmuUpdatable(value)
                        elif var_name == 'ORIGIN_Y':
                            trendModelObj.setOriginYFmuUpdatable(value)
                        elif var_name == 'ORIGIN_Z_SIMBOX':
                            trendModelObj.setOriginZFmuUpdatable(value)
                    elif trendModelObj.type == TrendType.HYPERBOLIC:
                        if var_name == 'CURVATURE':
                            trendModelObj.setCurvatureFmuUpdatable(value)
                        elif var_name == 'MIGRATIONANGLE':
                            trendModelObj.setMigrationAngleFmuUpdatable(value)
                        elif var_name == 'ORIGIN_X':
                            trendModelObj.setOriginXFmuUpdatable(value)
                        elif var_name == 'ORIGIN_Y':
                            trendModelObj.setOriginYFmuUpdatable(value)
                        elif var_name == 'ORIGIN_Z_SIMBOX':
                            trendModelObj.setOriginZFmuUpdatable(value)
                    elif  trendModelObj.type == TrendType.ELLIPTIC_CONE:
                        if var_name == 'CURVATURE':
                            trendModelObj.setCurvatureFmuUpdatable(value)
                        elif var_name == 'MIGRATIONANGLE':
                            trendModelObj.setMigrationAngleFmuUpdatable(value)
                        elif var_name == 'ORIGIN_X':
                            trendModelObj.setOriginXFmuUpdatable(value)
                        elif var_name == 'ORIGIN_Y':
                            trendModelObj.setOriginYFmuUpdatable(value)
                        elif var_name == 'RELATIVESIZE':
                            trendModelObj.setRelativeSizeOfEllipseFmuUpdatable(value)
                    if var_name =='RELSTDDEV':
                        zoneModel.setRelStdDevFmuUpdatable(gauss_name, value)

            elif var_type == 'TRUNC':
                trunc_rule = zoneModel.getTruncRule()
                if trunc_name == 'NONCUBIC':
                    # setAnglwFMUUpdatable take polygon_number counting from 0
                    trunc_rule.setAngleFmuUpdatable(poly_number-1, value)
                elif  trunc_name == 'BAYFILL':
                    if var_name == 'SF':
                        trunc_rule.setSFParamFmuUpdatable(value)
                    elif  var_name == 'YSF':
                        trunc_rule.setYSFParamFmuUpdatable(value)
                    elif  var_name == 'SBHD':
                        trunc_rule.setSBHDParamFmuUpdatable(value)

    aps_model.writeModel(output_model_file, tagged_variable_file, debug_level=Debug.VERY_VERBOSE)


if __name__ == '__main__':
    input_model_file = 'APS.xml'
    input_selected_FMU_variable_file = 'FMU_selected_variables.dat'
    output_model_file = 'APS_with_FMU_tags.xml'
    tagged_variable_file = 'FMU_tagged_variables.dat'
    tag_all_variables = True

    if tag_all_variables:
        # Set all APS model parameters as FMU updatable
        setAllAsFmuUpdatable(input_model_file, output_model_file, tagged_variable_file)
    else:
        print('Valg selected.')
        # Read selected FMU variables
        fmu_variables = read_selected_fmu_variables(input_selected_FMU_variable_file)
        print(fmu_variables)
        setSelectedAsFmuUpdatable(input_model_file, output_model_file, fmu_variables, tagged_variable_file)
