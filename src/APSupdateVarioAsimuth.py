#!/bin/env python
"""
Python3 script using ROXAPI to update 2D maps for asimuth anisotropy for
variogram for 3D gaussian field simulation.
Dependency: ROXAPI
"""
import importlib

import src.generalFunctionsUsingRoxAPI as gr
from src import APSModel, APSZoneModel, Trunc2D_Cubic_Multi_Overlay_xml

importlib.reload(APSModel)
importlib.reload(APSZoneModel)
importlib.reload(gr)
importlib.reload(Trunc2D_Cubic_Multi_Overlay_xml)

modelFileName = 'APS.xml'
print('- Read file: ' + modelFileName)
apsModel = APSModel.APSModel(modelFileName)
printInfo = apsModel.printInfo()

horizons = project.horizons
selectedZoneNumberList = apsModel.getSelectedZoneNumberList()

for zoneNumber in selectedZoneNumberList:
    zoneModel = apsModel.getZoneModel(zoneNumber)
    hName = zoneModel.getHorizonNameForVarioTrendMap()
    gaussFieldNames = zoneModel.getUsedGaussFieldNames()
    for gfName in gaussFieldNames:
        reprName = gfName + '_VarioAsimuthTrend'

        # Get asimuth value for this gauss field for this zone
        asimuthValue = zoneModel.getAnisotropyAsimuthAngle(gfName)

        # Set the value in the map to the constant asimuth value.
        # Assume that the map already exist. 
        gr.setConstantValueInHorizon(horizons, hName, reprName, asimuthValue, printInfo)

print('- Finished updating variogram asimuth trend maps in RMS project')
