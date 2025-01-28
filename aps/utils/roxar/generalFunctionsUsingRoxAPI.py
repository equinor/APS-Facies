#!/bin/env python
# -*- coding: utf-8 -*-
import sys
from pathlib import Path

import numpy as np
from warnings import warn

from aps.utils.exceptions.general import raise_error
from aps.utils.io import print_debug_information, print_error
from aps.utils.roxar.grid_model import (
    get3DParameter,
    modify_selected_grid_cells,
    update_code_names,
)
from aps.utils.constants.simple import Debug

import roxar
from roxar import Direction


def get_grid_dimension(project, name):
    grid = project.grid_models[name].get_grid(project.current_realisation)
    return grid.grid_indexer.dimensions


def get_project_realization_seed(project=None):
    external_seed = Path('./RMS_SEED_USED')
    if external_seed.exists():
        # For use in ERT, when the project seed is not set
        with open(external_seed, encoding='utf-8') as f:
            content = ''.join(f.readlines()).strip()
        seed = int(content.split()[-1])
        return seed
    if project is None:
        raise TypeError(f"'project' is required when {external_seed} does not exist")
    return project.seed + project.current_realisation + 1


def get_project_dir(project):
    return Path(project.filename).parent.absolute()


def set_continuous_3d_parameter_values(
    grid_model,
    parameter_name,
    input_values,
    zone_numbers=None,
    realisation_number=0,
    is_shared=False,
    debug_level=Debug.OFF,
):
    """Set 3D parameter with values for specified grid model.
    Input:
           grid_model     - Grid model object
           parameter_name - Name of 3D parameter to get.
           input_values    - A numpy array of length equal to the number of active cells and with continuous values.
                           Only the grid cells belonging to the specified zones are updated even though the values array
                           contain values for all active cells.
           zone_numbers - A list of integer values that are zone numbers (counted from 0).
                            If the list is empty or has all zones included in the list,
                            then grid cells in all zones are updated.
           realisation_number    - Realisation number counted from 0 for the parameter to get.
           is_shared      - Is set to true or false if the parameter is to be set to shared or non-shared.
           debug_level     - (value 0,1,2 or 3) and specify how much info is to be printed to screen.
                           (0 - almost nothing, 3 - also some debug info)
           function_name  - Name of python function that call this function (Just for more informative print output).

    Output: True if 3D grid model exist and can be updated, False if not.
    """

    function_name = set_continuous_3d_parameter_values.__name__
    # Check if specified grid model exists and is not empty
    if grid_model.is_empty(realisation_number):
        print(
            f'Specified grid model: {grid_model.name} is empty for realisation {realisation_number + 1}.'
        )
        return False

    # Check if specified parameter name exists and create new parameter if it does not exist.

    if parameter_name not in grid_model.properties:
        if debug_level >= Debug.VERY_VERBOSE:
            print(f'--- Create specified RMS parameter: {parameter_name}')
            if is_shared:
                print('--- Set parameter to shared.')
            else:
                print('--- Set parameter to non-shared.')

        _create_property(
            grid_model,
            input_values,
            parameter_name,
            zone_numbers,
            is_shared,
            realisation_number,
        )
    else:
        if debug_level >= Debug.VERY_VERBOSE:
            print(f'--- Update specified RMS parameter: {parameter_name}')

        # Parameter exist, but check if it is empty or not
        p = grid_model.properties[parameter_name]
        if p.is_empty(realisation_number):
            # Create parameter values (which are initialized to 0)
            grid = grid_model.get_grid(realisation_number)
            v = np.zeros(grid.defined_cell_count, np.float32)
            p.set_values(v, realisation_number)

        # Get all active cell values
        p = get3DParameter(grid_model, parameter_name, realisation_number)
        if p.is_empty(realisation_number):
            raise_error(
                function_name,
                f' Specified parameter: {parameter_name} is empty for realisation {realisation_number + 1}',
            )

        current_values = p.get_values(realisation_number)
        current_values = modify_selected_grid_cells(
            grid_model, zone_numbers, realisation_number, current_values, input_values
        )
        p.set_values(current_values, realisation_number)

    return True


def set_continuous_3d_parameter_values_in_zone(
    grid_model,
    parameter_names,
    input_values_for_zones,
    zone_number,
    realisation_number=0,
    is_shared=False,
    debug_level=Debug.OFF,
):
    """Set 3D parameter with values for specified grid model for specified zone (and region)
    Input:
           grid_model     - Grid model object
           parameter_names - List of names of 3D parameter to update.
           input_values_for_zones  - A list of numpy 3D arrays. They corresponds to the parameter names in parameter_names.
                                     The size of the numpy input arrays are (nx,ny,nLayers) where nx, ny must match
                                     the gridModels 3D grid size for the simulation box grid and nLayers must match
                                     the number of layers for the zone in simulationx box. Note that since nx, ny
                                     are the simulation box grid size, they can be larger than the number of cells
                                     reported for the grid in reverse faulted grids. The grid values must be of type
                                     numpy.float32. Only the grid cells belonging to the specified zone are updated,
                                     and error is raised if the number of grid cells for the zone doesn't match
                                     the size of the input array.
           zoneNumber    - The zone number (counted from 0 in the input)
           realisation_number    - Realisation number counted from 0 for the parameter to get.
           is_shared      - Is set to true or false if the parameter is to be set to shared or non-shared.
           debug_level   - (value 0,1,2 or 3) and specify how much info is to be printed to screen.
                           (0 - almost nothing, 3 - also some debug info)
    """

    # Check if specified grid model exists and is not empty
    if grid_model.is_empty(realisation_number):
        print(
            f'Specified grid model: {grid_model.name} is empty for realisation {realisation_number + 1}.'
        )
        return False

    # Check if the parameter is defined and create new if not existing
    grid = grid_model.get_grid(realisation_number)

    # Find grid layers for the zone
    indexer = grid.simbox_indexer
    zonation = indexer.zonation
    layer_ranges = zonation[zone_number]
    nx, ny, nz = indexer.dimensions
    start_layer = nz
    end_layer = 0
    for layer_range in layer_ranges:
        for layer in layer_range:
            if start_layer > layer:
                start_layer = layer
            if end_layer < layer:
                end_layer = layer
    end_layer = end_layer + 1
    start = (0, 0, start_layer)
    end = (nx, ny, end_layer)
    zone_cell_numbers = indexer.get_cell_numbers_in_range(start, end)

    num_layers = end_layer - start_layer
    # All input data vectors are from the same zone and has the same size
    [nx_in, ny_in, nz_in] = input_values_for_zones[0].shape
    if nx != nz_in or ny != ny_in or num_layers != nz_in:
        raise IOError(
            'Input array with values has different dimensions than the grid model:\n'
            f'Grid model nx: {nx}  Input array nx: {nx_in}\n'
            f'Grid model ny: {ny}  Input array ny: {ny_in}\n'
            f'Grid model nLayers for zone {zone_number} is: {num_layers}    Input array nz: {nz_in}'
        )

    defined_cell_indices = indexer.get_indices(zone_cell_numbers)
    i_indices = defined_cell_indices[:, 0]
    j_indices = defined_cell_indices[:, 1]
    k_indices = defined_cell_indices[:, 2]

    # Loop over all parameter names
    for parameter_index in range(len(parameter_names)):
        parameter_name = parameter_names[parameter_index]
        input_values_for_zone = input_values_for_zones[parameter_index]

        if parameter_name in grid_model.properties:
            property_param = grid_model.properties[parameter_name]
        else:
            # Create new parameter
            property_param = grid_model.properties.create(
                parameter_name, roxar.GridPropertyType.continuous, np.float32
            )
            property_param.set_shared(is_shared, realisation_number)
            if debug_level >= Debug.VERY_VERBOSE:
                print(f'--- Create specified RMS parameter: {parameter_name}')
                if is_shared:
                    print('--- Set parameter to shared.')
                else:
                    print('--- Set parameter to non-shared.')

        assert property_param is not None
        if property_param.is_empty(realisation_number):
            # Initialize to 0 if empty
            #  v = np.zeros(grid3D.defined_cell_count, np.float32)
            v = grid.generate_values(np.float32)
            property_param.set_values(v, realisation_number)

        # Get current values
        current_values = property_param.get_values(realisation_number)

        # Create 3D array for all cells in the grid including inactive cells
        new_values = np.zeros((nx, ny, nz), dtype=float, order='F')

        # Assign values from input array into the 3D grid array
        # Note that input array is of dimension (nx,ny,nLayers)
        # where nLayers is the number of layers of the input grid
        # These layers must correspond to layer from start_layer untill but not including end_layer
        # in the full 3D grid

        for k in range(start_layer, end_layer):
            new_values[:, :, k] = input_values_for_zone[:, :, k - start_layer]

        # Since the cell numbers and the indices all are based on the same range,
        # it is possible to use numpy vectorization to copy
        current_values[zone_cell_numbers] = new_values[i_indices, j_indices, k_indices]
        property_param.set_values(current_values, realisation_number)

    return True


def define_active_cell_indices(
    indexer,
    cell_numbers,
    ijk_handedness,
    use_left_handed_grid_indexing,
    grid_model_name,
    debug_level,
    switch_handedness_for_parameters=False,
):
    _, ny, _ = indexer.dimensions
    defined_cell_indices = indexer.get_indices(cell_numbers)
    switch_handedness = switch_handedness_for_parameters
    if (ijk_handedness == Direction.right) and use_left_handed_grid_indexing:
        switch_handedness = True
    if switch_handedness:
        if debug_level >= Debug.VERY_VERBOSE:
            print(
                f'-- Grid handedness for {grid_model_name} : {ijk_handedness}.  Switch handedness.'
            )
        i_indices = defined_cell_indices[:, 0]
        j_indices = -defined_cell_indices[:, 1] + ny - 1
    else:
        i_indices = defined_cell_indices[:, 0]
        j_indices = defined_cell_indices[:, 1]
    k_indices = defined_cell_indices[:, 2]
    return i_indices, j_indices, k_indices


def set_continuous_3d_parameter_values_in_zone_region(
    grid_model,
    parameter_names,
    input_values_for_zones,
    zone_number,
    region_number=0,
    region_parameter_name=None,
    realisation_number=0,
    is_shared=False,
    debug_level=Debug.OFF,
    fmu_mode=False,
    use_left_handed_grid_indexing=False,
    switch_handedness=False,
):
    """Set 3D parameter with values for specified grid model for specified zone (and region)
    Input:
           grid_model     - Grid model object
           parameter_names - List of names of 3D parameter to update.
           input_values_for_zones  - A list of numpy 3D arrays.
                                     They corresponds to the parameter names in parameter_names.
                                     The size of the numpy input arrays are (nx,ny,nLayers) where nx, ny must match
                                     the gridModels 3D grid size for the simulation box grid and nLayers must match
                                     the number of layers for the zone in simulationx box. Note that since nx, ny
                                     are the simulation box grid size, they can be larger than the number of cells
                                     reported for the grid in reverse faulted grids. The grid values must be of type
                                     numpy.float32. Only the grid cells belonging to the specified zone are updated,
                                     and error is raised if the number of grid cells for the zone doesn't match
                                     the size of the input array.
           zone_number    - The zone number (counted from 1 in the input)
           regionNumber  - The region number for the grid cells to be updated.
           region_parameter_name - The name of the 3D grid parameter containing a discrete 3D parameter with region numbers
           realisation_number    - Realisation number counted from 0 for the parameter to get.
           is_shared      - Is set to true or false if the parameter is to be set to shared or non-shared.
           debug_level   - (value 0,1,2 or 3) and specify how much info is to be printed to screen.
                           (0 - almost nothing, 3 - also some debug info)
    """

    function_name = set_continuous_3d_parameter_values_in_zone_region.__name__
    # Check if specified grid model exists and is not empty
    if grid_model.is_empty(realisation_number):
        print(
            f'Specified grid model: {grid_model.name} is empty for realisation {realisation_number + 1}'
        )
        return False

    # Check if the parameter is defined and create new if not existing
    grid = grid_model.get_grid(realisation_number)

    # Find grid layers for the zone
    indexer = grid.simbox_indexer
    try:
        ijk_handedness = indexer.ijk_handedness
    except AttributeError:
        ijk_handedness = indexer.handedness

    nx, ny, nz = indexer.dimensions
    end_layer, start_layer = get_layer_range(indexer, zone_number, fmu_mode)
    start = (0, 0, start_layer)
    end = (nx, ny, end_layer)
    zone_cell_numbers = indexer.get_cell_numbers_in_range(start, end)

    num_layers = end_layer - start_layer
    # All input data vectors are from the same zone and has the same size
    nx_in, ny_in, nz_in = input_values_for_zones[0].shape
    if nx != nx_in or ny != ny_in or num_layers > nz_in:
        raise IOError(
            'Input array with values has different dimensions than the grid model:\n'
            f'Grid model nx: {nx}  Input array nx: {nx_in}\n'
            f'Grid model ny: {ny}  Input array ny: {ny_in}\n'
            f'Grid model nLayers for zone {zone_number} is: {num_layers}    Input array nz: {nz_in}'
        )
    use_regions = False
    if region_parameter_name is None or len(region_parameter_name) == 0 or fmu_mode:
        i_indices, j_indices, k_indices = define_active_cell_indices(
            indexer,
            zone_cell_numbers,
            ijk_handedness,
            use_left_handed_grid_indexing,
            grid_model.name,
            debug_level,
            switch_handedness,
        )

    else:
        # Get region parameter values
        region_param_values = None
        zone_region_cell_numbers = None
        if region_parameter_name in grid_model.properties:
            p = grid_model.properties[region_parameter_name]
            if not p.is_empty(realisation_number):
                region_param_values = p.get_values(realisation_number)
        else:
            raise ValueError(
                f'Parameter {region_parameter_name} does not exist or is empty in grid model {grid_model.name}.'
            )
        region_param_values_in_zone = region_param_values[zone_cell_numbers]
        zone_region_cell_numbers = zone_cell_numbers[
            region_param_values_in_zone == region_number
        ]
        i_indices, j_indices, k_indices = define_active_cell_indices(
            indexer,
            zone_region_cell_numbers,
            ijk_handedness,
            use_left_handed_grid_indexing,
            grid_model.name,
            debug_level,
            switch_handedness,
        )
        use_regions = True

    # Loop over all parameter names
    for param_index in range(len(parameter_names)):
        parameter_name = parameter_names[param_index]
        input_values_for_zone = input_values_for_zones[param_index]
        if parameter_name in grid_model.properties:
            property_param = grid_model.properties[parameter_name]
        else:
            # Create new parameter
            property_param = grid_model.properties.create(
                parameter_name, roxar.GridPropertyType.continuous, np.float32
            )
            property_param.set_shared(is_shared, realisation_number)
            if debug_level >= Debug.VERY_VERBOSE:
                print(f'--- Create specified RMS parameter: {parameter_name}')
                if is_shared:
                    print('--- Set parameter to shared.')
                else:
                    print('--- Set parameter to non-shared.')

        assert property_param is not None
        if property_param.is_empty(realisation_number):
            # Initialize to 0 if empty
            v = grid.generate_values(np.float32)
            property_param.set_values(v, realisation_number)

        # Get current values
        current_values = property_param.get_values(realisation_number)

        # Assign values from input array into the 3D grid array
        # Note that input array is of dimension (nx,ny,nLayers)
        # where nLayers is the number of layers of the input grid
        # These layers must correspond to layer from start_layer until but not including end_layer
        # in the full 3D grid.

        # Create a 3D array for all cells in the grid including inactive cells
        # Since the cell numbers, and the indices all are based on the same range,
        # it is possible to use numpy vectorization to copy
        new_values = np.zeros((nx, ny, nz), dtype=float, order='F')
        for k in range(start_layer, end_layer):
            new_values[:, :, k] = input_values_for_zone[:, :, k - start_layer]

        if use_regions:
            current_values[zone_region_cell_numbers] = new_values[
                i_indices, j_indices, k_indices
            ]
        else:
            current_values[zone_cell_numbers] = new_values[
                i_indices, j_indices, k_indices
            ]

        property_param.set_values(current_values, realisation_number)

    return True


def get_layer_range(indexer, zone_number, fmu_mode=False):
    _, _, nz = indexer.dimensions
    if fmu_mode:
        if len(indexer.zonation) == 1:
            layer_ranges = indexer.zonation[0]
        else:
            raise ValueError(
                'While in FMU / ERT mode, the grid must have EXACTLY 1 zone'
            )
    else:
        layer_ranges = indexer.zonation[
            zone_number - 1
        ]  # Zonation is 0-indexed, while zone numbers are 1-indexed
    start_layer = nz
    end_layer = 0
    for layer_range in layer_ranges:
        if start_layer > layer_range.start:
            start_layer = layer_range.start
        if end_layer < layer_range.stop:
            end_layer = layer_range.stop
    return end_layer, start_layer


def update_continuous_3d_parameter_values(
    grid_model,
    parameter_name,
    input_values,
    cell_index_defined=None,
    realisation_number=0,
    is_shared=False,
    set_initial_values=False,
    debug_level=Debug.OFF,
):
    """
    Description:
    Set 3D parameter with continuous values for specified grid model. The input is specified for a subset of all grid cells.
    This subset is defined by the numpy vector cell_index_defined and the number of values is num_defined_cells.
    Only the subset of cells will be updated unless the parameter set_initial_values is set. In that case all cells not covered
    by the cell_index_defined will be initializes to 0.0. The input numpy vector input_values has length equal to number of
    active grid cells for the grid model and contain the values to be assigned to the 3D parameter with
    name parameter_name belonging to the grid model with name grid_model.
    If the grid parameter with name parameter_name does not exist, it will be created and assigned value 0 in all
    cells except the cells defined by the cell_index_defined where it will be assigned the values taken from
    the  input_values vector. If the grid parameter exist, the grid cells with indices defined in cell_index_defined will be
    updated with values from input_values.
    :param set_initial_values:
    :param grid_model:   Grid model object
    :param parameter_name: Name of 3D parameter to update.
    :param input_values:  A numpy array of length equal to num_active_cells where num_active_cells is the number of all grid cells in the
                         grid model that is not inactive and will therefore usually be a much longer vector than num_defined_cells.
                         Only the values in this vector corresponding to the selected cells defined by cell_index_defined will be used.
                         The values are of type continuous.

    :param cell_index_defined: A list with cell indices in the array of all active cells for the grid model. The subset of cells
                             defined by this index array are the grid cells to be updated.
    :param realisation_number: Realisation number counted from 0 for the 3D parameter.
    :param is_shared:   Is set to true or false if the parameter is to be set to shared or non-shared.
    :param debug_level: Specify how much info is to be printed to screen. (0 - almost nothing output to screen, 3 - much output to screen)

    """
    if input_values is None:
        return

    function_name = update_continuous_3d_parameter_values.__name__
    # Check if specified grid model exists and is not empty
    if grid_model.is_empty(realisation_number):
        raise ValueError(
            f'Specified grid model: {grid_model.name} is empty for realisation {realisation_number + 1}.\n'
            f'Cannot create parameter: {parameter_name} '
        )

    grid = grid_model.get_grid(realisation_number)
    num_active_cells = grid.defined_cell_count
    if num_active_cells != len(input_values):
        raise ValueError(
            f'Mismatch in number of active cells={num_active_cells} '
            f'and length of input array with values = {len(input_values)}'
        )

    # Check if specified parameter name exists and create new parameter if it does not exist.
    if parameter_name not in grid_model.properties:
        if debug_level >= Debug.VERY_VERBOSE:
            print(
                f'--- Create specified RMS parameter: {parameter_name} in {grid_model.name}'
            )
            if is_shared:
                print('--- Set parameter to shared.')
            else:
                print('--- Set parameter to non-shared.')

        # Create a new 3D parameter with the specified name of type float32
        p = grid_model.properties.create(
            parameter_name, roxar.GridPropertyType.continuous, np.float32
        )
        p.set_shared(is_shared, realisation_number)
        # Initialize the values to 0 for this new 3D parameter
        current_values = np.zeros(num_active_cells, np.float32)

    else:
        if debug_level >= Debug.VERY_VERBOSE:
            print(
                f'--- Update specified RMS parameter: {parameter_name} in {grid_model.name}'
            )

        # Parameter exist, but check if it is empty or not
        current_values = np.zeros(num_active_cells, np.float32)
        p = grid_model.properties[parameter_name]
        if not (p.is_empty(realisation_number) or set_initial_values):
            # Check if the parameter is to updated instead of being initialized to 0
            current_values = p.get_values(realisation_number)

    # Assign values to the defined cells as specified in cell_index_defined index vector
    # Using vector operations for numpy vector:
    if len(cell_index_defined) > 0:
        current_values[cell_index_defined] = input_values[cell_index_defined]
    else:
        current_values = input_values

    p.set_values(current_values, realisation_number)


def set_discrete_3d_parameter_values(
    grid_model,
    parameter_name,
    input_values,
    code_names,
    zone_numbers=None,
    realisation_number=0,
    is_shared=False,
    debug_level=Debug.OFF,
):
    """Set discrete 3D parameter with values for specified grid model.
    Input:
           grid_model     - Grid model object
           parameter_name - Name of 3D parameter to get.
           input_values    - A numpy array of length equal to the number of active cells and with continuous values.
                           Only the grid cells belonging to the specified zones are updated even though the values array
                           contain values for all active cells.
           zone_numbers - A list of integer values that are zone numbers (counted from 0). If the list is empty or has
                          all zones included in the list, then grid cells in all zones are updated.
           code_names     - A dictionary with code names and code values for the discrete parameter values of the form as
                           in the example:
                           {1: 'F1', 2: 'F2',3: 'F3'}.
                           NOTE: Be sure to input a code_names dictionary containing all relevant facies for
                           for all zones, not only the zones that are updated by this function. If not, then
                           existing facies names and codes for zones that are not updated will be lost
                           from the facies table and need to be re-created manually or by script.
           realisation_number    - Realisation number counted from 0 for the parameter to get.
           is_shared      - Is set to true or false if the parameter is to be set to shared or non-shared.
           debug_level     - (value 0,1,2 or 3) and specify how much info is to be printed to screen.
           functionName  - Name of python function that call this function (Just for more informative print output).

    Output: True if 3D grid model exist and can be updated or
             not if the 3D grid does not exist or if a new facies code is introduced but
            the corresponding facies name already exits.
    """
    function_name = set_discrete_3d_parameter_values.__name__
    # Check if specified grid model exists and is not empty
    if grid_model.is_empty(realisation_number):
        raise ValueError(
            f'Specified grid model: {grid_model.name} is empty for realisation {realisation_number + 1}.\n'
            f'Cannot create parameter: {parameter_name} '
        )
    elif input_values.dtype == np.float32:
        raise ValueError('A discrete property cannot be of type float32')
    # Check if specified parameter name exists and create new parameter if it does not exist.
    if parameter_name not in grid_model.properties:
        if debug_level >= Debug.VERY_VERBOSE:
            print(
                f'--- Create specified RMS parameter: {parameter_name} in {grid_model.name}'
            )
            if is_shared:
                print('--- Set parameter to shared.')
            else:
                print('--- Set parameter to non-shared.')

        _create_property(
            grid_model,
            input_values,
            parameter_name,
            zone_numbers,
            is_shared,
            realisation_number,
            code_names,
            dtype=np.uint8,
        )
    else:
        if debug_level >= Debug.VERY_VERBOSE:
            print(
                f'--- Update specified RMS parameter: {parameter_name} in {grid_model.name}'
            )

        p = grid_model.properties[parameter_name]
        if p.is_empty(realisation_number):
            # Create parameter values (which are initialized to 0)
            grid = grid_model.get_grid(realisation_number)
            v = np.zeros(grid.defined_cell_count, np.uint8)
            p.set_values(v, realisation_number)

        # Get all active cell values
        p = get3DParameter(grid_model, parameter_name, realisation_number)
        if p.is_empty(realisation_number):
            raise ValueError(
                f'In function {function_name}.  Some inconsistency in program.'
            )
        current_values = p.get_values(realisation_number)
        current_values = modify_selected_grid_cells(
            grid_model, zone_numbers, realisation_number, current_values, input_values
        )
        p.set_values(current_values, realisation_number)

        code_names = p.code_names.copy()
        for code in code_names.keys():
            if code_names[code] == '':
                warn(
                    'There exists facies codes without facies names. Set facies name equal to facies code'
                )
                code_names[code] = str(code)

        # Calculate updated facies table by combining the existing facies table for the 3D parameter
        # with facies table for the facies that are modelled for the updated zones
        # Update the facies table in the discrete 3D parameter
        update_code_names(p, code_names)

        if debug_level >= Debug.VERY_VERBOSE:
            print('--- Updated facies table: ')
            print(p.code_names)


def _create_property(
    grid_model,
    values,
    parameter_name,
    zone_numbers,
    is_shared,
    realisation_number,
    code_names=None,
    dtype=np.float32,
):
    property_type = roxar.GridPropertyType.discrete
    if dtype == np.float32:
        property_type = roxar.GridPropertyType.continuous
    p = grid_model.properties.create(parameter_name, property_type, dtype)
    current_values = np.zeros(len(values), dtype)
    current_values = modify_selected_grid_cells(
        grid_model, zone_numbers, realisation_number, current_values, values
    )
    p.set_values(current_values, realisation_number)
    p.set_shared(is_shared, realisation_number)
    if code_names is not None:
        p.code_names = code_names.copy()


def update_discrete_3d_parameter_values(
    grid_model,
    parameter_name,
    input_values,
    num_defined_cells=0,
    cell_index_defined=None,
    facies_table=None,
    realisation_number=0,
    is_shared=True,
    set_default_facies_name_when_undefined=True,
    set_initial_values=False,
    debug_level=Debug.OFF,
):
    """
    Description:
    Set 3D parameter with discrete values for specified grid model. The input is specified for a subset of all grid cells.
    This subset is defined by the numpy vector cell_index_defined and the number of values is num_defined_cells.
    Only the subset of cells will be updated. The input numpy vector input_values has length equal to number of
    active grid cells for the grid model and contain the values to be assigned to the 3D parameter with
    name parameter_name belonging to the grid model with name grid_model.
    If the grid parameter with name parameter_name does not exist, it will be created and assigned value 0 in all
    cells except the cells defined by the cell_index_defined where it will be assigned the values taken from
    the  input_values vector. If the grid parameter exist, the grid cells with indices defined in cell_index_defined will be
    updated with values from input_values.
    :param set_initial_values:
    :param set_default_facies_name_when_undefined:
    :param facies_table:
    :param grid_model:   Grid model object
    :param parameter_name: Name of 3D parameter to update.
    :param input_values:  A numpy array of length equal to nActiveCells where nActiveCells is the number of all grid cells in the
                         grid model that is not inactive and will therefore usually be a much longer vector than num_defined_cells.
                         Only the values in this vector corresponding to the selected cells defined by cell_index_defined will be used.
                         The values are of type discrete np.uint8.

    :param num_defined_cells: Length of the list cell_index_defined
    :param cell_index_defined: A list with cell indices in the array of all active cells for the grid model. The subset of cells
                             defined by this index array are the grid cells to be updated.
    :param code_names: A dictionary with code names and code values for the discrete parameter values of the form as in the example:
                      {1: 'F1', 2: 'F2',3: 'F3'}.
                      NOTE: Be sure to input a code_names dictionary containing all relevant facies for
                      for all zones, not only the zones that are updated by this function. If not, then
                      existing facies names and codes for zones that are not updated will be lost
                      from the facies table and need to be re-created manually or by script.
    :param realisation_number: Realisation number counted from 0 for the 3D parameter.
    :param is_shared:   Is set to true or false if the parameter is to be set to shared or non-shared.
    :param debug_level: Specify how much info is to be printed to screen. (0 - almost nothing output to screen, 3 - much output to screen)

    """
    function_name = update_discrete_3d_parameter_values.__name__
    # Check if specified grid model exists and is not empty
    if grid_model.is_empty(realisation_number):
        raise ValueError(
            f'Specified grid model: {grid_model.name} is empty for realisation {realisation_number + 1}.\n'
            f'Cannot create parameter: {parameter_name} '
        )

    if cell_index_defined is not None:
        assert num_defined_cells == len(cell_index_defined)
    grid = grid_model.get_grid(realisation_number)
    num_active_cells = grid.defined_cell_count
    assert num_active_cells == len(input_values)

    # Check if specified parameter name exists and create new parameter if it does not exist.
    if parameter_name not in grid_model.properties:
        if debug_level >= Debug.VERY_VERBOSE:
            print(
                f'--- Create specified RMS parameter: {parameter_name} in {grid_model.name}'
            )
            if is_shared:
                print('--- Set parameter to shared.')
            else:
                print('--- Set parameter to non-shared.')

        # Create a new 3D parameter with the specified name
        p = grid_model.properties.create(
            parameter_name, roxar.GridPropertyType.discrete, np.uint8
        )

        # Initialize the values to 0 for this new 3D parameter
        current_values = np.zeros(num_active_cells, np.uint8)

        # Assign values to the defined cells as specified in cell_index_defined index vector
        # Using vector operations for numpy vector:
        current_values[cell_index_defined] = input_values[cell_index_defined]

        p.set_values(current_values, realisation_number)
        p.set_shared(is_shared, realisation_number)
        p.code_names = facies_table.copy()
    else:
        if debug_level >= Debug.VERY_VERBOSE:
            print(
                f'--- Update specified RMS parameter: {parameter_name} in {grid_model.name}'
            )

        # Parameter exist, but check if it is empty or not
        # Initialize the values to 0
        current_values = np.zeros(num_active_cells, np.uint8)
        p = grid_model.properties[parameter_name]

        # Check if the parameter is to updated instead of being initialized to 0
        if not (p.is_empty(realisation_number) or set_initial_values):
            # Keep the existing values for cells that is not updated
            current_values = p.get_values(realisation_number)
            if debug_level >= Debug.VERY_VERBOSE:
                print(f'--- Get values from existing RMS parameter: {parameter_name}')

        # Assign values to the defined cells as specified in cell_index_defined index vector
        if num_defined_cells > 0:
            current_values[cell_index_defined] = input_values[cell_index_defined]
        else:
            current_values = input_values

        p.set_values(current_values, realisation_number)

        # Calculate updated facies table by combining the existing facies table for the 3D parameter
        # with facies table for the facies that are modelled for the updated zones
        # Update the facies table in the discrete 3D parameter
        update_code_names(p, facies_table)

        code_names = p.code_names.copy()
        if set_default_facies_name_when_undefined:
            for code in code_names.keys():
                if code_names[code] == '':
                    if debug_level >= Debug.ON:
                        warn(
                            'There exists facies codes without facies names. Set facies name equal to facies code'
                        )
                    code_names[code] = str(code)

        if debug_level >= Debug.VERY_VERBOSE:
            print('--- Updated facies table: ')
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
            print(
                '--- Create new data type for horizon to be used '
                'for variogram azimuth trend'
            )

    return reprObj


def get2DMapDimensions(
    horizons, horizonName, representationName, debug_level=Debug.OFF
):
    # Read information about 2D grid size,orientation and resolution
    # from existing 2D map.
    horizonObj = None
    for h in horizons:
        if h.name == horizonName:
            horizonObj = h
            break
    if horizonObj is None:
        raise ValueError(
            f'Error in  get2DMapInfo\nError: Horizon name: {horizonName} does not exist'
        )

    reprObj = None
    for representation in horizons.representations:
        if representation.name == representationName:
            reprObj = representation
            break
    if reprObj is None:
        raise ValueError(
            f'Error in  get2DMapInfo\n'
            f'Error: Horizons data type: {representationName} does not exist'
        )

    surface = horizons[horizonName][representationName]
    if not isinstance(surface, roxar.Surface):
        raise ValueError(
            'Error in get2DMapInfo\nError: Specified object is not a 2D grid'
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
        print(f"""\
---  For 2D map
  Map xmin: {xmin}
  Map xmax: {xmax}
  Map ymin: {ymin}
  Map ymax: {ymax}
  Map xinc: {xinc}
  Map yinc: {yinc}
  Map nx:   {nx}
  Map ny:   {ny}
  Map rotation:   {rotation}""")
    return [nx, ny, xinc, yinc, xmin, ymin, xmax, ymax, rotation]


def setConstantValueInHorizon(
    horizons,
    horizonName,
    reprName,
    inputValue,
    debug_level=Debug.OFF,
    xmin=0,
    ymin=0,
    xinc=0,
    yinc=0,
    nx=0,
    ny=0,
    rotation=0,
):
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
            f'Error in updateHorizonObject\n'
            f'Error: Horizon name: {horizonName} does not exist'
        )

    # Find the correct representation. Must exist.
    representation = None
    for _representation in horizons.representations:
        if _representation.name == reprName:
            representation = _representation
            break
    if representation is None:
        raise ValueError(
            f'Error in updateHorizonObject\n'
            f'Error: Horizons data type: {reprName} does not exist'
        )

    surfaceObj = horizons[horizonName][reprName]
    if isinstance(surfaceObj, roxar.Surface):
        empty_grid = False
        try:
            grid = surfaceObj.get_grid()
        except RuntimeError:
            # Create surface
            empty_grid = True
            if nx == 0 or ny == 0:
                print(
                    'Error in setConstantValueInHorizon: Grid dimensions are not specified'
                )
                sys.exit()
            grid = roxar.RegularGrid2D.create(xmin, ymin, xinc, yinc, nx, ny, rotation)
            values = grid.get_values()
            values[:] = inputValue
            grid.set_values(values)
            surfaceObj.set_grid(grid)
            if debug_level >= Debug.VERY_VERBOSE:
                print(
                    f'--- Create trend surface {reprName} for variogram azimuth in {horizonName}'
                    f' Value: {inputValue}'
                )

        if not empty_grid:
            # Modify grid values
            values = grid.get_values()
            values[:] = inputValue
            grid.set_values(values)
            surfaceObj.set_grid(grid)
            if debug_level >= Debug.VERY_VERBOSE:
                print(
                    f'--- Update trend surface {reprName} for variogram azimuth in {horizonName}'
                    f' Value: {inputValue}'
                )
