# -*- coding: utf-8 -*-
from enum import IntEnum, Enum, EnumMeta


class BaseMeta(EnumMeta):
    def __contains__(cls, member):
        return super().__contains__(member) or member in cls.__members__


class BaseEnum(Enum, metaclass=BaseMeta):
    pass


class Debug(IntEnum):
    READ = -1
    OFF = 0
    ON = 1
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
    RMS_TRENDMAP = 6


class TrendParameter(Enum):
    AZIMUTH = 'anisotropy_azimuth_angle'
    STACKING = 'stacking_angle'
    DIRECTION = 'stacking_direction'
    CURVATURE = 'curvature'
    MIGRATION = 'migration_angle'
    ORIGIN = 'origin'
    ORIGIN_TYPE = 'origin_type'
    RELATIVE_SIZE = 'relative_size_of_ellipse'
    RMS_PARAMETER = 'rms_parameter_name'
    RMS_TREND_MAP_NAME = 'rms_trendmap_name'
    RMS_TREND_MAP_ZONE = 'rms_trendmap_zone'


class CrossSectionType(Enum):
    IJ = 1
    IK = 2
    JK = 3


class Direction(IntEnum):
    # TODO: Ensure correct directions
    # Direction of stacking (prograding / retrograding)
    PROGRADING = 1
    RETROGRADING = -1


class GettableClass(type):
    def __getitem__(cls, item):
        return cls()[item]

    def __contains__(cls, item):
        return item in cls()


class Values(metaclass=GettableClass):
    MAIN_RANGE = NotImplemented
    PERPENDICULAR_RANGE = NotImplemented
    VERTICAL_RANGE = NotImplemented
    AZIMUTH_ANGLE_ANISOTROPY = NotImplemented
    DIP_ANGLE = NotImplemented
    POWER = NotImplemented
    RELATIVE_STD_DEV = NotImplemented
    # Trend
    AZIMUTH_ANGLE_DEPOSITIONAL = NotImplemented
    STACKING_ANGLE = NotImplemented
    CURVATURE = NotImplemented
    MIGRATION_ANGLE = NotImplemented
    RELATIVE_ELLIPSE_SIZE = NotImplemented
    # Tolerances
    MAX_ALLOWED_DEVIATION_BEFORE_ERROR = NotImplemented
    MAX_DEVIATION_BEFORE_ACTION = NotImplemented
    MAX_ALLOWED_FRACTION_OF_VALUES_OUTSIDE_TOLERANCE = NotImplemented

    @property
    def mapping(self):
        return {
            'main': self.MAIN_RANGE,
            'perpendicular': self.PERPENDICULAR_RANGE,
            'vertical': self.VERTICAL_RANGE,
            'azimuth': self.AZIMUTH_ANGLE_ANISOTROPY,
            'dip': self.DIP_ANGLE,
            'power': self.POWER,
            'relative_std_dev': self.RELATIVE_STD_DEV,
            # Trends
            'depositional_direction': self.AZIMUTH_ANGLE_DEPOSITIONAL,
            'stacking_angle': self.STACKING_ANGLE,
            'curvature': self.CURVATURE,
            'migration_angle': self.MIGRATION_ANGLE,
            'relative_size_of_ellipse': self.RELATIVE_ELLIPSE_SIZE,
            # Tolerances
            'max_allowed_deviation_before_error': self.MAX_ALLOWED_DEVIATION_BEFORE_ERROR,
            'max_deviation_before_action': self.MAX_DEVIATION_BEFORE_ACTION,
            'max_allowed_fraction_of_values_outside_tolerance': self.MAX_ALLOWED_FRACTION_OF_VALUES_OUTSIDE_TOLERANCE,
        }

    def __getitem__(self, item):
        return self.mapping[item]

    def __contains__(self, item):
        return item in self.mapping


class MinimumValues(Values):
    MAIN_RANGE = 0.0
    PERPENDICULAR_RANGE = 0.0
    VERTICAL_RANGE = 0.0
    AZIMUTH_ANGLE_ANISOTROPY = -720
    DIP_ANGLE = 0.0
    POWER = 1.0
    RELATIVE_STD_DEV = 0.0
    AZIMUTH_ANGLE_DEPOSITIONAL = -720
    STACKING_ANGLE = 0.0
    CURVATURE = 0.0
    MIGRATION_ANGLE = -90.0
    RELATIVE_ELLIPSE_SIZE = 0.0


class MaximumValues(Values):
    MAIN_RANGE = float('inf')
    PERPENDICULAR_RANGE = float('inf')
    VERTICAL_RANGE = float('inf')
    AZIMUTH_ANGLE_ANISOTROPY = 720
    DIP_ANGLE = 90.0
    POWER = 2.0
    RELATIVE_STD_DEV = float('inf')
    AZIMUTH_ANGLE_DEPOSITIONAL = 720
    STACKING_ANGLE = 90.0
    CURVATURE = float('inf')
    MIGRATION_ANGLE = 90.0
    RELATIVE_ELLIPSE_SIZE = float('inf')


class ModuloValues(Values):
    AZIMUTH_ANGLE_ANISOTROPY = 360.0
    AZIMUTH_ANGLE_DEPOSITIONAL = 360.0


class ProbabilityTolerances(Values):
    MAX_ALLOWED_DEVIATION_BEFORE_ERROR = 0.2
    MAX_DEVIATION_BEFORE_ACTION = 0.00005
    MAX_ALLOWED_FRACTION_OF_VALUES_OUTSIDE_TOLERANCE = 0.1


class GridModelConstants:
    ZONE_NAME = 'Zone'


class SimBoxThicknessConstants:
    DEFAULT_VALUE = 30


class Conform(Enum):
    Proportional = 'Proportional'
    TopConform = 'TopConform'
    BaseConform = 'BaseConform'
    Undefined = 'Undefined'


class TransformType(IntEnum):
    EMPIRIC = 0
    CUMNORM = 1


class FlipDirectionXtgeo:
    UPPER_LEFT_CORNER = -1
    LOWER_LEFT_CORNER = 1


class ExtrapolationMethod(Enum):
    ZERO = 'zero'
    MEAN = 'mean'
    EXTEND_LAYER_MEAN = 'extend_layer_mean'
    REPEAT_LAYER_MEAN = 'repeat_layer_mean'
    EXTEND = 'extend'
    REPEAT = 'repeat'


class ModelFileFormat(Enum):
    YML = 'yml'
    XML = 'xml'
    BOTH = 'both'
