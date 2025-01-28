#!/bin/env python

from aps.toolbox import redefine_zones_in_aps_model
from aps.utils.constants.simple import Debug

print(f"Run script: {redefine_zones_in_aps_model.__file__}  ")

new_zones = {
    1: "Zone_A",
    2: "Zone_B",
    3: "Zone_C2",
    4: "Zone_C1",
    5: "Zone_D",
}
old_zones = {
    1: "Zone_A3_orig",
    2: "Zone_A2_orig",
    3: "Zone_A1_orig",
    4: "Zone_B2_orig",
    5: "Zone_B1_orig",
    6: "Zone_C_orig",
    7: "Zone_D_orig",
}

# For each new zone, specify a list of which old zones to merge together.
# The first old zone in the list is used as the APS model for the new zone.
# A requirement is that the old zones in the list are neighbours so that they can be merged.
# A split of old zone into multipl new zones is done by specifying the same old zone name
# for each of the new zones.
zone_mapping = {
    "Zone_A":  ["Zone_A3_orig", "Zone_A2_orig", "Zone_A1_orig"],
    "Zone_B":  ["Zone_B1_orig", "Zone_B2_orig"],
    "Zone_C2": ["Zone_C_orig"],
    "Zone_C1": ["Zone_C_orig"],
    "Zone_D":  ["Zone_D_orig"],
}

params = {

    "input_aps_model_file": "examples/Test_zones_original.xml",
    "output_aps_model_file": "APS_remapped.xml",
    "new_zones": new_zones,
    "old_zones": old_zones,
    "zone_mapping": zone_mapping,
    #Optional keywords:
    "debug_level": Debug.VERBOSE,
    "grid_model_for_output_aps_model": "Test_remap_modified",
    "model_file_name": None,
}
redefine_zones_in_aps_model.run(params)
