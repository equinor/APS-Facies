#!/bin/env python
"""
Python3 script using ROXAPI to update 2D maps for azimuth anisotropy for
variogram for 3D gaussian field simulation.
Dependency: ROXAPI
"""
import importlib

import src.generalFunctionsUsingRoxAPI as gr
from src import APSModel, APSZoneModel

importlib.reload(APSModel)
importlib.reload(APSZoneModel)
importlib.reload(gr)

modelFileName = 'APS.xml'
print('- Read file: ' + modelFileName)
apsModel = APSModel.APSModel(modelFileName)
debug_level = apsModel.debug_level()

horizons = project.horizons
selectedZoneNumberList = apsModel.getSelectedZoneNumberList()

for zoneNumber in selectedZoneNumberList:
    zoneModel = apsModel.getZoneModel(zoneNumber)
    hName = zoneModel.getHorizonNameForVariogramTrendMap()
    gaussFieldNames = zoneModel.getUsedGaussFieldNames()
    for gfName in gaussFieldNames:
        reprName = gfName + '_VarioAzimuthTrend'

        # Get azimuth value for this gauss field for this zone
        azimuthValue = zoneModel.getAnisotropyAzimuthAngle(gfName)

        # Set the value in the map to the constant azimuth value.
        # Assume that the map already exist. 
        gr.setConstantValueInHorizon(horizons, hName, reprName, azimuthValue, debug_level)

print('- Finished updating variogram azimuth trend maps in RMS project')
