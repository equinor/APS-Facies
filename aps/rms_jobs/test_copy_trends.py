from aps.rms_jobs.copy_rms_param_trend_to_fmu_grid import run
from aps.algorithms.APSModel import APSModel
from aps.utils.constants.simple import Debug, ExtrapolationMethod


def test_copy_from_geo_to_ertbox_grid(project):
    aps_model_name = "aps.xml"
    fmu_mode = True
    ertbox_grid_model_name = "ERTBOX_coarse_grid"
    debug_level = Debug.VERY_VERBOSE
    extrapolation_method = ExtrapolationMethod.EXTEND_LAYER_MEAN

    aps_model = APSModel(aps_model_name)
    kwargs = {
        'aps_model_name': aps_model_name,
        'aps_model': aps_model,
        'fmu_mode': fmu_mode,
        'fmu_simulation_grid_name': ertbox_grid_model_name,
        'debug_level': debug_level,
        'extrapolation_method': extrapolation_method,
    } 
    run(project=project,
        save_region_param_to_ertbox=True,
        normalize_trend=True,
        **kwargs)


if __name__ == "__main__":
    test_copy_from_geo_to_ertbox_grid(project)
