#!/bin/env python
# -*- coding: utf-8 -*-
import roxar
import numpy as np
from src.utils.constants.simple import ProbabilityTolerances, Debug


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
    """ Get blocked well of type discrete and return dictionary with facies codes and names and facies log values in numpy array"""

    blocked_wells = getBlockedWells(project, grid_model_name, blocked_wells_set_name)
    if blocked_wells is None:
        return None, None
    if blocked_wells.is_empty(realization_number):
        print('Error: Specified blocked wells {} in grid model {} for realization {} is empty'
              ''.format(blocked_wells_set_name, grid_model_name, realization_number + 1))
        return None, None
    # Get facies property
    facies_property = blocked_wells.properties[facies_log_name]

    code_names = None
    if facies_property.type == roxar.GridPropertyType.discrete:
        code_names = facies_property.code_names
    else:
        print('Error: Specified log {} in blocked well set {} in grid model {} is not of type discrete'
              ''.format(facies_log_name, blocked_wells_set_name, grid_model_name))
        return None, None

    facies_log_values = facies_property.get_values(realization_number)
    return code_names, facies_log_values


def createProbabilityLogs(project, grid_model_name,
                          bw_name='BW',
                          facies_log_name='Facies',
                          additional_unobserved_facies_list=None,
                          output_facies_names=None,
                          conditional_prob_facies=None,
                          prefix_prob_logs='Prob_',
                          realization_number=0,
                          debug_level=Debug.OFF):
    """ Get Facies log from blocked wells and create probability logs that have values 0.0 or 1.0 for each facies.
        It is possible to specify a list of additional facies names for facies that should be modelled, but is not observed.
        Probability logs for these uncobserved facies will only contain 0 as value since the facies is not observed.  """

    code_names, facies_log_values = getFaciesTableAndLogValuesFromBlockedWells(project, grid_model_name, bw_name, facies_log_name, realization_number)
    blocked_wells = getBlockedWells(project, grid_model_name, bw_name)
    if blocked_wells is None:
        return

    if conditional_prob_facies is None:
        # Loop over all facies name in facies log and create a probability log binary values  (0 or 1) for each facies
        for code, name in code_names.items():
            prob_log_name = prefix_prob_logs + '_' + str(name)
            print('Create blocked well log for {}'.format(prob_log_name))
            prob_log = blocked_wells.properties.create(prob_log_name, roxar.GridPropertyType.continuous, np.float32)
            prob_values = blocked_wells.generate_values(discrete=False, fill_value=-1.0)

            for i in range(len(facies_log_values)):
                faciesCode = facies_log_values[i]
                if faciesCode == code:
                    # This grid cell in the blocked well is of matching facies as the facies for the probability log
                    # Assign 1.0 as probability for this cell in the blocked well
                    prob_values[i] = 1.0
                else:
                    # This grid cell in the blocked well is not matching facies as the facies for the probability log
                    # Assign 0.0 as probability for this cell in the blocked well
                    prob_values[i] = 0.0
            prob_log.set_values(prob_values)

        # Add probability logs for facies that are not observed in wells and therefore have 0 as probabilily in the blocked well logs
        for fName in additional_unobserved_facies_list:
            prob_log_name = prefix_prob_logs + '_' + str(fName)
            print('Create blocked well log for {}'.format(prob_log_name))
            prob_log = blocked_wells.properties.create(prob_log_name, roxar.GridPropertyType.continuous, np.float32)
            prob_values = blocked_wells.generate_values(discrete=False, fill_value=0.0)
            prob_log.set_values(prob_values)
    else:
        # Check input consistency

        for code, name in code_names.items():
            sum_prob = 0.0
            for output_name in output_facies_names:
                key = (output_name, name)
                prob = conditional_prob_facies[key]
                sum_prob = sum_prob + prob
            if abs(sum_prob - 1.0) > ProbabilityTolerances.MAX_DEVIATION_BEFORE_ACTION:
                raise ValueError('Sum of the conditional probabilities conditioned to {} is {} and not 1.0. Check specification.'.format(name, sum_prob))

        # Loop over all output facies names and create a probability log with probabilities depending on facies in input log. In this case
        # the probabilties for the output logs does not necessarily have ot contain only 0 or 1.
        for output_name in output_facies_names:
            prob_log_name = prefix_prob_logs + '_' + str(output_name)
            if debug_level >= Debug.ON:
                print('Create blocked well log for {}'.format(prob_log_name))
            prob_log = blocked_wells.properties.create(prob_log_name, roxar.GridPropertyType.continuous, np.float32)
            prob_values = blocked_wells.generate_values(discrete=False, fill_value=-1.0)

            for code, name in code_names.items():
                key = (output_name, name)
                prob_value = conditional_prob_facies[key]
                for i in range(len(facies_log_values)):
                    faciesCode = facies_log_values[i]
                    if faciesCode == code:
                        # This grid cell in the blocked well is of matching facies as the facies for the probability log
                        # Assign the specified probability for the output facies
                        prob_values[i] = prob_value
            prob_log.set_values(prob_values)


def createCombinedFaciesLogForBlockedWells(project, grid_model_name, bw_name, original_facies_log_name, original_code_names,
                                           new_facies_log_name, new_code_names, mapping_between_original_and_new):
    # Original facies log code and name table and log values
    code_names, facies_log_values = getFaciesTableAndLogValuesFromBlockedWells(project, grid_model_name, bw_name, original_facies_log_name)
    if code_names is None:
        return
    # Check that code_names and original_code_names are identical
    if code_names != original_code_names:
        print('Error: Specified facies table (code_names) for original facies log is different from facies table in original facies log')
        return
    # Create space for new facies log
    blocked_wells = getBlockedWells(project, grid_model_name, bw_name)
    new_facies_log = blocked_wells.properties.create(new_facies_log_name, roxar.GridPropertyType.discrete, np.int32)
    values = blocked_wells.generate_values(discrete=True, fill_value=0)

    # Create array mapping from old to new facies code
    new_code_for_old_code = np.zeros((len(original_code_names)+1),np.int32)
    for original_facies, new_facies in mapping_between_original_and_new.items():
        found = False
        original_code = None
        for code, name in original_code_names.items():
            if name == original_facies:
                original_code = code
                found = True
                break
        if not found:
            print('Error: The facies name {} is not found in original facies log'.format(original_facies))
            return

        found = False
        new_code = None
        for code, name in new_code_names.items():
            if name == new_facies:
                new_code = code
                found = True
                break
        if not found:
            print('Error: The facies name {} is not found in new facies log'.format(new_facies))
            return

        new_code_for_old_code[original_code] = new_code

    # For each new facies
    for i in range(len(facies_log_values)):
        code = facies_log_values[i]
        new_code = new_code_for_old_code[code]
        values[i] = int(new_code)
    new_facies_log.set_values(values)
    new_facies_log.code_names = new_code_names
    print('Blocked well log {} created/updated'.format(new_facies_log_name))
