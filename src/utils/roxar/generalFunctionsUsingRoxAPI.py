#!/bin/env python
# -*- coding: utf-8 -*-
import sys
import numpy as np
import roxar

from src.utils.constants.simple import Debug


# List of functions in this file
#                                print_debug_information(function_name, text)
#                                print_error(function_name, text)
#                                raise_error(function_name, text)
# [minimum,maximum,average]    = calcStatisticsFor3DParameter(prop, zoneNumberList, realisation=0)
# param                        = get3DParameter(gridModel, parameterName, debug_level=1)
# activeCellValues             = getContinuous3DParameterValues(gridModel, parameterName, realNumber=0,debug_level=1)
# [activeCellValues,codeNames] = getDiscrete3DParameterValues(gridModel, parameterName, realNumber=0, debug_level 1)
# isOK                         = setContinuous3DParameterValues(gridModel, parameterName, values, realNumber=0, isShared=True, debug_level=1)
# isOK                         = setDiscrete3DParameterValues(gridModel, parameterName, values, codeNames, realNumber=0, isShared=True, debug_level=1)
from src.utils.exceptions.general import raise_error
from src.utils.io import print_debug_information, print_error
from src.utils.roxar.grid_model import get3DParameter, modifySelectedGridCells, combineCodeNames


def setContinuous3DParameterValues(gridModel, parameterName, inputValues, zoneNumberList,
                                   realNumber=0, isShared=True, debug_level=Debug.OFF):
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
           debug_level     - (value 0,1,2 or 3) and specify how much info is to be printed to screen.
                           (0 - almost nothing, 3 - also some debug info)
           functionName  - Name of python function that call this function (Just for more informative print output).

    Output: True if 3D grid model exist and can be updated, False if not.
    """

    functionName = setContinuous3DParameterValues.__name__
    # Check if specified grid model exists and is not empty
    if gridModel.is_empty():
        text = 'Specified grid model: ' + gridModel.name + ' is empty.'
        print_error(functionName, text)
        return False

    # Check if specified parameter name exists and create new parameter if it does not exist.
    found = 0
    for p in gridModel.properties:
        if p.name == parameterName:
            found = 1
            break

    if found == 0:
        if debug_level >= Debug.VERY_VERBOSE:
            text = 'Create specified parameter: ' + parameterName
            print_debug_information(functionName, text)
            if isShared:
                text = 'Set parameter to shared.'
                print_debug_information(functionName, text)
            else:
                text = 'Set parameter to non-shared.'
                print_debug_information(functionName, text)

        p = gridModel.properties.create(parameterName, roxar.GridPropertyType.continuous, np.float32)
        currentValues = np.zeros(len(inputValues), np.float32)
        currentValues = modifySelectedGridCells(gridModel, zoneNumberList, realNumber, currentValues, inputValues)
        p.set_values(currentValues, realNumber)
        p.set_shared(isShared, realNumber)
    else:

        if debug_level >= Debug.VERY_VERBOSE:
            text = 'Update specified parameter: ' + parameterName
            print_debug_information(functionName, text)

        # Parameter exist, but check if it is empty or not
        p = gridModel.properties[parameterName]
        if p.is_empty(realNumber):
            # Create parameter values (which are initialized to 0)
            grid3D = gridModel.get_grid(realNumber)
            v = np.zeros(grid3D.defined_cell_count, np.float32)
            p.set_values(v, realNumber)

        # Get all active cell values
        p = get3DParameter(gridModel, parameterName, debug_level)
        if p.is_empty(realNumber):
            text = ' Specified parameter: ' + parameterName + ' is empty for realisation ' + str(realNumber)
            raise_error(functionName, text)

        currentValues = p.get_values(realNumber)
        currentValues = modifySelectedGridCells(gridModel, zoneNumberList, realNumber, currentValues, inputValues)
        p.set_values(currentValues, realNumber)
        p.set_shared(isShared, realNumber)
    return True


def setContinuous3DParameterValuesInZone(gridModel, parameterNameList, inputValuesForZoneList, zoneNumber,
                                         realNumber=0, isShared=False, debug_level=Debug.OFF):
    """Set 3D parameter with values for specified grid model for specified zone (and region)
    Input:
           gridModel     - Grid model object
           parameterNameList - List of names of 3D parameter to update.
           inputValuesForZoneList  - A list of numpy 3D arrays. They corresponds to the parameter names in parameterNameList.
                                     The size of the numpy input arrays are (nx,ny,nLayers) where nx, ny must match
                                     the gridModels 3D grid size for the simulation box grid and nLayers must match
                                     the number of layers for the zone in simulationx box. Note that since nx, ny
                                     are the simulation box grid size, they can be larger than the number of cells
                                     reported for the grid in reverse faulted grids. The grid values must be of type
                                     numpy.float32. Only the grid cells belonging to the specified zone are updated,
                                     and error is raised if the number of grid cells for the zone doesn't match
                                     the size of the input array.
           zoneNumber    - The zone number (counted from 0 in the input)
           realNumber    - Realisation number counted from 0 for the parameter to get.
           isShared      - Is set to true or false if the parameter is to be set to shared or non-shared.
           debug_level   - (value 0,1,2 or 3) and specify how much info is to be printed to screen.
                           (0 - almost nothing, 3 - also some debug info)
    """

    functionName = setContinuous3DParameterValuesInZone.__name__
    # Check if specified grid model exists and is not empty
    if gridModel.is_empty():
        text = 'Specified grid model: ' + gridModel.name + ' is empty.'
        print_error(functionName, text)
        return False

    # Check if the parameter is defined and create new if not existing
    grid3D = gridModel.get_grid(realNumber)

    # Find grid layers for the zone
    indexer = grid3D.simbox_indexer
    dimensions = indexer.dimensions
    zonation = indexer.zonation
    layer_ranges = zonation[zoneNumber]
    nx = dimensions[0]
    ny = dimensions[1]
    nz = dimensions[2]
    zoneName = grid3D.zone_names[zoneNumber]
    zone_cell_numbers = []
    start_layer = nz
    end_layer = 0
    for layer_range in layer_ranges:
        for layer in layer_range:
            if start_layer > layer:
                start_layer = layer
            if end_layer < layer:
                end_layer = layer
    end_layer = end_layer+1
    start = (0,0,start_layer)
    end = (nx,ny,end_layer)
    zone_cell_numbers = indexer.get_cell_numbers_in_range(start,end)

    nLayers = end_layer-start_layer
    # All input data vectors are from the same zone and has the same size
    inputArrayShape = inputValuesForZoneList[0].shape
    if nx != inputArrayShape[0] or ny != inputArrayShape[1] or nLayers != inputArrayShape[2]:
        raise IOError('Input array with values has different dimensions than the grid model:\n'
                      'Grid model nx: {}  Input array nx: {}\n'
                      'Grid model ny: {}  Input array ny: {}\n'
                      'Grid model nLayers for zone {} is: {}    Input array nz: {}'
                      ''.format(str(nx), str(inputArrayShape[0]), str(ny), str(inputArrayShape[1]), str(zoneNumber), str(nLayers), str(inputArrayShape[2]))
                      )

    # print('start_layer: {}   end_layer: {}'.format(str(start_layer),str(end_layer-1)))
    defined_cell_indices = indexer.get_indices(zone_cell_numbers)
    i_indices = defined_cell_indices[:,0]
    j_indices = defined_cell_indices[:,1]
    k_indices = defined_cell_indices[:,2]

    # Loop over all parameter names
    for paramIndx in range(len(parameterNameList)):
        paramName =  parameterNameList[paramIndx]
        inputValuesForZone = inputValuesForZoneList[paramIndx]
        found = False
        propertyParam = None
        for p in gridModel.properties:
            if p.name == paramName:
                found = True
                propertyParam = p
                break
        if not found:
            # Create new parameter
            propertyParam = gridModel.properties.create(paramName, roxar.GridPropertyType.continuous, np.float32)
            propertyParam.set_shared(isShared, realNumber)
            if debug_level >= Debug.VERY_VERBOSE:
                text = 'Create specified parameter: ' + paramName
                print_debug_information(functionName, text)
                if isShared:
                    text = 'Set parameter to shared.'
                    print_debug_information(functionName, text)
                else:
                    text = 'Set parameter to non-shared.'
                    print_debug_information(functionName, text)

        assert propertyParam is not None
        if propertyParam.is_empty(realNumber):
            # Initialize to 0 if empty
            #  v = np.zeros(grid3D.defined_cell_count, np.float32)
            v = grid3D.generate_values(np.float32)
            propertyParam.set_values(v, realNumber)

        # Get current values
        currentValues = propertyParam.get_values(realNumber)

        # Create 3D array for all cells in the grid including inactive cells
        new_3D_array = np.zeros((nx,ny,nz), dtype=float,order='F')

        # Assign values from input array into the 3D grid array
        # Note that input array is of dimension (nx,ny,nLayers)
        # where nLayers is the number of layers of the input grid
        # These layers must correspond to layer from start_layer untill but not including end_layer
        # in the full 3D grid

        for k in range(start_layer,end_layer):
            new_3D_array[:,:,k] = inputValuesForZone[:,:,k - start_layer]

        # Since the cell numbers and the indices all are based on the same range,
        # it is possible to use numpy vectorization to copy
        currentValues[zone_cell_numbers] = new_3D_array[i_indices, j_indices, k_indices]
        propertyParam.set_values(currentValues, realNumber)

    return True


def setContinuous3DParameterValuesInZoneRegion(
        gridModel, parameterNameList, inputValuesForZoneList, zoneNumber,
        regionNumber=0, regionParamName=None, realNumber=0, isShared=False, debug_level=Debug.OFF
):
    """Set 3D parameter with values for specified grid model for specified zone (and region)
    Input:
           gridModel     - Grid model object
           parameterNameList - List of names of 3D parameter to update.
           inputValuesForZoneList  - A list of numpy 3D arrays. They corresponds to the parameter names in parameterNameList.
                                     The size of the numpy input arrays are (nx,ny,nLayers) where nx, ny must match
                                     the gridModels 3D grid size for the simulation box grid and nLayers must match
                                     the number of layers for the zone in simulationx box. Note that since nx, ny
                                     are the simulation box grid size, they can be larger than the number of cells
                                     reported for the grid in reverse faulted grids. The grid values must be of type
                                     numpy.float32. Only the grid cells belonging to the specified zone are updated,
                                     and error is raised if the number of grid cells for the zone doesn't match
                                     the size of the input array.
           zoneNumber    - The zone number (counted from 0 in the input)
           regionNumber  - The region number for the grid cells to be updated.
           regionParamName - The name of the 3D grid parameter containing a discrete 3D parameter with region numbers
           realNumber    - Realisation number counted from 0 for the parameter to get.
           isShared      - Is set to true or false if the parameter is to be set to shared or non-shared.
           debug_level   - (value 0,1,2 or 3) and specify how much info is to be printed to screen.
                           (0 - almost nothing, 3 - also some debug info)
    """

    functionName = setContinuous3DParameterValuesInZoneRegion.__name__
    # Check if specified grid model exists and is not empty
    if gridModel.is_empty():
        text = 'Specified grid model: ' + gridModel.name + ' is empty.'
        print_error(functionName, text)
        return False

    # Check if the parameter is defined and create new if not existing
    grid3D = gridModel.get_grid(realNumber)

    # Find grid layers for the zone
    indexer = grid3D.simbox_indexer
    dimensions = indexer.dimensions
    zonation = indexer.zonation
    layer_ranges = zonation[zoneNumber]
    nx = dimensions[0]
    ny = dimensions[1]
    nz = dimensions[2]
    zoneName = grid3D.zone_names[zoneNumber]
    zone_cell_numbers = []
    start_layer = nz
    end_layer = 0
    for layer_range in layer_ranges:
        for layer in layer_range:
            if start_layer > layer:
                start_layer = layer
            if end_layer < layer:
                end_layer = layer
    end_layer = end_layer+1
    start = (0,0,start_layer)
    end = (nx,ny,end_layer)
    zone_cell_numbers = indexer.get_cell_numbers_in_range(start,end)

    nLayers = end_layer-start_layer
    # All input data vectors are from the same zone and has the same size
    inputArrayShape = inputValuesForZoneList[0].shape
    if nx != inputArrayShape[0] or ny != inputArrayShape[1] or nLayers != inputArrayShape[2]:
        raise IOError('Input array with values has different dimensions than the grid model:\n'
                      'Grid model nx: {}  Input array nx: {}\n'
                      'Grid model ny: {}  Input array ny: {}\n'
                      'Grid model nLayers for zone {} is: {}    Input array nz: {}'
                      ''.format(str(nx), str(inputArrayShape[0]), str(ny), str(inputArrayShape[1]),
                                str(zoneNumber), str(nLayers), str(inputArrayShape[2]))
                      )

    # print('start_layer: {}   end_layer: {}'.format(str(start_layer),str(end_layer-1)))
    defined_cell_indices = indexer.get_indices(zone_cell_numbers)
    i_indices = defined_cell_indices[:,0]
    j_indices = defined_cell_indices[:,1]
    k_indices = defined_cell_indices[:,2]

    # Get region parameter values
    regionParamValues = None
    if regionParamName is not None:
        if len(regionParamName) > 0:
            p = gridModel.properties[regionParamName]
            regionParamValues = p.get_values(realNumber)

    # Loop over all parameter names
    for paramIndx in range(len(parameterNameList)):
        paramName =  parameterNameList[paramIndx]
        inputValuesForZone = inputValuesForZoneList[paramIndx]
        found = False
        propertyParam = None
        for p in gridModel.properties:
            if p.name == paramName:
                found = True
                propertyParam = p
                break
        if not found:
            # Create new parameter
            propertyParam = gridModel.properties.create(paramName, roxar.GridPropertyType.continuous, np.float32)
            propertyParam.set_shared(isShared, realNumber)
            if debug_level >= Debug.VERY_VERBOSE:
                text = 'Create specified parameter: ' + paramName
                print_debug_information(functionName, text)
                if isShared:
                    text = 'Set parameter to shared.'
                    print_debug_information(functionName, text)
                else:
                    text = 'Set parameter to non-shared.'
                    print_debug_information(functionName, text)

        assert propertyParam is not None
        if propertyParam.is_empty(realNumber):
            # Initialize to 0 if empty
            #  v = np.zeros(grid3D.defined_cell_count, np.float32)
            v = grid3D.generate_values(np.float32)
            propertyParam.set_values(v, realNumber)

        # Get current values
        currentValues = propertyParam.get_values(realNumber)

        # Assign values from input array into the 3D grid array
        # Note that input array is of dimension (nx,ny,nLayers)
        # where nLayers is the number of layers of the input grid
        # These layers must correspond to layer from start_layer untill but not including end_layer
        # in the full 3D grid
        if regionParamValues is not None:
            for indx in range(len(i_indices)):
                i = i_indices[indx]
                j = j_indices[indx]
                k = k_indices[indx]
                # print('(i,j,k)=({},{},{})'.format(str(i), str(j), str(k)))
                cell_index = (i,j,k)
                cell_number = indexer.get_cell_numbers(cell_index)
                if start_layer <= k < end_layer:
                    if regionParamValues[cell_number] == regionNumber:
                        currentValues[cell_number] = inputValuesForZone[i,j,k - start_layer]
        else:
            # Create 3D array for all cells in the grid including inactive cells
            new_3D_array = np.zeros((nx,ny,nz), dtype=float,order='F')
            for k in range(start_layer,end_layer):
                new_3D_array[:, :, k] = inputValuesForZone[:, :, k - start_layer]

            # Since the cell numbers and the indices all are based on the same range,
            # it is possible to use numpy vectorization to copy
            currentValues[zone_cell_numbers] = new_3D_array[i_indices, j_indices, k_indices]

        propertyParam.set_values(currentValues, realNumber)

    return True


def updateContinuous3DParameterValues(gridModel, parameterName, inputValues, nDefinedCells=0, cellIndexDefined=None,
                                      realNumber=0, isShared=True, setInitialValues=False, debug_level=Debug.OFF):
    """
    Description:
    Set 3D parameter with continuous values for specified grid model. The input is specified for a subset of all grid cells.
    This subset is defined by the numpy vector cellIndexDefined and the number of values is nDefinedCells.
    Only the subset of cells will be updated unless the parameter setInitialValues is set. In that case all cells not covered
    by the cellIndexDefined will be initializes to 0.0. The input numpy vector inputValues has length equal to number of
    active grid cells for the grid model and contain the values to be assigned to the 3D parameter with
    name parameterName belonging to the grid model with name gridModel.
    If the grid parameter with name parameterName does not exist, it will be created and assigned value 0 in all
    cells except the cells defined by the cellIndexDefined where it will be assigned the values taken from
    the  inputValues vector. If the grid parameter exist, the grid cells with indices defined in cellIndexDefined will be
    updated with values from inputValues.
    :param setInitialValues:
    :param gridModel:   Grid model object
    :param parameterName: Name of 3D parameter to update.
    :param inputValues:  A numpy array of length equal to nActiveCells where nActiveCells is the number of all grid cells in the
                         grid model that is not inactive and will therefore usually be a much longer vector than nDefinedCells.
                         Only the values in this vector corresponding to the selected cells defined by cellIndexDefined will be used.
                         The values are of type continuous.

    :param nDefinedCells: Length of the list cellIndexDefined
    :param cellIndexDefined: A list with cell indices in the array of all active cells for the grid model. The subset of cells
                             defined by this index array are the grid cells to be updated.
    :param realNumber: Realisation number counted from 0 for the 3D parameter.
    :param isShared:   Is set to true or false if the parameter is to be set to shared or non-shared.
    :param debug_level: Specify how much info is to be printed to screen. (0 - almost nothing output to screen, 3 - much output to screen)

    """

    functionName = updateContinuous3DParameterValues.__name__
    if cellIndexDefined is not None:
        assert nDefinedCells == len(cellIndexDefined)

    grid3D = gridModel.get_grid(realNumber)
    nActiveCells = grid3D.defined_cell_count
    if nActiveCells != len(inputValues):
        raise ValueError('Mismatch in number of active cells={} and length of input array with values = {}'
                         ''.format(str(nActiveCells), str(len(inputValues)))
                         )

    # Check if specified grid model exists and is not empty
    if gridModel.is_empty():
        raise ValueError(
            'Specified grid model: {} is empty.'
            'Cannot create parameter: {} '
            ''.format(gridModel.name, parameterName)
        )

    # Check if specified parameter name exists and create new parameter if it does not exist.
    found = 0
    for p in gridModel.properties:
        if p.name == parameterName:
            found = 1
            break

    if found == 0:
        if debug_level >= Debug.VERY_VERBOSE:
            text = ' Create specified parameter: ' + parameterName + ' in ' + gridModel.name
            print_debug_information(functionName, text)
            if isShared:
                text = 'Set parameter to shared.'
                print_debug_information(functionName, text)
            else:
                text = 'Set parameter to non-shared.'
                print_debug_information(functionName, text)

        # Create a new 3D parameter with the specified name of type float32
        p = gridModel.properties.create(parameterName, roxar.GridPropertyType.continuous, np.float32)

        # Initialize the values to 0 for this new 3D parameter
        currentValues = np.zeros(nActiveCells, np.float32)

        # Assign values to the defined cells as specified in cellIndexDefined index vector
        # Using vector operations for numpy vector:
        if nDefinedCells > 0:
            currentValues[cellIndexDefined] = inputValues[cellIndexDefined]
        else:
            currentValues = inputValues

        p.set_values(currentValues, realNumber)
        p.set_shared(isShared, realNumber)
    else:
        if debug_level >= Debug.VERY_VERBOSE:
            text = ' Update specified parameter: ' + parameterName + ' in ' + gridModel.name
            print_debug_information(functionName, text)

        # Parameter exist, but check if it is empty or not
        currentValues = np.zeros(nActiveCells, np.float32)
        p = gridModel.properties[parameterName]
        if not p.is_empty(realNumber):
            # Check if the parameter is to updated instead of being initialized to 0
            if not setInitialValues:
                currentValues = p.get_values(realNumber)

        # Assign values to the defined cells as specified in cellIndexDefined index vector
        # Using vector operations for numpy vector:
        if nDefinedCells > 0:
            for i in range(nDefinedCells):
                indx = cellIndexDefined[i]
                currentValues[indx] = float(inputValues[indx])
        else:
            currentValues = inputValues

        p.set_values(currentValues, realNumber)
        p.set_shared(isShared, realNumber)


def setDiscrete3DParameterValues(gridModel, parameterName, inputValues, zoneNumberList, codeNames,
                                 realNumber=0, isShared=True, debug_level=Debug.OFF):
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
           debug_level     - (value 0,1,2 or 3) and specify how much info is to be printed to screen.
           functionName  - Name of python function that call this function (Just for more informative print output).

    Output: True if 3D grid model exist and can be updated or
             not if the 3D grid does not exist or if a new facies code is introduced but the corresponding facies name already exits.
    """
    functionName = setDiscrete3DParameterValues.__name__
    # Check if specified grid model exists and is not empty
    if gridModel.is_empty():
        raise ValueError(
            'Specified grid model: {} is empty.'
            'Cannot create parameter: {} '
            ''.format(gridModel.name, parameterName)
        )
    # Check if specified parameter name exists and create new parameter if it does not exist.
    found = 0
    for p in gridModel.properties:
        if p.name == parameterName:
            found = 1
            break

    if found == 0:
        if debug_level >= Debug.VERY_VERBOSE:
            text = ' Create specified parameter: ' + parameterName + ' in ' + gridModel.name
            print_debug_information(functionName, text)
            if isShared:
                text = ' Set parameter to shared.'
                print_debug_information(functionName, text)
            else:
                text = ' Set parameter to non-shared.'
                print_debug_information(functionName, text)

        p = gridModel.properties.create(parameterName, roxar.GridPropertyType.discrete, np.uint16)
        currentValues = np.zeros(len(inputValues), np.uint16)
        currentValues = modifySelectedGridCells(gridModel, zoneNumberList, realNumber, currentValues, inputValues)
        p.set_values(currentValues, realNumber)
        p.set_shared(isShared, realNumber)
        p.code_names = codeNames
    else:
        if debug_level >= Debug.VERY_VERBOSE:
            text = ' Update specified parameter: ' + parameterName + ' in ' + gridModel.name
            print_debug_information(functionName, text)

        p = gridModel.properties[parameterName]
        if p.is_empty(realNumber):
            # Create parameter values (which are initialized to 0)
            grid3D = gridModel.get_grid(realNumber)
            v = np.zeros(grid3D.defined_cell_count, np.uint16)
            p.set_values(v, realNumber)

        # Get all active cell values
        p = get3DParameter(gridModel, parameterName, debug_level)
        if p.is_empty(realNumber):
            raise ValueError(
                'In function {0}.  Some inconsistency in program.'
                ''.format(functionName)
            )
        currentValues = p.get_values(realNumber)
        currentValues = modifySelectedGridCells(gridModel, zoneNumberList, realNumber, currentValues, inputValues)
        p.set_values(currentValues, realNumber)

        p.set_shared(isShared, realNumber)
        originalCodeNames = p.code_names.copy()

        codeValList = originalCodeNames.keys()
        for code in codeValList:
            if originalCodeNames[code] == '':
                print('Warning: There exists facies codes without facies names. Set facies name equal to facies code')
                originalCodeNames[code] = str(code)

        # Calculate updated facies table by combining the existing facies table for the 3D parameter
        # with facies table for the facies that are modelled for the updated zones
        print('originalCodeNames:')
        print(originalCodeNames)
        print('codeNames:')
        print(codeNames)
        updatedCodeNames, err = combineCodeNames(originalCodeNames, codeNames)
        if err == 1:
            text1 = ' Try to define a new facies code with a facies name that already is used define a new facies name\n'
            text2 = ' for a facies code that already exists when updating facies realisation\n'
            print_error(functionName, '\n' + text1 + text2)
            print('Original facies codes from RMS project: ')
            print(repr(originalCodeNames))
            print('New facies codes specified in current APS model: ')
            print(repr(codeNames))

            raise ValueError(
                'In function {}. Try to define a new facies code with a facies name that already is used.\n'
                'or define a new facies name for a facies code that already exists when updating facies realisation'
                ''.format(functionName)
            )

        # Update the facies table in the discrete 3D parameter
        p.code_names = updatedCodeNames
        if debug_level >= Debug.VERY_VERBOSE:
            text = 'Updated facies table: '
            print_debug_information(functionName, text)
            print(p.code_names)


def updateDiscrete3DParameterValues(
        gridModel, parameterName, inputValues, nDefinedCells=0, cellIndexDefined=None,
        faciesTable=None, realNumber=0, isShared=True, setDefaultFaciesNameWhenUndefined=True,
        setInitialValues=False, debug_level=Debug.OFF
):
    """
    Description:
    Set 3D parameter with discrete values for specified grid model. The input is specified for a subset of all grid cells.
    This subset is defined by the numpy vector cellIndexDefined and the number of values is nDefinedCells.
    Only the subset of cells will be updated. The input numpy vector inputValues has length equal to number of
    active grid cells for the grid model and contain the values to be assigned to the 3D parameter with
    name parameterName belonging to the grid model with name gridModel.
    If the grid parameter with name parameterName does not exist, it will be created and assigned value 0 in all
    cells except the cells defined by the cellIndexDefined where it will be assigned the values taken from
    the  inputValues vector. If the grid parameter exist, the grid cells with indices defined in cellIndexDefined will be
    updated with values from inputValues.
    :param setInitialValues:
    :param setDefaultFaciesNameWhenUndefined:
    :param faciesTable:
    :param gridModel:   Grid model object
    :param parameterName: Name of 3D parameter to update.
    :param inputValues:  A numpy array of length equal to nActiveCells where nActiveCells is the number of all grid cells in the
                         grid model that is not inactive and will therefore usually be a much longer vector than nDefinedCells.
                         Only the values in this vector corresponding to the selected cells defined by cellIndexDefined will be used.
                         The values are of type discrete.

    :param nDefinedCells: Length of the list cellIndexDefined
    :param cellIndexDefined: A list with cell indices in the array of all active cells for the grid model. The subset of cells
                             defined by this index array are the grid cells to be updated.
    :param codeNames: A dictionary with code names and code values for the discrete parameter values of the form as in the example:
                      {1: 'F1', 2: 'F2',3: 'F3'}.
                      NOTE: Be sure to input a codeNames dictionary containing all relevant facies for
                      for all zones, not only the zones that are updated by this function. If not, then
                      existing facies names and codes for zones that are not updated will be lost
                      from the facies table and need to be re-created manually or by script.
    :param realNumber: Realisation number counted from 0 for the 3D parameter.
    :param isShared:   Is set to true or false if the parameter is to be set to shared or non-shared.
    :param debug_level: Specify how much info is to be printed to screen. (0 - almost nothing output to screen, 3 - much output to screen)

    """
    functionName = updateDiscrete3DParameterValues.__name__
    if cellIndexDefined is not None:
        assert nDefinedCells == len(cellIndexDefined)
    grid3D = gridModel.get_grid(realNumber)
    nActiveCells = grid3D.defined_cell_count
    assert nActiveCells == len(inputValues)

    # Check if specified grid model exists and is not empty
    if gridModel.is_empty():
        raise ValueError(
            'Specified grid model: {} is empty.'
            'Cannot create parameter: {} '
            ''.format(gridModel.name, parameterName)
        )
    # Check if specified parameter name exists and create new parameter if it does not exist.
    found = 0
    for p in gridModel.properties:
        if p.name == parameterName:
            found = 1
            break

    if found == 0:
        if debug_level >= Debug.VERY_VERBOSE:
            text = ' Create specified parameter: ' + parameterName + ' in ' + gridModel.name
            print_debug_information(functionName, text)
            if isShared:
                text = ' Set parameter to shared.'
                print_debug_information(functionName, text)
            else:
                text = ' Set parameter to non-shared.'
                print_debug_information(functionName, text)

        # Create a new 3D parameter with the specified name
        p = gridModel.properties.create(parameterName, roxar.GridPropertyType.discrete, np.uint16)

        # Initialize the values to 0 for this new 3D parameter
        currentValues = np.zeros(nActiveCells, np.uint16)

        # Assign values to the defined cells as specified in cellIndexDefined index vector
        # Using vector operations for numpy vector:
        if nDefinedCells > 0:
            for i in range(nDefinedCells):
                indx = cellIndexDefined[i]
                currentValues[indx] = int(inputValues[indx])
        else:
            for i in range(len(inputValues)):
                currentValues[i] = int(inputValues[i])

        p.set_values(currentValues, realNumber)
        p.set_shared(isShared, realNumber)
        p.code_names = faciesTable
    else:
        if debug_level >= Debug.VERY_VERBOSE:
            text = ' Update specified parameter: ' + parameterName + ' in ' + gridModel.name
            print_debug_information(functionName, text)

        # Parameter exist, but check if it is empty or not
        # Initialize the values to 0
        currentValues = np.zeros(nActiveCells, np.uint16)
        p = gridModel.properties[parameterName]
        if not p.is_empty(realNumber):
            # Check if the parameter is to updated instead of being initialized to 0
            if not setInitialValues:
                # Keep the existing values for cells that is not updated
                currentValues = p.get_values(realNumber)
                if debug_level >= Debug.VERY_VERBOSE:
                    print('Debug output: Get values from existing 3D parameter: {}'.format(parameterName))

        # Assign values to the defined cells as specified in cellIndexDefined index vector
        if nDefinedCells > 0:
            for i in range(nDefinedCells):
                indx = cellIndexDefined[i]
                currentValues[indx] = int(inputValues[indx])
        else:
            for i in range(len(inputValues)):
                currentValues[i] = int(inputValues[i])

        p.set_values(currentValues, realNumber)
        p.set_shared(isShared, realNumber)

        originalCodeNames = p.code_names.copy()

        # Calculate updated facies table by combining the existing facies table for the 3D parameter
        # with facies table for the facies that are modelled for the updated zones
        updatedCodeNames, err = combineCodeNames(originalCodeNames, faciesTable)
        if err == 1:
            text1 = ' Try to define a new facies code with a facies name that already is used or define a new facies name\n'
            text2 = ' for a facies code that already exists when updating facies realisation\n'
            print_error(functionName, '\n' + text1 + text2)
            print('Original facies codes from RMS project: ')
            print(repr(originalCodeNames))
            print('New facies codes specified in current APS model: ')
            print(repr(faciesTable))

            raise ValueError(
                'In function {}. Try to define a new facies code with a facies name that already is used.\n'
                'or define a new facies name for a facies code that already exists when updating facies realisation'
                ''.format(functionName)
            )

        if setDefaultFaciesNameWhenUndefined:
            codeValList = updatedCodeNames.keys()
            for code in codeValList:
                if updatedCodeNames[code] == '':
                    print('Warning: There exists facies codes without facies names. Set facies name equal to facies code')
                    updatedCodeNames[code] = str(code)

        # Update the facies table in the discrete 3D parameter
        p.code_names = updatedCodeNames
        if debug_level >= Debug.VERY_VERBOSE:
            text = 'Updated facies table: '
            print_debug_information(functionName, text)
            print(p.code_names)


def createHorizonDataTypeObject(horizons, representationName, debug_level=Debug.OFF):
    # Check if horizon representation (horizon data type) exist
    # for specified type. If not, create a new representation
    reprObj = None
    for representation in horizons.representations:
        if representation.name == representationName:
            reprObj = representation
            break
    if reprObj is None:
        # Create new representation
        reprObj = horizons.representations.create(
            representationName, roxar.GeometryType.surface, roxar.VerticalDomain.depth
        )
        if debug_level >= Debug.VERY_VERBOSE:
            text = 'Debug ouput: Create new data type for horizon to be used '
            text += 'for variogram azimuth trend'
            print(text)

    return reprObj


def get2DMapDimensions(horizons, horizonName, representationName, debug_level=Debug.OFF):
    # Read information about 2D grid size,orientation and resolution
    # from existing 2D map.
    horizonObj = None
    for h in horizons:
        if h.name == horizonName:
            horizonObj = h
            break
    if horizonObj is None:
        raise ValueError(
            'Error in  get2DMapInfo\n'
            'Error: Horizon name: ' + horizonName + ' does not exist'
        )

    reprObj = None
    for representation in horizons.representations:
        if representation.name == representationName:
            reprObj = representation
            break
    if reprObj is None:
        raise ValueError(
            'Error in  get2DMapInfo\n'
            'Error: Horizons data type: ' + representationName + ' does not exist'
        )

    surface = horizons[horizonName][representationName]
    if not isinstance(surface, roxar.Surface):
        raise ValueError(
            'Error in get2DMapInfo\n'
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
    if debug_level >= Debug.VERY_VERBOSE:
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
                              debug_level=Debug.OFF, xmin=0, ymin=0, xinc=0, yinc=0, nx=0, ny=0, rotation=0):
    # This function will replace a horizon with specified name and type with a new one with value equal
    # to the constant value specified in variable inputValue. The 2D grid dimensions can also specified if new maps
    # must created.
    # Find horizon with specified name. Must exist.
    horizonObj = None
    for h in horizons:
        if h.name == horizonName:
            horizonObj = h
            break
    if horizonObj is None:
        raise ValueError(
            'Error in updateHorizonObject\n'
            'Error: Horizon name: ' + horizonName + ' does not exist'
        )

    # Find the correct representation. Must exist.
    reprObj = None
    for representation in horizons.representations:
        if representation.name == reprName:
            reprObj = representation
            break
    if reprObj is None:
        raise ValueError(
            'Error in updateHorizonObject\n'
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
            if debug_level >= Debug.VERY_VERBOSE:
                text = 'Debug output: ' + 'Create trend surface ' + reprName
                text += ' for variogram azimuth in ' + horizonName
                text += ' Value: ' + str(inputValue)
                print(text)

        if emptyGrid == 0:
            # Modify grid values
            values = grid.get_values()
            values[:] = inputValue
            grid.set_values(values)
            surfaceObj.set_grid(grid)
            if debug_level >= Debug.VERY_VERBOSE:
                text = 'Debug output: ' + 'Update trend surface ' + reprName
                text = text + ' for variogram azimuth in ' + horizonName
                text = text + ' Value: ' + str(inputValue)
                print(text)
