#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import re
from copy import deepcopy
from typing import List


def find_polygon_reference(polygons, item):
    for polygon in polygons:
        if polygon['facies'] == item[0]:
            return polygon['name']
    return -1


def make_empty_fields(num):
    return [
        {
          "channel": i,
          "field": {
            "name": f"GRF0{i}",
          }
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
        rules = cls._add_indices(rules)
        rules = cls._add_minimum_fields(rules)
        return rules

    @staticmethod
    def _parse(line: str):
        if not line:
            return None
        _type = line.split(' ')[0]
        parsers = {
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
            for polygon in rule['polygons']:
                facies_name = polygon['facies']
                polygon['facies'] = {
                    'name': facies_name,
                    'index': indices['facies'][facies_name]
                }
            for item in rule['fields']:
                field_name = item['field']['name']
                item['field']['index'] = indices['field'][field_name]
            if 'overlay' in rule:
                for item in rule['overlay']['items']:
                    for polygon in item['polygons']:
                        field_name = polygon['field']['name']
                        polygon['field']['index'] = indices['field'][field_name]

                        facies_name = polygon['facies']['name']
                        polygon['facies']['index'] = indices['facies'][facies_name]
                    for facies in item['over']:
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

    class Combination:
        @staticmethod
        def parse(line: str):
            _mapping = {
                'NonCubicAndOverlay': 'NonCubicAndOverlay',
            }
            content = re.match(r"(?P<type>\w+) +(?P<name>\w+) +(?P<rule>\w+) +(?P<overlay>\w+)", line).groupdict()
            # content['type'] = _mapping[content['type']]
            return content

    class Cubic:
        @staticmethod
        def parse(line):
            # TODO: Implement
            return None

    class NonCubic:
        min_fields = 2

        @classmethod
        def parse(cls, line: str):
            content = re.match(r"NonCubic (?P<name>\w+) (?P<num_groups>\d+) +(?P<settings>(\[.*\],?)+)", line).groupdict()
            polygons = cls.polygons(content)
            return {
                'name': content['name'],
                'type': 'non-cubic',
                'minFields': cls.min_fields,  # TODO calculate?
                'polygons': polygons,
                'settings': cls.settings(content, polygons),
                'fields': make_empty_fields(cls.min_fields)
            }

        @staticmethod
        def settings(content, polygons):
            settings = []
            for item in get_array(content, 'settings'):
                try:
                    updatable = item[3]
                except IndexError:
                    updatable = False
                settings.append({
                    'polygon': find_polygon_reference(polygons, item),
                    'angle': item[1],
                    'fraction': item[2],
                    'updatable': updatable,
                })
            return settings

        @staticmethod
        def polygons(content):
            polygons = []
            items = get_array(content, 'settings')
            for i, item in enumerate(items):
                polygons.append({
                    # Polygons are 1 indexed
                    'name': i + 1,
                    'facies': item[0],
                    'proportion': 1 / len(items)
                })
            return polygons

    class Overlay:
        @classmethod
        def parse(cls, line: str):
            content = re.match(r"Overlay +(?P<name>\w+) +(?P<num_groups>\d+) +(?P<polygon_settings>[\d+ ]+) +(?P<settings>\[.+\])", line).groupdict()
            # Overlay A01 1  1 1 [[[['GRF03', 'F03', 1.0, 0.0]], ['F01']]]
            return {
                'name': content['name'],
                'type': 'overlay',
                'settings': cls.settings(content)
            }

        @staticmethod
        def settings(content):
            settings = get_array(content, 'settings')
            overlay = {
                'use': True,
                'items': []
            }
            for item in settings:
                overlay['items'].append({
                    'polygons': [
                        make_overlay_polygon(elem) for elem in item[0]
                    ],
                    'over': [
                        {
                            'name': name
                        } for name in item[1]
                    ]
                })
            return overlay


def _make_indices(items):
    indices = {}
    for i in range(len(items)):
        indices[items[i]] = i
    return indices


def _sorted_list(items):
    items = list(items)
    items.sort()
    return items


def _indices(items):
    return _make_indices(_sorted_list(items))


def _get_all_fields_indices(rule):
    fields = set()
    for item in rule['fields']:
        fields.add(item['field']['name'])
    if 'overlay' in rule:
        for item in rule['overlay']['items']:
            for polygon in item['polygons']:
                fields.add(polygon['field']['name'])
    return _indices(fields)


def _get_all_facies_indices(rule):
    facies = set()
    for polygon in rule['polygons']:
        facies.add(polygon['facies'])
    if 'overlay' in rule:
        for item in rule['overlay']['items']:
            for polygon in item['polygons']:
                facies.add(polygon['facies']['name'])
            for over_facies in item['over']:
                facies.add(over_facies['name'])
    return _indices(facies)


def parse(data: str):
    return Parser.parse(data)


def run(data):
    rules = parse(data)
    print(json.dumps(rules))


if __name__ == '__main__':
    with open('examples/truncation_settings.dat', 'r') as f:
        data = f.readlines()
    run(data)

