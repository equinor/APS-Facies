#!/bin/env python
# -*- coding: utf-8 -*-
from xml.etree.ElementTree import Element

import numpy as np
from collections import OrderedDict

from src.algorithms.Trend3D import (
    Trend3D_elliptic, Trend3D_elliptic_cone, Trend3D_hyperbolic, Trend3D_linear, Trend3D_rms_param,
)
from src.utils.checks import isVariogramTypeOK
from src.utils.constants.simple import Debug, VariogramType, CrossSectionType
from src.utils.simGauss2D_nrlib import simGaussField
from src.utils.xmlUtils import (
    getFloatCommand, getIntCommand, getKeyword, isFMUUpdatable,
    createFMUvariableNameForResidual, createFMUvariableNameForTrend
)

# Dictionaries of legal value ranges for gauss field parameters
from src.utils.records import VariogramRecord, SeedRecord, TrendRecord

_minimum_value = {
    'main': 0.0,
    'perpendicular': 0.0,
    'vertical': 0.0,
    'azimuth': 0.0,
    'dip': 0.0,
    'power': 1.0,
    'relative_std_dev': 0.0,
}

_maximum_value = {
    'azimuth': 360.0,
    'dip': 90.0,
    'power': 2.0,
}


class GaussianFieldSimulation:
    __slots__ = '_name', '_field', '_cross_section', '_grid_azimuth_angle', '_grid_size', '_simulation_box_size'

    def __init__(self, name, field, cross_section, grid_azimuth_angle, grid_size, simulation_box_size):
        self._name = name
        self._field = field
        self._cross_section = cross_section
        self._grid_azimuth_angle = grid_azimuth_angle
        self._grid_size = grid_size
        self._simulation_box_size = simulation_box_size

    @property
    def name(self):
        return self._name

    @property
    def field(self):
        return self._field

    @property
    def cross_section(self):
        return self._cross_section

    @property
    def grid_azimuth_angle(self):
        return self._grid_azimuth_angle

    @property
    def grid_size(self):
        return self._grid_size

    @property
    def simulation_box_size(self):
        return self._simulation_box_size


class GaussianField:
    def __init__(self, name, variogram=None, trend=None, seed=0):
        # TODO: Make sane default values for variogram and trend
        if trend is None:
            trend = Trend(name, use_trend=False)
        self._name = name
        self._variogram = variogram
        self._trend = trend
        self._seed = seed

    @property
    def seed(self):
        return self._seed

    @seed.setter
    def seed(self, value):
        # TODO: This probably should not be done
        self._seed = value

    @property
    def name(self):
        return self._name

    @property
    def variogram(self):
        return self._variogram

    @variogram.setter
    def variogram(self, value):
        # TODO: Verify
        self._variogram = value

    @property
    def trend(self):
        return self._trend

    @trend.setter
    def trend(self, value):
        # TODO: Verify
        self._trend = value

    def __getitem__(self, item):
        try:
            return getattr(self, item)
        except AttributeError:
            val = self.variogram[item]
            if val is not None:
                return val
            else:
                try:
                    return getattr(self.trend, item)
                except AttributeError:
                    raise AttributeError("The Gaussian Field ('{}') has no attribute {}".format(self.name, item))

    def _simulate(self, cross_section, grid_azimuth_angle, grid_size, simulation_box_size, debug_level=Debug.OFF):
        grid_dimensions, sizes, projection, = _get_projection_parameters(cross_section.type, grid_size, simulation_box_size)
        # Find data for specified Gauss field name
        seed_value = self.seed
        variogram_type = self.variogram.type
        power = self.variogram.power.value
        if debug_level >= Debug.VERY_VERBOSE:
            print('')
            print('Debug output: Within simGaussFieldWithTrendAndTransform')
            print('Debug output: Simulate gauss field: ' + self.name)
            print('Debug output: VariogramType: ' + str(variogram_type))
            print('Debug output: Azimuth angle for Main range direction: ' + str(self.variogram.angles.azimuth))
            print('Debug output: Azimuth angle for grid: ' + str(grid_azimuth_angle))
            print('Debug output: Dip angle for Main range direction: ' + str(self.variogram.angles.dip))

            if variogram_type == VariogramType.GENERAL_EXPONENTIAL:
                print('Debug output: Power    : ' + str(power))

            print('Debug output: Seed value: ' + str(seed_value))
        # Calculate 2D projection of the correlation ellipsoid
        angle1, range1, angle2, range2 = self.variogram.calc_2d_variogram_from_3d_variogram(grid_azimuth_angle, projection, debug_level)
        azimuth_variogram = angle1
        if debug_level >= Debug.VERY_VERBOSE:
            print(
                '\nDebug output: Range1 in projection: {projection} : {range1}\n'
                'Debug output: Range2 in projection: {projection} : {range2}\n'
                'Debug output: Angle from vertical axis for Range1 direction: {angle1}\n'
                'Debug output: Angle from vertical axis for Range2 direction: {angle2}\n'
                'Debug output: (gridDim1, gridDim2) = ({gridDim1},{gridDim2})\n'
                'Debug output: (Size1, Size2) = ({size1},  {size2})'
                ''.format(
                    projection=projection,
                    range1=range1, range2=range2,
                    angle1=angle1, angle2=angle2,
                    gridDim1=grid_dimensions[0], gridDim2=grid_dimensions[1],
                    size1=sizes[0], size2=sizes[1]
                )
            )
        residual_field = simGaussField(
            seed_value, grid_dimensions[0], grid_dimensions[1], sizes[0], sizes[1], variogram_type,
            range1, range2, azimuth_variogram, power, debug_level
        )
        # Calculate trend
        _, use_trend, trend_model, relative_std_dev, _ = self.trend.as_list()
        if use_trend:
            if debug_level >= Debug.VERBOSE:
                print('    - Use Trend: {}'.format(trend_model.type.name))
            min_max_difference, average_trend, trend_field = trend_model.createTrendFor2DProjection(
                simulation_box_size, grid_azimuth_angle, grid_size, cross_section.type, cross_section.relative_position
            )
            gauss_field_with_trend = _add_trend(
                residual_field, trend_field, relative_std_dev, min_max_difference, average_trend, debug_level
            )
        else:
            gauss_field_with_trend = residual_field
        trans_field = _transform_empiric_distribution_to_uniform(gauss_field_with_trend, debug_level)
        return trans_field

    def simulate(self, cross_section, grid_azimuth_angle, grid_size, simulation_box_size, debug_level=Debug.OFF):
        return GaussianFieldSimulation(
            name=self.name,
            field=self._simulate(cross_section, grid_azimuth_angle, grid_size, simulation_box_size, debug_level),
            cross_section=cross_section,
            grid_azimuth_angle=grid_azimuth_angle,
            grid_size=grid_size,
            simulation_box_size=simulation_box_size,
        )


def _make_ranged_property(name, error_template, minimum=None, maximum=None, additional_validator=None, show_given_value=True):
    if additional_validator is None:
        def additional_validator(self, value):
            return True
    if minimum is None:
        minimum = _minimum_value[name]
    if maximum is None:
        maximum = _maximum_value[name]

    class Property:
        __slots__ = '_' + name

        def __init__(self):
            setattr(self, '_' + name, None)

        def get(self):
            return getattr(self, '_' + name)

        def set(self, value):
            if not isinstance(value, FmuProperty):
                try:
                    updatable = getattr(self, '_' + name).updatable
                except AttributeError:
                    updatable = False
                value = FmuProperty(value, updatable)
            if minimum <= value.value <= maximum and additional_validator(self, value):
                setattr(self, '_' + name, value)
            else:
                template = error_template
                if show_given_value:
                    template += '({value} was given)'
                raise ValueError(
                    template.format(name=name, min=minimum, max=maximum, value=value.value)
                )
    return property(fget=Property.get, fset=Property.set)


def _make_simple_property(name, check, error_message):
    class Property:
        __slots__ = '_' + name

        def __init__(self):
            setattr(self, '_' + name, None)

        def get(self):
            return getattr(self, '_' + name)

        def set(self, value):
            if check(self, value):
                setattr(self, '_' + name, value)
            else:
                raise ValueError(error_message)

    return property(fget=Property.get, fset=Property.set)


def _make_trend(name):
    def is_model_and_rel_std_dev_set(self, value):
        if value:
            return self.model is not None and self.relative_std_dev is not None
        return True
    return _make_simple_property(name, is_model_and_rel_std_dev_set, 'While trend is used, a trend model MUST be given, and the relative std.dev. must be given')


def _make_angle(name):
    return _make_bounded_property(name, _minimum_value[name], _maximum_value[name], 'The {name} angle MUST be between {min}°, and {max}°.')


def _make_bounded_property(name, minimum, maximum, error_template, additional_validator=None):
    return _make_ranged_property(name, error_template, minimum, maximum, additional_validator)


def _make_lower_bounded_property(name, additional_validator=None):
    return _make_ranged_property(name, '{name} MUST be greater than (or equal to) 0', _minimum_value[name], float('inf'), additional_validator)


class FmuProperty:
    __slots__ = 'value', 'updatable'

    def __init__(self, value, updatable=False):
        # TODO: Ensure value is number, and updatable is boolean
        self.value = value
        self.updatable = updatable

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return '(' + str(self.value) + ', ' + str(self.updatable) + ')'


class CrossSection:
    __slots__ = '_type', '_relative_position'

    def __init__(self, type, relative_position):
        self._type = None
        self._relative_position = None

        self.type = type
        self.relative_position = relative_position

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        if value not in CrossSectionType:
            value = CrossSectionType[value]
        self._type = value

    @property
    def relative_position(self):
        return self._relative_position

    @relative_position.setter
    def relative_position(self, value):
        if not (0 <= value <= 1):
            raise ValueError(
                'The specified value must be in the interval [0.0, 1.0]'
            )
        self._relative_position = value


class Ranges:
    __slots__ = '_main', '_perpendicular', '_vertical'

    def __init__(self, main, perpendicular, vertical):
        self.main = main
        self.perpendicular = perpendicular
        self.vertical = vertical

    main = _make_lower_bounded_property('main')
    perpendicular = _make_lower_bounded_property('perpendicular')
    vertical = _make_lower_bounded_property('vertical')

    @property
    def range1(self):
        return self.main

    @range1.setter
    def range1(self, value):
        self.main = value

    @property
    def range2(self):
        return self.perpendicular

    @range2.setter
    def range2(self, value):
        self.perpendicular = value

    @property
    def range3(self):
        return self.vertical

    @range3.setter
    def range3(self, value):
        self.vertical = value


class Angles:
    __slots__ = '_azimuth', '_dip'

    def __init__(self, azimuth, dip):
        self.azimuth = azimuth
        self.dip = dip

    azimuth = _make_angle('azimuth')
    dip = _make_angle('dip')


class Trend:
    # __slots__ = '_name', '_use_trend', '_model', '_relative_std_dev'

    def __init__(self, name, use_trend=False, model=None, relative_std_dev=None):
        if relative_std_dev is None:
            relative_std_dev = FmuProperty(1.0, False)
        self._name = name
        self._model = model
        self.relative_std_dev = relative_std_dev
        self.use_trend = use_trend

    relative_srd_dev = _make_lower_bounded_property('relative_std_dev')
    use_trend = _make_trend('use_trend')

    @property
    def name(self):
        return self._name

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, value):
        if value is None:
            self.use_trend = False
        self._model = value

    @classmethod
    def from_definition(cls, definition):
        definition = TrendRecord._make(definition)
        return cls(
            name=definition.Name,
            use_trend=definition.UseTrend,
            model=definition.Object,
            relative_std_dev=FmuProperty(definition.RelStdev, definition.RelStdevFMU),
        )

    def as_list(self):
        return [
            self.name,
            self.use_trend,
            self.model,
            self.relative_std_dev.value,
            self.relative_std_dev.updatable,
        ]


class Variogram:
    def __init__(self, name, type, ranges, angles, power=None):
        if power is None:
            power = FmuProperty(_minimum_value['power'], False)
        self.name = name
        self._type = type
        self.ranges = ranges
        self.angles = angles
        self.power = power

    power = _make_ranged_property('power', 'power must be between {min}, and {max}')

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        if not isVariogramTypeOK(value):
            raise ValueError('The given variogram is not valid ({})'.format(value))
        elif (
                value == VariogramType.GENERAL_EXPONENTIAL
                and not (_minimum_value['power'] <= self.power.value <= _maximum_value['power'])
        ):
            raise ValueError("While using 'GENERAL_EXPONENTIAL' variogram, 'power' MUST be in [1, 2]")
        self._type = value

    @classmethod
    def from_definition(cls, definition):
        definition = VariogramRecord._make(definition)
        if isinstance(definition.Type, str):
            variogram_type = VariogramType[definition.Type]
        else:
            variogram_type = definition.Type
        return cls(
            name=definition.Name,
            type=variogram_type,
            ranges=Ranges(
                main=FmuProperty(definition.MainRange, definition.MainRangeFMUUpdatable),
                perpendicular=FmuProperty(definition.PerpRange, definition.PerpRangeFMUUpdatable),
                vertical=FmuProperty(definition.VertRange, definition.VertRangeFMUUpdatable),
            ),
            angles=Angles(
                azimuth=FmuProperty(definition.AzimuthAngle, definition.AzimuthAngleFMUUpdatable),
                dip=FmuProperty(definition.DipAngle, definition.DipAngleFMUUpdatable),
            ),
            power=FmuProperty(definition.Power, definition.PowerFMUUpdatable),
        )

    @staticmethod
    def __mapping__():
        return {
            'Name': 0,
            'Type': 1,
            'MainRange': 2,
            'PerpRange': 3,
            'VertRange': 4,
            'AzimuthAngle': 5,
            'DipAngle': 6,
            'Power': 7,
            'MainRangeFMUUpdatable': 8,
            'PerpRangeFMUUpdatable': 9,
            'VertRangeFMUUpdatable': 10,
            'AzimuthAngleFMUUpdatable': 11,
            'DipAngleFMUUpdatable': 12,
            'PowerFMUUpdatable': 13,
        }

    def __getitem__(self, item):
        if isinstance(item, str) and item in self.__mapping__():
            return self.as_list()[self.__mapping__()[item]]
        elif isinstance(item, int) and 0 <= item < len(self.as_list()):
            return self.as_list()[item]
        elif hasattr(self, item):
            return getattr(self, item)
        elif hasattr(self.ranges, item):
            return getattr(self.ranges, item)
        elif hasattr(self.angles, item):
            return getattr(self.angles, item)
        else:
            return None

    def as_list(self):
        return [
            self.name,
            self.type.name,
            self.ranges.main.value,
            self.ranges.perpendicular.value,
            self.ranges.vertical.value,
            self.angles.azimuth.value,
            self.angles.dip.value,
            self.power.value,
            self.ranges.main.updatable,
            self.ranges.perpendicular.updatable,
            self.ranges.vertical.updatable,
            self.angles.azimuth.updatable,
            self.angles.dip.updatable,
            self.power.updatable,
        ]

    def calc_2d_variogram_from_3d_variogram(self, grid_azimuth_angle, projection, debug_level=Debug.OFF):
        """
         Variogram ellipsoid in 3D is defined by a symmetric 3x3 matrix M such that
         transpose(V)*M * V = 1 where transpose(V) = [x,y,z]. The principal directions are found
         by diagonalization of the matrix. The diagonal matrix has the diagonal matrix elements
         D11 = 1/(B*B)  D22 = 1/(A*A)  D33 = 1/(C*C) where A,B,C are the half axes in the three
         principal directions. For variogram ellipsoid the MainRange = A, PerpRange = B, VertRange = C.
         To define the orientation, first define a ellipsoid oriented with
         MainRange in y direction, PerpRange in x direction and VertRange in z direction.
         Then rotate this ellipsoid first around x axis with angle defined as dipAngle in clockwise direction.
         The dip angle is the angle between the y axis and the new rotated y' axis along the main
         principal direction of the ellipsoid.
         Then rotate the the ellipsoid an angle around the z axis. This is the azimuthAngle. The final orientation
         is then found and the coordinate system defined by the principal directions for the ellipsoid
         are (x'',y'',z'') in which the M matrix is diagonal.
         We now define the ellipsoid in this coordinate system with the diagonal M matrix.
         The goal is now to transform the coordinate from this (x',y',z') system back to (x,y,z) and the the matrix M
         in this coordinate system. So the transformation will be the opposite of what was necessary to
         rotate the ellipsoid from standard position with principal main axis in y direction and the second
         pprincipal direction in x direction and the third in z direction.
         Note also that the coordinate system (x,y,z) is left handed and z axis is pointing
         downward compared to a right handed coordinate system.

         After calculating M in (x,y,z) coordinates, a project is taken into either x,y,or z plane to get the correlation
         ellipse in 2D cross section. This correlation ellipse is used when simulating 2D gaussian fields in cross sections.
         """
        func_name = self.calc_2d_variogram_from_3d_variogram.__name__
        if debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: Function: {}'.format(func_name))
        ry = self.ranges.main.value
        rx = self.ranges.perpendicular.value
        rz = self.ranges.vertical.value

        # Azimuth relative to global x,y,z coordinates
        azimuth = self.angles.azimuth.value

        # Azimuth relative to local coordinate system defined by the orientation of the grid (simulation box)
        azimuth = azimuth - grid_azimuth_angle

        # Dip angle relative to local simulation box
        dip = self.angles.dip.value

        # The transformations R_dip and R_azimuth defined below rotate the ellipsoid FROM standard orientation
        # in (x,y,z) TO the final orientation defined by azimuth and dip angles. But we need the inverse transformation
        # which means that the angles have opposite sign and the rotation matrixes come in opposite order to transform M matrix
        # FROM (x',y',z') t0 (x,y,z).
        azimuth = -azimuth * np.pi / 180.0
        dip = -dip * np.pi / 180.0

        cos_theta = np.cos(azimuth)
        sin_theta = np.sin(azimuth)
        cos_dip = np.cos(dip)
        sin_dip = np.sin(dip)

        # define R_dip matrix
        # R_dip*V will rotate the vector V by the angle dip around the x-axis.
        # The vector [0,1,0] (unit vector in y direction)  will get a positive z component if dip angle is positive
        # (between 0 and 90 degrees).
        # Note that z axis is down and that the (x,y,z) coordinate system is left-handed.
        R_dip = np.array([
            [1.0, 0.0, 0.0],
            [0.0, cos_dip, -sin_dip],
            [0.0, sin_dip, cos_dip]
        ])

        # define R_azimuth matrix
        # R_azimuth*V will rotate the vector V by the angle azimuth around the z axis.
        # The vector [0,1,0] (unit vector in y direction) will get positive x component if azimuth angle
        # is positive (between 0 and 180 degrees)
        R_azimuth = np.array([
            [cos_theta, sin_theta, 0.0],
            [-sin_theta, cos_theta, 0.0],
            [0.0, 0.0, 1.0]
        ])

        # The combination R = R_azimuth * R_dip will
        # rotate the vector V first by a dip angle around x axis and then by an azimuth angle around z axis

        # calculate R matrix to get from (x',y',z') to (x,y,z)
        R = R_dip.dot(R_azimuth)

        # calculate M matrix in principal coordinates (x',y',z')
        M_diag = np.array([
            [1.0 / (rx * rx), 0.0, 0.0],
            [0.0, 1.0 / (ry * ry), 0.0],
            [0.0, 0.0, 1.0 / (rz * rz)]
        ])

        # The M matrix in (x,y,z) coordinates is given by M = transpose(R) * M_diag * R
        tmp = M_diag.dot(R)
        Rt = np.transpose(R)
        M = Rt.dot(tmp)
        if debug_level >= Debug.VERY_VERY_VERBOSE:
            print('Debug output: M:')
            print(M)
            print('')

        # Let U be the 2x2 matrix in the projection (where row and column corresponding to
        # the coordinate that is set to 0 is removed

        # Calculate the projection of the ellipsoid onto the coordinate planes
        if projection == 'xy':
            U = np.array([
                [M[0, 0], M[0, 1]],
                [M[0, 1], M[1, 1]]
            ])
        elif projection == 'xz':
            U = np.array([
                [M[0, 0], M[0, 2]],
                [M[0, 2], M[2, 2]]
            ])
        elif projection == 'yz':
            U = np.array([
                [M[1, 1], M[1, 2]],
                [M[1, 2], M[2, 2]]
            ])
        else:
            raise ValueError('Unknown projection for calculation of 2D variogram ellipse from 3D variogram ellipsoid')
        # Calculate half-axes and rotation of the ellipse that results from the 2D projection of the 3D ellipsoid.
        # This is done by calculating eigenvalues and eigenvectors of the 2D version of the M matrix.
        # angles are azimuth angles (Measured from 2nd axis clockwise)
        angle1, range1, angle2, range2 = _calculate_projection(U, debug_level=debug_level)

        return angle1, range1, angle2, range2


class APSGaussModel:
    """
    Description: This class contain model parameter specification of the gaussian fields to be simulated for a zone.
    The class contain both variogram data and trend data. Both functions to read the parameters from and XML tree
    for the model file and functions to create an object from an initialization function exist.

    Constructor:
    def __init__(self,ET_Tree_zone=None, mainFaciesTable= None,modelFileName = None,
                 debug_level=Debug.OFF,zoneNumber=0,simBoxThickness=0)

    Properties
      used_gaussian_field_names

    Public functions:
    def initialize(self,inputZoneNumber,mainFaciesTable,gaussModelList,trendModelList,
                   simBoxThickness,previewSeed,debug_level=Debug.OFF)
    def getVariogramType(self,gaussFieldName)
    def getVariogramTypeNumber(self,gaussFieldName)
    def getMainRange(self,gaussFieldName)
    def getPerpRange(self,gaussFieldName)
    def getVertRange(self,gaussFieldName)
    def getAzimuthAngle(self,gaussFieldName)
    def getDipAngle(self,gaussFieldName)
    def getPower(self,gaussFieldName)
    def getTrendModel(self,gfName)
    def getTrendModelObject(self,gfName)
    def setZoneNumber(self,zoneNumber)
    def setVariogramType(self,gaussFieldName,variogramType)
    def setRange1(self,gaussFieldName,range1)
    def setRange2(self,gaussFieldName,range2)
    def setRange3(self,gaussFieldName,range3)
    def setAzimuthAngle(self,gaussFieldName)
    def setDipAngle(self,gaussFieldName)
    def setPower(self,gaussFieldName,power)
    def setSeedForPreviewSimulation(self,gfName,seed)
    def updateGaussFieldParam(self,gfName,variogramType,range1,range2,range3,azimuth,dip,power,
                              useTrend=0,relStdDev=0.0,trendModelObj=None)
    def updateGaussFieldVariogramParam(self,gfName,variogramType,range1,range2,range3,azimuth,dip,power)
    def removeGaussFieldParam(self,gfName)
    def updateGaussFieldTrendParam(self,gfName,useTrend,trendModelObj,relStdDev)
    def XMLAddElement(self,parent)
    def simGaussFieldWithTrendAndTransform(
        self, nGaussFields, (gridDimNx, gridDimNy, gridDimNz),
        (gridXSize, gridYSize, gridZSize), gridAzimuthAngle, previewCrossSection
    )

    Private functions:
    def __interpretXMLTree(ET_Tree_zone)
    """

    def __init__(self, ET_Tree_zone=None, mainFaciesTable=None, modelFileName=None,
                 debug_level=Debug.OFF, zoneNumber=0, simBoxThickness=0):
        """
        Description: Can create empty object or object with data read from xml tree representing the model file.
        """

        # Dictionary give xml keyword for each variable
        self.__xml_keyword = {
            'main': 'MainRange',
            'perpendicular': 'PerpRange',
            'vertical': 'VertRange',
            'azimuth': 'AzimuthAngle',
            'dip': 'DipAngle',
            'power': 'Power',
            'relative_std_dev': 'RelStdDev',
        }

        self._gaussian_models = OrderedDict()

        self.__class_name = self.__class__.__name__
        self.__debug_level = Debug.OFF
        self.__main_facies_table = None
        self.__sim_box_thickness = 0
        self.zone_number = 0
        self.__model_file_name = None

        if ET_Tree_zone is not None:
            # Get data from xml tree
            if debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: Call init ' + self.__class_name + ' and read from xml file')

            assert mainFaciesTable
            assert zoneNumber
            assert simBoxThickness
            assert modelFileName

            self.__main_facies_table = mainFaciesTable
            self.__zone_number = zoneNumber
            self.__sim_box_thickness = simBoxThickness
            self.__model_file_name = modelFileName
            self.__debug_level = debug_level

            self.__interpretXMLTree(ET_Tree_zone)

    def __interpretXMLTree(self, ET_Tree_zone):
        """
        Description: Read Gauss field models for current zone.
        Read trend models for the same gauss fields and start seed for 2D preview simulations.
        """
        zone_number = ET_Tree_zone.get("number")
        region_number = ET_Tree_zone.get("regionNumber")
        for gf in ET_Tree_zone.findall('GaussField'):
            gf_name = gf.get('name')
            if self.debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: Gauss field name: {}'.format(gf_name))

            # Read variogram for current GF
            variogram, variogram_type = self.get_variogram(gf, gf_name)

            range1, range1_fmu_updatable = self._get_value_from_xml('main', variogram)
            range2, range2_fmu_updatable = self._get_value_from_xml('perpendicular', variogram)
            range3, range3_fmu_updatable = self._get_value_from_xml('vertical', variogram)

            azimuth, azimuth_fmu_updatable = self._get_value_from_xml('azimuth', variogram)
            dip, dip_fmu_updatable = self._get_value_from_xml('dip', variogram)

            power = 1.0
            if variogram_type == VariogramType.GENERAL_EXPONENTIAL:
                power, _ = self._get_value_from_xml('power', variogram)
            power_fmu_updatable = isFMUUpdatable(variogram, 'Power')

            # Read trend model for current GF
            trend_xml_obj = gf.find('Trend')
            relative_std_dev = 0.0
            rel_std_dev_fmu_updatable = False
            if trend_xml_obj is not None:
                if self.debug_level >= Debug.VERY_VERBOSE:
                    print('Debug output: Read trend')
                use_trend = True

                if self.__sim_box_thickness <= 0.0:
                    raise ValueError(
                        'In model file {0} in keyword Trend for gauss field name: {1}\n'
                        'The use of trend functions requires that simulation box thickness is specified.\n'
                        ''.format(self.__model_file_name, gf_name, self.__class_name)
                    )

                # checking first child of element Trend to determine the type of Trend
                trend_name = trend_xml_obj[0]
                if trend_name is None:
                    raise ValueError(
                        'In model file {0} in keyword Trend for gauss field name: {1}\n'
                        'No actual Trend is specified.\n'
                        ''.format(self.__model_file_name, gf_name, self.__class_name)
                    )
                common_params = {
                    'zone_number': zone_number,
                    'region_number': region_number,
                    'gf_name': gf_name,
                    'modelFileName': self.__model_file_name,
                    'debug_level': self.debug_level
                }

                trend_models = {
                    'Linear3D': Trend3D_linear,
                    'Elliptic3D': Trend3D_elliptic,
                    'Hyperbolic3D': Trend3D_hyperbolic,
                    'RMSParameter': Trend3D_rms_param,
                    'EllipticCone3D': Trend3D_elliptic_cone,
                }
                try:
                    trend_model = trend_models[trend_name.tag](trend_xml_obj.find(trend_name.tag), **common_params)
                except KeyError:
                    raise NameError(
                        'Error in {className}\n'
                        'Error: Specified name of trend function {trendName} is not implemented.'
                        ''.format(className=self.__class_name, trendName=trend_name.tag)
                    )
            else:
                if self.debug_level >= Debug.VERY_VERBOSE:
                    print('Debug output: No trend is specified')
                use_trend = False
                trend_model = None
                relative_std_dev = 0.0
                rel_std_dev_fmu_updatable = False

            # Read relative std.dev.
            if use_trend:
                relative_std_dev, rel_std_dev_fmu_updatable = self._get_value_from_xml('relative_std_dev', gf)

            # Read preview seed for current GF
            seed = getIntCommand(gf, 'SeedForPreview', 'GaussField', modelFile=self.__model_file_name)

            # Add gauss field parameters to data structure
            self.updateGaussFieldParam(
                gf_name, variogram_type, range1, range2, range3, azimuth,
                dip, power, range1_fmu_updatable, range2_fmu_updatable, range3_fmu_updatable, azimuth_fmu_updatable,
                dip_fmu_updatable, power_fmu_updatable, use_trend, relative_std_dev, rel_std_dev_fmu_updatable, trend_model
            )
            # Set preview simulation start seed for gauss field
            self.setSeedForPreviewSimulation(gf_name, seed)

        # End loop over gauss fields for current zone model

        if self._gaussian_models is None:
            raise NameError(
                'Error when reading model file: {modelName}\n'
                'Error: Missing keyword GaussField under '
                'keyword Zone'
                ''.format(modelName=self.__model_file_name)
            )

        if self.debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: Gauss field variogram parameter for current zone model:')
            print([repr(grf.variogram) for grf in self._gaussian_models.values()])

            print('Debug output:Gauss field trend parameter for current zone model:')
            print([repr(grf.trend) for grf in self._gaussian_models.values()])

            print('Debug output: Gauss field preview seed for current zone model:')
            print([(name, grf.seed) for name, grf in self._gaussian_models.items()])

    def _get_value_from_xml(self, property_name, xml_tree):
        kwargs = {'parentKeyword': 'Vario', 'modelFile': self.__model_file_name}
        if property_name in _maximum_value:
            kwargs['maxValue'] = _maximum_value[property_name]
        if property_name in _minimum_value:
            kwargs['minValue'] = _minimum_value[property_name]

        keyword = self.__xml_keyword[property_name]
        value = getFloatCommand(xml_tree, keyword, **kwargs)
        fmu_updatable = isFMUUpdatable(xml_tree, keyword)
        return value, fmu_updatable

    def get_variogram(self, gf, gf_name):
        variogram = getKeyword(gf, 'Vario', 'GaussField', modelFile=self.__model_file_name)
        variogram_type = self.get_variogram_type(variogram)
        if not isVariogramTypeOK(variogram_type):
            raise ValueError(
                'In model file {0} in zone number: {1} in command Vario for gauss field {2}.\n'
                'Specified variogram type is not defined.'
                ''.format(self.__model_file_name, self.zone_number, gf_name)
            )
        return variogram, variogram_type

    @staticmethod
    def get_variogram_type(variogram) -> VariogramType:
        if isinstance(variogram, str):
            name = variogram
        elif isinstance(variogram, Element):
            name = variogram.get('name')
        elif isinstance(variogram, VariogramType):
            return variogram
        else:
            raise ValueError('Unknown type: {}'.format(str(variogram)))
        name = name.upper()
        try:
            return VariogramType[name]
        except KeyError:
            raise ValueError('Error: Unknown variogram type {}'.format(name))

    def initialize(
            self, zone_number, main_facies_table, gauss_model_list, trend_model_list,
            sim_box_thickness, preview_seed_list, debug_level=Debug.OFF):

        if debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: Call the initialize function in ' + self.__class_name)

        self.zone_number = zone_number
        self.__debug_level = debug_level
        self.__sim_box_thickness = sim_box_thickness
        self.__main_facies_table = main_facies_table

        # gauss_model_list  = list of objects of the form: [gfName,type,range1,range2,range3,azimuth,dip,power]
        # trend_model_list  = list of objects of the form: [gfName,useTrend,trendModelObj,relStdDev, relStdDevFMU]
        # preview_seed_list = list of objects of the form: [gfName,seedValue]
        assert len(trend_model_list) == len(gauss_model_list)
        for i in range(len(gauss_model_list)):
            try:
                variogram = VariogramRecord._make(gauss_model_list[i])
            except TypeError:
                raise ValueError('Programming error: Input list items in gauss_model_list is not of correct length')
            trend = TrendRecord._make(trend_model_list[i])
            seed = SeedRecord._make(preview_seed_list[i])
            assert variogram.Name == trend.Name
            assert variogram.Name == seed.Name

            self._gaussian_models[variogram.Name] = GaussianField(
                name=variogram.Name,
                # Set variogram parameters for this gauss field
                variogram=Variogram.from_definition(variogram),
                # Set trend model parameters for this gauss field
                trend=Trend.from_definition(trend),
                # Set preview simulation start seed for gauss field
                seed=seed.Seed,
            )

    @property
    def num_gaussian_fields(self):
        return len(self._gaussian_models)

    @property
    def zone_number(self):
        return self.__zone_number

    @zone_number.setter
    def zone_number(self, value):
        self.__zone_number = value

    @property
    def used_gaussian_field_names(self):
        # Require that this function always return the values in the same order since the ordering
        # is used to define list indices
        sorted_dictionary = OrderedDict(sorted(self._gaussian_models.items()))
        return [name for name in sorted_dictionary]

    def findGaussFieldParameterItem(self, gaussFieldName):
        try:
            return self.get_variogram_model(gaussFieldName)
        except KeyError:
            raise ValueError('Variogram data for gauss field name: {} is not found.'.format(gaussFieldName))

    def __get_property(self, gaussFieldName, keyword):
        return self.get_variogram_model(gaussFieldName)[keyword]

    def getVariogramType(self, gaussFieldName):
        return self.get_variogram_model(gaussFieldName).type

    def getVariogramTypeNumber(self, gaussFieldName):
        return self.getVariogramType(gaussFieldName).value

    def getMainRange(self, gaussFieldName):
        return self.__get_property(gaussFieldName, 'MainRange')

    def getMainRangeFmuUpdatable(self, gaussFieldName):
        return self.__get_property(gaussFieldName, 'MainRangeFMUUpdatable')

    def getPerpRange(self, gaussFieldName):
        return self.__get_property(gaussFieldName, 'PerpRange')

    def getPerpRangeFmuUpdatable(self, gaussFieldName):
        return self.__get_property(gaussFieldName, 'PerpRangeFMUUpdatable')

    def getVertRange(self, gaussFieldName):
        return self.__get_property(gaussFieldName, 'VertRange')

    def getVertRangeFmuUpdatable(self, gaussFieldName):
        return self.__get_property(gaussFieldName, 'VertRangeFMUUpdatable')

    def getAzimuthAngle(self, gaussFieldName):
        return self.__get_property(gaussFieldName, 'AzimuthAngle')

    def getAzimuthAngleFmuUpdatable(self, gaussFieldName):
        return self.__get_property(gaussFieldName, 'AzimuthAngleFMUUpdatable')

    def getDipAngle(self, gaussFieldName):
        return self.__get_property(gaussFieldName, 'DipAngle')

    def getDipAngleFmuUpdatable(self, gaussFieldName):
        return self.__get_property(gaussFieldName, 'DipAngleFMUUpdatable')

    def getPower(self, gaussFieldName):
        return self.__get_property(gaussFieldName, 'Power')

    def getPowerFmuUpdatable(self, gaussFieldName):
        return self.__get_property(gaussFieldName, 'PowerFMUUpdatable')

    def getTrendItem(self, gfName):
        try:
            return self._gaussian_models[gfName].trend
        except KeyError:
            return None

    def getTrendModel(self, gfName):
        trend = self.getTrendItem(gfName)
        if trend is None:
            return None, None, None, None
        else:
            return trend.use_trend, trend.model, trend.relative_std_dev.value, trend.relative_std_dev.updatable

    def hasTrendModel(self, gfName):
        trend = self.getTrendItem(gfName)
        if trend is None:
            return False
        else:
            return trend.use_trend

    def getTrendModelObject(self, gfName):
        item = self.getTrendItem(gfName)
        if item is None:
            return None
        else:
            return item.model

    def get_variogram_model(self, name):
        try:
            return self._gaussian_models[name].variogram
        except KeyError:
            return None

    @property
    def debug_level(self):
        return self.__debug_level

    @debug_level.setter
    def debug_level(self, value):
        self.__debug_level = value

    def setVariogramType(self, gaussFieldName, variogramType):
        self.get_variogram_model(gaussFieldName).type = variogramType

    def setMainRange(self, gaussFieldName, range1):
        self.get_variogram_model(gaussFieldName).ranges.main.value = range1

    def setMainRangeFmuUpdatable(self, gaussFieldName, value):
        self.get_variogram_model(gaussFieldName).ranges.main.updatable = value

    def setPerpRange(self, gaussFieldName, range2):
        self.get_variogram_model(gaussFieldName).ranges.perpendicular.value = range2

    def setPerpRangeFmuUpdatable(self, gaussFieldName, value):
        self.get_variogram_model(gaussFieldName).ranges.perpendicular.updatable = value

    def setVertRange(self, gaussFieldName, range3):
        self.get_variogram_model(gaussFieldName).ranges.vertical.value = range3

    def setVertRangeFmuUpdatable(self, gaussFieldName, value):
        self.get_variogram_model(gaussFieldName).ranges.vertical.updatable = value

    def setAzimuthAngle(self, gaussFieldName, azimuth):
        self.get_variogram_model(gaussFieldName).angles.azimuth.value = azimuth

    def setAzimuthAngleFmuUpdatable(self, gaussFieldName, value):
        self.get_variogram_model(gaussFieldName).angles.azimuth.updatable = value

    def setDipAngle(self, gaussFieldName, dip):
        self.get_variogram_model(gaussFieldName).angles.dip.value = dip

    def setDipAngleFmuUpdatable(self, gaussFieldName, value):
        self.get_variogram_model(gaussFieldName).angles.dip.updatable = value

    def setPower(self, gaussFieldName, power):
        self.get_variogram_model(gaussFieldName).power.value = power

    def setPowerFmuUpdatable(self, gaussFieldName, value):
        self.get_variogram_model(gaussFieldName).power.updatable = value

    def setRelStdDev(self, gaussFieldName, relStdDev):
        return self._set_relative_std_dev(gaussFieldName, value=relStdDev)

    def setRelStdDevFmuUpdatable(self, gaussFieldName, value):
        return self._set_relative_std_dev(gaussFieldName, updatable=value)

    def _set_relative_std_dev(self, gaussian_field_name, value=None, updatable=None):
        # Update trend parameters relStdDev for existing trend for gauss field model
        err = 0
        # Check if gauss field is already defined, then update parameters
        try:
            trend = self._gaussian_models[gaussian_field_name].trend
            if trend.use_trend:
                # Set updated value for relStdDev
                if value is None:
                    value = trend.relative_std_dev.value
                if updatable is None:
                    updatable = trend.relative_std_dev.updatable
                trend.relative_std_dev = FmuProperty(value, updatable)
        except KeyError:
            # This gauss field was not found.
            err = 1
        return err

    def setSeedForPreviewSimulation(self, gf_name, seed):
        err = 0
        if gf_name in self._gaussian_models:
            self._gaussian_models[gf_name].seed = seed
        else:
            err = 1
        return err

    def updateGaussFieldParam(
            self, gf_name, variogram_type, range1, range2, range3, azimuth, dip, power,
            range1_fmu_updatable, range2_fmu_updatable, range3_fmu_updatable, azimuth_fmu_updatable,
            dip_fmu_updatable, power_fmu_updatable, use_trend=False, rel_std_dev=0.0,
            rel_std_dev_fmu_updatable=False, trend_model_obj=None
    ):
        # Update or create new gauss field parameter object (with trend)
        if not isVariogramTypeOK(variogram_type):
            raise ValueError(
                'Error in {class_name} in updateGaussFieldParam\n'
                'Undefined variogram type specified.'.format(class_name=self.__class_name)
            )
        if any([range < 0 for range in [range1, range2, range3]]):
            raise ValueError(
                'Error in {class_name} in updateGaussFieldParam\n'
                'Correlation range < 0.0'.format(class_name=self.__class_name)
            )
        if variogram_type == VariogramType.GENERAL_EXPONENTIAL and not (1.0 <= power <= 2.0):
            raise ValueError(
                'Error in {class_name} in updateGaussFieldParam\n'
                'Exponent in GENERAL_EXPONENTIAL variogram is outside [1.0, 2.0]'.format(class_name=self.__class_name)
            )
        if rel_std_dev < 0.0:
            raise ValueError(
                'Error in {class_name} in updateGaussFieldParam\n'
                'Relative standard deviation used when trends are specified is negative.'
                ''.format(class_name=self.__class_name)
            )

        # Check if gauss field is already defined, then update parameters or create new
        if gf_name not in self._gaussian_models:
            if trend_model_obj is None:
                use_trend = False
                rel_std_dev = 0.0
                rel_std_dev_fmu_updatable = False
            else:
                use_trend = True
            self._gaussian_models[gf_name] = GaussianField(gf_name)
        # Create data for a new gauss field for both variogram  data and trend data
        # But data for trend parameters must be set by another function and default is set here.
        self._gaussian_models[gf_name].variogram = Variogram.from_definition([
            gf_name, variogram_type, range1, range2, range3, azimuth, dip, power,
            range1_fmu_updatable, range2_fmu_updatable, range3_fmu_updatable, azimuth_fmu_updatable,
            dip_fmu_updatable, power_fmu_updatable
        ])
        self._gaussian_models[gf_name].trend = self.create_gauss_field_trend(
            gf_name, use_trend, trend_model_obj, rel_std_dev, rel_std_dev_fmu_updatable
        )

    def updateGaussFieldVariogramParameters(
            self, gf_name, variogram_type, range1, range2, range3, azimuth, dip, power,
            range1_fmu_updatable, range2_fmu_updatable, range3_fmu_updatable,
            azimuth_fmu_updatable, dip_fmu_updatable, power_fmu_updatable):
        # Update gauss field variogram parameters for existing gauss field model
        # But it does not create new object.
        err = 0
        # Check that gauss field is already defined, then update parameters.
        if gf_name in self._gaussian_models:
            self._gaussian_models[gf_name].variogram = Variogram.from_definition([
                gf_name, variogram_type, range1, range2, range3, azimuth, dip, power,
                range1_fmu_updatable, range2_fmu_updatable, range3_fmu_updatable,
                azimuth_fmu_updatable, dip_fmu_updatable, power_fmu_updatable
            ])
        else:
            err = 1
        return err

    def removeGaussFieldParam(self, gfName):
        # Remove from dicts
        self._gaussian_models.pop(gfName, None)

    def updateGaussFieldTrendParam(self, gf_name, use_trend, trend_model_obj, rel_std_dev, rel_std_dev_fmu_updatable):
        # Update trend parameters for existing trend for gauss field model
        # But it does not create new trend object.
        err = 0
        if trend_model_obj is None:
            err = 1
        else:
            # Check if gauss field is already defined, then update parameters
            if gf_name in self._gaussian_models:
                self._gaussian_models[gf_name].trend = Trend(
                    name=gf_name,
                    use_trend=use_trend,
                    model=trend_model_obj,
                    relative_std_dev=FmuProperty(rel_std_dev, rel_std_dev_fmu_updatable)
                )
            else:
                # This gauss field was not found.
                err = 1
        return err

    @staticmethod
    def create_gauss_field_trend(gf_name, use_trend, trend_model_obj, rel_std_dev, rel_std_dev_fmu_updatable):
        return Trend(
            name=gf_name,
            use_trend=use_trend,
            model=trend_model_obj,
            relative_std_dev=FmuProperty(rel_std_dev, rel_std_dev_fmu_updatable)
        )

    def XMLAddElement(self, parent, fmu_attributes):
        if self.debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: call XMLADDElement from ' + self.__class_name)

        # Add child command GaussField
        for grf in self._gaussian_models.values():
            gf_name = grf.name
            variogram = grf.variogram
            variogram_type = variogram.type

            if gf_name != grf.variogram.name or gf_name != grf.trend.name:
                raise ValueError('Error in class: ' + self.__class_name + ' in XMLAddElement')
            trend = grf.trend
            use_trend = trend.use_trend
            trend_obj = trend.model

            tag = 'GaussField'
            attribute = {'name': gf_name}
            elem = Element(tag, attribute)
            parent.append(elem)
            gf_element = elem

            tag = 'Vario'
            attribute = {'name': variogram_type if isinstance(variogram_type, str) else variogram_type.name}
            elem = Element(tag, attribute)
            gf_element.append(elem)
            variogram_element = elem

            properties = ['main', 'perpendicular', 'vertical', 'azimuth', 'dip']

            for prop in properties:
                self._add_xml_element(gf_name, prop, parent, variogram_element, fmu_attributes, createFMUvariableNameForResidual)

            if variogram_type in ['GENERAL_EXPONENTIAL', VariogramType.GENERAL_EXPONENTIAL]:
                self._add_xml_element(gf_name, 'power', parent, variogram_element, fmu_attributes, createFMUvariableNameForResidual)

            if use_trend:
                # Add trend
                trend_obj.XMLAddElement(gf_element, fmu_attributes)

                self._add_xml_element(gf_name, 'relative_std_dev', parent, gf_element, fmu_attributes, createFMUvariableNameForTrend)

            tag = 'SeedForPreview'
            elem = Element(tag)
            seed = grf.seed
            elem.text = ' ' + str(seed) + ' '
            gf_element.append(elem)

    def _add_xml_element(self, gf_name, property_name, parent, xml_element, fmu_attributes, create_fmu_variable):
        zone_number = parent.get('number')
        region_number = parent.get('regionNumber')
        tag = self.__xml_keyword[property_name]
        value = self._gaussian_models[gf_name][property_name]
        elem = Element(tag)
        elem.text = ' ' + str(value) + ' '
        if value.updatable:
            fmu_attribute = create_fmu_variable(tag, gf_name, zone_number, region_number)
            fmu_attributes.append(fmu_attribute)
            elem.attrib = dict(kw=fmu_attribute)
        xml_element.append(elem)

    def simGaussFieldWithTrendAndTransform(
            self, simulation_box_size, grid_size, grid_azimuth_angle, cross_section
    ):
        """ This function is used to create 2D simulation of horizontal or vertical cross sections. The gauss simulation is 2D
            and the correlation ellipsoid for the 3D variogram is projected into the specified cross section in 2D.
            The 3D trend definition is used to calculate an 2D cross section of the trend in the specified horizontal or vertical cross section grid plane
            specified by cross_section.relative_position which is a number between 0 and 1.
            Here 0 means smallest grid index and 1 means largest grid index for the specified cross section direction (IJ plane, IK, plane or JK plane).
            The trend and residual gauss field is added using the specified relative standard deviation and the resulting gaussian field with trend is
            transformed by empiric transformation such that the histogram over all simulated values in the 2D grid become uniform between 0 and 1."""

        gauss_field_items = []
        for grf in self._gaussian_models.values():
            gauss_field_items.append(
                grf.simulate(cross_section, grid_azimuth_angle, grid_size, simulation_box_size, self.debug_level),
            )
        return gauss_field_items

    def calc2DVariogramFrom3DVariogram(self, name, grid_azimuth_angle, projection):
        return self._gaussian_models[name].variogram.calc_2d_variogram_from_3d_variogram(grid_azimuth_angle, projection, self.debug_level)


def _get_projection_parameters(cross_section_type, grid_size, simulation_box_size):
    x_sim_box_size, y_sim_box_size, z_sim_box_size = simulation_box_size
    x_grid, y_grid, z_grid = grid_size
    if cross_section_type == CrossSectionType.IJ:
        grid_dimensions = (x_grid, y_grid)
        size = (x_sim_box_size, y_sim_box_size)
        projection = 'xy'
    elif cross_section_type == CrossSectionType.IK:
        grid_dimensions = (x_grid, z_grid)
        size = (x_sim_box_size, z_sim_box_size)
        projection = 'xz'
    elif cross_section_type == CrossSectionType.JK:
        grid_dimensions = (y_grid, z_grid)
        size = (y_sim_box_size, z_sim_box_size)
        projection = 'yz'
    else:
        raise ValueError('Undefined cross section {}'.format(cross_section_type.name))
    return grid_dimensions, size, projection


def _add_trend(residual_field, trend_field, rel_sigma, trend_max_min_difference, average_trend, debug_level=Debug.OFF):
    """
    Description: Calculate standard deviation sigma = rel_sigma * trend_max_min_difference.
    Add trend and residual field  Field = Trend + sigma*residual
    Input residual_field and trend_field should be 1D float numpy arrays of same size.
    Return is trend plus residual with correct standard deviation as numpy 1D array.
    """
    # Standard deviation
    if abs(trend_max_min_difference) == 0.0:
        sigma = rel_sigma * average_trend
    else:
        sigma = rel_sigma * trend_max_min_difference
    if debug_level >= Debug.VERY_VERBOSE:
        print('Debug output:  Relative standard deviation = ' + str(rel_sigma))
        print('Debug output:  Difference between max value and min value of trend = ' + str(trend_max_min_difference))
        print('Debug output:  Calculated standard deviation = ' + str(sigma))
        print('')
    n = len(trend_field)
    if len(trend_field) != len(residual_field):
        raise IOError('Internal error: Mismatch between size of trend field and residual field in _addTrend')

    gauss_field_with_trend = np.zeros(n, np.float32)
    for i in range(n):
        gauss_field_with_trend[i] = trend_field[i] + residual_field[i] * sigma
    return gauss_field_with_trend


def _transform_empiric_distribution_to_uniform(values, debug_level=Debug.OFF):
    """
    Take input as numpy 1D float array and return numpy 1D float array where
    the values is transformed to uniform distribution.
    The input array is regarded as outcome of  probability distribution.
    The output assign the empiric percentile from the cumulative empiric distribution
    to each array element. This ensure that the probability distribution of the output
    regarded as outcome from a probability distribution is uniform.
    """
    # Transform into uniform distribution
    if debug_level >= Debug.VERY_VERBOSE:
        print('Debug output:  Transform 2D Gauss field by empiric transformation to uniform distribution\n')

    n = len(values)
    transformed = np.zeros(n, np.float32)
    sort_index = np.argsort(values)
    for i in range(n):
        index = sort_index[i]
        u = float(i) / float(n)
        transformed[index] = u

    return transformed


def _calculate_projection(U, debug_level=Debug.OFF):
    func_name = _calculate_projection.__name__
    if debug_level >= Debug.VERY_VERY_VERBOSE:
        print('Debug output: U:')
        print(U)
    w, v = np.linalg.eigh(U)
    if debug_level >= Debug.VERY_VERY_VERBOSE:
        print('Debug output: Eigenvalues:')
        print(w)
        print('Debug output: Eigenvectors')
        print(v)

    # Largest eigenvalue and corresponding eigenvector should be defined as main principal range and direction
    if v[0, 1] != 0.0:
        angle = np.arctan(v[0, 0] / v[0, 1])
        angle = angle * 180.0 / np.pi
        if angle < 0.0:
            angle = angle + 180.0
    else:
        # y component is 0, hence the direction is defined by the x axis
        angle = 90.0
    angle1 = angle
    range1 = np.sqrt(1.0 / w[0])
    if debug_level >= Debug.VERY_VERY_VERBOSE:
        print('Debug output: Function: {funcName} Direction (angle): {angle} for range: {range}'
              ''.format(funcName=func_name, angle=angle1, range=range1))

    # Smallest eigenvalue and corresponding eigenvector should be defined as perpendicular principal direction
    if v[1, 1] != 0.0:
        angle = np.arctan(v[1, 0] / v[1, 1])
        angle = angle * 180.0 / np.pi
        if angle < 0.0:
            angle = angle + 180.0
    else:
        # y component is 0, hence the direction is defined by the x axis
        angle = 90.0
    angle2 = angle
    range2 = np.sqrt(1.0 / w[1])
    if debug_level >= Debug.VERY_VERY_VERBOSE:
        print('Debug output: Function: {funcName} Direction (angle): {angle} for range: {range}'
              ''.format(funcName=func_name, angle=angle2, range=range2))

    # Angles are azimuth angles
    return angle1, range1, angle2, range2
