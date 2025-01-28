#!/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import os
from pathlib import Path
from typing import Dict, List
from aps.utils.constants.simple import Debug
from aps.utils.exceptions.xml import MissingKeyword
from aps.utils.methods import get_item_from_model_file, get_selected_zones
from aps.utils.xmlUtils import getTextCommand
from aps.utils.ymlUtils import get_text_value, readYml


def read_facies_prob_trend_model(
    project, model_file_name: str, trend_keyword: str, debug_level: Debug = Debug.OFF
):
    # Check suffix of file for file type
    model_file = Path(model_file_name)
    suffix = model_file.suffix.lower().strip('.')
    if suffix in ['yaml', 'yml']:
        param_dict = _read_facies_prob_trend_model_yml(
            project, model_file_name, trend_keyword, debug_level=debug_level
        )
    elif suffix == 'xml':
        param_dict = _read_facies_prob_trend_model_xml(
            project, model_file_name, trend_keyword, debug_level=debug_level
        )
    else:
        raise ValueError(
            f"Model file name: {model_file_name}  must be either 'xml' or 'yml' format"
        )
    return param_dict


def _read_facies_prob_trend_model_yml(
    project, model_file_name: str, trend_keyword: str, debug_level: Debug = Debug.OFF
):
    assert model_file_name
    spec_all = readYml(model_file_name)

    parent_kw = trend_keyword
    spec = spec_all[parent_kw] if parent_kw in spec_all else None
    if spec is None:
        raise ValueError(f'Missing keyword: {parent_kw} ')

    grid_model_name = get_text_value(spec, parent_kw, 'GridModelName')
    zone_param_name = get_text_value(spec, parent_kw, 'ZoneParamName')
    facies_interpretation_param_name = get_text_value(
        spec, parent_kw, 'FaciesParamName'
    )
    prefix = get_text_value(spec, parent_kw, 'ProbParamNamePrefix')
    selected_zones_string = get_text_value(spec, parent_kw, 'SelectedZones')
    selected_zones = [int(text) for text in selected_zones_string.split()]
    model_param_dict = {
        'project': project,
        'model_file_name': model_file_name,
        'model_file_format': 'yml',
        'debug_level': debug_level,
        'grid_model_name': grid_model_name,
        'zone_param_name': zone_param_name,
        'facies_interpretation_param_name': facies_interpretation_param_name,
        'prefix': prefix,
        'selected_zones': selected_zones,
        'parent_dict': spec,
        'parent_kw': parent_kw,
    }
    return model_param_dict


def _read_facies_prob_trend_model_xml(
    project, model_file_name: str, trend_keyword: str, debug_level: Debug = Debug.OFF
):
    assert model_file_name
    if not os.path.exists(model_file_name):
        raise IOError(f'File {model_file_name} does not exist')

    tree = ET.parse(model_file_name).getroot()
    root = tree.find(trend_keyword)
    if root is None:
        raise MissingKeyword(trend_keyword, model_file_name)
    kwargs = dict(parentKeyword=trend_keyword, modelFile=model_file_name, required=True)

    grid_model_name = getTextCommand(root, 'GridModelName', **kwargs)

    zone_param_name = getTextCommand(root, 'ZoneParamName', **kwargs)

    facies_interpretation_param_name = getTextCommand(root, 'FaciesParamName', **kwargs)

    prefix = getTextCommand(root, 'ProbParamNamePrefix', **kwargs)

    selected_zones = get_selected_zones(root, model_file=model_file_name)

    model_param_dict = {
        'project': project,
        'model_file_name': model_file_name,
        'model_file_format': 'xml',
        'debug_level': debug_level,
        'grid_model_name': grid_model_name,
        'zone_param_name': zone_param_name,
        'facies_interpretation_param_name': facies_interpretation_param_name,
        'prefix': prefix,
        'selected_zones': selected_zones,
        'trend_root': root,
    }
    return model_param_dict


class BaseDefineFacies:
    def __init__(
        self,
        project=None,
        model_file_name: str = None,
        trend_keyword: str = None,
        debug_level: Debug = Debug.OFF,
        grid_model_name: str = None,
        zone_param_name: str = None,
        facies_interpretation_param_name: str = None,
        prefix: str = None,
        selected_zones: List[int] = [],
    ):
        assert project
        self._project = project
        self._debug_level = debug_level

        self._grid_model_name = grid_model_name
        self._zone_parameter_name = zone_param_name
        self._facies_parameter_name = facies_interpretation_param_name
        self._probability_parameter_name_prefix = prefix
        self._selected_zone_numbers = selected_zones

        self._trend_root = None

        if model_file_name is not None:
            # Read model file and overwrite model parameters
            print(f'Read model file: {model_file_name}  ')
            if trend_keyword not in ['FaciesProbTrend', 'FaciesProbMapDepTrend']:
                raise ValueError(
                    f'Internal programming error. Undefined input for trend_keyword: {trend_keyword} '
                )
            model_param_dict = read_facies_prob_trend_model(
                project,
                model_file_name,
                trend_keyword=trend_keyword,
                debug_level=debug_level,
            )

            self._file_format = model_param_dict['model_file_format']
            if self._file_format == 'xml':
                self._trend_root = model_param_dict['trend_root']
            elif self._file_format == 'yml':
                self._parent_dict = model_param_dict['parent_dict']
                self._parent_kw = model_param_dict['parent_kw']

            self._grid_model_name = model_param_dict['grid_model_name']
            self._zone_parameter_name = model_param_dict['zone_param_name']
            self._facies_parameter_name = model_param_dict[
                'facies_interpretation_param_name'
            ]
            self._probability_parameter_name_prefix = model_param_dict['prefix']
            self._selected_zone_numbers = model_param_dict['selected_zones']

        # Check that all necessary parameters are set
        if self._grid_model_name is None:
            raise ValueError(f'Missing specification of: grid_model_name')
        if self._zone_parameter_name is None:
            raise ValueError(f'Missing specification of: zone_parameter_name')
        if self._facies_parameter_name is None:
            raise ValueError(f'Missing specification of: facies_parameter_name')
        if self._probability_parameter_name_prefix is None:
            raise ValueError(f'Missing specification of: prefix')
        if len(self._selected_zone_numbers) == 0:
            raise ValueError(f'Missing specification of: selected_zones')

    @property
    def debug_level(self):
        return self._debug_level

    @property
    def grid_model_name(self):
        return self._grid_model_name

    @property
    def zone_param_name(self):
        return self._zone_parameter_name

    @property
    def facies_param_name(self):
        return self._facies_parameter_name

    @property
    def project(self):
        return self._project

    @property
    def selected_zone_numbers(self):
        return self._selected_zone_numbers

    @property
    def prefix(self):
        return self._probability_parameter_name_prefix

    def calculate_facies_probability_parameter(self, debug_level=Debug.OFF):
        raise NotImplementedError
