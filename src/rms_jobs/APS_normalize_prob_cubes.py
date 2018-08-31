#!/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
from src.algorithms.APSModel import APSModel
from src.utils.constants.simple import Debug, ProbabilityTolerances
from src.utils.methods import get_model_file_name
from src.utils.roxar.grid_model import (
    getContinuous3DParameterValues,  getDiscrete3DParameterValues,
    find_defined_cells,
)
from src.utils.roxar.generalFunctionsUsingRoxAPI import  setContinuous3DParameterValues
import src.utils.roxar.generalFunctionsUsingRoxAPI

def check_and_normalise_probability(
    probability_values_per_rms_param, 
    probability_parameter_per_facies, 
    facies_names_for_zone, 
    cell_index_defined,
    tolerance_of_probability_normalisation = 0.1,
    eps = 0.001,
    debug_level=Debug.ON
    ):
    """
    Check that probability values are valid probabilities.
    If the probabilities are not normalised, but the deviation from 1.0 for the 
    sum of probabilities are relatively close to 1.0 
    (as defined by the tolerance_of_probability_normalisation), the values are 
    normalised. If the sum of probabilities are larger than the tolerance,
    an error message is raised. If the sum of probabilities are closer to 1.0 
    than the value in input variable eps, nothing is done. 
    If the sum of input probabilities are between eps and 
    tolerance_of_probability_normalisation, then the probabilities are normalised.

    The list cell_index_defined is an index vector. The length is in general less than
    the total number of active cells for the grid. Typically the
    cell_index_defined vector represents active cells belonging to a specified
    zone or zone and region combination, but could in principle be any subset of interest 
    of the total set of all active cells. The content of the cell_index_defined array is indices in
    vectors containing all active cells and is a way of defining a subset of cells.
    :param probability_values_per_rms_param: dictionary where the key is rms parameter name and the value is a numpy vector
    :param probability_parameter_per_facies: dictionary where the key is facies_name and the value is rms parameter name 
                                             for the probabilities for this facies.
    :param facies_names_for_zone: list of facies names for a specific zone or (zone,region) combination.
    :param cell_index_defined: list of indices for the grid cells that are selected (belongs to a specific zone or (zone,region) combination.
    :param tolerance_of_probability_normalisation: float variable with maximum difference between sum of input probabilities and 1.0 
                                                   that is accepted before error is raised. It is also used as a tolerance for 
                                                   how much larger than 1.0 the input probability can be without raising an error or 
                                                   how large negative an input probability can be without raising an error. 
                                                   In any case if an input probability is less than 0 it is set to 0 and 
                                                   if it is larger than 1.0 it is set to 1.0.
    :param eps: float variable which define maximum difference between sum of input probabilities and 1.0 that is accepted 
                without having to do any normalisation.
    :param debug_level: Define output print level from the function.
    :return: integer with number of grid cells for which the probabilities are re-calculated to be normalised.
    """
    num_defined_cells = len(cell_index_defined)
    probabilities_selected_cells = np.zeros(num_defined_cells, np.float32)
    sum_probabilities_selected_cells = np.zeros(num_defined_cells, np.float32)
    num_cell_with_modified_probability = 0

    # Check that probability values are in interval [0,1]
    for facies_name in facies_names_for_zone:
        parameter_name = probability_parameter_per_facies[facies_name]

        # All grid cells (active cells in the grid)
        all_values = probability_values_per_rms_param[parameter_name]

        # The cells  belonging to the zone,region as defined by the input cell_index_defined array
        probabilities_selected_cells = all_values[cell_index_defined]
        num_negative = 0
        num_above_one = 0
        for i in range(num_defined_cells):
            v = probabilities_selected_cells[i]
            if v < -tolerance_of_probability_normalisation:
                num_negative += 1
                probabilities_selected_cells[i] = 0.0
            elif v < 0.0:
                probabilities_selected_cells[i] = 0.0
            elif v > 1.0 + tolerance_of_probability_normalisation:
                num_above_one += 1
                probabilities_selected_cells[i] = 1.0
            elif v > 1.0:
                probabilities_selected_cells[i] = 1.0
        if num_defined_cells > 0:
            negative_fraction = float(num_negative)/float(num_defined_cells)
            above_one_fraction = float(num_above_one)/float(num_defined_cells)
            if negative_fraction > 0.1:
                raise ValueError(
                    'Probability for facies {} in {} has {} negative values.'
                    ''.format(facies_name, parameter_name, num_negative)
                    )
            if above_one_fraction > 0.1:
                raise ValueError(
                    'Probability for facies {} in {} has {} values above 1.0'
                    ''.format(facies_name, parameter_name, num_above_one)
                    )
        # Sum up probability over all facies per selected cell
        all_values[cell_index_defined] = probabilities_selected_cells
        sum_probabilities_selected_cells += probabilities_selected_cells
        probability_values_per_rms_param[parameter_name] = all_values
    # Check normalisation and report error if input probabilities are too far from 1.0
    
    ones = np.ones(num_defined_cells, np.float32)

    if not np.allclose(sum_probabilities_selected_cells, ones, eps):
        unacceptable_prob_normalisation = 0
        min_acceptable_prob_sum = 1.0 - tolerance_of_probability_normalisation
        max_acceptable_prob_sum = 1.0 + tolerance_of_probability_normalisation
        for i in range(num_defined_cells):
            if not (min_acceptable_prob_sum <= sum_probabilities_selected_cells[i] <= max_acceptable_prob_sum):
                    unacceptable_prob_normalisation += 1

        unacceptable_prob_normalisation_fraction = float(unacceptable_prob_normalisation)/float(num_defined_cells)
        if unacceptable_prob_normalisation_fraction > 0.1:
            largest_prob_sum = 0.0
            smallest_prob_sum = 1.0
            for i in range(num_defined_cells):
                if smallest_prob_sum > sum_probabilities_selected_cells[i]:
                    smallest_prob_sum = sum_probabilities_selected_cells[i]
                if largest_prob_sum < sum_probabilities_selected_cells[i]:
                    largest_prob_sum = sum_probabilities_selected_cells[i]
            raise ValueError(
                'Sum of input facies probabilities is either less than: {} or larger than: {} in: {} cells.\n'
                'Input probabilities should be normalised and the sum close to 1.0 but found a minimum value of: {} and a maximum value of: {}\n'
                'Check input probabilities!'
                    ''.format(min_acceptable_prob_sum, max_acceptable_prob_sum, unacceptable_prob_normalisation, smallest_prob_sum, largest_prob_sum)
                )

        # Normalize
        psum = sum_probabilities_selected_cells
        p = np.zeros(num_defined_cells, np.float32)
    
        for f in range(len(facies_names_for_zone)):
            facies_name = facies_names_for_zone[f]
            parameter_name = probability_parameter_per_facies[facies_name]
            all_values = probability_values_per_rms_param[parameter_name]
            p = all_values[cell_index_defined]

            for i in range(num_defined_cells):
                if np.abs(psum[i] - 1.0) > eps:
                    # Have to normalize
                    if f == 0:
                        num_cell_with_modified_probability += 1
                    p[i] = p[i] / psum[i]
            

            # The cells  belonging to the zone,region as defined by the input cell_index_defined array
            # is updated by normalised values
            all_values[cell_index_defined] = p
            probability_values_per_rms_param[parameter_name] = all_values

    return num_cell_with_modified_probability, probability_values_per_rms_param


def check_and_normalize_probabilities_for_APS(project, model_file, tolerance_of_probability_normalisation, eps, overwrite):

    # Read APS model
    print('- Read file: ' + model_file)
    aps_model = APSModel(model_file)
    debug_level = aps_model.debug_level
    grid_model_name = aps_model.getGridModelName()
    grid_model = project.grid_models[grid_model_name]
    grid = grid_model.get_grid()

    zone_param_name = aps_model.getZoneParamName()
    region_param_name = aps_model.getRegionParamName()

    realization_number = project.current_realisation

    # Read zone parameter from RMS
    assert zone_param_name is not None
    zone_values, _ = getDiscrete3DParameterValues(grid_model, zone_param_name, realization_number)

    # Read region parameter from RMS
    region_values = None
    if region_param_name != '':
        region_values, _ = getDiscrete3DParameterValues(grid_model, region_param_name, realization_number)

    # Get list of all zone models
    all_zone_models = aps_model.sorted_zone_models

    # Get all probability parameter names
    probability_parameter_names = aps_model.getAllProbParam()

    # Probability values for each RMS parameter
    probability_values_per_rms_param = {}


    for parameter_name in probability_parameter_names:
        parameter_values = getContinuous3DParameterValues(grid_model, parameter_name, realization_number)
        probability_values_per_rms_param[parameter_name] = parameter_values

    # Loop over all pairs of (zone_number, region_number) that is specified and selected
    # Check and normalize the probabilities for each (zone,region) model
    for key, zone_model in all_zone_models.items():
        zone_number = key[0]
        region_number = key[1]
        if not aps_model.isSelected(zone_number, region_number):
            continue

        use_constant_probability = zone_model.useConstProb()
        if use_constant_probability:
            # No probability cubes for this (zone,region)
            continue

        # RMS probability parameter names for each facies
        probability_parameter_per_facies = {}
        facies_names_for_zone = zone_model.getFaciesInZoneModel()
        for facies_name in facies_names_for_zone:
            probability_parameter_per_facies[facies_name] = zone_model.getProbParamName(facies_name)

        # For current (zone,region) find the active cells
        cell_index_defined = find_defined_cells(zone_values, zone_number, region_values, region_number, debug_level=Debug.OFF)
        if len(cell_index_defined) == 0:
            print(
                'Warning: No active grid cells for (zone,region)=({},{})\n'
                '         Skip this zone, region combination'
                ''.format(zone_number, region_number)
            )
            continue

        # Update contents in probability_values_per_rms_param
        num_cells_modified_probability, probability_values_per_rms_param = check_and_normalise_probability(probability_values_per_rms_param, 
                                                                                                           probability_parameter_per_facies, 
                                                                                                           facies_names_for_zone, cell_index_defined,
                                                                                                           tolerance_of_probability_normalisation, 
                                                                                                           eps, debug_level)
        # Write back to RMS project updated probabilities if necessary
        if debug_level >= Debug.ON:
            print('--- Number of cells that are normalised for (zone,region)=({},{}) are {} of {} cells.'
                  ''.format(zone_number, region_number, num_cells_modified_probability, len(cell_index_defined)))


    # End loop over zones
            

    for parameter_name in probability_parameter_names:
        parameter_values = probability_values_per_rms_param[parameter_name]

        if not overwrite:
            parameter_name = parameter_name + '_norm'
        zone_number_list = []
        if not setContinuous3DParameterValues(grid_model, parameter_name, parameter_values, zone_number_list, 
                                              realization_number, isShared=True, debug_level=Debug.OFF):
            raise IOError('Can not update parameter {}'.format(parameter_name))
        else:
            if debug_level>= Debug.ON:
                print('--- Updated probability cube: {}'.format(parameter_name))



def run(roxar=None, project=None,
        eps=ProbabilityTolerances.MAX_DEVIATION_BEFORE_ACTION,
        tolerance_of_probability_normalisation=ProbabilityTolerances.MAX_ALLOWED_DEVIATION_BEFORE_ERROR,
        overwrite = True,
        **kwargs
):
    real_number = project.current_realisation
    print('Run: APS_normalize_prob_cubes  on realisation ' + str(real_number + 1))
    model_file = get_model_file_name(**kwargs)
    check_and_normalize_probabilities_for_APS(project, model_file, tolerance_of_probability_normalisation, eps, overwrite)
    print('Finished APS_normalize_prob_cubes')


if __name__ == '__main__':
    import roxar
    run(roxar, project)
