#!/bin/env python
# -*- coding: utf-8 -*-
"""
Python3  script with roxAPI
This script will read grid dimensions of the grid for the specified grid model in the model file.
"""

from xml.etree.ElementTree import Element

from aps.utils.roxar.grid_model import GridAttributes, get_zone_names
from aps.algorithms.APSModel import APSModel
from aps.utils.constants.simple import Debug
from aps.utils.methods import get_run_parameters
from aps.utils.xmlUtils import prettify


def writeXMLFileGridDimensions(
    project, gridModelName, outputFile, debug_level=Debug.OFF
):
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
            f'Could not find grid model with name: {gridModelName} in RMS project'
        )
    # Get the grid
    grid = gridModel.get_grid()
    zone_names = get_zone_names(gridModel)
    # Get Grid attributes
    grid_attributes = GridAttributes(grid, zone_names)

    nx, ny, nz = grid_attributes.dimensions
    nx_simbox, ny_simbox, nz_simbox = grid_attributes.sim_box_size.simbox_dimensions
    xinc = grid_attributes.sim_box_size.x_length / nx
    yinc = grid_attributes.sim_box_size.y_length / ny

    # Create xml tree with output
    topElement = Element('RMS_grid_model_data')
    attribute = {'name': gridModel.name}
    gmElement = Element('GridModel', attribute)
    topElement.append(gmElement)

    for i in range(len(grid_attributes.zone_names)):
        tag = 'ZoneName'
        attribute = {
            'number': str(i + 1),
            'nLayers': str(grid_attributes.num_layers_per_zone[i]),
            'start': str(grid_attributes.start_layers_per_zone[i]),
            'end': str(grid_attributes.end_layers_per_zone[i] - 1),
        }
        name = grid_attributes.zone_names[i]
        zNameObj = Element(tag, attribute)
        zNameObj.text = ' ' + name.strip() + ' '
        gmElement.append(zNameObj)

    tags = [
        ('XSize', grid_attributes.sim_box_size.x_length),
        ('YSize', grid_attributes.sim_box_size.y_length),
        ('AzimuthAngle', grid_attributes.sim_box_size.azimuth_angle),
        ('OrigoX', grid_attributes.sim_box_size.x0),
        ('OrigoY', grid_attributes.sim_box_size.y0),
        ('NX', nx),
        ('NY', ny),
        ('NX_simbox', nx_simbox),
        ('NY_simbox', ny_simbox),
        ('Xinc', xinc),
        ('Yinc', yinc),
    ]

    for tag, value in tags:
        element = Element(tag)
        element.text = ' {0} '.format(value)
        gmElement.append(element)

    with open(outputFile, 'w', encoding='utf-8') as file:
        print(f'- Write file: {outputFile}')
        root = prettify(topElement)
        file.write(root)


def run(roxar=None, project=None, **kwargs):
    # TODO: Separate this part into a CLI program
    params = get_run_parameters(**kwargs)
    model_file = params['model_file']
    output_rms_data_file = params['rms_data_file']

    # Read APS model
    print(f'- Read file: {model_file}')
    aps_model = APSModel(model_file)
    debug_level = aps_model.debug_level
    grid_model_name = aps_model.grid_model_name

    writeXMLFileGridDimensions(
        project, grid_model_name, output_rms_data_file, debug_level
    )
    print(f'\nFinished running: {__file__}')


if __name__ == '__main__':
    import roxar

    run(roxar, project)  # noqa
