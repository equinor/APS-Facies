# Test script for prob_logs_from_original_facies_logs.py
from aps.toolbox import prob_logs_from_original_facies_logs
from aps.utils.constants.simple import Debug


params = {
    'project': project,
    'model_file': "estimate_prob_logs_example.yml",
    }

prob_logs_from_original_facies_logs.run(params)
