#!/bin/env python
# -*- coding: utf-8 -*-
"""
Python3  script with roxAPI
This script will read the RMS project and save all relevant information necessary for the APSGUI.
This will include:
- Grid model name for selected grid model specified by user
- 3D parameter names for selected grid model
- name and type of all horizons in horizon container
- Name of all discrete variables (facies) in selected log from selected well
- Name of workflow
- Name of RMS project

Example input file to be specified before running this script.
<?xml version="1.0" ?>
<GetRMSProjectData>

 <GridModel>
   <Name> APS_NESLEN_ODM </Name>
   <ZoneParameter>  Zone </ZoneParameter>
   <RegionParameter>  Region </RegionParameter>
 </GridModel>



 <WellName name="B2">
   <Trajectory name="Drilled trajectory">
     <Logrun name="log">
       <LogName>
         ODM_Facies
       </LogName>
     </Logrun>
   </Trajectory>
 </WellName>
 <HorizonReference name="top_middle_Neslen_1" type="DepthSurface">  </HorizonReference>
 <Horizon> top_middle_Neslen_1 </Horizon>
 <Horizon> top_middle_Neslen_2 </Horizon>
 <Horizon> top_middle_Neslen_3 </Horizon>
 <Horizon> top_middle_Neslen_4 </Horizon>
 <Horizon> top_middle_Neslen_5 </Horizon>
 <Horizon> top_middle_Neslen_6 </Horizon>
</GetRMSProjectData>
"""

import copy
import datetime
from warnings import warn
from xml.etree.ElementTree import Element, parse

import numpy as np

from aps.utils.roxar.generalFunctionsUsingRoxAPI import (
    get2DMapDimensions, setConstantValueInHorizon, createHorizonDataTypeObject
)
from aps.utils.roxar.grid_model import getDiscrete3DParameterValues, GridAttributes
from aps.algorithms.APSMainFaciesTable import APSMainFaciesTable
from aps.utils.constants.simple import Debug
from aps.utils.methods import get_prefix
from aps.utils.xmlUtils import getKeyword, getTextCommand, prettify


def readInputXMLFile(modelFileName, debug_level=Debug.OFF):
    """
    This function read user specification of which grid model etc to scan from RMS.
    :param modelFileName:
    :param debug_level:
    :return:
    """
    # Read model if it is defined
    tree = parse(modelFileName)
    root = tree.getroot()

    kw = 'GridModel'
    gridModelObj = getKeyword(root, kw, parentKeyword='', modelFile=None, required=True)

    kw1 = 'Name'
    text = getTextCommand(gridModelObj, kw1, parentKeyword=kw, defaultText=None, modelFile=None, required=True)
    gridModelName = text.strip()

    kw3 = 'ZoneParameter'
    text = getTextCommand(gridModelObj, kw3, parentKeyword=kw, defaultText=None, modelFile=None, required=False)
    zoneParamName = None
    if text is not None:
        zoneParamName = text.strip()
    else:
        print('Keyword: {} not used'.format(kw3))

    kw4 = 'RegionParameter'
    text = getTextCommand(gridModelObj, kw4, parentKeyword=kw, defaultText=None, modelFile=None, required=False)
    regionParamName = None
    if text is not None:
        regionParamName = text.strip()
    else:
        print('Keyword: {} not used'.format(kw4))

    if debug_level >= Debug.VERY_VERBOSE:
        print('Debug output: Grid model:         ' + gridModelName)
        if zoneParamName is not None:
            print('Debug output: Zone parameter:     ' + zoneParamName)
        if regionParamName is not None:
            print('Debug output: Region parameter:   ' + regionParamName)

    kw = 'GaussFields'
    text = getTextCommand(root, kw, parentKeyword='', defaultText=None, modelFile=None, required=False)
    gfNames = []
    if text is not None:
        names = text.split()
        for i in range(len(names)):
            name = names[i]
            gfNames.append(name)
    else:
        print('Keyword: {} not used'.format(kw))

    kw = 'HorizonReference'
    hRefObj = root.find(kw)
    horizonRefName = None
    horizonRefType = None
    if hRefObj is not None:
        text = hRefObj.get('name')
        horizonRefName = text.strip()
        text = hRefObj.get('type')
        horizonRefType = text.strip()
        if debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: Horizon reference:  ' + horizonRefName + ' with type ' + horizonRefType)
    else:
        print('Keyword: {} not used'.format(kw))

    kw = 'Horizon'
    horizonList = []
    for hObj in root.findall(kw):
        if hObj is not None:
            text = hObj.text
            horizonList.append(text.strip())
        else:
            print('Keyword: {} not used'.format(kw))

    kw1 = 'WellName'
    wellRefName = None
    wellNameRefObj = None
    wellNameRefObj = root.find(kw1)
    if wellNameRefObj is not None:
        text = wellNameRefObj.get('name')
        wellRefName = text.strip()
    else:
        print('Keyword: {} not used'.format(kw1))
        trajectoryName = 'Trajectory'
        logrunName = 'Logrun'
        logName = 'LogName'

    if wellNameRefObj is not None:
        kw2 = 'Trajectory'
        trajectoryName = 'Trajectory'
        trRefObj = wellNameRefObj.find(kw2)
        if trRefObj is not None:
            text = trRefObj.get('name')
            trajectoryName = text.strip()
        else:
            print('Error: Missing keyword: {}'.format(kw2))

        kw3 = 'Logrun'
        logrunName = 'Logrun'
        logrunRefObj = trRefObj.find(kw3)
        if logrunRefObj is not None:
            text = logrunRefObj.get('name')
            logrunName = text.strip()
        else:
            print('Error: Missing keyword: {}'.format(kw3))

        kw4 = 'LogName'
        logName = 'LogName'
        logNameRefObj = logrunRefObj.find(kw4)
        if logrunRefObj is not None:
            if logNameRefObj is not None:
                text = logNameRefObj.text
                logName = text.strip()
            else:
                print('Error: Missing keyword: {}'.format(kw4))

    if debug_level >= Debug.VERY_VERBOSE:
        if wellRefName is not None:
            print(
                'Debug output: Well reference:     ' + wellRefName + '   ' + trajectoryName + '   ' + logrunName + '   ' + logName)

    return (gridModelName, zoneParamName, regionParamName, gfNames, horizonRefName, horizonRefType, horizonList,
            wellRefName, trajectoryName, logrunName, logName)


def scanRMSProjectAndWriteXMLFile(project, inputFile, outputRMSDataFile, debug_level=Debug.OFF):
    """
    Read a specification of which data to scan from the RMS project
        - Read a user specified input XML file specifying which grid model etc to scan.
        - Scan the RMS project using roxAPI to get RMS project information.
        - Write the RMS project info to an output XML file.
    :param project:
    :param inputFile:
    :param outputRMSDataFile:
    :param debug_level:
    :return:
    """
    [
        gridModelName, zoneParamName, regionParamName, gfNames, horizonRefName, horizonRefType,
        horizonList, wellRefName, trajectoryName, logrunName, logName
    ] = readInputXMLFile(inputFile, debug_level)

    topElement = Element('RMS_project_data')

    # -- Commands using experimental roxAPI functionality --
    workflowNames = []
    workflowList = project.workflows
    for wflow in workflowList:
        name = wflow.name
        workflowNames.append(name)
    # -- End commands using experimental roxAPI functionality --

    tag = 'Project'
    attribute = {'name': project.name}
    prElement = Element(tag, attribute)
    topElement.append(prElement)

    tag = 'Date'
    dateObj = Element(tag)
    d = datetime.datetime.today()
    t = datetime.datetime.now()
    line = 'Date: ' + d.strftime("%d/%m/%y") + ' Clock: ' + t.strftime("%H.%M.%S")
    dateObj.text = line.strip()
    prElement.append(dateObj)

    tag = 'ProjectFile'
    prFileObj = Element(tag)
    prFileObj.text = ' ' + project.filename + ' '
    prElement.append(prFileObj)

    tag = 'Seed'
    seedElement = Element(tag)
    seedElement.text = ' ' + str(project.seed) + ' '
    prElement.append(seedElement)

    tag = 'RealisationNumber'
    realNumberElement = Element(tag)
    realizationNumber = project.current_realisation
    realNumberElement.text = ' ' + str(realizationNumber) + ' '

    prElement.append(realNumberElement)

    tag = 'WorkflowList'
    wfElement = Element(tag)
    prElement.append(wfElement)
    for wfName in workflowNames:
        tag = 'Workflow'
        wfNameElement = Element(tag)
        wfNameElement.text = ' ' + wfName + ' '
        wfElement.append(wfNameElement)

    # Read data from RMS project and write to XML file
    # Scan grid model data
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

    if debug_level >= Debug.VERY_VERBOSE:
        print('Debug outout: Read data for grid model: ' + gridModel.name + ' from  RMS project.')
        print('Debug output: Grid model is shared:     ' + str(gridModel.shared))

    attribute = {'name': gridModel.name}
    gmElement = Element('GridModel', attribute)
    topElement.append(gmElement)

    zoneValues = None
    regionValues = None
    # Scan for all 3D parameters in grid model
    properties = gridModel.properties
    for prop in properties:
        if len(prop.name) > 40:
            # Skip this model. Is probably not a model but a dummy model name
            continue
        name = prop.name

        # Check if this is the specified zone parameter
        if name == zoneParamName:
            # Get the zone parameter values
            zoneValues, codeNamesZone = getDiscrete3DParameterValues(
                gridModel, name, realization_number=realizationNumber
            )
        # Check if the property type is integer or float type

        if regionParamName is not None:
            # Check if this is the specified region parameter
            if name == regionParamName:
                # Get the region parameter values
                regionValues, codeNamesRegion = getDiscrete3DParameterValues(
                    gridModel, name, realization_number=realizationNumber
                )

        # Check if the property type is integer or float type

        isDiscrete = 0
        try:
            # This will return the existing property since it already exist
            # If a value error occur the parameter is not continuous
            prop2 = properties.create(name, roxar.GridPropertyType.continuous, np.float32)
        except ValueError:
            # Not continuous parameter
            isDiscrete = 1

        if isDiscrete:
            attribute = {'type': 'Discrete'}
        else:
            attribute = {'type': 'Continuous'}
        propElement = Element('Property', attribute)
        propElement.text = ' ' + prop.name + ' '
        gmElement.append(propElement)
    # end for properties in gridmodel

    zonesAndRegions = {}
    if regionParamName is None:
        if zoneParamName is not None:
            if zoneValues is None:
                raise ValueError('Zone parameter is not defined or empty')

            # Only zone numbers are reported
            for i in range(len(zoneValues)):
                zVal = zoneValues[i]
                rVal = 0
                key = (zVal, rVal)
                if key not in zonesAndRegions:
                    if debug_level >= Debug.VERY_VERBOSE:
                        print('Debug output: Add zone = ({})'.format(str(zVal)))
                    zonesAndRegions[key] = 1
    else:
        # Both zone numbers and region numbers are reported
        if zoneValues is None:
            raise ValueError('Zone parameter is not defined or empty')
        if regionValues is None:
            raise ValueError('Region parameter is not defined or empty')
        if len(zoneValues) != len(regionValues):
            raise ValueError('Length of zone parameter and region parameter are different. Some inconsistency.')
        for i in range(len(zoneValues)):
            zVal = zoneValues[i]
            rVal = regionValues[i]
            key = (zVal, rVal)
            if key not in zonesAndRegions:
                if debug_level >= Debug.VERY_VERBOSE:
                    print('Debug output: Add (zone,region) = ({},{})'.format(str(zVal), str(rVal)))
                zonesAndRegions[key] = 1

    # Zone and region information

    for key, value in zonesAndRegions.items():
        zNumber = key[0]
        rNumber = key[1]
        tag = 'ZoneAndRegionNumbers'
        attributes={'zoneNumber': str(zNumber), 'regionNumber': str(rNumber)}
        zoneAndRegionElement = Element(tag, attributes)
        zoneAndRegionElement.text = ' '
        gmElement.append(zoneAndRegionElement)

    for name in gfNames:
        gfElement = Element('GaussFieldNames')
        gfElement.text = ' ' + name + ' '
        gmElement.append(gfElement)

    # Get grid dimensions etc for the grid model
    grid = gridModel.get_grid()
    grid_attributes = GridAttributes(grid, debug_level)
    nx, ny, nz = grid_attributes.dimensions
    xinc = grid_attributes.sim_box_size.x_length / nx
    yinc = grid_attributes.sim_box_size.y_length / ny

    tag = 'NZones'
    nZonesObj = Element(tag)
    nZonesObj.text = ' ' + str(grid_attributes.num_zones) + ' '
    gmElement.append(nZonesObj)

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
        ('Xinc', xinc),
        ('Yinc', yinc),
    ]
    for tag, value in tags:
        xml_element = Element(tag)
        xml_element.text = ' ' + str(value) + ' '
        gmElement.append(xml_element)
    # Finished writing grid model data

    if horizonRefName is not None:
        # Start scanning for horizon names and 2D map size information
        found = False
        if horizonRefName in project.horizons:
            found = True
        if not found:
            raise ValueError('Error: Specified name for reference horizon: ' + horizonRefName + ' is not an existing horizon')

        found = False
        if horizonRefType in project.horizons[horizonRefName]:
            found = True
        if not found:
            raise ValueError('Error: Specified type for reference horizon: ' + horizonRefType + ' is not defined')
        # Use the specified reference horizon name and type to get 2D surface grid info
        [nx, ny, xinc, yinc, xmin, ymin, xmax, ymax, rotation] = get2DMapDimensions(
            project.horizons, horizonRefName, horizonRefType, debug_level)
        tag = 'SurfaceTrendDimensions'
        surface_element = Element(tag)
        topElement.append(surface_element)

        tags = [
            ('NX', nx),
            ('NY', ny),
            ('Xmin', xmin),
            ('Xmax', xmax),
            ('Ymin', ymin),
            ('Ymax', ymax),
            ('Xinc', xinc),
            ('Yinc', yinc),
            ('Rotation', rotation),
        ]
        for tag, value in tags:
            xml_element = Element(tag)
            xml_element.text = ' ' + str(value) + ' '
            surface_element.append(xml_element)

        for horizon_name in horizonList:
            tag = 'Horizon'
            horizon_element = Element(tag)
            horizon_element.text = ' ' + copy.copy(horizon_name) + ' '
            topElement.append(horizon_element)

    # Find facies names in reference well log
    if wellRefName is not None:
        well = project.wells[wellRefName]
        trajectory = well.wellbore.trajectories[trajectoryName]
        log_run = trajectory.log_runs[logrunName]
        log_curve = log_run.log_curves[logName]
        facies_code_names = log_curve.get_code_names()

        if debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: Facies names:')
            print(facies_code_names)

        facies_table = APSMainFaciesTable(facies_table=facies_code_names)
        facies_table.XMLAddElement(topElement)
    with open(outputRMSDataFile, 'w') as file:
        if debug_level > Debug.SOMEWHAT_VERBOSE:
            print(f'Write file: {outputRMSDataFile}')
        root = prettify(topElement)
        file.write(root)


def create2DMapsForVariogramAzimuthAngle(project, inputFile, debug_level=Debug.OFF):

    (gridModelName, zoneParamName, regionParamName, gfNames,
     horizonRefName, horizonRefType, horizonList,
     wellRefName, trajectoryName, logrunName, logName) = readInputXMLFile(inputFile, debug_level)

    if horizonRefName is None or horizonRefType is None:
        return

    print('Create 2D maps in the horizon container to be used for variogram azimuth angle')
    # Get dimensions from the reference map
    # horizons is defined to be a pointer to horizons in RMS by roxapi
    horizons = project.horizons
    [nx, ny, xinc, yinc, xmin, ymin, xmax, ymax, rotation] = get2DMapDimensions(
        horizons, horizonRefName, horizonRefType, debug_level
    )
    # Gauss field names (standard hardcoded names)
    # gaussFieldNames = ['GF1','GF2','GF3','GF4']
    gaussFieldNames = gfNames
    azimuthValue = 0.0
    for hName in horizonList:
        for gfName in gaussFieldNames:
            reprName = gfName + '_VarioAzimuthTrend'
            # Create new horizon data type for this gauss field if not already existing
            createHorizonDataTypeObject(horizons, reprName, debug_level)

            # Set the value in the map to the constant azimuth value
            setConstantValueInHorizon(
                horizons, hName, reprName, azimuthValue, debug_level,
                xmin, ymin, xinc, yinc, nx, ny, rotation
            )


def run(roxar=None, project=None, **kwargs):
    warn("deprecated", DeprecationWarning)
    prefix = get_prefix(**kwargs)
    scriptName = prefix + '/' + 'getRMSProjectData.py'
    inputFile = prefix + '/' + 'getRMSProjectData.xml'
    outputRMSDataFile = prefix + '/' + 'rms_project_data_for_APS_gui.xml'
    debug_level = Debug.OFF
    # Create 2D maps which can be used in RMS petrosim jobs for variogram azimuth angle
    if debug_level >= Debug.ON:
        print('Start running APS workflow preparation script')
        print('Read file: {}'.format(inputFile))
    create2DMapsForVariogramAzimuthAngle(project, inputFile, debug_level)
    if debug_level >= Debug.ON:
        print('Read RMS project and save some data to be read by the APS GUI script')
    scanRMSProjectAndWriteXMLFile(project, inputFile, outputRMSDataFile, debug_level)
    if debug_level >= Debug.ON:
        print('Finished running: ' + scriptName)


# ----------------  Main ----------------------------------------------------
if __name__ == '__main__':
    import roxar
    run(roxar, project)
