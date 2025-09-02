---
title: Probability trends
---
## Utility script to create trends for probability cubes (RMS3D continuous parameter for facies probabilities)

**Description**: Python script to create simple probability trends from deterministic 3D facies interpretation using conditional probabilities.

**Dependency**: The API `rmsapi` following the RMS installation and the python module `aps.toolbox` following the APS plugin installation.

**Input**: Deterministic 3D discrete parameter with facies interpretation, list of zones to make facies trend for, optionally conditional facies probabilities.

**Output**: A 3D trend parameter for each of the specified facies.

**Usage of the 3D facies probability trend parameters**: The trend parameters can be input to e.g. RMS petrosim where the trend is combined with facies probability logs to create facies probability cubes.

The utility script `define_facies_prob_trend.py`:

### Alternative ways to implement the use of this script

- Make your own Python script, define all input in your script with an input dictionary and call the utility scripts run function with the input dictionary

- Make your own Python script and specify the keyword `model_file_name` and a yml model file specifying the input.

**NOTE**: Use the Python script as a Python job in RMS since it applies the API `rmsapi` from RMS.


### Example of a Python script using a yml configuration file (model file) as input
In this case the input data directory contains the keyword `model_file_name` to specify the input yml configuration file.

```python
from aps.toolbox import define_facies_prob_trend
from aps.utils.constants.simple import Debug


print(f"Run script: {define_facies_prob_trend.__file__}")

kwargs = {
    "project": project,
    "debug_level": Debug.VERBOSE,
    "model_file_name": "examples/test_define_facies_prob_trend_common_zone_spec.yml",
}
define_facies_prob_trend.run(kwargs)
```

### Example 1 yml file format
This example will for each zone calculate volume fraction of each available facies from the input deterministic 3D facies parameter.
The result will be a constant trend value equal to the facies volume fraction for each facies for each zone.

```yaml
FaciesProbTrend:
    GridModelName: GridModelFine
    ZoneParamName: Zone
    FaciesParamName: Facies_initial_example_1
    ProbParamNamePrefix: ProbTrendEx1
    SelectedZones: 1 2 3 4 5 6
    UseConstantProbFromVolumeFraction: True

```

### Example 2 yml file format
This example will use conditional probabilities for modelled facies given interpreted facies for two zones based on the input deterministic 3D facies parameter.

The modelled facies are $F_1$, $F_2$, $F_3$, $F_4$, $F_5$

The interpreted facies in the input 3D facies parameter are: $A$, $B$, $C$, $D$

The keyword `CondProbMatrix` has keyword (zone, modelled_facies_name, interpreted_facies_name) and a conditional probability $P(M \mid I)$ is specified for modelled facies $M$ given interpreted facies $I$ for each modelled and interpreted facies and zone.
Note that sum over all modelled facies for given interpreted facies must be $1.0$.

```yaml
FaciesProbTrend:
  GridModelName: GridModelFine
  ZoneParamName: Zone
  FaciesParamName: Deterministic_facies
  ProbParamNamePrefix: ProbTrend2
  SelectedZones: 1 4
  UseConstantProbFromVolumeFraction: False
  CondProbMatrix:
    (1, F1, A): 0.90
    (1, F2, A): 0.05
    (1, F3, A): 0.0
    (1, F4, A): 0.0
    (1, F5, A): 0.05

    (1, F1, B): 0.025
    (1, F2, B): 0.95
    (1, F3, B): 0.025
    (1, F4, B): 0.0
    (1, F5, B): 0.0

    (1, F1, C): 0.0
    (1, F2, C): 0.05
    (1, F3, C): 0.90
    (1, F4, C): 0.05
    (1, F5, C): 0.0

    (1, F1, D): 0.0
    (1, F2, D): 0.0
    (1, F3, D): 0.05
    (1, F4, D): 0.95
    (1, F5, D): 0.0

    (4, F1, A): 0.90
    (4, F2, A): 0.05
    (4, F3, A): 0.0
    (4, F4, A): 0.0
    (4, F5, A): 0.05

    (4, F1, B): 0.025
    (4, F2, B): 0.95
    (4, F3, B): 0.025
    (4, F4, B): 0.0
    (4, F5, B): 0.0

    (4, F1, C): 0.0
    (4, F2, C): 0.05
    (4, F3, C): 0.90
    (4, F4, C): 0.05
    (4, F5, C): 0.0

    (4, F1, D): 0.0
    (4, F2, D): 0.0
    (4, F3, D): 0.05
    (4, F4, D): 0.95
    (4, F5, D): 0.0
```

### Example of a Python script where all input is specified within the script
In this case the input data directory contains all input data needed and the keyword `model_file_name` is not used.

The keyword for the dictionary cond_prob_matrix is of the form (`zone_number`, `modelled_facies_name`,
 `interpreted_facies_name`).

```python
from aps.toolbox import define_facies_prob_trend
from aps.utils.constants.simple import Debug

print(f"Run script: {define_facies_prob_trend.__file__}")

selected_zones = [1, 2]
cond_prob_matrix = {
    (1, "F1", "A"): 0.5,
    (1, "F2", "A"): 0.3,
    (1, "F3", "A"): 0.2,

    (1, "F1", "B"): 0.0,
    (1, "F2", "B"): 1.0,
    (1, "F3", "B"): 0.0,

    (1, "F1", "C"): 0.1,
    (1, "F2", "C"): 0.2,
    (1, "F3", "C"): 0.7,

    (1, "F1", "D"): 0.15,
    (1, "F2", "D"): 0.25,
    (1, "F3", "D"): 0.6,

    (2, "F1", "A"): 1.0,
    (2, "F2", "A"): 0.0,
    (2, "F3", "A"): 0.0,

    (2, "F1", "B"): 0.0,
    (2, "F2", "B"): 1.0,
    (2, "F3", "B"): 0.0,

    (2, "F1", "C"): 0.0,
    (2, "F2", "C"): 0.0,
    (2, "F3", "C"): 1.0,

    (2, "F1", "D"): 0.5,
    (2, "F2", "D"): 0.4,
    (2, "F3", "D"): 0.1,
}
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
```
