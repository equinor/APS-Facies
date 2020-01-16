from src.rms_jobs.APS_main import run as run_truncation
from src.rms_jobs.APS_normalize_prob_cubes import run as run_normalization
from src.rms_jobs.APS_simulate_gauss_singleprocessing import run as run_simulation
from src.rms_jobs.updateAPSModelFromFMU import run as run_update_fmu_variables_in_model_file
from src.rms_jobs.update_trend_location_relative_to_fmu import run as run_update_trend_location
from src.rms_jobs.import_fields_from_disk import run as run_import_fields
from src.rms_jobs.export_fields_to_disk import run as run_export_fields
from src.rms_jobs.export_simbox_grid_to_disk import run as run_export_aps_grid
from src.rms_jobs.create_simulation_grid import run as run_create_simulation_grid

from src.utils.decorators import loggable
from src.utils.fmu import fmu_aware_model_file
from src.utils.io import create_temporary_model_file
from src.utils.roxar.job import JobConfig


@loggable
def run(config):
    config = JobConfig(config)
    if config.error_message:
        raise ValueError(config.error_message)
    with create_temporary_model_file(config.model) as model_file:
        kwargs = config.get_parameters(model_file)

        if not kwargs['use_constant_probabilities']:
            run_normalization(**kwargs)
        if config.run_fmu_workflows:
            if config.create_fmu_grid:
                run_create_simulation_grid(**kwargs)

            run_update_trend_location(**kwargs)
        if config.update_model_with_fmu_variables:
            run_update_fmu_variables_in_model_file(**kwargs)
        with fmu_aware_model_file(**kwargs):
            if config.simulate_fields:
                run_simulation(**kwargs)
                if config.run_fmu_workflows:
                    run_export_aps_grid(**kwargs)
                    run_export_fields(**kwargs)

                    run_import_fields(
                        load_dir=kwargs['fmu_export_location'],
                        grid_name=kwargs['rms_grid_name'],
                        **kwargs
                    )
            else:
                run_import_fields(
                    grid_name=kwargs['rms_grid_name'],
                    **kwargs
                )

        run_truncation(**kwargs)
