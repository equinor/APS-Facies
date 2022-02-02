"""Sample a map to a 3D grid (zone) so the e.g. a map trend can be taken in.

JRIV/OLIA
"""
import numpy as np
import xtgeo
from aps.algorithms.APSModel import APSModel
from aps.utils.roxar.sample_map_to_grid import trend_map_to_grid_param



def run(*, project, zone_number, **kwargs):
    trend_map_name = kwargs['trend_map']
    aps_model = kwargs['aps_model']
    grid_model_name = aps_model.grid_model_name
    ertbox_grid_model_name = kwargs['fmu_simulation_grid_name']
    debug_level = kwargs['debug_level']
    result_param_name = kwargs['trend_param_name']
    zone_param_name = kwargs['zone_param_name']
    grid_model_name = aps_model.grid_model_name
    fmu_mode = kwargs['fmu_mode']


    if fmu_mode:
        trend_map_to_grid_param(project, ertbox_grid_model_name,
            trend_map_name, result_param_name,
            fmu_mode=fmu_mode,
            debug_level=debug_level)

    trend_map_to_grid_param(project, grid_model_name,
        trend_map_name, result_param_name,
        fmu_mode=fmu_mode,
        zone_number=zone_number,
        zone_param_name=zone_param_name,
        debug_level=debug_level)

if __name__ == "__main__":
    # Test example

    model_file_name = "aps_custom_trend_fmu.xml"
    zone_number = 1
    aps_model = APSModel(model_file_name)
    kwargs = {}
    kwargs['model_file'] =  model_file_name
    kwargs['trend_map']= "A"
    kwargs['trend_param_name'] = "Trend_from_map"
    kwargs['aps_model'] = aps_model
    kwargs['fmu_simulation_grid_name'] = "ERTBOXNEW"
    kwargs['debug_level'] = Debug.VERBOSE
    kwargs['zone_param_name'] = "Zone"
    kwargs['fmu_mode'] = True

    run(project=project, zone_number=zone_number, **kwargs)
