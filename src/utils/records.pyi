# -*- coding: utf-8 -*-
from typing import NamedTuple, Union, Optional

from src.algorithms import Trend3D
from src.algorithms.APSGaussModel import GaussianFieldName
from src.utils.constants.simple import VariogramType


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
