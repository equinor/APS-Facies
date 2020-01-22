#!/bin/env python
# -*- coding: utf-8 -*-
from pathlib import Path

import numpy as np
from base64 import b64decode

from src.algorithms.APSGaussModel import (
    GaussianField,
    Variogram,
    Ranges,
    Angles,
    Trend,
    GaussianFieldSimulationSettings,
)
from src.algorithms.APSModel import APSModel
from src.algorithms.properties import CrossSection
from src.utils.constants.simple import (
    VariogramType,
    MinimumValues,
    MaximumValues,
    TrendType,
    Direction,
    OriginType,
    ProbabilityTolerances,
)
from src.utils.exceptions.xml import ApsXmlError
from src.utils.roxar.generalFunctionsUsingRoxAPI import get_project_dir
from src.utils.roxar.grid_model import (
    get_simulation_box_thickness,
    average_of_property_inside_zone_region,
    getDiscrete3DParameterValues,
    create_zone_parameter,
    GridSimBoxSize,
)
from src.utils.plotting import create_facies_map
from src.utils.truncation_rules import make_truncation_rule
from src.utils.xmlUtils import prettify


def empty_if_none(func):
    def wrapper(*args):
        # TODO: Generalize?
        if any([arg is None for arg in args]):
            return []
        else:
            return func(*args)
    return wrapper


def _option_mapping():
    return {
        'variogram': VariogramType,
        'origin': OriginType,
        'stacking_direction': Direction,
        'trend': TrendType,
    }


class RMSData:
    def __init__(self, roxar, project):
        self.roxar = roxar
        self.project = project

    def is_discrete(self, _property, can_be_empty=False):
        return self.is_property_type(_property, self.roxar.GridPropertyType.discrete, can_be_empty)

    def is_continuous(self, _property, can_be_empty=False):
        return self.is_property_type(_property, self.roxar.GridPropertyType.continuous, can_be_empty)

    def is_property_type(self, _property, type, can_be_empty=False):
        return (
            _property.type == type
            and (
                can_be_empty
                or not _property.is_empty(self.project.current_realisation)
            )
        )

    def get_project_name(self):
        return Path(self.project.filename).name

    def get_project_dir(self):
        return str(get_project_dir(self.project))

    def _get_project_location(self):
        return Path(self.project.filename).parent

    def get_fmu_parameter_list_dir(self):
        return str((self._get_project_location()).absolute())

    def get_current_workflow_name(self):
        return self.roxar.rms.get_running_workflow_name()

    def get_grid_models(self):
        return self.project.grid_models

    def get_grid_model(self, name):
        if not isinstance(name, str):
            raise ValueError('The name of a grid model must be a string')
        grid_models = self.get_grid_models()
        return grid_models[name]

    def get_grid(self, name, realization=None):
        if realization is None:
            realization = self.project.current_realisation
        return self.get_grid_model(name).get_grid(realization)

    def get_grid_model_names(self):
        grid_models = self.get_grid_models()
        models = []
        for grid_model in grid_models:
            name = grid_model.name
            models.append({'name': name, 'exists': self.grid_exists(name)})
        return models

    def get_realization_parameters(self, grid_model_name):
        return self._get_parameter_names(grid_model_name, self.is_discrete)

    def get_region_parameters(self, grid_model_name):
        return self._get_parameter_names(grid_model_name, self.is_region_parameter)

    def get_rms_trend_parameters(self, grid_model_name):
        return self._get_parameter_names(grid_model_name, self.is_trend_parameter)

    def get_probability_cube_parameters(self, grid_model_name):
        return self._get_parameter_names(grid_model_name, self.is_probability_cube)

    def get_simulation_box_size(self, grid_model_name, rough=False):
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

    def get_grid_size(self, grid_model_name):
        # TODO: Add option to get zone thickness
        grid = self.get_grid(grid_model_name)
        return grid.grid_indexer.dimensions

    def _get_parameter_names(self, grid_model_name, check):
        grid_model = self.get_grid_model(grid_model_name)
        return [parameter.name for parameter in grid_model.properties if check(parameter)]

    def get_zones(self, grid_model_name):
        grid = self.get_grid(grid_model_name)
        return [
            {
                'code': key + 1,
                'name': grid.zone_names[key]
            } for key in grid.simbox_indexer.zonation
        ]

    def get_regions(self, grid_model_name, zone_name, region_parameter):
        # TODO: Ensure that available regions depends on zone
        grid_model = self.get_grid_model(grid_model_name)
        regions = self.get_code_names(grid_model.properties[region_parameter])
        return regions

    def grid_exists(self, name):
        exists = True
        try:
            self.get_grid(name)
        except (KeyError, ValueError):
            exists = False
        return exists

    def is_region_parameter(self, param):
        # TODO: Implement properly
        return (
            self.is_discrete(param)
            and len(param.code_names) > 0
        )

    def is_trend_parameter(self, param):
        return self.is_continuous(param)

    def is_probability_cube(self, param):
        return (
            self.is_continuous(param)
        )

    def _get_blocked_well_set(self, grid_model_name):
        return self.get_grid_model(grid_model_name).blocked_wells_set

    def get_blocked_well_set_names(self, grid_model_name):
        return [blocked_well.name for blocked_well in self._get_blocked_well_set(grid_model_name)]

    def get_blocked_well(self, grid_model_name, blocked_well_name):
        block_wells = self._get_blocked_well_set(grid_model_name)
        return block_wells[blocked_well_name]

    def calculate_average_of_probability_cube(
            self, grid_model_name, probability_cube_parameters,
            zone_number,
            region_parameter=None, region_number=None
    ):

        # Get parameters from RMS
        realisation_number = self.project.current_realisation
        grid_model = self.project.grid_models[grid_model_name]
        # get zone_values and region_values
        zone_values = create_zone_parameter(grid_model, realization_number=realisation_number).get_values(realisation_number)
        if region_parameter:
            region_values, _ = getDiscrete3DParameterValues(grid_model, region_parameter, realisation_number)
        else:
            region_values = None

        averages = average_of_property_inside_zone_region(
            grid_model, probability_cube_parameters,
            zone_values, zone_number,
            region_values, region_number,
            realisation_number
        )
        # numpy float to regular float
        return {parameter: float(probability) for parameter, probability in averages.items()}

    @empty_if_none
    def get_blocked_well_logs(self, grid_model_name, blocked_well_name):
        blocked_wells = self.get_blocked_well(grid_model_name, blocked_well_name)
        return [property_log.name for property_log in blocked_wells.properties if self.is_discrete(property_log)]

    @empty_if_none
    def get_facies_table_from_blocked_well_log(self, grid_model_name, blocked_well_name, facies_log_name):
        """ Use Roxar API to get table of discrete codes and associated names for a discrete log"""

        # Get blocked wells
        grid_model = self.get_grid_model(grid_model_name)
        blocked_wells_set = grid_model.blocked_wells_set
        blocked_wells = blocked_wells_set[blocked_well_name]

        # Get facies property
        facies_property = blocked_wells.properties[facies_log_name]
        return self.get_code_names(facies_property)

    @staticmethod
    def save_model(path, content):
        return RMSData.save_file(path, content, prettify)

    @staticmethod
    def save_file(path, content, prettifier=None):
        if prettifier is None:
            prettifier = lambda _: _
        try:
            with open(Path(path), 'w') as f:
                f.write(prettifier(b64decode(content).decode()))
            return True
        except FileNotFoundError:
            return False

    @staticmethod
    def simulate_gaussian_field(field, grid_index_order='F'):
        simulation = RMSData._simulate_gaussian_field(field)
        data = simulation.field_as_matrix(grid_index_order)
        return data.tolist()

    @staticmethod
    def simulate_realization(fields, specification, grid_index_order='F'):
        simulations = [RMSData._simulate_gaussian_field(field) for field in fields]
        truncation_rule = make_truncation_rule(specification)
        facies, _ = create_facies_map(simulations, truncation_rule, use_code=True)

        data = np.reshape(facies, simulations[0].settings.dimensions, grid_index_order).transpose()
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
    def get_constant(_property, _type='min,max'):
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
    def get_options(_type):
        return [item.name for item in _option_mapping()[_type]]

    @staticmethod
    def get_code_names(_property):
        return [{'code': code, 'name': name} for code, name in _property.code_names.items()]

    @staticmethod
    def is_aps_model_valid(encoded_xml):
        valid = True
        error = ''
        try:
            APSModel.from_string(b64decode(encoded_xml).decode())
        except (ValueError, ApsXmlError) as e:
            valid = False
            error = str(e)
        except (Exception) as e:
            valid = False
            error = str(e)
        return {'valid': valid, 'error': error}

    @staticmethod
    def _simulate_gaussian_field(field):
        if 'field' in field:
            field = field['field']
        name, variogram, trend, settings = field['name'], field['variogram'], field['trend'], field['settings']

        if trend is None:
            trend = {}
        if settings is None:
            settings = GaussianFieldSimulationSettings(
                cross_section=CrossSection('IJ', 0.5),
                grid_azimuth=0,
                grid_size=(100, 100, 1),
                simulation_box_size=(100, 100, 1),
                seed=0,
            )
        else:
            settings = GaussianFieldSimulationSettings.from_dict(**settings)
        simulation = GaussianField(
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
        return simulation

    @staticmethod
    def open_wiki_help():
        import webbrowser
        webbrowser.open('https://wiki.equinor.com/wiki/index.php/Res:APS_Adaptive_Plurigaussian_Simulation')
