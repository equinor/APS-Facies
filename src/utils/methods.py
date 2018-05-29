from enum import Enum

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
    selected_zone_numbers = []
    zones = []
    obj = tree.find(keyword)
    if obj is not None:
        texts = obj.text.split()
        for s in texts:
            zones.append(int(s.strip()))
        for i in range(len(zones)):
            zone_number = zones[i]
            # Zone numbers are specified from 1, but need them numbered from 0
            selected_zone_numbers.append(zone_number - 1)
        return selected_zone_numbers
    else:
        raise MissingKeyword(keyword, model_file)


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


def get_model_file_name(**kwargs):
    return _get_file_name(kwargs, legal_kwargs=['modelFileName', 'model_file_name', 'model'], default_name='APS.xml')


def get_rms_project_data_file(**kwargs):
    return _get_file_name(kwargs, legal_kwargs=['output_rms_data_file'], default_name='rms_project_data_for_APS_gui.xml')


def get_global_ipl_file(**kwargs):
    return _get_file_name(kwargs, legal_kwargs=['globalIPLFile', 'global_ipl_file'], default_name='test_global_include.ipl')


def get_debug_level(**kwargs):
    debug_level = _get_value(kwargs, legal_kwargs=['debugInfo', 'debug_level'], default_value=Debug.OFF)
    if isinstance(debug_level, int):
        debug_levels = get_legal_values_of_enum(Debug)
        if debug_level < min(debug_levels):
            debug_level = min(debug_levels)
        elif debug_level > max(debug_levels):
            debug_level = max(debug_levels)
        return Debug(debug_level)
    else:
        return debug_level


def _get_file_name(kwargs, legal_kwargs, default_name):
    use_prefix_as_fallback = kwargs.get('use_prefix_as_fallback', False)
    file_name = _get_value(kwargs, legal_kwargs, default_name)
    if file_name == default_name and use_prefix_as_fallback:
        prefix = get_prefix(**kwargs)
        file_name = prefix + '/' + default_name
        file_name.replace('//', '/')
    return file_name


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


def get_run_parameters(**kwargs):
    base_path = get_prefix(**kwargs)
    model_file = get_model_file_name(**kwargs)
    rms_data_file = get_rms_project_data_file(**kwargs)
    global_ipl_file = get_global_ipl_file(**kwargs)
    debug_level = get_debug_level(**kwargs)
    input_dir = base_path + '/tmp_gauss_sim'
    return model_file, rms_data_file, global_ipl_file, input_dir, debug_level
