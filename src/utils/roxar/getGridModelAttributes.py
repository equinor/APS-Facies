#!/bin/env python
# -*- coding: utf-8 -*-
"""
Python3  script with roxAPI
This script will read grid dimensions of the grid for the specified grid model in the model file.
"""

from xml.etree.ElementTree import Element

import src.utils.roxar.generalFunctionsUsingRoxAPI as gr
from src.algorithms.APSModel import APSModel
from src.utils.constants.simple import Debug
from src.utils.methods import get_run_parameters
from src.utils.xmlUtils import prettify


def writeXMLFileGridDimensions(project, gridModelName, outputFile, debug_level=Debug.OFF):
    # Find grid model
    grid_models = project.grid_models
    found = False
    gridModel = None
    for grid_model in grid_models:
        if grid_model.name == gridModelName:
            gridModel = grid_model
            found = True
            break
    if not found:
        raise ValueError(
            'Could not find grid model with name: {} in RMS project'
            ''.format(gridModelName)
        )
    # Get the grid
    grid = gridModel.get_grid()

    # Get Grid attributes
    [xmin, xmax, ymin, ymax, zmin, zmax, simBoxXLength, simBoxYLength,
     azimuthAngle, x0, y0, nx, ny, nz, nZonesGrid,
     zoneNames, nLayersPerZone, startLayerPerZone, endLayerPerZone] = gr.getGridAttributes(grid, debug_level)

    xinc = simBoxXLength/nx
    yinc = simBoxYLength/ny


    # Create xml tree with output
    topElement = Element('RMS_grid_model_data')
    attribute = {'name': gridModel.name}
    gmElement = Element('GridModel', attribute)
    topElement.append(gmElement)

    for i in range(len(zoneNames)):
        tag = 'ZoneName'
        attribute = {'number': str(i + 1), 'nLayers': str(nLayersPerZone[i]), 'start': str(startLayerPerZone[i]), 'end': str(endLayerPerZone[i])}
        name = zoneNames[i]
        zNameObj = Element(tag, attribute)
        zNameObj.text = ' ' + name.strip() + ' '
        gmElement.append(zNameObj)

    tag = 'XSize'
    xsObj = Element(tag)
    xsObj.text = ' ' + str(simBoxXLength) + ' '
    gmElement.append(xsObj)

    tag = 'YSize'
    ysObj = Element(tag)
    ysObj.text = ' ' + str(simBoxYLength) + ' '
    gmElement.append(ysObj)

    tag = 'AzimuthAngle'
    azimuthObj = Element(tag)
    azimuthObj.text = ' ' + str(azimuthAngle) + ' '
    gmElement.append(azimuthObj)

    tag = 'OrigoX'
    x0_obj = Element(tag)
    x0_obj.text = ' ' + str(x0) + ' '
    gmElement.append(x0_obj)

    tag = 'OrigoY'
    y0_obj = Element(tag)
    y0_obj.text = ' ' + str(y0) + ' '
    gmElement.append(y0_obj)

    tag = 'NX'
    nxObj = Element(tag)
    nxObj.text = ' ' + str(nx) + ' '
    gmElement.append(nxObj)

    tag = 'NY'
    nyObj = Element(tag)
    nyObj.text = ' ' + str(ny) + ' '
    gmElement.append(nyObj)

    tag = 'Xinc'
    xincObj = Element(tag)
    xincObj.text = ' ' + str(xinc) + ' '
    gmElement.append(xincObj)

    tag = 'Yinc'
    yincObj = Element(tag)
    yincObj.text = ' ' + str(yinc) + ' '
    gmElement.append(yincObj)

    with open(outputFile, 'w') as file:
        print('- Write file: ' + outputFile)
        root = prettify(topElement)
        file.write(root)
    return


def run(roxar=None, project=None, **kwargs):
    # TODO: Separate this part into a CLI program

    model_file, output_rms_data_file, _, _, _ = get_run_parameters(**kwargs)

    # Read APS model
    print('- Read file: ' + model_file)
    aps_model = APSModel(model_file)
    debug_level = aps_model.debug_level()
    grid_model_name = aps_model.getGridModelName()

    writeXMLFileGridDimensions(project, grid_model_name, output_rms_data_file, debug_level)
    print('')
    print('Finished running: ' + __file__)


if __name__ == '__main__':
    import roxar
    run(roxar, project)