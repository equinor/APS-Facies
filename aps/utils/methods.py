# -*- coding: utf-8 -*-
from pathlib import Path
from typing import Dict, TypeVar, Set, Type, List, Optional, Union
from xml.etree.ElementTree import Element

import numpy as np
from enum import Enum
from warnings import warn

from aps.utils.constants.simple import Debug, ModelFileFormat
from aps.utils.exceptions.xml import MissingKeyword
from aps.utils.aps_config import APSConfig
from copy import copy

from aps.utils.types import (
    ModelFile,
    SeedLogFile,
    OutputModelFile,
    GlobalVariablesFile,
    RmsProjectDataFile,
    FilePath,
    WorkflowName,
    ProbabilityLogSpecificationFile,
    JobName,
)

T = TypeVar('T')
U = TypeVar('U')


def invert_dict(to_be_inverted: Dict[T, U]) -> Dict[U, T]:
    return {to_be_inverted[key]: key for key in to_be_inverted.keys()}


def get_legal_values_of_enum(enum: Union[Enum, Type[Enum]]) -> Set[int]:
    if isinstance(enum, Enum) or issubclass(enum, Enum):
        return {v.value for v in enum.__members__.values()}
    return set([])


def get_printable_legal_values_of_enum(enum: Union[Enum, Type[Enum]]) -> List[str]:
    legal_values = get_legal_values_of_enum(enum)
    if legal_values:
        return [str(values) for values in legal_values]
    return ['']


def get_item_from_model_file(
    tree: Element, keyword: str, model_file_name: Optional[str] = None
) -> str:
    item = tree.find(keyword)
    if item is not None:
        text = item.text.strip()
        return copy(text.strip())
    else:
        raise MissingKeyword(keyword, model_file_name)


def get_selected_zones(
    tree: Element, keyword: str = 'SelectedZones', model_file: Optional[str] = None
) -> List[int]:
    obj = tree.find(keyword)
    if obj is None:
        raise MissingKeyword(keyword, model_file)

    texts = obj.text.split()
    try:
        zone_numbers = [int(s.strip()) for s in texts]
    except ValueError:
        print(
            f'Specified zone numbers in keyword {keyword} are not only positive integer values'
        )

    for znr in zone_numbers:
        if znr <= 0:
            raise ValueError(
                f'List of selected zone numbers must have positive integer values'
            )
    return zone_numbers


def get_colors(n: int, min_colors: int = 2) -> List[str]:
    """
    :param n: The number of colors / facies
    :type n: int
    :param min_colors: The minimum number of colors needed. Default 2
    :type min_colors: int
    :return: List of colors
    :rtype: List[str]
    """
    colors = [
        'lawngreen',
        'grey',
        'dodgerblue',
        'gold',
        'darkorchid',
        'cyan',
        'firebrick',
        'olivedrab',
        'blue',
        'crimson',
        'darkorange',
        'red',
    ]
    if min_colors <= n <= len(colors):
        return colors[:n]
    else:
        return []


def get_model_file_name(_default_name: str = 'APS.xml', **kwargs) -> ModelFile:
    return _get_file_name(
        kwargs,
        legal_kwargs=['modelFileName', 'model_file_name', 'model_file', 'model'],
        default_name=_default_name,
    )


def get_rms_project_data_file(**kwargs) -> RmsProjectDataFile:
    return _get_file_name(
        kwargs,
        legal_kwargs=['output_rms_data_file'],
        default_name='rms_project_data_for_APS_gui.xml',
    )


def get_global_variables_file() -> GlobalVariablesFile:
    return APSConfig.global_variables_file()


def get_debug_level(**kwargs) -> Debug:
    debug_level = _get_value(
        kwargs, legal_kwargs=['debugInfo', 'debug_level'], default_value=Debug.OFF
    )
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
        kwargs,
        legal_kwargs=['fmu_variables_file', 'input_selected_fmu_variable_file'],
        default_name='examples/FMU_selected_variables.dat',
    )


def get_output_model_file(**kwargs) -> OutputModelFile:
    return _get_file_name(
        kwargs, legal_kwargs=['output_model_file'], default_name='APS_updated.xml'
    )


def get_output_tagged_variables_file(**kwargs):
    return _get_file_name(
        kwargs,
        legal_kwargs=['output_tagged_variables_file'],
        default_name='output_list_of_FMU_tagged_variables.dat',
    )


def get_tag_all_variables(**kwargs):
    return _get_value(kwargs, legal_kwargs=['tag_all_variables'], default_value=True)


def get_model_file_format(**kwargs) -> ModelFileFormat:
    return ModelFileFormat(
        _get_value(kwargs, legal_kwargs=['model_file_format'], default_value='both')
    )


def get_write_log_file(**kwargs):
    return _get_value(kwargs, legal_kwargs=['write_log_file'], default_value=True)


def get_seed_log_file(**kwargs) -> SeedLogFile:
    return _get_file_name(
        kwargs, legal_kwargs=['seed_log_file'], default_name='seedLogFile.dat'
    )


def _get_file_name(
    kwargs: Dict[str, str], legal_kwargs: List[str], default_name: str
) -> Optional[FilePath]:
    use_prefix_as_fallback = kwargs.get('use_prefix_as_fallback', False)
    file_name = _get_value(kwargs, legal_kwargs, default_name)
    if file_name == default_name and use_prefix_as_fallback:
        prefix = get_prefix(**kwargs)
        file_name = prefix + '/' + default_name
        file_name.replace('//', '/')
    if file_name:
        return Path(file_name)
    return None


def _get_value(kwargs: Dict[str, T], legal_kwargs: List[str], default_value: T) -> T:
    value = default_value
    for keyword in legal_kwargs:
        if keyword in kwargs:
            value = kwargs[keyword]
    return value


def get_prefix(**kwargs) -> str:
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
    RESAMPLE = 5
    PROBABILITY_DEP_TREND = 6
    REMAP_ZONE_MODELS = 7


def get_specification_file(
    _type: SpecificationType = SpecificationType.APS_MODEL,
    _format: ModelFileFormat = ModelFileFormat.XML,
    **kwargs,
) -> Optional[ProbabilityLogSpecificationFile]:
    mapping_xml = {
        SpecificationType.APS_MODEL: 'APS.xml',
        SpecificationType.PROBABILITY_LOG: 'Create_prob_logs.xml',
        SpecificationType.FACIES_LOG: 'Create_redefined_blocked_facies_log.xml',
        SpecificationType.CONVERT_BITMAP: 'bitmap2rms_model.xml',
        SpecificationType.PROBABILITY_TREND: 'defineProbTrend.xml',
        SpecificationType.PROBABILITY_DEP_TREND: 'Create_depositional_probability_trend.xml',
        SpecificationType.RESAMPLE: 'resample.xml',
    }
    mapping_yml = {
        SpecificationType.PROBABILITY_LOG: 'Create_prob_logs.yml',
        SpecificationType.FACIES_LOG: 'Create_redefined_blocked_facies_log.yml',
        SpecificationType.CONVERT_BITMAP: 'bitmap2rms_model.yml',
        SpecificationType.PROBABILITY_TREND: 'defineProbTrend.yml',
        SpecificationType.PROBABILITY_DEP_TREND: 'Create_depositional_probability_trend.yml',
        SpecificationType.RESAMPLE: 'resample.yml',
        SpecificationType.REMAP_ZONE_MODELS: 'redefine_zone_models.yml',
    }
    if _format == ModelFileFormat.XML and _type in mapping_xml:
        file = get_model_file_name(_default_name=mapping_xml[_type], **kwargs)
        if not file:
            file = mapping_xml[_type]
        if Path(file).exists():
            if _type != SpecificationType.APS_MODEL:
                # This print is meant for help scripts in a period before xml format
                # is deprecated for the help scripts.
                print(f'Use XML file: {file} ')
        else:
            raise ValueError(f'File: {file} does not exist.')
        return str(file)
    if _format == ModelFileFormat.YML and _type in mapping_yml:
        file = get_model_file_name(_default_name=mapping_yml[_type], **kwargs)
        if not file:
            file = mapping_yml[_type]
        if Path(file).exists():
            print(f'Use YML file: {file} ')
        else:
            raise ValueError(f'File: {file} does not exist.')
        return str(file)
    if _format == ModelFileFormat.BOTH:
        # First check yml format then xml format
        if _type in mapping_yml:
            file = get_model_file_name(_default_name=mapping_yml[_type], **kwargs)
            if not file:
                file = mapping_yml[_type]
            if Path(file).exists():
                print(f'Use YAML file: {file} ')
                return str(file)
        if _type in mapping_xml:
            file = get_model_file_name(_default_name=mapping_xml[_type], **kwargs)
            if not file:
                file = mapping_xml[_type]
            if Path(file).exists():
                if _type != SpecificationType.APS_MODEL:
                    # This print is meant for help scripts in a period before xml format
                    # is deprecated for the help scripts.
                    print(f'Use XML file: {file} ')
                return str(file)
            else:
                raise ValueError(f'File: {file} does not exist.')
    else:
        raise ValueError(f'Unknown file format: {_format}')


# TODO: Make more generic; dict with precise names?
def get_facies_code(**kwargs):
    return _get_value(kwargs, legal_kwargs=['facies_code'], default_value=0)


def get_run_test_script(**kwargs):
    return _get_value(kwargs, legal_kwargs=['run_test_script'], default_value=False)


def get_run_parameters(**kwargs) -> dict:
    return {
        'model_file': get_specification_file(**kwargs),
        'output_model_file': get_output_model_file(**kwargs),
        'rms_data_file': get_rms_project_data_file(**kwargs),
        'global_variables_file': get_global_variables_file(),
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
        'current_job_name': get_job_name(),
        'debug_level': get_debug_level(**kwargs),
    }


def calc_average(cell_index_defined: List[int], values: List[float]) -> float:
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


def get_workflow_name() -> WorkflowName:
    try:
        import roxar.rms

        name = roxar.rms.get_running_workflow_name()
    except ImportError:
        name = None
    return name


def get_job_name() -> JobName:
    try:
        import roxar.rms

        name = roxar.rms.get_running_job_name()
    except ImportError:
        name = None
    return name


def check_missing_keywords_list(params: dict, required_kw: list):
    missing_kw = []
    for kw in required_kw:
        if kw not in params or params[kw] is None:
            missing_kw.append(kw)
    if len(missing_kw) > 0:
        raise ValueError(f'Missing specification of the keywords: {missing_kw}')


def check_missing_keywords_dict(params: dict, required_kw: dict):
    missing_kw = []
    for kw in required_kw:
        if kw not in params or params[kw] is None:
            missing_kw.append(kw)
    if len(missing_kw) > 0:
        raise ValueError(f'Missing specification of the keywords: {missing_kw}')


def get_cond_prob_dict(
    input_cond_table: dict, active_zone_list: list, common_facies_list: bool = True
):
    conditional_prob_facies = {}
    err_list = []
    common_prob_spec_all_zones = False
    for key in input_cond_table:
        # Check syntax
        try:
            prob = float(input_cond_table[key])
        except ValueError:
            err_list.append(
                f"Specified probability '{input_cond_table[key]}'  is not a float number for '{key}'\n"
            )
        key_string = str(key)
        key_string.strip()
        if key_string[0] != '(' or key_string[-1] != ')':
            err_list.append(f'Missing parenteses in {key}\n')
        text = key_string[1:]
        text = text[: len(text) - 1]
        words = text.split(',')

        if len(words) != 3:
            raise ValueError(
                f'Expecting 3 values: zonenumber, facies_to_model, facies_interpreted  in {key}\n'
            )
        if not common_facies_list:
            if words[0] == '*':
                err_list.append(
                    f"Facies list vary from zone to zone. Can not use '*' in {key}  for zone number in this case."
                )

        if words[0] == '*':
            common_prob_spec_all_zones = True
        else:
            if common_prob_spec_all_zones:
                err_list.append(
                    f"When using '*' for zone number, this must be used for  {key} and all other specified conditional probabilities."
                )
        try:
            if not common_prob_spec_all_zones:
                zone_number = int(words[0])
            fac_to_model = words[1].strip()
            fac_conditioned_to = words[2].strip()
        except ValueError:
            err_list.append(f'Expecting: integer, string, string  in {key}\n')

        if len(err_list) == 0:
            if common_prob_spec_all_zones:
                for znr in active_zone_list:
                    new_key = (znr, fac_to_model, fac_conditioned_to)
                    conditional_prob_facies[new_key] = input_cond_table[key]
            else:
                new_key = (zone_number, fac_to_model, fac_conditioned_to)
                conditional_prob_facies[new_key] = input_cond_table[key]

    if len(err_list) != 0:
        print(f'Errors found:\n')
        for err in err_list:
            print(f' {err}  ')
        print('\n')
        raise ValueError(f'Errors found in specification of conditional probabilities.')

    return conditional_prob_facies
