#!/bin/env python
# -*- coding: utf-8 -*-
# Example using model file as input

from aps.toolbox import create_probability_logs
from aps.utils.constants.simple import Debug

print(f"Run script: {create_probability_logs.__file__}  ")


# Define input parameters
input_dict ={
    'project': project,
    'model_file_name': "examples/Create_prob_logs_no_cond_prob.yml",
    'debug_level': Debug.VERBOSE,
}
create_probability_logs.run(input_dict)

