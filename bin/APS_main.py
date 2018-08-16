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
import numpy as np

from src.utils.roxar.generalFunctionsUsingRoxAPI import (
    updateContinuous3DParameterValues, updateDiscrete3DParameterValues,
)
from src.utils.roxar.grid_model import (
    get3DParameter, getContinuous3DParameterValues,
    isParameterDefinedWithValuesInRMS, getDiscrete3DParameterValues,
    find_defined_cells,
)

from src.utils.methods import calc_average
from src.algorithms.APSModel import APSModel
from src.utils.constants.simple import Debug, ProbabilityTolerances
from src.utils.methods import get_model_file_name




def transform_empiric(cell_index_defined, gauss_values, alpha_values):
    """
    For the defined cells, transform the input Gaussian fields by the
    cumulative empiric distribution to get uniform distribution of the cells.
    The result is assigned to the input vectors alpha which also is returned.
    The input vectors gaussValues and alpha_values are both of length equal to
    the number of active cells in the grid model. The list cell_index_defined is an
    index array with indices in the gaussValues and alpha_values arrays. The length of cell_index_defined
    is nDefinedCells and is usually less than the number of active grid cells in the grid model.
    Typically the cell indices defined in cell_index_defined are all cells within a zone or a (zone,region) combination.

    :param cell_index_defined: Index array. The length is nDefinedCells.
                             The content is cell index which is used in the
                             grid parameter gaussValues or alpha_values.
    :type cell_index_defined: list
    :param gauss_values: Gaussian fields to be transformed. The length is the
                        same as the list of active cells in the grid model.
                        Only the subset of cells with indices specified in cell_index_defined
                        are considered here.
    :type gauss_values: numpy vector
    :param alpha_values: Transformed gaussian fields. The length is the same as
                        the gaussValues. The input values in the
                        alpha vectors are updated for those cells that belongs
                        to specified cell_index_defined list.
    :type alpha_values: numpy vector
    :return: The updated alpha vector is returned. Only cells with indices defined by
             the list cell_index_defined are modified compared with the values
             the vector had as input.
    """
    y1_defined = []
    num_defined_cells = len(cell_index_defined)
    for i in range(num_defined_cells):
        index = cell_index_defined[i]
        y1_defined.append(gauss_values[index])

    sort_index = np.argsort(y1_defined)
    for i in range(num_defined_cells):
        index = sort_index[i]
        # Assign the probability p= i/N to the cell corresponding to y1_defined cell
        # with number i in sorting from smallest to highest value.
        # Use cell_index_defined to assign it to the correct cell.
        alpha_values[cell_index_defined[index]] = float(i) / float(num_defined_cells)

    return alpha_values


def check_and_normalise_probability(
        num_facies, prob_parameter_values_for_facies, use_const_probability, cell_index_defined,
        eps=0.0000001, tolerance_of_probability_normalisation = 0.01,
        debug_level=Debug.SOMEWHAT_VERBOSE
):
    """
    Check that probability cubes or probabilities in input probFacies is
    normalised. If not normalised, a normalisation is done. The list
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
                                     Note: If useConstProb = 1, the values
                                     list has one element only. and represent
                                     a constant facies probability.
                                     If useConstProb = 0, the values is a list
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
    :type cell_index_defined: list
    :param eps: # TODO
    :param debug_level: Define output print level from the function.
    :type debug_level: Debug
    :return: list of vectors, one per facies. The vectors are normalised
             probabilities for the subset of grid cells defined by the
             cell_index_defined index vector.
            TODO: Correct?
    """
    # The list prob_parameter_values_for_facies has items =[name,values]
    # Define index names for this item
    NAME = 0
    VAL = 1

    num_defined_cells = len(cell_index_defined)

    # Check that probabilities sum to 1
    if debug_level >= Debug.VERY_VERBOSE:
        if not use_const_probability:
            print('Debug output: Check normalisation of probability cubes.')
        else:
            print('Debug output: Check normalisation of probabilities.')

    probability_defined = []
    num_cell_with_modified_probability = 0
    if not use_const_probability:
        # Allocate space for probability per facies per defined cell
        for f in range(num_facies):
            probability_defined.append(np.zeros(num_defined_cells, np.float32))
            item = prob_parameter_values_for_facies[f]
            facies_name = item[NAME]
            values = item[VAL]
            if debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: Facies: ' + facies_name)

            num_negative = 0
            num_above_one = 0
            for i in range(num_defined_cells):
                index = cell_index_defined[i]
                v = values[index]
                if v < 0.0:
                    num_negative += 1
                elif v > 1.0:
                    num_above_one += 1
                probability_defined[f][i] = v
            if num_negative > 0:
                raise ValueError(
                    'Probability for facies ' + facies_name + ' has ' + str(num_negative) + ' negative values'
                )
            if num_above_one > 0:
                raise ValueError(
                    'Probability for facies ' + facies_name + ' has ' + str(num_above_one) + ' values above 1.0'
                )

        # Sum up probability over all facies per defined cell
        p = probability_defined[0]
        psum = np.copy(p)
        ones = np.ones(num_defined_cells, np.float32)
        for f in range(1, num_facies):
            # sum of np arrays (cell by cell sum)
            psum += probability_defined[f]

        if not np.allclose(psum, ones, eps):
            if debug_level >= Debug.VERBOSE:
                text = '--- Normalise probability cubes.'
                print(text)

            unacceptable_prob_normalisation = 0
            min_acceptable_prob_sum = 1.0 - tolerance_of_probability_normalisation
            max_acceptable_prob_sum = 1.0 + tolerance_of_probability_normalisation
            largest_prob_sum = 0.0
            smallest_prob_sum = 1.0
            for i in range(num_defined_cells):
                if smallest_prob_sum > psum[i]:
                    smallest_prob_sum = psum[i]
                if largest_prob_sum < psum[i]:
                    largest_prob_sum = psum[i]

                if not (min_acceptable_prob_sum <= psum[i] <= max_acceptable_prob_sum):
                    unacceptable_prob_normalisation += 1

            if unacceptable_prob_normalisation > 0:
                raise ValueError(
                    'Sum of input facies probabilities is either less than: {} or larger than: {} in: {} cells.\n'
                    'Input probabilities should be normalised and the sum close to 1.0 but found a minimum value of: {} and a maximum value of: {}\n'
                    'Check input probabilities!'
                    ''.format(min_acceptable_prob_sum, max_acceptable_prob_sum, unacceptable_prob_normalisation, smallest_prob_sum, largest_prob_sum)
                )
            for f in range(num_facies):
                p = probability_defined[f]  # Points to array of probabilities
                for i in range(num_defined_cells):
                    if np.abs(psum[i] - 1.0) > eps:
                        # Have to normalize
                        if f == 0:
                            num_cell_with_modified_probability += 1
                        p[i] = p[i] / psum[i]
                        # print('i,p,psum:' + str(i) + ' ' + str(p[i]) + ' ' + str(psum[i]))

            if debug_level >= Debug.VERY_VERBOSE:
                print(
                    'Debug output: Number of grid cells in zone is:                           {}\n'
                    'Debug output: Number of grid cells which is recalculated and normalized: {}'
                    ''.format(num_defined_cells, num_cell_with_modified_probability)
                )
    else:
        for f in range(num_facies):
            item = prob_parameter_values_for_facies[f]
            facies_name = item[NAME]
            values = item[VAL]
            if debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: Facies: {} with constant probability: '.format(facies_name, values[0]))
            probability_defined.append(values[0])

        # Check that probabilities sum to 1
        psum = probability_defined[0]
        for f in range(1, num_facies):
            psum = psum + probability_defined[f]
        if abs(psum - 1.0) > eps:
            raise ValueError(
                'Probabilities for facies are not normalized for this zone '
                '(Total: {})'.format(psum)
            )

    return probability_defined, num_cell_with_modified_probability


def run(
        roxar=None, project=None,
        eps=ProbabilityTolerances.MAX_DEVIATION_BEFORE_ACTION,
        tolerance_of_probability_normalisation=ProbabilityTolerances.MAX_ALLOWED_DEVIATION_BEFORE_ERROR,
        write_trends_to_rms_for_qc_purpose=True,
        **kwargs
):
    realization_number = project.current_realisation
    print('Run: APS_trunc  on realisation ' + str(realization_number + 1))

    model_file_name = get_model_file_name(**kwargs)

    print('- Read file: ' + model_file_name)
    aps_model = APSModel(model_file_name)
    debug_level = aps_model.debug_level
    rms_project_name = aps_model.getRMSProjectName()
    grid_model_name = aps_model.getGridModelName()
    grid_model = project.grid_models[grid_model_name]
    if grid_model.is_empty():
        raise ValueError('Specified grid model: ' + grid_model.name + ' is empty.')

    all_zone_models = aps_model.sorted_zone_models
    zone_param_name = aps_model.getZoneParamName()
    region_param_name = aps_model.getRegionParamName()
    use_regions = region_param_name != ''
    result_param_name = aps_model.getResultFaciesParamName()

    # Get zone param values
    if debug_level >= Debug.VERBOSE:
        print('--- Get RMS zone parameter: ' + zone_param_name + ' from RMS project ' + rms_project_name)
    zone_values, _ = getDiscrete3DParameterValues(grid_model, zone_param_name, realization_number, debug_level)

    region_values = None
    if use_regions:
        if debug_level >= Debug.VERBOSE:
            print('--- Get RMS region parameter: ' + region_param_name + ' from RMS project ' + rms_project_name)
        region_values, _ = getDiscrete3DParameterValues(grid_model, region_param_name, realization_number, debug_level)

    # Get or initialize array for facies realisation
    num_cells_total = len(zone_values)
    facies_real = np.zeros(num_cells_total, np.uint16)
    code_names_for_input = {}
    # Check if specified facies realization exists and get it if so.
    if isParameterDefinedWithValuesInRMS(grid_model, result_param_name, realization_number):
        if debug_level >= Debug.VERBOSE:
            print('--- Get RMS facies parameter which will be updated: {} from RMS project: {}'.format(result_param_name, rms_project_name))
        [facies_real, code_names_for_input] = getDiscrete3DParameterValues(grid_model, result_param_name, realization_number, debug_level)
    else:
        if debug_level >= Debug.VERBOSE:
            print('--- Facies parameter: {}  for the result will be created in the RMS project: {}'.format(result_param_name, rms_project_name))

    # Gaussian field related lists
    gf_names_already_read = []
    gf_all_values = []
    gf_all_alpha = []
    gf_all_trend_values = []

    # Probability related lists
    probability_parameter_names_already_read = []
    probability_parameter_all_values = []
    # The four lists: probability_parameter_all_values,probability_parameter_values_for_facies,gf_all_values,
    # gf_all_alpha will use a list of items where the item is of the form item =[name,value]
    # Index values are defined by:
    NAME = 0  # Name of index in items = [ name, values]
    VAL = 1  # Name of index in items = [ name, values]

    # List of modelled facies names
    all_facies_names_modelled = []
    if debug_level >= Debug.VERY_VERBOSE:
        if aps_model.isAllZoneRegionModelsSelected():
            print('Debug output: All combinations of zone and region is selected to be run')
        else:
            print('Debug output: Selected (zone,region) pairs to simulate:')
            for key, zone_model in all_zone_models.items():
                zone_number = key[0]
                region_number = key[1]
                if not aps_model.isSelected(zone_number, region_number):
                    continue
                if use_regions:
                    print('    (zone,region)=({},{})'.format(key[0], key[1]))
                else:
                    print('    zone={}'.format(key[0]))

    # Loop over all pairs of (zone_number, region_number) that is specified and selected
    # This loop calculates facies for the given (zone_number, region_number) combination
    for key, zone_model in all_zone_models.items():
        zone_number = key[0]
        region_number = key[1]
        if not aps_model.isSelected(zone_number, region_number):
            continue

        if use_regions:
            if debug_level >= Debug.SOMEWHAT_VERBOSE:
                print('\n- Run model for (zone_number, region_number) = ({},{})\n'.format(zone_number, region_number))
        else:
            if debug_level >= Debug.SOMEWHAT_VERBOSE:
                print('\n- Run model for zone number: {}\n'.format(zone_number))

        zone_model = aps_model.getZoneModel(zone_number, region_number)

        # Read trend parameters for truncation parameters
        zone_model.getTruncationParam(grid_model, realization_number)

        use_constant_probability = zone_model.useConstProb()
        gf_names_for_zone = zone_model.used_gaussian_field_names
        facies_names_for_zone = zone_model.getFaciesInZoneModel()
        num_facies = len(facies_names_for_zone)

        if debug_level >= Debug.VERBOSE:
            for gf_name in gf_names_for_zone:
                print('--- Gauss field parameter used for this zone: ' + gf_name)

        # Get the gauss field parameter name if not already done.
        for gf_name in gf_names_for_zone:
            if not (gf_name in gf_names_already_read):
                gf_names_already_read.append(gf_name)
                if debug_level >= Debug.VERY_VERBOSE:
                    print('Debug output: Gauss field parameter: ' + gf_name + ' is now being loaded.')
                values = getContinuous3DParameterValues(grid_model, gf_name, realization_number, debug_level)
                gf_all_values.append([gf_name, values])

                # Allocate space for transformed gauss field property vector alpha
                gf_name_trans = gf_name + '_transf'
                if isParameterDefinedWithValuesInRMS(grid_model, gf_name_trans, realization_number):
                    if debug_level >= Debug.VERBOSE:
                        print('--- Get transformed gauss field parameter: {} which will be updated'.format(gf_name_trans))
                    alpha = getContinuous3DParameterValues(grid_model, gf_name_trans, realization_number, debug_level)
                else:
                    if debug_level >= Debug.VERBOSE:
                        print('--- Create transformed gauss field parameter: {}'.format(gf_name_trans))
                    alpha = np.zeros(len(values), np.float32)
                gf_all_alpha.append([gf_name_trans, alpha])

                if write_trends_to_rms_for_qc_purpose:
                    # Allocate space for possible trends to write to RMS regardless of whether
                    #  trend is used or not in the model
                    # Note that the trend parameter read contains all grid cell values for all zones
                    #  so even if some zones don't use # this trend, others may use it. It will be read
                    #  only once for the whole grid anyway.
                    gf_name_trend = gf_name + '_trend'

                    # Read 3D RMS parameter containing trend parameter if this parameter exist.
                    #  It will be updated if any trend is created.
                    # Alternatively if it does not exist in RMS, create space for trend as RMS 3D parameters.
                    # Note the RMS 3D parameter for trend values is create only for QC purpose only.
                    if debug_level >= Debug.VERBOSE:
                        print('--- Read and write calculated trends to RMS for QC purpose. ')
                    if isParameterDefinedWithValuesInRMS(grid_model, gf_name_trend, realization_number):
                        if debug_level >= Debug.VERBOSE:
                            print('--- Get RMS parameter: {} which may be updated for QC purpose if trends are used'.format(gf_name_trend))
                        trend = getContinuous3DParameterValues(grid_model, gf_name_trend, realization_number, debug_level)
                    else:
                        trend = np.zeros(len(values), np.float32)
                    gf_all_trend_values.append([gf_name_trend, trend])

            else:
                if debug_level >= Debug.VERY_VERBOSE:
                    print('Debug output: Gauss field parameter: ' + gf_name + ' is already loaded.')

        # For current (zone,region) find the active cells
        cell_index_defined = find_defined_cells(zone_values, zone_number, region_values, region_number, debug_level)
        if debug_level >= Debug.VERBOSE:
            if use_regions:
                print(
                    '--- Number of active cells for (zone,region)=({},{}): {}'
                    ''.format(zone_number, region_number, len(cell_index_defined))
                )
            else:
                print('--- Number of active cells for zone: {}'.format(len(cell_index_defined)))
        if len(cell_index_defined) == 0:
            print(
                'Warning: No active grid cells for (zone,region)=({},{})\n'
                '         Skip this zone, region combination'
                ''.format(zone_number, region_number)
            )
            continue

        # For current zone,transform all gaussian fields used in this zone and update alpha
        index = -999
        gf_alpha_for_current_zone = []
        for gf_name in gf_names_for_zone:
            for j in range(len(gf_all_values)):
                name = gf_all_values[j][NAME]
                if name == gf_name:
                    index = j
                    break
            values = gf_all_values[index][VAL]

            if zone_model.hasTrendModel(gf_name):
                # Add trend to gaussian residual fields
                trend = gf_all_trend_values[index][VAL]

                use_trend, trend_model, rel_std_dev, rel_std_dev_fmu = zone_model.getTrendModel(gf_name)

                if debug_level >= Debug.VERBOSE:
                    trend_type = trend_model.type.name
                    if use_regions:
                        print(
                            '--- Calculate trend for: {} for (zone,region)=({},{})\n'
                            '--- Trend type: {}'
                            ''.format(gf_name, zone_number, region_number, trend_type)
                        )
                    else:
                        print(
                            '--- Calculate trend for: {} for zone: {}\n'
                            '--- Trend type: {}'
                            ''.format(gf_name, zone_number, trend_type)
                        )

                sim_box_thickness = zone_model.getSimBoxThickness()
                # trend_values contain trend values for the cells belonging to the set defined by cell_index_defined
                minmax_difference, trend_values = trend_model.createTrend(
                    grid_model, realization_number, len(cell_index_defined),
                    cell_index_defined, zone_number, sim_box_thickness
                )

                # Calculate trend plus residual for the cells defined by cell_index_defined
                # and replace the residual values by trend + residual in array: values
                sigma = rel_std_dev * minmax_difference
                residual_values = values[cell_index_defined]
                val = trend_values + sigma * residual_values
                # updates array values for the selected grid cells
                values[cell_index_defined] = val
                if debug_level >= Debug.VERY_VERBOSE:
                    print('Debug output: Trend minmax_difference = ' + str(minmax_difference))
                    print('Debug output: SimBoxThickness = ' + str(sim_box_thickness))
                    print('Debug output: RelStdDev = ' + str(rel_std_dev))
                    print('Debug output: Sigma = ' + str(sigma))
                    print('Debug output: Min trend, max trend    : ' + str(trend_values.min()) + ' ' + str(trend_values.max()))
                    print('Debug output: Residual min,max        : ' + str(sigma * residual_values.min()) + ' ' + str(sigma * residual_values.max()))
                    print('Debug output: trend + residual min,max: ' + str(val.min()) + ' ' + str(val.max()))

                if write_trends_to_rms_for_qc_purpose:
                    # Write back to RMS project the untransformed gaussian values with trend for the zone
                    gf_names_untransformed = gf_name + '_untransf'
                    updateContinuous3DParameterValues(
                        grid_model, gf_names_untransformed, values, cell_index_defined, realization_number,
                        isShared=False, setInitialValues=False, debug_level=debug_level
                     )
                    trend = gf_all_trend_values[index][VAL]

                    # update array trend for the selected grid cells
                    trend[cell_index_defined] = trend_values
                    gf_all_trend_values[index][VAL] = trend
                    gf_names_trend = gf_all_trend_values[index][NAME]

                    # Write back to RMS project the trend values for the zone
                    updateContinuous3DParameterValues(
                        grid_model, gf_names_trend, trend, cell_index_defined, realization_number,
                        isShared=False, setInitialValues=False, debug_level=debug_level
                    )
                    if debug_level >= Debug.VERBOSE:
                        if use_regions:
                            print('--- Create or update parameter: {} for (zone,region)= ({},{})'.format(gf_names_trend, zone_number, region_number))
                        else:
                            print('--- Create or update parameter: {} for zone number: {}'.format(gf_names_trend, zone_number))

            alpha = gf_all_alpha[index][VAL]
            # Update alpha for current zone
            if debug_level >= Debug.VERBOSE:
                if use_regions:
                    print('--- Transform: {} for zone: {}'.format(gf_name, zone_number))
                else:
                    print('--- Transform: {} for (zone, region)=({},{})'.format(gf_name, zone_number, region_number))

            alpha = transform_empiric(cell_index_defined, values, alpha)
            gf_all_alpha[index][VAL] = alpha
            gf_names_trans = gf_all_alpha[index][NAME]

            # List of transformed values for each facies for current (zone,region)
            gf_alpha_for_current_zone.append([gf_name, alpha])

            # Write back to RMS project the transformed gaussian values for the zone
            updateContinuous3DParameterValues(
                grid_model, gf_names_trans, alpha, cell_index_defined, realization_number,
                isShared=False, setInitialValues=False, debug_level=debug_level
            )
            if debug_level >= Debug.VERBOSE:
                if use_regions:
                    print('--- Create or update parameter: {} for (zone,region)= ({},{})'.format(gf_names_trans, zone_number, region_number))
                else:
                    print('--- Create or update parameter: {} for zone number: {}'.format(gf_names_trans, zone_number))

        # Get all facies names to be modelled for this zone and corresponding probability parameters
        probability_parameter_values_for_facies = []
        for facies_name in facies_names_for_zone:
            probability_parameter = zone_model.getProbParamName(facies_name)
            if debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: Zone: {}  Facies name: {}  Probability: {}'.format(zone_number, facies_name, probability_parameter))
            values = []
            if use_constant_probability:
                values.append(float(probability_parameter))
                # Add the probability values to a common list containing probabilities for
                # all facies used in the whole model (all zones) to avoid loading the same data multiple times.
                probability_parameter_all_values.append([facies_name, values])

                # Probabilities for each facies for current zone
                probability_parameter_values_for_facies.append([facies_name, values])
            else:
                if not (probability_parameter in probability_parameter_names_already_read):
                    probability_parameter_names_already_read.append(probability_parameter)
                    if debug_level >= Debug.VERY_VERBOSE:
                        print(
                            'Debug output: Probability parameter: {} is now being loaded for facies: {} for zone: {}'
                            ''.format(probability_parameter, facies_name, zone_number)
                        )

                    values = getContinuous3DParameterValues(grid_model, probability_parameter, realization_number, debug_level)

                    # Add the probability values to a common list containing probabilities for
                    # all facies used in the whole model (all zones) to avoid loading the same data multiple times.
                    probability_parameter_all_values.append([facies_name, values])

                    # Probabilities for each facies for current zone
                    probability_parameter_values_for_facies.append([facies_name, values])

                else:
                    if debug_level >= Debug.VERY_VERBOSE:
                        if use_regions:
                            print(
                                'Debug output: Probability parameter: {} '
                                'is already loaded for facies: {} for (zone,region)=({},{})'
                                ''.format(probability_parameter, facies_name, zone_number, region_number)
                            )
                        else:
                            print(
                                'Debug output: Probability parameter: {} is already loaded for facies: {} for zone: {}'
                                ''.format(probability_parameter, facies_name, zone_number)
                            )

                    index = -999
                    # Get the probability values from the common list since it already is loaded
                    for i in range(len(probability_parameter_all_values)):
                        name = probability_parameter_all_values[i][NAME]
                        if facies_name == name:
                            index = i
                            break
                    # Probabilities for each facies for current zone
                    values = probability_parameter_all_values[index][VAL]
                    probability_parameter_values_for_facies.append([facies_name, values])

        # end for

        # Check and normalise probabilities if necessary for current zone
        if debug_level >= Debug.VERBOSE:
            print('--- Check normalisation of probability fields.')
        probability_defined, num_cells_modified_probability = check_and_normalise_probability(
            num_facies, probability_parameter_values_for_facies, use_constant_probability, cell_index_defined,
            eps, tolerance_of_probability_normalisation, debug_level
        )
        if debug_level >= Debug.VERBOSE:
            print('--- Number of cells that are normalised: ' + str(num_cells_modified_probability))

            # Facies realisation for current zone is updated.
            if debug_level >= Debug.VERBOSE:
                print('--- Truncate transformed Gaussian fields.')

        facies_real, volume_fraction = zone_model.applyTruncations(
            probability_defined, gf_alpha_for_current_zone, facies_real, len(cell_index_defined), cell_index_defined
        )

        if debug_level >= Debug.VERBOSE:
            print('')
            main_facies_table = aps_model.getMainFaciesTable()
            if use_constant_probability:
                if use_regions:
                    print(
                        '--- Zone_number:  Region_number:    Facies_code:   Facies_name:'
                        '     Volumefraction_specified:    Volumefracion_realisation:'
                    )
                    for f in range(len(facies_names_for_zone)):
                        facies_name = facies_names_for_zone[f]
                        facies_code = main_facies_table.getFaciesCodeForFaciesName(facies_name)
                        item = probability_parameter_values_for_facies[f]
                        if facies_name != item[NAME]:
                            raise ValueError('Inconsistencies in data structure in APS_main')

                        probabilities = item[VAL]
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
                        if facies_name != item[NAME]:
                            raise ValueError('Inconsistencies in data structure in APS_main')

                        probabilities = item[VAL]
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
                        if facies_name != item[NAME]:
                            raise ValueError('Inconsistencies in data structure in APS_main')

                        values = item[VAL]
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
                        if facies_name != item[NAME]:
                            raise ValueError('Inconsistencies in data structure in APS_main')

                        values = item[VAL]
                        average_probabilities = calc_average(cell_index_defined, values)
                        print('{0:4d} {1:4d}  {2:10}  {3:.3f}   {4:.3f}'.format(
                            zone_number, facies_code, facies_name, volume_fraction[f], average_probabilities)
                        )

        for facies_name in facies_names_for_zone:
            if facies_name not in all_facies_names_modelled:
                all_facies_names_modelled.append(facies_name)
                if debug_level >= Debug.VERY_VERBOSE:
                    print('Debug: Add facies: ' + facies_name + ' to the list of modelled facies')

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
        text = 'Debug output: Facies codes and names before merging with existing facies table for facies realisation:'
        print(text)
        print(repr(code_names))

    # Write facies realisation back to RMS project for all zones that is modelled.
    if debug_level >= Debug.VERBOSE:
        if aps_model.isAllZoneRegionModelsSelected():
            print('Debug output: All combinations of zone and region is selected to be run')
        else:
            print('--- The following (zone,region) numbers are updated in facies realization:')
            for key, zone_model in all_zone_models.items():
                zone_number = key[0]
                region_number = key[1]
                if not aps_model.isSelected(zone_number, region_number):
                    continue
                if use_regions:
                    print('    (zone,region)=({},{})'.format(key[0], key[1]))
                else:
                    print('    zone={}'.format(key[0]))

    # Overwrite the existing facies realization, but note that now the facies_real should contain values
    # equal to the original facies realization for all cells that is not updated
    #  (not belonging to (zones, regions) that is updated)
    updateDiscrete3DParameterValues(
        grid_model, result_param_name, facies_real, faciesTable=code_names,
        realNumber=realization_number, isShared=False, setInitialValues=False,
        debug_level=Debug.OFF
    )
    if debug_level >= Debug.SOMEWHAT_VERBOSE:
        print('- Create or update parameter: ' + result_param_name)

    print('')
    if debug_level >= Debug.SOMEWHAT_VERBOSE:
        print('- Updated facies table:')
        p = get3DParameter(grid_model, result_param_name)
        print('- Facies_name   Facies_code')
        for key in p.code_names:
            u = p.code_names.get(key)
            print('  {0:10}  {1:3d}'.format(u, key))

        print('')
    print('Finished APS_main.py')


# --------------- Start main script ------------------------------------------
if __name__ == '__main__':
    import roxar
    run(roxar, project)
