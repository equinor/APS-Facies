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


class OperationalMode(Enum):
    EXPERIMENTAL = 0
    NORMAL = 1


class OriginType(Enum):
    """
    'RELATIVE' for relative to grid coordinates e.g. [0,0,0] for grid [x_min, x_max, simboxtop].
    'ABSOLUTE' for coordinates.
    """
    RELATIVE = 1
    ABSOLUTE = 2


class TrendType(Enum):
    NONE = 0
    ELLIPTIC = 1
    HYPERBOLIC = 2


def get_legal_values_of_enum(enum):
    if isinstance(enum, Enum) or isinstance(enum, IntEnum):
        return {v.value for v in enum.__members__.values()}
