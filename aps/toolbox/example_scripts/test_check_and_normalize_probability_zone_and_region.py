# Example using dictionary with input parameters

from aps.toolbox import check_and_normalise_probability
from aps.utils.constants.simple import Debug

print(f'Run script: {check_and_normalise_probability.__file__}  ')
print('This example use regions.')

# Define input parameters

# Modelled facies for each zone can vary from zone to zone
modelling_facies_per_zone_region_dict = {
    (1, 1): ['F1', 'F2', 'F3'],
    (1, 2): ['F1', 'F3'],
    (1, 3): [
        'F2',
        'F3',
    ],
    (1, 4): ['F1', 'F2', 'F3'],
    (2, 1): ['F1', 'F2'],
    (2, 2): ['F1', 'F3'],
    #    (2,3): ["F2", "F3"],
    (2, 4): ['F1', 'F2', 'F3'],
    (4, 5): ['F1', 'F2', 'F3'],
}
prob_param_names_dict = {
    'F1': 'Prob_zone_region_F1',
    'F2': 'Prob_zone_region_F2',
    'F3': 'Prob_zone_region_F3',
}

input_dict = {
    'project': project,
    'grid_model_name': 'GridModelFine',
    'region_param_name': 'DiscreteParam',
    'modelling_facies_per_zone_region': modelling_facies_per_zone_region_dict,
    'prob_param_per_facies': prob_param_names_dict,
    'overwrite': False,
    'debug_level': Debug.OFF,
    'tolerance_of_probability_normalisation': 0.16,
    'max_allowed_fraction_of_values_outside_tolerance': 0.05,
    'stop_on_error': False,
    'report_zone_regions': True,
}

check_and_normalise_probability.run(input_dict)
