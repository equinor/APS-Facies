---
title: Copy 3D parameters to or from ERTBOX
---

## Utility script to copy discrete and continuous 3D parameters to/from ERTBOX

**Description**: Python script to copy from geomodel grid to ERTBOX grid or from ERTBOX grid to geomodel grid.
The application can be to use ERTBOX but update petrophysical 3D parameters by ERT when not using APS,
or it can be to copy realizations from geomodel grid to ERTBOX grid to do statistical calculation of ensembles in ERTBOX.

**Dependency**: The API `rmsapi` following the RMS installation and the python module `aps.toolbox` following the APS plugin installation.

**Input**: Name of geogrid parameters and corresponding name in ERTBOX grid,
grid conformity type for each zone, grid model names zone parameter name.

**Output**: 3D parameters copied either from geomodel grid to ERTBOX grid or the other way.
When copying to ERTBOX,
also a parameter with value 0 / 1 with value 1 for each grid cell in ERTBOX grid having original value coming from the geomodel grid can be made.
This parameter is useful to filter out all extrapolated values in the ERTBOX and only use the values corresponding to geomodel grid cell values in for instance ensemble statistical calculations in ERTBOX grid.

The utility script `copy_rms_param_to_ertbox_grid.py`:

**Alternative ways to implement the use of this script**:

- Make your own Python script, define all input in your script with
 an input dictionary and call the utility scripts run function with the input dictionary

- Make your own Python script and specify the keyword `model_file_name` and a yml model file specifying the input.

**NOTE**: Use the Python script as a Python job in RMS since it applies the API `rmsapi` from RMS.

### Example of a Python script using a yml configuration file (model file) as input
In this case the input data directory contains the keyword "model_file_name" to specify the input yml configuration file.

```python
from aps.toolbox import copy_rms_param_to_ertbox_grid
from aps.utils.constants.simple import Debug


print(f"Run script: {copy_rms_param_to_ertbox_grid.__file__}")


params = {
    "project": project,
    "model_file_name": "examples/resample_properties_from_ertbox.yml",
    "debug_level": Debug.VERBOSE,
}

copy_rms_param_to_ertbox_grid.run(params)
```

### Example 1 yml file format
This example copy 3D parameters from ertbox to geogrid.

```yaml
# This model specification is used in the script to resample RMS 3D parameters
# from ertbox grid to geo grid.

Resample:
    Mode: from_ertbox_to_geo
    GridModelName: GridModelFine
    ERTBoxGridName: ERTBOX
    ZoneParam: Zone
    GeoGridParameters:
        1: PermFromErtbox2 PoroFromErtbox2
        2: PermFromErtbox2 PoroFromErtbox2
        3: PermFromErtbox2 PoroFromErtbox2
        4: PermFromErtbox2 PoroFromErtbox2
        5: PermFromErtbox2 PoroFromErtbox2
        6: PermFromErtbox2 PoroFromErtbox2

    ErtboxParameters:
        1: middle_Neslen_1_Perm middle_Neslen_1_Poro
        2: middle_Neslen_2_Perm middle_Neslen_2_Poro
        3: middle_Neslen_3_Perm middle_Neslen_3_Poro
        4: middle_Neslen_4_Perm middle_Neslen_4_Poro
        5: middle_Neslen_5_Perm middle_Neslen_5_Poro
        6: middle_Neslen_6_Perm middle_Neslen_6_Poro

    Conformity:
        1: TopConform
        2: Proportional
        3: BaseConform
        4: TopConform
        5: BaseConform
        6: BaseConform
```

### Example 2 yml file format
This example copy 3D parameters from geogrid to ertbox grid.

```yaml
# This model specification is used in the script to resample RMS 3D parameters
# from geogrid to ertbox grid.

Resample:
    Mode: from_geo_to_ertbox
    GridModelName: GridModelFine
    ERTBoxGridName: ERTBOX
    ZoneParam: Zone
    ExtrapolationMethod: repeat
    GeoGridParameters:
        1: Perm Poro
        2: Perm Poro
        3: Perm Poro
        4: Perm Poro
        5: Perm Poro
        6: Perm Poro

    Conformity:
        1: TopConform
        2: Proportional
        3: BaseConform
        4: TopConform
        5: BaseConform
        6: BaseConform

# Available extrapolation methods:
# zero, mean, extend, repeat,
# extend_layer_mean, repeat_layer_mean

# Example using run_copy_rms_param_to_ertbox with input parameters
# to copy 3D parameters from ertbox grid to geogrid.
```

### Example of a Python script where all input specification is specified in the script when copying from ertbox to geomodel grid
In this case the input data directory contains all necessary input and the keyword `model_file_name` is not used.
```python
from aps.toolbox import copy_rms_param_to_ertbox_grid
from aps.utils.constants.simple import Debug

print(f"Run script: {copy_rms_param_to_ertbox_grid.__file__}")
print(f"Copy 3D parameters from Ertbox grid to geo grid")

params ={
    "project": project,
    "debug_level": Debug.ON,
    "Mode": "from_ertbox_to_geo",
    "GeoGridParameters": {
        1: ["PermFromErtbox", "PoroFromErtbox"],
        2: ["PermFromErtbox", "PoroFromErtbox"],
        3: ["PermFromErtbox", "PoroFromErtbox"],
        4: ["PermFromErtbox", "PoroFromErtbox"],
        5: ["PermFromErtbox", "PoroFromErtbox"],
        6: ["PermFromErtbox", "PoroFromErtbox"],
    },
    "ErtboxParameters": {
        1: ["middle_Neslen_1_Perm", "middle_Neslen_1_Poro"],
        2: ["middle_Neslen_2_Perm", "middle_Neslen_2_Poro"],
        3: ["middle_Neslen_3_Perm", "middle_Neslen_3_Poro"],
        4: ["middle_Neslen_4_Perm", "middle_Neslen_4_Poro"],
        5: ["middle_Neslen_5_Perm", "middle_Neslen_5_Poro"],
        6: ["middle_Neslen_6_Perm", "middle_Neslen_6_Poro"],
    },
    "Conformity": {
        1: "TopConform",
        2: "Proportional",
        3: "BaseConform",
        4: "TopConform",
        5: "BaseConform",
        6: "BaseConform",
    },
    "GridModelName": "GridModelFine",
    "ZoneParam": "Zone",
    "ERTBoxGridName": "ERTBOX",
}

copy_rms_param_to_ertbox_grid.run(params)
```

### Example of a Python script where all input specification is specified in the script when copying from geomodel grid to ertbox grid
In this case the input data directory contains all necessary input and the keyword
 `model_file_name` is not used.

When copying from geogrid to ERTBOX grid, it is also possible to create a 0 / 1 parameter with value 1 for all grid cells in ERTBOX that corresponds to a grid cell in the geomodel grid.

This "active" parameter can be used to select only original grid cell values originating from the geomodel and remove values in the ERTBOX grid that is based on extrapolation of original grid cell values.

```python
# Example using run_copy_rms_param_to_ertbox with input parameters
# to copy 3D parameters from geogrid to ertbox grid
# and apply extrapolation if necessary in ertbox grid.

from aps.toolbox import copy_rms_param_to_ertbox_grid
from aps.utils.constants.simple import Debug

print(f"Run script: {copy_rms_param_to_ertbox_grid.__file__}")
print("Copy 3D parameter from Geo grid to Ertbox grid")

params ={
    "project": project,
    "debug_level": Debug.ON,
    "Mode": "from_geo_to_ertbox",
    "GeoGridParameters": {
        1: ["Perm", "Poro"],
        2: ["Perm", "Poro"],
        3: ["Perm", "Poro"],
        4: ["Perm", "Poro"],
        5: ["Perm", "Poro"],
        6: ["Perm", "Poro"],
    },
    "Conformity": {
        1: "TopConform",
        2: "Proportional",
        3: "BaseConform",
        4: "TopConform",
        5: "BaseConform",
        6: "BaseConform",
    },
    "GridModelName": "GridModelFine",
    "ZoneParam": "Zone",
    "ERTBoxGridName": "ERTBOX",
    "ExtrapolationMethod": "repeat",
    "SaveActiveParam": True,
}

copy_rms_param_to_ertbox_grid.run(params)
```
