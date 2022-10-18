from aps.rms_jobs.APS_main import run as run_truncation
from aps.rms_jobs.APS_normalize_prob_cubes import run as run_normalization
from aps.rms_jobs.APS_simulate_gauss_singleprocessing import run as run_simulation
from aps.rms_jobs.updateAPSModelFromFMU import run as run_update_fmu_variables_in_model_file
from aps.rms_jobs.import_fields_from_disk import run as run_import_fields
from aps.rms_jobs.export_fields_to_disk import run as run_export_fields
from aps.rms_jobs.export_simbox_grid_to_disk import run as run_export_aps_grid
from aps.rms_jobs.create_simulation_grid import run as run_create_simulation_grid
from aps.rms_jobs.check_grid_index_origin import run as run_check_grid_index_origin
from aps.rms_jobs.export_fmu_config_files import run as run_export_fmu_config_files
from aps.rms_jobs.copy_rms_param_trend_to_fmu_grid import run as  run_copy_rms_param_trend_to_fmu_grid
from aps.utils.decorators import loggable, output_version_information
from aps.utils.fmu import fmu_aware_model_file
from aps.utils.io import create_temporary_model_file
from aps.utils.roxar.job import JobConfig, classify_job_configuration

import roxar.rms
import sys


def run(config):
    # NOTE: The variable `project`, is added to `run`'s scope by RMS
    # `project` is NOT available outside of the `run` method (in RMS)
    #
    # While running locally (i.e. using the rms-mock), the `project` variable
    # is injected into the global (__builtin__) namespace, and is thus available whenever one imports roxar

    @classify_job_configuration(roxar, project)  # noqa
    @loggable
    @output_version_information
    def execute(job: JobConfig):
        if job.error_message:
            raise ValueError(job.error_message)
        with create_temporary_model_file(job.model) as model_file:
            kwargs = job.get_parameters(model_file)

            if job.export_fmu_config_files:
                run_export_fmu_config_files(**kwargs)
            if job.run_fmu_workflows and job.create_fmu_grid:
                run_create_simulation_grid(**kwargs)
            run_check_grid_index_origin(**kwargs)
            if not kwargs['use_constant_probabilities']:
                run_normalization(**kwargs)
            if job.update_model_with_fmu_variables:
                run_update_fmu_variables_in_model_file(**kwargs)
            if job.run_fmu_workflows:
                run_copy_rms_param_trend_to_fmu_grid(**kwargs)
            with fmu_aware_model_file(**kwargs):
                if job.simulate_fields:
                    run_simulation(**kwargs)
                    if job.run_fmu_workflows:
                        run_export_aps_grid(**kwargs)
                        run_export_fields(**kwargs)

                        run_import_fields(
                            load_dir=kwargs['fmu_export_location'],
                            geo_grid_name=kwargs['rms_grid_name'],
                            **kwargs
                        )
                else:
                    run_import_fields(
                        geo_grid_name=kwargs['rms_grid_name'],
                        **kwargs
                    )

            run_truncation(**kwargs)

            # Ensure traceback is on per default
            sys.excepthook = sys.__excepthook__

            print('Finished')
    execute(config)
