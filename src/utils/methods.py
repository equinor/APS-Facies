# -*- coding: utf-8 -*-
from pathlib import Path

import numpy as np
from enum import Enum
from warnings import warn

from src.utils.constants.simple import Debug
from src.utils.exceptions.xml import MissingKeyword

from copy import copy


def invert_dict(to_be_inverted):
    return {
        to_be_inverted[key]: key for key in to_be_inverted.keys()
    }


def get_legal_values_of_enum(enum):
    if isinstance(enum, Enum) or issubclass(enum, Enum):
        return {v.value for v in enum.__members__.values()}
    return set([])


def get_printable_legal_values_of_enum(enum):
    legal_values = get_legal_values_of_enum(enum)
    if legal_values:
        return [str(values) for values in legal_values]
    return ['']


def get_item_from_model_file(tree, keyword, model_file_name=None):
    item = tree.find(keyword)
    if item is not None:
        text = item.text.strip()
        return copy(text.strip())
    else:
        raise MissingKeyword(keyword, model_file_name)


def get_selected_zones(tree, keyword='SelectedZones', model_file=None):
    obj = tree.find(keyword)
    if obj is None:
        raise MissingKeyword(keyword, model_file)

    texts = obj.text.split()
    zone_numbers = [int(s.strip()) for s in texts]
    return [
        zone_number - 1  # Zone numbers are specified from 1, but need them numbered from 0
        for zone_number in zone_numbers
    ]


def get_colors(n, min_colors=2):
    """
    :param n: The number of colors / facies
    :type n: int
    :param min_colors: The minimum number of colors needed. Default 2
    :type min_colors: int
    :return: List of colors
    :rtype: List[str]
    """
    colors = [
        'lawngreen', 'grey', 'dodgerblue', 'gold', 'darkorchid', 'cyan', 'firebrick',
        'olivedrab', 'blue', 'crimson', 'darkorange', 'red',
    ]
    if min_colors <= n <= len(colors):
        return colors[:n]
    else:
        return []


def get_model_file_name(_default_name='APS.xml', **kwargs):
    return _get_file_name(
        kwargs, legal_kwargs=['modelFileName', 'model_file_name', 'model_file', 'model'], default_name=_default_name,
    )


def get_rms_project_data_file(**kwargs):
    return _get_file_name(
        kwargs, legal_kwargs=['output_rms_data_file'], default_name='rms_project_data_for_APS_gui.xml',
    )


def get_global_variables_file(**kwargs):
    return _get_file_name(
        kwargs,
        legal_kwargs=[
            'global_variables', 'globalIPLFile', 'global_ipl_file', 'global_include_file', 'global_variables_file',
        ],
        default_name='../../fmuconfig/output/global_variables.yml',
    )


def get_debug_level(**kwargs):
    debug_level = _get_value(kwargs, legal_kwargs=['debugInfo', 'debug_level'], default_value=Debug.OFF)
    if isinstance(debug_level, str):
        try:
            debug_level = int(debug_level)
        except ValueError:
            warn('Illegal debug level, {}. Using default of OFF'.format(debug_level))
            debug_level = Debug.OFF
    if isinstance(debug_level, int):
        debug_levels = get_legal_values_of_enum(Debug)
        if debug_level < min(debug_levels):
            debug_level = min(debug_levels)
        elif debug_level > max(debug_levels):
            debug_level = max(debug_levels)
        return Debug(debug_level)
    else:
        return debug_level


def get_fmu_variables_file(**kwargs):
    return _get_file_name(
        kwargs, legal_kwargs=['fmu_variables_file', 'input_selected_fmu_variable_file'],
        default_name='examples/FMU_selected_variables.dat',
    )


def get_output_model_file(**kwargs):
    return _get_file_name(kwargs, legal_kwargs=['output_model_file'], default_name='APS_updated.xml')


def get_output_tagged_variables_file(**kwargs):
    return _get_file_name(
        kwargs, legal_kwargs=['output_tagged_variables_file'], default_name='output_list_of_FMU_tagged_variables.dat',
    )


def get_tag_all_variables(**kwargs):
    return _get_value(kwargs, legal_kwargs=['tag_all_variables'], default_value=True)


def get_write_log_file(**kwargs):
    return _get_value(kwargs, legal_kwargs=['write_log_file'], default_value=True)


def get_seed_log_file(**kwargs):
    return _get_file_name(kwargs, legal_kwargs=['seed_log_file'], default_name='seedLogFile.dat')


def _get_file_name(kwargs, legal_kwargs, default_name):
    use_prefix_as_fallback = kwargs.get('use_prefix_as_fallback', False)
    file_name = _get_value(kwargs, legal_kwargs, default_name)
    if file_name == default_name and use_prefix_as_fallback:
        prefix = get_prefix(**kwargs)
        file_name = prefix + '/' + default_name
        file_name.replace('//', '/')
    if file_name:
        return Path(file_name)
    return None


def _get_value(kwargs, legal_kwargs, default_value):
    value = default_value
    for keyword in legal_kwargs:
        if keyword in kwargs:
            value = kwargs[keyword]
    return value


def get_prefix(**kwargs):
    base_path = kwargs.get('prefix', '.')
    if base_path.endswith('/'):
        base_path = base_path[:-1]
    return base_path


class SpecificationType(Enum):
    APS_MODEL = 0
    PROBABILITY_LOG = 1
    FACIES_LOG = 2
    CONVERT_BITMAP = 3
    PROBABILITY_TREND = 4


def get_specification_file(_type=SpecificationType.APS_MODEL, **kwargs):
    mapping = {
        SpecificationType.APS_MODEL: 'APS.xml',
        SpecificationType.PROBABILITY_LOG: 'Create_prob_logs.xml',
        SpecificationType.FACIES_LOG: 'Create_redefined_blocked_facies_log.xml',
        SpecificationType.CONVERT_BITMAP: 'bitmap2rms_model.xml',
        SpecificationType.PROBABILITY_TREND: 'defineProbTrend.xml',
    }
    if _type in mapping:
        file = get_model_file_name(_default_name=mapping[_type], **kwargs)
        if not file:
            file = mapping[_type]
        return str(file)
    return None


# TODO: Make more generic; dict with precise names?
def get_facies_code(**kwargs):
    return _get_value(kwargs, legal_kwargs=['facies_code'], default_value=0)


def get_run_test_script(**kwargs):
    return _get_value(kwargs, legal_kwargs=['run_test_script'], default_value=False)


def get_run_parameters(**kwargs):
    return {
        'model_file': get_specification_file(**kwargs),
        'output_model_file': get_output_model_file(**kwargs),
        'rms_data_file': get_rms_project_data_file(**kwargs),
        'global_variables_file': get_global_variables_file(**kwargs),
        'output_tagged_variables_file': get_output_tagged_variables_file(**kwargs),
        'tag_all_variables': get_tag_all_variables(**kwargs),
        'fmu_variables_file': get_fmu_variables_file(**kwargs),
        'write_log_file': get_write_log_file(**kwargs),
        'seed_log_file': get_seed_log_file(**kwargs),
        'input_directory': get_prefix(**kwargs) + '/tmp_gauss_sim',
        'probability_log_specification_file': get_specification_file(**kwargs),
        'facies_code': get_facies_code(**kwargs),
        'run_test_script': get_run_test_script(**kwargs),
        'workflow_name': get_workflow_name(),
        'current_job_name' : get_job_name(),
        'debug_level': get_debug_level(**kwargs),
    }


def calc_average(cell_index_defined, values):
    """
    Calculates average of the values array.
    Input:
           numpy arrays for:
           cell_index_defined - Array of cell indices to cells to be averaged.
           values - Array of values (all cell values from a RMS property)
    Output:
            average  - average value
    """
    return np.average(values[cell_index_defined])


def get_workflow_name():
    try:
        import roxar.rms
        name = roxar.rms.get_running_workflow_name()
    except ImportError:
        name = None
    return name

def get_job_name():
    try:
        import roxar.rms
        name = roxar.rms.get_running_job_name()
    except ImportError:
        name = None
    return name
