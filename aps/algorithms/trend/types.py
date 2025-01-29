from typing import Union

from aps.algorithms.trend import (
    Trend3D_linear,
    Trend3D_hyperbolic,
    Trend3D_rms_param,
    Trend3D_elliptic,
    Trend3D_rms_map,
)

Trend = Union[
    Trend3D_linear,
    Trend3D_hyperbolic,
    Trend3D_rms_param,
    Trend3D_elliptic,
    Trend3D_rms_map,
]
