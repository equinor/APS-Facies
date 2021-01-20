from typing import Union

from aps.algorithms.truncation_rules import Trunc3D_bayfill, Trunc2D_Cubic, Trunc2D_Angle

TruncationRule = Union[Trunc3D_bayfill, Trunc2D_Cubic, Trunc2D_Angle]
