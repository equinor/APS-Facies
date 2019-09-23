from src.algorithms.APSModel import APSModel
from src.rms_jobs.APS_normalize_prob_cubes import run as run_normalization
from src.rms_jobs.APS_simulate_gauss_singleprocessing import run as run_simulation
from src.rms_jobs.APS_main import run as run_truncation
from src.utils.io import create_temporary_model_file

import roxar


class Config:
    def __init__(self, config):
        self._config = config

    @property
    def error_message(self):
        return self._config['errorMessage']

    @property
    def model(self):
        return self._config['model']

    @property
    def run_fmu_workflows(self):
        return self._config['options']['runFmuWorkflows']['value']


def run(config):
    config = Config(config)
    if config.error_message:
        raise ValueError(config.error_message)
    with create_temporary_model_file(config.model) as model_file:
        use_constant_probabilities = APSModel(model_file).use_constant_probability
        if not use_constant_probabilities:
            run_normalization(roxar, project, model_file=model_file)
        run_simulation(roxar, project, model_file=model_file, seed_log_file=None)
        run_truncation(roxar, project, model_file=model_file)
