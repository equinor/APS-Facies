#!/bin/env python
# -*- coding: utf-8 -*-
"""
Dependency: ROXAPI
Python 3 truncation script to be run in RMS 10 workflow
Input:
      XML model file.
Output:
      Facies realisation updated for specified zones.
      Updated 3D parameter for transformed gaussian fields.
"""
from collections import OrderedDict

import numpy as np

from src.algorithms.APSModel import APSModel
from src.utils.checks import check_probability_values, check_probability_normalisation
from src.utils.constants.simple import Debug, ProbabilityTolerances
from src.utils.grid import update_rms_parameter
from src.utils.methods import calc_average, get_specification_file
from src.utils.records import Probability
from src.utils.roxar.generalFunctionsUsingRoxAPI import (
    update_discrete_3d_parameter_values,
)
from src.utils.roxar.grid_model import (
    get3DParameter, getContinuous3DParameterValues,
    isParameterDefinedWithValuesInRMS, getDiscrete3DParameterValues,
    find_defined_cells, create_zone_parameter,
)
from src.utils.simulation import initialize_rms_parameters


def transform_empiric(cell_index_defined, gauss_values, alpha_values):
    """
    For the defined cells, transform the input Gaussian fields by the
    cumulative empiric distribution to get uniform distribution of the cells.
    The result is assigned to the input vectors alpha which also is returned.
    The input vectors gauss_values and alpha_values are both of length equal to
    the number of active cells in the grid model. The list cell_index_defined is an
    index array with indices in the gauss_values and alpha_values arrays. The length of cell_index_defined
    is num_defined_cells and is usually less than the number of active grid cells in the grid model.
    Typically the cell indices defined in cell_index_defined are all cells within a zone or a (zone,region) combination.

    :param cell_index_defined: Index array. The length is num_defined_cells.
                             The content is cell index which is used in the
                             grid parameter gauss_values or alpha_values.
    :type cell_index_defined: numpy vector
    :param gauss_values: Gaussian fields to be transformed. The length is the
                        same as the list of active cells in the grid model.
                        Only the subset of cells with indices specified in cell_index_defined
                        are considered here.
    :type gauss_values: numpy vector
    :param alpha_values: Transformed gaussian fields. The length is the same as
                        the gauss_values. The input values in the
                        alpha vectors are updated for those cells that belongs
                        to specified cell_index_defined list.
    :type alpha_values: numpy vector
    :return: The updated alpha vector is returned. Only cells with indices defined by
             the list cell_index_defined are modified compared with the values
             the vector had as input.
    """
    if gauss_values is None:
        return None
    num_defined_cells = len(cell_index_defined)
    increment = 1.0 / num_defined_cells
    # Numpy vector operation to select subset of values corresponding to the defined grid cells
    gauss_values_selected = gauss_values[cell_index_defined]

    # The numpy array operations below are equivalent to
    # the code:
    #    sort_index = np.argsort(gauss_values_selected)
    #    for i in range(num_defined_cells):
    #        index = sort_index[i]
    #        alpha_values[cell_index_defined[index]] = float(i) / float(num_defined_cells)

    range_array = np.arange(num_defined_cells)
    sort_index = np.argsort(gauss_values_selected)
    sorted_cell_index_defined = cell_index_defined[sort_index]
    alpha_values[sorted_cell_index_defined] = range_array * increment
    return alpha_values


def check_and_normalise_probability(
        num_facies, 
        prob_parameter_values_for_facies, 
        use_const_probability, 
        cell_index_defined,
        eps,
        tolerance_of_probability_normalisation,
        max_allowed_fraction_with_mismatch,
        debug_level
):
    """
    Check that probability cubes or probabilities in input prob_parameter_values_for_facies is
    normalised. If not normalised, a normalisation is done. The numpy vector
    cell_index_defined is an index vector. The length is in general less than
    the total number of active cells for the grid. Typically the
    cell_index_defined vector represents active cells belonging to a specified
    zone, but could in principle be any subset of interest of the total set of
    all active cells. The content of the cell_index_defined array is indices in
    vectors containing all active cells and is a way of defining a subset of
    cells.
    :param num_facies: the number of facies
    :type num_facies: int
    :param prob_parameter_values_for_facies: A list of vectors where each vector
                                     represents probabilities for active grid
                                     cells. The first entry corresponds to the
                                     first facies in the facies list and so on.
                                     [facies_name,values] = prob_parameter_values_for_facies[f]
                                     where facies_name is facies name and values is
                                     the probability values per cell.
                                     Note: If use_const_probability = 1, the values
                                     list has one element only. and represent
                                     a constant facies probability.
                                     If use_const_probability = 0, the values is a list
                                     of probabilities, one per grid cell.
    :type prob_parameter_values_for_facies: list
    :param use_const_probability: Is True if prob_parameter_values_for_facies contains constant
                         probabilities and False if prob_parameter_values_for_facies
                         contains vectors of probabilities, one value per
                         active grid cell.
    :type use_const_probability: bool
    :param cell_index_defined: A vector containing indices. cell_index_defined[i]
                             is an index in the probability vectors in
                             prob_parameter_values_for_facies. It is a way to defined
                             a filter of grid cells, a subset of all active
                             grid cells in the grid.
    :type cell_index_defined: numpy vector
    :param eps: Probability tolerance. If normalisation of probability values deviates more than eps from 1.0,
                calculations are done to normalise the probabilities.
    :type eps: float value > 0.0 but usually small
    :param debug_level: Define output print level from the function.
    :type debug_level: Debug
    :return: list of vectors, one per facies. The vectors are normalised
             probabilities for the subset of grid cells defined by the
             cell_index_defined index vector.
    """
    # The list prob_parameter_values_for_facies has items =[name,values]
    # Define index names for this item

    if debug_level >= Debug.VERY_VERBOSE:
        if use_const_probability:
            print('Debug output: Check normalisation of probabilities.')
        else:
            print('Debug output: Check normalisation of probability cubes.')

    probability_defined = []
    num_cell_with_modified_probability = 0
    if use_const_probability:
        for f in range(num_facies):
            item = prob_parameter_values_for_facies[f]
            facies_name = item.name
            values = item.value
            if debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: Facies: {} with constant probability: '.format(facies_name, values[0]))
            probability_defined.append(values[0])

        # Check that probabilities sum to 1
        psum = probability_defined[0]
        for f in range(1, num_facies):
            psum = psum + probability_defined[f]
        if abs(psum - 1.0) > eps:
            raise ValueError(
                f'Probabilities for facies are not normalized for this zone (Total: {psum})'
            )

    else:
        num_defined_cells = len(cell_index_defined)

        # Allocate space for probability per facies per defined cell
        for f in range(num_facies):
            probability_defined.append(np.zeros(num_defined_cells, np.float32))
            item = prob_parameter_values_for_facies[f]
            facies_name = item.name
            values = item.value
            if debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: Facies: ' + facies_name)

            defined_values = values[cell_index_defined]
            # Check that probabilities are in interval [0,1]. If not, set to 0 if negative and 1 if larger than 1.
            # Error message if too large fraction of input values are outside interval [0,1] also when using tolerance.
            probability_defined[f] = check_probability_values(
                defined_values, 
                tolerance_of_probability_normalisation,
                max_allowed_fraction_with_mismatch, 
                facies_name
            )

        # Sum up probability over all facies per defined cell
        prob_vector = probability_defined[0]
        psum = np.copy(prob_vector)
        for f in range(1, num_facies):
            # sum of np arrays (cell by cell sum)
            psum += probability_defined[f]

        normalise_is_necessary = check_probability_normalisation(psum, 
                                                                 eps, 
                                                                 tolerance_of_probability_normalisation,
                                                                 max_allowed_fraction_with_mismatch
        )
        if normalise_is_necessary:
            if debug_level >= Debug.VERBOSE:
                print('--- Normalise probability cubes.')

            for f in range(num_facies):
                prob_vector = probability_defined[f]
                if f == 0:
                    # Numpy operation to make an array with 0 or 1 where 1 is set if condition is satisfied
                    # Number of cells with 1 are number of cells with modified probabilities
                    check_value = (psum > (1.0 + eps)) | (psum < (1.0 - eps))
                    num_cell_with_modified_probability = check_value.sum()

                # Normalisation
                prob_vector = prob_vector / psum
                probability_defined[f] = prob_vector

            if debug_level >= Debug.VERY_VERBOSE:
                print(
                    f'Debug output: Number of grid cells in zone is:                           {num_defined_cells}\n'
                    f'Debug output: Number of grid cells which is recalculated and normalized: {num_cell_with_modified_probability}'
                )
    return probability_defined, num_cell_with_modified_probability


def get_used_gauss_field_names_in_zone(gauss_field_names_in_zone, gauss_field_names_in_truncation_rule):
    '''
    input:
    - list of gauss fields specified for a zone
    - list of gauss_fields used in truncation rule for the same zone
    Return an ordered dictionary with gauss field name as key and bool values as values.
    The bool values are true if the gauss field is used, false if not used.
    '''
    use_gauss_field_in_zone = OrderedDict()
    for name in gauss_field_names_in_zone:
        use_gauss_field_in_zone[name] = name in gauss_field_names_in_truncation_rule
    return use_gauss_field_in_zone


# @do_cprofile
def run(
        project,
        eps=ProbabilityTolerances.MAX_DEVIATION_BEFORE_ACTION,
        tolerance_of_probability_normalisation=ProbabilityTolerances.MAX_ALLOWED_DEVIATION_BEFORE_ERROR,
        max_allowed_fraction_with_mismatch=ProbabilityTolerances.MAX_ALLOWED_FRACTION_OF_VALUES_OUTSIDE_TOLERANCE,
        write_rms_parameters_for_qc_purpose=True,
        **kwargs
):
    realization_number = project.current_realisation
    print(f'Run: APS_trunc on realisation {realization_number + 1}')

    model_file_name = get_specification_file(**kwargs)

    print(f'- Read file: {model_file_name}')
    aps_model = APSModel(model_file_name)
    debug_level = aps_model.debug_level
    grid_model = project.grid_models[aps_model.grid_model_name]
    if grid_model.is_empty():
        raise ValueError(f'Specified grid model: {grid_model.name} is empty.')

    all_zone_models = aps_model.sorted_zone_models
    zone_param_name = aps_model.getZoneParamName()
    region_param_name = aps_model.getRegionParamName()
    use_regions = bool(region_param_name)
    result_param_name = aps_model.getResultFaciesParamName()

    # Get zone param values
    if debug_level >= Debug.VERBOSE:
        print(f'--- Get RMS zone parameter: {zone_param_name} from RMS project {aps_model.rms_project_name}')
    zone_param = create_zone_parameter(
        grid_model,
        name=zone_param_name,
        realization_number=realization_number,
        set_shared=False,
        debug_level=debug_level,
    )
    zone_values = zone_param.get_values(realization_number)

    region_values = None
    if use_regions:
        if debug_level >= Debug.VERBOSE:
            print(f'--- Get RMS region parameter: {region_param_name} from RMS project {aps_model.rms_project_name}')
        region_values, _ = getDiscrete3DParameterValues(grid_model, region_param_name, realization_number, debug_level)

    # Get or initialize array for facies realisation
    num_cells_total = len(zone_values)
    facies_real = np.zeros(num_cells_total, np.uint16)
    code_names_for_input = {}
    # Check if specified facies realization exists and get it if so.
    if isParameterDefinedWithValuesInRMS(grid_model, result_param_name, realization_number):
        if debug_level >= Debug.VERBOSE:
            print(
                f'--- Get RMS facies parameter which will be updated: '
                f'{result_param_name} from RMS project: {aps_model.rms_project_name}'
            )
        facies_real, code_names_for_input = getDiscrete3DParameterValues(
            grid_model, result_param_name, realization_number, debug_level
        )
    else:
        if debug_level >= Debug.VERBOSE:
            print(
                f'--- Facies parameter: {result_param_name} for the result will be created '
                f'in the RMS project: {aps_model.rms_project_name}'
            )

    # Initialize dictionaries keeping gauss field values and trends for all used gauss fields
    gf_all_values, gf_all_alpha, gf_all_trend_values = initialize_rms_parameters(
        project, aps_model, write_rms_parameters_for_qc_purpose
    )
    # Probability related lists
    probability_parameter_names_already_read = []
    probability_parameter_all_values = []
    # The two lists: probability_parameter_all_values, probability_parameter_values_for_facies,
    # will use a list of items where the item is of the form item =[name,value]

    # List of modelled facies names
    all_facies_names_modelled = []
    if debug_level >= Debug.VERY_VERBOSE:
        if aps_model.isAllZoneRegionModelsSelected():
            print('Debug output: All combinations of zone and region is selected to be run')
        else:
            print('Debug output: Selected (zone,region) pairs to simulate:')
            print_zones_and_regions(all_zone_models, aps_model, use_regions)

    # Loop over all pairs of (zone_number, region_number) that is specified and selected
    # This loop calculates facies for the given (zone_number, region_number) combination
    for key, zone_model in all_zone_models.items():
        zone_number, region_number = key
        if not aps_model.isSelected(zone_number, region_number):
            continue

        if debug_level >= Debug.SOMEWHAT_VERBOSE:
            if use_regions:
                print(f'\n- Run model for (zone_number, region_number) = ({zone_number}, {region_number})\n')
            else:
                print(f'\n- Run model for zone number: {zone_number}\n')

        zone_model = aps_model.getZoneModel(zone_number, region_number)

        # Read trend parameters for truncation rule parameters
        zone_model.getTruncationParam(grid_model, realization_number)

        # Number of gauss fields defined for the zone in model file
        gf_names_for_zone = zone_model.used_gaussian_field_names

        # Number of gauss fields used in truncation rule for the zone in model file
        gf_names_for_truncation_rule = zone_model.getGaussFieldsInTruncationRule()

        facies_names_for_zone = zone_model.facies_in_zone_model
        num_facies = len(facies_names_for_zone)

        if debug_level >= Debug.VERBOSE:
            print('--- Gauss field parameter specified for this zone: ')
            for gf_name in gf_names_for_zone:
                print(f'---   {gf_name}')
            print('--- Gauss field parameter used in truncation rule for this zone: ')
            for gf_name in gf_names_for_truncation_rule:
                print(f'---   {gf_name}')

        # For current (zone,region) find the active cells
        cell_index_defined = find_defined_cells(
            zone_values, zone_number, region_values, region_number, debug_level=debug_level,
        )
        if debug_level >= Debug.VERBOSE:
            if use_regions:
                print(
                    f'--- Number of active cells for (zone,region)='
                    f'({zone_number}, {region_number}): {len(cell_index_defined)}'
                )
            else:
                print(f'--- Number of active cells for zone: {len(cell_index_defined)}')
        if len(cell_index_defined) == 0:
            print(
                f'Warning: No active grid cells for (zone, region)=({zone_number}, {region_number})\n'
                '         Skip this zone, region combination'
            )
            continue

        # For current zone,transform all gaussian fields used in this zone and update alpha
        # NOTE: The dictionary for alpha fields for current zone must be ordered in the same sequence as gf_names_for_zone
        gf_alpha_for_current_zone = OrderedDict()
        for gf_name in gf_names_for_zone:
            if gf_name in gf_names_for_truncation_rule:
                gauss_field_values_all = gf_all_values[gf_name]

                if debug_level >= Debug.VERBOSE:
                    if use_regions:
                        print(f'--- Transform: {gf_name} for zone: {zone_number}')
                    else:
                        print(f'--- Transform: {gf_name} for (zone, region)=({zone_number}, {region_number})')
                # Update alpha for current zone
                alpha_all = gf_all_alpha[gf_name]
                alpha_all = transform_empiric(cell_index_defined, gauss_field_values_all, alpha_all)
                gf_all_alpha[gf_name] = alpha_all

                # Dictionary of transformed values for gauss field for current (zone,region)
                gf_alpha_for_current_zone[gf_name] = alpha_all

                if write_rms_parameters_for_qc_purpose:
                    # Write back to RMS project the transformed gaussian values for the zone
                    update_rms_parameter(
                        grid_model, gf_name, alpha_all, cell_index_defined,
                        realization_number, variable_name_extension='transf',
                        use_regions=use_regions, zone_number=zone_number,
                        region_number=region_number, debug_level=debug_level
                    )

            else:
                # This gauss field name is specified for the zone but not used in truncation rule and not simulated or
                # used. But it is necessary to have defined an entry for it to keep this dictionary in the same order
                # and of same length as the list of gauss field names for zone.
                gf_alpha_for_current_zone[gf_name] = None

        # Get all facies names to be modelled for this zone and corresponding probability parameters
        probability_parameter_values_for_facies = []
        for facies_name in facies_names_for_zone:
            probability_parameter = zone_model.getProbParamName(facies_name)
            if debug_level >= Debug.VERY_VERBOSE:
                print(
                    f'Debug output: Zone: {zone_number}  '
                    f'Facies name: {facies_name}  '
                    f'Probability: {probability_parameter}'
                )
            values = []
            if zone_model.use_constant_probabilities:
                values.append(float(probability_parameter))
                # Add the probability values to a common list containing probabilities for
                # all facies used in the whole model (all zones) to avoid loading the same data multiple times.
                probability_parameter_all_values.append(Probability(facies_name, values))

                # Probabilities for each facies for current zone
                probability_parameter_values_for_facies.append(Probability(facies_name, values))
            else:
                if probability_parameter not in probability_parameter_names_already_read:
                    probability_parameter_names_already_read.append(probability_parameter)
                    if debug_level >= Debug.VERY_VERBOSE:
                        print(
                            f'Debug output: '
                            f'Probability parameter: {probability_parameter} is now being loaded '
                            f'for facies: {facies_name} for zone: {zone_number}'
                        )

                    values = getContinuous3DParameterValues(grid_model, probability_parameter, realization_number, debug_level)

                    # Add the probability values to a common list containing probabilities for
                    # all facies used in the whole model (all zones) to avoid loading the same data multiple times.
                    probability_parameter_all_values.append(Probability(facies_name, values))

                    # Probabilities for each facies for current zone
                    probability_parameter_values_for_facies.append(Probability(facies_name, values))

                else:
                    if debug_level >= Debug.VERY_VERBOSE:
                        if use_regions:
                            print(
                                f'Debug output: Probability parameter: {probability_parameter} '
                                f'is already loaded for facies: {facies_name} for (zone, region)='
                                f'({zone_number}, {region_number})'
                            )
                        else:
                            print(
                                f'Debug output: '
                                f'Probability parameter: {probability_parameter} is already loaded '
                                f'for facies: {facies_name} for zone: {zone_number}'
                            )

                    index = -np.infty
                    # Get the probability values from the common list since it already is loaded
                    for i in range(len(probability_parameter_all_values)):
                        name = probability_parameter_all_values[i].name
                        if facies_name == name:
                            index = i
                            break
                    # Probabilities for each facies for current zone
                    values = probability_parameter_all_values[index].value
                    probability_parameter_values_for_facies.append(Probability(facies_name, values))

        # end for

        # Check and normalise probabilities if necessary for current zone
        if debug_level >= Debug.VERBOSE:
            print('--- Check normalisation of probability fields.')
        probability_defined, num_cells_modified_probability = check_and_normalise_probability(
            num_facies, 
            probability_parameter_values_for_facies, 
            zone_model.use_constant_probabilities,
            cell_index_defined, 
            eps, 
            tolerance_of_probability_normalisation,
            max_allowed_fraction_with_mismatch,
            debug_level
        )
        if debug_level >= Debug.VERBOSE:
            print(f'--- Number of cells that are normalised: {num_cells_modified_probability}')

        # Apply truncations and calculate or update facies realization
        if debug_level >= Debug.VERBOSE:
            print('--- Truncate transformed Gaussian fields.')

        if zone_model.key_resolution > 0:
            # Use optimization
            if debug_level >= Debug.VERBOSE:
                print('--- Use optimization (Memoization and vectorization)')
            facies_real, volume_fraction = zone_model.applyTruncations_vectorized(
                probability_defined, gf_alpha_for_current_zone, facies_real, cell_index_defined
            )
        else:
            # Do not use optimization
            facies_real, volume_fraction = zone_model.applyTruncations(
                probability_defined, gf_alpha_for_current_zone, facies_real, cell_index_defined
            )

        if debug_level >= Debug.ON:
            print('')
            main_facies_table = aps_model.getMainFaciesTable()
            if zone_model.use_constant_probabilities:
                if use_regions:
                    print(
                        '--- Zone_number:  Region_number:    Facies_code:   Facies_name:'
                        '     Volumefraction_specified:    Volumefracion_realisation:'
                    )
                    for f in range(len(facies_names_for_zone)):
                        facies_name = facies_names_for_zone[f]
                        facies_code = main_facies_table.getFaciesCodeForFaciesName(facies_name)
                        item = probability_parameter_values_for_facies[f]
                        if facies_name != item.name:
                            raise ValueError('Inconsistencies in data structure in APS_main')

                        probabilities = item.value
                        print('{0:4d} {1:4d} {2:4d}  {3:10}  {4:.3f}   {5:.3f}'.format(
                            zone_number, region_number, facies_code, facies_name, probabilities[0], volume_fraction[f])
                        )
                else:
                    print(
                        '--- Zone_number:    Facies_code:   Facies_name:'
                        '     Volumefraction_specified:    Volumefracion_realisation:'
                    )
                    for f in range(len(facies_names_for_zone)):
                        facies_name = facies_names_for_zone[f]
                        facies_code = main_facies_table.getFaciesCodeForFaciesName(facies_name)
                        item = probability_parameter_values_for_facies[f]
                        if facies_name != item.name:
                            raise ValueError('Inconsistencies in data structure in APS_main')

                        probabilities = item.value
                        print('{0:4d} {1:4d}  {2:10}  {3:.3f}   {4:.3f}'.format(
                            zone_number, facies_code, facies_name, probabilities[0], volume_fraction[f])
                        )

            else:
                if use_regions:
                    print(
                        '--- Zone_number:  Region_number:   Facies_code:   Facies_name:'
                        '     Volumefraction_realisation  Volumefraction_from_probcube:'
                    )
                    for f in range(len(facies_names_for_zone)):
                        facies_name = facies_names_for_zone[f]
                        facies_code = main_facies_table.getFaciesCodeForFaciesName(facies_name)
                        item = probability_parameter_values_for_facies[f]
                        if facies_name != item.name:
                            raise ValueError('Inconsistencies in data structure in APS_main')

                        values = item.value
                        average_probabilities = calc_average(cell_index_defined, values)
                        print(
                            '{0:4d} {1:4d} {2:4d}  {3:10}  {4:.3f}   {5:.3f}'
                            ''.format(
                                zone_number, region_number, facies_code,
                                facies_name, volume_fraction[f], average_probabilities
                            )
                        )
                else:
                    print(
                        '--- Zone_number:    Facies_code:   Facies_name:'
                        '     Volumefraction_realisation  Volumefraction_from_probcube:'
                    )
                    for f in range(len(facies_names_for_zone)):
                        facies_name = facies_names_for_zone[f]
                        facies_code = main_facies_table.getFaciesCodeForFaciesName(facies_name)
                        item = probability_parameter_values_for_facies[f]
                        if facies_name != item.name:
                            raise ValueError('Inconsistencies in data structure in APS_main')

                        values = item.value
                        average_probabilities = calc_average(cell_index_defined, values)
                        print('{0:4d} {1:4d}  {2:10}  {3:.3f}   {4:.3f}'.format(
                            zone_number, facies_code, facies_name, volume_fraction[f], average_probabilities)
                        )

        for facies_name in facies_names_for_zone:
            if facies_name not in all_facies_names_modelled:
                all_facies_names_modelled.append(facies_name)
                if debug_level >= Debug.VERY_VERBOSE:
                    print(f'Debug: Add facies: {facies_name} to the list of modelled facies')

    # End loop over zones

    print('')

    # Write/update facies realisation
    main_facies_table = aps_model.getMainFaciesTable()

    code_names = code_names_for_input.copy()
    for i in range(len(all_facies_names_modelled)):
        facies_name = all_facies_names_modelled[i]
        facies_code = main_facies_table.getFaciesCodeForFaciesName(facies_name)
        code_names.update({facies_code: facies_name})

    if debug_level >= Debug.VERY_VERBOSE:
        print('Debug output: Facies codes and names before merging with existing facies table for facies realisation:')
        print(repr(code_names))

    # Write facies realisation back to RMS project for all zones that is modelled.
    if debug_level >= Debug.VERBOSE:
        if aps_model.isAllZoneRegionModelsSelected():
            print('Debug output: All combinations of zone and region is selected to be run')
        else:
            print('--- The following (zone,region) numbers are updated in facies realization:')
            print_zones_and_regions(all_zone_models, aps_model, use_regions)

    # Overwrite the existing facies realization, but note that now the facies_real should contain values
    # equal to the original facies realization for all cells that is not updated
    #  (not belonging to (zones, regions) that is updated)
    update_discrete_3d_parameter_values(
        grid_model, result_param_name, facies_real, facies_table=code_names,
        realisation_number=realization_number, is_shared=False, set_initial_values=False,
        debug_level=debug_level,
    )
    if debug_level >= Debug.SOMEWHAT_VERBOSE:
        print(f'- Create or update parameter: {result_param_name}')

    print('')
    if debug_level >= Debug.ON:
        print('- Updated facies table:')
        p = get3DParameter(grid_model, result_param_name)
        print('- Facies_name   Facies_code')
        for key in p.code_names:
            u = p.code_names.get(key)
            print(f'  {u:10}  {key:3d}')

        print('')
    print('Finished APS_main.py')


def print_zones_and_regions(all_zone_models, aps_model, use_regions):
    for key, zone_model in all_zone_models.items():
        zone_number, region_number = key
        if not aps_model.isSelected(zone_number, region_number):
            continue
        if use_regions:
            print(f'    (zone, region)=({zone_number}, {region_number})')
        else:
            print(f'    zone={zone_number}')
