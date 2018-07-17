#!/bin/env python
# -*- coding: utf-8 -*-
"""
Python3 script using ROXAPI to update 2D maps for azimuth anisotropy for
variogram for 3D gaussian field simulation.
Dependency: ROXAPI
"""
from warnings import warn
import roxar

from src.utils.roxar.generalFunctionsUsingRoxAPI import setConstantValueInHorizon
from src.algorithms.APSModel import APSModel


def run():
    warn("deprecated", DeprecationWarning)
    modelFileName = 'APS.xml'
    print('- Read file: ' + modelFileName)
    apsModel = APSModel(modelFileName)
    debug_level = apsModel.debug_level()
    horizons = project.horizons
    allZoneModels = apsModel.getAllZoneModels()
    for key, zoneModel in allZoneModels.items():

        hName = zoneModel.getHorizonNameForVariogramTrendMap()
        gaussFieldNames = zoneModel.used_gaussian_field_names
        for gfName in gaussFieldNames:
            reprName = gfName + '_VarioAzimuthTrend'

            # Get azimuth value for this gauss field for this zone
            azimuthValue = zoneModel.getAnisotropyAzimuthAngle(gfName)

            # Set the value in the map to the constant azimuth value.
            # Assume that the map already exist.
            setConstantValueInHorizon(horizons, hName, reprName, azimuthValue, debug_level)
    print('- Finished updating variogram azimuth trend maps in RMS project')


if __name__ == '__main__':
    run()
