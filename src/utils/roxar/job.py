import json
from base64 import b64decode
from functools import wraps

from typing import Dict

from src.algorithms.APSModel import APSModel
from src.utils.constants.simple import Debug, ProbabilityTolerances, TransformType
from src.utils.decorators import cached
from src.utils.fmu import get_export_location, get_ert_location, is_initial_iteration


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
            'tolerance_of_probability_normalisation': self._tolerance_of_probability_normalisation,
            'field_file_format': self.field_file_format,
            'transform_type_grf': self._transformation_type_for_grf,
            'current_job_name': self.roxar.rms.get_running_job_name(),
            'export_fmu_config_files': self.export_fmu_config_files,
        }

    @property
    @cached
    def error_message(self):
        export_error = self._config['errorMessage']
        if export_error:
            return export_error

        if self.run_fmu_workflows:
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
    def field_file_format(self):
        try:
            return self._config['fmu']['fieldFileFormat']['value']
        except KeyError:
            raise ValueError(
                'Version migration error: Please open this job interactively and save it again before running it.'
            )

    @property
    def update_model_with_fmu_variables(self):
        return (
                self._only_run_fmu_variables_update
                or self.run_fmu_workflows
        ) and self.global_variables_file

    @property
    def simulate_fields(self):
        # The stored value has two values: True or False
        # If this is True and also in FMU mode to update GRF fields:
        #  It means that it should be checked whether a directory with name 0
        #  exist or not at the top level of the FMU directory structure
        #  (same level as the directory fmuconfig, ert and rms directories).
        #  If the directory with name 0 exists, it means that the fields should be simulated and exported to FMU
        #  since 0 is the iteration number in the Ensemble Smoother algorithm and corresponds to
        #  creating initial ensemble. If directory with name 1 or 2 or 3 ... exists instead of directory with name 0,
        #  it means that the iteration number is > 0 which means that the smoother algorithm has updated the GRF's
        #  In this case the GRF's should be imported into APS instead.
        # If this is False:
        #  It means that the fields should be simulated and exported regardless
        #  of whether the directory with name 0 exist or not at the top level of the FMU directory structure.

        if self.fmu_mode:
            # Check if simulate/export  or import
            if self._config['options']['importFields']['value']:
                # Automatic detect
                if is_initial_iteration(self.debug_level):
                    # Simulate and export
                    if self.debug_level >= Debug.ON:
                        print(
                            '- APS is running in FMU mode for AHM and automatic selected: '
                            'Simulate GRF files and export to FMU'
                        )
                    return True
                else:
                    # Import GRF from file when running in FMU workflow
                    if self.debug_level >= Debug.ON:
                        print(
                            '- APS is running in FMU mode for AHM and automatic selected: '
                            'Import updated GRF files from FMU'
                        )
                    return False
            else:
                if self.debug_level >= Debug.ON:
                    print('- APS is running in FMU mode for AHM and simulate GRF files and export to FMU')
                return True
        else:
            # Simulate and export since not in FMU mode to update GRF's
            return True

    @property
    def max_fmu_grid_depth(self):
        return self._config['fmu']['maxDepth']['value']

    @property
    def _max_allowed_fraction_of_values_outside_tolerance(self):
        return self._config['parameters']['maxAllowedFractionOfValuesOutsideTolerance']['selected']

    @property
    def _tolerance_of_probability_normalisation(self):
        try:
            return self._config['parameters']['toleranceOfProbabilityNormalisation']['selected']
        except KeyError:
            # Some, older jobs may not be updated, and this "config.parameters.toleranceOfProbabilityNormalisation"
            # does not exist.
            return ProbabilityTolerances.MAX_ALLOWED_DEVIATION_BEFORE_ERROR

    @property
    def _transformation_type_for_grf(self):
        try:
            return self._config['parameters']['transformType']['selected']
        except KeyError:
            # Some, older jobs may not be updated, and this "config.parameters.transformType"
            # does not exist.
            return TransformType.EMPIRIC

    @property
    def export_fmu_config_files(self):
        try:
            export_fmu = self._config['options']['exportFmuConfigFiles']['value']
            return export_fmu
        except KeyError:
            # Some, older jobs may not be updated, and this "config.options.exportFmuConfigFiles"
            # does not exist.
            return False

    @property
    def debug_level(self):
        return Debug(self._config['parameters']['debugLevel']['selected'])

    @property
    def _config_location(self):
        if self.run_fmu_workflows or self._only_run_fmu_variables_update:
            return get_ert_location() / '..' / '..' / 'fmuconfig' / 'output'
        return None

    @property
    def global_variables_file(self):
        config_location = self._config_location
        if config_location and config_location.exists() and config_location.is_dir():
            file_priority = [
                'global_variables.yml',
                'global_variables.yaml',
                'global_variables.ipl',
            ]
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
