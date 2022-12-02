# Example using dictionary with input parameters

from aps.toolbox import check_and_normalise_probability
from aps.utils.constants.simple import Debug, ProbabilityTolerances

print(f"Run script: {check_and_normalise_probability.__file__}  ")
print("Example with zones.")
# Define input parameters
modelling_facies_per_zone_dict = {
    1: ["F1", "F2", "F3", "F4", "F5"],
#    2: ["F1", "F2", "F3", "F4", "F5"],
    3: ["F1", "F2", "F3", "F4", "F5"],
#    4: ["F1", "F2", "F3", "F4", "F5"],
    5: ["F1", "F2", "F3", "F4", "F5"],
    6: ["F1", "F2", "F3", "F4", "F5"],
}
prob_param_names_dict = {
    "F1": "Prob_F1",
    "F2": "Prob_F2",
    "F3": "Prob_F3",
    "F4": "Prob_F4",
    "F5": "Prob_F5",
}

input_dict = {
    "project": project,
    "grid_model_name":  "GridModelFine",
    "modelling_facies_per_zone":  modelling_facies_per_zone_dict,
    "prob_param_per_facies": prob_param_names_dict,
    "overwrite":  False,
    "debug_level":  Debug.VERBOSE,
    "tolerance_of_probability_normalisation": ProbabilityTolerances.MAX_ALLOWED_DEVIATION_BEFORE_ERROR,
    "max_allowed_fraction_of_values_outside_tolerance": ProbabilityTolerances.MAX_ALLOWED_FRACTION_OF_VALUES_OUTSIDE_TOLERANCE,
    "report_zone_regions": True,
}

check_and_normalise_probability.run(input_dict)
