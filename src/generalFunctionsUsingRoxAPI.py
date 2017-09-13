#!/bin/env python
import sys

import numpy as np
import roxar


# List of functions in this file
#                                printInfoText(functionName,text)
#                                printError(functionName,text)
#                                printErrorAndTerminate(functionName,text)
# [minimum,maximum,average]    = calcStatisticsFor3DParameter(prop,zoneNumberList,realisation=0)
# param                        = get3DParameter(gridModel,parameterName,realNumber=0,printInfo = 1)
# [activeCellValues]           = getContinuous3DParameterValues(gridModel,parameterName,realNumber=0,printInfo = 1)
# [activeCellValues,codeNames] = getDiscrete3DParameterValues(gridModel,parameterName,realNumber=0,printInfo = 1)
# isOK                         = setContinuous3DParameterValues(gridModel,parameterName,values,realNumber=0,isShared=True,printInfo = 1)
# isOK                         = setDiscrete3DParameterValues(gridModel,parameterName,values,codeNames,realNumber=0,isShared=True,printInfo = 1)


def calcStatisticsFor3DParameter(gridModel, paramName, zoneNumberList, realNumber=0, printInfo=1):
    """Calculates basic characteristics of property. Calculates the basric statistics of the Property object provided.
    Input:
           property       - The Property object we wish to perform calculation on. 
           zoneNumberList - List of zone numbers (counting from 0) for zones that are included in the min,max,average calculation.
                            Empty list or list containing all zones will find min,max,average over all zones
           realNumber     - Realisation number counted from 0 for the parameter to get.

    Output: 
            minimum  - minimum value
            maximum  - maximum value
            average  - average value
    """
    functionName = 'calcStatisticsFor3DParameter'
    [values] = getSelectedGridCells(gridModel, paramName, zoneNumberList, realNumber, printInfo)

    maximum = np.max(values)
    minimum = np.min(values)
    average = np.average(values)
    if printInfo >= 3:
        if len(zoneNumberList) > 0:
            text = ' Calculate min, max, average for parameter: ' + paramName + ' for selected zones '
            printInfoText(functionName, text)
        else:
            text = ' Calculate min, max, average for parameter: ' + paramName
            printInfoText(functionName, text)

        text = ' Min: ' + str(minimum) + '  Max: ' + str(maximum) + '  Average: ' + str(average)
        printInfoText(functionName, text)

    return [minimum, maximum, average]


def calcAverage(nDefinedCells, cellIndexDefined, values):
    """ 
    Calculates average of the values array.
    Input:
           nDefinedCells  - Number of selected cells to average.
           cellIndexDefined - Array of cell indices to cells to be averaged.
           realNumber     - Realisation number counted from 0 for the parameter to get.

    Output: 
            average  - average value
    """
    sumValue = 0.0
    for i in range(nDefinedCells):
        indx = cellIndexDefined[i]
        sumValue += values[indx]
    #        print('value: ' + str(values[indx]))
    average = sumValue / float(nDefinedCells)
    return average


def printInfoText(functionName, text):
    if functionName == ' ':
        print('Debug output: ' + text + '\n')
    else:
        print('Debug output in ' + functionName + ': ' + text + '\n')
    return


def printError(functionName, text):
    print('Error in ' + functionName + ': ' + text)


def printErrorAndTerminate(functionName, text):
    raise ValueError('Error in ' + functionName + ': ' + text + '\n'
                                                                'Error: Must exit from ' + functionName
                     )


def getCellValuesFilteredOnDiscreteParam(code, valueArray):
    """
         Description: Calculate an index array to address all active (physical) cells in the
                      grid corresponding to the cells with specified integer value (code).
                      Is used to identify a subset of all grid cells that have grid cell values
                      equal to the specified value in the input parameter code.
                      Example of use of the output index list cellIndexDefined:
                         indexIn3DParameterVector = cellIndexDefined[i]  
                      where i runs from 1 to nDefinedCells.    
                      Hence if valueArray is all active cell values for the zone parameter and code is a zoneNumber
                      then the cellIndexDefined list will contain a list of all cell numbers for cells belonging
                      to the specified zoneNumber.
         Input:      code - An integer value. The function search through the whole vector valueArray and find
                            all the values equal to code and save its cell index to cellIndexDefined.
                     valueArray - A vector containing the 3D parameter values for the whole grid (all active cells).

         Output:    nDefinedCells - The number of cells found that match the value in the input variable code.
                    cellIndexDefined - A list of the cell indices where the valueArray value is equal to code.
    """
    nDefinedCells = 0
    cellIndexDefined = []
    nCellsTotal = len(valueArray)
    for i in range(nCellsTotal):
        if valueArray[i] == code:
            cellIndexDefined.append(i)
            nDefinedCells += 1

    return [nDefinedCells, cellIndexDefined]


def get3DParameter(gridModel, parameterName, realNumber=0, printInfo=1):
    """Get 3D parameter from grid model.
    Input: 
           gridModel     - Grid model object
           parameterName - Name of 3D parameter to get. 
           realNumber    - Realisation number counted from 0 for the parameter to get.
           printInfo     - (value 0,1,2 or 3) and specify how much info is to be printed to screen.
           functionName  - Name of python function that call this function (Just for more informative print output).

    Output: parameter object
    """
    functionName = 'get3DParameter'
    # Check if specified grid model exists and is not empty
    if gridModel.is_empty():
        text = 'Specified grid model: ' + gridModel.name + ' is empty.'
        printErrorAndTerminate(functionName, text)

    # Check if specified parameter name exists.
    found = 0
    for p in gridModel.properties:
        if p.name == parameterName:
            found = 1
            break

    if found == 0:
        text = ' Specified parameter: ' + parameterName + ' does not exist.'
        printErrorAndTerminate(functionName, text)

    param = gridModel.properties[parameterName]

    return param


def getContinuous3DParameterValues(gridModel, parameterName, realNumber=0, printInfo=1):
    """Get array of continuous values (numpy.float32) from active cells for specified 3D parameter from grid model.
    Input: 
           gridModel     - grid model object
           parameterName - Name of 3D parameter to get. 
           realNumber    - Realisation number counted from 0 for the parameter to get.
           printInfo     - (value 0,1,2 or 3) and specify how much info is to be printed to screen.
           functionName  - Name of python function that call this function (Just for more informative print output).

    Output: numpy array with values for each active grid cell for specified 3D parameter.
    """
    functionName = 'getContinuous3DParameterValues'
    param = get3DParameter(gridModel, parameterName, realNumber, printInfo)
    if param.is_empty(realNumber):
        text = ' Specified parameter: ' + parameterName + ' is empty for realisation ' + str(realNumber)
        printErrorAndTerminate(functionName, text)

    activeCellValues = param.get_values(realNumber)
    return [activeCellValues]


def getDiscrete3DParameterValues(gridModel, parameterName, realNumber=0, printInfo=1):
    """Get array of discrete values (numpy.uint16) from active cells for specified 3D parameter from grid model.
    Input: 
           gridModel     - Grid model object.
           parameterName - Name of 3D parameter to get. 
           realNumber    - Realisation number counted from 0 for the parameter to get.
           printInfo     - (value 0,1,2 or 3) and specify how much info is to be printed to screen. (0 - almost nothing, 3 - also some debug info)
           functionName  - Name of python function that call this function (Just for more informative print output).

    Output: numpy array with values for each active grid cell for specified 3D parameter 
            and a dictionary object with codeNames and values.
    """
    functionName = 'getDiscrete3DParameterValues'
    param = get3DParameter(gridModel, parameterName, realNumber, printInfo)
    if param.is_empty(realNumber):
        text = ' Specified parameter: ' + parameterName + ' is empty for realisation ' + str(realNumber)
        printErrorAndTerminate(functionName, text)

    activeCellValues = param.get_values(realNumber)
    codeNames = param.code_names
    return [activeCellValues, codeNames]


def getSelectedGridCells(gridModel, paramName, zoneNumberList, realNumber, printInfo=1):
    """
    Input:
           gridModel     - Grid model object
           parameterName - Name of 3D parameter to get. 

           zoneNumberList - A list of integer values that are zone numbers (counted from 0). If the list is empty or has all zones
                            included in the list, then grid cells in all zones are updated.
           realNumber    - Realisation number counted from 0 for the parameter to get.
    Output:
           Numpy vector with parameter values for the active cells belonging to the specified zones. Note that the output
           is in general not of the same length as a vector with all active cells.
    """
    functionName = 'getSelectedGridCells'
    allValues = getContinuous3DParameterValues(gridModel, paramName, realNumber, printInfo)
    if len(zoneNumberList) > 0:
        # Get values for the specified zones
        grid3D = gridModel.get_grid(realNumber)
        indexer = grid3D.simbox_indexer
        dimI, dimJ, dimK = indexer.dimensions
        nCellsSelected = 0
        for zoneIndx in indexer.zonation:
            if zoneIndx in zoneNumberList:
                layerRanges = indexer.zonation[zoneIndx]
                for lr in layerRanges:
                    # Get all the cell numbers for the layer range
                    cellNumbers = indexer.get_cell_numbers_in_range((0, 0, lr.start), (dimI, dimJ, lr.stop))
                    # Set values for all cells in this layer
                    nCellsSelected += len(cellNumber)
                    for cIndx in cellNumbers:
                        values.append(allValues[cIndx])
        values = np.asarray(values)
        return [values]
    else:
        return [allValues]


def modifySelectedGridCells(gridModel, zoneNumberList, realNumber, oldValues, newValues):
    # Is used to set new values in existing 3D parameter 
    # for selected cells defined by a list of zone numbers
    grid3D = gridModel.get_grid(realNumber)
    indexer = grid3D.simbox_indexer
    dimI, dimJ, dimK = indexer.dimensions
    for zoneIndx in indexer.zonation:
        if zoneIndx in zoneNumberList:
            layerRanges = indexer.zonation[zoneIndx]
            for lr in layerRanges:
                # Get all the cell numbers for the layer range
                cellNumbers = indexer.get_cell_numbers_in_range((0, 0, lr.start), (dimI, dimJ, lr.stop))
                # Set values for all cells in this layer
                oldValues[cellNumbers] = newValues[cellNumbers]
    return [oldValues]


def setContinuous3DParameterValues(gridModel, parameterName, inputValues, zoneNumberList,
                                   realNumber=0, isShared=True, printInfo=1):
    """Set 3D parameter with values for specified grid model.
    Input: 
           gridModel     - Grid model object
           parameterName - Name of 3D parameter to get.
           inputValues    - A numpy array of length equal to the number of active cells and with continuous values.
                           Only the grid cells belonging to the specified zones are updated even though the values array
                           contain values for all active cells.
           zoneNumberList - A list of integer values that are zone numbers (counted from 0). 
                            If the list is empty or has all zones included in the list, 
                            then grid cells in all zones are updated.
           realNumber    - Realisation number counted from 0 for the parameter to get.
           isShared      - Is set to true or false if the parameter is to be set to shared or non-shared.
           printInfo     - (value 0,1,2 or 3) and specify how much info is to be printed to screen.
                           (0 - almost nothing, 3 - also some debug info)
           functionName  - Name of python function that call this function (Just for more informative print output).

    Output: True if 3D grid model exist and can be updated, False if not.
    """

    functionName = 'setContinuous3DParameterValues'
    # Check if specified grid model exists and is not empty
    if gridModel.is_empty():
        text = 'Specified grid model: ' + gridModel.name + ' is empty.'
        printError(functionName, text)
        return False

    # Check if specified parameter name exists and create new parameter if it does not exist.
    found = 0
    for p in gridModel.properties:
        if p.name == parameterName:
            found = 1
            break

    if found == 0:
        if printInfo >= 3:
            text = 'Create specified parameter: ' + parameterName
            printInfoText(functionName, text)
            if isShared:
                text = 'Set parameter to shared.'
                printInfoText(functionName, text)
            else:
                text = 'Set parameter to non-shared.'
                printInfoText(functionName, text)

        p = gridModel.properties.create(parameterName, roxar.GridPropertyType.continuous, np.float32)
        currentValues = np.zeros(len(inputValues), np.float32)
        [currentValues] = modifySelectedGridCells(gridModel, zoneNumberList, realNumber, currentValues, inputValues)
        p.set_values(currentValues, realNumber)
        p.set_shared(isShared, realNumber)
    else:

        if printInfo >= 3:
            text = 'Update specified parameter: ' + parameterName
            printInfoText(functionName, text)

        # Parameter exist, but check if it is empty or not
        p = gridModel.properties[parameterName]
        if p.is_empty(realNumber):
            # Create parameter values (which are initialized to 0)
            grid3D = gridModel.get_grid(realNumber)
            v = np.zeros(grid3D.defined_cell_count, np.float32)
            p.set_values(v, realNumber)

        # Get all active cell values
        p = get3DParameter(gridModel, parameterName, realNumber, printInfo)
        if p.is_empty(realNumber):
            text = ' Specified parameter: ' + parameterName + ' is empty for realisation ' + str(realNumber)
            printErrorAndTerminate(functionName, text)

        currentValues = p.get_values(realNumber)
        [currentValues] = modifySelectedGridCells(gridModel, zoneNumberList, realNumber, currentValues, inputValues)
        p.set_values(currentValues, realNumber)
        p.set_shared(isShared, realNumber)
    return True


def combineCodeNames(originalCodeNames, newCodeNames):
    error = 0
    codeValList = newCodeNames.keys()
    for code in codeValList:
        if not (code in originalCodeNames):
            # New code
            u = newCodeNames.get(code)
            for k in originalCodeNames:
                v = originalCodeNames.get(k)
                if u == v:
                    # The facies name for this code already exist
                    error = 1
                    break
            item = {code: u}
            originalCodeNames.update(item)
            # error is 1 if the new facies code to be added to the original one has a facies name that already is used
        else:
            # not a new code
            u = newCodeNames.get(code)
            v = originalCodeNames.get(code)
            if u != v:
                # The code has different names in the existing original and the new codeNames dictionary
                error = 1

    return [originalCodeNames, error]


def setDiscrete3DParameterValues(gridModel, parameterName, inputValues, zoneNumberList, codeNames,
                                 realNumber=0, isShared=True, printInfo=1):
    """Set discrete 3D parameter with values for specified grid model.
    Input: 
           gridModel     - Grid model object
           parameterName - Name of 3D parameter to get. 
           inputValues    - A numpy array of length equal to the number of active cells and with continuous values.
                           Only the grid cells belonging to the specified zones are updated even though the values array
                           contain values for all active cells.
           zoneNumberList - A list of integer values that are zone numbers (counted from 0). If the list is empty or has all zones
                            included in the list, then grid cells in all zones are updated.
           codeNames     - A dictionary with code names and code values for the discrete parameter values of the form as in the example:
                           {1: 'F1', 2: 'F2',3: 'F3'}. 
                           NOTE: Be sure to input a codeNames dictionary containing all relevant facies for 
                           for all zones, not only the zones that are updated by this function. If not, then 
                           existing facies names and codes for zones that are not updated will be lost 
                           from the facies table and need to be re-created manually or by script.
           realNumber    - Realisation number counted from 0 for the parameter to get.
           isShared      - Is set to true or false if the parameter is to be set to shared or non-shared.
           printInfo     - (value 0,1,2 or 3) and specify how much info is to be printed to screen.
           functionName  - Name of python function that call this function (Just for more informative print output).

    Output: True if 3D grid model exist and can be updated or 
             not if the 3D grid does not exist or if a new facies code is introduced but the corresponding facies name already exits.
    """
    functionName = 'setDiscrete3DParameterValues'
    # Check if specified grid model exists and is not empty
    if gridModel.is_empty():
        text = 'Specified grid model: ' + gridModel.name + ' is empty.'
        printError(functionName, text)
        return False

    # Check if specified parameter name exists and create new parameter if it does not exist.
    found = 0
    for p in gridModel.properties:
        if p.name == parameterName:
            found = 1
            break

    if found == 0:
        if printInfo >= 3:
            text = ' Create specified parameter: ' + parameterName + ' in ' + gridModel.name
            printInfoText(functionName, text)
            if isShared:
                text = ' Set parameter to shared.'
                printInfoText(functionName, text)
            else:
                text = ' Set parameter to non-shared.'
                printInfoText(functionName, text)

        p = gridModel.properties.create(parameterName, roxar.GridPropertyType.discrete, np.uint16)
        currentValues = np.zeros(len(inputValues), np.uint16)
        [currentValues] = modifySelectedGridCells(gridModel, zoneNumberList, realNumber, currentValues, inputValues)
        p.set_values(currentValues, realNumber)
        p.set_shared(isShared, realNumber)
        p.code_names = codeNames
    else:
        if printInfo >= 3:
            text = ' Update specified parameter: ' + parameterName + ' in ' + gridModel.name
            printInfoText(functionName, text)

        p = gridModel.properties[parameterName]
        if p.is_empty(realNumber):
            # Create parameter values (which are initialized to 0)
            grid3D = gridModel.get_grid(realNumber)
            v = np.zeros(grid3D.defined_cell_count, np.uint16)
            p.set_values(v, realNumber)

        # Get all active cell values
        p = get3DParameter(gridModel, parameterName, realNumber, printInfo)
        if p.is_empty(realNumber):
            text = ' Specified parameter: ' + parameterName + ' is empty for realisation ' + str(realNumber)
            printErrorAndTerminate(functionName, text)

        currentValues = p.get_values(realNumber)
        [currentValues] = modifySelectedGridCells(gridModel, zoneNumberList, realNumber, currentValues, inputValues)
        p.set_values(currentValues, realNumber)

        p.set_shared(isShared, realNumber)
        originalCodeNames = p.code_names.copy()
        [updatedCodeNames, err] = combineCodeNames(originalCodeNames, codeNames)
        if err == 1:
            text1 = ' Try to define a new facies code with a facies name that already is used define a new facies name\n'
            text2 = ' for a facies code that already exists when updating facies realisation\n'
            printError(functionName, '\n' + text1 + text2)
            print('Original facies codes from RMS project: ')
            print(repr(originalCodeNames))
            print('New facies codes specified in current APS model: ')
            print(repr(codeNames))
            return False
        p.code_names = updatedCodeNames
        if printInfo >= 3:
            text = 'Updated facies table: '
            printInfoText(functionName, text)
            print(p.code_names)
    return True


def getGridAttributes(grid, printInfo):
    indexer = grid.grid_indexer
    dimensions = indexer.dimensions

    # Get Max and Min coordinates
    cell_numbers = indexer.get_cell_numbers_in_range((0, 0, 0), dimensions)
    cell_corners = grid.get_cell_corners(cell_numbers)

    xmin = cell_corners[:, :, 0].min()
    xmax = cell_corners[:, :, 0].max()
    ymin = cell_corners[:, :, 1].min()
    ymax = cell_corners[:, :, 1].max()
    zmin = cell_corners[:, :, 2].min()
    zmax = cell_corners[:, :, 2].max()

    if printInfo >= 3:
        print('Min. X: {}   | Max. X: {}'.format(xmin, xmax))
        print('Min. Y: {}   | Max. Y: {}'.format(ymin, ymax))
        print('Min. Z: {}   | Max. Z: {}'.format(zmin, zmax))
        print('------------------------------------------------')

    # Get number of cells
    total_cells = dimensions[0] * dimensions[1] * dimensions[2]

    # Get Zone names
    zoneNames = []
    for i, zone_index in enumerate(indexer.zonation.keys(), start=1):
        zone_name = grid.zone_names[zone_index]
        zoneNames.append(zone_name)

    if printInfo >= 3:
        print('Total no. of cells:', total_cells)
        print('No. of defined cells:', grid.defined_cell_count)
        print('No. of undefined cells:', total_cells - grid.defined_cell_count)
        print('------------------------------------------------')

        # Get dimensions
        print('Number of columns:', dimensions[0])
        print('Number of rows:', dimensions[1])
        print('Number of layers:', dimensions[2])
        print('No. of zones:', len(indexer.zonation))
        print('------------------------------------------------')

        # Print Zones and Layers
        zoneNames = []
        for i, zone_index in enumerate(indexer.zonation.keys(), start=1):
            zone_name = grid.zone_names[zone_index]
            zoneNames.append(zone_name)
            number_layers = 0
            layers = ""
            for layer_range in indexer.zonation[zone_index]:
                start = layer_range[0]
                end = layer_range[-1]
                number_layers += (end + 1 - start)
                # Indexes start with 0, so add 1 to give user-friendly output
                layers = "{}-{} ".format(start + 1, end + 1)
            print('Zone{}: "{}", Layers {} ({} layers)'.format(i, zone_name, layers, number_layers))
        print(' ')
    nZones = len(indexer.zonation)

    [simBoxXLength, simBoxYLength, asimuthAngle, x0, y0] = getGridSimBoxSize(grid, printInfo)
    return [xmin, xmax, ymin, ymax, zmin, zmax, simBoxXLength, simBoxYLength, asimuthAngle, x0, y0,
            dimensions[0], dimensions[1], dimensions[2], nZones, zoneNames]


def getGridSimBoxSize(grid, printInfo):
    indexer = grid.grid_indexer
    (nx, ny, nz) = indexer.dimensions

    # Calculate dimensions of the simulation box
    cell_00 = grid.get_cell_corners_by_index((0, 0, 0))
    cell_10 = grid.get_cell_corners_by_index((nx - 1, 0, 0))
    cell_01 = grid.get_cell_corners_by_index((0, ny - 1, 0))
    cell_11 = grid.get_cell_corners_by_index((nx - 1, ny - 1, 0))
    x2 = cell_01[2][0]
    x1 = cell_10[1][0]
    x0 = cell_00[0][0]
    y2 = cell_01[2][1]
    y1 = cell_10[1][1]
    y0 = cell_00[0][1]
    simBoxXLength = np.sqrt((x1 - x0) * (x1 - x0) + (y1 - y0) * (y1 - y0))
    simBoxYLength = np.sqrt((x2 - x0) * (x2 - x0) + (y2 - y0) * (y2 - y0))
    cosTheta = (y2 - y0) / simBoxYLength
    sinTheta = (x2 - x0) / simBoxYLength
    asimuthAngle = np.arctan(sinTheta / cosTheta)
    asimuthAngle = asimuthAngle * 180.0 / np.pi
    if printInfo >= 3:
        print('Debug output: Length in x direction:  ' + str(simBoxXLength))
        print('Debug output: Length in y direction:  ' + str(simBoxYLength))
        print('Debug output: Sim box rotation angle: ' + str(asimuthAngle))
    return [simBoxXLength, simBoxYLength, asimuthAngle, x0, y0]


def createHorizonDataTypeObject(horizons, representationName, printInfo=0):
    # Check if horizon representation (horizon data type) exist
    # for specified type. If not, create a new representation
    reprObj = None
    for representation in horizons.representations:
        if representation.name == representationName:
            reprObj = representation
            break
    if reprObj == None:
        # Create new representation
        reprObj = horizons.representations.create(representationName,
                                                  roxar.GeometryType.surface,
                                                  roxar.VerticalDomain.depth)
        if printInfo >= 3:
            text = 'Debug ouput: Create new data type for horizon to be used '
            text = text + 'for variogram asimuth trend'
            print(text)

    return reprObj


def get2DMapDimensions(horizons, horizonName, representationName, printInfo):
    # Read information about 2D grid size,orientation and resolution
    # from existing 2D map.
    horizonObj = None
    for h in horizons:
        if h.name == horizonName:
            horizonObj = h
            break
    if horizonObj == None:
        raise ValueError('Error in  get2DMapInfo\n'
                         'Error: Horizon name: ' + horizonName + ' does not exist'
                         )

    reprObj = None
    for representation in horizons.representations:
        if representation.name == representationName:
            reprObj = representation
            break
    if reprObj == None:
        raise ValueError('Error in  get2DMapInfo\n'
                         'Error: Horizons data type: ' + representationName + ' does not exist'
                         )

    surface = horizons[horizonName][representationName]
    if not isinstance(surface, roxar.Surface):
        raise ValueError('Error in get2DMapInfo\n'
                         'Error: Specified object is not a 2D grid'
                         )
    grid = surface.get_grid()
    values = grid.get_values()
    shape = values.shape
    xinc = grid.increment[0]
    yinc = grid.increment[1]
    nx = shape[0]
    ny = shape[1]
    coordinates = grid.get_coordinates()
    coordinates.mask[:, :, :2] = 0
    xmin = coordinates[:, :, 0].min()
    xmax = coordinates[:, :, 0].max()
    ymin = coordinates[:, :, 1].min()
    ymax = coordinates[:, :, 1].max()
    rotation = grid.rotation
    if printInfo >= 3:
        print('Debug output:  For 2D map')
        print('  Map xmin: ' + str(xmin))
        print('  Map xmax: ' + str(xmax))
        print('  Map ymin: ' + str(ymin))
        print('  Map ymax: ' + str(ymax))
        print('  Map xinc: ' + str(xinc))
        print('  Map yinc: ' + str(yinc))
        print('  Map nx:   ' + str(nx))
        print('  Map ny:   ' + str(ny))
        print('  Map rotation:   ' + str(rotation))
    return [nx, ny, xinc, yinc, xmin, ymin, xmax, ymax, rotation]


def setConstantValueInHorizon(horizons, horizonName, reprName, inputValue,
                              printInfo=0, xmin=0, ymin=0, xinc=0, yinc=0, nx=0, ny=0, rotation=0):
    # This function will replace a horizon with specified name and type with a new one with value equal 
    # to the constant value specified in variable inputValue. The 2D grid dimensions can also specified if new maps
    # must created.
    # Find horizon with specified name. Must exist.
    horizonObj = None
    for h in horizons:
        if h.name == horizonName:
            horizonObj = h
            break
    if horizonObj == None:
        raise ValueError('Error in updateHorizonObject\n'
                         'Error: Horizon name: ' + horizonName + ' does not exist'
                         )

    # Find the correct representation. Must exist.
    reprObj = None
    for representation in horizons.representations:
        if representation.name == reprName:
            reprObj = representation
            break
    if reprObj == None:
        raise ValueError('Error in updateHorizonObject\n'
                         'Error: Horizons data type: ' + reprName + ' does not exist'
                         )

    surfaceObj = horizons[horizonName][reprName]
    if isinstance(surfaceObj, roxar.Surface):
        emptyGrid = 0
        try:
            grid = surfaceObj.get_grid()
        except RuntimeError:
            # Create surface 
            emptyGrid = 1
            if nx == 0 or ny == 0:
                print('Error in  setConstantValueInHorizon:  Grid dimensions are not specified')
                sys.exit()
            grid = roxar.RegularGrid2D.create(xmin, ymin, xinc, yinc, nx, ny, rotation)
            values = grid.get_values()
            values[:] = inputValue
            grid.set_values(values)
            surfaceObj.set_grid(grid)
            if printInfo >= 3:
                text = 'Debug output: ' + 'Create trend surface ' + reprName
                text = text + ' for variogram asimuth in ' + horizonName
                text = text + ' Value: ' + str(inputValue)
                print(text)

        if emptyGrid == 0:
            # Modify grid values
            values = grid.get_values()
            values[:] = inputValue
            grid.set_values(values)
            surfaceObj.set_grid(grid)
            if printInfo >= 3:
                text = 'Debug output: ' + 'Update trend surface ' + reprName
                text = text + ' for variogram asimuth in ' + horizonName
                text = text + ' Value: ' + str(inputValue)
                print(text)
    return
