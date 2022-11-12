#!/bin/env python
# -*- coding: utf-8 -*-
import json
from enum import Enum
from pathlib import Path
from typing import Callable, Dict, Type, Optional, List, Union
from warnings import warn

import numpy as np
from base64 import b64decode

from roxar import Project, GridPropertyType
from roxar.grids import (
    Grid3D,
    GridModel,
    Property,
    BlockedWells,
    BlockedWellsSet,
)
from aps.algorithms.APSGaussModel import (
    GaussianField,
    Variogram,
    Ranges,
    Angles,
    Trend,
    GaussianFieldSimulationSettings,
    GaussianFieldSimulation,
)
from aps.algorithms.APSModel import APSModel
from aps.algorithms.properties import CrossSection
from aps.rms_jobs.create_simulation_grid import create_ertbox_grid_model
from aps.utils.constants.simple import (
    VariogramType,
    MinimumValues,
    MaximumValues,
    TrendType,
    Direction,
    OriginType,
    ProbabilityTolerances,
    CrossSectionType,
    GridModelConstants,
)
from aps.utils.debug import parse_dot_master
from aps.utils.exceptions.xml import ApsXmlError
from aps.utils.numeric import flip_if_necessary
from aps.utils.roxar.generalFunctionsUsingRoxAPI import get_project_dir
from aps.utils.roxar.grid_model import (
    get_simulation_box_thickness,
    average_of_property_inside_zone_region,
    getDiscrete3DParameterValues,
    create_zone_parameter,
    GridSimBoxSize,
    get_zone_names,
)
from aps.utils.facies_map import create_facies_map
from aps.utils.roxar.migrations import Migration
from aps.utils.truncation_rules import make_truncation_rule
from aps.utils.types import (
    ProjectName, ProjectPath, FmuParameterListPath, WorkflowName, GridName, RegionParameter,
    TrendParameter, TrendMapName, TrendMapZone, ProbabilityCubeParameter, RealizationParameter,
    GridSize, ZoneNumber, SimulationBoxOrigin,
    RegionNumber, Average, XML, VariogramName, TrendName, DirectionName, OriginTypeName,
    GridModelName,
)
from aps.utils.xmlUtils import prettify
from aps.utils.constants.simple import Debug

def empty_if_none(func: Callable) -> Callable:
    def wrapper(*args, **kwargs):
        # TODO: Generalize?
        if any(arg is None for arg in args):
            return []
        else:
            return func(*args, **kwargs)

    return wrapper


def _option_mapping() -> Dict[str, Type[Enum]]:
    return {
        'variogram': VariogramType,
        'origin': OriginType,
        'stacking_direction': Direction,
        'trend': TrendType,
    }


class RMSData:
    """
    Purpose: Get RMS project data to be used in APS GUI using Roxar API.
    """
    def __init__(self, roxar, project: Project):
        self.roxar = roxar
        self.project = project

    def is_discrete(self, _property: Property, can_be_empty: bool = False) -> bool:
        return self.is_property_type(_property, self.roxar.GridPropertyType.discrete, can_be_empty)

    def is_continuous(self, _property: Property, can_be_empty: bool = False) -> bool:
        return self.is_property_type(_property, self.roxar.GridPropertyType.continuous, can_be_empty)

    def is_property_type(
            self,
            _property: Property,
            type: GridPropertyType,
            can_be_empty: bool = False,
    ) -> bool:
        return (
                _property.type == type
                and (
                        can_be_empty
                        or not _property.is_empty(self.project.current_realisation)
                )
        )

    def get_project_name(self) -> ProjectName:
        return Path(self.project.filename).name

    def get_project_dir(self) -> ProjectPath:
        return str(get_project_dir(self.project))

    def _get_project_location(self) -> Path:
        return Path(self.project.filename).parent

    def get_fmu_parameter_list_dir(self) -> FmuParameterListPath:
        default_location = self._get_project_location() / '..' / '..' / 'fmuconfig' / 'output'
        return str(default_location.absolute())

    def get_current_workflow_name(self) -> WorkflowName:
        return self.roxar.rms.get_running_workflow_name()

    def get_grid_model(self, name: str) -> GridModel:
        if not isinstance(name, str):
            raise ValueError('The name of a grid model must be a string')
        grid_models = self.project.grid_models
        return grid_models[name]

    def get_grid(self, name: GridName, realization: Optional[int] = None) -> Grid3D:
        if realization is None:
            realization = self.project.current_realisation
        return self.get_grid_model(name).get_grid(realization)

    def get_grid_models(self) -> List[dict]:
        grid_models = self.project.grid_models
        models = []
        for grid_model in grid_models:
            name = grid_model.name
            grid = grid_model.get_grid(realisation=self.project.current_realisation)
            exists = self.grid_exists(name)
            zone_names = []
            if exists:
                zone_names = get_zone_names(grid_model)
            models.append({
                'name': name,
                'exists': exists,
                'zones': len(zone_names) if exists else 0,
                'hasDualIndexSystem': grid.has_dual_index_system if exists else False,
            })
        return models

    def get_realization_parameters(self, grid_model_name: GridName) -> List[RealizationParameter]:
        return self._get_parameter_names(grid_model_name, self.is_discrete)

    def get_region_parameters(self, grid_model_name: GridName) -> List[RegionParameter]:
        return self._get_parameter_names(grid_model_name, self.is_region_parameter)

    def get_rms_trend_parameters(self, grid_model_name: GridName) -> List[TrendParameter]:
        return self._get_parameter_names(grid_model_name, self.is_trend_parameter)

    def get_rms_trend_map_zones(self) -> Dict[str, List[str]]:
        rms_surface_representations = self.project.zones.representations
        representation_names = [item.name for item in rms_surface_representations]
        zone_names = self.project.zones.keys()
        # Find the surface types (representations) that have values and are not empty
        # for each zone in the zone container in RMS
        zones = {}
        for zone_name in zone_names:
            representations = []
            for rep_name in representation_names:
                try:
                    surface = self.project.zones[zone_name][rep_name]
                except KeyError:
                    surface = None

                if surface and not surface.is_empty():
                    representations.append(rep_name)

            zones[zone_name] = representations
        return zones

    def get_probability_cube_parameters(self, grid_model_name: GridName) -> List[ProbabilityCubeParameter]:
        return self._get_parameter_names(grid_model_name, self.is_probability_cube)

    def get_simulation_box_size(self, grid_model_name: GridName, rough: bool = False) -> dict:
        grid = self.get_grid(grid_model_name)
        sim_box_attributes = GridSimBoxSize(grid)
        kwargs = {}
        if rough:
            kwargs['max_number_of_selected_cells'] = 10

        sim_box_z_length = get_simulation_box_thickness(grid, **kwargs)
        return {
            'size': {
                'x': sim_box_attributes.x_length,
                'y': sim_box_attributes.y_length,
                'z': sim_box_z_length,
            },
            'rotation': sim_box_attributes.azimuth_angle,
            'origin': {
                'x': sim_box_attributes.x0,
                'y': sim_box_attributes.y0,
            },
        }

    def get_grid_size(self, grid_model_name: GridName) -> GridSize:
        # TODO: Add option to get zone thickness
        grid = self.get_grid(grid_model_name)
        try:
            return grid.grid_indexer.dimensions
        except RuntimeError:
            # RMS 12 compatibility
            return 0, 0, 0

    def _get_parameter_names(self, grid_model_name: GridName, check: Callable) -> List[str]:
        grid_model = self.get_grid_model(grid_model_name)
        return [parameter.name for parameter in grid_model.properties if check(parameter)]

    def get_zones(self, grid_model_name: GridName) -> List[dict]:
        grid = self.get_grid(grid_model_name)
        grid_model = self.get_grid_model(grid_model_name)
        zone_names = get_zone_names(grid_model)
        if len(zone_names) == 0:
            name = GridModelConstants.ZONE_NAME
            warn(f"No zone parameter with name '{name}' found. Create zone parameter from grid.")
            create_zone_parameter(grid_model)
            zone_names = get_zone_names(grid_model)
        zones = []
        for key, zonations in grid.simbox_indexer.zonation.items():
            zonation, *_reverse = zonations
            zones.append({
                'code': key + 1,
                'name': zone_names[key],
                'thickness': zonation.stop - zonation.start,
            })
        return zones

    def get_regions(
            self,
            grid_model_name: GridName,
            zone_name: str,
            region_parameter: RegionParameter,
    ) -> List[dict]:
        # TODO: Ensure that available regions depends on zone
        grid_model = self.get_grid_model(grid_model_name)
        return self.get_code_names(grid_model.properties[region_parameter])

    def grid_exists(self, name: GridName) -> bool:
        try:
            grid = self.get_grid(name)

            try:
                # That is, the grid exists, but is empty
                grid.zone_names
            except RuntimeError:
                return False

        except (KeyError, ValueError):
            return False
        return True

    def is_region_parameter(self, param: Property) -> bool:
        # TODO: Implement properly
        return (
                self.is_discrete(param)
                and len(param.code_names) > 0
        )

    def is_trend_parameter(self, param: Property) -> bool:
        return self.is_continuous(param)

    def is_probability_cube(self, param: Property) -> bool:
        return (
            self.is_continuous(param)
        )

    def _get_blocked_well_set(self, grid_model_name: GridName) -> BlockedWellsSet:
        return self.get_grid_model(grid_model_name).blocked_wells_set

    def get_blocked_well_set_names(self, grid_model_name: GridName) -> List[str]:
        return [blocked_well.name for blocked_well in self._get_blocked_well_set(grid_model_name)]

    def get_blocked_well(self, grid_model_name: GridName, blocked_well_name: str) -> BlockedWells:
        block_wells = self._get_blocked_well_set(grid_model_name)
        return block_wells[blocked_well_name]

    def calculate_average_of_probability_cube(
            self,
            grid_model_name: GridName,
            probability_cube_parameters: List[ProbabilityCubeParameter],
            zone_number: ZoneNumber,
            region_parameter: Optional[RegionParameter] = None,
            region_number: Optional[RegionNumber] = None,
            debug_level=Debug.VERBOSE,
    ) -> Dict[ProbabilityCubeParameter, Average]:
        # Ensure not duplicated parameter names for probability cubes
        param_names = list(set(probability_cube_parameters))
        param_names.sort()

        # Get parameters from RMS
        realisation_number = self.project.current_realisation
        grid_model = self.project.grid_models[grid_model_name]
        # get zone_values and region_values
        zone_values = create_zone_parameter(grid_model, realization_number=realisation_number).get_values(
            realisation_number)
        if region_parameter:
            region_values, _ = getDiscrete3DParameterValues(grid_model, region_parameter, realisation_number)
        else:
            region_values = None

        averages = average_of_property_inside_zone_region(
            grid_model, param_names,
            zone_values, zone_number,
            region_values, region_number,
            realisation_number
        )
        if debug_level >= Debug.VERBOSE:
            if region_values is not None:
                text = f"zone number: {zone_number}  region number:  {region_number} "
            else:
                text = f"zone: {zone_number}"
            print(f"-- Calculate average of probability cubes for {text}")
            for name,prob in averages.items():
                print(f" {name}  Average prob: {prob}")

        # numpy float to regular float
        return {parameter: float(probability) for parameter, probability in averages.items()}

    def create_ertbox_grid(self,
        geo_grid_model_name: GridName,
        ertbox_grid_model_name: GridName,
        nLayers: int,
        debug_level: Debug = Debug.OFF) -> None:
        create_ertbox_grid_model(self.project,
            geo_grid_model_name, ertbox_grid_model_name,
            nLayers, debug_level=debug_level)

    @empty_if_none
    def get_blocked_well_logs(self, grid_model_name: GridName, blocked_well_name: str) -> List[str]:
        blocked_wells = self.get_blocked_well(grid_model_name, blocked_well_name)
        return [property_log.name for property_log in blocked_wells.properties if self.is_discrete(property_log)]

    @empty_if_none
    def get_facies_table_from_blocked_well_log(
            self,
            grid_model_name: GridModelName,
            blocked_well_name: str,
            facies_log_name: str,
            region_parameter_name: str,
    ) -> List[Dict[str, int]]:
        """ Use Roxar API to get table of discrete codes and associated names for a discrete log"""

        # Get blocked wells
        grid_model = self.get_grid_model(grid_model_name)
        blocked_wells_set = grid_model.blocked_wells_set
        blocked_wells = blocked_wells_set[blocked_well_name]

        # Get facies property
        facies_property = blocked_wells.properties[facies_log_name]

        # Determine which facies appear in which zone, if any
        observed_facies = facies_property.get_values(self.project.current_realisation)
        observed_indices = blocked_wells.get_cell_numbers(self.project.current_realisation)

        # Get zone parameter. If non-existing create it.
        # If existing but empty, fill it with values
        zone_param = create_zone_parameter(grid_model,
            realization_number=self.project.current_realisation)
        zone_values = zone_param.get_values(self.project.current_realisation)

        regions = np.zeros(zone_values.shape, zone_values.dtype)
        if region_parameter_name != '__REGIONS_NOT_IN_USE__':  # Hack to avoid incompatibility with decorator
            regions = grid_model.properties[region_parameter_name].get_values(self.project.current_realisation)

        def find_defined(property, facies_code):
            return [int(_code) for _code in set(property[observed_indices[observed_facies == facies_code]])]

        facies = []
        for code, name in facies_property.code_names.items():
            where = {
                'zones': find_defined(zone_values, code),
                'regions': find_defined(regions, code),
            }
            facies.append({
                'code': code,
                'name': name,
                'observed': where,
            })
        return facies

    def load_dot_master(self) -> dict:
        try:
            project_root = Path(__file__).parent.parent.parent.parent
            with open(project_root / 'local.settings.json', encoding="utf-8") as f:
                debug_settings = json.load(f)
                filename = self.project.filename
                if filename.startswith('/'):
                    filename = filename[1:]
                project_location = Path(debug_settings['projectRootLocation']) / filename
        except Exception:
            project_location = Path(self.project.filename)
        return parse_dot_master(project_location / 'pythoncomp/apsgui/.master')

    def migrate_state(self, state: str, from_version: str, to_version: str):
        migration = Migration(self)
        return migration.migrate(_decode_state(state), from_version, to_version)

    def can_migrate_state(self, from_version: str, to_version: str) -> bool:
        migration = Migration(self)
        return migration.can_migrate(from_version, to_version)

    @staticmethod
    def run_aps_workflow(state: str) -> None:
        from aps.api.main import run

        run(_decode_state(state))

    @staticmethod
    def save_model(path: str, content: XML) -> bool:
        return RMSData.save_file(path, content, prettify)

    @staticmethod
    def save_file(
            path: str,
            content: XML,
            prettifier: Optional[Callable[[str], str]] = None,
    ) -> bool:
        if prettifier is None:
            prettifier = lambda _: _
        try:
            with open(Path(path), 'w') as f:
                f.write(prettifier(_decode(content)))
            return True
        except FileNotFoundError:
            return False

    @staticmethod
    def dump_aps_model(
            encoded_xml: str,
            model_path: str,
            fmu_configuration_path: Optional[str] = None,
            prop_dist_path: Optional[str] = None,
    ) -> bool:
        try:
            model = decode_model(encoded_xml)
        except Exception as e:
            return False
        model.dump(
            name=model_path,
            attributes_file_name=fmu_configuration_path,
            probability_distribution_file_name=prop_dist_path,
        )
        return True

    @staticmethod
    def has_fmu_updatable_values(encoded_xml):
        try:
            model = decode_model(encoded_xml)
        except Exception as e:
            return False
        return model.has_fmu_updatable_values

    @staticmethod
    def simulate_gaussian_field(field, grid_index_order: str = 'F'):
        simulation = RMSData._simulate_gaussian_field(field)
        data = simulation.field_as_matrix(grid_index_order)
        return data.tolist()

    @staticmethod
    def simulate_realization(fields, specification, grid_index_order='F') -> dict:
        simulations = [RMSData._simulate_gaussian_field(field) for field in fields]
        truncation_rule = make_truncation_rule(specification)
        facies, _ = create_facies_map(simulations, truncation_rule, use_code=True)

        data = np.reshape(facies, simulations[0].settings.dimensions, grid_index_order).transpose()
        data = flip_if_necessary(data, simulations[0].cross_section)
        return {
            'faciesMap': data.tolist(),
            'fields': [
                {
                    'name': simulation.name,
                    'data': simulation.field_as_matrix(grid_index_order).tolist(),
                } for simulation in simulations
            ]
        }

    @staticmethod
    def get_truncation_map_polygons(specification):
        truncation_rule = make_truncation_rule(specification)

        # Calculate polygons for truncation map for current facies probability
        # as specified when calling setTruncRule(faciesProb)
        facies_polygons = truncation_rule.truncMapPolygons()
        if isinstance(facies_polygons, np.ndarray):
            facies_polygons = facies_polygons.tolist()
        facies_index_per_polygon = truncation_rule.faciesIndxPerPolygon()
        # NOTE: Names has the correct order (relative to facies_index_per_polygon)
        names = truncation_rule.getFaciesInTruncRule()

        return [
            {
                'name': names[facies_index_per_polygon[i]],
                'polygon': facies_polygons[i]
            } for i in range(len(facies_polygons))
        ]

    @staticmethod
    def get_constant(_property: str, _type: str = 'min,max') -> Dict[str, float]:
        res = {
            'min': None,
            'max': None,
            'tolerance': None,
        }
        for item in _type.lower().split(','):
            if item in ['min', 'minimum']:
                res['min'] = MinimumValues[_property]
            elif item in ['max', 'maximum']:
                res['max'] = MaximumValues[_property]
            elif item in ['tolerance']:
                res['tolerance'] = ProbabilityTolerances[_property]
            else:
                raise ValueError('The property type \'{}\' is not known'.format(item))
        return res

    @staticmethod
    def get_options(_type: str) -> Union[
        List[VariogramName],
        List[TrendName],
        List[DirectionName],
        List[OriginTypeName]
    ]:
        return [item.name for item in _option_mapping()[_type]]

    @staticmethod
    def get_code_names(_property: Property) -> List[dict]:
        return [{'code': code, 'name': name} for code, name in _property.code_names.items()]

    @staticmethod
    def is_aps_model_valid(encoded_xml: str) -> Dict[str, Union[bool, str]]:
        valid = True
        error = ''
        try:
            decode_model(encoded_xml)
        except (ValueError, ApsXmlError) as e:
            valid = False
            error = str(e)
        except Exception as e:
            valid = False
            error = str(e)
        return {'valid': valid, 'error': error}

    @staticmethod
    def _simulate_gaussian_field(field: dict) -> GaussianFieldSimulation:
        if 'field' in field:
            field = field['field']
        name, variogram, trend, settings = field['name'], field['variogram'], field['trend'], field['settings']

        if trend is None:
            trend = {}
        if settings is None:
            settings = GaussianFieldSimulationSettings(
                cross_section=CrossSection(CrossSectionType.IJ, 0.5),
                grid_azimuth=0,
                grid_size=(100, 100, 1),
                simulation_box_size=(100, 100, 1),
                simulation_box_origin=(0, 0, 0),
                seed=0,
            )
        else:
            settings = GaussianFieldSimulationSettings.from_dict(**settings)
        return GaussianField(
            name=name,
            variogram=Variogram(
                name=name,
                type=variogram['type'],
                ranges=Ranges(
                    **variogram['range']
                ),
                angles=Angles(
                    **variogram['angle']
                ),
                power=variogram['power'],
            ),
            trend=Trend.from_dict(name, **trend),
            settings=settings,
        ).simulate()

    @staticmethod
    def open_wiki_help() -> None:
        import webbrowser
        webbrowser.open('https://wiki.equinor.com/wiki/index.php/Res:APS_Adaptive_Plurigaussian_Simulation')

    @staticmethod
    def exists(path: str, has_parent: bool = False) -> bool:
        if not path:
            return False
        path = _decode(path)
        if has_parent:
            return Path(path).parent.exists()
        return Path(path).exists()

    @staticmethod
    def load_file(path: str) -> Optional[str]:
        try:
            with open(path, 'r') as f:
                content = f.read()
            return content
        except FileNotFoundError:
            return None


def _decode(base64_encoded: str) -> str:
    return b64decode(base64_encoded).decode()


def _decode_state(encoded: str) -> dict:
    return json.loads(_decode(encoded))


def decode_model(encoded_xml: str) -> APSModel:
    return APSModel.from_string(_decode(encoded_xml))
