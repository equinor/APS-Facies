#!/bin/env python
''' 
Description: This script can be used to create binary (0/1) logs or probability logs from facies logs for blocked wells.
             The script read a specified blocked well set and find all wells having a specified facies log name.
             All the facies names found in the facies log are used when creating probability logs, one log per facies.
             The user of the script can in addition specify additional facies names in an input list. These additional
             facies names which are not equal to any facies in the facies logs, can be regarded as unobserved facies
             but nevertheless facies that the user want to include in the APS facies model. So it is important to
             also include these facies to ensure that these facies get 0 probability in blocked well grid cells in
             probability cubes created for these facies.

Input:       Grid model name, 
             name of blocked well set, 
             name of facies log which must exist for at least some wells in the blocked well set, 
             a prefix of output probability logs for each facies,
             list of additional (unobserved) facies that one want to create a probability log for.

Output:      New logs are created in the blocked well set with defined values in wells having the specified facies log
'''
#import importlib
import roxar
import numpy as np
import src.utils.roxar.modifyBlockedWellData
#importlib.reload(src.utils.roxar.modifyBlockedWellData)
from src.utils.roxar.modifyBlockedWellData import createProbabilityLogs

if __name__ == '__main__':
    # -------- Project/user specific assignment to be set by the user -----------
    grid_model_name = 'GridModelFine'
    blocked_wells_set_name = 'BW'
    input_facies_log_name = 'Deterministic_facies'
    prefix_prob_logs = 'Prob'
    assign_binary_probabilities = False

    # Case: assign_binary_probabilities = True
    # Optionally specify additional output facies logs for facies names not observed in the facies log
    additional_unobserved_facies_list = []

    # Case: assign_binary_probabilities = False 
    # In this case the user must specify a probability for each facies in the output probability logs. 
    # The output facies can have different facies names than the facies names used in the input facies log.
    # Specify output_facies_names as list of the facies names of the output probability logs.
    # Also specify conditioned probability for new facies given observed facies in input facies log
    output_facies_names = ['F1', 'F2', 'F3', 'F4', 'F5']
    conditional_prob_facies = { ('F1','A'): 1.0,
                                ('F2','A'): 0.0,
                                ('F3','A'): 0.0,
                                ('F4','A'): 0.0,
                                ('F5','A'): 0.0,
                                
                                ('F1','B'): 0.0,
                                ('F2','B'): 1.0,
                                ('F3','B'): 0.0,
                                ('F4','B'): 0.0,
                                ('F5','B'): 0.0,
                                
                                ('F1','C'): 0.0,
                                ('F2','C'): 0.0,
                                ('F3','C'): 1.0,
                                ('F4','C'): 0.0,
                                ('F5','C'): 0.0,
                                
                                ('F1','D'): 0.0,
                                ('F2','D'): 0.0,
                                ('F3','D'): 0.0,
                                ('F4','D'): 0.5,
                                ('F5','D'): 0.5
                                }
    
    #  ------- End of user specific input --------------------------------------

    if assign_binary_probabilities:
        print('Calculate probability logs as binary logs')

        createProbabilityLogs(project, grid_model_name, 
                              bw_name=blocked_wells_set_name, 
                              facies_log_name=input_facies_log_name, 
                              additional_unobserved_facies_list=additional_unobserved_facies_list, 
                              prefix_prob_logs=prefix_prob_logs)
    else:
        print('Calculate probability logs using specified conditional probabilities:')
        for key, prob_value in conditional_prob_facies.items():
            print('Prob({}| {}) = {}'.format(key[0], key[1], prob_value))

        createProbabilityLogs(project, grid_model_name, 
                              bw_name=blocked_wells_set_name, 
                              facies_log_name=input_facies_log_name, 
                              output_facies_names=output_facies_names,
                              conditional_prob_facies=conditional_prob_facies,
                              prefix_prob_logs=prefix_prob_logs)
