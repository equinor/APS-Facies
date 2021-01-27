# -*- coding: utf-8 -*-
from typing import List, Union, Dict, Any

import numpy as np
from enum import Enum

from aps.algorithms.truncation_rules import Trunc2D_Cubic, Trunc3D_bayfill, Trunc2D_Angle
from aps.algorithms.properties import FmuProperty
from aps.algorithms.APSMainFaciesTable import APSMainFaciesTable, Facies
from aps.utils.constants.simple import Debug
from aps.utils.types import FaciesName


class TruncationType(Enum):
    CUBIC = 'cubic'
    NON_CUBIC = 'non-cubic'
    BAYFILL = 'bayfill'


def ordered(func):
    def wrapper(*args, **kwargs):
        items = func(*args, **kwargs)
        if all([isinstance(item, tuple) for item in items]):
            return [item[0] for item in sorted(items, key=lambda x: x[1])]
        return items
    return wrapper


class TruncationSpecification:
    __slots__ = '_type', '_facies_table', '_gaussian_fields', '_values', '_probabilities', '_use_constant_parameters'

    def __init__(
            self,
            _type:                   Union[str, TruncationType],
            facies_table:            Dict[str, List[Facies]],
            gaussian_fields:         Dict[str, Any],
            values:                  Dict[str, Any],
            probabilities:           Dict[str, float],
            use_constant_parameters: bool,
    ):
        self._type = TruncationType(_type)
        self._facies_table = facies_table
        self._gaussian_fields = gaussian_fields
        self._values = values
        self._probabilities = probabilities
        self._use_constant_parameters = use_constant_parameters

    @property
    def type(self) -> TruncationType:
        return self._type

    @property
    def global_facies_table(self) -> List[Facies]:
        return self._facies_table['global']

    @property
    def facies_in_zone(self) -> List[Facies]:
        return self._facies_table['zone']

    @property
    @ordered
    def facies_in_rule(self) -> List[Facies]:
        return self._facies_table['rule']

    @property
    def fields_in_zone(self) -> List[str]:
        return self._gaussian_fields['zone']

    @property
    @ordered
    def fields_in_rule(self) -> List[str]:
        return self._gaussian_fields['rule']

    @property
    @ordered
    def fields_in_background(self) -> List[List[List[str]]]:
        return self._gaussian_fields['background']

    @property
    def use_constant_parameters(self) -> bool:
        return self._use_constant_parameters

    @property
    def values(self) -> dict:
        if self.type == TruncationType.BAYFILL:
            values = {
                item['name'].lower(): FmuProperty(item['factor']['value'], item['factor']['updatable'])
                for item in self._values['polygons']
            }
            return {
                'sf_value': values['sf'].value,
                'sf_fmu_updatable': values['sf'].updatable,
                'sf_name': '',
                'ysf': values['ysf'].value,
                'ysf_fmu_updatable': values['ysf'].updatable,
                'sbhd': values['sbhd'].value,
                'sbhd_fmu_updatable': values['sbhd'].updatable,
                'faciesInTruncRule': [facies.name for facies in self.facies_in_rule],
            }
        elif self.type == TruncationType.NON_CUBIC:
            return {
                'truncStructure': [
                    [polygon['facies'], polygon['angle']['value'], polygon['fraction'], polygon['angle']['updatable']]
                    for polygon in self._polygons()
                ],
                'overlayGroups': self._get_overlay(),
                'keyResolution': 209,
            }
        elif self.type == TruncationType.CUBIC:
            return {
                'truncStructureList': [self._values['direction']] + [
                        [polygon['facies'], polygon['fraction']] + polygon['level']
                        for polygon in self._polygons(sort=False)
                    ],
                'overlayGroups': self._get_overlay(),
                'keyResolution': 209,
            }
        else:
            raise ValueError("Invalid truncation type ({type})".format(type=self.type))

    def _polygons(self, _type='polygons', sort=True):
        if sort:
            return sorted(self._values[_type] or [], key=lambda polygon: polygon['order'])
        else:
            return self._values[_type]

    @property
    def probabilities(self) -> List[float]:
        return [self._probabilities[facies.name] for facies in self.facies_in_zone]

    @classmethod
    def from_dict(
            cls,
            specification:           dict
    ) -> 'TruncationSpecification':
        facies_tables = cls._get_facies_table(specification)
        fields = cls._get_gaussian_fields(specification)
        probabilities = cls._get_facies_probabilities(specification)
        return cls(
            _type=TruncationType(specification['type']),
            facies_table=facies_tables,
            gaussian_fields=fields,
            values=specification['values'],
            probabilities=probabilities,
            use_constant_parameters=specification['constantParameters'],
        )

    def _get_overlay(self):
        overlay = {}
        for polygon in self._polygons(_type='overlay'):
            over = self._get_overlay_facies(polygon)
            if over not in overlay:
                overlay[over] = []
            overlay[over].append([polygon['field'], polygon['facies'], polygon['fraction'], polygon['center']])
        for over in overlay:
            overlay[over] = [overlay[over], list(over)]
        return list(overlay.values())

    @staticmethod
    def _get_overlay_facies(polygon):
        over = polygon['over']
        over.sort()
        return tuple(over)

    @staticmethod
    def _get_facies_table(specification: dict) -> dict:
        facies_tables = {
            'global': [],
            'zone': [],
            'rule': [],
        }
        for facies in specification['globalFaciesTable']:
            item = Facies(facies['name'], facies['code'])
            facies_tables['global'].append(item)
            if facies['inZone']:
                facies_tables['zone'].append(item)
            order = facies['inRule']
            if order >= 0:
                facies_tables['rule'].append((item, order))
        return facies_tables

    @staticmethod
    def _get_facies_probabilities(specification: dict) -> Dict[FaciesName, float]:
        return {
            facies['name']: facies['probability']
            for facies in specification['globalFaciesTable']
        }

    @staticmethod
    def _get_gaussian_fields(specification: dict) -> dict:
        fields = {
            'zone': [],
            'rule': [],
            'background': [],
        }
        for field in specification['gaussianRandomFields']:
            item = field['name']
            if field['inZone']:
                fields['zone'].append(item)
            order = field['inRule']
            if order >= 0:
                fields['rule'].append((item, order))
                if field.get('inBackground', True):
                    fields['background'].append((item, order))
        return fields


def make_truncation_rule(specification: Union[TruncationSpecification, dict]) -> Union[Trunc2D_Angle, Trunc3D_bayfill]:
    specification = TruncationSpecification.from_dict(specification)

    facies_table = APSMainFaciesTable(
        facies_table={facies.code: facies.name for facies in specification.global_facies_table}
    )
    kwargs = {
        'faciesInZone': [facies.name for facies in specification.facies_in_zone],
        'alphaFieldNameForBackGroundFacies': [field for field in specification.fields_in_background],
        'gaussFieldsInZone': [field for field in specification.fields_in_zone],
        'useConstTruncParam': specification.use_constant_parameters,
        'debug_level': Debug.OFF,
    }
    kwargs.update(specification.values)

    if specification.type == TruncationType.CUBIC:
        trunc = Trunc2D_Cubic()
        del kwargs['useConstTruncParam']
    elif specification.type == TruncationType.NON_CUBIC:
        trunc = Trunc2D_Angle()
    elif specification.type == TruncationType.BAYFILL:
        trunc = Trunc3D_bayfill()
    else:
        raise NotImplementedError()

    trunc.initialize(
        facies_table,
        **kwargs
    )

    trunc.setTruncRule(np.array(specification.probabilities))
    return trunc
