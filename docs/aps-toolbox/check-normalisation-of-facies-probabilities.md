---
title: Check normalisation of facies probabilities
---
## Utility script to check and normalize 3D facies probability parameters from RMS

**Description**
: Python script to check and normalize facies probabilities.

**Dependency**
: The API `rmsapi` following the RMS installation and the python module `aps.toolbox` following the APS plugin installation.

**Input**
: Modelling facies names for each zone, name of facies probability parameters, tolerance parameters. Optionally, an APS model file can be input.

**Output**
: Modified or new facies probability parameters.


The utility script `check_and_normalise_probability.py`:

**Alternative ways to implement the use of this script**

- Make your own Python script, define all input in your script with
 an input dictionary and call the utility scripts run function with the input dictionary

- Make your own Python script and specify the keyword `model_file_name` and a yml model file specifying the input.

!!! NOTE

    Use the Python script as a Python job in RMS since it applies the API `rmsapi`from RMS.

### Example of a Python script using APS model file as input
In this case the input data directory contains the keyword `model_file_name` to specify an existing APS model file.
The APS model file can be exported from the APS job in RMS.

```python

from aps.toolbox import check_and_normalise_probability
from aps.utils.constants.simple import Debug, ProbabilityTolerances

print(f"Run script: {check_and_normalise_probability.__file__}")
print("Example using APS model file")

# Define input parameters
input_dict = {
    "project": project,
    "aps_model_file": "APS.xml",
    "overwrite": False,
    "debug_level": Debug.VERBOSE,
    "tolerance_of_probability_normalisation": 0.1,
    "max_allowed_fraction_of_values_outside_tolerance": 0.01
}

check_and_normalise_probability.run(input_dict)
```

### Example of a Python script where all input is specified in the script
In this case facies to use per zone, facies probability parameters, and tolerances are specified in the script.

This example does not use regions, only zones.

```python
from aps.toolbox import check_and_normalise_probability
from aps.utils.constants.simple import Debug, ProbabilityTolerances

print(f"Run script: {check_and_normalise_probability.__file__}")
print("Example with zones.")
# Define input parameters for specific zones
modelling_facies_per_zone_dict = {
    1: ["F1", "F2", "F3", "F4", "F5"],
    3: ["F1", "F2", "F3", "F4", "F5"],
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
    "grid_model_name": "GridModelFine",
    "modelling_facies_per_zone": modelling_facies_per_zone_dict,
    "prob_param_per_facies": prob_param_names_dict,
    "overwrite": False,
    "debug_level": Debug.VERBOSE,
    "tolerance_of_probability_normalisation": ProbabilityTolerances.MAX_ALLOWED_DEVIATION_BEFORE_ERROR,
    "max_allowed_fraction_of_values_outside_tolerance": ProbabilityTolerances.MAX_ALLOWED_FRACTION_OF_VALUES_OUTSIDE_TOLERANCE,
    "report_zone_regions": True,
}

check_and_normalise_probability.run(input_dict)
```

### Example of a Python script where all input is specified in the script
In this case facies to use per zone and region pair, facies probability parameters, and tolerances are specified in the script.

This example uses both zone and regions.
```python
from aps.toolbox import check_and_normalise_probability
from aps.utils.constants.simple import Debug

print(f"Run script: {check_and_normalise_probability.__file__}")
print("This example use regions.")

# Define input parameters

# Modelled facies for each zone can vary from zone to zone
modelling_facies_per_zone_region_dict = {
    (1, 1): ["F1", "F2", "F3"],
    (1, 2): ["F1", "F3"],
    (1, 3): ["F2", "F3"],
    (1, 4): ["F1", "F2", "F3"],
    (2, 1): ["F1", "F2"],
    (2, 2): ["F1", "F3"],
    (2, 3): ["F2", "F3"],
    (2, 4): ["F1", "F2", "F3"],
    (4, 5): ["F1", "F2", "F3"],
}

prob_param_names_dict = {
    "F1": "Prob_zone_region_F1",
    "F2": "Prob_zone_region_F2",
    "F3": "Prob_zone_region_F3",
}

input_dict = {
    "project": project,
    "grid_model_name": "GridModelFine",
    "region_param_name": "DiscreteParam",
    "modelling_facies_per_zone_region": modelling_facies_per_zone_region_dict,
    "prob_param_per_facies": prob_param_names_dict,
    "overwrite": False,
    "debug_level": Debug.OFF,
    "tolerance_of_probability_normalisation": 0.16,
    "max_allowed_fraction_of_values_outside_tolerance": 0.05,
    "stop_on_error": False,
    "report_zone_regions": True,
}

check_and_normalise_probability.run(input_dict)
```
