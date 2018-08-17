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
