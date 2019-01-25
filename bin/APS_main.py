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
from collections import OrderedDict
from src.utils.roxar.generalFunctionsUsingRoxAPI import (
    setContinuous3DParameterValues, updateContinuous3DParameterValues, updateDiscrete3DParameterValues,
)
from src.utils.roxar.grid_model import (
    get3DParameter, getContinuous3DParameterValues,
    isParameterDefinedWithValuesInRMS, getDiscrete3DParameterValues,
    find_defined_cells,
)

from src.utils.methods import calc_average, get_specification_file
from src.algorithms.APSModel import APSModel
from src.utils.constants.simple import Debug, ProbabilityTolerances
from src.utils.checks import check_probability_values,  check_probability_normalisation

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
    increment = 1.0/num_defined_cells
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
        num_facies, prob_parameter_values_for_facies, use_const_probability, cell_index_defined,
        eps=0.0000001, tolerance_of_probability_normalisation = 0.01,
        debug_level=Debug.SOMEWHAT_VERBOSE
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

            defined_values = values[cell_index_defined]
            # Check that probabilities are in interval [0,1]. If not, set to 0 if negative and 1 if larger than 1.
            # Error message if too large fraction of input values are outside interval [0,1] also when using tolerance.
            probability_defined[f] =  check_probability_values(defined_values, tolerance_of_probability_normalisation,
                                                               facies_name)

        # Sum up probability over all facies per defined cell
        prob_vector = probability_defined[0]
        psum = np.copy(prob_vector)
        for f in range(1, num_facies):
            # sum of np arrays (cell by cell sum)
            psum += probability_defined[f]

        normalise_is_necessary = check_probability_normalisation(psum, eps, tolerance_of_probability_normalisation)
        if  normalise_is_necessary:
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



def get_all_gauss_field_names_in_model(aps_model):
    ''' 
    Returns the lists:
         - all gauss field names specified in any zone in the whole model
         - all gauss field names used in one or more zones in the whole model
    Returns also a list with all gauss field names used in at least one zone and which has trend.
    '''
    all_zone_models = aps_model.sorted_zone_models
    gauss_field_names_specified = []
    gauss_field_names_used = []
    gauss_field_names_with_trend = []
    for key, zone_model in all_zone_models.items():
        zone_number = key[0]
        region_number = key[1]
        if not aps_model.isSelected(zone_number, region_number):
            continue

        zone_model = aps_model.getZoneModel(zone_number, region_number)

        # Gauss fields defined for the zone in model file
        gf_names_for_zone = zone_model.used_gaussian_field_names

        # Gauss fields used in truncation rule for the zone in model file
        gf_names_for_truncation_rule = zone_model.getGaussFieldsInTruncationRule()

        for name in gf_names_for_zone:
            if name not in gauss_field_names_specified:
                gauss_field_names_specified.append(name)
            if name in gf_names_for_truncation_rule:
                if  name not in gauss_field_names_used:
                    gauss_field_names_used.append(name)
                if zone_model.hasTrendModel(name):
                    if name not in gauss_field_names_with_trend:
                        gauss_field_names_with_trend.append(name)


    return gauss_field_names_specified, gauss_field_names_used, gauss_field_names_with_trend

def get_used_gauss_field_names_in_zone(gauss_field_names_in_zone, gauss_field_names_in_truncation_rule):
    '''
    input: 
    - list of gauss fields specified for a zone
    - list of gauss_fields used in truncation rule for the same zone
    Return an ordered dictionary with gauss field name as key and bool values as values. 
    The bool values are true if the gauss field is used, false if not used.
    '''
    use_gauss_field_in_zone = OrderedDict()
    for i in range(len(gauss_field_names_in_zone)):
        name = gauss_field_names_in_zone[i]
        use_gauss_field_in_zone[name] = name in gauss_field_names_in_truncation_rule
    return use_gauss_field_in_zone



def initialize_rms_parameters(project, aps_model, write_rms_parameters_for_qc_purpose):
    '''
    Returns dictionaries with numpy arrays containing the gauss field values, trend values, transformed gauss field values for each gauss field name. The key is gauss field name.
    '''
    grid_model_name = aps_model.getGridModelName()
    realization_number = project.current_realisation
    grid_model = project.grid_models[grid_model_name]
    grid3D = grid_model.get_grid(realization_number)
    number_of_active_cells = grid3D.defined_cell_count
    debug_level = aps_model.debug_level

    # all_gauss_field_names is a list of all gauss fields used in at least one zone
    # all_gauss_field_names_with_trend is a list of all gauss fields used in at least one zone and which has trend
    gauss_field_names_specified, gauss_field_names_used, gauss_field_names_with_trend = get_all_gauss_field_names_in_model(aps_model)

    # Keeps all simulated gauss fields (residual fields)
    gf_all_values = OrderedDict()

    # Keeps all transformed gauss fields (gauss field with trends that are transformed to [0,1] distribution)
    gf_all_alpha  = OrderedDict()

    # Keeps all trend values  and untransformed gauss fields with trend
    gf_all_trend_values = OrderedDict()
    gf_all_values_untransformed = OrderedDict()


    # Initialize all values to 0
    if debug_level >= Debug.VERBOSE:
        print('--- Initialize values for:')
    for name in gauss_field_names_used:
        gf_all_values[name] = np.zeros(number_of_active_cells, np.float32)
        gf_all_alpha[name] = np.zeros(number_of_active_cells, np.float32)
        if debug_level >= Debug.VERBOSE:
            print('---    {}'.format(name))

    # Simulated gauss fields that are used in some zones are read from RMS 
    # They are required and must exist. 
    for name in gauss_field_names_used:
        parameter_name = name
        values = getContinuous3DParameterValues(grid_model, name, realization_number)
        gf_all_values[name] = values

    # Initialize the RMS 3D parameters for QC with extension _trend, _transf, _untransf
    if write_rms_parameters_for_qc_purpose:
        # Write initial values to transformed gauss parameters
        zone_number_list = []
        for name in gauss_field_names_used:
            parameter_name = name + '_transf'
            input_values = gf_all_alpha[name]
            setContinuous3DParameterValues( 
                grid_model, parameter_name, input_values, 
                zone_number_list, realization_number
            )

        if len(gauss_field_names_with_trend) > 0:
            if debug_level >= Debug.VERBOSE:
                print('--- Initialize trend values for:')
            for name in gauss_field_names_with_trend:
                gf_all_trend_values[name] = np.zeros(number_of_active_cells, np.float32)
                gf_all_values_untransformed[name] = np.zeros(number_of_active_cells, np.float32)
                if debug_level >= Debug.VERBOSE:
                    print('---    {}'.format(name))

            # Write initial values to trend gauss parameters
            for name in gauss_field_names_with_trend:
                parameter_name = name + '_untransf'
                input_values = gf_all_values_untransformed[name]
                setContinuous3DParameterValues(
                    grid_model, parameter_name, input_values, 
                    zone_number_list, realization_number
                )
                parameter_name = name + '_trend'
                input_values = gf_all_trend_values[name]
                setContinuous3DParameterValues(
                    grid_model, parameter_name, input_values, 
                    zone_number_list, realization_number
                )

    return gf_all_values, gf_all_alpha, gf_all_trend_values, gf_all_values_untransformed



def add_trend_to_gauss_field(project, aps_model, 
                             zone_number, region_number, use_regions, 
                             gauss_field_name, 
                             gauss_field_values, 
                             cell_index_defined):
    '''
    Calculate trend and add trend to simulated gaussian residual field to get the gaussian field with trend. 
    Standard deviation for residual field is calculated by using the specified relative standard deviation and the trend max minus min of trend function.
    Returns gauss field where the grid cells defined by cell_index_defined are updated. All other grid cell values are not modified. 
    The lenght of this array is equal to the length of all active grid cells in the grid model.
    Returns also trend values in a separate array, but this array has length equal to cell_index_defined and does only contain the values for the grid cells
    that are selected by cell_index_defined.
    '''
    grid_model_name = aps_model.getGridModelName()
    realization_number = project.current_realisation
    grid_model = project.grid_models[grid_model_name]
    debug_level = aps_model.debug_level
    key = (zone_number, region_number)
    zone_model = aps_model.sorted_zone_models[key]

    # Get trend model, relative standard deviation
    use_trend, trend_model, rel_std_dev, rel_std_dev_fmu = zone_model.getTrendModel(gauss_field_name)

    if debug_level >= Debug.VERBOSE:
        trend_type = trend_model.type.name
        if use_regions:
            print(
                '--- Calculate trend for: {} for (zone,region)=({},{})\n'
                '--- Trend type: {}'
                ''.format(gauss_field_name, zone_number, region_number, trend_type)
                )
        else:
            print(
                '--- Calculate trend for: {} for zone: {}\n'
                '--- Trend type: {}'
                ''.format(gauss_field_name, zone_number, trend_type)
                )

    sim_box_thickness = zone_model.getSimBoxThickness()
    # trend_values contain trend values for the cells belonging to the set defined by cell_index_defined
    minmax_difference, trend_values = trend_model.createTrend(
        grid_model, realization_number, len(cell_index_defined),
        cell_index_defined, zone_number, sim_box_thickness
        )

    # Calculate trend plus residual for the cells defined by cell_index_defined
    # and replace the residual values by trend + residual in array: gauss_field_values
    sigma = rel_std_dev * minmax_difference
    residual_values = gauss_field_values[cell_index_defined]
    val = trend_values + sigma * residual_values
    # updates array values for the selected grid cells
    gauss_field_values[cell_index_defined] = val
    if debug_level >= Debug.VERY_VERBOSE:
        print('Debug output: Trend minmax_difference = ' + str(minmax_difference))
        print('Debug output: SimBoxThickness = ' + str(sim_box_thickness))
        print('Debug output: RelStdDev = ' + str(rel_std_dev))
        print('Debug output: Sigma = ' + str(sigma))
        print('Debug output: Min trend, max trend    : ' + str(trend_values.min()) + ' ' + str(trend_values.max()))
        print('Debug output: Residual min,max        : ' + str(sigma * residual_values.min()) + ' ' + str(sigma * residual_values.max()))
        print('Debug output: trend + residual min,max: ' + str(val.min()) + ' ' + str(val.max()))

    return gauss_field_values, trend_values

def update_RMS_parameters_for_qc_purpose(grid_model, gauss_field_name,
                                         gauss_field_values,
                                         gauss_field_trend_values,
                                         cell_index_defined,
                                         realization_number,
                                         use_regions,
                                         zone_number,
                                         region_number,
                                         debug_level):
    # Write back to RMS project the untransformed gaussian values with trend for the zone
    update_RMS_parameter(grid_model, 
                         gauss_field_name,
                         gauss_field_values, 
                         cell_index_defined, 
                         realization_number, 
                         variable_name_extension='untransf',
                         use_regions=use_regions,
                         zone_number=zone_number,
                         region_number=region_number,
                         debug_level=debug_level)

    # Write back to RMS project the trend values for the zone
    update_RMS_parameter(grid_model, 
                         gauss_field_name,
                         gauss_field_trend_values, 
                         cell_index_defined, 
                         realization_number, 
                         variable_name_extension='trend',
                         use_regions=use_regions,
                         zone_number=zone_number,
                         region_number=region_number,
                         debug_level=debug_level)

def update_RMS_parameter(grid_model, 
                         gauss_field_name, 
                         values, 
                         cell_index_defined, 
                         realization_number, 
                         variable_name_extension=None,
                         use_regions=False,
                         zone_number=0,
                         region_number=0,
                         debug_level=Debug.OFF):
    # Write back to RMS project the updated rms 3D parameter
    if variable_name_extension is None:
        rms_variable_name = gauss_field_name
    else:
        rms_variable_name = gauss_field_name + '_' + variable_name_extension

    updateContinuous3DParameterValues(
        grid_model, 
        rms_variable_name, 
        values, 
        cell_index_defined, 
        realization_number,
        isShared=False, setInitialValues=False, 
        debug_level=debug_level
    )
    if debug_level >= Debug.VERBOSE:
        if use_regions:
            print('--- Create or update parameter: {} for (zone,region)= ({},{})'.format(rms_variable_name, zone_number, region_number))
        else:
            print('--- Create or update parameter: {} for zone number: {}'.format(rms_variable_name, zone_number))

def run(
        roxar=None, project=None,
        eps=ProbabilityTolerances.MAX_DEVIATION_BEFORE_ACTION,
        tolerance_of_probability_normalisation=ProbabilityTolerances.MAX_ALLOWED_DEVIATION_BEFORE_ERROR,
        write_rms_parameters_for_qc_purpose=True,
        **kwargs
):
    realization_number = project.current_realisation
    print('Run: APS_trunc  on realisation ' + str(realization_number + 1))

    model_file_name = get_specification_file(**kwargs)

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
    use_regions = bool(region_param_name)
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
            print('--- Get RMS facies parameter which will be updated: {} from RMS project: {}'
                  ''.format(result_param_name, rms_project_name))
        facies_real, code_names_for_input = getDiscrete3DParameterValues(grid_model, result_param_name, 
                                                                         realization_number, debug_level)
    else:
        if debug_level >= Debug.VERBOSE:
            print('--- Facies parameter: {}  for the result will be created in the RMS project: {}'
                  ''.format(result_param_name, rms_project_name))

    # Initialize dictionaries keeping gauss field values and trends for all used gauss fields
    gf_all_values, gf_all_alpha, gf_all_trend_values, gf_all_values_untransformed = initialize_rms_parameters(project, 
                                                                                                              aps_model, 
                                                                                                              write_rms_parameters_for_qc_purpose)
    # Probability related lists
    probability_parameter_names_already_read = []
    probability_parameter_all_values = []
    # The two lists: probability_parameter_all_values, probability_parameter_values_for_facies,
    # will use a list of items where the item is of the form item =[name,value]
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

        # Read trend parameters for truncation rule parameters
        zone_model.getTruncationParam(grid_model, realization_number)

        # Info about whether constant probabilities or probability cubes are used.
        use_constant_probability = zone_model.useConstProb()

        # Number of gauss fields defined for the zone in model file
        gf_names_for_zone = zone_model.used_gaussian_field_names

        # Number of gauss fields used in truncation rule for the zone in model file
        gf_names_for_truncation_rule = zone_model.getGaussFieldsInTruncationRule()

        # This dictionary has value True/False depending on whether a gauss field is used or not in the truncation rule for current zone (or zone/region).
        use_gauss_field_in_zone = get_used_gauss_field_names_in_zone(gf_names_for_zone, gf_names_for_truncation_rule)

        facies_names_for_zone = zone_model.getFaciesInZoneModel()
        num_facies = len(facies_names_for_zone)

        if debug_level >= Debug.VERBOSE:
            print('--- Gauss field parameter specified for this zone: ')
            for gf_name in gf_names_for_zone:
                print('---   {}'.format(gf_name))
            print('--- Gauss field parameter used in trunction rule for this zone: ')
            for gf_name in gf_names_for_truncation_rule:
                print('---   {}'.format(gf_name))


        # For current (zone,region) find the active cells
        cell_index_defined = find_defined_cells(zone_values, zone_number, region_values, region_number, debug_level=Debug.OFF)
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
        # NOTE: The dictionary for alpha fields for current zone must be ordered in the same sequence as gf_names_for_zone
        gf_alpha_for_current_zone = OrderedDict()
        for gf_name in gf_names_for_zone:
            if use_gauss_field_in_zone[gf_name]:
                gauss_field_values_all = gf_all_values[gf_name]
                if zone_model.hasTrendModel(gf_name):
                    gauss_field_values_all, trend_values_for_zone = add_trend_to_gauss_field(
                        project, aps_model, zone_number, region_number, 
                        use_regions, gf_name, gauss_field_values_all, cell_index_defined
                    )
                    if write_rms_parameters_for_qc_purpose:
                        # Update array trend for the selected grid cells
                        # Note that the numpy vector trend contains values for all active grid cells
                        # while trend_values_for_zone contain values calculated for the current zone and current parameter
                        trend_values_all = gf_all_trend_values[gf_name]
                        trend_values_all[cell_index_defined] = trend_values_for_zone
                        gf_all_trend_values[gf_name] = trend_values_all

                        update_RMS_parameters_for_qc_purpose(
                            grid_model, gf_name, gauss_field_values_all,
                            trend_values_all, cell_index_defined, realization_number,
                            use_regions, zone_number, region_number, debug_level
                        )

                if debug_level >= Debug.VERBOSE:
                    if use_regions:
                        print('--- Transform: {} for zone: {}'.format(gf_name, zone_number))
                    else:
                        print('--- Transform: {} for (zone, region)=({},{})'.format(gf_name, zone_number, region_number))
                # Update alpha for current zone
                alpha_all = gf_all_alpha[gf_name]
                alpha_all = transform_empiric(cell_index_defined, gauss_field_values_all, alpha_all)
                gf_all_alpha[gf_name] = alpha_all



                # Dictionary of transformed values for gauss field for current (zone,region)
                gf_alpha_for_current_zone[gf_name] = alpha_all

                if write_rms_parameters_for_qc_purpose:
                    # Write back to RMS project the transformed gaussian values for the zone
                    update_RMS_parameter(
                        grid_model, gf_name, alpha_all, cell_index_defined, 
                        realization_number, variable_name_extension='transf',
                        use_regions=use_regions, zone_number=zone_number,
                        region_number=region_number, debug_level=debug_level
                    )
                    
            else:
                # This gauss field name is specified for the zone but not used in truncation rule and not simulated or used
                # But it is necessary to have defined an entry for it to keep this dictionary in same order and of same length
                # as the list of gauss field names for zone.
                gf_alpha_for_current_zone[gf_name] = None


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

        # Apply truncations and calculate or update facies realization
        if debug_level >= Debug.VERBOSE:
            print('--- Truncate transformed Gaussian fields.')
        facies_real, volume_fraction = zone_model.applyTruncations(
            probability_defined, gf_alpha_for_current_zone, facies_real, len(cell_index_defined), cell_index_defined
        )

        if debug_level >= Debug.ON:
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
    if debug_level >= Debug.ON:
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
