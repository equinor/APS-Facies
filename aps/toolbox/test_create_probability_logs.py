# Example using dictionary with input parameters

from aps.toolbox import create_probability_logs
from aps.utils.constants.simple import Debug

print(f"Run script: {create_probability_logs.__file__}  ")

# Define input parameters

# Modelled facies for each zone can vary from zone to zone
modelling_facies_dict = {
    1: ["F1", "F2", "F3"],
    2: ["F1", "F2", "F3"],
    3: ["F1", "F2", "F3"],
    4: ["F1", "F2", "F3"],
    5: ["F1", "F2", "F3"],
    6: ["F1", "F2", "F3"],
}
# Observed facies for zone 1 and 6 is A, B, C, D
# Observed facies for zone 2,3,4,5 is A, B, C
# Prob for modelled facies F1 is set to 1 where A is observed
# Prob for modelled facies F2 is set to 1 where B is observed
# Prob for modelled facies F3 is set to 1 where C is observed
# Where observed facies is D in zone 1 and 6:
#   F1 is assigned prob = 0.7
#   F2 is assigned prob = 0.2
#   F3 is assigned prob = 0.1
conditional_prob_facies ={
    (1, "F1", "A"): 1.0,
    (1, "F2", "A"): 0.0,
    (1, "F3", "A"): 0.0,
    (1, "F1", "B"): 0.0,
    (1, "F2", "B"): 1.0,
    (1, "F3", "B"): 0.0,
    (1, "F1", "C"): 0.0,
    (1, "F2", "C"): 0.0,
    (1, "F3", "C"): 1.0,
    (1, "F1", "D"): 0.7,
    (1, "F2", "D"): 0.2,
    (1, "F3", "D"): 0.1,

    (2, "F1", "A"): 1.0,
    (2, "F2", "A"): 0.0,
    (2, "F3", "A"): 0.0,
    (2, "F1", "B"): 0.0,
    (2, "F2", "B"): 1.0,
    (2, "F3", "B"): 0.0,
    (2, "F1", "C"): 0.0,
    (2, "F2", "C"): 0.0,
    (2, "F3", "C"): 1.0,

    (3, "F1", "A"): 1.0,
    (3, "F2", "A"): 0.0,
    (3, "F3", "A"): 0.0,
    (3, "F1", "B"): 0.0,
    (3, "F2", "B"): 1.0,
    (3, "F3", "B"): 0.0,
    (3, "F1", "C"): 0.0,
    (3, "F2", "C"): 0.0,
    (3, "F3", "C"): 1.0,

    (4, "F1", "A"): 1.0,
    (4, "F2", "A"): 0.0,
    (4, "F3", "A"): 0.0,
    (4, "F1", "B"): 0.0,
    (4, "F2", "B"): 1.0,
    (4, "F3", "B"): 0.0,
    (4, "F1", "C"): 0.0,
    (4, "F2", "C"): 0.0,
    (4, "F3", "C"): 1.0,

    (5, "F1", "A"): 1.0,
    (5, "F2", "A"): 0.0,
    (5, "F3", "A"): 0.0,
    (5, "F1", "B"): 0.0,
    (5, "F2", "B"): 1.0,
    (5, "F3", "B"): 0.0,
    (5, "F1", "C"): 0.0,
    (5, "F2", "C"): 0.0,
    (5, "F3", "C"): 1.0,

    (6, "F1", "A"): 1.0,
    (6, "F2", "A"): 0.0,
    (6, "F3", "A"): 0.0,
    (6, "F1", "B"): 0.0,
    (6, "F2", "B"): 1.0,
    (6, "F3", "B"): 0.0,
    (6, "F1", "C"): 0.0,
    (6, "F2", "C"): 0.0,
    (6, "F3", "C"): 1.0,
    (6, "F1", "D"): 0.7,
    (6, "F2", "D"): 0.2,
    (6, "F3", "D"): 0.1,
}

input_dict = {
    "project":                   project,
    "debug_level":               Debug.VERBOSE,
    "grid_model_name":           "GridModelFine",
    "bw_name":                   "BW4",
    "facies_log_name":           "Facies",
    "zone_log_name":             "Zone",
    "modelling_facies_per_zone": modelling_facies_dict,
    "prefix_prob_logs":          "Prob",
    "conditional_prob_facies":   conditional_prob_facies,
}

create_probability_logs.run(input_dict)
