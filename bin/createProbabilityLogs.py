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
    grid_model_name = 'GridModel2'
    blocked_wells_set_name = 'BW'
    facies_log_name = 'Facies'
    prefix_prob_logs = 'Prob'
    additional_unobserved_facies_list = ['F6']
    #  ------- End of user specific input --------------------------------------

    createProbabilityLogs(project, grid_model_name, 
                          bw_name=blocked_wells_set_name, 
                          facies_log_name=facies_log_name, 
                          additional_unobserved_facies_list=additional_unobserved_facies_list,
                          prefix_prob_logs=prefix_prob_logs)
