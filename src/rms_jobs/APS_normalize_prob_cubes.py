#!/bin/env python
# -*- coding: utf-8 -*-
import numpy as np

from src.algorithms.APSModel import APSModel
from src.utils.constants.simple import Debug, ProbabilityTolerances
from src.utils.methods import get_specification_file
from src.utils.roxar.generalFunctionsUsingRoxAPI import set_continuous_3d_parameter_values
from src.utils.roxar.grid_model import (
    getContinuous3DParameterValues,
    getDiscrete3DParameterValues,
    find_defined_cells,
    create_zone_parameter,
)
from src.utils.checks import check_probability_values, check_probability_normalisation


class NormalisationError(ValueError):
    pass


def check_and_normalise_probability(
        probability_values_per_rms_param,
        zone_model,
        cell_index_defined,
        tolerance_of_probability_normalisation=0.1,
        eps=0.001,
        debug_level=Debug.OFF,
        max_tolerance=ProbabilityTolerances.MAX_ALLOWED_FRACTION_OF_VALUES_OUTSIDE_TOLERANCE,
        grid_model=None,
        realization_number=0,
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
    :param realization_number:
    :type realization_number: int
    :param grid_model:
    :type grid_model: GridModel
    :param zone_model:
    :type zone_model: APSZoneModel
    :param probability_values_per_rms_param: dictionary where the key is rms parameter name and the value is a numpy vector
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
    :param max_tolerance: float
    :return: integer with number of grid cells for which the probabilities are re-calculated to be normalised.
    """
    # RMS probability parameter names for each facies
    # list of facies names for a specific zone or (zone, region) combination
    facies_names_for_zone = zone_model.facies_in_zone_model
    # dictionary where the key is facies_name, and the value is rms parameter name for the probabilities for this facies
    probability_parameter_per_facies = {
        facies_name: zone_model.getProbParamName(facies_name)
        for facies_name in facies_names_for_zone
    }

    sum_probabilities_selected_cells = np.zeros(len(cell_index_defined), np.float32)
    num_cell_with_modified_probability = 0

    # Check that probability values are in interval [0,1]
    for facies_name in facies_names_for_zone:
        parameter_name = probability_parameter_per_facies[facies_name]

        # All grid cells (active cells in the grid)
        all_values = probability_values_per_rms_param[parameter_name]

        # The cells belonging to the zone,region as defined by the input cell_index_defined array
        probabilities_selected_cells = all_values[cell_index_defined]

        # Check probability values, ensure that they are in the interval [0,1]. If outside this interval,
        # they are set to 0 if negative or 1 if above 1, but error message if too large fraction of grid cells have
        # value outside the tolerance specified.
        probabilities_selected_cells = check_probability_values(
            probabilities_selected_cells, tolerance_of_probability_normalisation,
            facies_name, parameter_name
        )

        # Sum up probability over all facies per selected cell
        all_values[cell_index_defined] = probabilities_selected_cells
        sum_probabilities_selected_cells += probabilities_selected_cells
        probability_values_per_rms_param[parameter_name] = all_values

    if (sum_probabilities_selected_cells == 0).any():
        name = 'APS_problematic_cells_in_probability_cubes'
        set_continuous_3d_parameter_values(
            grid_model,
            name,
            input_values=sum_probabilities_selected_cells == 0,
            realisation_number=realization_number,
            debug_level=debug_level,
        )
        parameter_names = format_names(probability_parameter_per_facies.values())
        raise NormalisationError(
            f'The probability cubes {parameter_names}, in zone {zone_model.zone_number}, '
            f'have some areas with 0 cumulative probability. '
            f'These areas are shown in {name}.'
        )

    # Check normalisation and report error if input probabilities are too far from 1.0
    normalise_is_necessary = check_probability_normalisation(
        sum_probabilities_selected_cells, eps, tolerance_of_probability_normalisation,
        max_tolerance,
    )
    if normalise_is_necessary:
        # Normalize
        psum = sum_probabilities_selected_cells

        for ii, facies_name in enumerate(facies_names_for_zone):
            parameter_name = probability_parameter_per_facies[facies_name]
            all_values = probability_values_per_rms_param[parameter_name]
            p = all_values[cell_index_defined]
            if ii == 0:
                check_value = (psum > (1.0 + eps)) | (psum < (1.0 - eps))
                num_cell_with_modified_probability = check_value.sum()

            # Normalize
            p = p / psum

            # The cells belonging to the zone,region as defined by the input cell_index_defined array
            # is updated by normalised values
            all_values[cell_index_defined] = p
            probability_values_per_rms_param[parameter_name] = all_values

    return num_cell_with_modified_probability, probability_values_per_rms_param


def format_names(names):
    parameter_names = ''
    n = len(names)
    for ii, probability_cube in enumerate(names):
        parameter_names += f"'{probability_cube}'"

        if ii < n - 2:
            parameter_names += ', '
        elif ii == n - 2:
            parameter_names += ', and '
        elif ii == n - 1:
            # The last item does not have a comma after it
            pass
    return parameter_names


def check_and_normalize_probabilities_for_APS(
        project,
        model_file,
        tolerance_of_probability_normalisation,
        eps,
        overwrite,
        max_tolerance=ProbabilityTolerances.MAX_ALLOWED_FRACTION_OF_VALUES_OUTSIDE_TOLERANCE,
):
    # Read APS model
    print(f'- Read file: {model_file}')
    aps_model = APSModel(model_file)
    debug_level = aps_model.debug_level
    grid_model_name = aps_model.grid_model_name
    grid_model = project.grid_models[grid_model_name]

    zone_param_name = aps_model.getZoneParamName()
    region_param_name = aps_model.getRegionParamName()

    realization_number = project.current_realisation

    # Read zone parameter from RMS
    assert zone_param_name is not None
    zone_param = create_zone_parameter(
        grid_model,
        name=zone_param_name,
        realization_number=realization_number,
        set_shared=False,
        debug_level=debug_level,
    )
    zone_values = zone_param.get_values(realization_number)

    # Read region parameter from RMS
    region_values = None
    if region_param_name:
        region_values, _ = getDiscrete3DParameterValues(grid_model, region_param_name, realization_number)

    # Get list of all zone models
    all_zone_models = aps_model.sorted_zone_models

    # Get all probability parameter names
    probability_parameter_names = aps_model.getAllProbParam()

    # Probability values for each RMS parameter
    probability_values_per_rms_param = {
        parameter_name: getContinuous3DParameterValues(grid_model, parameter_name, realization_number)
        for parameter_name in probability_parameter_names
    }

    # Loop over all pairs of (zone_number, region_number) that is specified and selected
    # Check and normalize the probabilities for each (zone, region) model
    for key, zone_model in all_zone_models.items():
        zone_number, region_number = key
        if not aps_model.isSelected(zone_number, region_number):
            continue

        if zone_model.useConstProb():
            # No probability cubes for this (zone, region)
            continue

        # For current (zone,region) find the active cells
        cell_index_defined = find_defined_cells(zone_values, zone_number, region_values, region_number, debug_level)
        if len(cell_index_defined) == 0:
            print(
                f'Warning: No active grid cells for (zone,region)=({zone_number}, {region_number})\n'
                '         Skip this zone, region combination'
            )
            continue

        # Update contents in probability_values_per_rms_param
        num_cells_modified_probability, probability_values_per_rms_param = check_and_normalise_probability(
            probability_values_per_rms_param,
            zone_model,
            cell_index_defined,
            tolerance_of_probability_normalisation,
            eps,
            debug_level,
            max_tolerance,
            grid_model,
            realization_number,
        )
        # Write back to RMS project updated probabilities if necessary
        if debug_level >= Debug.ON:
            print(
                f'--- Number of cells that are normalised for (zone,region)=({zone_number}, {region_number}) '
                f'are {num_cells_modified_probability} of {len(cell_index_defined)} cells.'
            )

    # End loop over zones

    for parameter_name in probability_parameter_names:
        parameter_values = probability_values_per_rms_param[parameter_name]

        if not overwrite:
            parameter_name = parameter_name + '_norm'
        zone_number_list = []
        if not set_continuous_3d_parameter_values(grid_model, parameter_name, parameter_values, zone_number_list, realization_number, is_shared=True):
            raise IOError(f'Can not update parameter {parameter_name}')
        else:
            if debug_level >= Debug.ON:
                print(f'--- Updated probability cube: {parameter_name}')


def run(
        project,
        eps=ProbabilityTolerances.MAX_DEVIATION_BEFORE_ACTION,
        tolerance_of_probability_normalisation=ProbabilityTolerances.MAX_ALLOWED_DEVIATION_BEFORE_ERROR,
        overwrite=True,
        max_allowed_fraction_of_values_outside_tolerance=ProbabilityTolerances.MAX_ALLOWED_FRACTION_OF_VALUES_OUTSIDE_TOLERANCE,
        **kwargs
):
    real_number = project.current_realisation
    print(f'Run: APS_normalize_prob_cubes on realisation {real_number + 1}')
    model_file = get_specification_file(**kwargs)

    check_and_normalize_probabilities_for_APS(
        project,
        model_file,
        tolerance_of_probability_normalisation,
        eps,
        overwrite,
        max_allowed_fraction_of_values_outside_tolerance,
    )
    print('Finished APS_normalize_prob_cubes')
