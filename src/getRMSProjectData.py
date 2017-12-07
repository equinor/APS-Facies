#!/bin/env python
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
import importlib
import sys
import numpy as np
import roxar
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element


import src.generalFunctionsUsingRoxAPI as gr
import src.APSDataFromRMS as APSDataFromRMS
import src.APSMainFaciesTable as APSMainFaciesTable 
import src.utils.xml as xml

importlib.reload(gr)
importlib.reload(APSDataFromRMS)
importlib.reload(APSMainFaciesTable)
importlib.reload(xml)

from src.utils.constants.simple import Debug
from src.utils.xml import prettify


def readInputXMLFile(modelFileName, debug_level=Debug.OFF):
    """
    This function read user specification of which grid model etc to scan from RMS.
    :param modelFileName:
    :param debug_level:
    :return:
    """
    # Read model if it is defined
    tree = ET.parse(modelFileName)
    root = tree.getroot()

    kw = 'GridModel'
    gridModelObj = root.find(kw)
    if gridModelObj is None:
        print('Error: Missing specification of ' + kw)
        sys.exit()
        
    kw1 = 'Name'
    gridModelNameObj = gridModelObj.find(kw1)
    if gridModelNameObj is None:
        print('Error: Missing specification of keyword ' + kw1 + ' under keyword ' + kw)
        sys.exit()
    text = gridModelNameObj.text
    gridModelName = text.strip()

    kw3 = 'ZoneParameter'
    zoneParamNameObj = gridModelObj.find(kw3)
    if zoneParamNameObj is None:
        print('Error: Missing specification of keyword ' + kw3 + ' under keyword ' + kw)
        sys.exit()
    text = zoneParamNameObj.text
    zoneParamName = text.strip()

    kw4 = 'RegionParameter'
    regionParamName=None
    regionParamNameObj = gridModelObj.find(kw4)
    if regionParamNameObj is not None:
        text = regionParamNameObj.text
        regionParamName = text.strip()
    else:
        print('Note: Missing specification of keyword ' + kw4 + ' under keyword ' + kw)
        print('      You will not be able to use APS models for regions if this is not specified')


    if debug_level >= Debug.VERY_VERBOSE:
        print('Debug output: Grid model:         ' + gridModelName)
        print('Debug output: Zone parameter:     ' + zoneParamName)
        if regionParamName is not None:
            print('Debug output: Region parameter:   ' + regionParamName)

    kw = 'GaussFields'
    gfNames = []
    gfNameObj = root.find(kw)
    text = gfNameObj.text
    names = text.split()
    for i in range(len(names)):
        name = names[i]
        gfNames.append(name)

    kw = 'HorizonReference'
    hRefObj = root.find(kw)
    if hRefObj is None:
        print('Error: Missing specification of ' + kw)
        sys.exit()
    text = hRefObj.get('name')
    horizonRefName = text.strip()
    text = hRefObj.get('type')
    horizonRefType = text.strip()
    if debug_level >= Debug.VERY_VERBOSE:
        print('Debug output: Horizon reference:  ' + horizonRefName + ' with type ' + horizonRefType)

    kw = 'Horizon'
    horizonList = []
    for hObj in root.findall(kw):
        if hObj is not None:
            text = hObj.text
            horizonList.append(text.strip())

    kw1 = 'WellName'
    wellNameRefObj = root.find(kw1)
    if wellNameRefObj is None:
        print('Error: Missing specification of ' + kw1)
        sys.exit()
    text = wellNameRefObj.get('name')
    wellRefName = text.strip()

    kw2 = 'Trajectory'
    trRefObj = wellNameRefObj.find(kw2)
    if trRefObj is None:
        print('Error: Missing specification of ' + kw2 + ' under ' + kw1)
        sys.exit()
    text = trRefObj.get('name')
    trajectoryName = text.strip()

    kw3 = 'Logrun'
    logrunRefObj = trRefObj.find(kw3)
    if logrunRefObj is None:
        print('Error: Missing specification of ' + kw3 + ' under ' + kw2)
        sys.exit()
    text = logrunRefObj.get('name')
    logrunName = text.strip()

    kw4 = 'LogName'
    logNameRefObj = logrunRefObj.find(kw4)
    if logNameRefObj is None:
        print('Error: Missing specification of ' + kw4 + ' under ' + kw3)
        sys.exit()
    text = logNameRefObj.text
    logName = text.strip()

    if debug_level >= Debug.VERY_VERBOSE:
        print(
            'Debug output: Well reference:     ' + wellRefName + '   ' + trajectoryName + '   ' + logrunName + '   ' + logName)

    return [gridModelName, zoneParamName, regionParamName, gfNames, horizonRefName, horizonRefType, horizonList,
            wellRefName, trajectoryName, logrunName, logName]


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
            [zoneValues, codeNamesZone] = gr.getDiscrete3DParameterValues(gridModel, name, realNumber=realizationNumber, debug_level=debug_level)
        # Check if the property type is integer or float type

        if regionParamName is not None:
            # Check if this is the specified region parameter
            if name == regionParamName:
                # Get the region parameter values
                [regionValues, codeNamesRegion] = gr.getDiscrete3DParameterValues(gridModel, name,realNumber=realizationNumber,  debug_level=debug_level)

                
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
    if regionParamName == None:
        # Only zone numbers are reported
        for i in range(len(zoneValues)):
            zVal = zoneValues[i]
            rVal = 0
            key = (zVal,rVal)
            if not key in zonesAndRegions:
                if debug_level >= Debug.VERY_VERBOSE:
                    print('Debug output: Add (zone,region) = ({},{})'.format(str(zVal), str(rVal)))
                zonesAndRegions[key] = 1
    else:
        # Both zone numbers and region numbers are reported
        assert len(zoneValues) == len(regionValues)
        for i in range(len(zoneValues)):
            zVal = zoneValues[i]
            rVal = regionValues[i]
            key = (zVal,rVal)
            if not key in zonesAndRegions:
                if debug_level >= Debug.VERY_VERBOSE:
                    print('Debug output: Add (zone,region) = ({},{})'.format(str(zVal), str(rVal)))
                zonesAndRegions[key] = 1

    # Zone and region informatione

    for key, value in zonesAndRegions.items():
        zNumber = key[0]
        rNumber = key[1]
        tag='ZoneAndRegionNumbers'
        attributes={'zoneNumber':str(zNumber),'regionNumber':str(rNumber)}
        zoneAndRegionElement = Element(tag, attributes)
        zoneAndRegionElement.text = ' '
        gmElement.append(zoneAndRegionElement)        

                
    for name in gfNames:
        gfElement = Element('GaussFieldNames')
        gfElement.text = ' ' + name + ' '
        gmElement.append(gfElement)

    # Get grid dimensions etc for the grid model
    zoneNames = []
    nLayersPerZone = []
    grid = gridModel.get_grid()
    [xmin, xmax, ymin, ymax, zmin, zmax, xLength, yLength,
     azimuthAngle, x0, y0, nx, ny, nz, nZonesGrid, zoneNames, nLayersPerZone] = gr.getGridAttributes(grid, debug_level)
    xinc = xLength / nx
    yinc = yLength / ny

    tag = 'NZones'
    nZonesObj = Element(tag)
    nZonesObj.text = ' ' + str(nZonesGrid) + ' '
    gmElement.append(nZonesObj)

    for i in range(len(zoneNames)):
        tag = 'ZoneName'
        attribute = {'number': str(i + 1), 'nLayers': str(nLayersPerZone[i])}
        name = zoneNames[i]
        zNameObj = Element(tag, attribute)
        zNameObj.text = ' ' + name.strip() + ' '
        gmElement.append(zNameObj)

    tag = 'XSize'
    xsObj = Element(tag)
    xsObj.text = ' ' + str(xLength) + ' '
    gmElement.append(xsObj)

    tag = 'YSize'
    ysObj = Element(tag)
    ysObj.text = ' ' + str(yLength) + ' '
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
    # Finished writing grid model data


    # Start scanning for horizon names and 2D map size information
    found = 0
    if horizonRefName in project.horizons:
        found = 1
    if found == 0:
        print('Error: Specified name for reference horizon: ' + horizonRefName + ' is not an existing horizon')
        sys.exit()

    found = 0
    if horizonRefType in project.horizons[horizonRefName]:
        found = 1
    if found == 0:
        print('Error: Specified type for reference horizon: ' + horizonRefType + ' is not defined')
        sys.exit()
    # Use the specified reference horizon name and type to get 2D surface grid info
    [nx, ny, xinc, yinc, xmin, ymin, xmax, ymax, rotation] = gr.get2DMapDimensions(
        project.horizons, horizonRefName, horizonRefType, debug_level
    )
    tag = 'SurfaceTrendDimensions'
    surfObj = Element(tag)
    topElement.append(surfObj)

    tag = 'NX'
    nxObj = Element(tag)
    nxObj.text = ' ' + str(nx) + ' '
    surfObj.append(nxObj)

    tag = 'NY'
    nyObj = Element(tag)
    nyObj.text = ' ' + str(ny) + ' '
    surfObj.append(nyObj)

    tag = 'Xmin'
    xminObj = Element(tag)
    xminObj.text = ' ' + str(xmin) + ' '
    surfObj.append(xminObj)

    tag = 'Xmax'
    xmaxObj = Element(tag)
    xmaxObj.text = ' ' + str(xmax) + ' '
    surfObj.append(xmaxObj)

    tag = 'Ymin'
    yminObj = Element(tag)
    yminObj.text = ' ' + str(ymin) + ' '
    surfObj.append(yminObj)

    tag = 'Ymax'
    ymaxObj = Element(tag)
    ymaxObj.text = ' ' + str(ymax) + ' '
    surfObj.append(ymaxObj)

    tag = 'Xinc'
    xincObj = Element(tag)
    xincObj.text = ' ' + str(xinc) + ' '
    surfObj.append(xincObj)

    tag = 'Yinc'
    yincObj = Element(tag)
    yincObj.text = ' ' + str(yinc) + ' '
    surfObj.append(yincObj)

    tag = 'Rotation'
    rotObj = Element(tag)
    rotObj.text = ' ' + str(rotation) + ' '
    surfObj.append(rotObj)

    for hName in horizonList:
        tag = 'Horizon'
        hNameObj = Element(tag)
        hNameObj.text = ' ' + copy.copy(hName) + ' '
        topElement.append(hNameObj)

    # Find facies names in reference well log
    well = project.wells[wellRefName]
    trajectory = well.wellbore.trajectories[trajectoryName]
    log_run = trajectory.log_runs[logrunName]
    log_curve = log_run.log_curves[logName]
    faciesCodeNames = log_curve.get_code_names()

    if debug_level >= Debug.VERY_VERBOSE:
        print('Debug output: Facies names: ')
        print(faciesCodeNames)

    faciesTable = APSMainFaciesTable.APSMainFaciesTable(fTable=faciesCodeNames)
    faciesTable.XMLAddElement(topElement)
    # print('Write file: ' + outputRMSDataFile)
    with open(outputRMSDataFile, 'w') as file:
        if debug_level > Debug.SOMEWHAT_VERBOSE:
            print('Write file: ' + outputRMSDataFile)
        root = prettify(topElement)
        file.write(root)
    return


def create2DMapsForVariogramAzimuthAngle(project, inputFile, debug_level=Debug.OFF):
    [gridModelName, zoneParamName, regionParamName, gfNames, horizonRefName, horizonRefType, horizonList,
     wellRefName, trajectoryName, logrunName, logName] = readInputXMLFile(inputFile, debug_level)

    # Get dimensions from the reference map
    # horizons is defined to be a pointer to horizons in RMS by roxapi
    horizons = project.horizons
    [nx, ny, xinc, yinc, xmin, ymin, xmax, ymax, rotation] = gr.get2DMapDimensions(
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
            gr.createHorizonDataTypeObject(horizons, reprName, debug_level)

            # Set the value in the map to the constant azimuth value
            gr.setConstantValueInHorizon(
                horizons, hName, reprName, azimuthValue, debug_level,
                xmin, ymin, xinc, yinc, nx, ny, rotation
            )


# ----------------  Main ----------------------------------------------------
scriptName = 'getRMSProjectData.py'
inputFile = 'getRMSProjectData.xml'
outputRMSDataFile = 'rms_project_data_for_APS_gui.xml'
debug_level = Debug.VERY_VERBOSE

# Create 2D maps which can be used in RMS petrosim jobs for variogram azimuth angle
print('Start running APS workflow preparation script')
print('Read file: ' + inputFile)
print('Create 2D maps in the horizon container to be used for variogram azimuth angle')
create2DMapsForVariogramAzimuthAngle(project, inputFile, debug_level)

print('Read RMS project and save some data to be read by the APS GUI script')
scanRMSProjectAndWriteXMLFile(project, inputFile, outputRMSDataFile, debug_level)
print('Finished running: ' + scriptName)



# print(' ')
# print('Start test output')
# rmsData = APSDataFromRMS.APSDataFromRMS(debug_level)
# rmsData.readRMSDataFromXMLFile(outputRMSDataFile)
# rmsData.printData()
# print('Finished test output')
