# Example using run_copy_rms_param_to_ertbox with input parameters

from aps.toolbox import copy_rms_param_to_ertbox_grid
from aps.utils.constants.simple import Debug

print(f"Run script: {copy_rms_param_to_ertbox_grid.__file__}  ")

params ={
    "project": project,
    "debug_level": Debug.ON,
    "parameter_names": {
        1: ["Perm", "Poro"],
        2: ["Perm", "Poro"],
        3: ["Perm", "Poro"],
        4: ["Perm", "Poro"],
        5: ["Perm", "Poro"],
        6: ["Perm", "Poro"],
    },
    "conformity": {
        1: "TopConform",
        2: "Proportional",
        3: "BaseConform",
        4: "TopConform",
        5: "BaseConform",
        6: "BaseConform",
    },
    "grid_model_name": "GridModelFine",
    "zone_param_name": "Zone",
    "ertbox_grid_name": "ERTBOX",
    "extrapolation_method": "repeat",
    "save_active": True,
}
copy_rms_param_to_ertbox_grid.run(params)

