#!/bin/env python
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
