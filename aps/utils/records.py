# -*- coding: utf-8 -*-
from collections import namedtuple

VariogramRecord = namedtuple(
    'VariogramRecord', [
        'Name',
        'Type',
        'MainRange',
        'PerpRange',
        'VertRange',
        'AzimuthAngle',
        'DipAngle',
        'Power',
        'MainRangeFMUUpdatable',
        'PerpRangeFMUUpdatable',
        'VertRangeFMUUpdatable',
        'AzimuthAngleFMUUpdatable',
        'DipAngleFMUUpdatable',
        'PowerFMUUpdatable'
    ]
)

SeedRecord = namedtuple(
    'SeedRecord', [
        'Name',
        'Seed'
    ]
)

TrendRecord = namedtuple(
    'TrendRecord', [
        'Name',
        'UseTrend',
        'Object',
        'RelStdev',
        'RelStdevFMU'
    ]
)

FaciesRecord = namedtuple(
    'FaciesRecord', [
        'Name',
        'Code'
    ]
)

FaciesProbabilityRecord = namedtuple(
    'FaciesProbabilityRecord', [
        'Name',
        'Probability'
    ]
)


class Probability:
    __slots__ = 'name', 'value'

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __iter__(self):
        return (self.name, self.value).__iter__()
