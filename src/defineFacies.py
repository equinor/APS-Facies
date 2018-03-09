#!/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET

from src.utils.constants.simple import Debug
from src.utils.exceptions.xml import MissingKeyword
from src.utils.methods import get_item_from_model_file, get_selected_zones


def xml_property(keyword):
    def wrapper(func):
        @property
        def decorator(self):
            attribute_name = '_' + func.__qualname__.replace('.', '__')
            param = self.__getattribute__(attribute_name)
            if param is None:
                self.__setattr__(attribute_name, self._get_item_from_model_file(keyword))
            return self.__getattribute__(attribute_name)
        return decorator
    return wrapper


class BaseDefineFacies:
    def __init__(self, model_file_name, project, main_keyword, debug_level=Debug.OFF):
        assert model_file_name
        assert project

        self.debug_level = debug_level
        self._model_file_name = model_file_name
        self._root = self.get_root(model_file_name, main_keyword)
        self.__project = project

        self.__grid_model_name = None
        self.__zone_parameter_name = None
        self.__facies_parameter_name = None
        self.__probability_parameter_name_prefix = None
        self.__selected_zone_numbers = None

    @property
    def project(self):
        return self.__project

    @xml_property('GridModelName')
    def grid_model_name(self): pass

    @xml_property('ZoneParamName')
    def zone_parameter_name(self): pass

    @xml_property('FaciesParamName')
    def facies_parameter_name(self): pass

    @xml_property('ProbParamNamePrefix')
    def probability_parameter_name_prefix(self): pass

    @property
    def selected_zone_numbers(self):
        if self.__selected_zone_numbers is None:
            self.__selected_zone_numbers = get_selected_zones(self._root, model_file=self._model_file_name)
        return self.__selected_zone_numbers

    def _get_item_from_model_file(self, keyword):
        return get_item_from_model_file(self._root, keyword, self._model_file_name)

    def get_root(self, model_file_name, main_keyword):
        if self.debug_level >= Debug.ON:
            print('Read model file: ' + model_file_name)
        tree = ET.parse(model_file_name).getroot()
        root = tree.find(main_keyword)
        if root is None:
            raise MissingKeyword(main_keyword, model_file_name)
        return root

    def calculate_facies_probability_parameter(self, debug_level=Debug.OFF):
        raise NotImplementedError
