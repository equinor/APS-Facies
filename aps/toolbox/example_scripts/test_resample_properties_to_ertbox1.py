# Example using run_copy_rms_param_to_ertbox with input parameters
# to copy 3D parameters from geogrid to ertbox grid
# and apply extrapolation if necessary in ertbox grid.

from aps.toolbox import copy_rms_param_to_ertbox_grid
from aps.utils.constants.simple import Debug

print(f"Run script: {copy_rms_param_to_ertbox_grid.__file__}  ")
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

