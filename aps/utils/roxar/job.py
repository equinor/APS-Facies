import json
import sys
from pathlib import Path
from base64 import b64decode
from functools import wraps
from warnings import warn

from typing import Dict

from aps.algorithms.APSModel import APSModel
from aps.utils.constants.simple import Debug, ProbabilityTolerances, TransformType, ExtrapolationMethod
from aps.utils.decorators import cached
from aps.utils.fmu import get_export_location, is_initial_iteration
from aps.utils.roxar._config_getters import get_debug_level
from aps.utils.roxar.migrations import Migration
from aps.utils.roxar.rms_project_data import RMSData
from aps.utils.aps_config import APSConfig
from aps.utils.roxar.progress_bar import APSProgressBar
from aps.utils.check_rms_interactive_or_batch import check_rms_execution_mode

def excepthook(type, value, traceback):
    print(f"ERROR:")
    print(f"Type:  {type.__name__}")
    print(f"{value}")

class JobConfig:
    def __init__(self, roxar, project, config: Dict):
        self.roxar = roxar
        self.project = project
        migrated = self._migrate_state(config)
        if migrated['errors']:
            warn(f"There was a problem migrating the state; {migrated['errors']}")
        self._config = migrated['state']

        # Traceback is on per default
        sys.excepthook = sys.__excepthook__
        if self.debug_level <= Debug.VERBOSE:
            # Traceback is turned off when low log output
            sys.excepthook = excepthook

        # Ensure that existing config file is read
        if self._only_run_fmu_variables_update or self.run_fmu_workflows:
            APSConfig.init(
                self.project,
                use_available_config_file=self.use_customized_fmu_config,
                must_read_existing_config_file=True,
            )
        else:
            APSConfig.init(self.project)

    def initialize_progress_bar(self, aps_model: APSModel):
        estimated_number_of_steps = aps_model.estimate_progress_steps()
        APSProgressBar.initialize_progress_bar(number_of_steps=estimated_number_of_steps)

    def get_parameters(self, model_file):
        # Represents the ORIGINAL APS model
        aps_model = APSModel(model_file, debug_level=self.debug_level)

        # Check that zone parameter exists and if not, then create it
        aps_model.check_or_create_zone_parameter(self.project, debug_level=self.debug_level)

        # Keep only models for (zone,region) pairs with active cells
        aps_model.check_active_cells(self.project, debug_level=self.debug_level)

        # Update simbox thickness to match current grid model and also write back the updated model
        # since both model file and APSModel object is used later and must be consistent.
        self.check_and_update_simbox_thickness(model_file, aps_model)

        # Initialize progress bar
        self.initialize_progress_bar(aps_model)

        return {
            'roxar': self.roxar,
            'project': self.project,
            'model_file': model_file,
            'output_model_file': model_file,
            'global_variables': self.global_variables_file,
            'max_fmu_grid_layers': self.max_fmu_grid_layers,
            'fmu_mode': self.run_fmu_workflows,
            'fmu_mode_only_param': self._only_run_fmu_variables_update,
            'fmu_simulate_fields': self.simulate_fields,
            'fmu_simulation_grid_name': self.fmu_grid_name,
            'export_ertbox_grid': self.export_ertbox_grid,
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
            'extrapolation_method': self.rms_param_trend_extrapolation_method,
            'fmu_use_residual_fields': self.fmu_use_residual_fields
        }

    @property
    @cached
    def error_message(self):
        export_error = self._config['errorMessage']
        if export_error:
            return export_error

        aps_model = APSModel.from_string(self.model, check_with_grid_model=True, project=self.project)
        if self.run_fmu_workflows:
            for zone_model in aps_model.zone_models:
                if not zone_model.grid_layout:
                    return (
                           f'The zone with code {zone_model.zone_number} does not have any conformity specified. '
                           f'This is required, when running in ERT / AHM.'
                    )
        # Check if APS model is consistent with grid model and has only zones defined in grid model
        ok, err_msg = self.check_zones(aps_model)
        if not ok:
            return err_msg

        return None

    @property
    @cached
    def model(self):
        return b64decode(self._config['model']).decode('UTF-8')

    @property
    def create_fmu_grid(self):
        # Create grid if in fmu ahm mode and grid does not exist or is specified to be created in GUI
        return self.run_fmu_workflows and (self._config['fmu']['create']['value'] or (self.fmu_grid_name not in self.project.grid_models))

    @property
    def export_ertbox_grid(self):
        rms_mode_is_batch = check_rms_execution_mode(self.debug_level)
        return self._config['fmu']['exportErtBoxGrid']['value'] and not rms_mode_is_batch

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
        return self._config['fmu']['fieldFileFormat']['value']

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
        #  It means that it should be checked if the ERT iteration is 0 or not.
        #  If no folder with iteration exists, the default is to return True which means to simulate and export GRF files.
        #  If folder with name 0 exist, also in this case return True.
        #  If there exist a folder with name equal to an integer > 0, the return is False 
        #  since in this case ERT iteration is > 0 and APS must use the updated GRF coming from ERT.
        #  In this case the GRF's should be imported into APS instead.
        # If this is False:
        #  It means that the fields should be simulated and exported regardless
        #  of whether there exist any directory with positive integer number as name or not at
        #  the top level of the FMU directory structure.

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
                        if self.fmu_use_residual_fields:
                            print(
                                '- APS will only exchange the GRF residuals with ERT for GRF with trend'
                            )

                    return True
                else:
                    # Import GRF from file when running in FMU workflow
                    if self.debug_level >= Debug.ON:
                        print(
                            '- APS is running in FMU mode for AHM and automatic selected: '
                            'Import updated GRF files from FMU'
                        )
                        if self.fmu_use_residual_fields:
                            print(
                                '- APS will only exchange the GRF residuals with ERT for GRF with trend'
                            )
                    return False
            else:
                if self.debug_level >= Debug.ON:
                    print('- APS is running in FMU mode for AHM and simulate GRF files and export to FMU')
                    if self.fmu_use_residual_fields:
                        print(
                            '- APS will only exchange the GRF residuals with ERT for GRF with trend'
                        )

                return True
        else:
            # Simulate and export since not in FMU mode to update GRF's
            return True

    @property
    def max_fmu_grid_layers(self):
        return self._config['fmu']['maxDepth']['value']

    @property
    def use_customized_fmu_config(self):
        try:
            use_non_standard_fmu = self._config['fmu']['useNonStandardFmu']['value']
            return use_non_standard_fmu
        except KeyError:
            # Some, older jobs may not be updated, and this "config.fmu.useNonStandardFmu"
            # does not exist.
            return False

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
        if check_rms_execution_mode(self.debug_level):
            # RMS run in batch model. Don't write the files
            return False
        try:
            if self.fmu_mode or self._only_run_fmu_variables_update:
                return self._config['options']['exportFmuConfigFiles']['value']
            else:
                return False
        except KeyError:
            # Some, older jobs may not be updated, and this "config.options.exportFmuConfigFiles"
            # does not exist.
            return False

    @property
    def fmu_use_residual_fields(self):
        try:
            use_residual = self._config['fmu']['onlyUpdateResidualFields']['value']
            return use_residual
        except KeyError:
            # Some, older jobs may not be updated,
            # and this "config.fmu.onlyUpdateResidualFields" does not exist.
            return False

    @property
    def debug_level(self):
        return get_debug_level(self._config)

    @property
    def global_variables_file(self):
        file_path = Path(APSConfig.global_variables_file())
        if file_path.exists():
            return str(file_path.absolute())
        return None

    @property
    def write_rms_parameters_for_qc_purpose(self):
        return self.debug_level >= Debug.VERY_VERBOSE

    @property
    def rms_param_trend_extrapolation_method(self): 
        return ExtrapolationMethod(self._config['fmu']['customTrendExtrapolationMethod']['value'])


    def to_json(self):
        return json.dumps(self._config)

    def _migrate_state(self, state: dict) -> dict:
        migration = Migration(RMSData(self.roxar, self.project))
        return migration.migrate(state)

    def check_zones(self, aps_model: APSModel):
        if aps_model.zones_removed:
            current_job_name = self.roxar.rms.get_running_job_name()
            print(f"Consistency error: Grid model has changed since the APS job {current_job_name} was created.")
            print( "  Fix the problem using the following help script: APS_remap_zone_models.")
            print( "  This script will take as input a YAML file specifying:")
            print( "        1. The old APS model (exported to model file)")
            print( "        2. Table of old zones and of new zones and a table defining the correspondence between them.")
            print( "        3. The output will be a new APS model file having new zones and corresponding settings for the new zones.")
            print( "  See the APS documentation of the help scripts on Equinor Wiki.")
            print( "  The current job will be stopped since additional information is needed to remap the zone models from the old to the new grid model.")
            if current_job_name is not None:
                err_message = f"Current grid model: {aps_model.grid_model_name}  has less number of zones than specified in the APS job: {current_job_name}. "
            else:
                err_message = f"Current grid model has less number of zones than specified in the APS job."

            if self.run_fmu_workflows:
                self._config['fmu']['create']['value'] = True
                if aps_model.fmu_ertbox_name in self.project.grid_models:
                    fmu_ertbox_grid_model = self.project.grid_models[aps_model.fmu_ertbox_name]
                    print(f"Warning: Will delete ERTBOX grid model: {aps_model.fmu_ertbox_name}. Must be created again.")
                    del fmu_ertbox_grid_model

            return False, err_message
        return True, None

    def check_and_update_simbox_thickness(self, model_file: str, aps_model: APSModel):
        aps_model.check_and_update_simbox_thickness(self.project, debug_level=self.debug_level)
        aps_model.write_model(model_file)


def classify_job_configuration(roxar, project):
    def decorator(func):
        @wraps(func)
        def wrapper(config: dict):
            config = JobConfig(roxar, project, config)
            func(config)
        return wrapper
    return decorator
