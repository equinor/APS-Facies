#!/bin/env python
# -*- coding: utf-8 -*-
import roxar
import numpy as np
import collections
from src.utils.constants.simple import  ProbabilityTolerances, Debug
from src.utils.roxar.grid_model import  create_zone_parameter, getDiscrete3DParameterValues


def get_facies_code(code_names, facies_name):
    for code, name in code_names.items():
        if name == facies_name:
            return code
    return None


def getBlockedWells(project, grid_model_name, bw_name):
    """ Get blocked wells """
    grid_model = project.grid_models[grid_model_name]
    if grid_model.is_empty():
        print('Error: Empty grid model {}'.format(grid_model_name))
        return None
    blocked_wells_set = grid_model.blocked_wells_set
    blocked_wells = blocked_wells_set[bw_name]
    return blocked_wells


def getFaciesTableFromBlockedWells(project, grid_model_name, blocked_wells_set_name, facies_log_name, realization_number=0):
    """ Get blocked well of type discrete and return dictionary with facies codes and names."""
    # Get blocked wells
    blocked_wells = getBlockedWells(project, grid_model_name, bw_name)
    if blocked_wells is not None:
        if blocked_wells.is_empty(realization_number):
            return None
        # Get facies property
        facies_property = blocked_wells.properties[facies_log_name]
        if facies_property.type == roxar.GridPropertyType.discrete:
            code_names = facies_property.code_names
            return code_names
        else:
            print('Error: Specified log {} in blocked well set {} in grid model {} is not of type discrete'
                  ''.format(facies_log_name, blocked_wells_set_name, grid_model_name))
            return None
    else:
        return None


def getFaciesTableAndLogValuesFromBlockedWells(project, grid_model_name, blocked_wells_set_name, facies_log_name, realization_number=0):
    """ Get blocked well of type discrete and return dictionary with facies codes and names and facies log values in numpy array
        Note that the returned facies log values can be a masked numpy array (to represent inactive or undefined values)
        so the output must be checked if it is a masked array.
    """

    blocked_wells = getBlockedWells(project, grid_model_name, blocked_wells_set_name)
    if blocked_wells is None:
        return None, None
    if blocked_wells.is_empty(realization_number):
        print('Error: Specified blocked wells {} in grid model {} for realization {} is empty'
              ''.format(blocked_wells_set_name, grid_model_name, str(realization_number+1)))
        return None, None
    # Get facies property
    facies_property = blocked_wells.properties[facies_log_name]

    if facies_property.type == roxar.GridPropertyType.discrete:
        code_names = facies_property.code_names
    else:
        print('Error: Specified log {} in blocked well set {} in grid model {} is not of type discrete'
              ''.format(facies_log_name, blocked_wells_set_name, grid_model_name))
        return None, None

    facies_log_values = facies_property.get_values(realization_number)
    return code_names, facies_log_values


def createProbabilityLogs(
        project, grid_model_name,
        bw_name='BW',
        facies_log_name='Facies',
        zone_log_name='Zone',
        modelling_facies_per_zone=None,
        additional_unobserved_facies_list=None,
        output_facies_names=None,
        conditional_prob_facies=None,
        prefix_prob_logs='Prob_',
        realization_number=0,
        accept_unobserved_facies_names=True,
        debug_level=Debug.OFF
):
    """ Get Facies log from blocked wells and create probability logs that have values 0.0 or 1.0 for each facies.
        It is possible to specify a list of additional facies names for facies that should be modelled, but is not observed.
        Probability logs for these unobserved facies will only contain 0 as value since the facies is not observed.
        It is possible to specify conditional probability for facies given the input facies.
    """
    code_names, facies_log_values = getFaciesTableAndLogValuesFromBlockedWells(project, grid_model_name, bw_name, facies_log_name, realization_number)
    code_names_zone,  zone_log_values = getFaciesTableAndLogValuesFromBlockedWells(project, grid_model_name, bw_name, zone_log_name, realization_number)
    blocked_wells = getBlockedWells(project, grid_model_name, bw_name)
    if blocked_wells is None:
        return
    facies_names_in_log = code_names.values()

    # Make list of all facies logs to be created by reading through specified facies list for each specified zone
    # Make a dictionary of all probability logs
    probability_log_names = []
    probability_logs = {}

    sorted_zone_facies_dictionary = collections.OrderedDict(sorted(modelling_facies_per_zone.items()))

    # Find max zone number
    max_zone_number = 0
    for zone_number, zone_name in code_names_zone.items():
        if max_zone_number < zone_number:
            max_zone_number = zone_number

    # Find max facies code
    max_code_number = 0
    for code, name in code_names.items():
        if max_code_number < code:
            max_code_number = code

    # Find which facies is defined for each zone
    is_modelling_facies = np.zeros((max_zone_number+1, max_code_number+2), np.int32)
    modelled_facies_not_observed = []
    for zone_number, facies_for_modelling in sorted_zone_facies_dictionary.items():
        for facies_name in facies_for_modelling:
            if facies_name not in facies_names_in_log:
                if not accept_unobserved_facies_names:
                    raise ValueError(
                        'Specified facies name for modelling {} does not exist in facies log {}'
                        ''.format(facies_name, facies_log_name)
                    )
                else:
                    if facies_name not in modelled_facies_not_observed:
                        modelled_facies_not_observed.append(facies_name)

            prob_log_name = prefix_prob_logs + '_' + str(facies_name)
            prob_log = None
            if prob_log_name not in probability_log_names:
                probability_log_names.append(prob_log_name)
                prob_log = blocked_wells.properties.create(prob_log_name, roxar.GridPropertyType.continuous, np.float32)

                # Initialize to impossible value and define all values as undefined by mask = 1
                prob_values = blocked_wells.generate_values(discrete=False, fill_value=-1.0)
                mask_values = blocked_wells.generate_values(discrete=True, fill_value=1)
                # Set first entry to defined initially as a workaround to make masked logs in prob_log
                # It is necessary to have at least one point in the log that is not undefined to get log as a masked array.
                # This value is reset to undefined before any updating of the initial empty logs with data
                mask_values[0] = 0
                prob_values_with_mask = np.ma.array(prob_values, mask=mask_values)
                prob_log.set_values(prob_values_with_mask, realization_number)
                probability_logs[facies_name] = prob_log

            code_for_facies = get_facies_code(code_names, facies_name)
            # If the code_for_facies is None which means that facies_name is not found in the facies log,
            # it means that the facies_name is not observed, but is anyway a modelling facies.
            # If None is sent into the numpy array below, then is_modelling_facies will be one for all facies codes.
            is_modelling_facies[zone_number, code_for_facies] = 1

    if len(modelled_facies_not_observed) > 0 and conditional_prob_facies is None:
        print('Warning: The following facies is specified to be modelled, but is not observed in facies log')
        print('These facies will get probability 0 in probability logs:')
        for name in modelled_facies_not_observed:
            print('  {}'.format(name))

    use_mask_facies = False
    use_mask_zone = False
    if type(facies_log_values) == np.ma.core.MaskedArray:
        use_mask_facies = True
    if type(zone_log_values) == np.ma.core.MaskedArray:
        use_mask_zone = True
    use_mask_prob = use_mask_zone or use_mask_facies

    if conditional_prob_facies is None:
        # Run through all probability logs that were initialized
        for facies_name, prob_log in probability_logs.items():
            facies_code = get_facies_code(code_names, facies_name)
            if facies_code is None:
                facies_code = max_code_number + 1
            prob_values = prob_log.get_values(realization_number)
            mask_values = None
            if use_mask_prob:
                mask_values = prob_values.mask
                # set first entry to undefined initially since it was set to
                # defined in initialization as a workaround
                mask_values[0] = 1

            # Run through the values in the facies log
            for i in range(len(facies_log_values)):
                update_prob_log = False
                zone_number = -1
                if use_mask_zone:
                    if not zone_log_values.mask[i]:
                        zone_number = zone_log_values[i]
                else:
                    zone_number = zone_log_values[i]

                facies_code_in_log = -1
                if use_mask_facies:
                    if not facies_log_values.mask[i]:
                        facies_code_in_log = facies_log_values[i]
                else:
                    facies_code_in_log = facies_log_values[i]

                if zone_number > 0 and facies_code_in_log >= 0:
                    # Check that the grid cell has facies that belongs to the zone
                    if is_modelling_facies[zone_number, facies_code_in_log]:
                        # Check that the grid cell also has facies belonging to the current probability log that is to be updated
                        if is_modelling_facies[zone_number, facies_code]:
                            update_prob_log = True

                if update_prob_log:
                    # This grid cell has facies that belongs to the set of facies that is to be modelled
                    if facies_code_in_log == facies_code:
                        # Facies code from facies log match the facies for the probability log
                        # and is a modelling facies for the zone. Give probability 1
                        prob_values[i] = 1
                        if use_mask_prob:
                            mask_values[i] = 0
                    else:
                        # Facies code from facies log is different from the facies for the probability log
                        # but is a modelling facies for the zone. Give probability 0
                        prob_values[i] = 0
                        if use_mask_prob:
                            mask_values[i] = 0
            if use_mask_prob:
                prob_values_with_mask = np.ma.array(prob_values, mask=mask_values)
                prob_log.set_values(prob_values_with_mask)
            else:
                prob_log.set_values(prob_values)
            print('Define {}'.format(prob_log.name))
    else:

        # Check input consistency
        for code, name in code_names.items():
            for zone_number, facies_for_modelling in sorted_zone_facies_dictionary.items():
                sum_prob = 0.0
                is_defined = False
                for facies_name in facies_for_modelling:
                    if name in facies_for_modelling:
                        is_defined = True
                        key = (facies_name, name)
                        prob = conditional_prob_facies[key]
                        sum_prob = sum_prob + prob
                if is_defined:
                    if abs(sum_prob - 1.0) > ProbabilityTolerances.MAX_DEVIATION_BEFORE_ACTION:
                        raise ValueError(
                            'Sum of the conditional probabilities conditioned to {} is {} and not 1.0 for zone {}.'
                            ' Check specification.'
                            ''.format(name, sum_prob, zone_number)
                        )

        # Run through all probability logs that were initialized
        for facies_name, prob_log in probability_logs.items():
            prob_values = prob_log.get_values(realization_number)
            mask_values = prob_values.mask

            # Run through the values in the facies log
            for i in range(len(facies_log_values)):
                update_prob_log = False
                zone_number_in_log = -1
                if use_mask_zone:
                    if not zone_log_values.mask[i]:
                        zone_number_in_log = zone_log_values[i]
                else:
                    zone_number_in_log = zone_log_values[i]

                facies_code_in_log = -1
                if use_mask_facies:
                    if not facies_log_values.mask[i]:
                        facies_code_in_log = facies_log_values[i]
                else:
                    facies_code_in_log = facies_log_values[i]

                if zone_number_in_log > 0 and facies_code_in_log >= 0:
                    if is_modelling_facies[zone_number_in_log, facies_code_in_log]:
                        update_prob_log = True

                if update_prob_log:
                    # This grid cell has facies that belongs to the set of facies that is to be modelled
                    zone_number_in_log = zone_log_values[i]
                    facies_code_in_log = facies_log_values[i]
                    facies_name_in_log = code_names[facies_code_in_log]

                    # Get the conditioned probability for facies with name 'facies_name'
                    #  given that the facies log has facies name 'facies_name_in_log'
                    key = (facies_name, facies_name_in_log)
                    prob = conditional_prob_facies[key]

                    prob_values[i] = prob
                    mask_values[i] = 0

            prob_values_with_mask = np.ma.array(prob_values, mask=mask_values)
            prob_log.set_values(prob_values_with_mask)
            print('Define {}'.format(prob_log.name))


def createCombinedFaciesLogForBlockedWells(
        project, grid_model_name, bw_name, original_facies_log_name,
        new_facies_log_name, new_code_names, mapping_between_original_and_new
):
    # Original facies log code and name table and log values
    original_code_names, facies_log_values = getFaciesTableAndLogValuesFromBlockedWells(project, grid_model_name, bw_name, original_facies_log_name)
    if original_code_names is None:
        return
    # Create space for new facies log
    blocked_wells = getBlockedWells(project, grid_model_name, bw_name)
    new_facies_log = blocked_wells.properties.create(new_facies_log_name, roxar.GridPropertyType.discrete, np.int32)
    # Initialize all values to undefined by masking them
    values = blocked_wells.generate_values(discrete=True, fill_value=0)
    mask_values = blocked_wells.generate_values(discrete=True, fill_value=1)

    max_code = -1
    for code, name in original_code_names.items():
        if code > max_code:
            max_code = code

    # Create array mapping from old to new facies code
    new_code_for_old_code = np.zeros((max_code + 1), np.int32)
    for original_facies, new_facies in mapping_between_original_and_new.items():
        found = False
        original_code = None
        for code, name in original_code_names.items():
            if name.strip() == original_facies.strip():
                original_code = code
                found = True
                break
        if not found:
            print('Error: The facies name {} is not found in original facies log'.format(original_facies))
            return

        found = False
        new_code = None
        for code, name in new_code_names.items():
            if name.strip() == new_facies.strip():
                new_code = code
                found = True
                break
        if not found:
            print('Error: The facies name {} is not found in new facies log'.format(new_facies))
            return

        new_code_for_old_code[original_code] = new_code

    # For each new facies
    if type(facies_log_values) == np.ma.core.MaskedArray:
        # numpy masked array also containing masked (undefined) values
        for i in range(len(facies_log_values)):
            if not facies_log_values.mask[i]:
                code = facies_log_values[i]
                new_code = new_code_for_old_code[code]
                values[i] = int(new_code)
                mask_values[i] = 0
            else:
                mask_values[i] = 1

        # Define a facies value array with mask to be set as result facies log in RMS
        values_with_mask = np.ma.array(values, mask=mask_values)
        new_facies_log.set_values(values_with_mask)
    else:
        for i in range(len(facies_log_values)):
            code = facies_log_values[i]
            new_code = new_code_for_old_code[code]
            values[i] = int(new_code)
        new_facies_log.set_values(values)

    new_facies_log.code_names = new_code_names
    print('Blocked well log {} created/updated'.format(new_facies_log_name))


def cell_numbers_for_blocked_wells(project, grid_model_name, bw_name):
    blocked_wells = getBlockedWells(project, grid_model_name, bw_name)
    blocked_wells_cell_numbers = blocked_wells.get_cell_numbers()
    for i in range(len(blocked_wells_cell_numbers)):
        cell_number = blocked_wells_cell_numbers[i]
    return  blocked_wells_cell_numbers
    
def get_facies_in_zone_from_blocked_wells(project, grid_model_name, bw_name, facies_log_name, zone_number, 
                                          region_param_name=None, region_number= 0, realization_number=0):
    cell_numbers =  cell_numbers_for_blocked_wells(project, grid_model_name, bw_name)
    # Check if zone parameter exist. If not create it
    grid_model = project.grid_models[grid_model_name]
    zone_parameter = create_zone_parameter(grid_model, realization_number)
    zone_values = zone_parameter.get_values(realization_number)
    zone_values_in_bw = np.zeros(len(cell_numbers), np.uint8)
    zone_values_in_bw = zone_values[cell_numbers]
    code_names, facies_log_values = getFaciesTableAndLogValuesFromBlockedWells(project, grid_model_name, bw_name, facies_log_name)
    assert len(facies_log_values) == len(cell_numbers)

    facies_values_found = []
    region_parameter = None
    if region_param_name != None:
        region_values, region_code_names = getDiscrete3DParameterValues(grid_model, region_param_name, realization_number=realization_number)
        region_values_in_bw = np.zeros(len(cell_numbers), np.uint8)
        region_values_in_bw = region_values[cell_numbers]
        for i in range(len(cell_numbers)):
            indx = cell_numbers[i]
            zone_val = zone_values_in_bw[i]
            region_val = region_values_in_bw[i]
            if zone_val == zone_number and region_val == region_number:
                facies_value = facies_log_values[i]
#                print('cell number: {}  zone value: {}  region_number: {}  facies: {}'.format(indx, zone_val, region_val, facies_value))
                if facies_value not in facies_values_found:
                    facies_values_found.append(facies_value)
    else:
        for i in range(len(cell_numbers)):
            indx = cell_numbers[i]
            zone_val = zone_values_in_bw[i]
            if zone_val == zone_number:
                facies_value = facies_log_values[i]
#                print('cell number: {}  zone value: {}  facies: {}'.format(indx, zone_val, facies_value))
                if facies_value not in facies_values_found:
                    facies_values_found.append(facies_value)

    facies_names_found = []
    for i in range(len(facies_values_found)):
        code = facies_values_found[i]
        facies_name = code_names[code]
        facies_names_found.append(facies_name)
    return facies_names_found
