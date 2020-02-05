import json
from base64 import b64decode
from functools import wraps

from pathlib import Path
from typing import Dict

from src.algorithms.APSModel import APSModel
from src.utils.constants.simple import Debug
from src.utils.decorators import cached
from src.utils.fmu import get_export_location, get_ert_location


class JobConfig:
    def __init__(self, roxar, project, config: Dict):
        self.roxar = roxar
        self.project = project
        self._config = config

    def get_parameters(self, model_file):
        aps_model = APSModel(model_file)  # Represents the ORIGINAL APS model
        return {
            'roxar': self.roxar,
            'project': self.project,
            'model_file': model_file,
            'output_model_file': model_file,
            'global_variables': self.global_variables_file,
            'max_fmu_grid_depth': self.max_fmu_grid_depth,
            'fmu_mode': self.run_fmu_workflows,
            'fmu_simulation_grid_name': self.fmu_grid_name,
            'rms_grid_name': aps_model.grid_model_name,
            'fmu_export_location': get_export_location(),
            'aps_model': aps_model,
            'use_constant_probabilities': aps_model.use_constant_probability,
            'workflow_name': self.roxar.rms.get_running_workflow_name(),
            'seed_log_file': None,
            'write_rms_parameters_for_qc_purpose': self.write_rms_parameters_for_qc_purpose,
            'debug_level': self.debug_level,
            'max_allowed_fraction_of_values_outside_tolerance': self._max_allowed_fraction_of_values_outside_tolerance,
        }

    @property
    @cached
    def error_message(self):
        export_error = self._config['errorMessage']
        if export_error:
            return export_error
        if self.fmu_mode:
            aps_model = APSModel.from_string(self.model, debug_level=None)
            for zone_model in aps_model.zone_models:
                if not zone_model.grid_layout:
                    return (
                           f'The zone with code {zone_model.zone_number} does not have any conformity specified. '
                           f'This is required, when running in ERT / AHM.'
                    )
        return None

    @property
    @cached
    def model(self):
        return b64decode(self._config['model']).decode('UTF-8')

    @property
    def create_fmu_grid(self):
        return (
            self._config['fmu']['create']['value']
            and self.fmu_grid_name not in self.project.grid_models
        )

    @property
    def fmu_grid_name(self):
        return self._config['fmu']['simulationGrid']['current']

    @property
    def fmu_mode(self):
        return self._config['fmu']['runFmuWorkflows']['value']

    @property
    def run_fmu_workflows(self):
        return self.fmu_mode and not self._only_run_fmu_variables_update

    @property
    def _only_run_fmu_variables_update(self):
        return self._config['fmu']['onlyUpdateFromFmu']['value']

    @property
    def update_model_with_fmu_variables(self):
        return (
                self._only_run_fmu_variables_update
                or self.fmu_mode
        ) and self.global_variables_file

    @property
    def simulate_fields(self):
        # The stored value is whether to import the fields, or not
        return not self._config['options']['importFields']['value']

    @property
    def max_fmu_grid_depth(self):
        return self._config['fmu']['maxDepth']['value']

    @property
    def _max_allowed_fraction_of_values_outside_tolerance(self):
        return self._config['parameters']['maxAllowedFractionOfValuesOutsideTolerance']['selected']

    @property
    def debug_level(self):
        return Debug(self._config['parameters']['debugLevel']['selected'])

    @property
    def _config_location(self):
        if self.fmu_mode:
            return get_ert_location() / '..' / '..' / 'fmuconfig' / 'output'
        return Path(self._config['parameters']['path']['fmuParameterListLocation']['selected'])

    @property
    def global_variables_file(self):
        config_location = self._config_location
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

    @property
    def write_rms_parameters_for_qc_purpose(self):
        return (
                not self.run_fmu_workflows
                or self.debug_level >= Debug.ON
        )

    def to_json(self):
        return json.dumps(self._config)


def classify_job_configuration(roxar, project):
    def decorator(func):
        @wraps(func)
        def wrapper(config: dict):
            config = JobConfig(roxar, project, config)
            func(config)
        return wrapper
    return decorator
