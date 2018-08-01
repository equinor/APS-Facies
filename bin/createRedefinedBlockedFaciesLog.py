#!/bin/env python
'''
Description:
            This script can be used to create new facies log from a specified (original) facies log for blocked wells. 
            The new facies logs can be defined by combining facies existing in the original logs such that two or more facies in the original facies log
            are combined into one new facies in the new log.

Input:      Name of grid model,
            name of blocked well set,
            name of original facies log,
            python dictionary code_names for original facies log. The format is a python dictionary with code as key and name as value.
            name of new facies log,
            python dictionary code_names for new combined facies log. The format is a python dictionary with code as key and name as value.
            python dictionary with facies names from original facies log as key and for each key the name of the facies name from the new facies log is specified.

            Comments: The dictionary associating original facies names with new facies names define which original facies names are combined 
            and what the combined facies name is.

Output:     New blocked well facies log with combined facies (re-defined) facies.

''' 
import roxar
import numpy as np
from src.utils.roxar.modifyBlockedWellData import createCombinedFaciesLogForBlockedWells

if __name__ == '__main__':
    # -------- Project/user specific assignment to be set by the user -----------
    grid_model_name = 'GridModel2'
    bw_name = 'BW'
    original_facies_log_name = 'Facies_case2'
    original_code_names = {1: 'F1',
                           2: 'F2',
                           3: 'F3',
                           4: 'F4',
                           5: 'F5',
                           6: 'F6'}

    new_facies_log_name = 'Facies_case2_combined'
    new_code_names = { 1: 'New_F01',
                       2: 'New_F02',
                       3: 'New_F03',
                       4: 'F5'}

    mapping = { 'F1':'New_F01',
                'F2':'New_F02',
                'F3':'New_F01',
                'F4':'New_F03',
                'F5':'F5',
                'F6':'New_F03'}



    #  ------- End of user specific input --------------------------------------
    createCombinedFaciesLogForBlockedWells(project, grid_model_name, bw_name, original_facies_log_name, original_code_names, 
                                           new_facies_log_name, new_code_names, mapping)
