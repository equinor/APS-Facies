#!/bin/env python
# -*- coding: utf-8 -*-
from numpy import float64, ndarray

from aps.algorithms.APSMainFaciesTable import APSMainFaciesTable
from aps.algorithms.trend import (
    Trend3D_elliptic,
    Trend3D_elliptic_cone,
    Trend3D_hyperbolic,
    Trend3D_linear,
    Trend3D_rms_param,
    Trend3D_rms_map,
    Trend3D,
)
from typing import List, Optional, Tuple, Union, TypeVar, Dict, Callable
from xml.etree.ElementTree import Element

import numpy as np
from collections import OrderedDict

from aps.algorithms.properties import (
    make_ranged_property,
    make_trend_property,
    make_angle_property,
    make_lower_bounded_property,
    FmuProperty,
    CrossSection,
)
from aps.utils.checks import isVariogramTypeOK
from aps.utils.constants.simple import (
    Debug,
    VariogramType,
    CrossSectionType,
    MinimumValues,
    MaximumValues,
    ModuloValues,
    TrendType,
    Direction,
    OriginType,
)
from aps.utils.containers import FmuAttribute
from aps.utils.numeric import flip_if_necessary
from aps.utils.simGauss2D import simGaussField
from aps.utils.types import (
    GridSize,
    SimulationBoxSize,
    SimulationBoxOrigin,
    GaussianFieldName,
    PropertyName,
    XMLKeyword,
    Number,
)
from aps.utils.xmlUtils import (
    getIntCommand,
    getKeyword,
    createFMUvariableNameForResidual,
    createFMUvariableNameForTrend,
    get_fmu_value_from_xml,
    isFMUUpdatable,
)

# Dictionaries of legal value ranges for gauss field parameters
from aps.utils.records import VariogramRecord, SeedRecord, TrendRecord


T = TypeVar('T')


class Point3D(tuple):
    def __new__(cls, **kwargs):
        point = (kwargs['x'], kwargs['y'], kwargs['z'])
        return super().__new__(cls, point)


class Point2D(tuple):
    def __new__(cls, **kwargs):
        point = (kwargs['x'], kwargs['y'])
        return super().__new__(cls, point)


class GaussianFieldSimulationSettings:
    __slots__ = (
        '_cross_section',
        '_grid_azimuth',
        '_grid_size',
        '_simulation_box_size',
        '_simulation_box_origin',
        '_seed',
    )
    # TODO: Fill in remaining data

    def __init__(
        self,
        cross_section: CrossSection,
        grid_azimuth: float,
        grid_size: GridSize,
        simulation_box_size: SimulationBoxSize,
        simulation_box_origin: SimulationBoxOrigin,
        seed: int,
    ):
        assert isinstance(cross_section, CrossSection)
        assert all(isinstance(coor, int) for coor in grid_size) and len(grid_size) == 3
        assert (
            all(isinstance(coor, (float, int)) for coor in simulation_box_size)
            and len(simulation_box_size) == 3
        )
        assert (
            all(isinstance(coor, (float, int)) for coor in simulation_box_origin)
            and len(simulation_box_origin) == 2
        )
        assert isinstance(seed, int)
        grid_azimuth %= 360

        self._cross_section = cross_section
        self._grid_azimuth = grid_azimuth
        self._grid_size = grid_size
        self._simulation_box_size = simulation_box_size
        self._simulation_box_origin = simulation_box_origin
        self._seed = seed

        # Rescale grid size (nx, ny, nz) for preview grid used in the GUI
        self._rescale_grid_size_for_preview()

    @property
    def cross_section(self) -> CrossSection:
        return self._cross_section

    @property
    def grid_azimuth(self) -> float:
        return self._grid_azimuth

    @property
    def grid_size(self) -> GridSize:
        return self._grid_size

    @property
    def simulation_box_size(self) -> SimulationBoxSize:
        return self._simulation_box_size

    @property
    def simulation_box_origin(self) -> SimulationBoxOrigin:
        return self._simulation_box_origin

    @property
    def seed(self) -> int:
        return self._seed

    @property
    def dimensions(self) -> Tuple[int, int]:
        grid_size = self.grid_size
        mapping = {
            CrossSectionType.IJ: (grid_size[0], grid_size[1]),
            CrossSectionType.IK: (grid_size[0], grid_size[2]),
            CrossSectionType.JK: (grid_size[1], grid_size[2]),
        }
        try:
            return mapping[self.cross_section.type]
        except KeyError:
            raise NotImplementedError

    def _rescale_grid_size_for_preview(self):
        # Change nz to be half of horizontal number of grid cells
        # as default for cross sections.
        # GUI preview plot does not care about grid cell size, but
        # only about number of grid cell values represented as a 2D matrix
        x_dim = self._grid_size[0]
        y_dim = self._grid_size[1]
        z_dim = self._grid_size[2]
        if x_dim <= y_dim:
            if x_dim < 100:
                y_dim = int(y_dim * 100 / x_dim)
                x_dim = 100
            z_dim = int(y_dim / 2)
        elif y_dim < x_dim:
            if y_dim < 100:
                x_dim = int(x_dim * 100 / y_dim)
                y_dim = 100
            z_dim = int(x_dim / 2)
        self._grid_size = (x_dim, y_dim, z_dim)

    def merge(
        self,
        cross_section: Optional[CrossSection] = None,
        grid_azimuth: Optional[float] = None,
        grid_size: Optional[GridSize] = None,
        simulation_box_size: Optional[SimulationBoxSize] = None,
        simulation_box_origin: Optional[SimulationBoxOrigin] = None,
        seed: Optional[int] = None,
    ) -> 'GaussianFieldSimulationSettings':
        if cross_section is None:
            cross_section = self.cross_section
        if grid_azimuth is None:
            grid_azimuth = self.grid_azimuth
        if grid_size is None:
            grid_size = self.grid_size
        if simulation_box_size is None:
            simulation_box_size = self.simulation_box_size
        if simulation_box_origin is None:
            simulation_box_origin = self.simulation_box_origin
        if seed is None:
            seed = self.seed
        return GaussianFieldSimulationSettings(
            cross_section=cross_section,
            grid_azimuth=grid_azimuth,
            grid_size=grid_size,
            simulation_box_size=simulation_box_size,
            simulation_box_origin=simulation_box_origin,
            seed=seed,
        )

    @classmethod
    def from_dict(cls, **kwargs) -> 'GaussianFieldSimulationSettings':
        return cls(
            cross_section=CrossSection.from_dict(**kwargs['crossSection']),
            grid_azimuth=kwargs['gridAzimuth'],
            grid_size=Point3D(**kwargs['gridSize']),
            simulation_box_size=Point3D(**kwargs['simulationBox']),
            simulation_box_origin=Point2D(**kwargs['simulationBoxOrigin']),
            seed=kwargs['seed'],
        )


class GaussianFieldSimulation:
    __slots__ = '_name', '_field', '_settings'

    def __init__(
        self,
        name: GaussianFieldName,
        field: ndarray,
        settings: GaussianFieldSimulationSettings,
    ):
        self._name = name
        self._field = field
        self._settings = settings

    @property
    def name(self) -> GaussianFieldName:
        return self._name

    @property
    def field(self) -> ndarray:
        return self._field

    @property
    def settings(self) -> GaussianFieldSimulationSettings:
        return self._settings

    @property
    def cross_section(self) -> CrossSection:
        return self._settings.cross_section

    @property
    def grid_azimuth(self) -> float:
        return self._settings.grid_azimuth

    @property
    def grid_size(self) -> GridSize:
        return self._settings.grid_size

    @property
    def simulation_box_size(self) -> SimulationBoxSize:
        return self._settings.simulation_box_size

    def field_as_matrix(self, grid_index_order: str = 'F') -> ndarray:
        data = np.reshape(
            self.field, self.settings.dimensions, grid_index_order
        ).transpose()
        data = flip_if_necessary(data, self.cross_section)
        return data


class GaussianField:
    def __init__(
        self,
        name: Union[GaussianFieldName, str],
        variogram: Optional['Variogram'] = None,
        trend: Optional['Trend'] = None,
        seed: Optional[int] = None,
        settings: Optional[GaussianFieldSimulationSettings] = None,
    ):
        # TODO: Make sane default values for variogram and trend
        if trend is None:
            trend = Trend(name, use_trend=False)
        if all(_ is None for _ in [seed, settings]):
            seed = 0
        if all(_ is not None for _ in [seed, settings]):
            settings = settings.merge(seed=seed)
        self._name = name
        self._variogram = variogram
        self._trend = trend
        self._seed = seed
        self._settings = settings

    @property
    def seed(self) -> int:
        if self._seed is None:
            return self._settings.seed
        return self._seed

    @seed.setter
    def seed(self, value):
        # TODO: This probably should not be done
        if self.settings is not None:
            self._settings = self.settings.merge(seed=value)
        self._seed = value

    @property
    def name(self) -> GaussianFieldName:
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def variogram(self) -> 'Variogram':
        return self._variogram

    @variogram.setter
    def variogram(self, value):
        # TODO: Verify
        self._variogram = value

    @property
    def trend(self) -> 'Trend':
        return self._trend

    @trend.setter
    def trend(self, value):
        # TODO: Verify
        self._trend = value

    @property
    def settings(self) -> Optional[GaussianFieldSimulationSettings]:
        return self._settings

    @settings.setter
    def settings(self, value):
        if not (isinstance(value, GaussianFieldSimulationSettings) or value is None):
            raise TypeError(
                'Settings must be of type "GaussianFieldSimulationSettings", or None'
            )
        self._settings = value

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
                    raise AttributeError(
                        f"The Gaussian Field ('{self.name}') has no attribute {item}"
                    )

    def _simulate(
        self,
        cross_section: Optional[CrossSection] = None,
        grid_azimuth: Optional[float] = None,
        grid_size: Optional[GridSize] = None,
        simulation_box_size: Optional[SimulationBoxSize] = None,
        simulation_box_origin: Optional[SimulationBoxOrigin] = None,
        debug_level: Debug = Debug.OFF,
    ) -> ndarray:
        args = (
            cross_section,
            grid_azimuth,
            grid_size,
            simulation_box_size,
            simulation_box_origin,
        )
        if self.settings is None:
            settings = GaussianFieldSimulationSettings(*args)
        else:
            settings = self.settings.merge(*args)

        grid_dimensions_2d, sizes, projection = _get_projection_parameters(
            settings.cross_section.type,
            settings.grid_size,
            settings.simulation_box_size,
        )
        # Find data for specified Gauss field name
        seed_value = self.seed
        variogram_type = self.variogram.type
        power = self.variogram.power.value
        if debug_level >= Debug.VERY_VERBOSE:
            print('')
            print('--- Within simGaussFieldWithTrendAndTransform')
            print('--- Simulate gauss field: ' + self.name)
            print('--- VariogramType: ' + str(variogram_type))
            print(
                '--- Azimuth angle for Main range direction: '
                + str(self.variogram.angles.azimuth)
            )
            print('--- Azimuth angle for grid: ' + str(settings.grid_azimuth))
            print(
                '--- Dip angle for Main range direction: '
                + str(self.variogram.angles.dip)
            )

            if variogram_type == VariogramType.GENERAL_EXPONENTIAL:
                print('--- Power    : ' + str(power))

            print('--- Seed value: ' + str(seed_value))
        # Calculate 2D projection of the correlation ellipsoid
        angle1, range1, angle2, range2 = (
            self.variogram.calc_2d_variogram_from_3d_variogram(
                settings.grid_azimuth, projection, debug_level
            )
        )
        azimuth_variogram = angle1
        if debug_level >= Debug.VERY_VERBOSE:
            print(f'\n--- Range1 in projection: {projection} : {range1}')
            print(f'--- Range2 in projection: {projection} : {range2}')
            print(f'--- Angle from vertical axis for Range1 direction: {angle1}')
            print(f'--- Angle from vertical axis for Range2 direction: {angle2}')
            print(
                f'--- (gridDim1, gridDim2) = ({grid_dimensions_2d[0]},{grid_dimensions_2d[1]})'
            )
            print(f'--- (Size1, Size2) = ({sizes[0]},  {sizes[1]})')

        residual_field = simGaussField(
            seed_value,
            *grid_dimensions_2d,
            *sizes,
            variogram_type,
            range1,
            range2,
            azimuth_variogram,
            power,
            debug_level,
        )
        # Calculate trend
        _, use_trend, trend_model, relative_std_dev, _ = self.trend.as_list()
        if use_trend and trend_model.type in (
            TrendType.NONE,
            TrendType.RMS_PARAM,
            TrendType.RMS_TRENDMAP,
        ):
            print(
                f'Note: No preview is implemented for trend type {trend_model.type.name}. Ignore trend in preview. '
            )
            gauss_field_with_trend = residual_field
        elif use_trend:
            if debug_level >= Debug.VERBOSE:
                print(f'-- Use Trend: {trend_model.type.name}')
            min_max_difference, average_trend, trend_field = (
                trend_model.createTrendFor2DProjection(
                    settings.simulation_box_size,
                    settings.grid_azimuth,
                    settings.grid_size,
                    settings.cross_section,
                    settings.simulation_box_origin,
                )
            )
            gauss_field_with_trend = _add_trend(
                residual_field,
                trend_field,
                relative_std_dev,
                min_max_difference,
                average_trend,
                debug_level,
            )
        else:
            gauss_field_with_trend = residual_field
        return _transform_empiric_distribution_to_uniform(
            gauss_field_with_trend, debug_level
        )

    def simulate(
        self,
        cross_section: Optional[CrossSection] = None,
        grid_azimuth: Optional[float] = None,
        grid_size: Optional[GridSize] = None,
        simulation_box_size: Optional[SimulationBoxSize] = None,
        simulation_box_origin: Optional[SimulationBoxOrigin] = None,
        debug_level: Debug = Debug.OFF,
    ) -> GaussianFieldSimulation:
        if self.settings is None:
            self.settings = GaussianFieldSimulationSettings(
                cross_section,
                grid_azimuth,
                grid_size,
                simulation_box_size,
                simulation_box_origin,
                self.seed,
            )
        else:
            self.settings = self.settings.merge(cross_section, grid_azimuth)
        return GaussianFieldSimulation(
            name=self.name,
            field=self._simulate(),
            settings=self.settings,
        )


MainRange = FmuProperty[int]
PerpendicularRange = FmuProperty[int]
VerticalRange = FmuProperty[int]


class Ranges:
    __slots__ = '_main', '_perpendicular', '_vertical'

    def __init__(
        self,
        main: Union[MainRange, int],
        perpendicular: Union[PerpendicularRange, int],
        vertical: Union[VerticalRange, int],
    ):
        self.main = main
        self.perpendicular = perpendicular
        self.vertical = vertical

    main: MainRange = make_lower_bounded_property('main', strictly_greater=True)
    perpendicular: PerpendicularRange = make_lower_bounded_property(
        'perpendicular', strictly_greater=True
    )
    vertical: VerticalRange = make_lower_bounded_property(
        'vertical', strictly_greater=True
    )

    @property
    def range1(self) -> MainRange:
        return self.main

    @range1.setter
    def range1(self, value):
        self.main = value

    @property
    def range2(self) -> PerpendicularRange:
        return self.perpendicular

    @range2.setter
    def range2(self, value):
        self.perpendicular = value

    @property
    def range3(self) -> VerticalRange:
        return self.vertical

    @range3.setter
    def range3(self, value):
        self.vertical = value


class Angles:
    __slots__ = '_azimuth', '_dip'

    def __init__(
        self,
        azimuth: Union[FmuProperty[float], float],
        dip: Union[FmuProperty[float], float],
    ):
        self.azimuth = azimuth
        self.dip = dip

    azimuth: FmuProperty[float] = make_angle_property('azimuth')
    dip: FmuProperty[float] = make_angle_property('dip')


class Trend:
    __slots__ = '_name', '_use_trend', '_model', '_relative_std_dev'

    def __init__(
        self,
        name: GaussianFieldName,
        use_trend: bool = False,
        model: Optional[Trend3D] = None,
        relative_std_dev: Optional[FmuProperty[float]] = None,
    ):
        if relative_std_dev is None:
            relative_std_dev = FmuProperty(1.0, False)
        elif isinstance(relative_std_dev, dict):
            relative_std_dev = FmuProperty(
                relative_std_dev['value'], relative_std_dev['updatable']
            )
        self._name = name
        self._model = model
        self.relative_std_dev = relative_std_dev
        self.use_trend = use_trend

    relative_std_dev: FmuProperty[float]
    relative_std_dev = make_lower_bounded_property('relative_std_dev')
    use_trend: bool
    use_trend = make_trend_property('use_trend')

    @property
    def name(self) -> GaussianFieldName:
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def model(
        self,
    ) -> Optional[
        Union[
            Trend3D_hyperbolic,
            Trend3D_elliptic,
            Trend3D_linear,
            Trend3D_rms_param,
            Trend3D_rms_map,
        ]
    ]:
        return self._model

    @model.setter
    def model(self, value):
        if value is None:
            self.use_trend = False
        self._model = value

    @classmethod
    def from_definition(cls, definition: Union[TrendRecord, List]) -> 'Trend':
        definition = TrendRecord._make(definition)
        return cls(
            name=definition.Name,
            use_trend=definition.UseTrend,
            model=definition.Object,
            relative_std_dev=FmuProperty(definition.RelStdev, definition.RelStdevFMU),
        )

    def as_list(self) -> Tuple[GaussianFieldName, bool, Optional[Trend3D], float, bool]:
        return (
            self.name,
            self.use_trend,
            self.model,
            self.relative_std_dev.value,
            self.relative_std_dev.updatable,
        )

    @classmethod
    def from_dict(cls, name: GaussianFieldName, use: bool = False, **kwargs) -> 'Trend':
        try:
            relative_std_dev = kwargs.pop('relativeStdDev')
        except KeyError:
            relative_std_dev = None
        model = cls.get_model(**kwargs) if use else None
        return cls(
            name=name, use_trend=use, model=model, relative_std_dev=relative_std_dev
        )

    @staticmethod
    def get_model(**kwargs) -> Trend3D:
        kwargs = _map_js_to_py(**kwargs)
        _type = kwargs['type']
        if _type == TrendType.NONE:
            # TODO: Refactor Trend3D, so as to return an empty Trend3D object?
            return None
        else:
            trend_models = {
                TrendType.RMS_PARAM: Trend3D_rms_param,
                TrendType.RMS_TRENDMAP: Trend3D_rms_map,
                TrendType.LINEAR: Trend3D_linear,
                TrendType.ELLIPTIC: Trend3D_elliptic,
                TrendType.ELLIPTIC_CONE: Trend3D_elliptic_cone,
                TrendType.HYPERBOLIC: Trend3D_hyperbolic,
            }
            try:
                return trend_models[_type](**kwargs)
            except KeyError:
                raise IOError(f'Missing input data for trend model: {_type.name}')


def _map_js_to_py(add_empty=False, **kwargs):
    res = {}
    for key, value in kwargs.items():
        if key == 'type':
            try:
                _type = getattr(TrendType, value)
            except AttributeError:
                _type = TrendType.NONE
            res['type'] = _type
        elif key == 'angle':
            suffix = '_angle'
            for _key, _value in kwargs[key].items():
                _add_parameter(_key + suffix, _value, res, add_empty)
        elif key == 'stackingDirection':
            try:
                direction = getattr(Direction, value)
                res['direction'] = direction
            except AttributeError:
                if add_empty:
                    res['direction'] = None
        elif key == 'parameter':
            _add_parameter('rms_parameter_name', value, res, add_empty)
        elif key == 'trendMapName':
            _add_parameter('rms_trendmap_name', value, res, add_empty)
        elif key == 'trendMapZone':
            _add_parameter('rms_trendmap_zone', value, res, add_empty)
        elif key == 'curvature':
            _add_parameter('curvature', value, res, add_empty)
        elif key == 'origin':
            if value['type'] is None:
                continue
            _type = getattr(OriginType, value['type'], None)
            x, x_updatable = _get_value(value['x'])
            y, y_updatable = _get_value(value['y'])
            z, z_updatable = _get_value(value['z'])
            origin = []
            updatable = []
            for v, u in [(x, x_updatable), (y, y_updatable), (z, z_updatable)]:
                if v is not None or add_empty:
                    origin.append(v)
                    updatable.append(u)
            if len(origin) > 0 or add_empty:
                res['origin'] = tuple(origin)
                res['origin_fmu_updatable'] = tuple(updatable)
            if _type is not None or add_empty:
                res['origin_type'] = _type
        elif key == 'relativeSize':
            _add_parameter('relative_size', value, res, add_empty)
        else:
            raise NotImplementedError
    return res


def _get_value(value):
    if isinstance(value, dict):
        return value['value'], value['updatable']
    return value, None


def _add_parameter(name, value, res, add_emtpy=False):
    if value is not None or add_emtpy:
        if isinstance(value, dict):
            _value, updatable = _get_value(value)
            if _value is not None or add_emtpy:
                res[name] = _value
                res[name + '_fmu_updatable'] = updatable
        else:
            res[name] = value


class Variogram:
    types: VariogramType = VariogramType

    def __init__(
        self,
        name: GaussianFieldName,
        type: VariogramType,
        ranges: Ranges,
        angles: Angles,
        power: Optional[FmuProperty] = None,
    ):
        self._type = None

        if power is None:
            power = FmuProperty(MinimumValues['power'], False)
        self.name = name
        self.power = power
        self.type = type
        self.ranges = ranges
        self.angles = angles

    power: FmuProperty[float]
    power = make_ranged_property('power', 'power must be between {min}, and {max}')

    @property
    def type(self) -> VariogramType:
        return self._type

    @type.setter
    def type(self, value):
        if isinstance(value, str):
            value = value.upper()
        if not isVariogramTypeOK(value):
            raise ValueError(f'The given variogram is not valid ({value})')
        elif value == VariogramType.GENERAL_EXPONENTIAL and not (
            MinimumValues['power'] <= self.power.value <= MaximumValues['power']
        ):
            raise ValueError(
                "While using 'GENERAL_EXPONENTIAL' variogram, 'power' MUST be in [1, 2]"
            )
        if isinstance(value, str):
            value = VariogramType[value]
        self._type = value

    @classmethod
    def from_definition(cls, definition: Union[VariogramRecord, List]):
        definition = VariogramRecord._make(definition)
        if isinstance(definition.Type, str):
            variogram_type = VariogramType[definition.Type]
        else:
            variogram_type = definition.Type
        return cls(
            name=definition.Name,
            type=variogram_type,
            ranges=Ranges(
                main=FmuProperty(
                    definition.MainRange, definition.MainRangeFMUUpdatable
                ),
                perpendicular=FmuProperty(
                    definition.PerpRange, definition.PerpRangeFMUUpdatable
                ),
                vertical=FmuProperty(
                    definition.VertRange, definition.VertRangeFMUUpdatable
                ),
            ),
            angles=Angles(
                azimuth=FmuProperty(
                    definition.AzimuthAngle, definition.AzimuthAngleFMUUpdatable
                ),
                dip=FmuProperty(definition.DipAngle, definition.DipAngleFMUUpdatable),
            ),
            power=FmuProperty(definition.Power, definition.PowerFMUUpdatable),
        )

    @staticmethod
    def __mapping__() -> Dict[str, int]:
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

    def as_list(self) -> list:
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

    def calc_2d_variogram_from_3d_variogram(
        self,
        grid_azimuth: float,
        projection: str,
        debug_level: Debug = Debug.OFF,
    ) -> Tuple[float64, float64, float64, float64]:
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
        principal direction in x direction and the third in z direction.
        Note also that the coordinate system (x,y,z) is left handed and z axis is pointing
        downward compared to a right handed coordinate system.

        After calculating M in (x,y,z) coordinates, a project is taken into either x,y,or z plane to get the correlation
        ellipse in 2D cross section. This correlation ellipse is used when simulating 2D gaussian fields in cross sections.
        """
        func_name = self.calc_2d_variogram_from_3d_variogram.__name__
        if debug_level >= Debug.VERY_VERBOSE:
            print(f'--- Function: {func_name}')
        ry = self.ranges.main.value
        rx = self.ranges.perpendicular.value
        rz = self.ranges.vertical.value
        assert all(r > 0 for r in [rx, ry, rz])

        # Azimuth relative to global x,y,z coordinates
        azimuth = self.angles.azimuth.value

        # Azimuth relative to local coordinate system defined by the orientation of the grid (simulation box)
        azimuth = azimuth - grid_azimuth

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
        R_dip = np.array(
            [[1.0, 0.0, 0.0], [0.0, cos_dip, -sin_dip], [0.0, sin_dip, cos_dip]]
        )

        # define R_azimuth matrix
        # R_azimuth*V will rotate the vector V by the angle azimuth around the z axis.
        # The vector [0,1,0] (unit vector in y direction) will get positive x component if azimuth angle
        # is positive (between 0 and 180 degrees)
        R_azimuth = np.array(
            [[cos_theta, sin_theta, 0.0], [-sin_theta, cos_theta, 0.0], [0.0, 0.0, 1.0]]
        )

        # The combination R = R_azimuth * R_dip will
        # rotate the vector V first by a dip angle around x axis and then by an azimuth angle around z axis

        # calculate R matrix to get from (x',y',z') to (x,y,z)
        R = R_dip.dot(R_azimuth)

        # calculate M matrix in principal coordinates (x',y',z')
        M_diag = np.array(
            [
                [1.0 / (rx * rx), 0.0, 0.0],
                [0.0, 1.0 / (ry * ry), 0.0],
                [0.0, 0.0, 1.0 / (rz * rz)],
            ]
        )

        # The M matrix in (x,y,z) coordinates is given by M = transpose(R) * M_diag * R
        tmp = M_diag.dot(R)
        Rt = np.transpose(R)
        M = Rt.dot(tmp)
        if debug_level >= Debug.VERY_VERY_VERBOSE:
            print('--- M:')
            print(M)
            print('')

        # Let U be the 2x2 matrix in the projection (where row and column corresponding to
        # the coordinate that is set to 0 is removed

        # Calculate the projection of the ellipsoid onto the coordinate planes
        if projection == 'xy':
            U = np.array([[M[0, 0], M[0, 1]], [M[0, 1], M[1, 1]]])
        elif projection == 'xz':
            U = np.array([[M[0, 0], M[0, 2]], [M[0, 2], M[2, 2]]])
        elif projection == 'yz':
            U = np.array([[M[1, 1], M[1, 2]], [M[1, 2], M[2, 2]]])
        else:
            raise ValueError(
                'Unknown projection for calculation of 2D variogram ellipse from 3D variogram ellipsoid'
            )
        # Calculate half-axes and rotation of the ellipse that results from the 2D projection of the 3D ellipsoid.
        # This is done by calculating eigenvalues and eigenvectors of the 2D version of the M matrix.
        # angles are azimuth angles (Measured from 2nd axis clockwise)
        angle1, range1, angle2, range2 = _calculate_projection(
            U, debug_level=debug_level
        )

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

    def __init__(
        self,
        ET_Tree_zone: Optional[Element] = None,
        mainFaciesTable: Optional[APSMainFaciesTable] = None,
        modelFileName: Optional[str] = None,
        debug_level: int = Debug.OFF,
        simBoxThickness: Number = 0,
    ):
        """
        Description: Can create empty object or object with data read from xml tree representing the model file.
        """

        # Dictionary give xml keyword for each variable
        self.__xml_keyword: Dict[PropertyName, XMLKeyword] = {
            'main': 'MainRange',
            'perpendicular': 'PerpRange',
            'vertical': 'VertRange',
            'azimuth': 'AzimuthAngle',
            'dip': 'DipAngle',
            'power': 'Power',
            'relative_std_dev': 'RelStdDev',
        }

        self._gaussian_models: Dict[GaussianFieldName, GaussianField] = OrderedDict()

        self.__class_name: str = self.__class__.__name__
        self.__debug_level = Debug.OFF
        self.__main_facies_table = None
        self.__sim_box_thickness = 0
        self.__zone_number = 0
        self.__model_file_name = None

        if ET_Tree_zone is not None:
            # Get data from xml tree
            if debug_level >= Debug.VERY_VERBOSE:
                print(f'--- Call init {self.__class_name} and read from xml file')

            assert mainFaciesTable is not None
            assert simBoxThickness is not None

            self.__main_facies_table = mainFaciesTable
            self.__sim_box_thickness = simBoxThickness
            self.__model_file_name = modelFileName
            self.__debug_level = debug_level

            self.__interpretXMLTree(ET_Tree_zone)

    def __interpretXMLTree(self, ET_Tree_zone):
        """
        Description: Read Gauss field models for current zone.
        Read trend models for the same gauss fields and start seed for 2D preview simulations.
        """
        zone_number = ET_Tree_zone.get('number')
        region_number = ET_Tree_zone.get('regionNumber')
        for gf in ET_Tree_zone.findall('GaussField'):
            gf_name = gf.get('name')
            if self.debug_level >= Debug.VERY_VERBOSE:
                print(f'--- Gauss field name: {gf_name}')

            # Read variogram for current GF
            variogram, variogram_type = self.get_variogram(gf, gf_name, zone_number)

            range1, range1_fmu_updatable = self._get_value_from_xml('main', variogram)
            range2, range2_fmu_updatable = self._get_value_from_xml(
                'perpendicular', variogram
            )
            range3, range3_fmu_updatable = self._get_value_from_xml(
                'vertical', variogram
            )

            azimuth, azimuth_fmu_updatable = self._get_value_from_xml(
                'azimuth', variogram
            )
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
                    print('--- Read trend')
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
                    'model_file_name': self.__model_file_name,
                    'debug_level': self.debug_level,
                }

                trend_models = {
                    'Linear3D': Trend3D_linear,
                    'Elliptic3D': Trend3D_elliptic,
                    'Hyperbolic3D': Trend3D_hyperbolic,
                    'RMSParameter': Trend3D_rms_param,
                    'RMSTrendMap': Trend3D_rms_map,
                    'EllipticCone3D': Trend3D_elliptic_cone,
                }
                try:
                    trend_model = trend_models[trend_name.tag].from_xml(
                        trend_xml_obj.find(trend_name.tag), **common_params
                    )
                except KeyError:
                    raise NameError(
                        'Error in {className}\n'
                        'Error: Specified name of trend function {trendName} is not implemented.'
                        ''.format(className=self.__class_name, trendName=trend_name.tag)
                    )
            else:
                if self.debug_level >= Debug.VERY_VERBOSE:
                    print('--- No trend is specified')
                use_trend = False
                trend_model = None
                relative_std_dev = 0.0
                rel_std_dev_fmu_updatable = False

            # Read relative std.dev.
            if use_trend:
                relative_std_dev, rel_std_dev_fmu_updatable = self._get_value_from_xml(
                    'relative_std_dev', gf
                )

            # Read preview seed for current GF
            seed = getIntCommand(
                gf, 'SeedForPreview', 'GaussField', modelFile=self.__model_file_name
            )

            # Add gauss field parameters to data structure
            self.updateGaussFieldParam(
                gf_name,
                variogram_type,
                range1,
                range2,
                range3,
                azimuth,
                dip,
                power,
                range1_fmu_updatable,
                range2_fmu_updatable,
                range3_fmu_updatable,
                azimuth_fmu_updatable,
                dip_fmu_updatable,
                power_fmu_updatable,
                use_trend,
                relative_std_dev,
                rel_std_dev_fmu_updatable,
                trend_model,
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
            print('--- Gauss field variogram parameter for current zone model:')
            print([grf.variogram.type for grf in self._gaussian_models.values()])

            print('--- Gauss field trend parameter for current zone model:')
            print([grf.trend.name for grf in self._gaussian_models.values()])

            print('--- Gauss field preview seed for current zone model:')
            print([(name, grf.seed) for name, grf in self._gaussian_models.items()])

    def _get_value_from_xml(
        self, property_name: str, xml_tree: Element
    ) -> Tuple[Number, bool]:
        kwargs = {'parentKeyword': 'Vario', 'modelFile': self.__model_file_name}

        if property_name in MaximumValues:
            kwargs['maxValue'] = MaximumValues[property_name]
        if property_name in MinimumValues:
            kwargs['minValue'] = MinimumValues[property_name]
        if property_name in ModuloValues:
            kwargs['moduloAngle'] = ModuloValues[property_name]

        keyword = self.__xml_keyword[property_name]
        return get_fmu_value_from_xml(xml_tree, keyword, **kwargs)

    def get_variogram(
        self,
        gf: Element,
        gf_name: GaussianFieldName,
        zone_number: int,
    ) -> Tuple[Element, VariogramType]:
        variogram = getKeyword(
            gf, 'Vario', 'GaussField', modelFile=self.__model_file_name
        )
        variogram_type = self.get_variogram_type(variogram)
        if not isVariogramTypeOK(variogram_type):
            raise ValueError(
                f'In model file {self.__model_file_name} in zone number: {zone_number}'
                f' in command Vario for gauss field {gf_name}.\n'
                'Specified variogram type is not defined.'
            )
        return variogram, variogram_type

    @staticmethod
    def get_variogram_type(
        variogram: Union[str, VariogramType, Element],
    ) -> VariogramType:
        if isinstance(variogram, str):
            name = variogram
        elif isinstance(variogram, Element):
            name = variogram.get('name')
        elif isinstance(variogram, VariogramType):
            return variogram
        else:
            raise ValueError(f'Unknown type: {variogram}')
        name = name.upper()
        try:
            return VariogramType[name]
        except KeyError:
            raise ValueError(f'Error: Unknown variogram type {name}')

    def initialize(
        self,
        main_facies_table: APSMainFaciesTable,
        gauss_model_list: List[List[Union[str, float, bool]]],
        trend_model_list: Union[
            List[
                Union[
                    List[Union[str, int, Trend3D_hyperbolic, float]],
                    List[Union[str, int, Trend3D_elliptic]],
                ]
            ],
            List[
                Union[
                    List[Union[str, int, Trend3D_hyperbolic, float]],
                    List[Union[str, int, Trend3D_elliptic_cone, float]],
                    List[Union[str, int, Trend3D_hyperbolic]],
                ]
            ],
            List[
                Union[
                    List[Union[str, int, Trend3D_linear]],
                    List[Union[str, int, Trend3D_elliptic, float]],
                    List[Union[str, int, Trend3D_elliptic]],
                ]
            ],
            List[
                Union[
                    List[Union[str, int, Trend3D_linear, float]],
                    List[Union[str, int, Trend3D_linear]],
                ]
            ],
            List[
                Union[
                    List[Union[str, int, Trend3D_hyperbolic, float]],
                    List[Union[str, int, Trend3D_elliptic]],
                    List[Union[str, int, Trend3D_elliptic, float]],
                ]
            ],
        ],
        sim_box_thickness: float,
        preview_seed_list: List[List[Union[str, int]]],
        debug_level: Debug = Debug.OFF,
    ) -> None:
        if debug_level >= Debug.VERY_VERBOSE:
            print(f'--- Call the initialize function in {self.__class_name}')

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
                raise ValueError(
                    'Programming error: Input list items in gauss_model_list is not of correct length'
                )
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
    def fields(self) -> List[GaussianField]:
        return list(self._gaussian_models.values())

    @property
    def num_gaussian_fields(self) -> int:
        return len(self._gaussian_models)

    @property
    def zone_number(self) -> int:
        return self.__zone_number

    @zone_number.setter
    def zone_number(self, value: int):
        self.__zone_number = value

    @property
    def used_gaussian_field_names(self) -> List[GaussianFieldName]:
        # Require that this function always return the values in the same order since the ordering
        # is used to define list indices
        # The sequence here should be the same as the sequence in alphaIndxList in the truncation base class Trunc2D_Base
        ordered_dictionary = OrderedDict(self._gaussian_models.items())
        return [name for name in ordered_dictionary]

    def findGaussFieldParameterItem(
        self, gaussFieldName: GaussianFieldName
    ) -> List[Union[str, float, bool]]:
        try:
            return self.get_variogram_model(gaussFieldName)
        except KeyError:
            raise ValueError(
                'Variogram data for gauss field name: {} is not found.'.format(
                    gaussFieldName
                )
            )

    def __get_property(
        self, gaussFieldName: GaussianFieldName, keyword: str
    ) -> Union[str, float, bool]:
        return self.get_variogram_model(gaussFieldName)[keyword]

    def getVariogramType(self, gaussFieldName: GaussianFieldName) -> VariogramType:
        return self.get_variogram_model(gaussFieldName).type

    def getVariogramTypeNumber(self, gaussFieldName: GaussianFieldName) -> int:
        return self.getVariogramType(gaussFieldName).value

    def getMainRange(self, gaussFieldName: GaussianFieldName) -> float:
        return self.__get_property(gaussFieldName, 'MainRange')

    def getMainRangeFmuUpdatable(self, gaussFieldName: GaussianFieldName) -> bool:
        return self.__get_property(gaussFieldName, 'MainRangeFMUUpdatable')

    def getPerpRange(self, gaussFieldName: GaussianFieldName) -> float:
        return self.__get_property(gaussFieldName, 'PerpRange')

    def getPerpRangeFmuUpdatable(self, gaussFieldName: GaussianFieldName):
        return self.__get_property(gaussFieldName, 'PerpRangeFMUUpdatable')

    def getVertRange(self, gaussFieldName: GaussianFieldName) -> float:
        return self.__get_property(gaussFieldName, 'VertRange')

    def getVertRangeFmuUpdatable(self, gaussFieldName: GaussianFieldName) -> bool:
        return self.__get_property(gaussFieldName, 'VertRangeFMUUpdatable')

    def getAzimuthAngle(self, gaussFieldName: GaussianFieldName) -> float:
        return self.__get_property(gaussFieldName, 'AzimuthAngle')

    def getAzimuthAngleFmuUpdatable(self, gaussFieldName: GaussianFieldName) -> bool:
        return self.__get_property(gaussFieldName, 'AzimuthAngleFMUUpdatable')

    def getDipAngle(self, gaussFieldName: GaussianFieldName) -> float:
        return self.__get_property(gaussFieldName, 'DipAngle')

    def getDipAngleFmuUpdatable(self, gaussFieldName: GaussianFieldName) -> bool:
        return self.__get_property(gaussFieldName, 'DipAngleFMUUpdatable')

    def getPower(self, gaussFieldName: GaussianFieldName) -> float:
        return self.__get_property(gaussFieldName, 'Power')

    def getPowerFmuUpdatable(self, gaussFieldName: GaussianFieldName) -> bool:
        return self.__get_property(gaussFieldName, 'PowerFMUUpdatable')

    def getTrendItem(self, gfName: GaussianFieldName) -> Optional[Trend]:
        try:
            return self._gaussian_models[gfName].trend
        except KeyError:
            return None

    def getTrendModel(
        self,
        gfName: GaussianFieldName,
    ) -> Union[
        Tuple[None, None, None, None],
        Tuple[
            bool,
            Union[
                Trend3D_hyperbolic,
                Trend3D_elliptic,
                Trend3D_linear,
                Trend3D_rms_param,
                Trend3D_rms_map,
            ],
            float,
            bool,
        ],
    ]:
        trend = self.getTrendItem(gfName)
        if trend is None:
            return None, None, None, None
        else:
            return (
                trend.use_trend,
                trend.model,
                trend.relative_std_dev.value,
                trend.relative_std_dev.updatable,
            )

    def hasTrendModel(self, gfName: GaussianFieldName) -> bool:
        trend = self.getTrendItem(gfName)
        if trend is None:
            return False
        else:
            return trend.use_trend

    def getTrendModelObject(self, gfName: GaussianFieldName) -> Optional[Trend3D]:
        item = self.getTrendItem(gfName)
        if item is None:
            return None
        else:
            return item.model

    def get_model(self, name: GaussianFieldName) -> Optional[GaussianField]:
        try:
            return self._gaussian_models[name]
        except KeyError:
            return None

    def get_variogram_model(self, name: GaussianFieldName) -> Optional[Variogram]:
        try:
            return self._gaussian_models[name].variogram
        except KeyError:
            return None

    @property
    def debug_level(self) -> Debug:
        return self.__debug_level

    @debug_level.setter
    def debug_level(self, value):
        self.__debug_level = value

    def setVariogramType(
        self, gaussFieldName: GaussianFieldName, variogramType: VariogramType
    ) -> None:
        self.get_variogram_model(gaussFieldName).type = variogramType

    def setMainRange(self, gaussFieldName: GaussianFieldName, range1: float) -> None:
        self.get_variogram_model(gaussFieldName).ranges.main.value = range1

    def setMainRangeFmuUpdatable(
        self, gaussFieldName: GaussianFieldName, value: bool
    ) -> None:
        self.get_variogram_model(gaussFieldName).ranges.main.updatable = value

    def setPerpRange(self, gaussFieldName: GaussianFieldName, range2: float) -> None:
        self.get_variogram_model(gaussFieldName).ranges.perpendicular.value = range2

    def setPerpRangeFmuUpdatable(
        self, gaussFieldName: GaussianFieldName, value: bool
    ) -> None:
        self.get_variogram_model(gaussFieldName).ranges.perpendicular.updatable = value

    def setVertRange(self, gaussFieldName: GaussianFieldName, range3: float) -> None:
        self.get_variogram_model(gaussFieldName).ranges.vertical.value = range3

    def setVertRangeFmuUpdatable(
        self, gaussFieldName: GaussianFieldName, value: bool
    ) -> None:
        self.get_variogram_model(gaussFieldName).ranges.vertical.updatable = value

    def setAzimuthAngle(
        self, gaussFieldName: GaussianFieldName, azimuth: float
    ) -> None:
        self.get_variogram_model(gaussFieldName).angles.azimuth.value = azimuth

    def setAzimuthAngleFmuUpdatable(
        self, gaussFieldName: GaussianFieldName, value: bool
    ) -> None:
        self.get_variogram_model(gaussFieldName).angles.azimuth.updatable = value

    def setDipAngle(self, gaussFieldName: GaussianFieldName, dip: float) -> None:
        self.get_variogram_model(gaussFieldName).angles.dip.value = dip

    def setDipAngleFmuUpdatable(
        self, gaussFieldName: GaussianFieldName, value: bool
    ) -> None:
        self.get_variogram_model(gaussFieldName).angles.dip.updatable = value

    def setPower(self, gaussFieldName: GaussianFieldName, power: float) -> None:
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

    def setSeedForPreviewSimulation(self, gf_name: GaussianFieldName, seed: int) -> int:
        err = 0
        if gf_name in self._gaussian_models:
            self._gaussian_models[gf_name].seed = seed
        else:
            err = 1
        return err

    def updateGaussFieldParam(
        self,
        gf_name: GaussianFieldName,
        variogram_type: VariogramType,
        range1: float,
        range2: float,
        range3: float,
        azimuth: float,
        dip: float,
        power: float,
        range1_fmu_updatable: bool,
        range2_fmu_updatable: bool,
        range3_fmu_updatable: bool,
        azimuth_fmu_updatable: bool,
        dip_fmu_updatable: bool,
        power_fmu_updatable: bool,
        use_trend: bool = False,
        rel_std_dev: float = 0.0,
        rel_std_dev_fmu_updatable: bool = False,
        trend_model_obj: Optional[Trend3D] = None,
    ) -> None:
        # Update or create new gauss field parameter object (with trend)
        if not isVariogramTypeOK(variogram_type):
            raise ValueError(
                f'Error in {self.__class_name} in updateGaussFieldParam\n'
                'Undefined variogram type specified.'
            )
        if any(range < 0 for range in [range1, range2, range3]):
            raise ValueError(
                f'Error in {self.__class_name} in updateGaussFieldParam\n'
                'Correlation range < 0.0'
            )
        if variogram_type == VariogramType.GENERAL_EXPONENTIAL and not (
            1.0 <= power <= 2.0
        ):
            raise ValueError(
                f'Error in {self.__class_name} in updateGaussFieldParam\n'
                'Exponent in GENERAL_EXPONENTIAL variogram is outside [1.0, 2.0]'
            )
        if rel_std_dev < 0.0:
            raise ValueError(
                f'Error in {self.__class_name} in updateGaussFieldParam\n'
                'Relative standard deviation used when trends are specified is negative.'
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
        self._gaussian_models[gf_name].variogram = Variogram.from_definition(
            [
                gf_name,
                variogram_type,
                range1,
                range2,
                range3,
                azimuth,
                dip,
                power,
                range1_fmu_updatable,
                range2_fmu_updatable,
                range3_fmu_updatable,
                azimuth_fmu_updatable,
                dip_fmu_updatable,
                power_fmu_updatable,
            ]
        )
        self._gaussian_models[gf_name].trend = self.create_gauss_field_trend(
            gf_name, use_trend, trend_model_obj, rel_std_dev, rel_std_dev_fmu_updatable
        )

    def updateGaussFieldVariogramParameters(
        self,
        gf_name: str,
        variogram_type,
        range1: float,
        range2: float,
        range3: float,
        azimuth: float,
        dip: float,
        power: float,
        range1_fmu_updatable: bool,
        range2_fmu_updatable: bool,
        range3_fmu_updatable: bool,
        azimuth_fmu_updatable: bool,
        dip_fmu_updatable: bool,
        power_fmu_updatable: bool,
    ) -> int:
        # Update gauss field variogram parameters for existing gauss field model
        # But it does not create new object.
        err = 0
        # Check that gauss field is already defined, then update parameters.
        if gf_name in self._gaussian_models:
            self._gaussian_models[gf_name].variogram = Variogram.from_definition(
                [
                    gf_name,
                    variogram_type,
                    range1,
                    range2,
                    range3,
                    azimuth,
                    dip,
                    power,
                    range1_fmu_updatable,
                    range2_fmu_updatable,
                    range3_fmu_updatable,
                    azimuth_fmu_updatable,
                    dip_fmu_updatable,
                    power_fmu_updatable,
                ]
            )
        else:
            err = 1
        return err

    def removeGaussFieldParam(self, gfName: str) -> None:
        # Remove from dicts
        self._gaussian_models.pop(gfName, None)

    def updateGaussFieldTrendParam(
        self,
        gf_name: GaussianFieldName,
        use_trend: bool,
        trend_model_obj: Trend3D,
        rel_std_dev: Number,
        rel_std_dev_fmu_updatable: bool,
    ) -> int:
        # Update trend parameters for existing trend for gauss field model
        # But it does not create new trend object.
        err = 0
        if trend_model_obj is not None and gf_name in self._gaussian_models:
            self._gaussian_models[gf_name].trend = Trend(
                name=gf_name,
                use_trend=use_trend,
                model=trend_model_obj,
                relative_std_dev=FmuProperty(rel_std_dev, rel_std_dev_fmu_updatable),
            )
        else:
            # This gauss field was not found.
            err = 1
        return err

    @staticmethod
    def create_gauss_field_trend(
        gf_name: GaussianFieldName,
        use_trend: bool,
        trend_model_obj: Trend3D,
        rel_std_dev: float,
        rel_std_dev_fmu_updatable: bool,
    ) -> Trend:
        return Trend(
            name=gf_name,
            use_trend=use_trend,
            model=trend_model_obj,
            relative_std_dev=FmuProperty(rel_std_dev, rel_std_dev_fmu_updatable),
        )

    def XMLAddElement(
        self,
        parent: Element,
        zone_number: int,
        region_number: int,
        fmu_attributes: List[FmuAttribute],
    ) -> None:
        if self.debug_level >= Debug.VERY_VERY_VERBOSE:
            print(f'--- call XMLADDElement from {self.__class_name}')

        # Add child command GaussField
        for grf in self._gaussian_models.values():
            gf_name = grf.name
            variogram = grf.variogram
            variogram_type = variogram.type

            if gf_name != grf.variogram.name or gf_name != grf.trend.name:
                raise ValueError(
                    'Error in class: ' + self.__class_name + ' in XMLAddElement'
                )
            trend = grf.trend
            use_trend = trend.use_trend
            trend_obj = trend.model

            tag = 'GaussField'
            attribute = {'name': gf_name}
            elem = Element(tag, attribute)
            parent.append(elem)
            gf_element = elem

            tag = 'Vario'
            attribute = {
                'name': variogram_type
                if isinstance(variogram_type, str)
                else variogram_type.name
            }
            elem = Element(tag, attribute)
            gf_element.append(elem)
            variogram_element = elem

            properties = ['main', 'perpendicular', 'vertical', 'azimuth', 'dip']

            for prop in properties:
                self._add_xml_element(
                    grf,
                    prop,
                    parent,
                    variogram_element,
                    fmu_attributes,
                    createFMUvariableNameForResidual,
                )

            if variogram_type in [
                'GENERAL_EXPONENTIAL',
                VariogramType.GENERAL_EXPONENTIAL,
            ]:
                self._add_xml_element(
                    grf,
                    'power',
                    parent,
                    variogram_element,
                    fmu_attributes,
                    createFMUvariableNameForResidual,
                )

            if use_trend:
                # Add trend
                trend_obj.XMLAddElement(
                    gf_element, zone_number, region_number, gf_name, fmu_attributes
                )

                self._add_xml_element(
                    grf,
                    'relative_std_dev',
                    parent,
                    gf_element,
                    fmu_attributes,
                    createFMUvariableNameForTrend,
                )

            tag = 'SeedForPreview'
            elem = Element(tag)
            seed = grf.seed
            elem.text = ' ' + str(seed) + ' '
            gf_element.append(elem)

    def _add_xml_element(
        self,
        grf: GaussianField,
        property_name: str,
        parent: Element,
        xml_element: Element,
        fmu_attributes: List[FmuAttribute],
        create_fmu_variable: Callable,
    ) -> None:
        zone_number = parent.get('number')
        region_number = parent.get('regionNumber')
        tag = self.__xml_keyword[property_name]
        value = grf[property_name]
        elem = Element(tag)
        elem.text = ' ' + str(value) + ' '
        if isinstance(value, FmuProperty) and value.updatable:
            fmu_attribute = create_fmu_variable(
                tag, grf.name, zone_number, region_number
            )
            fmu_attributes.append(FmuAttribute(fmu_attribute, value.value))
            elem.attrib = dict(kw=fmu_attribute)
        xml_element.append(elem)

    def simGaussFieldWithTrendAndTransform(
        self,
        simulation_box_size: SimulationBoxSize,
        grid_size: GridSize,
        grid_azimuth: float,
        cross_section: CrossSection,
        simulation_box_origin,
    ) -> List[GaussianField]:
        """
        This function is used to create 2D simulation of horizontal or vertical cross sections.
        The gauss simulation is 2D and the correlation ellipsoid for the 3D variogram is projected into the
        specified cross section in 2D. The 3D trend definition is used to calculate an 2D cross section of the trend
        in the specified horizontal or vertical cross section grid plane specified by cross_section.relative_position,
        which is a number between 0 and 1. Here 0 means 'smallest' grid index, and 1 means 'largest' grid index for
        the specified cross section direction (IJ plane, IK, plane or JK plane).
        The trend and residual gauss field is added using the specified relative standard deviation and the resulting
        gaussian field with trend is transformed by empiric transformation such that the histogram over
        all simulated values in the 2D grid become uniform between 0 and 1.
        """

        return [
            grf.simulate(
                cross_section,
                grid_azimuth,
                grid_size,
                simulation_box_size,
                simulation_box_origin,
                self.debug_level,
            )
            for grf in self._gaussian_models.values()
        ]

    def calc2DVariogramFrom3DVariogram(
        self,
        name: GaussianFieldName,
        grid_azimuth: float,
        projection: str,
    ) -> Tuple[float64, float64, float64, float64]:
        return self._gaussian_models[
            name
        ].variogram.calc_2d_variogram_from_3d_variogram(
            grid_azimuth,
            projection,
            self.debug_level,
        )


def _get_projection_parameters(
    cross_section_type: CrossSectionType,
    grid_size: GridSize,
    simulation_box_size: SimulationBoxSize,
    resize_for_gui: bool = True,
) -> Tuple[Tuple[int, int], Tuple[float, float], str]:
    x_sim_box_size, y_sim_box_size, z_sim_box_size = simulation_box_size
    x_grid, y_grid, z_grid = grid_size
    if cross_section_type == CrossSectionType.IJ:
        grid_dimensions_2d = (x_grid, y_grid)
        size = (x_sim_box_size, y_sim_box_size)
        projection = 'xy'
    elif cross_section_type == CrossSectionType.IK:
        grid_dimensions_2d = (x_grid, z_grid)
        size = (x_sim_box_size, z_sim_box_size)
        projection = 'xz'
    elif cross_section_type == CrossSectionType.JK:
        grid_dimensions_2d = (y_grid, z_grid)
        size = (y_sim_box_size, z_sim_box_size)
        projection = 'yz'
    else:
        raise ValueError('Undefined cross section {}'.format(cross_section_type.name))
    return grid_dimensions_2d, size, projection


def _add_trend(
    residual_field,
    trend_field,
    rel_sigma,
    trend_max_min_difference,
    average_trend,
    debug_level=Debug.OFF,
):
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
        print(f'---  Relative standard deviation = {rel_sigma}')
        print(
            f'---  Difference between max value and min value of trend = {trend_max_min_difference}'
        )
        print(f'---  Calculated standard deviation = {sigma}')
        print('')
    n = len(trend_field)
    if n != len(residual_field):
        raise IOError(
            'Internal error: Mismatch between size of trend field and residual field in _addTrend'
        )

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
        print(
            '---  Transform 2D Gauss field by empiric transformation to uniform distribution\n'
        )

    n = len(values)
    transformed = np.zeros(n, np.float32)
    sort_index = np.argsort(values)

    u_vec = np.arange(0, n, 1, dtype=np.float32) / n
    transformed[sort_index] = u_vec

    return transformed


def _calculate_projection(U, debug_level=Debug.OFF):
    func_name = _calculate_projection.__name__
    if debug_level >= Debug.VERY_VERY_VERBOSE:
        print('--- U:')
        print(U)
    w, v = np.linalg.eigh(U)
    if debug_level >= Debug.VERY_VERY_VERBOSE:
        print('--- Eigenvalues:')
        print(w)
        print('--- Eigenvectors')
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
        print(
            f'--- Function: {func_name} Direction (angle): {angle1} for range: {range1}'
        )

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
        print(
            f'--- Function: {func_name} Direction (angle): {angle2} for range: {range2}'
        )

    # Angles are azimuth angles
    return angle1, range1, angle2, range2
