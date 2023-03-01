import functools
from random import sample
from typing import Optional, List
from uuid import uuid4
from warnings import warn

from aps.utils.constants.simple import Debug, ExtrapolationMethod
from aps.utils.roxar._config_getters import get_debug_level


@functools.total_ordering
class _Version:
    __slots__ = 'major', 'minor', 'patch'

    def __init__(self, version: str):
        version = [int(part) for part in version.split('.')]

        self.patch = 0
        self.minor = 0
        self.major = 0

        if not 1 <= len(version) <= 3:
            raise ValueError(f'Not a valid semantic version ({version}). Should be major[.minor[.patch]]')

        if len(version) >= 3:
            self.patch = version[2]
        if len(version) >= 2:
            self.minor = version[1]
        self.major = version[0]

    def __str__(self):
        return f"{self.major}.{self.minor}.{self.patch}"

    def as_tuple(self):
        return self.major, self.minor, self.patch

    def __lt__(self, other):
        return self.as_tuple() < other.as_tuple()

    def __eq__(self, other):
        return self.as_tuple() == other.as_tuple()


class Migration:
    def __init__(self, rms_data: 'RMSData'):
        self.rms_data = rms_data

    def add_max_allowed_fraction_of_values_outside_tolerance(self, state: dict):
        constants = self.rms_data.get_constant('max_allowed_fraction_of_values_outside_tolerance', 'tolerance')
        state['parameters']['maxAllowedFractionOfValuesOutsideTolerance'] = {
            'selected': constants['tolerance']
        }
        return state

    def add_zone_thickness(self, state: dict):
        grid_model_id = state['gridModels']['current']
        if not grid_model_id:
            return state

        grid_model = state['gridModels']['available'][grid_model_id]
        thicknesses = {
            zone['code']: zone['thickness']
            for zone in
            self.rms_data.get_zones(grid_model['name'])
        }
        for zone in state['zones']['available'].values():
            zone['thickness'] = thicknesses[zone['code']]
        return state

    def add_number_of_zones_to_grid(self, state: dict):
        mapping = {
            grid_model['name']: grid_model['zones']
            for grid_model in self.rms_data.get_grid_models()
        }
        for grid_model in state['gridModels']['available'].values():
            grid_model['zones'] = mapping[grid_model['name']]
        return state

    @staticmethod
    def add_observable_facies(state):
        for facies in state['facies']['global']['available'].values():
            facies['observed'] = None

        for zone in state['zones']['available'].values():
            zone['touched'] = True
            for region in zone['regions'] or []:
                region['touched'] = True
        return state

    def add_has_dual_index_system(self, state: dict):
        mapping = {
            grid['name']: grid['hasDualIndexSystem']
            for grid in
            self.rms_data.get_grid_models()
        }
        for grid_model in state['gridModels']['available'].values():
            grid_model['hasDualIndexSystem'] = mapping[grid_model['name']]
        return state

    @staticmethod
    def ensure_numeric_codes(state: dict):
        def _ensure_numeric_codes(item: dict):
            code = item['code']
            if isinstance(code, str):
                try:
                    code = int(code)
                except Exception as e:
                    warn(f"The given code, {code} could not be parsed as an integer")
            item['code'] = code

        for facies in state['facies']['global']['available'].values():
            _ensure_numeric_codes(facies)
        for zone in state['zones']['available'].values():
            _ensure_numeric_codes(zone)
            if zone['regions']:
                for region in zone['regions'].values():
                    _ensure_numeric_codes(region)
        return state

    def add_tolerance_of_probability_normalisation(self, state: dict):
        constant = self.rms_data.get_constant('max_allowed_deviation_before_error', 'tolerance')
        state['parameters']['toleranceOfProbabilityNormalisation'] = {
            'selected': constant['tolerance']
        }
        return state

    @staticmethod
    def remove_path_parameter(state):
        del state['parameters']['path']
        return state

    @staticmethod
    def add_transform_type(state: dict):
        state['parameters']['transformType'] = {
            'selected': 0,
        }
        return state

    @staticmethod
    def add_export_fmu_config_file(state: dict):
        state['options']['exportFmuConfigFiles'] = {
            'value': False,
        }
        return state

    @staticmethod
    def add_use_only_residual_fields(state: dict):
        state['fmu']['onlyUpdateResidualFields'] = {
            'value': False,
        }
        return state


    @staticmethod
    def add_field_export_format(state: dict):
        state['fmu']['fieldFileFormat'] = {
            'value': 'grdecl',
        }
        return state

    @staticmethod
    def add_custom_trend_extrapolation_method(state: dict):
        state['fmu']['customTrendExtrapolationMethod'] = {
            'value': ExtrapolationMethod.EXTEND_LAYER_MEAN.value,
        }
        return state

    def add_trend_map(self, state: dict):
        trend_map_zones_dict = self.rms_data.get_rms_trend_map_zones()
        state['parameters']['rmsTrendMapZones'] = {'available': trend_map_zones_dict}
        for key in state['gaussianRandomFields']['available'] :
            state['gaussianRandomFields']['available'] [key]['trend']['trendMapName'] = None
            state['gaussianRandomFields']['available'] [key]['trend']['trendMapZone'] = None

        return state

    @staticmethod
    def add_use_customized_fmu_directory_structure(state: dict):
        state['fmu']['useNonStandardFmu'] = {
            'value':  False,
        }
        return state

    @staticmethod
    def add_check_export_ertbox_grid(state: dict):
        state['fmu']['exportErtBoxGrid'] = {
            'value':  True,
        }
        return state

    def attempt_upgrading_legacy_state(self, state: dict):
        return _attempt_upgrading_legacy_state(self, state)

    @staticmethod
    def add_possibly_missing_root_polygon_to_cubic_truncation_rules(state: dict):

        def new_root(id: Optional[str] = None, children: List[str] = None) -> dict:
            return {
                'id': id or str(uuid4()),
                'facies': None,
                'fraction': 1,
                'order': -1,
                'overlay': False,
                'parent': None,
                'children': children or [],
            }

        for truncation_rule in state['truncationRules']['available'].values():
            if truncation_rule['type'] == 'cubic':
                polygons = truncation_rule['polygons']
                if not polygons:
                    # All cubic truncation rules should have at least one polygon; its root
                    polygons.append(new_root())
                else:
                    polygon_lookup = {polygon['id']: polygon for polygon in polygons}
                    background_polygons = [polygon for polygon in polygons if not polygon['overlay']]
                    polygon = sample(background_polygons, 1)[0]

                    while polygon['parent'] is not None and polygon['parent'] in polygon_lookup:
                        polygon = polygon_lookup[polygon['parent']]
                    parent = polygon['parent']
                    if parent is not None:
                        # That is, there are references to a root that does not exist
                        # This was caused by a bug in the "simple" cubic truncation rule, where
                        # the root was not added
                        polygons.append(new_root(
                            id=parent,
                            children=[child['id'] for child in background_polygons if child['parent'] == parent],
                        ))
        return state

    @property
    def migrations(self):
        return [
            {
                'from': '0.0.0',
                'to': '1.0.0',
                'up': self.attempt_upgrading_legacy_state
            },
            {
                'from': '1.0.0',
                'to': '1.1.0',
                'up': self.add_max_allowed_fraction_of_values_outside_tolerance,
            },
            {
                'from': '1.1.0',
                'to': '1.2.0',
                'up': lambda state: self.add_number_of_zones_to_grid(self.add_zone_thickness(state)),
            },
            {
                'from': '1.2.0',
                'to': '1.3.0',
                'up': self.add_observable_facies,
            },
            {
                'from': '1.3.0',
                'to': '1.4.0',
                'up': self.add_has_dual_index_system,
            },
            {
                'from': '1.4.0',
                'to': '1.4.1',
                'up': self.ensure_numeric_codes,
            },
            {
                'from': '1.4.1',
                'to': '1.5.0',
                'up': self.add_tolerance_of_probability_normalisation,
            },
            {
                'from': '1.5.0',
                'to': '1.6.0',
                'up': self.remove_path_parameter,
            },
            {
                'from': '1.6.0',
                'to': '1.7.0',
                'up': self.add_field_export_format,
            },
            {
                'from': '1.7.0',
                'to': '1.8.0',
                'up': lambda state: self.add_transform_type(self.add_export_fmu_config_file(state)),
            },
            {
                'from': '1.8.0',
                'to': '1.8.1',
                'up': self.add_possibly_missing_root_polygon_to_cubic_truncation_rules,
            },
            {
                'from': '1.8.1',
                'to': '1.9.0',
                'up': self.add_custom_trend_extrapolation_method,
            },
            {
                'from': '1.9.0',
                'to': '1.10.0',
                'up': self.add_trend_map,
            },
            {
                'from': '1.10.0',
                'to': '1.11.0',
                'up': self.add_use_only_residual_fields,
            },
            {
                'from': '1.11.0',
                'to': '1.12.0',
                'up': self.add_use_customized_fmu_directory_structure,
            },
            {
                'from': '1.12.0',
                'to': '1.13.0',
                'up': self.add_check_export_ertbox_grid,
            },

        ]

    def get_migrations(self, from_version: str, to_version: Optional[str] = None):
        _migrations = [
            migration for migration in self.migrations
            if (
                    (
                            to_version is None
                            or _Version(to_version) > _Version(migration['from'])
                    )
                    and _Version(from_version) < _Version(migration['to'])
            )
        ]
        return _migrations

    def migrate(self, state: dict, from_version: Optional[str] = None, to_version: Optional[str] = None):
        errors = None

        if from_version is None:
            try:
                from_version = state['version']
            except KeyError:
                from_version = '0.0.0'

        migrations = self.get_migrations(from_version, to_version)

        if get_debug_level(state) >= Debug.VERBOSE:
            if len(migrations) == 0:
                print(f'-- State at latest version ({from_version}). No migration needed.')
            else:
                if to_version is None:
                    to_version = self.migrations[-1]['to']
                print(f"-- Migrating state from {from_version} to {to_version}")

        try:
            for migration in migrations:
                state = migration['up'](state)
                state['version'] = migration['to']
        except Exception as e:
            errors = e.__repr__()
            print(f"Error: ")
            warn(errors)
            raise KeyError(f"In migration:  {errors} ")
        return {
            'state': state,
            'errors': errors,
        }

    def can_migrate(self, from_version: str, to_version: str) -> bool:
        if not from_version:
            return False
        version = from_version
        for migration in self.migrations:
            if version == migration['from']:
                version = migration['to']
        return version == to_version


def _attempt_upgrading_legacy_state(self: Migration, state: dict):
    # Missing state version
    state['version'] = '0.0.0'

    if isinstance(state['gridModels']['available'], list):
        _migrate_list_of_grids_to_identified_grids(self, state)

    _ensure_state_has_key(state, 'debugLevel')

    _ensure_state_has_key(state, 'fmu')

    _ensure_has_available(state, 'gaussianRandomFields', 'fields')

    _ensure_has_available(state, 'truncationRules', 'rules')

    _ensure_state_has_key(state, 'panels')
    return state


def _ensure_state_has_key(state: dict, key: str):
    if key not in state:
        state[key] = {}


def _ensure_has_available(state: dict, item_key: str, old_available_key: str):
    if old_available_key in state[item_key]:
        state[item_key]['available'] = state[item_key][old_available_key]
        del state[item_key][old_available_key]


def _migrate_list_of_grids_to_identified_grids(self: Migration, state: dict):
    current = state['gridModels']['current']
    grid_models: List[dict] = self.rms_data.get_grid_models()
    for grid_model in grid_models:
        grid_model['id'] = str(uuid4())
        if current == grid_model['name']:
            current = grid_model['id']
    state['gridModels']['available'] = {
        grid_model['id']: grid_model for grid_model in grid_models
    }
    state['gridModels']['current'] = current
