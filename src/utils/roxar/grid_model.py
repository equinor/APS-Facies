# -*- coding: utf-8 -*-
import numpy as np

from src.utils.constants.simple import Debug
from src.utils.exceptions.general import raise_error
from src.utils.io import print_debug_information

from roxar import GridPropertyType


def calcStatisticsFor3DParameter(grid_model, parameter_name, zone_number_list, realization_number=0, debug_level=Debug.OFF):
    """
    Calculates basic characteristics of property. Calculates the basric statistics of the Property object provided.
    TODO
    Input:
           property       - The Property object we wish to perform calculation on.

    :param grid_model: TODO: property!
    :param parameter_name: TODO: property!
    :param zone_number_list:  List of zone numbers (counting from 0) for zones that
                            are included in the min, max, average calculation. Empty
                            list or list containing all zones will find
                            min, max, average over all zones
    :param realization_number: Realisation number counted from 0 for the parameter to get.
    :param debug_level: TODO
    :returns: tuple (minimum, maximum, average)
        WHERE
        float minimum is the minimum value
        float maximum is the maximum value
        float average is the average value
    """
    function_name = calcStatisticsFor3DParameter.__name__
    values = getSelectedGridCells(grid_model, parameter_name, zone_number_list, realization_number, debug_level)

    maximum = np.max(values)
    minimum = np.min(values)
    average = np.average(values)
    if debug_level >= Debug.VERY_VERBOSE:
        if len(zone_number_list) > 0:
            text = ' Calculate min, max, average for parameter: ' + parameter_name + ' for selected zones '
            print_debug_information(function_name, text)
        else:
            text = ' Calculate min, max, average for parameter: ' + parameter_name
            print_debug_information(function_name, text)

        text = ' Min: ' + str(minimum) + '  Max: ' + str(maximum) + '  Average: ' + str(average)
        print_debug_information(function_name, text)

    return minimum, maximum, average


def get3DParameter(grid_model, parameter_name):
    """Get 3D parameter from grid model.
    Input:
           grid_model     - Grid model object
           parameter_name - Name of 3D parameter to get.
           function_name  - Name of python function that call this function (Just for more informative print output).

    Output: parameter object
    """
    # Check if specified grid model exists and is not empty
    if grid_model.is_empty():
        raise ValueError("Expected non-empty grid model, but was empty. (Grid Model: '{}')".format(grid_model.name))

    # Check if specified parameter name exists.
    if parameter_name not in grid_model.properties:
        raise ValueError(
            "The parameter '{}' was expected in grid model '{}', but does not exist."
            "".format(parameter_name, grid_model.name)
        )

    return grid_model.properties[parameter_name]


def getContinuous3DParameterValues(grid_model, parameter_name, realization_number=0, debug_level=Debug.OFF):
    """Get array of continuous values (numpy.float32) from active cells for specified 3D parameter from grid model.
    Input:
           grid_model     - grid model object
           parameter_name - Name of 3D parameter to get.
           realization_number    - Realisation number counted from 0 for the parameter to get.
           debug_level     - (value 0,1,2 or 3) and specify how much info is to be printed to screen.
           function_name  - Name of python function that call this function (Just for more informative print output).

    Output: numpy array with values for each active grid cell for specified 3D parameter.
    """
    function_name = getContinuous3DParameterValues.__name__
    param = get3DParameter(grid_model, parameter_name)
    if param.is_empty(realization_number):
        text = ' Specified parameter: ' + parameter_name + ' is empty for realisation ' + str(realization_number)
        raise_error(function_name, text)

    active_cell_values = param.get_values(realization_number)
    return active_cell_values


def getSelectedGridCells(grid_model, parameter_name, zone_number_list, realization_number, debug_level=Debug.OFF):
    """
    Input:
           grid_model     - Grid model object
           parameterName - Name of 3D parameter to get.

           zone_number_list - A list of integer values that are zone numbers (counted from 0). If the list is empty or has all zones
                            included in the list, then grid cells in all zones are updated.
           realization_number    - Realisation number counted from 0 for the parameter to get.
    Output:
           Numpy vector with parameter values for the active cells belonging to the specified zones. Note that the output
           is in general not of the same length as a vector with all active cells.
    """
    all_values = getContinuous3DParameterValues(grid_model, parameter_name, realization_number, debug_level)
    if len(zone_number_list) > 0:
        # Get values for the specified zones
        grid = grid_model.get_grid(realization_number)
        indexer = grid.simbox_indexer
        dim_i, dim_j, dim_k = indexer.dimensions
        num_cells_selected = 0
        values = []
        for zone_index in indexer.zonation:
            if zone_index in zone_number_list:
                layer_ranges = indexer.zonation[zone_index]
                for lr in layer_ranges:
                    # Get all the cell numbers for the layer range
                    cell_numbers = indexer.get_cell_numbers_in_range((0, 0, lr.start), (dim_i, dim_j, lr.stop))

                    # Set values for all cells in this layer
                    num_cells_selected += len(cell_numbers)
                    for cIndx in cell_numbers:
                        values.append(all_values[cIndx])
        values = np.asarray(values)
        return values
    else:
        return all_values


def getCellValuesFilteredOnDiscreteParam(code, value_array):
    """
    Calculate an index array to address all active (physical) cells in the
    grid corresponding to the cells with specified integer value (code).
    Is used to identify a subset of all grid cells that have grid cell values
    equal to the specified value in the input parameter code.
    Example of use of the output index list cell_index_defined:
    indexIn3DParameterVector = cell_index_defined[i]
    where i runs from 1 to num_defined_cells.
    Hence if valueArray is all active cell values for the zone parameter and code is a zoneNumber
    then the cell_index_defined list will contain a list of all cell numbers for cells belonging
    to the specified zoneNumber.

    :param code: An integer value. The function search through the whole vector valueArray and find
                 all the values equal to code and save its cell index to cell_index_defined.
    :param value_array: A vector containing the 3D parameter values for the whole grid (all active cells).
    :returns: tuple (num_defined_cells, cell_index_defined)
        WHERE
        int num_defined_cells is the number of cells found that match the value in the input variable code.
        list cell_index_defined is a list of the cell indices where the valueArray value is equal to code.
    """
    cell_index_defined = []
    num_cells_total = len(value_array)
    for i in range(num_cells_total):
        if value_array[i] == code:
            cell_index_defined.append(i)
    num_defined_cells = len(cell_index_defined)

    return num_defined_cells, cell_index_defined


def isParameterDefinedWithValuesInRMS(grid_model, parameter_name, realization_number):
    # Check if specified 3D parameter name is defined and has values
    found = False
    for p in grid_model.properties:
        if p.name == parameter_name:
            found = True
            break

    if found:
        p = grid_model.properties[parameter_name]
        if not p.is_empty(realization_number):
            return True
    return False


def getDiscrete3DParameterValues(grid_model, parameter_name, realization_number=0, debug_level=Debug.OFF):
    """Get array of discrete values (numpy.uint16) from active cells for specified 3D parameter from grid model.
    Input:
           grid_model     - Grid model object.
           parameter_name - Name of 3D parameter to get.
           realization_number    - Realisation number counted from 0 for the parameter to get.
           debug_level     - (value 0,1,2 or 3) and specify how much info is to be printed to screen. (0 - almost nothing, 3 - also some debug info)
           function_name  - Name of python function that call this function (Just for more informative print output).

    Output: numpy array with values for each active grid cell for specified 3D parameter
            and a dictionary object with code_names and values. If dictionary for code and facies names
            has empty facies names, the facies name is set to the code value to avoid empty facies names.
    """
    function_name = getDiscrete3DParameterValues.__name__
    param = get3DParameter(grid_model, parameter_name)
    # Check that parameter is defined and not empty
    if param.is_empty(realization_number):
        text = ' Specified parameter: ' + parameter_name + ' is empty for realisation ' + str(realization_number)
        raise_error(function_name, text)
    # Check that parameter_name refer to a discrete parameter
    if param.type is not GridPropertyType.discrete:
        text = ' Specified parameter: ' + parameter_name + ' is not a discrete parameter'
        raise_error(function_name, text)
    active_cell_values = param.get_values(realization_number)
    code_names = param.code_names
    code_val_list = code_names.keys()
    for code in code_val_list:
        if code_names[code] == '':
            code_names[code] = str(code)

    return active_cell_values, code_names


def modifySelectedGridCells(grid_model, zone_number_list, realization_number, old_values, new_values):
    # Is used to set new values in existing 3D parameter
    # for selected cells defined by a list of zone numbers
    grid = grid_model.get_grid(realization_number)
    indexer = grid.simbox_indexer
    dim_i, dim_j, dim_k = indexer.dimensions
    for zone_index in indexer.zonation:
        if zone_index in zone_number_list:
            layer_ranges = indexer.zonation[zone_index]
            for lr in layer_ranges:
                # Get all the cell numbers for the layer range
                cell_numbers = indexer.get_cell_numbers_in_range((0, 0, lr.start), (dim_i, dim_j, lr.stop))
                # Set values for all cells in this layer
                old_values[cell_numbers] = new_values[cell_numbers]
    return old_values


def update_code_names(old_code_names, new_code_names):
    code_val_list = new_code_names.keys()
    for code in code_val_list:
        if code not in old_code_names:
            # New code
            u = new_code_names.get(code)
            for k in old_code_names:
                v = old_code_names.get(k)
                if u == v:
                    # The facies name for this code already exist
                    raise ValueError('The facies name "{}" already exists for facies code{}'.format(u, code))

            item = {code: u}
            old_code_names.update(item)
        else:
            # not a new code
            u = new_code_names.get(code)
            v = old_code_names.get(code)
            if u != v:
                if len(v) > 0:
                    # Check if the facies name is equal to the code
                    # then it can be overwritten by the new one.
                    if v == str(code):
                        old_code_names[code] = u
                    else:
                        # The code has different names in the existing original and the new code_names dictionary
                        raise ValueError(
                            'The facies code {code} has a different name in the new and original'
                            ' ({old_name}, and {new_name} respectively)'
                            ''.format(code=code, old_name=v, new_name=u)
                        )
                else:
                    # The facies name is empty string, assign a name from the new to it
                    old_code_names[code] = u


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
    sim_box_x_length = np.sqrt((x1 - x0) * (x1 - x0) + (y1 - y0) * (y1 - y0))
    sim_box_y_length = np.sqrt((x2 - x0) * (x2 - x0) + (y2 - y0) * (y2 - y0))
    cos_theta = (y2 - y0) / sim_box_y_length
    sin_theta = (x2 - x0) / sim_box_y_length
    azimuth_angle = np.arctan(sin_theta / cos_theta)
    azimuth_angle *= 180.0 / np.pi
    if debug_level >= Debug.VERY_VERBOSE:
        print('Debug output: Length in x direction:  ' + str(sim_box_x_length))
        print('Debug output: Length in y direction:  ' + str(sim_box_y_length))
        print('Debug output: Sim box rotation angle: ' + str(azimuth_angle))
    return sim_box_x_length, sim_box_y_length, azimuth_angle, x0, y0


def getNumberOfLayersPerZone(grid, zone_number):
    indexer = grid.grid_indexer
    layer_ranges = indexer.zonation[zone_number]
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
        layer_ranges = indexer.zonation[key]
        number_layers = 0
        for layer_range in layer_ranges:
            start = layer_range[0]
            end = layer_range[-1]
            number_layers += (end + 1 - start)
        number_layers_per_zone.append(number_layers)
    return number_layers_per_zone


def getZoneLayerNumbering(grid_model, realization_number=0):
    grid = grid_model.get_grid(realization_number)
    indexer = grid.simbox_indexer
    number_layers_per_zone = []
    start_layers_per_zone = []
    end_layers_per_zone = []
    for key in indexer.zonation:
        layer_ranges = indexer.zonation[key]
        number_layers = 0
        # sim box indexer should not have repeated layer numbering
        assert(len(layer_ranges) == 1)
        layer_range = layer_ranges[0]
        start = layer_range[0]
        end = layer_range[-1]
        number_layers += (end + 1 - start)
        number_layers_per_zone.append(number_layers)
        start_layers_per_zone.append(start)
        end_layers_per_zone.append(end)
    return [number_layers_per_zone, start_layers_per_zone, end_layers_per_zone]


def getGridAttributes(grid, debug_level=Debug.OFF):
    indexer = grid.simbox_indexer
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
    zone_names = []
    for i, zone_index in enumerate(indexer.zonation.keys(), start=1):
        zone_name = grid.zone_names[zone_index]
        zone_names.append(zone_name)

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
    zone_names = []
    start_layer_per_zone = []
    end_layer_per_zone = []
    num_layers_per_zone = []
    for i, zone_index in enumerate(indexer.zonation.keys(), start=1):
        zone_name = grid.zone_names[zone_index]
        zone_names.append(zone_name)
        # Only one interval of layers per zone for grid layers in sim box
        assert len(indexer.zonation[zone_index]) == 1
        layer_range = indexer.zonation[zone_index]
        current_range = layer_range[0]
        start = current_range[0]
        end = current_range[-1]
        start_layer_per_zone.append(start)
        end_layer_per_zone.append(end)
        num_layers_in_zone = (end + 1 - start)
        num_layers_per_zone.append(num_layers_in_zone)
        # Indexes start with 0, so add 1 to give user-friendly output
        if debug_level >= Debug.VERY_VERBOSE:
            layers_text = "{}-{} ".format(str(start + 1), str(end + 1))
            print('Zone{}: "{}", Layers {} ({} layers)\n'.format(i, zone_name, layers_text, num_layers_in_zone))
    num_zones = len(indexer.zonation)
    sim_box_x_length, sim_box_y_length, azimuth_angle, x0, y0 = getGridSimBoxSize(grid, debug_level)
    return (
        xmin, xmax, ymin, ymax, zmin, zmax, sim_box_x_length, sim_box_y_length, azimuth_angle, x0, y0,
        dimensions[0], dimensions[1], dimensions[2], num_zones, zone_names, num_layers_per_zone, start_layer_per_zone,
        end_layer_per_zone
    )
