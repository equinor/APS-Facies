#!/bin/env python
import sys

import numpy as np
import importlib
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


def calcStatisticsFor3DParameter(
        gridModel, paramName, zoneNumberList, realNumber=0,
        debug_level=Debug.OFF
):
    """
    Calculates basic characteristics of property. Calculates the basric statistics of the Property object provided.
    TODO
    Input:
           property       - The Property object we wish to perform calculation on.

    :param gridModel: TODO: property!
    :param paramName: TODO: property!
    :param zoneNumberList:  List of zone numbers (counting from 0) for zones that
                            are included in the min, max, average calculation. Empty
                            list or list containing all zones will find
                            min, max, average over all zones
    :param realNumber: Realisation number counted from 0 for the parameter to get.
    :param debug_level: TODO
    :returns: tuple (minimum, maximum, average)
        WHERE
        float minimum is the minimum value
        float maximum is the maximum value
        float average is the average value
    """
    functionName = 'calcStatisticsFor3DParameter'
    values = getSelectedGridCells(gridModel, paramName, zoneNumberList, realNumber, debug_level)

    maximum = np.max(values)
    minimum = np.min(values)
    average = np.average(values)
    if debug_level >= Debug.VERY_VERBOSE:
        if len(zoneNumberList) > 0:
            text = ' Calculate min, max, average for parameter: ' + paramName + ' for selected zones '
            print_debug_information(functionName, text)
        else:
            text = ' Calculate min, max, average for parameter: ' + paramName
            print_debug_information(functionName, text)

        text = ' Min: ' + str(minimum) + '  Max: ' + str(maximum) + '  Average: ' + str(average)
        print_debug_information(functionName, text)

    return minimum, maximum, average


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
    # print('value: ' + str(values[indx]))
    average = sumValue / float(nDefinedCells)
    return average


def print_debug_information(function_name, text):
    if function_name in [' ', '']:
        print('Debug output: {text}\n'.format(text=text))
    else:
        print('Debug output in {function_name}: {text}\n'.format(function_name=function_name, text=text))


def print_error(function_name, text):
    print('Error in {function_name}: {text}'.format(function_name=function_name, text=text))


def raise_error(function_name, text):
    raise ValueError(
        'Error in {function_name}: {text}\n'
        'Error: Must exit from {function_name}'
        ''.format(function_name=function_name, text=text)
    )


def getCellValuesFilteredOnDiscreteParam(code, valueArray):
    """
    Calculate an index array to address all active (physical) cells in the
    grid corresponding to the cells with specified integer value (code).
    Is used to identify a subset of all grid cells that have grid cell values
    equal to the specified value in the input parameter code.
    Example of use of the output index list cellIndexDefined:
    indexIn3DParameterVector = cellIndexDefined[i]
    where i runs from 1 to nDefinedCells.
    Hence if valueArray is all active cell values for the zone parameter and code is a zoneNumber
    then the cellIndexDefined list will contain a list of all cell numbers for cells belonging
    to the specified zoneNumber.

    :param code: An integer value. The function search through the whole vector valueArray and find
                 all the values equal to code and save its cell index to cellIndexDefined.
    :param valueArray: A vector containing the 3D parameter values for the whole grid (all active cells).
    :returns: tuple (nDefinedCells, cellIndexDefined)
        WHERE
        int nDefinedCells is the number of cells found that match the value in the input variable code.
        list cellIndexDefined is a list of the cell indices where the valueArray value is equal to code.
    """
    cellIndexDefined = []
    nCellsTotal = len(valueArray)
    for i in range(nCellsTotal):
        if valueArray[i] == code:
            cellIndexDefined.append(i)
    nDefinedCells = len(cellIndexDefined)

    return nDefinedCells, cellIndexDefined


def isParameterDefinedWithValuesInRMS(gridModel, parameterName, realNumber):
    # Check if specified 3D parameter name is defined and has values
    found = False
    for p in gridModel.properties:
        if p.name == parameterName:
            found = True
            break
        
    if found:
        p =  gridModel.properties[parameterName]
        if not p.is_empty(realNumber):
            return True
    return False


def get3DParameter(gridModel, parameterName, realNumber=0, debug_level=Debug.OFF):
    """Get 3D parameter from grid model.
    Input:
           gridModel     - Grid model object
           parameterName - Name of 3D parameter to get.
           realNumber    - Realisation number counted from 0 for the parameter to get.
           debug_level     - (value 0,1,2 or 3) and specify how much info is to be printed to screen.
           functionName  - Name of python function that call this function (Just for more informative print output).

    Output: parameter object
    """
    functionName = 'get3DParameter'
    # Check if specified grid model exists and is not empty
    if gridModel.is_empty():
        text = 'Specified grid model: ' + gridModel.name + ' is empty.'
        raise_error(functionName, text)

    # Check if specified parameter name exists.
    found = 0
    for p in gridModel.properties:
        if p.name == parameterName:
            found = 1
            break

    if found == 0:
        text = ' Specified parameter: ' + parameterName + ' does not exist.'
        raise_error(functionName, text)

    param = gridModel.properties[parameterName]

    return param


def getContinuous3DParameterValues(gridModel, parameterName, realNumber=0, debug_level=Debug.SOMEWHAT_VERBOSE):
    """Get array of continuous values (numpy.float32) from active cells for specified 3D parameter from grid model.
    Input:
           gridModel     - grid model object
           parameterName - Name of 3D parameter to get.
           realNumber    - Realisation number counted from 0 for the parameter to get.
           debug_level     - (value 0,1,2 or 3) and specify how much info is to be printed to screen.
           functionName  - Name of python function that call this function (Just for more informative print output).

    Output: numpy array with values for each active grid cell for specified 3D parameter.
    """
    functionName = 'getContinuous3DParameterValues'
    param = get3DParameter(gridModel, parameterName, debug_level)
    if param.is_empty(realNumber):
        text = ' Specified parameter: ' + parameterName + ' is empty for realisation ' + str(realNumber)
        raise_error(functionName, text)

    activeCellValues = param.get_values(realNumber)
    return activeCellValues


def getDiscrete3DParameterValues(gridModel, parameterName, realNumber=0, debug_level=Debug.OFF):
    """Get array of discrete values (numpy.uint16) from active cells for specified 3D parameter from grid model.
    Input:
           gridModel     - Grid model object.
           parameterName - Name of 3D parameter to get.
           realNumber    - Realisation number counted from 0 for the parameter to get.
           debug_level     - (value 0,1,2 or 3) and specify how much info is to be printed to screen. (0 - almost nothing, 3 - also some debug info)
           functionName  - Name of python function that call this function (Just for more informative print output).

    Output: numpy array with values for each active grid cell for specified 3D parameter
            and a dictionary object with codeNames and values. If dictionary for code and facies names 
            has empty facies names, the facies name is set to the code value to avoid empty facies names.
    """
    functionName = 'getDiscrete3DParameterValues'
    param = get3DParameter(gridModel, parameterName, debug_level)
    if param.is_empty(realNumber):
        text = ' Specified parameter: ' + parameterName + ' is empty for realisation ' + str(realNumber)
        raise_error(functionName, text)

    activeCellValues = param.get_values(realNumber)
    codeNames = param.code_names

    codeValList = codeNames.keys()
    for code in codeValList:
        if codeNames[code] == '':
            codeNames[code] = str(code)

    return [activeCellValues, codeNames]


def getSelectedGridCells(gridModel, paramName, zoneNumberList, realNumber, debug_level=Debug.OFF):
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
    allValues = getContinuous3DParameterValues(gridModel, paramName, realNumber, debug_level)
    if len(zoneNumberList) > 0:
        # Get values for the specified zones
        grid3D = gridModel.get_grid(realNumber)
        indexer = grid3D.simbox_indexer
        dimI, dimJ, dimK = indexer.dimensions
        nCellsSelected = 0
        values = []
        for zoneIndx in indexer.zonation:
            if zoneIndx in zoneNumberList:
                layerRanges = indexer.zonation[zoneIndx]
                for lr in layerRanges:
                    # Get all the cell numbers for the layer range
                    cellNumbers = indexer.get_cell_numbers_in_range((0, 0, lr.start), (dimI, dimJ, lr.stop))

                    # Set values for all cells in this layer
                    nCellsSelected += len(cellNumbers)
                    for cIndx in cellNumbers:
                        values.append(allValues[cIndx])
        values = np.asarray(values)
        return values
    else:
        return allValues


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
    return oldValues


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

    functionName = 'setContinuous3DParameterValues'
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

def updateContinuous3DParameterValues(gridModel, parameterName, inputValues, nDefinedCells=0, cellIndexDefined=None,
                                      realNumber=0, isShared=True, setInitialValues=False, debug_level=Debug.SOMEWHAT_VERBOSE):
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

    functionName = 'updateContinuous3DParameterValues'
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


                if len(v) > 0:
                    # Check if the facies name is equal to the code
                    # then it can be overwritten by the new one.
                    if v == str(code):
                        originalCodeNames[code] = u
                    else:
                        # The code has different names in the existing original and the new codeNames dictionary
                        error = 1
                        break
                else:
                    # The facies name is empty string, assign a name from the new to it
                    originalCodeNames[code] = u

    return originalCodeNames, error


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
    functionName = 'setDiscrete3DParameterValues'
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

def updateDiscrete3DParameterValues(gridModel, parameterName, inputValues, nDefinedCells=0, cellIndexDefined=None,
                                    faciesTable=None, realNumber=0, isShared=True, 
                                    setDefaultFaciesNameWhenUndefined=True, setInitialValues=False, debug_level=Debug.SOMEWHAT_VERBOSE):
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
    functionName = 'updateDiscrete3DParameterValues'
    if cellIndexDefined is not None:
        assert nDefinedCells == len(cellIndexDefined)
    if debug_level >= Debug.VERY_VERBOSE:
        print('Debug output: nDefinedCells input: {}'.format(str(nDefinedCells)))
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
                    print(repr(currentValues))

            
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
        [updatedCodeNames, err] = combineCodeNames(originalCodeNames, faciesTable)
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


def getNumberOfLayersPerZone(grid, zoneNumber):
    indexer = grid.grid_indexer
    zone_name = grid.zone_names[zoneNumber]
    layer_ranges = indexer.zonation[zoneNumber]
    number_layers = 0
    for layer_range in layer_ranges:
        start = layer_range[0]
        end = layer_range[-1]
        number_layers += (end + 1 - start)
    return number_layers


def getNumberOfLayers(grid):
    indexer = grid.grid_indexer
    number_layers_per_zone = []
    for key in indexer.zonation:
        zone_name = grid.zone_names[key]
        layer_ranges = indexer.zonation[key]
        number_layers = 0
        for layer_range in layer_ranges:
            start = layer_range[0]
            end = layer_range[-1]
            number_layers += (end + 1 - start)
        number_layers_per_zone.append(number_layers)
    return number_layers_per_zone


def getGridAttributes(grid, debug_level=Debug.OFF):
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

    if debug_level >= Debug.VERY_VERBOSE:
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

    if debug_level >= Debug.VERY_VERBOSE:
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
    nLayersPerZone = []
    nLayersPerZone = getNumberOfLayers(grid)
    simBoxXLength, simBoxYLength, azimuthAngle, x0, y0 = getGridSimBoxSize(grid, debug_level)
    return (
        xmin, xmax, ymin, ymax, zmin, zmax, simBoxXLength, simBoxYLength, azimuthAngle, x0, y0,
        dimensions[0], dimensions[1], dimensions[2], nZones, zoneNames, nLayersPerZone
    )


def getGridSimBoxSize(grid, debug_level=Debug.OFF):
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
    azimuthAngle = np.arctan(sinTheta / cosTheta)
    azimuthAngle = azimuthAngle * 180.0 / np.pi
    if debug_level >= Debug.VERY_VERBOSE:
        print('Debug output: Length in x direction:  ' + str(simBoxXLength))
        print('Debug output: Length in y direction:  ' + str(simBoxYLength))
        print('Debug output: Sim box rotation angle: ' + str(azimuthAngle))
    return simBoxXLength, simBoxYLength, azimuthAngle, x0, y0


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
        reprObj = horizons.representations.create(representationName,
                                                  roxar.GeometryType.surface,
                                                  roxar.VerticalDomain.depth)
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
    return nx, ny, xinc, yinc, xmin, ymin, xmax, ymax, rotation


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
    return
