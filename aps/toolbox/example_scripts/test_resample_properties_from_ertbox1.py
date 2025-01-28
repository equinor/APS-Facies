# Example using run_copy_rms_param_to_ertbox with input parameters
# to copy 3D parameters from ertbox grid to geogrid.


from aps.toolbox import copy_rms_param_to_ertbox_grid
from aps.utils.constants.simple import Debug

print(f'Run script: {copy_rms_param_to_ertbox_grid.__file__}  ')
print(f'Copy 3D parameters from Ertbox grid to geo grid')
params = {
    'project': project,
    'debug_level': Debug.ON,
    'Mode': 'from_ertbox_to_geo',
    'GeoGridParameters': {
        1: ['PermFromErtbox', 'PoroFromErtbox'],
        2: ['PermFromErtbox', 'PoroFromErtbox'],
        3: ['PermFromErtbox', 'PoroFromErtbox'],
        4: ['PermFromErtbox', 'PoroFromErtbox'],
        5: ['PermFromErtbox', 'PoroFromErtbox'],
        6: ['PermFromErtbox', 'PoroFromErtbox'],
    },
    'ErtboxParameters': {
        1: ['middle_Neslen_1_Perm', 'middle_Neslen_1_Poro'],
        2: ['middle_Neslen_2_Perm', 'middle_Neslen_2_Poro'],
        3: ['middle_Neslen_3_Perm', 'middle_Neslen_3_Poro'],
        4: ['middle_Neslen_4_Perm', 'middle_Neslen_4_Poro'],
        5: ['middle_Neslen_5_Perm', 'middle_Neslen_5_Poro'],
        6: ['middle_Neslen_6_Perm', 'middle_Neslen_6_Poro'],
    },
    'Conformity': {
        1: 'TopConform',
        2: 'Proportional',
        3: 'BaseConform',
        4: 'TopConform',
        5: 'BaseConform',
        6: 'BaseConform',
    },
    'GridModelName': 'GridModelFine',
    'ZoneParam': 'Zone',
    'ERTBoxGridName': 'ERTBOX',
}
copy_rms_param_to_ertbox_grid.run(params, project.seed)
