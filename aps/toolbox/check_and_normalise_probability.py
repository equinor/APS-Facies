#!/bin/env python
# -*- coding: utf-8 -*-
"""
Description:
    The purpose of this script is to check that specified facies probability parameters are normalized,
    which means that for each active grid cell in a given zone and region, the sum of the facies probabilities sum up to 1.
    The script can accept deviations from 1.0 for the sum within specified tolerances and for a
    specified maximum fraction of the grid cells in the zone (and region).
    The method is as follows:
    - Loop over all specified zones or (zone, region) combinations
    - Get the active cells for the specified zone or (zone, region) combination.
    - Sum over the specified facies for the given zone or (zone, region) combination.
    - Check that individual probabilities for the facies are between 0 and 1
    - If the fraction of number of grid cells with probabilities outside inteval [-tolerance, 1+ tolerance]
      is larger than specified max allowed fraction, then error message is generated.
    - Truncate the probabilities such that prob < 0 is set to 0 and prob > 1 is set to 1.
    - Check that the sum of probabilities are within the interval [1-tolerance, 1+tolerance]
    - Count the number of grid cells that violates the tolerance.
    - Calculate the fraction of grid cells having sum of probabilities violating the tolerance.
    - Raise value error if the fraction of grid cells violating the tolerance is larger than
      a specified fraction.
    - Check also if some grid cells have sum of probabilities equal to 0. For these grid cells
      create a 3D parameter with value 1 for these grid cells and report the
      number of such grid cells.
    - If all these tests are successfully completed, and if there are need for normalization
      the probabilities are normalized cell by cell by dividing each facies probability
      by the sum of facies probabilities.

    The script take a dictionary as input. It is possible to run the script by:
    - specify aps_model_file as input. In this case no other specification of input is necessary.
      The aps_model_file must then be an export from the APSGUI job that will use the facies probabilities.
    - specify for each zone  or (zone, region) combination which facies to use
      and which 3D parameter with facies probabilities belongs to each of the facies. Furthermore, specify
      tolerance criteria, grid model name, region parameter name. If the user wants to use this script
      to calculate the normalization without tolerance restrictions, it can be done by specifying that
      it is allowed to have a 100% fraction of grid cells violating normalization tolerance.

    Output:
    - The user can specify either to overwrite or create new 3D parameters with normalized probabilities.

    Three examples of use:

    # -------------------------------------------------------------------------------------------
    # Example 1: Use APS model file as input.
    #            Only the keys: project, aps_model_file is required here and the other parameters
    #            in this example have default values and can be ommited.

    from aps.toolbox import check_and_normalise_probability
    from aps.utils.constants.simple import Debug

    # Define input parameters
    input_dict = {
        "project": project,
        "aps_model_file": "APS.xml",
        "overwrite":  False,
        "debug_level":  Debug.VERBOSE,
        "tolerance_of_probability_normalisation": 0.15,
        "max_allowed_fraction_of_values_outside_tolerance": 0.03,
    }

    check_and_normalise_probability.run(input_dict)
    # ----------------------------------------------------------------

    # Example 2: The specification is done directly not using the APS model file.
    #            In this example, the APS job that will use the facies probability parameters
    #            has specified a model per zone. No regions are used.

    from aps.toolbox import check_and_normalise_probability
    from aps.utils.constants.simple import Debug

    # Define input parameters

    # Modelled facies for each zone can vary
    # The probabilities are specified for 2 zones.
    # The keys for this dictionary is the zone number.
    modelling_facies_per_zone_dict = {
        1: ["F1", "F2", "F3"],
        2: ["F1", "F2"],
    }

    # For each facies, name of the 3D probability parameter is specified.
    # Note that specification of probabilities for all zones are saved in
    # the same 3D facies probability parameter.
    prob_param_names_dict = {
        "F1": "Prob_F1",
        "F2": "Prob_F2",
        "F3": "Prob_F3",
    }

    # The main input dictionary
    # Note that in this example the key 'modelling_facies_per_zone' is used.
    input_dict = {
        "project": project,
        "grid_model_name":  "GridModelFine",
        "modelling_facies_per_zone":  modelling_facies_per_zone_dict,
        "prob_param_per_facies": prob_param_names_dict,
        "overwrite":  False,
        "debug_level":  Debug.VERBOSE,
        "tolerance_of_probability_normalisation": 0.15,
        "max_allowed_fraction_of_values_outside_tolerance": 0.05
    }

    check_and_normalise_probability.run(input_dict)

    # ---------------------------------------------------------------------------------------
    # Example 3:  The specification is done directly not using the APS model file.
    #             In this example, the APS job that will use the facies probability parameters
    #             has specified a model per zone and region.

    from aps.toolbox import check_and_normalise_probability
    from aps.utils.constants.simple import Debug

    # Define input parameters

    # Modelled facies for each zone and region combination can vary
    # The probabilities are specified for 2 zones where both zones have 4 regions
    # The keys for this dictionary is a tuple (zone_number, region_number)
    modelling_facies_per_zone_region_dict = {
        (1,1): ["F1", "F2", "F3"],
        (1,2): ["F1", "F3"],
        (1,3): ["F2", "F3",],
        (1,4): ["F1", "F2", "F3"],
        (2,1): ["F1", "F2"],
        (2,2): ["F1", "F3"],
        (2,3): ["F2", "F3"],
        (2,4): ["F1", "F2", "F3"],

    }
    # For each facies, name of the 3D probability parameter is specified.
    # Note that specification of probabilities for all zone, region combinations
    # are saved in the same 3D facies probability parameter.
    prob_param_names_dict = {
        "F1": "Prob_zone_region_F1",
        "F2": "Prob_zone_region_F2",
        "F3": "Prob_zone_region_F3",
    }

    # The main input dictionary
    # Note that in this example the key 'modelling_facies_per_zone_region' and 'region_param_name'
    # is used.
    input_dict = {
        "project": project,
        "grid_model_name":  "GridModelFine",
        "region_param_name": "DiscreteParam",
        "modelling_facies_per_zone_region":  modelling_facies_per_zone_region_dict,
        "prob_param_per_facies": prob_param_names_dict,
        "overwrite":  False,
        "debug_level":  Debug.VERBOSE,
        "tolerance_of_probability_normalisation": 0.15,
        "max_allowed_fraction_of_values_outside_tolerance": 0.05
    }

    check_and_normalise_probability.run(input_dict)

"""

import numpy as np
import roxar
from roxar.grids import GridModel

from aps.utils.constants.simple import Debug, ProbabilityTolerances, GridModelConstants
from aps.utils.roxar.generalFunctionsUsingRoxAPI import (
    set_continuous_3d_parameter_values,
    set_discrete_3d_parameter_values,
)
from aps.utils.roxar.grid_model import (
    getContinuous3DParameterValues,
    getDiscrete3DParameterValues,
    find_defined_cells,
    create_zone_parameter,
)
from aps.utils.checks import check_probability_values, check_probability_normalisation
from aps.utils.methods import check_missing_keywords_list, check_missing_keywords_dict


class NormalisationError(ValueError):
    pass


def run(params):
    """
    Check normalization of input facies probabilities and normalize them if not normalized.
    """
    project = params.get('project', None)
    if project is None:
        raise ValueError(f"Missing specification of the project variable in 'params' ")

    real_number = project.current_realisation
    print(
        f'Check normalisation of facies probabilities for realisation {real_number + 1}'
    )

    defined_keywords = [
        'project',
        'debug_level',
        'aps_model_file',
        'modelling_facies_per_zone',
        'modelling_facies_per_zone_region',
        'grid_model_name',
        'region_param_name',
        'prob_param_per_facies',
        'overwrite',
        'tolerance_of_probability_normalisation',
        'max_allowed_fraction_of_values_outside_tolerance',
        'stop_on_error',
        'report_zone_regions',
    ]

    if 'aps_model_file' not in params:
        # Check that necessary input is specified in params
        if 'region_param_name' in params:
            # Require that facies is specified per ( zone, region) pair
            keyword = 'modelling_facies_per_zone_region'
            if keyword not in params:
                raise ValueError(
                    f'Missing keyword: {keyword}. Required when using regions.'
                )
        else:
            # Require that facies is specified per zone
            keyword = 'modelling_facies_per_zone'
            if keyword not in params:
                raise ValueError(
                    f'Missing keyword: {keyword}. Required when not using regions.'
                )

        # Check that other required keywords exists
        keywords_required = [
            'grid_model_name',
            'prob_param_per_facies',
        ]
        check_missing_keywords_list(params, keywords_required)

    unknown_keywords = []
    keys = list(params.keys())
    for key in keys:
        if key not in defined_keywords:
            unknown_keywords.append(key)
    if len(unknown_keywords) > 0:
        raise ValueError(
            f'Unknown keywords used: {unknown_keywords}.\nRemove unknown keyword '
        )

    check_and_normalize_probabilities_for_APS(project, params)
    print('Finished normalization of facies probabilities')


def check_and_normalize_probabilities_for_APS(
    project,
    params,
):
    aps_model_file_name = params.get('aps_model_file', None)
    debug_level = params.get('debug_level', Debug.OFF)
    realization_number = project.current_realisation
    facies_per_zone_dict = None
    facies_per_zone_region_dict = None
    region_values = None
    prob_params_per_facies = {}

    if aps_model_file_name is not None:
        # Use APS model file as input to get facies per zone (and region) and probability parameters
        (
            grid_model,
            use_regions,
            facies_per_zone_dict,
            facies_per_zone_region_dict,
            prob_params_per_facies,
            probability_parameter_names,
            zone_values,
            region_values,
        ) = get_params_from_aps_model(
            project, aps_model_file_name, realization_number, debug_level=debug_level
        )

    else:
        # Get all parameters from input dict
        (
            grid_model,
            use_regions,
            facies_per_zone_dict,
            facies_per_zone_region_dict,
            prob_params_per_facies,
            probability_parameter_names,
            zone_values,
            region_values,
        ) = get_input_params(project, params, realization_number)

    max_prob_norm_tolerance = params.get(
        'tolerance_of_probability_normalisation',
        ProbabilityTolerances.MAX_ALLOWED_DEVIATION_BEFORE_ERROR,
    )
    max_allowed_fraction = params.get(
        'max_allowed_fraction_of_values_outside_tolerance',
        ProbabilityTolerances.MAX_ALLOWED_FRACTION_OF_VALUES_OUTSIDE_TOLERANCE,
    )
    min_prob_norm_tolerance = ProbabilityTolerances.MAX_DEVIATION_BEFORE_ACTION

    overwrite = params.get('overwrite', False)
    stop_on_error = params.get('stop_on_error', True)

    # Probability values for each RMS parameter
    probability_values_per_rms_param = {
        parameter_name: getContinuous3DParameterValues(
            grid_model, parameter_name, realization_number
        )
        for parameter_name in probability_parameter_names
    }

    if use_regions:
        facies_dict = facies_per_zone_region_dict
    else:
        facies_dict = facies_per_zone_dict
    assert facies_dict is not None
    # Loop over all pairs of (zone_number, region_number) that is specified and selected
    # Check and normalize the probabilities for each (zone, region) model
    probability_values_per_rms_param = check_and_normalize_all_zones(
        facies_dict,
        zone_values,
        region_values,
        grid_model,
        realization_number,
        use_regions,
        probability_values_per_rms_param,
        prob_params_per_facies,
        max_prob_norm_tolerance,
        min_prob_norm_tolerance,
        max_allowed_fraction,
        debug_level,
        stop_on_error=stop_on_error,
    )

    # Write back to RMS project updated probabilities if necessary
    for parameter_name in probability_parameter_names:
        parameter_values = probability_values_per_rms_param[parameter_name]

        if not overwrite:
            parameter_name = parameter_name + '_norm'
        zone_number_list = []
        is_shared = grid_model.shared
        update_successful = set_continuous_3d_parameter_values(
            grid_model,
            parameter_name,
            parameter_values,
            zone_number_list,
            realization_number,
            is_shared=is_shared,
        )
        if not update_successful:
            raise IOError(f'Can not update parameter {parameter_name}')
        else:
            if debug_level >= Debug.ON:
                print(f'- Updated probability cube: {parameter_name}')

    return


def get_params_from_aps_model(
    project,
    aps_model_file_name: str,
    realization_number: int,
    debug_level: Debug = Debug.OFF,
):
    # Use APS model file as input to get facies per zone (and region) and probability parameters
    from aps.algorithms.APSModel import APSModel

    if debug_level >= Debug.ON:
        print(f'- Read file: {aps_model_file_name}')
    aps_model = APSModel(aps_model_file_name)
    grid_model_name = aps_model.grid_model_name
    grid_model = project.grid_models[grid_model_name]
    region_param_name = aps_model.getRegionParamName()
    zone_param_name = GridModelConstants.ZONE_NAME
    use_regions = (region_param_name is not None) and len(region_param_name) > 0

    # Read zone and region parameter from RMS
    zone_values, _ = getDiscrete3DParameterValues(
        grid_model, zone_param_name, realization_number
    )
    facies_per_zone_region_dict = None
    facies_per_zone_dict = None
    region_values = None
    if use_regions:
        region_values, _ = getDiscrete3DParameterValues(
            grid_model, region_param_name, realization_number
        )
        facies_per_zone_region_dict = {}
    else:
        facies_per_zone_dict = {}
    # Get list of all zone models
    all_zone_models = aps_model.sorted_zone_models

    # Get all probability parameter names
    probability_parameter_names = aps_model.getAllProbParam()

    # Loop over all pairs of (zone_number, region_number) that is specified and selected
    # Check and normalize the probabilities for each (zone, region) model
    prob_params_per_facies = {}
    for key, zone_model in all_zone_models.items():
        (zone_number, region_number) = key
        if debug_level >= Debug.VERBOSE:
            if use_regions:
                print(f'-- Zone: {zone_number}  Region number: {region_number} ')
            else:
                print(f'-- Zone: {zone_number} ')
        if not aps_model.isSelected(zone_number, region_number):
            continue

        if zone_model.use_constant_probabilities:
            # No probability cubes for this (zone, region)
            if debug_level >= Debug.VERBOSE:
                print('--   Constant probabilities specified.')
            continue
        facies_names_for_zone = zone_model.facies_in_zone_model
        if use_regions:
            facies_per_zone_region_dict[key] = facies_names_for_zone
        else:
            facies_per_zone_dict[zone_number] = facies_names_for_zone

        for facies_name in facies_names_for_zone:
            param_name = zone_model.getProbParamName(facies_name)
            if facies_name not in prob_params_per_facies:
                prob_params_per_facies[facies_name] = param_name
            else:
                if param_name != prob_params_per_facies[facies_name]:
                    raise ValueError(
                        f'The facies {facies_name} has different probability parameter names in different zones.\n'
                        f'The parameter name: {param_name} is used in  zone number {zone_model.zone_number}\n'
                        f'The parameter name: {prob_params_per_facies[facies_name]} is used in another zone.\n'
                        'For each facies name, only use one probability parameter\n'
                        '(which of course may have different values in each zone and region)'
                    )
    return (
        grid_model,
        use_regions,
        facies_per_zone_dict,
        facies_per_zone_region_dict,
        prob_params_per_facies,
        probability_parameter_names,
        zone_values,
        region_values,
    )


def get_input_params(
    project,
    params: dict,
    realization_number: int,
):
    project = params.get('project')
    grid_model_name = params.get('grid_model_name')
    region_param_name = params.get('region_param_name', None)
    zone_param_name = GridModelConstants.ZONE_NAME
    grid_model = project.grid_models[grid_model_name]

    # Get all probability parameter names
    prob_params_per_facies = params.get('prob_param_per_facies')
    probability_parameter_names = list(prob_params_per_facies.values())

    # Read zone and region parameter from RMS
    zone_code_names = None
    zone_values = None
    region_code_names = None
    region_values = None
    zone_values, zone_code_names = getDiscrete3DParameterValues(
        grid_model, zone_param_name, realization_number
    )

    use_regions = (region_param_name is not None) and len(region_param_name) > 0
    facies_per_zone_dict = None
    facies_per_zone_region_dict = None
    if use_regions:
        region_values, region_code_names = getDiscrete3DParameterValues(
            grid_model, region_param_name, realization_number
        )
        facies_per_zone_region_dict = params.get('modelling_facies_per_zone_region')
        facies_dict = facies_per_zone_region_dict

    else:
        facies_per_zone_dict = params.get('modelling_facies_per_zone')
        facies_dict = facies_per_zone_dict

    # Check consistency
    facies_checked_list = []
    facies_used = []
    facies_list_with_prob_param = list(prob_params_per_facies.keys())
    for key, facies_list in facies_dict.items():
        for name in facies_list:
            if name not in facies_used:
                facies_used.append(name)
            if (name not in facies_list_with_prob_param) and (
                name not in facies_checked_list
            ):
                facies_checked_list.append(name)
    if len(facies_checked_list) > 0:
        raise ValueError(
            f"Facies used in zones but don't have any specified probability parameter:\n {facies_checked_list} "
        )

    not_used = []
    for name in facies_list_with_prob_param:
        if name not in facies_used:
            not_used.append(name)
    if len(not_used) > 0:
        raise ValueError(
            f'Facies specified with probability parameters, but not used in any zone or region:\n {not_used}'
        )

    check_grid_zone_regions = params.get('report_zone_regions', False)
    if check_grid_zone_regions:
        defined_zone_regions, defined_zones = check_zones_regions_used(
            zone_code_names,
            zone_values,
            region_code_names=region_code_names,
            region_param_values=region_values,
        )
        if use_regions:
            print('List of (zone, region) found in the grid and if used or not:')
            print('Zone number   Region number   Specified')
            for item in defined_zone_regions:
                (zone_number, region_number) = item
                is_used = item in facies_dict
                print(
                    f'  {zone_number}             {region_number}               {"Yes" if is_used else "No"} '
                )
        else:
            print('List of zones found in the grid and if used or not:')
            print('  Zone number   Specified')
            for zone_number in defined_zones:
                is_used = zone_number in facies_dict
                print(f'  {zone_number}        {is_used} ')

    return (
        grid_model,
        use_regions,
        facies_per_zone_dict,
        facies_per_zone_region_dict,
        prob_params_per_facies,
        probability_parameter_names,
        zone_values,
        region_values,
    )


def check_and_normalize_all_zones(
    facies_per_zone_region_dict,
    zone_values,
    region_values,
    grid_model,
    realization_number,
    use_regions,
    probability_values_per_rms_param,
    probability_params_per_facies,
    max_prob_norm_tolerance,
    min_prob_norm_tolerance,
    max_allowed_fraction,
    debug_level,
    stop_on_error,
):
    # if stop_on_error is False then accumulate all error messages and some info message in error_dict
    # and print out at the end to get all error messages for all zones and all regions.
    error_dict = {
        'Error': False,
        'Message': [],
    }
    for key, facies_list_per_zone_region in facies_per_zone_region_dict.items():
        if use_regions:
            (zone_number, region_number) = key
            print(f'Zone number: {zone_number}  Region number: {region_number}')
        else:
            zone_number = int(key)
            region_number = 0
            print(f'Zone number: {zone_number}')

        # For current (zone,region) find the active cells
        cell_index_defined = find_defined_cells(
            zone_values, zone_number, region_values, region_number
        )
        if len(cell_index_defined) == 0:
            if use_regions:
                print(
                    f'Warning: No active grid cells for (zone,region)=({zone_number}, {region_number})\n'
                    f'         Skip this zone, region combination'
                )
            else:
                print(
                    f'Warning: No active grid cells for zone: {zone_number}\n'
                    f'         Skip this zone'
                )
            continue

        # Update contents in probability_values_per_rms_param
        if stop_on_error:
            num_cells_modified_probability, probability_values_per_rms_param = (
                check_and_normalise_probability(
                    grid_model,
                    realization_number,
                    zone_number,
                    probability_values_per_rms_param,
                    facies_list_per_zone_region,
                    probability_params_per_facies,
                    cell_index_defined,
                    region_number=region_number,
                    tolerance_of_probability_normalisation=max_prob_norm_tolerance,
                    eps=min_prob_norm_tolerance,
                    max_allowed_fraction_with_mismatch=max_allowed_fraction,
                    debug_level=debug_level,
                )
            )
        else:
            (
                num_cells_modified_probability,
                probability_values_per_rms_param,
                error_dict,
            ) = check_and_normalise_probability(
                grid_model,
                realization_number,
                zone_number,
                probability_values_per_rms_param,
                facies_list_per_zone_region,
                probability_params_per_facies,
                cell_index_defined,
                region_number=region_number,
                tolerance_of_probability_normalisation=max_prob_norm_tolerance,
                eps=min_prob_norm_tolerance,
                max_allowed_fraction_with_mismatch=max_allowed_fraction,
                debug_level=debug_level,
                stop_on_error=stop_on_error,
                error_dict=error_dict,
            )

        if debug_level >= Debug.ON:
            if region_number > 0:
                print(
                    f'- Number of cells that are normalised for (zone,region)=({zone_number}, {region_number}) '
                    f'are {num_cells_modified_probability} of {len(cell_index_defined)} cells.'
                )
            else:
                print(
                    f'- Number of cells that are normalised for zone: {zone_number} '
                    f'are {num_cells_modified_probability} of {len(cell_index_defined)} cells.'
                )
    # End loop over (zone, region) pair
    if not stop_on_error:
        if error_dict['Error']:
            print('')
            if use_regions:
                print('Errors in normalization per zone and region:\n')
            else:
                print('\nErrors in normalization per zone:\n')
            for msg in error_dict['Message']:
                print(msg)

            raise NormalisationError('Normalization errors found.')
    return probability_values_per_rms_param


def check_and_normalise_probability(
    grid_model,
    realization_number,
    zone_number,
    probability_values_per_rms_param,
    facies_list_per_zone_region,
    prob_param_per_facies,
    cell_index_defined,
    region_number=0,
    tolerance_of_probability_normalisation=ProbabilityTolerances.MAX_ALLOWED_DEVIATION_BEFORE_ERROR,
    eps=ProbabilityTolerances.MAX_DEVIATION_BEFORE_ACTION,
    max_allowed_fraction_with_mismatch=ProbabilityTolerances.MAX_ALLOWED_FRACTION_OF_VALUES_OUTSIDE_TOLERANCE,
    debug_level=Debug.OFF,
    stop_on_error=True,
    error_dict=None,
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

    :param grid_model:
    :type grid_model: GridModel
    :param realization_number:
    :type realization_number: int
    :param zone_number:
    :type zone_number: int
    :param probability_values_per_rms_param: dictionary where the key is rms parameter name and the value is a numpy vector
    :type probability_values_per_rms_param: dict
    :facies_list_per_zone_region: dictionary with list of facies names for each zone or (zone,region) combination.
    :type facies_list_per_zone_region: dict
    :prob_param_per_facies: dict with name of facies probability 3D parameter per facies.
    :type prob_param_per_facies: dict
    :param cell_index_defined: list of indices for the grid cells that are selected (belongs to a specific zone or (zone,region) combination.
    :type cell_index_defined: list
    :param region_number:
    :type region_number: int
    :param tolerance_of_probability_normalisation: Criteria to check probabilities, cumulative probabilities and negative probabilities.
    :type tolerance_of_probability_normalisation: float
    :param eps: Dfine maximum difference between sum of input probabilities and 1.0 that is accepted without having to do any normalisation.
    :type eps: float
    :param max_allowed_fraction_with_mismatch: Criteria for raising error if the fraction of number of grid cells with invalid probabilities exceed this fraction.
    :type param max_allowed_fraction_with_mismatch: float
    :param debug_level: Define output print level from the function.
    :type debug_level: int
    :param stop_on_error: Turn on/off whether to raise error immediately in the check of probability or accumulate the error message and raise error at the end.
    :type stop_on_error: bool
    :param error_dict: contains list of error messages if any from check of probabilities.
    :type error_dict: dict
    :return: integer with number of grid cells for which the probabilities are re-calculated to be normalised.
    """
    if not stop_on_error:
        error_dict['Message'].append('')
        if region_number > 0:
            error_dict['Message'].append(
                f'Zone number: {zone_number} Region number: {region_number} '
            )
        else:
            error_dict['Message'].append(f'Zone number: {zone_number}')

    # List of facies names for a specific(zone, region) combination
    facies_names_for_zone = facies_list_per_zone_region

    # RMS probability parameter names for each facies
    # Dictionary where the key is facies_name, and the value is
    # rms parameter name for the probabilities for this facies
    prob_param_names = probability_values_per_rms_param.keys()

    sum_probabilities_selected_cells = np.zeros(len(cell_index_defined), np.float32)
    num_cell_with_modified_probability = 0

    # Check that probability values are in interval [0,1]
    err_found_in_zone = False
    for facies_name in facies_names_for_zone:
        parameter_name = prob_param_per_facies[facies_name]

        # All grid cells (active cells in the grid)
        all_values = probability_values_per_rms_param[parameter_name]

        # The cells belonging to the zone,region as defined by the input cell_index_defined array
        probabilities_selected_cells = all_values[cell_index_defined]

        # Check probability values, ensure that they are in the interval [0,1]. If outside this interval,
        # probabilities < 0 is set to 0 and probabilities > 1 is set to 1.
        # If the fraction of grid cells with probabilities outside the tolerance interval
        # [1-tolerance_of_probability_normalisation, 1+tolerance_of_probability_normalisation] is
        # larger than max_allowed_fraction_with_mismatch, errors are reported.
        if stop_on_error:
            probabilities_selected_cells = check_probability_values(
                probabilities_selected_cells,
                tolerance_of_probability_normalisation,
                max_allowed_fraction_with_mismatch,
                facies_name,
                parameter_name,
            )
        else:
            probabilities_selected_cells, error_dict, err_found = (
                check_probability_values(
                    probabilities_selected_cells,
                    tolerance_of_probability_normalisation,
                    max_allowed_fraction_with_mismatch,
                    facies_name,
                    parameter_name,
                    stop_on_error=stop_on_error,
                    error_dict=error_dict,
                )
            )
            if err_found:
                err_found_in_zone = True

        # Sum up probability over all facies per selected cell
        all_values[cell_index_defined] = probabilities_selected_cells
        sum_probabilities_selected_cells += probabilities_selected_cells
        probability_values_per_rms_param[parameter_name] = all_values

    if (sum_probabilities_selected_cells == 0).any():
        name = 'APS_problematic_cells_in_probability_cubes'
        # The property MAY have been created with a previous version as a continuous property.
        # In that case, writing code names to that property will cause a runtime error in RMS.
        _remove_existing_if_necessary(
            grid_model, name, desired_type=roxar.GridPropertyType.discrete
        )
        grid = grid_model.get_grid(realization_number)
        values = grid.generate_values(np.uint8)
        values[cell_index_defined] = sum_probabilities_selected_cells == 0
        number_of_problematic_cells = np.sum(values[cell_index_defined])

        set_discrete_3d_parameter_values(
            grid_model,
            name,
            input_values=values,
            code_names={
                0: 'OK',
                1: 'Problematic',
            },
            realisation_number=realization_number,
            debug_level=debug_level,
        )
        parameter_names = _format_names(prob_param_names)
        err_msg = (
            f'The probability cubes {parameter_names}, in zone {zone_number}, '
            f'have some areas with 0 cumulative probability.\n'
            f'These areas are shown in {name}.'
            f'Number of grid cells with 0 cumulative probability is: {number_of_problematic_cells}.'
        )
        # Can not continue with this error since have to avoid zero division
        raise NormalisationError(err_msg)

    # Check normalisation and report error if input probabilities are too far from 1.0
    if stop_on_error:
        normalise_is_necessary = check_probability_normalisation(
            sum_probabilities_selected_cells,
            eps,
            tolerance_of_probability_normalisation,
            max_allowed_fraction_with_mismatch,
        )
    else:
        normalise_is_necessary, error_dict, err_found = check_probability_normalisation(
            sum_probabilities_selected_cells,
            eps,
            tolerance_of_probability_normalisation,
            max_allowed_fraction_with_mismatch,
            stop_on_error=stop_on_error,
            error_dict=error_dict,
        )

        if err_found:
            err_found_in_zone = True

    if not stop_on_error and not err_found_in_zone:
        error_dict['Message'].append('Ok')

    if normalise_is_necessary:
        # Normalize
        psum = sum_probabilities_selected_cells

        for i, facies_name in enumerate(facies_names_for_zone):
            parameter_name = prob_param_per_facies[facies_name]
            all_values = probability_values_per_rms_param[parameter_name]
            p = all_values[cell_index_defined]
            if i == 0:
                check_value = (psum > (1.0 + eps)) | (psum < (1.0 - eps))
                num_cell_with_modified_probability = check_value.sum()

            # Normalize
            p_norm = p / psum

            # The cells belonging to the zone,region as defined by the input cell_index_defined array
            # is updated by normalised values
            all_values[cell_index_defined] = p_norm
            probability_values_per_rms_param[parameter_name] = all_values

    if stop_on_error:
        return num_cell_with_modified_probability, probability_values_per_rms_param
    else:
        return (
            num_cell_with_modified_probability,
            probability_values_per_rms_param,
            error_dict,
        )


def _format_names(names):
    parameter_names = ''
    n = len(names)
    for i, probability_cube in enumerate(names):
        parameter_names += f"'{probability_cube}'"

        if i < n - 2:
            parameter_names += ', '
        elif i == n - 2:
            parameter_names += ', and '
        elif i == n - 1:
            # The last item does not have a comma after it
            pass
    return parameter_names


def _remove_existing_if_necessary(
    grid_model: GridModel, name: str, desired_type: roxar.GridPropertyType
):
    if name in grid_model.properties:
        prop = grid_model.properties[name]
        if prop.type != desired_type:
            del grid_model.properties[name]


def check_zones_regions_used(
    zone_code_names,
    zone_param_values,
    region_code_names=None,
    region_param_values=None,
):
    zone_region_used = []
    zones_used = []
    if region_code_names is not None:
        for zone_number in zone_code_names:
            for region_number in region_code_names:
                key = (zone_number, region_number)
                selected_grid_cells = (zone_param_values == zone_number) & (
                    region_param_values == region_number
                )
                if len(selected_grid_cells) > 0:
                    zone_region_used.append(key)
    else:
        for zone_number in zone_code_names:
            selected_grid_cells = zone_param_values == zone_number
            if len(selected_grid_cells) > 0:
                zones_used.append(zone_number)
    return zone_region_used, zones_used
