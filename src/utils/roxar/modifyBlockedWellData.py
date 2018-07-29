#!/bin/env python
import roxar
import numpy as np

def getBlockedWells(project, grid_model_name,bw_name):
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
    blocked_wells =  getBlockedWells(project, grid_model_name, bw_name)
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

    blocked_wells =  getBlockedWells(project, grid_model_name, blocked_wells_set_name)
    if blocked_wells == None:
        return None, None
    if blocked_wells.is_empty(realization_number):
        print('Error: Specified blocked wells {} in grid model {} for realization {} is empty'
              ''.format(blocked_wells_set_name, grid_model_name, str(realization_number+1)))
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


def createProbabilityLogs(project, grid_model_name, bw_name='BW', facies_log_name='Facies', additional_unobserved_facies_list = None, 
                          prefix_prob_logs='Prob_',realization_number=0):
    """ Get Facies log from blocked wells and create probability logs that have values 0.0 or 1.0 for each facies.
        It is possible to specify a list of additional facies names for facies that should be modelled, but is not observed.
        Probability logs for these uncobserved facies will only contain 0 as value since the facies is not observed.  """

    code_names, facies_log_values = getFaciesTableAndLogValuesFromBlockedWells(project, grid_model_name, bw_name, facies_log_name, realization_number)
    blocked_wells = getBlockedWells(project, grid_model_name,bw_name)
    if blocked_wells == None:
        return
    # Loop over all facies name in facies log and create a probability log for each of them
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

def createCombinedFaciesLogForBlockedWells(project, grid_model_name, bw_name, original_facies_log_name, original_code_names, 
                                           new_facies_log_name, new_code_names, mapping_between_original_and_new):
    # Original facies log code and name table and log values
    code_names, facies_log_values = getFaciesTableAndLogValuesFromBlockedWells(project, grid_model_name, bw_name, original_facies_log_name)
    if code_names == None:
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
                originalCode = code
                found = True
                break
        if not found:
            print('Error: The facies name {} is not found in original facies log'.format(original_facies))
            return

        found = False
        new_code = None
        for code, name in new_code_names.items():
            if name == new_facies:
                newCode = code
                found = True
                break
        if not found:
            print('Error: The facies name {} is not found in new facies log'.format(new_facies))
            return
        
        new_code_for_old_code[originalCode] = newCode


    # For each new facies
    for i in range(len(facies_log_values)):
        code = facies_log_values[i]
        new_code = new_code_for_old_code[code]
        values[i] = int(new_code)
    new_facies_log.set_values(values)
    new_facies_log.code_names = new_code_names
    print('Blocked well log {} created/updated'.format(new_facies_log_name))
