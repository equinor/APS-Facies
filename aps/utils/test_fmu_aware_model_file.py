from aps.utils.fmu import fmu_aware_model_file
from aps.utils.constants.simple import Debug
from aps.algorithms.APSModel import APSModel


aps_model_file = 'aps.xml'
output_aps_model_file = 'aps_out.xml'
aps_model = APSModel(aps_model_file)
debug_level = Debug.VERY_VERBOSE
ertbox_grid_model_name = 'ERTBOX'
fmu_mode = True
kwargs ={
    'project': project,
    'model_file': aps_model_file,
    'output_model_file': output_aps_model_file,
    'fmu_mode': fmu_mode,
    'aps_model': aps_model,
    'debug_level': debug_level,
    'fmu_simulation_grid_name': ertbox_grid_model_name,
    'rms_grid_name': aps_model.grid_model_name,
    'fmu_use_residual_fields': aps_model.fmu_use_residual_fields,
}

def run(**kwargs):
    with fmu_aware_model_file(**kwargs):
        print("Called fmu_aware_model_file")


if __name__ == "__main__":
    run(**kwargs)
