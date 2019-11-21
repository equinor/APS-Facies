from pathlib import Path

from src.algorithms.APSModel import APSModel
from src.rms_jobs.APS_main import run as run_truncation
from src.rms_jobs.APS_normalize_prob_cubes import run as run_normalization
from src.rms_jobs.APS_simulate_gauss_singleprocessing import run as run_simulation
from src.rms_jobs.updateAPSModelFromFMU import run as run_update_fmu_variables_in_model_file
from src.rms_jobs.update_trend_location_relative_to_fmu import run as run_update_trend_location
from src.utils.io import create_temporary_model_file

import roxar


class Config:
    def __init__(self, config):
        self._config = config

    def get_parameters(self, model_file):
        return {
            'roxar': roxar,
            'project': project,
            'model_file': model_file,
            'output_model_file': model_file,
            'global_include_file': self.global_include_file,
            'max_fmu_grid_depth': self.max_fmu_grid_depth,
            'layers_per_zone': [
                self.max_fmu_grid_depth for _ in range(len(project.zones))
            ] if self.run_fmu_workflows else None,
            'fmu_mode': self.run_fmu_workflows,
            'seed_log_file': None,
            'write_rms_parameters_for_qc_purpose': False,
        }

    @property
    def error_message(self):
        return self._config['errorMessage']

    @property
    def model(self):
        return self._config['model']

    @property
    def run_fmu_workflows(self):
        return self._config['options']['runFmuWorkflows']['value']

    @property
    def max_fmu_grid_depth(self):
        return self._config['parameters']['fmu']['maxDepth']

    @property
    def global_include_file(self):
        project_location = Path(self._config['parameters']['path']['project']['selected'])
        config_location = project_location / '../input/config/aps_gui'
        file_priority = [
            'global_variables.yml',
            'global_variables.yaml',
            'global_variables.ipl',
        ]
        if config_location.exists():
            if config_location.is_dir():
                for file_name in file_priority:
                    location = config_location / file_name
                    if location.exists():
                        return str(location.absolute())
        return None


def run(config):
    config = Config(config)
    if config.error_message:
        raise ValueError(config.error_message)
    with create_temporary_model_file(config.model) as model_file:
        kwargs = config.get_parameters(model_file)
        use_constant_probabilities = APSModel(model_file).use_constant_probability
        if not use_constant_probabilities:
            run_normalization(**kwargs)
        if config.run_fmu_workflows:
            # Add a flag for whether `run_initial_ensable`, or `run_import_from_fmu` should be run
            # (user specified in the GUI)
            # We also need to get / update the truncation rule parameters (in the model file) that FMU may change
            # That is, to use a different fmu_variables file (similar / equivalent to global_variables.ipl)
            run_update_fmu_variables_in_model_file(**kwargs)
            # run_initial_ensable is equivalent to running the APS workflows ONCE
            # Once that is done, (that is the the facies realization, and GRFs with trends exists),
            # only loading from disk, and running `run_truncation` should be done
            run_update_trend_location(**kwargs)
        run_simulation(**kwargs)
        # The GRFs should not be written to RMS if Debug is not set, and we are not in FMU mode

        # Script for moving stuff from "FMU" grid to "regular" grid
        run_truncation(**kwargs)
