#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import re
import sys
from copy import deepcopy
from pathlib import Path
from typing import List


def find_polygon_references(polygons, item):
    references = []
    for polygon in polygons:
        if polygon['facies'] == item[0]:
            if 'name' in polygon:
                references.append(polygon['name'])
            elif 'order' in polygon:
                references.append(polygon['order'])
            else:
                raise KeyError(f'No name or order in polygon {polygon}')

    if len(references) == 0:
        return -1
    elif len(references) == 1:
        return references.pop()
    else:
        return tuple(references)


def make_empty_fields(num):
    return [
        {
            'channel': i,
            'field': {
                'name': f'GRF0{i}',
            },
        }
        for i in range(1, num + 1)
    ]


def get_array(content, key):
    return json.loads(content[key].replace("'", '"'))


def make_overlay_polygon(elem):
    return {
        'field': {'name': elem[0]},
        'facies': {'name': elem[1]},
        'probability': elem[2],
        'interval': elem[3],
    }


def _get_overlays(rule, content):
    _mapping = {
        'non-cubic': 'NonCubicAndOverlay',
        'cubic': 'CubicAndOverlay',
    }
    extension = [rule]
    try:
        connections = content[_mapping[rule['type']]].values()
    except KeyError:
        connections = []
    for connection in connections:
        if connection['rule'] == rule['name']:
            _rule = deepcopy(rule)
            _rule['name'] = connection['name']
            _rule['overlay'] = content['overlay'][connection['overlay']]['settings']
            extension.append(_rule)
    return extension


def _extend_rules_with_overlay(rules, content):
    with_overlays = []
    for rule in rules:
        with_overlays.extend(_get_overlays(rule, content))
    return with_overlays


class Parser:
    @classmethod
    def parse(cls, lines: List[str]):
        content = {}
        for line in lines:
            item = cls._parse(line.strip())
            if item:
                if item['type'] not in content:
                    content[item['type']] = {}
                content[item['type']][item['name']] = item
        rules = cls._make_rules(content)
        rules = cls._copy_rules(rules)
        rules = cls._add_indices(rules)
        rules = cls._add_minimum_fields(rules)
        return rules

    @staticmethod
    def _copy_rules(rules):
        """Helper method to ensure NO dicts are duplicated by Python, to "optimize" memory usage"""
        _rules = []
        for rule in rules:
            _rules.append(deepcopy(rule))
        return _rules

    @staticmethod
    def _parse(line: str):
        if not line:
            return None
        _type = line.split(' ')[0]
        parsers = {
            'Bayfill': Parser.Bayfill,
            'Cubic': Parser.Cubic,
            'NonCubic': Parser.NonCubic,
            'Overlay': Parser.Overlay,
            'NonCubicAndOverlay': Parser.Combination,
            'CubicAndOverlay': Parser.Combination,
        }
        try:
            parser = parsers[_type]
        except KeyError:
            raise ValueError(f'Invalid type; {_type}')
        return parser.parse(line)

    @staticmethod
    def _add_indices(rules):
        # TODO: Finne alle navn på felter og facies, or så å indeksere de (i alfabetisk rekkefølge)
        for rule in rules:
            indices = {
                'facies': _get_all_facies_indices(rule),
                'field': _get_all_fields_indices(rule),
            }
            if not all(_is_indexed(polygon['facies']) for polygon in rule['polygons']):
                for polygon in rule['polygons']:
                    facies_name = polygon['facies']
                    polygon['facies'] = {
                        'name': facies_name,
                        'index': indices['facies'][facies_name],
                    }
            for item in rule['fields']:
                field_name = item['field']['name']
                item['field']['index'] = indices['field'][field_name]
            if 'overlay' in rule:
                for item in rule['overlay']:
                    for polygon in item['polygons']:
                        field_name = polygon['field']['name']
                        polygon['field']['index'] = indices['field'][field_name]

                        facies_name = polygon['facies']['name']
                        polygon['facies']['index'] = indices['facies'][facies_name]
                    for facies in item['background']:
                        facies['index'] = indices['facies'][facies['name']]
        return rules

    @staticmethod
    def _add_minimum_fields(rules):
        for rule in rules:
            rule['minFields'] = len(_get_all_fields_indices(rule))
        return rules

    @staticmethod
    def _make_rules(content: dict):
        types = ['cubic', 'non-cubic', 'bayfill']
        rules = []
        for _type in types:
            if _type in content:
                rules.extend(content[_type].values())
        return _extend_rules_with_overlay(rules, content)
        # for rule in rules:
        #     _get_overlays(rule, content)
        # return rules

    class Bayfill:
        min_fields = 3

        @classmethod
        def parse(cls, line):
            match = re.match(
                r'Bayfill +(?P<name>\w+) +(?P<num_facies>\d+) +(?P<rule>\[.*\])', line
            ).groupdict()
            rule = json.loads(match['rule'].replace("'", '"'))
            polygons = cls.polygons(rule)
            return {
                'name': match['name'],
                'type': 'bayfill',
                'minFields': cls.min_fields,
                'polygons': polygons,
                'settings': cls.settings(rule, polygons),
                'fields': make_empty_fields(cls.min_fields),
            }

        names = (
            'Floodplain',
            'Subbay',
            'Wave influenced Bayfill',
            'Bayhead Delta',
            'Lagoon',
        )

        @classmethod
        def polygons(cls, rule):
            if len(rule) != len(cls.names):
                raise ValueError(
                    f'Incorrect number of polygons. Expected {len(cls.names)}, but got {len(rule)}.'
                )
            return [
                {
                    'name': cls.names[index],
                    'facies': {
                        'name': polygon[0],
                        'index': index,
                    },
                    'proportion': 1 / len(rule),
                }
                for index, polygon in enumerate(rule)
            ]

        @classmethod
        def settings(cls, rule, polygons):
            mapping = {
                polygon['facies']['name']: polygon['name'] for polygon in polygons
            }
            settings = []
            for polygon in rule:
                if len(polygon) == 3:
                    facies_name, slant_factor, value = polygon
                    settings.append(
                        {
                            'name': slant_factor,
                            'polygon': mapping[facies_name],
                            'slantFactor': {
                                'value': value,
                                'updatable': False,
                            },
                        }
                    )
            return settings

    class Combination:
        @staticmethod
        def parse(line: str):
            _mapping = {
                'NonCubicAndOverlay': 'NonCubicAndOverlay',
            }
            return re.match(
                r'(?P<type>\w+) +(?P<name>\w+) +(?P<rule>\w+) +(?P<overlay>\w+)', line
            ).groupdict()

    class Cubic:
        min_fields = 2

        @classmethod
        def parse(cls, line):
            # TODO: Implement
            content = re.match(
                r'(?P<type>\w+) +(?P<name>\w+) +(?P<num_polygons>\d+) +(?P<rule>\[.*\])',
                line,
            ).groupdict()
            polygons = cls.polygons(content)
            return {
                'name': content['name'],
                'type': 'cubic',
                'minFields': cls.min_fields,
                'polygons': polygons,
                'settings': cls.settings(content, polygons),
                'fields': make_empty_fields(cls.min_fields),
            }

        @staticmethod
        def polygons(content):
            items = get_array(content, 'rule')[1:]
            return [
                {'name': i + 1, 'facies': item[0], 'proportion': 1 / len(items)}
                for i, item in enumerate(items)
            ]

        @staticmethod
        def settings(content, polygons):
            cubic_specification = get_array(content, 'rule')

            settings = {'direction': cubic_specification[0], 'polygons': []}
            for polygon in cubic_specification[1:]:
                settings['polygons'].append(
                    {
                        'polygon': find_polygon_references(polygons, polygon),
                        'fraction': polygon[1],
                        'level': tuple(polygon[2:]),
                    }
                )
            return settings

    class NonCubic:
        min_fields = 2

        @classmethod
        def parse(cls, line: str):
            content = re.match(
                r'NonCubic (?P<name>\w+) (?P<num_groups>\d+) +(?P<settings>(\[.*\],?)+)',
                line,
            ).groupdict()
            polygons = cls.polygons(content)
            return {
                'name': content['name'],
                'type': 'non-cubic',
                'minFields': cls.min_fields,  # TODO calculate?
                'polygons': polygons,
                'settings': cls.settings(content, polygons),
                'fields': make_empty_fields(cls.min_fields),
            }

        @staticmethod
        def settings(content, polygons):
            settings = []
            for item in get_array(content, 'settings'):
                try:
                    updatable = item[3]
                except IndexError:
                    updatable = False
                settings.append(
                    {
                        'polygon': find_polygon_references(polygons, item),
                        'angle': {
                            'value': item[1],
                            'updatable': updatable,
                        },
                        'fraction': item[2],
                    }
                )
            counter = {}
            for setting in settings:
                polygon = setting['polygon']
                if isinstance(polygon, tuple):
                    if polygon not in counter:
                        counter[polygon] = 0
                    setting['polygon'] = polygon[counter[polygon]]
                    counter[polygon] += 1
            return settings

        @staticmethod
        def polygons(content):
            items = get_array(content, 'settings')
            return [
                {
                    # Polygons are 1 indexed
                    'order': i + 1,
                    'facies': item[0],
                    'proportion': 1 / len(items),
                }
                for i, item in enumerate(items)
            ]

    class Overlay:
        @classmethod
        def parse(cls, line: str):
            content = re.match(
                r'Overlay +(?P<name>\w+) +(?P<num_groups>\d+) +(?P<polygon_settings>[\d+ ]+) +(?P<settings>\[.+\])',
                line,
            ).groupdict()
            # Overlay A01 1  1 1 [[[['GRF03', 'F03', 1.0, 0.0]], ['F01']]]
            return {
                'name': content['name'],
                'type': 'overlay',
                'settings': cls.settings(content),
            }

        @staticmethod
        def settings(content):
            settings = get_array(content, 'settings')
            overlay = []
            for item in settings:
                overlay.append(
                    {
                        'polygons': [make_overlay_polygon(elem) for elem in item[0]],
                        'background': [{'name': name} for name in item[1]],
                    }
                )
            return overlay


def _make_indices(items):
    return {items[i]: i for i in range(len(items))}


def _sorted_list(items):
    items = list(items)
    items.sort()
    return items


def _indices(items):
    return _make_indices(_sorted_list(items))


def _get_all_fields_indices(rule):
    fields = {item['field']['name'] for item in rule['fields']}
    if 'overlay' in rule:
        for item in rule['overlay']:
            for polygon in item['polygons']:
                fields.add(polygon['field']['name'])
    return _indices(fields)


def _is_indexed(facies):
    return isinstance(facies, dict) and set(facies.keys()) == {'name', 'index'}


def _get_all_facies_indices(rule):
    if all(_is_indexed(polygon['facies']) for polygon in rule['polygons']):
        return {
            polygon['facies']['name']: polygon['facies']['index']
            for polygon in rule['polygons']
        }
    facies = {polygon['facies'] for polygon in rule['polygons']}
    if 'overlay' in rule:
        for item in rule['overlay']:
            for polygon in item['polygons']:
                facies.add(polygon['facies']['name'])
            for over_facies in item['background']:
                facies.add(over_facies['name'])
    return _indices(facies)


def parse(data: str):
    return Parser.parse(data)


def run(dump_site: Path):
    truncation_rules_path = (
        Path(__file__).parent / '..' / 'examples/truncation_settings.dat'
    )
    with open(truncation_rules_path, 'r', encoding='utf-8') as f:
        data = f.readlines()

    rules = {
        'types': [
            {'name': 'Bayfill', 'type': 'bayfill', 'order': 1},
            {'name': 'Non-Cubic', 'type': 'non-cubic', 'order': 2},
            {'name': 'Cubic', 'type': 'cubic', 'order': 3},
        ],
        'templates': parse(data),
    }
    with open(dump_site, 'w') as f:
        json.dump(rules, f)


if __name__ == '__main__':
    run(Path(sys.argv[1]))
