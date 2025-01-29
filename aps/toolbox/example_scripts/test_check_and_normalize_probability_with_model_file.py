# Example using dictionary with input parameters

from aps.toolbox import check_and_normalise_probability
from aps.utils.constants.simple import Debug, ProbabilityTolerances

print(f'Run script: {check_and_normalise_probability.__file__}  ')
print('Example using APS model file')

# Define input parameters
input_dict = {
    'project': project,
    'aps_model_file': 'APS.xml',
    'overwrite': False,
    'debug_level': Debug.VERBOSE,
    'tolerance_of_probability_normalisation': 0.1,
    'max_allowed_fraction_of_values_outside_tolerance': 0.01,
}

check_and_normalise_probability.run(input_dict)
