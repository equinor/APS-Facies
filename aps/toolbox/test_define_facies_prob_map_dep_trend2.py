# Example using model file as input
from aps.toolbox import define_facies_prob_map_dep_trend
from aps.utils.constants.simple import Debug

print(f"Run script: {define_facies_prob_map_dep_trend.__file__}  ")

kwargs = {
    "project": project,
    "debug_level": Debug.VERBOSE,
    "model_file_name": "examples/test_define_prob_map_dep_trend2.xml",
}
define_facies_prob_map_dep_trend.run(kwargs)
