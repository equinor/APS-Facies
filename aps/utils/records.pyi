# -*- coding: utf-8 -*-
from typing import NamedTuple, Union, Optional

from aps.algorithms.trend import Trend3D
from aps.algorithms.APSGaussModel import GaussianFieldName
from aps.utils.constants.simple import VariogramType
from aps.utils.types import FaciesName, FaciesCode


class VariogramRecord(NamedTuple):
    Name: GaussianFieldName
    Type: Union[str, VariogramType]
    MainRange: int
    PerpRange: int
    VertRange: int
    AzimuthAngle: float
    DipAngle: float
    Power: float
    MainRangeFMUUpdatable: bool
    PerpRangeFMUUpdatable: bool
    VertRangeFMUUpdatable: bool
    AzimuthAngleFMUUpdatable: bool
    DipAngleFMUUpdatable: bool
    PowerFMUUpdatable: bool

class TrendRecord(NamedTuple):
     Name: GaussianFieldName
     UseTrend: bool
     Object: Optional[Trend3D]
     RelStdev: float
     RelStdevFMU: bool


class SeedRecord(NamedTuple):
    Name: GaussianFieldName
    Seed: int


class FaciesRecord(NamedTuple):
    Name: FaciesName
    Code: FaciesCode


class FaciesProbabilityRecord(NamedTuple):
    Name: str
    Probability: Union[str, float]


class Probability:
    __slots__ = 'name', 'value'
    def __init__(self, name: str, value): ...
    def __iter__(self): ...
