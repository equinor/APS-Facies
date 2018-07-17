# -*- coding: utf-8 -*-
from numpy import ndarray

from src.utils.constants.simple import VariogramType, Debug


def simGaussField(
        iseed: int,
        nx: int,
        ny: int,
        xsize: float,
        ysize: float,
        variogram_type: VariogramType,
        range_major_axis: float,
        range_minor_axis: float,
        azimuth_angle: float,
        power: float = None,
        debug_level: Debug = Debug.OFF
) -> ndarray: ...
