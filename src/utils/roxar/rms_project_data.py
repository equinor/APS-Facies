#!/bin/env python
# -*- coding: utf-8 -*-
from src.algorithms.APSGaussModel import (
    GaussianField, Variogram, Ranges, Angles, Trend, GaussianFieldSimulationSettings,
)
from src.algorithms.properties import CrossSection
from src.utils.constants.simple import VariogramType, MinimumValues, MaximumValues, TrendType, Direction, OriginType

from src.algorithms.APSModel import APSModel

from base64 import b64decode

from src.utils.exceptions.xml import ApsXmlError
from src.utils.roxar.grid_model import calcStatisticsFor3DParameter


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

    def is_discrete(self, _property):
        return _property.type == self.roxar.GridPropertyType.discrete

    def is_continuous(self, _property):
        return _property.type == self.roxar.GridPropertyType.continuous

    def get_grid_models(self):
        return self.project.grid_models

    def get_grid_model(self, name):
        grid_models = self.get_grid_models()
        return grid_models[name]

    def get_grid_model_names(self):
        return [grid_model.name for grid_model in self.get_grid_models()]

    def get_zone_parameters(self, grid_model_name):
        return self._get_parameter_names(grid_model_name, self.is_zone_parameter)

    def get_region_parameters(self, grid_model_name):
        return self._get_parameter_names(grid_model_name, self.is_region_parameter)

    def get_rms_trend_parameters(self, grid_model_name):
        return self._get_parameter_names(grid_model_name, self.is_trend_parameter)

    def get_probability_cube_parameters(self, grid_model_name):
        return self._get_parameter_names(grid_model_name, self.is_probability_cube)

    def _get_parameter_names(self, grid_model_name, check):
        grid_model = self.get_grid_model(grid_model_name)
        return [parameter.name for parameter in grid_model.properties if check(parameter)]

    def get_zones(self, grid_model_name, zone_parameter):
        grid_model = self.get_grid_model(grid_model_name)
        zones = self.get_code_names(grid_model.properties[zone_parameter])
        return zones

    def get_regions(self, grid_model_name, zone_name, region_parameter):
        # TODO: Ensure that available regions depends on zone
        grid_model = self.get_grid_model(grid_model_name)
        regions = self.get_code_names(grid_model.properties[region_parameter])
        return regions

    def is_zone_parameter(self, param):
        return (
                self.is_discrete(param)
                and set(param.code_names.values()) <= set([zone.name for zone in self.project.zones])
                and len(param.code_names) > 0
        )

    def is_region_parameter(self, param):
        # TODO: Implement properly
        return (
            self.is_discrete(param)
            and any([name != '' for name in param.code_names.values()])
            and len(param.code_names) > 0
        )

    def is_trend_parameter(self, param):
        return self.is_continuous(param)

    def is_probability_cube(self, param):
        return (
            self.is_continuous(param)
            and param.name.lower().startswith('prob')
        )

    def _get_blocked_well_set(self, grid_model_name):
        return self.get_grid_model(grid_model_name).blocked_wells_set

    def get_blocked_well_set_names(self, grid_model_name):
        return [blocked_well.name for blocked_well in self._get_blocked_well_set(grid_model_name)]

    def get_blocked_well(self, grid_model_name, blocked_well_name):
        block_wells = self._get_blocked_well_set(grid_model_name)
        return block_wells[blocked_well_name]

    def calculate_average_of_probability_cube(self, grid_model_name, probability_cube_parameters, zones=None):
        if zones is None:
            zones = []
        averages = {}
        for probability_cube in probability_cube_parameters:
            _, _, average = calcStatisticsFor3DParameter(
                grid_model=self.project.grid_models[grid_model_name],
                parameter_name=probability_cube,
                zone_number_list=zones
            )
            averages[probability_cube] = float(average)
        return averages

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
    def simulate_gaussian_field(name, variogram, trend, settings=None):
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
        grid_index_order = 'C'
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
        data = simulation.field_as_matrix(grid_index_order)
        return data.tolist()

    @staticmethod
    def get_constant(_property, _type='min,max'):
        res = {}
        for item in _type.lower().split(','):
            if item in ['min', 'minimum']:
                res['min'] = MinimumValues[_property]
            elif item in ['max', 'maximum']:
                res['max'] = MaximumValues[_property]
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
            APSModel.from_string(b64decode(encoded_xml))
        except (ValueError, ApsXmlError) as e:
            valid = False
            error = str(e)
        except (Exception) as e:
            valid = False
            error = str(e)
        return {'valid': valid, 'error': error}


def list_all_wells(project):
    """ Make a list of all well names in project """
    well_names = []
    for w in project.wells:
        well_names.append(w.name)
        print(w.name)


def list_all_wellbores(project):
    """ For each well list all wellbores"""
    well_names = []
    well_bore_names = []
    i = 0
    for well in project.wells:
        well_names.append(well.name)
        well_bore_names.append([])
        print(well.name)

        for wb in well.all_wellbores:
            well_bore_names[i].append(wb.name)
            print('   ' + wb.name)
        i = i + 1


def list_all_trajectories(project):
    """ For each well and each wellbore list all trajectories"""
    well_names = []
    well_bore_names = []
    well_trajectory_names = []
    i = 0
    for well in project.wells:
        well_names.append(well.name)
        well_bore_names.append([])
        well_trajectory_names.append([])
        print(well.name)
        j = 0
        for wb in well.all_wellbores:
            well_bore_names[i].append(wb.name)
            well_trajectory_names[i].append([])
            print('   ' + wb.name)
            for trj in wb.trajectories:
                well_trajectory_names[i][j].append(trj.name)
                print('      ' + trj.name)
            j = j + 1
        i = i + 1


def list_all_logruns(project):
    """ For each well and each wellbore and each trajectory list all logruns"""
    well_names = []
    well_bore_names = []
    well_trajectory_names = []
    well_logruns_names = []
    i = 0
    for well in project.wells:
        well_names.append(well.name)
        well_bore_names.append([])
        well_trajectory_names.append([])
        well_logruns_names.append([])
        print(well.name)
        j = 0
        for wb in well.all_wellbores:
            well_bore_names[i].append(wb.name)
            well_trajectory_names[i].append([])
            well_logruns_names[i].append([])
            print('   ' + wb.name)
            k = 0
            for trj in wb.trajectories:
                well_trajectory_names[i][j].append(trj.name)
                well_logruns_names[i][j].append([])
                print('      ' + trj.name)
                n = 0
                for logrun in trj.log_runs:
                    well_logruns_names[i][j][k].append(logrun.name)
                    print('         ' + logrun.name)
                    n = n + 1
                k = k + 1
            j = j + 1
        i = i + 1


def get_code_names(project):
    """ For each well and each wellbore and each trajectory list all logruns"""
    return {well.name: _get_well_bores(well) for well in project.wells}


def _get_well_bores(well):
    return {well_bore.name: _get_trajectories(well_bore) for well_bore in well.all_wellbores}


def _get_trajectories(well_bore):
    return {trajectory.name: _get_log_runs(trajectory) for trajectory in well_bore.trajectories}


def _get_log_runs(trajectory):
    return {logrun.name: _get_code_names(logrun) for logrun in trajectory.log_runs}


def _get_code_names(logrun):
    return {log.name: log.get_code_names() for log in logrun.log_curves if log.is_discrete}


def list_all_logs(project):
    """ For each well and each wellbore and each trajectory and each logrun list all logs"""
    well_names = []
    well_bore_names = []
    well_trajectory_names = []
    well_logruns_names = []
    well_logs_names = []
    i = 0
    for well in project.wells:
        well_names.append(well.name)
        well_bore_names.append([])
        well_trajectory_names.append([])
        well_logruns_names.append([])
        well_logs_names.append([])
        print(well.name)
        j = 0
        for wb in well.all_wellbores:
            well_bore_names[i].append(wb.name)
            well_trajectory_names[i].append([])
            well_logruns_names[i].append([])
            well_logs_names[i].append([])
            print('   ' + wb.name)
            k = 0
            for trj in wb.trajectories:
                well_trajectory_names[i][j].append(trj.name)
                well_logruns_names[i][j].append([])
                well_logs_names[i][j].append([])
                print('      ' + trj.name)
                n = 0
                for logrun in trj.log_runs:
                    well_logruns_names[i][j][k].append(logrun.name)
                    well_logs_names[i][j][k].append([])
                    print('         ' + logrun.name)
                    m = 0
                    for log in logrun.log_curves:
                        well_logs_names[i][j][k][n].append(log.name)
                        if log.is_discrete:
                            logtype = 'Discrete'
                        else:
                            logtype = 'Continuous'
                        print('            ' + log.name + ' type: ' + logtype)
                        m = m + 1
                    n = n + 1
                k = k + 1
            j = j + 1
        i = i + 1


def get_code_names_for_log(project, name):
    """ Run through all wells and check if a log with specified name exist. Save the code_names and code_values.
        If there are more than one well with the specified log name, check that the code_names and
        code_values are equal. If this is true, return the code_names dictionary else return None.
    """
    list_of_list_of_code_names = []
    code_names = None
    for well in project.wells:

        for wb in well.all_wellbores:
            # print('   ' + wb.name)
            for trj in wb.trajectories:
                # print('      ' + trj.name)
                for logrun in trj.log_runs:
                    # print('      ' + logrun.name)
                    for log in logrun.log_curves:
                        if log.is_discrete:
                            if log.name == name:
                                # Found a log with correct name
                                code_names = log.get_code_names()
                                for cn in list_of_list_of_code_names:
                                    # Check that the two dictionaries are equal
                                    testValue = cmp(cn, code_names)
                                    if testValue != 0:
                                        print('code_names:')
                                        print(code_names)
                                        print('cn:')
                                        print(cn)
                                        return None
                            # print('         ' + log.name + ' type: ' + logtype)
        print('Facies table for log with name {}'.format(name))
        print(code_names)
    return code_names


def all_trajectories_in_project(project):
    """Generate all the trajectories associated with a given project."""
    for well in project.wells:
        for wellbore in well.all_wellbores:
            for trajectory in wellbore.trajectories:
                yield trajectory


def all_log_curves_with_name(project, name):
    """Generate all log curves bearing a specified name."""
    for trajectory in all_trajectories_in_project(project):
        for log_run in trajectory.log_runs:
            try:
                yield log_run.log_curves[name]
            except KeyError:
                pass


def search(project, name):
    """
        Display all log curves with a specific name. This function displays the well name, trajectory name,
        log run name and log curve name of matching log curves found in the project.
    """
    for log_curve in all_log_curves_with_name(project, name):
        print("{} : {} : {} : {}".format(log_curve.log_run.trajectory.wellbore.name, log_curve.log_run.trajectory.name,
                                         log_curve.log_run.name, log_curve.name))
    # --------------------------------------------------------------


# Main script body
# Define a name to search for
# log_curve_name = 'Facies'
# search(project, log_curve_name)
#
# print('List of all wells in RMS project:')
# list_all_wells(project)
#
# print('\nList of all wells with well bores in RMS project:')
# list_all_wellbores(project)
#
# print('\nList of all wells with well bores and trajectories in RMS project:')
# list_all_trajectories(project)
#
# print('\nList of all wells with well bores and trajectories and logruns in RMS project:')
# list_all_logruns(project)
#
# print('\nList of all wells with well bores and trajectories and logruns and logs in RMS project:')
# list_all_logs(project)
#
# name = 'Facies'
# code_names = get_code_names_for_log(project, name)
# if code_names is not None:
#     print('Log with name: {} has Code_names:'.format(name))
#     print(code_names)
# else:
#     print(
#        'Could not find any log with name {} or the log is not defined with same code_names in all wells where the log exists'
#         ''.format(name))

# list_all_logruns(project)
