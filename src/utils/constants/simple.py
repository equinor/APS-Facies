from enum import IntEnum, Enum


class Debug(IntEnum):
    OFF = 0
    ON = 1
    SOMEWHAT_VERBOSE = 1
    VERBOSE = 2
    VERY_VERBOSE = 3
    VERY_VERY_VERBOSE = 4


class VariogramType(Enum):
    SPHERICAL = 1
    EXPONENTIAL = 2
    GAUSSIAN = 3
    GENERAL_EXPONENTIAL = 4
    MATERN32 = 5
    MATERN52 = 6
    MATERN72 = 7
    CONSTANT = 8


class OperationalMode(Enum):
    EXPERIMENTAL = 0
    NORMAL = 1


class OriginType(Enum):
    """
    'RELATIVE' for relative coordinates
    'ABSOLUTE' for coordinates.
    """
    RELATIVE = 1
    ABSOLUTE = 2


class TrendType(Enum):
    NONE = 0
    LINEAR = 1
    ELLIPTIC = 2
    HYPERBOLIC = 3
    RMS_PARAM = 4
    ELLIPTIC_CONE = 5
