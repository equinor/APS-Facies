---
title: Redefine or merge blocked well facies logs
---

## Utility script to redefine or merge facies in blocked well logs

**Description**
: Python script to merge or redefine blocked well facies logs.

**Dependency**
: The API `rmsapi` following the RMS installation and the python module `aps.toolbox` following the APS plugin installation.

**Input**
: Blocked well set, facies log, specification of new facies names and code, specification of how to map original to new facies.

**Output**
: A new blocked well facies log.

The utility script `create_redefined_blocked_facies_log.py`:

### Alternative ways to implement the use of this script

- Make your own Python script, define all input in your script with an input dictionary and call the utility scripts run function with the input dictionary

- Make your own Python script and specify the keyword `model_file_name` and a yml model file specifying the input.

!!! NOTE

    Use the Python script as a Python job in RMS since it applies the API `rmsapi` from RMS.

### Example of a Python script using a yml configuration file (model file) as input

In this case the input data directory contains the keyword `model_file_name` to specify the input yml configuration file.

```python
from aps.toolbox import create_redefined_blocked_facies_log
from aps.utils.constants.simple import Debug


print(f"Run script: {create_redefined_blocked_facies_log.__file__}")


params = {
    "project": project,
    "debug_level": Debug.VERBOSE,
    "model_file_name": "examples/test_redefine_blocked_facies_log.xml",
    "realization_number": project.current_realisation,
}

create_redefined_blocked_facies_log.run(params)
```

### Example 1 yml file format

This example will merge and rename facies.

```yaml
MergeFaciesLog:
  GridModelName: GridModelFine
  BlockedWells: BW3
  OriginalFaciesLogName: FaciesEx1
  NewFaciesLogName: TestMergedFacies2Yml
  NewFaciesCodes:
    1: A
    2: B
    3: C
  FromOldToNewFacies:
    F1: A
    F2: A
    F3: B
    F4: B
    F5: C
    F6: C
```

### Example of a Python script where all input is specified within the script

In this case the input data directory contains all input data needed and the keyword `model_file_name` is not used.

```python
from aps.toolbox import create_redefined_blocked_facies_log
from aps.utils.constants.simple import Debug

print(f"Run script: {create_redefined_blocked_facies_log.__file__}")

new_code_names = {
    1: "A",
    2: "B",
    3: "C",
}
# Original facies log has facies names F1, F2, F3, F4, F5, F6
# New facies log has facies names A,B,C
mapping = {
    "F1": "A",
    "F2": "A",
    "F3": "B",
    "F4": "B",
    "F5": "C",
    "F6": "C",
}

params = {
    "project": project,
    "debug_level": Debug.VERBOSE,
    "grid_model_name": "GridModelFine",
    "bw_name": "BW3",
    "original_facies_log_name": "FaciesEx1",
    "new_facies_log_name": "TestMergedFacies1",
    "new_code_names": new_code_names,
    "mapping_between_original_and_new": mapping,
    "realization_number": project.current_realisation,
}

create_redefined_blocked_facies_log.run(params)
```
