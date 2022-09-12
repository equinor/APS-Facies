# Example using a dictionary with input parameters

from aps.toolbox import define_facies_prob_trend
from aps.utils.constants.simple import Debug

print(f"Run script: {define_facies_prob_trend.__file__}  ")

selected_zones = [1,2,3]
cond_prob_matrix = [
    ["F1", "A", 0.8],
    ["F2", "A", 0.1],
    ["F3", "A", 0.1],

    ["F1", "B", 0.0],
    ["F2", "B", 1.0],
    ["F3", "B", 0.0],

    ["F1", "C", 0.1],
    ["F2", "C", 0.2],
    ["F3", "C", 0.7],

    ["F1", "D", 0.1],
    ["F2", "D", 0.2],
    ["F3", "D", 0.7],
]
kwargs = {
    "project": project,
    "debug_level": Debug.VERBOSE,
    "grid_model_name": "GridModelFine",
    "zone_param_name": "Zone",
    "facies_interpretation_param_name": "Deterministic_facies",
    "prefix": "ProbTrendTest1",
    "selected_zones": selected_zones,
    "use_const_prob": False,
    "cond_prob_matrix": cond_prob_matrix,
}
define_facies_prob_trend.run(kwargs)
