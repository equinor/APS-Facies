# Example using input parameters from a dictionary

from aps.toolbox import define_facies_prob_map_dep_trend
from aps.utils.constants.simple import Debug

print(f'Run script: {define_facies_prob_map_dep_trend.__file__}  ')

selected_zones = [1, 2, 3]
zone_azimuth_values = [45.0, 35.0, 25.0]
kwargs = {
    'project': project,
    'debug_level': Debug.VERBOSE,
    'grid_model_name': 'GridModelFine',
    'zone_param_name': 'Zone',
    'facies_interpretation_param_name': 'Deterministic_facies',
    'prefix': 'ProbTestDep1',
    'selected_zones': selected_zones,
    'zone_azimuth_values': zone_azimuth_values,
    'resolution': 25,
}
define_facies_prob_map_dep_trend.run(kwargs)
