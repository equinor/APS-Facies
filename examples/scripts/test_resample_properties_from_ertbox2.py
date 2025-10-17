# Example using run_copy_rms_param_to_ertbox with model file as input

from aps.toolbox import copy_rms_param_to_ertbox_grid
from aps.utils.constants.simple import Debug

print(f'Run script: {copy_rms_param_to_ertbox_grid.__file__}  ')

params = {
    'project': project,
    'model_file_name': 'examples/resample_properties_from_ertbox.yml',
    'debug_level': Debug.VERBOSE,
}
copy_rms_param_to_ertbox_grid.run(params, project.seed)
