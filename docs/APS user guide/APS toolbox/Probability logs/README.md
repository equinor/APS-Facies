---
title: Probability logs
---
## Utility script to create blocked well probability logs

**Description**: Python script to create probability logs

**Dependency**: The API `rmsapi` following the RMS installation and the python module `aps.toolbox` following the APS plugin installation.

**Input**: Blocked well facies log and specification of which facies to model and which zones to use.

**Output**: One blocked well log per facies. For each grid cell in the blocked well, the probability log value takes a value from 0 to 1.

**Usage of the probability logs**: A probability log containing only 0 or 1 can be used to condition probability cubes to reproduce blocked well facies logs 100% while probabilities between 0 and 1 represents uncertainties in blocked well facies.


The utility script `create_probability_logs.py`:

### Alternative ways to implement the use of this script

- Make your own Python script, define all input in your script with an input dictionary and call the utility scripts run function with the input dictionary

- Make your own Python script and specify the keyword `model_file_name` and a yml model file specifying the input.

- NOTE: Use the Python script as a Python job in RMS since it applies the API `rmsapi` from RMS.


### Example of a Python script using a yml configuration file (model file) as input

In this case the input data directory contains the keyword `model_file_name` to specify the input yml configuration file.

```python hl_lines="6"
from aps.toolbox import create_probability_logs
from aps.utils.constants.simple import Debug

input_dict = {
    'project': project,
    'model_file_name': "test_prob_logs1.yml",
    'debug_level': Debug.VERBOSE,
}
create_probability_logs.run(input_dict)
```


### Example 1 yml file format
This example create 0/1 probability logs
The facies selected to be used vary from zone to zone.
Number of zones: 6

```yaml
ProbLogs:
    GridModelName: GridModelFine
    BlockedWells: BW3
    FaciesLogName: FaciesEx1
    ZoneLogName: Zone
    OutputPrefix: ProbEx1
    ModellingFaciesPerZone:
        1: F1 F2 F3 F4 F5 F6
        2: F1 F2 F3 F4 F5 F6
        3: F1 F2 F3 F4 F5 F6
        4: F1 F2 F3 F4 F5 F6
        5: F1 F2    F4 F5 F6
        6:    F2       F5 F6
    UseConditionalProbabilities: False
```


### Example 2 of yml file format
This example use conditional probability for modelled facies given interpreted facies.

Number of zones used: 2

Facies observed in zone 1: F1, F2, F3, F4

Facies observed in zone 6: F1, F2, F3, F4, F5

Facies chosen to be modelled for zone 1: F1, F2, F4

Facies chosen to be modelled for zone 6: F1, F4, F5

**Note**: The name of modelled facies does not have to be a subset of the interpreted/observed facies.

In this example, modelled facies names are same as interpreted facies names.

```yaml


ProbLogs:
    GridModelName: GridModelFine
    BlockedWells: BW2
    FaciesLogName: FaciesLog
    ZoneLogName: Zone
    OutputPrefix: Prob_ex_1_yml
    ModellingFaciesPerZone:
        1: F1 F2    F4
        6: F1       F4 F5
    UseConditionalProbabilities: True

    CondProbMatrix:
        (1, F1, F1): 1.0
        (1, F2, F1): 0.0
        (1, F4, F1): 0.0

        (1, F1, F2): 0.0
        (1, F2, F2): 1.0
        (1, F4, F2): 0.0

        (1, F1, F3): 0.5
        (1, F2, F3): 0.3
        (1, F4, F3): 0.2

        (1, F1, F4): 0.0
        (1, F2, F4): 0.0
        (1, F4, F4): 1.0

        (6, F1, F1): 1.0
        (6, F4, F1): 0.0
        (6, F5, F1): 0.0

        (6, F1, F2): 0.50
        (6, F4, F2): 0.50
        (6, F5, F2): 0.0

        (6, F1, F3): 0.0
        (6, F4, F3): 0.9
        (6, F5, F3): 0.1

        (6, F1, F4): 0.0
        (6, F4, F4): 1.0
        (6, F5, F4): 0.0

        (6, F1, F5): 0.0
        (6, F4, F5): 0.0
        (6, F5, F5): 1.0
```

### Example of how to specify input directly in the input python dictionary
In this case the input data directory contains all necessary input, and is not using the keyword `model_file_name`.


```python
from aps.toolbox import create_probability_logs
from aps.utils.constants.simple import Debug
# Define input parameters

# Modelled facies for each zone can vary from zone to zone. In this case regions are not used
# so the specification has region number 0.
# The key for modelling_facies_dict is (zone_number, region_number)
modelling_facies_dict = {
    (1,0): ["F1", "F2", "F3"],
    (2,0): ["F1", "F2", "F3"],
}
# Observed facies for zone 1 is A, B, C, D
# Observed facies for zone 2 is A, B, C
# Prob for modelled facies F1 is set to 1 where A is observed
# Prob for modelled facies F2 is set to 1 where B is observed
# Prob for modelled facies F3 is set to 1 where C is observed
# Where observed facies is D in zone 1 :
#    F1 is assigned prob = 0.7
#    F2 is assigned prob = 0.2
#    F3 is assigned prob = 0.1
# The dictionary conditional_prob_facies has
# key of the form (zone_number, modelled_facies_name, interpreted_facies_name)
conditional_prob_facies = {
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
}

# If the model should use regions, specify the key "region_log_name" with name of the blocked well region log.
# Only when region is not used, it is possible to use "conditional_prob_facies".
# The keyword "debug_level" is optional. Possible values are Debug.OFF, Debug.ON, Debug.VERBOSE
# and specify level of output to terminal when running the script.
input_dict = {
    "project": project,
    "debug_level": Debug.VERBOSE,
    "grid_model_name": "GridModelFine",
    "bw_name": "BW4",
    "facies_log_name": "Facies",
    "zone_log_name": "Zone",
    "modelling_facies_per_zone_region": modelling_facies_dict,
    "prefix_prob_logs": "Prob",
    "conditional_prob_facies": conditional_prob_facies,
}

create_probability_logs.run(input_dict)
```
