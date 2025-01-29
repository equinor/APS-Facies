# Example using model file as input

from aps.toolbox import define_facies_prob_trend
from aps.utils.constants.simple import Debug

print(f'Run script: {define_facies_prob_trend.__file__}  ')

kwargs = {
    'project': project,
    'debug_level': Debug.VERBOSE,
    'model_file_name': 'examples/test_define_facies_prob_trend_common_zone_spec.yml',
}
define_facies_prob_trend.run(kwargs)
