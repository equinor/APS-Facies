#!/bin/env python
# -*- coding: utf-8 -*-
import roxar
import numpy as np
import collections

from typing import Dict, List
from aps.utils.constants.simple import ProbabilityTolerances, Debug
from aps.utils.roxar.grid_model import create_zone_parameter, getDiscrete3DParameterValues


def get_facies_code(code_names, facies_name):
    for code, name in code_names.items():
        if name == facies_name:
            return code
    return None


def getBlockedWells(project, grid_model_name, bw_name):
    """ Get blocked wells """
    grid_model = project.grid_models[grid_model_name]
    realisation_number = project.current_realisation
    if grid_model.is_empty(realisation_number):
        print(f'Error: Empty grid model {grid_model_name} for realisation {realisation_number}')
        return None
    blocked_wells_set = grid_model.blocked_wells_set
    blocked_wells = blocked_wells_set[bw_name]
    return blocked_wells


def getFaciesTableAndLogValuesFromBlockedWells(project, grid_model_name, 
                                               blocked_wells_set_name, 
                                               facies_log_name, realization_number=0):
    """ Get blocked well of type discrete and return dictionary with facies codes and names 
        and facies log values in numpy array.
        Note that the returned facies log values can be a masked numpy array 
        (to represent inactive or undefined values)
        so the output must be checked if it is a masked array.
    """

    blocked_wells = getBlockedWells(project, grid_model_name, blocked_wells_set_name)
    if blocked_wells is None:
        return None, None
    if blocked_wells.is_empty(realization_number):
        print(f'Error: Specified blocked wells {blocked_wells_set_name} in grid model {grid_model_name}'
              f'for realization {realization_number + 1} is empty')
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


def get_discrete_log_from_blocked_well_set(project,
        grid_model_name,
        blocked_wells_set_name,
        realization_number,
        log_name):

    blocked_wells = getBlockedWells(project, grid_model_name, blocked_wells_set_name)
    if blocked_wells is None:
        raise ValueError(
            f"Blocked well set: {blocked_wells_set_name} is not found in:  {grid_model_name}"
        )

    if blocked_wells.is_empty(realization_number):
        raise ValueError(
            f"Specified blocked well set: {blocked_wells_set_name} "
            f"in grid model: {grid_model_name} "
            f"for realization: {realization_number + 1} is empty."
        )

    # Get facies property
    if log_name in blocked_wells.properties:
        discrete_property = blocked_wells.properties[log_name]
    else:
        raise ValueError(
            f"Specified log: {log_name} is not found in: {blocked_wells_set_name}."
        )
    if discrete_property.type == roxar.GridPropertyType.discrete:
        code_names = discrete_property.code_names
    else:
        raise ValueError(
            f"Specified log: {log_name} is not of type discrete."
        )
    discrete_log_values = discrete_property.get_values(realization_number)
    return code_names, discrete_log_values

def get_facies_zone_table_and_log_from_bw(project, grid_model_name,
        blocked_wells_set_name,
        facies_log_name,
        zone_log_name,
        realization_number=0):
    """ Get blocked well of type discrete and return dictionary
        with facies codes and names and zone codes and names.
        Return also facies and zone log values as numpy arrays.
        Note that the returned facies log values can be a masked numpy array
        (to represent inactive or undefined values)
        so the output must be checked if it is a masked array.
    """
    zone_code_names, zone_log_values = \
        get_discrete_log_from_blocked_well_set(project,
            grid_model_name,
            blocked_wells_set_name,
            realization_number,
            zone_log_name)

    facies_code_names, facies_log_values = \
        get_discrete_log_from_blocked_well_set(project,
            grid_model_name,
            blocked_wells_set_name,
            realization_number,
            facies_log_name)

    # Dict of facies names found in each zone
    print(f"Facies log: {facies_log_name}")
    print(f"Zone   log: {zone_log_name}")
    facies_per_zone ={}
    for zone_number, _ in zone_code_names.items():
        selected_facies_values = facies_log_values[zone_log_values == zone_number]
        facies_codes_found_in_zone = []
        for i in range(len(selected_facies_values)):
            facies_code = selected_facies_values[i]
            if facies_code >= 0:
                # Negative or masked values are not used
                if facies_code not in facies_codes_found_in_zone:
                    facies_codes_found_in_zone.append(facies_code)

        facies_names_found =[ facies_code_names[code] for code in facies_codes_found_in_zone]
        facies_per_zone[zone_number] = facies_names_found

        if zone_number <= 0:
            print(
                f"Note: Zone log has a zone with zone number equal to 0 or less in {blocked_wells_set_name} .\n"
                "All probability logs in this zone will be undefined."
            )
        else:
            if len(facies_codes_found_in_zone) > 0:
                print(f"Facies found in facies log for zone: {zone_number}")
                for fcode in facies_codes_found_in_zone:
                    print(f"    {facies_code_names[fcode]}")
            else:
                print(
                    f"Note: No facies found in facies log for zone: {zone_number} in {blocked_wells_set_name}  \n"
                    "All probability logs will be undefined in this zone."
                )


    return zone_code_names, zone_log_values, facies_code_names, facies_log_values, facies_per_zone


def createProbabilityLogs(
        project=None,
        grid_model_name=None,
        bw_name='BW',
        facies_log_name='Facies',
        zone_log_name='Zone',
        modelling_facies_per_zone=None,
        conditional_prob_facies=None,
        prefix_prob_logs='Prob_',
        realization_number=0,
        accept_unobserved_facies_names=True,
        debug_level=Debug.OFF
):
    """ Get Facies log from blocked wells and create probability logs that have values 0.0 or 1.0 for each facies.
        It is possible to specify a list of additional facies names for facies that should be modelled,
        but is not observed. Probability logs for these unobserved facies will only contain 0 as value
        since the facies is not observed. It is possible to specify conditional probability for facies
        given the input facies.
    """
    _, zone_log_values, code_names, facies_log_values, facies_per_zone = get_facies_zone_table_and_log_from_bw(project,
        grid_model_name,
        bw_name,
        facies_log_name,
        zone_log_name,
        realization_number)

    blocked_wells = getBlockedWells(project, grid_model_name, bw_name)
    if blocked_wells is None:
        return
    facies_names_in_log = code_names.values()

    # Make list of all facies logs to be created by reading through specified facies list for each specified zone
    # Make a dictionary of all probability logs
    probability_log_names = []
    probability_logs = {}

    sorted_zone_facies_dictionary = collections.OrderedDict(sorted(modelling_facies_per_zone.items()))
    modelled_facies_codes_observed_per_zone = check_observed_facies_per_zone(sorted_zone_facies_dictionary, 
                                                                             code_names,
                                                                             facies_log_values,
                                                                             zone_log_values)

    keys_for_modelled_facies_per_zone = modelled_facies_codes_observed_per_zone.keys()

    # This list is used to inform the user about facies specified to be modelled but is not observed
    modelled_facies_not_observed = []

    # This list is used to inform the user about facies specified to be modelled and also is observed
    modelled_facies_observed = []

    for zone_number, facies_for_modelling in sorted_zone_facies_dictionary.items():
        for facies_name in facies_for_modelling:
            if facies_name not in facies_names_in_log:
                if not accept_unobserved_facies_names:
                    raise ValueError(
                        f"Specified facies name for modelling: {facies_name} "
                        f"does not exist in facies log: {facies_log_name}"
                    )
                else:
                    # Append facies that is specified to be modelled, but not observed in wells to the list
                    # of modelling facies that is not observed.
                    if facies_name not in modelled_facies_not_observed:
                        modelled_facies_not_observed.append(facies_name)
            else:
                # Facies specified to be modelled and also found in blocked well facies log
                if facies_name not in modelled_facies_observed:
                    modelled_facies_observed.append(facies_name)
                
            prob_log_name = prefix_prob_logs + '_' + str(facies_name)
            if prob_log_name not in probability_log_names:
                probability_log_names.append(prob_log_name)
                prob_log = blocked_wells.properties.create(prob_log_name, roxar.GridPropertyType.continuous, np.float32)

                # Initialize to impossible value and define all values as undefined by mask = 1
                prob_values = blocked_wells.generate_values(discrete=False, fill_value=-1.0, realisation=realization_number)
                mask_values = blocked_wells.generate_values(discrete=True, fill_value=1, realisation=realization_number)
                # Set first entry to defined initially as a workaround to make masked logs in prob_log
                # It is necessary to have at least one point in the log that is not undefined to get log as a masked array.
                # This value is reset to undefined before any updating of the initial empty logs with data
                mask_values[0] = 0
                prob_values_with_mask = np.ma.array(prob_values, mask=mask_values)
                prob_log.set_values(prob_values_with_mask, realization_number)
                probability_logs[facies_name] = prob_log

    use_mask_facies = False
    use_mask_zone = False
    if type(facies_log_values) == np.ma.core.MaskedArray:
        use_mask_facies = True
    if type(zone_log_values) == np.ma.core.MaskedArray:
        use_mask_zone = True
    use_mask_prob = use_mask_zone or use_mask_facies

    if conditional_prob_facies is None:
        for zone_number, facies_for_modelling in sorted_zone_facies_dictionary.items():
            warn_msg_obs_facies_not_specified = []
            warn_msg_specified_facies_not_observed = []
            for name in facies_per_zone[zone_number]:
                if name not in facies_for_modelling:
                    warn_msg_obs_facies_not_specified.append(
                        f" {name}  "
                    )
            for fname in facies_for_modelling:
                if fname not in facies_per_zone[zone_number]:
                    warn_msg_specified_facies_not_observed.append(
                        f"  {fname}  "
                    )
            if warn_msg_specified_facies_not_observed:
                print(f"Warning: Following facies is specified but not observed for zone {zone_number}")
                print( "         Probability log for these facies will be 0 in this zone.")
                print( "         Maybe there are some misspelled facies names here?")
                for msg in warn_msg_specified_facies_not_observed:
                    print(msg)
                print(" ")
            if warn_msg_obs_facies_not_specified:
                print(f"Warning: Following facies is observed but not specified for zone {zone_number}.")
                print( "         Forgot to specify them for this zone?")
                print( "         The probability logs for these facies will be set to either undefined or ")
                print( "         to 0 probability for this zone:")
                for msg in warn_msg_obs_facies_not_specified:
                    print(msg)
                print(" ")

        # Run through all probability logs that were initialized
        for facies_name, prob_log in probability_logs.items():
            facies_code = get_facies_code(code_names, facies_name)
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
                    # The facies code is not missing code
                    # Check that the grid cell has facies that belongs to the zone
                    key = (zone_number, facies_code_in_log)
                    if key in keys_for_modelled_facies_per_zone:
                        # This facies is a modelled facies for this zone either observed or not observed
                        if modelled_facies_codes_observed_per_zone[key] != 0:
                            # This modelling facies belongs to a zone with some observed facies
                            # Set probability log to 1 or 0
                            update_prob_log = True
                        else:
                            # This modelling facies belongs to a zone without any observed facies
                            # Let probability log be missing code
                            pass
                if update_prob_log:
                    if facies_code_in_log == facies_code:
                        # Modelled facies matching the observed facies
                        # Set probability 1
                        prob_values[i] = 1
                        if use_mask_prob:
                            mask_values[i] = 0
                    else:
                        # Modelled facies not matching the observed facies
                        # Set probability 0
                        prob_values[i] = 0
                        if use_mask_prob:
                            mask_values[i] = 0
            if use_mask_prob:
                prob_values_with_mask = np.ma.array(prob_values, mask=mask_values)
                prob_log.set_values(prob_values_with_mask, realization_number)
            else:
                prob_log.set_values(prob_values, realization_number)
            print(f'Probability log defined:  {prob_log.name}')
    else:

        # Check input consistency
        # For each facies in the blocked well, log, check that it is defined in the list of modelled facies
        for zone_number, facies_for_modelling in sorted_zone_facies_dictionary.items():
            for name in facies_per_zone[zone_number]:
                sum_prob = 0.0
                err_list =[] 
                for facies_name in facies_for_modelling:
                    key = (zone_number, facies_name, name)
                    if key not in conditional_prob_facies:
                        # Check if the specified facies and facies to condition to belongs to the zone
                        err_list.append(
                            f"  P({facies_name} | {name} ) in zone {zone_number}"
                        )
                    else:
                        prob = conditional_prob_facies[key]
                        sum_prob = sum_prob + prob
                if err_list:
                    print(f"Missing specification of conditional probabilities of modelled facies conditioned to {name} :")
                    for s in err_list:
                        print(f" {s}")
                    raise ValueError("Need specification of conditional probabilities")

                if abs(sum_prob - 1.0) > ProbabilityTolerances.MAX_DEVIATION_BEFORE_ACTION:
                    raise ValueError(
                        f"Sum of the conditional probabilities in zone: {zone_number} "
                        f"conditioned to: {name} is {sum_prob} and not 1. Check specification."
                    )
            # Check if there are specified conditional probabilities given
            # interpreted facies that does not exist and give a warning that this will be igored.
            warning_msg = []
            for key in conditional_prob_facies:
                (znr, fmodelled, finterpreted) = key
                if znr == zone_number:
                    if finterpreted not in facies_per_zone[zone_number]:
                        warning_msg.append(
                            f"   P( {fmodelled} |{finterpreted}) "
                            f"specified but {finterpreted} is not observed in zone {zone_number}  ")
            if warning_msg:
                print("Warnings: Unused conditional probabilities:")
                for msg in warning_msg:
                    print(msg)
                print("\n")

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


                facies_code = get_facies_code(code_names, facies_name)
                if facies_code is None:
                    facies_code = -1
                if zone_number_in_log > 0 and facies_code_in_log >= 0:
                    # The facies code in well log is not missing code
                        update_prob_log = True

                if update_prob_log:
                    # This grid cell has facies that belongs to the set of facies that is to be modelled
                    facies_code_in_log = facies_log_values[i]
                    facies_name_in_log = code_names[facies_code_in_log]
                    # Get the conditioned probability for facies with name 'facies_name'
                    #  given that the facies log has facies name 'facies_name_in_log'
                    try:
                        # Only blocked well grid cells with specified conditional probabilities for modelled facies is updated
                        key = (zone_number_in_log, facies_name, facies_name_in_log)
                        prob = conditional_prob_facies[key]

                        prob_values[i] = prob
                        mask_values[i] = 0
                    except:
                        # For this case the probability is undefined
                        pass
                        

            prob_values_with_mask = np.ma.array(prob_values, mask=mask_values)
            prob_log.set_values(prob_values_with_mask, realization_number)
            print(f'Probability log defined:  {prob_log.name}')

    # Verify that the created probability logs are consistent (sum up to 1) for each grid cell in blocked wells 
    check_probability_logs(probability_log_names, 
                           probability_logs,
                           code_names,
                           zone_log_values,
                           sorted_zone_facies_dictionary, 
                           realization_number,
                           debug_level
    )



def check_observed_facies_per_zone(specified_modelled_facies_per_zone_dict, 
                                   code_names,
                                   facies_log_values,
                                   zone_log_values):
    # Find which modelled facies is observed or not for each zone
    zones_specified = list(specified_modelled_facies_per_zone_dict.keys())
    number_of_values_in_facies_log = len(facies_log_values)
    number_of_values_in_zone_log   = len(zone_log_values)
    assert(number_of_values_in_facies_log == number_of_values_in_zone_log)

    modelled_facies_codes_observed_in_zone = {}
    index_all_values = np.arange(number_of_values_in_zone_log)
    for zone_number in zones_specified:
        modelled_facies = specified_modelled_facies_per_zone_dict[zone_number]
        number_of_modelled_facies_observed_in_zone = 0
        for facies_name in modelled_facies:
            facies_code = get_facies_code(code_names, facies_name)
            if facies_code is not None:
                # This modelled facies is observed in facies log in some zone
                index_selected_values = index_all_values[(zone_log_values == zone_number) & (facies_log_values == facies_code)]
                if len(index_selected_values) > 0:
                    # This facies is both defined as a modelled facies and also observed for current zone
                    key = (zone_number, facies_code)
                    modelled_facies_codes_observed_in_zone[key] = 1
                    number_of_modelled_facies_observed_in_zone = number_of_modelled_facies_observed_in_zone +1
                else:
                    # This facies is defined as a modelled facies but not observed for current zone.
                    key = (zone_number, facies_code)
                    modelled_facies_codes_observed_in_zone[key] = 0
            else:
                # This facies is defined as a modelled facies but does not exist in the facies log at all
                facies_code = -1
                key = (zone_number, facies_code)
                modelled_facies_codes_observed_in_zone[key] = 0

        codes = list(code_names.keys())
        keys = modelled_facies_codes_observed_in_zone.keys()
        # Include also facies code -1 which is defined as the code for all modelled facies not found in the facies log
        codes.append(-1) 
        if number_of_modelled_facies_observed_in_zone > 0:
            for facies_code in codes:
                key = (zone_number, facies_code)
                if key in keys:
                    if modelled_facies_codes_observed_in_zone[key] == 0:
                        # This facies is defined as modelled but not observed and there exist 
                        # modelled facies that is observed for the same zone
                        # Need to distinguish this facies from unobserved facies in zones that 
                        # does not have any observed facies at all.
                        modelled_facies_codes_observed_in_zone[key] = -1

    return modelled_facies_codes_observed_in_zone

def check_probability_logs(probability_log_names, 
                           probability_logs,
                           code_names,
                           zone_log_values, 
                           modelling_facies_per_zone, 
                           realization_number,
                           debug_level=Debug.VERBOSE):
    print('\nCheck created probability logs:\n')
    normalization_error = {}
    count_zones = 0
    for zone_number, modelling_facies in modelling_facies_per_zone.items():
        first = True
        sum_values = None
        number_of_active_values = 0
        for facies_name in modelling_facies:
            prob_log = probability_logs[facies_name]
            prob_values = prob_log.get_values(realization_number)
            selected_prob_values = prob_values[zone_log_values == zone_number]
            if first:
                first = False
                sum_values = selected_prob_values
                number_of_active_values = len(sum_values)
            else:
                if number_of_active_values > 0:
                    sum_values = sum_values + selected_prob_values

        if number_of_active_values == 0:
            print(f'Zone: {zone_number} has no blocked well cells with probability logs')
        else:
            # Check if the sum is 1 for all entries in the numpy array
            eps = 0.001

            check_value = (sum_values > (1.0 + eps)) | (sum_values < (1.0 - eps))
            num_cell_with_not_normalized_prob = check_value.sum()
            normalization_error[zone_number] =  num_cell_with_not_normalized_prob
            if num_cell_with_not_normalized_prob > 0:
                count_zones = count_zones +1
    if count_zones == 0:
        print('Normalization of probability logs is OK')
    else:
        for zone_number, modelling_facies in modelling_facies_per_zone.items():
            if normalization_error[zone_number] > 0:
                print(
                    f"Zone: {zone_number} Number of cell values in BW where sum of probability logs "
                    f"has values outside interval [{1-eps}, {1+eps}]: {num_cell_with_not_normalized_prob}"
                )
            if debug_level >= Debug.VERBOSE:
                for i in range(len(sum_values)):
                    text = str(i)
                    if sum_values[i] >(1+eps) or sum_values[i] < (1-eps):
                        for facies in modelling_facies:
                            prob_log = probability_logs[facies]
                            prob_values = prob_log.get_values(realization_number)
                            p = prob_values[i]
                            text = text + ' ' + '('+ facies + ' ' + str(p) +')' + '  '
                        text = text + '  sum= ' + str(sum_values[i])
                    print(text)




def createCombinedFaciesLogForBlockedWells(params):
    project = params['project']
    grid_model_name = params['grid_model_name']
    bw_name = params['bw_name']
    original_facies_log_name = params['original_facies_log_name']
    new_facies_log_name = params['new_facies_log_name']
    new_code_names = params['new_code_names']
    mapping_between_original_and_new = params['mapping_between_original_and_new']
    realization_number = params['realization_number']

    # Original facies log code and name table and log values
    original_code_names, facies_log_values = getFaciesTableAndLogValuesFromBlockedWells(project, grid_model_name, bw_name, original_facies_log_name)
    if original_code_names is None:
        return
    # Create space for new facies log
    blocked_wells = getBlockedWells(project, grid_model_name, bw_name)
    new_facies_log = blocked_wells.properties.create(new_facies_log_name, roxar.GridPropertyType.discrete, np.int32)
    # Initialize all values to undefined by masking them
    values = blocked_wells.generate_values(discrete=True, fill_value=0, realisation=realization_number)
    mask_values = blocked_wells.generate_values(discrete=True, fill_value=1, realisation=realization_number)

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
            print(f"Error: The facies name {original_facies} is not found in original facies log")
            return

        found = False
        new_code = None
        for code, name in new_code_names.items():
            if name.strip() == new_facies.strip():
                new_code = code
                found = True
                break
        if not found:
            print(f"Error: The facies name {new_facies} is not found in new facies log")
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
        new_facies_log.set_values(values_with_mask, realization_number)
    else:
        for i in range(len(facies_log_values)):
            code = facies_log_values[i]
            new_code = new_code_for_old_code[code]
            values[i] = int(new_code)
        new_facies_log.set_values(values, realization_number)

    new_facies_log.code_names = new_code_names
    print(f"Blocked well log {new_facies_log_name} created/updated")


def cell_numbers_for_blocked_wells(project, grid_model_name, bw_name):
    blocked_wells = getBlockedWells(project, grid_model_name, bw_name)
    blocked_wells_cell_numbers = blocked_wells.get_cell_numbers(project.current_realisation)
    return blocked_wells_cell_numbers


def get_facies_in_zone_from_blocked_wells(project, grid_model_name, bw_name, facies_log_name, zone_number,
                                          region_param_name=None, region_number=0, realization_number=0):
    cell_numbers = cell_numbers_for_blocked_wells(project, grid_model_name, bw_name)
    # Check if zone parameter exist. If not create it
    grid_model = project.grid_models[grid_model_name]
    zone_parameter = create_zone_parameter(grid_model, realization_number)
    zone_values = zone_parameter.get_values(realization_number)
    zone_values_in_bw = zone_values[cell_numbers]
    code_names, facies_log_values = getFaciesTableAndLogValuesFromBlockedWells(project, grid_model_name, bw_name, facies_log_name)
    assert len(facies_log_values) == len(cell_numbers)

    facies_values_found = []
    if region_param_name is not None:
        region_values, _ = getDiscrete3DParameterValues(grid_model, region_param_name, realization_number=realization_number)
        region_values_in_bw = region_values[cell_numbers]
        for i in range(len(cell_numbers)):
            zone_val = zone_values_in_bw[i]
            region_val = region_values_in_bw[i]
            if zone_val == zone_number and region_val == region_number:
                facies_value = facies_log_values[i]
                if facies_value not in facies_values_found:
                    facies_values_found.append(facies_value)
    else:
        for i in range(len(cell_numbers)):
            zone_val = zone_values_in_bw[i]
            if zone_val == zone_number:
                facies_value = facies_log_values[i]
                if facies_value not in facies_values_found:
                    facies_values_found.append(facies_value)

    facies_names_found = []
    for i in range(len(facies_values_found)):
        code = facies_values_found[i]
        facies_name = code_names[code]
        facies_names_found.append(facies_name)
    return facies_names_found
