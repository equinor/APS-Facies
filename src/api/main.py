from pathlib import Path

from src.algorithms.APSModel import APSModel
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
from src.utils.constants.simple import Debug
from src.utils.fmu import get_grid, get_export_location, fmu_aware_model_file
from src.utils.io import create_temporary_model_file

import roxar.rms


class Config:
    def __init__(self, config):
        self._config = config

    def get_parameters(self, model_file):
        aps_model = APSModel(model_file)  # Represents the ORIGINAL APS model
        return {
            'roxar': roxar,
            'project': project,
            'model_file': model_file,
            'output_model_file': model_file,
            'global_variables': self.global_variables_file,
            'max_fmu_grid_depth': self.max_fmu_grid_depth,
            'layers_per_zone': self._get_layers_per_zone(aps_model),
            'fmu_mode': self.run_fmu_workflows,
            'fmu_simulation_grid_name': self.fmu_grid_name,
            'rms_grid_name': aps_model.grid_model_name,
            'aps_model': aps_model,
            'use_constant_probabilities': aps_model.use_constant_probability,
            'workflow_name': roxar.rms.get_running_workflow_name(),
            'seed_log_file': None,
            'write_rms_parameters_for_qc_purpose': self.write_rms_parameters_for_qc_purpose,
            'debug_level': self.debug_level,
            'max_allowed_fraction_of_values_outside_tolerance': self._max_allowed_fraction_of_values_outside_tolerance,
        }

    def _get_layers_per_zone(self, aps_model):
        if not self.run_fmu_workflows:
            return None

        grid = get_grid(project, aps_model)
        layers = []
        for zonation, *reverse in grid.grid_indexer.zonation.values():
            layers.append(zonation.stop - zonation.start)
        return layers

    @property
    def error_message(self):
        return self._config['errorMessage']

    @property
    def model(self):
        return self._config['model']

    @property
    def create_fmu_grid(self):
        return (
            self._config['fmu']['create']['value']
            and self.fmu_grid_name not in project.grid_models
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
    def global_variables_file(self):
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

    @property
    def write_rms_parameters_for_qc_purpose(self):
        return (
                not self.run_fmu_workflows
                or self.debug_level >= Debug.ON
        )


@loggable
def run(config):
    config = Config(config)
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
                        load_dir=get_export_location(project),
                        grid_name=kwargs['rms_grid_name'],
                        **kwargs
                    )
            else:
                run_import_fields(
                    grid_name=kwargs['rms_grid_name'],
                    **kwargs
                )

        run_truncation(**kwargs)
