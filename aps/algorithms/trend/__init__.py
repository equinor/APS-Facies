#!/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2017 Statoil ASA
#
# Class for Trends used in APS modelling
# Subclass for each trend type
#  - linear
#  - elliptic
#  - hyperbolic
#  - RMSParameter
#
####################################################################
# Kari B. Skjerve, karbor@equinor.com
# Oddvar Lia, olia@equinor.com
# 2017/2018
####################################################################

import math
from typing import Union, List, Tuple, Optional, Dict, Any
from xml.etree.ElementTree import Element

import numpy as np

from aps.algorithms.properties import (
    make_angle_property,
    FmuProperty,
    make_lower_bounded_property,
    make_ranged_property,
    CrossSection,
)
from aps.utils.constants.simple import (
    Debug,
    OriginType,
    TrendType,
    CrossSectionType,
    Direction,
    TrendParameter,
    GridModelConstants,
)

from aps.utils.containers import FmuAttribute
from aps.utils.types import (
    Point3D,
    SimulationBoxOrigin,
    GaussianFieldName,
    HyperbolicTrendParameters,
)
from aps.utils.xmlUtils import (
    getIntCommand,
    getTextCommand,
    createFMUvariableNameForTrend,
    fmu_xml_element,
    get_fmu_value_from_xml,
    get_origin_type_from_model_file,
)


def required_parameters(_type: TrendType) -> List[TrendParameter]:
    # TODO: Remove?
    none = []
    rms_parameter = none + [TrendParameter.RMS_PARAMETER]
    rms_trendmap = none + [
        TrendParameter.RMS_TREND_MAP_NAME,
        TrendParameter.RMS_TREND_MAP_ZONE,
    ]
    linear = none + [
        TrendParameter.AZIMUTH,
        TrendParameter.STACKING,
        TrendParameter.DIRECTION,
    ]
    elliptic = linear + [
        TrendParameter.CURVATURE,
        TrendParameter.ORIGIN,
        TrendParameter.ORIGIN_TYPE,
    ]
    hyperbolic = elliptic + [TrendParameter.MIGRATION]
    elliptic_cone = hyperbolic + [TrendParameter.RELATIVE_SIZE]
    requirements = {
        TrendType.NONE: none,
        TrendType.RMS_PARAM: rms_parameter,
        TrendType.RMS_TRENDMAP: rms_trendmap,
        TrendType.LINEAR: linear,
        TrendType.ELLIPTIC: elliptic,
        TrendType.HYPERBOLIC: hyperbolic,
        TrendType.ELLIPTIC_CONE: elliptic_cone,
    }
    return requirements[_type]


class Trend3D:
    """
    Description: Parent class for Trend3D
    The following functions must be specified for the sub classes:
    _calcParam(self)
    _writeTrendSpecificParam(self)
    _trendValueCalculation(self, parametersForTrendCalc, x, y, k, zinc)
    """

    def __init__(
        self,
        azimuth_angle: float = 0.0,
        azimuth_angle_fmu_updatable: bool = False,
        stacking_angle: float = 0.0001,
        stacking_angle_fmu_updatable: bool = False,
        direction: Direction = Direction.PROGRADING,
        debug_level: Debug = Debug.OFF,
        **kwargs,
    ):
        """
        Initialize common parameters for all methods implemented in sub classes.
        These parameters will be defined in sub classes
        """
        # Depositional direction
        azimuth_angle_update = azimuth_angle % 360.0
        self.azimuth = FmuProperty(azimuth_angle_update, azimuth_angle_fmu_updatable)
        # Angle between facies
        self.stacking_angle = FmuProperty(stacking_angle, stacking_angle_fmu_updatable)
        # Direction of stacking (prograding/retrograding)
        self.stacking_direction = direction

        self._debug_level = debug_level
        self._sim_box_azimuth = None

        if self._debug_level >= Debug.VERY_VERBOSE:
            print('--- Trend:')
            print(f'--- Azimuth:        {self.azimuth.value}')
            print(f'--- Stacking angle: {self.stacking_angle.value}')
            print(f'--- Stacking type:  {self.stacking_direction.value}')

        # Position of a reference point for the trend function.
        # This is in global coordinates for (x, y) and relative to simulation box for the zone for z coordinate.
        self._x_center = 0.0
        self._y_center = 0.0
        self._z_center = 0.0
        self._x_sim_box = 0.0
        self._y_sim_box = 0.0
        self._z_sim_box = 0.0
        self._start_layer = -1
        self._end_layer = -1

        self._x_center_in_sim_box_coordinates = 0.0
        self._y_center_in_sim_box_coordinates = 0.0
        self._z_center_in_sim_box_coordinates = 0.0

    @classmethod
    def from_xml(
        cls,
        trend_rule_xml: Element,
        model_file_name: Optional[str] = None,
        debug_level: Debug = Debug.OFF,
    ) -> 'Trend3D':
        """Read common parameters from xml tree for all trend types"""
        azimuth, is_azimuth_fmu_updatable = get_fmu_value_from_xml(
            trend_rule_xml, 'azimuth', modelFile=model_file_name
        )
        stacking_angle, is_stack_angle_fmu_updatable = get_fmu_value_from_xml(
            trend_rule_xml,
            'stackAngle',
            modelFile=model_file_name,
        )
        stacking_direction = getIntCommand(
            trend_rule_xml, 'directionStacking', modelFile=model_file_name
        )
        if debug_level >= Debug.VERY_VERBOSE:
            print(f'--- Trend parameters:')
            print(f'---   Azimuth:        {azimuth}')
            print(f'---   Stacking angle: {stacking_angle}')
            print(f'---   Stacking type:  {stacking_direction}')

        return cls(
            azimuth_angle=azimuth,
            azimuth_angle_fmu_updatable=is_azimuth_fmu_updatable,
            stacking_angle=stacking_angle,
            stacking_angle_fmu_updatable=is_stack_angle_fmu_updatable,
            direction=Direction(stacking_direction),
            debug_level=debug_level,
        )

    def XMLAddElement(
        self,
        parent: Element,
        zone_number: int,
        region_number: int,
        gf_name: GaussianFieldName,
        fmu_attributes: List[FmuAttribute],
    ) -> None:
        raise NotImplementedError

    def _XMLAddElementTag(
        self,
        trend_element: Element,
        zone_number: Union[int, str],
        region_number: Optional[Union[str, int]],
        gf_name: str,
        fmu_attributes: List[FmuAttribute],
    ) -> None:
        def add_tag(tag: str, value: Union[FmuProperty, Direction]):
            obj = Element(tag)
            obj.text = f' {value} '
            if isinstance(value, FmuProperty) and value.updatable:
                fmu_attribute = createFMUvariableNameForTrend(
                    tag, gf_name, zone_number, region_number
                )
                fmu_attributes.append(FmuAttribute(fmu_attribute, value.value))
                obj.attrib = dict(kw=fmu_attribute)
            trend_element.append(obj)

        add_tag(tag='azimuth', value=self.azimuth)
        add_tag(tag='directionStacking', value=self.stacking_direction)
        add_tag(tag='stackAngle', value=self.stacking_angle)

    azimuth: FmuProperty[float] = make_angle_property(
        'azimuth', full_name='depositional_direction'
    )

    stacking_angle: FmuProperty[float] = make_angle_property('stacking_angle')

    @property
    def stacking_direction(self) -> Direction:
        return self._direction

    @stacking_direction.setter
    def stacking_direction(self, direction):
        if not isinstance(direction, Direction):
            direction = Direction(direction)
        if direction not in Direction:
            raise ValueError(
                f'Error in {self._class_name}\n'
                'Error: Cannot set stacking type to be a number different from -1 and 1.'
            )
        else:
            self._direction = direction

    @property
    def type(self) -> TrendType:
        return TrendType.NONE

    @property
    def _class_name(self) -> str:
        return self.__class__.__name__

    def setAzimuthFmuUpdatable(self, value):
        self.azimuth.updatable = value

    def setStackingAngleFmuUpdatable(self, value):
        self.stacking_angle.updatable = value

    def _setTrendCenter(
        self,
        x0: float,
        y0: float,
        azimuth_angle: float,
        sim_box_x_length: float,
        sim_box_y_length: float,
        sim_box_thickness: float,
        origin_type: Optional[OriginType] = None,
        origin: Optional[Union[Point3D, 'Point3DProperty']] = None,
    ) -> None:
        aA = azimuth_angle * math.pi / 180.0
        if isinstance(origin, Point3DProperty):
            origin = origin.as_point()
        if origin is None or origin_type is None:
            x_center, y_center = x0, y0
            z_center = 0.0  # Top of zone
            self._x_center_in_sim_box_coordinates = 0.0
            self._y_center_in_sim_box_coordinates = 0.0
            self._z_center_in_sim_box_coordinates = 0.0

        elif origin_type == OriginType.RELATIVE:
            # Calculate the global coordinate for x and y for the center point and z coordinate relative to simulation box
            x_center = (
                x0
                + origin[0] * sim_box_x_length * math.cos(aA)
                + origin[1] * sim_box_y_length * math.sin(aA)
            )
            y_center = (
                y0
                - origin[0] * sim_box_x_length * math.sin(aA)
                + origin[1] * sim_box_y_length * math.cos(aA)
            )
            z_center = origin[2] * sim_box_thickness
            self._x_center_in_sim_box_coordinates = origin[0] * sim_box_x_length
            self._y_center_in_sim_box_coordinates = origin[1] * sim_box_y_length
            self._z_center_in_sim_box_coordinates = z_center

        elif origin_type == OriginType.ABSOLUTE:
            x_center, y_center = origin[0], origin[1]
            z_center = origin[2] * sim_box_thickness
            dx = origin[0] - x0
            dy = origin[1] - y0
            self._x_center_in_sim_box_coordinates = dx * math.cos(aA) - dy * math.sin(
                aA
            )
            self._y_center_in_sim_box_coordinates = dx * math.sin(aA) + dy * math.cos(
                aA
            )
            self._z_center_in_sim_box_coordinates = z_center
        else:
            raise ValueError(
                'In {}\nOrigin type must be either {} or {}.'.format(
                    self._class_name, OriginType.RELATIVE.name, OriginType.ABSOLUTE.name
                )
            )
        self._x_center = x_center
        self._y_center = y_center
        self._z_center = z_center
        self._x_sim_box = sim_box_x_length
        self._y_sim_box = sim_box_y_length
        self._z_sim_box = sim_box_thickness

    def as_dict(self) -> Dict[str, Any]:
        return dict(
            azimuth_angle=self.azimuth.value,
            azimuth_angle_fmu_updatable=self.azimuth.updatable,
            stacking_angle=self.stacking_angle.value,
            stacking_angle_fmu_updatable=self.stacking_angle.updatable,
            direction=self.stacking_direction,
            debug_level=self._debug_level,
        )

    def _calculateTrendModelParam(self, use_relative_azimuth: bool = False):
        raise NotImplementedError(
            'Can not use: {} object as a trend object. Use sub classes of this as trend'.format(
                self._class_name
            )
        )

    def _writeTrendSpecificParam(self) -> None:
        raise NotImplementedError(
            'Can not use: {} object as a trend object. Use sub classes of this as trend'.format(
                self._class_name
            )
        )

    def _trendValueCalculation(self, parameters_for_trend_calc, x, y, k, zinc):
        raise NotImplementedError(
            'Can not use: {} object as a trend object. Use sub classes of this as trend'.format(
                self._class_name
            )
        )

    def _trendValueCalculationSimBox(
        self, parameters_for_trend_calc: tuple, i, j, k, xinc, yinc, zinc
    ):
        raise NotImplementedError(
            'Can not use: {} object as a trend object. Use sub classes of this as trend'.format(
                self._class_name
            )
        )

    def createTrend(
        self,
        grid_model,
        realization_number,
        cell_index_defined,
        zone_number,
        sim_box_thickness,
        project=None,
        keep_temporary_trend_param=False,
        debug_level=Debug.OFF,
    ):
        """
        Description: Create trend values for 3D grid zone using Roxar API.
                     The trend is calculated in simulation box.
        """
        from aps.utils.roxar.grid_model import GridSimBoxSize

        # Check if specified grid model exists and is not empty
        if grid_model.is_empty(realization_number):
            raise ValueError(
                f'Error: Specified grid model: {grid_model.name} is empty'
                f'       for realization {realization_number}.'
            )

        # Using simbox indexer
        grid_3d = grid_model.get_grid(realization_number)
        grid_indexer = grid_3d.simbox_indexer
        (nx, ny, nz) = grid_indexer.dimensions

        sim_box_attributes = GridSimBoxSize(grid_3d)
        self._sim_box_azimuth = sim_box_attributes.azimuth_angle

        # Define self._x_center, self._y_center for the trend
        self._setTrendCenter(
            sim_box_attributes.x0,
            sim_box_attributes.y0,
            sim_box_attributes.azimuth_angle,
            sim_box_attributes.x_length,
            sim_box_attributes.y_length,
            sim_box_thickness,
        )
        # For the selected and active cell numbers defined by cell_index_defined
        # get the cell center points and the ijk indices in simbox indexing system.
        # Cell center points are in real coordinates, not simbox coordinates.
        # This is OK in FMU mode since the ERTBOX is used, and is OK for grid
        # that does not have dual grid indexing. The only case where grid cell position
        # is calculated explicitly in simbox is when running without FMU AHM mode
        # and the grid has reverse staircase faults (dual index system).
        cell_center_points = None
        ijk_cell_indices = grid_indexer.get_indices(cell_index_defined)
        if grid_3d.has_dual_index_system:
            # Do not use cell center points (since they come from the real grid)
            # but use x,y coordinates from simulation box coordinate system
            cell_center_points = sim_box_attributes.calculate_cell_center_points(
                ijk_cell_indices
            )
        else:
            cell_center_points = grid_3d.get_cell_centers(cell_index_defined)

        zonation = grid_indexer.zonation
        layer_ranges = zonation[zone_number - 1]
        # In simbox there is only one interval of layers per zone and they
        # come after each other and layer numbering increases downwards
        start_layer = np.infty
        end_layer = -np.infty
        for layer in layer_ranges:
            if start_layer > layer[0]:
                start_layer = layer[0]
            if end_layer < layer[-1]:
                end_layer = layer[-1]

        # Set start and end layer for this zone
        self._start_layer = start_layer
        self._end_layer = end_layer
        num_layers_in_zone = sum(len(layer) for layer in layer_ranges)
        zinc = sim_box_thickness / num_layers_in_zone
        if debug_level >= Debug.VERY_VERBOSE:
            print(f'---  In {self._class_name}')
            print(f'---  Zone number: {zone_number}')
            print(f'---  Grid model: {grid_model.name}')
            print(f'---  SimboxThickness: {sim_box_thickness}')
            print(f'---  Zinc: {zinc}')
            print(f'---  Simbox dimensions nx,ny,nz: {nx}, {ny}, {nz}')
            print(f'---  Start simbox layer in zone: {start_layer + 1}')
            print(f'---  End   simbox layer in zone: {end_layer + 1}')
            print(f'---  Trend type: {self.type.name}')

            if self.type not in [TrendType.RMS_PARAM, TrendType.RMS_TRENDMAP]:
                print(f'---  Trend azimuth: {self.azimuth.value}')
                print(f'---  StackingAngle: {self.stacking_angle.value}')
                print(f'---  Direction: {self.stacking_direction.value}')
                print(f'---  x_center: {self._x_center}')
                print(f'---  y_center: {self._y_center}')
                print(f'---  z_center (sim box): {self._z_center}')

            self._writeTrendSpecificParam()

            # Create an empty array with 0 values with correct length
            # corresponding to all active cells in the grid

        if isinstance(self, Trend3D_rms_param):
            from aps.utils.roxar.grid_model import getContinuous3DParameterValues

            if debug_level >= Debug.VERBOSE:
                print(
                    f'-- RMS 3D parameter: {self.trend_parameter_name}\n'
                    '-- No preview is implemented for this yet.'
                )
            # Values for all active cells
            values_in_active_cells = getContinuous3DParameterValues(
                grid_model, self.trend_parameter_name, realization_number
            )
            # Values for selected cells (using numpy vectors)
            values_in_selected_cells = values_in_active_cells[cell_index_defined]
            # If the user defined trend is constant, change one grid cell value to ensure it is not
            # constant to avoid errors later.
            if len(values_in_selected_cells) > 0:
                if np.ptp(values_in_selected_cells) < 0.000001:
                    values_in_selected_cells[0] += 1.0
        elif isinstance(self, Trend3D_rms_map):
            from aps.utils.roxar.sample_map_to_grid import (
                trend_map_to_grid_param,
                check_existence_of_map,
            )
            from aps.utils.roxar.grid_model import getContinuous3DParameterValues

            if not check_existence_of_map(
                project, self.trend_map_zone, self.trend_map_name
            ):
                raise IOError(
                    f'Specified 2D trend map:  zone name: {self.trend_map_zone} surface type: {self.trend_map_name}\n'
                    ' does not exist or is empty.  Check the trend specification for trend of type RMS_TRENDMAP'
                )
            if debug_level >= Debug.VERBOSE:
                print(f'-- RMS 2D trend map from zone: {self.trend_map_zone}')
                print(f'-- Representation or type: {self.trend_map_name}')
                print('-- No preview is implemented for this yet.')

            # Create 3D parameter from 2D trend map
            trend_param_name = 'tmp_' + self.trend_map_zone + '_' + self.trend_map_name
            trend_map_to_grid_param(
                project,
                grid_model.name,
                self.trend_map_name,
                self.trend_map_zone,
                trend_param_name,
                zone_number=zone_number,
                debug_level=debug_level,
            )

            # Values for all active cells
            values_in_active_cells = getContinuous3DParameterValues(
                grid_model,
                trend_param_name,
                realization_number,
            )
            # Values for selected cells (using numpy vectors)
            values_in_selected_cells = values_in_active_cells[cell_index_defined]
            # If the user defined trend is constant, change one grid cell value to ensure it is not
            # constant to avoid errors later.
            if np.ptp(values_in_selected_cells) < 0.000001:
                values_in_selected_cells[0] += 1.0
            if not keep_temporary_trend_param:
                del grid_model.properties[trend_param_name]
        else:
            num_defined_cells = len(cell_index_defined)
            values_in_selected_cells = np.zeros(num_defined_cells, np.float32)
            parameters_for_trend_calc = self._calculateTrendModelParam()
            index_vector = np.arange(num_defined_cells)
            x_vec = cell_center_points[index_vector, 0]
            y_vec = cell_center_points[index_vector, 1]
            k_vec = ijk_cell_indices[index_vector, 2]
            values_in_selected_cells = self._trendValueCalculation_vectorized(
                parameters_for_trend_calc, x_vec, y_vec, k_vec, zinc
            )
        if len(values_in_selected_cells) > 0:
            min_value = values_in_selected_cells.min()
            max_value = values_in_selected_cells.max()
            minmax_difference = max_value - min_value
            values_rescaled = (values_in_selected_cells - min_value) / minmax_difference

            min_value = values_rescaled.min()
            max_value = values_rescaled.max()
            minmax_difference = max_value - min_value
        else:
            raise ValueError(f'Trend has no active cells')
        return minmax_difference, values_rescaled

    def createTrendFor2DProjection(
        self,
        sim_box_size,
        azimuth_sim_box: float,
        preview_size,
        cross_section: CrossSection,
        sim_box_origin: SimulationBoxOrigin,
    ) -> Tuple[np.float64, np.float64, np.ndarray]:
        if self.type in [TrendType.RMS_PARAM, TrendType.NONE, TrendType.RMS_TRENDMAP]:
            raise NotImplementedError(
                'Preview of Trend of type RMS_PARAM, RMS_TRENDMAP or NONE is not implemented'
            )
        sim_box_x_size, sim_box_y_size, sim_box_z_size = sim_box_size
        nx_preview, ny_preview, nz_preview = preview_size
        projection_type = cross_section.type
        cross_section_relative_pos = cross_section.relative_position
        sim_box_x_origin, sim_box_y_origin = sim_box_origin

        # Define relative azimuth relative to y axis in simulation box coordinates
        self._relative_azimuth = self.azimuth.value - azimuth_sim_box

        # Define self._x_center, self._y_center for the trend
        self._setTrendCenter(
            sim_box_x_origin,
            sim_box_y_origin,
            azimuth_sim_box,
            sim_box_x_size,
            sim_box_y_size,
            sim_box_z_size,
        )

        if self._debug_level >= Debug.VERY_VERBOSE:
            print(f'---  Trend type: {self.type.name}')
            if self.type not in [TrendType.RMS_PARAM, TrendType.RMS_TRENDMAP]:
                print(f'---  Trend azimuth:      {self.azimuth.value}')
                print(f'---  StackingAngle:      {self.stacking_angle.value}')
                print(f'---  Direction:          {self.stacking_direction.value}')
                print(
                    f'---  x_center (sim box): {self._x_center_in_sim_box_coordinates}'
                )
                print(
                    f'---  y_center (sim box): {self._y_center_in_sim_box_coordinates}'
                )
                print(
                    f'---  z_center (sim box): {self._z_center_in_sim_box_coordinates}'
                )
                print(f'---  Projection type:    {projection_type}')
                print(f'---  nx_preview:         {nx_preview}')
                print(f'---  ny_preview:         {ny_preview}')
                print(f'---  nz_preview:         {nz_preview}')

            self._writeTrendSpecificParam()

        # Calculate parameters used in the trend function.
        # Use simulation box coordinates and azimuth must be relative to simulation box
        parameters_for_trend_calc = self._calculateTrendModelParam(
            use_relative_azimuth=True
        )
        xinc = sim_box_x_size / nx_preview
        yinc = sim_box_y_size / ny_preview
        zinc = sim_box_z_size / nz_preview
        # Note: Save trend values for the 2D fields in 1D numpy vector in 'C' sequence
        if projection_type == CrossSectionType.IJ:
            ndim1 = nx_preview
            ndim2 = ny_preview
            k = int(cross_section_relative_pos * (nz_preview - 1))
            values = np.zeros(nx_preview * ny_preview, np.float32)
            # values(i,j) as 1D vector
            for j in range(ny_preview):
                for i in range(nx_preview):
                    indx = (
                        i + j * nx_preview
                    )  # Index for 2D matrix where j is row and i is column
                    trendValue = self._trendValueCalculationSimBox(
                        parameters_for_trend_calc, i, j, k, xinc, yinc, zinc
                    )
                    values[indx] = trendValue

        elif projection_type == CrossSectionType.IK:
            ndim1 = nx_preview
            ndim2 = nz_preview
            j = int(cross_section_relative_pos * (ny_preview - 1))
            values = np.zeros(nx_preview * nz_preview, np.float32)
            # values(i,k) as 1D vector
            for k in range(nz_preview):
                for i in range(nx_preview):
                    indx = (
                        i + k * nx_preview
                    )  # Index for 2D matrix where k is row and i is column index
                    trendValue = self._trendValueCalculationSimBox(
                        parameters_for_trend_calc, i, j, k, xinc, yinc, zinc
                    )
                    values[indx] = trendValue

        elif projection_type == CrossSectionType.JK:
            ndim1 = ny_preview
            ndim2 = nz_preview
            i = int(cross_section_relative_pos * (nx_preview - 1))
            values = np.zeros(ny_preview * nz_preview, np.float32)
            # values(j,k) as 1D vector
            for k in range(nz_preview):
                for j in range(ny_preview):
                    indx = (
                        j + k * ny_preview
                    )  # Index for 2D matrix where k is row and j is column index
                    trendValue = self._trendValueCalculationSimBox(
                        parameters_for_trend_calc, i, j, k, xinc, yinc, zinc
                    )
                    values[indx] = trendValue
        else:
            raise ValueError("Invalid projection type. Must be one of 'IJ', 'IK', 'JK'")

        # Estimate an approximate min and max trend value from the zone by evaluating the trend in a small subset of points
        # Calculate trends for every n'th grid cell location in all three directions
        # Note it is important that this is done over the whole 3D simbox volume and not over only the specified cross section
        # so that the actual standard deviation is comparable with the 3D simulation
        nxstep = max(int(nx_preview / 5), 1)
        nystep = max(int(ny_preview / 5), 1)
        nzstep = max(int(nz_preview / 5), 1)
        max_value = -999999999
        min_value = 99999999
        nvalues = 0
        sum_values = 0.0
        for k in range(0, nz_preview, nzstep):
            for j in range(0, ny_preview, nystep):
                for i in range(0, nx_preview, nxstep):
                    trend_value = self._trendValueCalculationSimBox(
                        parameters_for_trend_calc, i, j, k, xinc, yinc, zinc
                    )
                    if max_value < trend_value:
                        max_value = trend_value
                    if min_value > trend_value:
                        min_value = trend_value
                    sum_values = sum_values + trendValue
                    nvalues += 1

        average_trend = sum_values / nvalues

        minmax_difference = max_value - min_value
        if abs(average_trend) > 0.00001:
            if abs(minmax_difference / average_trend) < 0.0001:
                values_rescaled = np.ones(ndim1 * ndim2, float)
                average_trend = 1.0
            else:
                values_rescaled = (values - min_value) / minmax_difference
        else:
            if abs(minmax_difference) < 0.00001:
                values_rescaled = np.ones(ndim1 * ndim2, float)
                average_trend = 1.0
            else:
                values_rescaled = (values - min_value) / minmax_difference
        min_value_rescaled = values_rescaled.min()
        max_value_rescaled = values_rescaled.max()
        minmax_difference = max_value_rescaled - min_value_rescaled
        if self._debug_level >= Debug.VERY_VERBOSE:
            print(
                f'--- Approximate estimate of min value of trend within simBox before rescaling: {min_value}'
            )
            print(
                f'--- Approximate estimate of max value of trend within simBox before rescaling: {max_value}'
            )
            print(
                f'--- Difference between max and min value within simBox after rescaling: {minmax_difference}'
            )

        return minmax_difference, average_trend, values_rescaled


# ----------------------------------------------------------------------------------------------------------


class Trend3D_linear(Trend3D):
    """
    Description: Create a linear trend 3D object
    Input is model parameters.
    """

    def __init__(
        self,
        azimuth_angle: float = 0.0,
        azimuth_angle_fmu_updatable: bool = False,
        stacking_angle: float = 0.0001,
        stacking_angle_fmu_updatable: bool = False,
        direction: Direction = Direction.PROGRADING,
        debug_level: Debug = Debug.OFF,
        **kwargs,
    ):
        super().__init__(
            azimuth_angle,
            azimuth_angle_fmu_updatable,
            stacking_angle,
            stacking_angle_fmu_updatable,
            direction,
            debug_level,
            **kwargs,
        )
        # Add additional for current trend type here

    @property
    def type(self) -> TrendType:
        return TrendType.LINEAR

    @classmethod
    def from_xml(
        cls,
        trend_rule_xml: Element,
        model_file_name: Optional[str] = None,
        debug_level: Debug = Debug.OFF,
    ) -> 'Trend3D_linear':
        return super().from_xml(trend_rule_xml, model_file_name, debug_level)
        # Additional input parameters comes here (for other Trend3D-types)

    def XMLAddElement(
        self,
        parent: Element,
        zone_number: int,
        region_number: int,
        gf_name: GaussianFieldName,
        fmu_attributes: List[FmuAttribute],
    ) -> None:
        # Add to the parent element a new element with specified tag and attributes.
        # The attributes are a dictionary with {name:value}
        # After this function is called, the parent element has got a new child element
        # for the current class.
        if self._debug_level >= Debug.VERY_VERBOSE:
            print(f'--- call XMLADDElement from {self._class_name}')

        trend_element = Element('Trend')
        parent.append(trend_element)
        linear_3d_element = Element('Linear3D')
        trend_element.append(linear_3d_element)
        super()._XMLAddElementTag(
            linear_3d_element, zone_number, region_number, gf_name, fmu_attributes
        )

    def _setTrendCenter(
        self,
        x0,
        y0,
        azimuth_angle,
        sim_box_x_length,
        sim_box_y_length,
        sim_box_thickness,
        origin_type=None,
        origin=None,
    ):
        # Reference point in simulation box coordinates (midpoint of the box)
        self._x_center = x0
        self._y_center = y0
        self._z_center = sim_box_thickness / 2.0

        # For linear trend, the reference point (xCenter, yCenter, zCenter) is actually irrelevant
        # and is chosen to be in the middle of simulation box
        self._x_center_in_sim_box_coordinates = 0.5
        self._y_center_in_sim_box_coordinates = 0.5
        self._z_center_in_sim_box_coordinates = 0.5

    def _calculateTrendModelParam(
        self, use_relative_azimuth: bool = False
    ) -> Tuple[float, float, float]:
        """
        Calculate normal vector to iso-surfaces (planes) for constant trend values
        a*(x-x0)+b*(y-y0)+c*(z-z0) = K where K is a constant is such
        an iso surface and [a,b,c] is the normal vector to the plane.
        """
        # Calculate the 3D linear trend parameters
        # Note that the coordinate system is left handed with z axis down, x from West to East and y axis from South to North
        # Positive stacking angle means the angle is 90 + stacking_angle relative to z axis
        alpha = self.stacking_angle.value * np.pi / 180.0
        if use_relative_azimuth:
            azimuth = self._relative_azimuth
        else:
            azimuth = self.azimuth.value

        if self.stacking_direction == Direction.PROGRADING:
            theta = azimuth * np.pi / 180.0
        else:
            theta = (azimuth + 180.0) * np.pi / 180.0

        # Normal vector to a plane with constant trend value is [xComponent,yComponent,zComponent]
        if abs(self.stacking_angle) < 0.001:
            x_component = 0.0
            y_component = 0.0
            z_component = 1.0
        else:
            x_component = math.sin(alpha) * math.sin(theta)
            y_component = math.sin(alpha) * math.cos(theta)
            z_component = math.cos(alpha)
        if self.stacking_direction == Direction.RETROGRADING:
            # Change sign of normal vector (The gradient)
            x_component = -x_component
            y_component = -y_component
            z_component = -z_component

        return x_component, y_component, z_component

    def _writeTrendSpecificParam(self) -> None:
        print('')

    def _trendValueCalculation(self, parameters_for_trend_calc, x, y, k, zinc):
        # Calculate trend value for point(x,y,z) relative to origin defined by (xCenter, yCenter,zCenter)
        # Here only a shift in the global x,y coordinates are done. The z coordinate is relative to simulation box.
        zRel = (k - self._start_layer + 0.5) * zinc - self._z_center
        xRel = x - self._x_center
        yRel = y - self._y_center
        return self._linearTrendFunction(parameters_for_trend_calc, xRel, yRel, zRel)

    def _trendValueCalculation_vectorized(
        self, parameters_for_trend_calc, x_vec, y_vec, k_vec, zinc
    ):
        # Calculate trend value for point(x,y,z) relative to origin defined by (xCenter, yCenter,zCenter)
        # Here only a shift in the global x,y coordinates are done. The z coordinate is relative to simulation box.
        zRel_vec = (k_vec - self._start_layer + 0.5) * zinc - self._z_center
        xRel_vec = x_vec - self._x_center
        yRel_vec = y_vec - self._y_center
        return self._linearTrendFunction_vectorized(
            parameters_for_trend_calc, xRel_vec, yRel_vec, zRel_vec
        )

    def _trendValueCalculationSimBox(
        self,
        parameters_for_trend_calc: Tuple[float, float, float],
        i,
        j,
        k,
        xinc,
        yinc,
        zinc,
    ):
        # Calculate trend value for point(x,y,z) in simulation box coordinates.
        # The origin corresponds to the corner of cell (0,0,startLayer)
        zRel = (k - self._start_layer + 0.5) * zinc
        xRel = (i + 0.5) * xinc
        yRel = (j + 0.5) * yinc
        return self._linearTrendFunction(parameters_for_trend_calc, xRel, yRel, zRel)

    def _linearTrendFunction(
        self,
        parameters_for_trend_calc: Tuple[float, float, float],
        x_rel: float,
        y_rel: float,
        z_rel: float,
    ) -> float:
        x_component, y_component, z_component = parameters_for_trend_calc
        return x_component * x_rel + y_component * y_rel + z_component * z_rel

    @staticmethod
    def _linearTrendFunction_vectorized(
        parameters_for_trend_calc: Tuple[float, float, float],
        x_rel_vec,
        y_rel_vec,
        z_rel_vec,
    ):
        x_component, y_component, z_component = parameters_for_trend_calc
        return (
            x_component * x_rel_vec + y_component * y_rel_vec + z_component * z_rel_vec
        )


# ----------------------------------------------------------------------------------------------------------


def validator(self, value: Union[FmuProperty[float], float]) -> bool:
    if isinstance(value, FmuProperty):
        value = value.value
    return isinstance(value, float) or isinstance(value, int)


class Point3DProperty:
    _dimension = 3

    def __init__(self, *args):
        fmu_updatable = [False, False, False]
        if len(args) == 1:
            origin = args[0]
            if isinstance(origin, Point3DProperty):
                fmu_updatable = origin.fmu_as_point()
                origin = origin.as_point()
        elif len(args) == 2:
            origin = args[0]
            fmu_updatable = args[1]
        elif len(args) == self._dimension:
            origin = list(args)
            for i in range(len(origin)):
                element = origin[i]
                if isinstance(element, FmuProperty):
                    origin[i] = element.value
                    fmu_updatable[i] = element.updatable
        else:
            raise ValueError('Invalid constructor arguments')
        if len(origin) != len(fmu_updatable) != self._dimension:
            raise ValueError('Error: Origin must have length 3')
        self.x = FmuProperty(origin[0], fmu_updatable[0])
        self.y = FmuProperty(origin[1], fmu_updatable[1])
        self.z = FmuProperty(origin[2], fmu_updatable[2])

    x: FmuProperty[float] = make_ranged_property(
        'x',
        'first coordinate MUST be a number (int, or float)',
        -float('inf'),
        float('inf'),
        validator,
    )
    y: FmuProperty[float] = make_ranged_property(
        'y',
        'second coordinate MUST be a number (int, or float)',
        -float('inf'),
        float('inf'),
        validator,
    )
    z: FmuProperty[float] = make_ranged_property(
        'z',
        'third coordinate MUST be a number (int, or float)',
        -float('inf'),
        float('inf'),
        validator,
    )

    def __len__(self):
        return 3

    def __getitem__(self, item: int) -> FmuProperty[float]:
        if item == 0:
            return self.x
        elif item == 1:
            return self.y
        elif item == 2:
            return self.z
        else:
            raise IndexError

    def __eq__(self, other):
        if isinstance(other, Point3DProperty):
            return self.x == other.x and self.y == other.y and self.z == other.z
        elif len(other) == len(self):
            return (
                self.x.value == other[0]
                and self.y.value == other[1]
                and self.z.value == other[2]
            )
        else:
            return False

    def as_point(self) -> Point3D:
        return self.x.value, self.y.value, self.z.value

    def fmu_as_point(self) -> Tuple[bool, bool, bool]:
        return self.x.updatable, self.y.updatable, self.z.updatable


class Trend3D_conic(Trend3D):
    """A helper class, to gather common functionality from elliptic, and hyperbolic trends"""

    def __init__(
        self,
        azimuth_angle: float = 0.0,
        azimuth_angle_fmu_updatable: bool = False,
        stacking_angle: float = 0.0001,
        stacking_angle_fmu_updatable: bool = False,
        curvature: float = 0.0001,
        curvature_fmu_updatable: bool = False,
        migration_angle: Optional[float] = None,
        migration_angle_fmu_updatable: bool = False,
        origin: Tuple[float, float, float] = (0.0, 0.0, 0.0),
        origin_fmu_updatable: Union[bool, Tuple[bool, bool, bool]] = (
            False,
            False,
            False,
        ),
        origin_type: OriginType = OriginType.RELATIVE,
        direction: Direction = Direction.PROGRADING,
        debug_level: Debug = Debug.OFF,
        **kwargs,
    ):
        # TODO: Curvature MUST be greater than 0
        super().__init__(
            azimuth_angle,
            azimuth_angle_fmu_updatable,
            stacking_angle,
            stacking_angle_fmu_updatable,
            direction,
            debug_level,
            **kwargs,
        )

        self._migration_angle = None
        self.curvature = FmuProperty(curvature, curvature_fmu_updatable)
        if migration_angle is not None:
            self.migration_angle = FmuProperty(
                migration_angle, migration_angle_fmu_updatable
            )

        if isinstance(origin_fmu_updatable, bool):
            origin_fmu_updatable = (
                origin_fmu_updatable,
                origin_fmu_updatable,
                origin_fmu_updatable,
            )
        self.origin = Point3DProperty(origin, origin_fmu_updatable)
        self.origin_type = origin_type

    curvature: FmuProperty[float] = make_lower_bounded_property(
        'curvature', strictly_greater=True
    )

    migration_angle: FmuProperty[float] = make_angle_property(
        'migration_angle',
        strictly_less=True,
        strictly_greater=True,
    )

    # TODO: Use Point3DProperty instead of this
    @property
    def origin(self) -> Point3DProperty:
        return self._origin

    @origin.setter
    def origin(self, origin):
        if not isinstance(origin, Point3DProperty):
            self._origin = Point3DProperty(origin, self._origin.fmu_as_point())
        else:
            self._origin = Point3DProperty(origin)

    @property
    def origin_type(self) -> OriginType:
        return self._origin_type

    @origin_type.setter
    def origin_type(self, _type: OriginType):
        if _type not in OriginType:
            raise ValueError(
                'Error: In {}\n'
                "Error: Origin type must be either 'Relative' or 'Absolute' "
                ''.format(self._class_name)
            )
        self._origin_type = _type

    @property
    def type(self) -> TrendType:
        raise NotImplementedError

    @classmethod
    def from_xml(
        cls,
        trend_rule_xml: Element,
        model_file_name: Optional[str] = None,
        debug_level: Debug = Debug.OFF,
        get_migration_angle: bool = True,
        get_origin_z: bool = True,
    ) -> 'Trend3D_conic':
        base_trend = super().from_xml(trend_rule_xml, model_file_name, debug_level)

        # Additional input parameters comes here (for other Trend3D-types)
        curvature, is_curvature_fmu_updatable = get_fmu_value_from_xml(
            trend_rule_xml,
            'curvature',
            modelFile=model_file_name,
            required=True,
        )

        migration_angle, is_migration_angle_fmu_updatable = None, False
        if get_migration_angle:
            migration_angle, is_migration_angle_fmu_updatable = get_fmu_value_from_xml(
                trend_rule_xml,
                'migrationAngle',
                modelFile=model_file_name,
                required=False,
                defaultValue=0,
            )

        origin_x, is_origin_x_fmu_updatable = get_fmu_value_from_xml(
            trend_rule_xml,
            'origin_x',
            modelFile=model_file_name,
            required=True,
        )

        origin_y, is_origin_y_fmu_updatable = get_fmu_value_from_xml(
            trend_rule_xml,
            'origin_y',
            modelFile=model_file_name,
            required=True,
        )

        origin_z, is_origin_z_fmu_updatable = 0.0, False
        if get_origin_z:
            origin_z, is_origin_z_fmu_updatable = get_fmu_value_from_xml(
                trend_rule_xml,
                'origin_z_simbox',
                modelFile=model_file_name,
                required=True,
            )

        origin = (origin_x, origin_y, origin_z)
        is_origin_fmu_updatable = (
            is_origin_x_fmu_updatable,
            is_origin_y_fmu_updatable,
            is_origin_z_fmu_updatable,
        )
        origin_type = get_origin_type_from_model_file(trend_rule_xml, model_file_name)
        representation = base_trend.as_dict()
        representation.update(
            dict(
                curvature=curvature,
                curvature_fmu_updatable=is_curvature_fmu_updatable,
                migration_angle=migration_angle,
                migration_angle_fmu_updatable=is_migration_angle_fmu_updatable,
                origin=origin,
                origin_fmu_updatable=is_origin_fmu_updatable,
                origin_type=origin_type,
                debug_level=debug_level,
            )
        )
        return cls(**representation)

    def setCurvatureFmuUpdatable(self, value: bool) -> None:
        self.curvature.updatable = value

    def setOriginXFmuUpdatable(self, value: bool) -> None:
        self.origin.x.updatable = value

    def setOriginYFmuUpdatable(self, value: bool) -> None:
        self.origin.y.updatable = value

    def setOriginZFmuUpdatable(self, value: bool) -> None:
        self.origin.z.updatable = value

    def as_dict(self):
        try:
            migration_angle = self.migration_angle.value
            migration_angle_fmu_updatable = self.migration_angle.updatable
        except (NotImplementedError, AttributeError):
            migration_angle = None
            migration_angle_fmu_updatable = False
        representation = super().as_dict()
        representation.update(
            dict(
                curvature=self.curvature.value,
                curvature_fmu_updatable=self.curvature.updatable,
                migration_angle=migration_angle,
                migration_angle_fmu_updatable=migration_angle_fmu_updatable,
                origin=self.origin.as_point(),
                origin_fmu_updatable=self.origin.fmu_as_point(),
                origin_type=self.origin_type,
            )
        )
        return representation


ConicTrend = Trend3D_conic


class Trend3D_elliptic(Trend3D_conic):
    """
    Description: Create an elliptic trend 3D object
    Input is model parameters.
    """

    def __init__(
        self,
        azimuth_angle: float = 0.0,
        azimuth_angle_fmu_updatable: bool = False,
        stacking_angle: float = 0.0001,
        stacking_angle_fmu_updatable: bool = False,
        curvature: float = 0.0001,
        curvature_fmu_updatable: bool = False,
        origin: Tuple[float, float, float] = (0.0, 0.0, 0.0),
        origin_fmu_updatable: Union[bool, Tuple[bool, bool, bool]] = (
            False,
            False,
            False,
        ),
        origin_type: OriginType = OriginType.RELATIVE,
        direction: Direction = Direction.PROGRADING,
        debug_level: Debug = Debug.OFF,
        **kwargs,
    ):
        # TODO: Ensure that these values are consistent with the tests!
        # Stacking angle must be > 0.
        # if abs(stacking_angle) < 0.00001:
        #     stacking_angle = 0.00001
        super().__init__(
            azimuth_angle,
            azimuth_angle_fmu_updatable,
            stacking_angle,
            stacking_angle_fmu_updatable,
            curvature,
            curvature_fmu_updatable,
            None,
            False,  # migration angle
            origin,
            origin_fmu_updatable,
            origin_type,
            direction,
            debug_level,
        )

    @property
    def migration_angle(self):
        raise NotImplementedError

    @migration_angle.setter
    def migration_angle(self, value):
        raise NotImplementedError

    @property
    def type(self):
        return TrendType.ELLIPTIC

    def XMLAddElement(
        self,
        parent: Element,
        zone_number: int,
        region_number: int,
        gf_name: GaussianFieldName,
        fmu_attributes: List[FmuAttribute],
    ) -> None:
        """
        Add to the parent element a new element with specified tag and attributes.
        The attributes are a dictionary with {name:value}
        After this function is called, the parent element has got a new child element
        for the current class.
        """
        if self._debug_level >= Debug.VERY_VERBOSE:
            print(f'--- call XMLADDElement from {self._class_name}')

        trendElement = Element('Trend')
        parent.append(trendElement)
        elliptic3DElement = Element('Elliptic3D')
        trendElement.append(elliptic3DElement)
        super()._XMLAddElementTag(
            elliptic3DElement, zone_number, region_number, gf_name, fmu_attributes
        )

        tags = [
            ('curvature', self.curvature),
            ('origin_x', self.origin.x),
            ('origin_y', self.origin.y),
            ('origin_z_simbox', self.origin.z),
        ]
        for tag, prop in tags:
            elliptic3DElement.append(
                fmu_xml_element(
                    tag,
                    prop.value,
                    prop.updatable,
                    zone_number,
                    region_number,
                    gf_name,
                    createFMUvariableNameForTrend,
                    fmu_attributes,
                )
            )

        tag = 'origintype'
        obj = Element(tag)
        if self.origin_type == OriginType.RELATIVE:
            obj.text = ' Relative '
        elif self.origin_type == OriginType.ABSOLUTE:
            obj.text = ' Absolute '
        elliptic3DElement.append(obj)

    @classmethod
    def from_xml(
        cls,
        trend_rule_xml: Element,
        model_file_name: Optional[str] = None,
        debug_level: Debug = Debug.OFF,
        **kwargs,
    ) -> 'Trend3D_elliptic':
        return super().from_xml(
            trend_rule_xml, model_file_name, debug_level, get_migration_angle=False
        )

    def _setTrendCenter(
        self,
        x0,
        y0,
        azimuth_angle,
        sim_box_x_length,
        sim_box_y_length,
        sim_box_thickness,
        **kwargs,
    ):
        super()._setTrendCenter(
            x0,
            y0,
            azimuth_angle,
            sim_box_x_length,
            sim_box_y_length,
            sim_box_thickness,
            self.origin_type,
            self.origin,
        )

    def _trendValueCalculation(self, parameters_for_trend_calc, x, y, k, zinc):
        # Elliptic

        # Calculate x,y,z in sim box coordinates with origin in reference point
        z1 = (k - self._start_layer + 0.5) * zinc - self._z_center
        x1 = x - self._x_center
        y1 = y - self._y_center

        # Calculate trend value for point(x,y,z) relative to reference point (xCenter, yCenter, zCenter)
        return self._ellipticTrendFunction(parameters_for_trend_calc, x1, y1, z1)

    def _trendValueCalculation_vectorized(
        self, parameters_for_trend_calc, x_vec, y_vec, k_vec, zinc
    ):
        # Elliptic

        # Calculate x,y,z in sim box coordinates with origin in reference point
        z1_vec = (k_vec - self._start_layer + 0.5) * zinc - self._z_center
        x1_vec = x_vec - self._x_center
        y1_vec = y_vec - self._y_center

        # Calculate trend value for point(x,y,z) relative to reference point (xCenter, yCenter, zCenter)
        return self._ellipticTrendFunction_vectorized(
            parameters_for_trend_calc, x1_vec, y1_vec, z1_vec
        )

    def _trendValueCalculationSimBox(
        self,
        parameters_for_trend_calc: Tuple[float, float, float, float, float],
        i,
        j,
        k,
        xinc,
        yinc,
        zinc,
    ):
        # Elliptic

        # Calculate x,y,z in sim box coordinates with origin in reference point
        z = (k - self._start_layer + 0.5) * zinc - self._z_center_in_sim_box_coordinates
        x = (i + 0.5) * xinc - self._x_center_in_sim_box_coordinates
        y = (j + 0.5) * yinc - self._y_center_in_sim_box_coordinates

        # Calculate trend value for point(x,y,z) relative to reference point (xCenterInSimBox, yCenterInSimBox, zCenterInSimBox)
        return self._ellipticTrendFunction(parameters_for_trend_calc, x, y, z)

    def _ellipticTrendFunction(
        self,
        parameters_for_trend_calc: Tuple[float, float, float, float, float],
        x: float,
        y: float,
        z: float,
    ) -> float:
        # Input(x,y,z) must be relative to reference point(xCenter, yCenter, zCenter)
        sin_theta, cos_theta, tan_alpha, a, b = parameters_for_trend_calc

        if z != 0.0:
            L = z * tan_alpha
            x_center = -L * sin_theta
            y_center = -L * cos_theta
        else:
            x_center = 0.0
            y_center = 0.0

        x_rel = x - x_center
        y_rel = y - y_center
        x_rotated = x_rel * cos_theta - y_rel * sin_theta
        y_rotated = x_rel * sin_theta + y_rel * cos_theta
        return np.sqrt(np.square(x_rotated / a) + np.square(y_rotated / b))

    @staticmethod
    def _ellipticTrendFunction_vectorized(
        parameters_for_trend_calc: Tuple[float, float, float, float, float],
        x_vec,
        y_vec,
        z_vec,
    ):
        # Input(x,y,z) must be relative to reference point(xCenter, yCenter, zCenter)
        sin_theta, cos_theta, tan_alpha, a, b = parameters_for_trend_calc
        index_vec = np.arange(len(z_vec))
        selected = index_vec[z_vec != 0]
        L = np.zeros(len(z_vec), np.float32)
        x_center = np.zeros(len(z_vec), np.float32)
        y_center = np.zeros(len(z_vec), np.float32)

        L[selected] = z_vec[selected] * tan_alpha
        x_center[selected] = -L[selected] * sin_theta
        y_center[selected] = -L[selected] * cos_theta

        x_rel = x_vec - x_center
        y_rel = y_vec - y_center
        x_rotated = x_rel * cos_theta - y_rel * sin_theta
        y_rotated = x_rel * sin_theta + y_rel * cos_theta
        return np.sqrt(np.square(x_rotated / a) + np.square(y_rotated / b))

    def _calculateTrendModelParam(
        self, use_relative_azimuth: bool = False
    ) -> Tuple[float, float, float, float, float]:
        # Calculate the 3D trend values for Elliptic
        alpha = (
            self.stacking_direction.value
            * (90.0 - self.stacking_angle.value)
            * np.pi
            / 180.0
        )
        if use_relative_azimuth:
            theta = self._relative_azimuth * np.pi / 180.0
        else:
            theta = self.azimuth.value * np.pi / 180.0

        # Elliptic
        a = 1
        b = self.curvature.value
        sin_theta = math.sin(theta)
        cos_theta = math.cos(theta)
        tan_alpha = math.tan(alpha)
        return sin_theta, cos_theta, tan_alpha, a, b

    def _writeTrendSpecificParam(self) -> None:
        # Elliptic
        print(f'---  Curvature: {self.curvature}')
        print(f'---  Origin: ({self.origin.x}, {self.origin.y}, {self.origin.z})')
        print(f'---  Origin type: {self.origin_type.name}')

    def as_dict(self) -> dict:
        representation = super().as_dict()
        del representation['migration_angle']
        del representation['migration_angle_fmu_updatable']
        return representation


# ----------------------------------------------------------------------------------------------------------


class Trend3D_hyperbolic(Trend3D_conic):
    """
    Description: Create a hyperbolic trend 3D object
    Input is model parameters.
    """

    def __init__(
        self,
        azimuth_angle: float = 0.0,
        azimuth_angle_fmu_updatable: bool = False,
        stacking_angle: float = 0.0001,
        stacking_angle_fmu_updatable: bool = False,
        curvature: float = 0.0001,
        curvature_fmu_updatable: bool = False,
        migration_angle: float = 0.0,
        migration_angle_fmu_updatable: bool = False,
        origin: Tuple[float, float, float] = (0.0, 0.0, 0.0),
        origin_fmu_updatable: Union[bool, Tuple[bool, bool, bool]] = (
            False,
            False,
            False,
        ),
        origin_type: OriginType = OriginType.RELATIVE,
        direction: Direction = Direction.PROGRADING,
        debug_level: Debug = Debug.OFF,
        **kwargs,
    ):
        super().__init__(
            azimuth_angle,
            azimuth_angle_fmu_updatable,
            stacking_angle,
            stacking_angle_fmu_updatable,
            curvature,
            curvature_fmu_updatable,
            migration_angle,
            migration_angle_fmu_updatable,
            origin,
            origin_fmu_updatable,
            origin_type,
            direction,
            debug_level,
            **kwargs,
        )

    @classmethod
    def from_xml(
        cls,
        trend_rule_xml: Element,
        model_file_name: Optional[str] = None,
        debug_level: Debug = Debug.OFF,
        **kwargs,
    ) -> 'Trend3D_hyperbolic':
        return super().from_xml(trend_rule_xml, model_file_name, debug_level)

    def setMigrationAngleFmuUpdatable(self, value):
        self.migration_angle.updatable = value

    @property
    def type(self) -> TrendType:
        return TrendType.HYPERBOLIC

    def _setTrendCenter(
        self,
        x0: float,
        y0: float,
        azimuth_angle: float,
        sim_box_x_length: float,
        sim_box_y_length: float,
        sim_box_thickness: float,
        origin_type: Optional[OriginType] = None,
        origin: Optional[Point3D] = None,
    ) -> None:
        super()._setTrendCenter(
            x0,
            y0,
            azimuth_angle,
            sim_box_x_length,
            sim_box_y_length,
            sim_box_thickness,
            self.origin_type,
            self.origin,
        )

    def _trendValueCalculation(self, parameters_for_trend_calc, x, y, k, zinc):
        # Hyperbolic

        # Calculate x,y,z in sim box coordinates with origin in reference point
        z1 = (k - self._start_layer + 0.5) * zinc - self._z_center
        x1 = x - self._x_center
        y1 = y - self._y_center

        # Calculate trend value for point(x,y,z) relative to reference point (xCenter, yCenter, zCenter)
        return self._hyperbolicTrendFunction(parameters_for_trend_calc, x1, y1, z1)

    def _trendValueCalculation_vectorized(
        self, parameters_for_trend_calc, x_vec, y_vec, k_vec, zinc
    ):
        # Hyperbolic

        # Calculate x,y,z in sim box coordinates with origin in reference point
        z1_vec = (k_vec - self._start_layer + 0.5) * zinc - self._z_center
        x1_vec = x_vec - self._x_center
        y1_vec = y_vec - self._y_center

        # Calculate trend value for point(x,y,z) relative to reference point (xCenter, yCenter, zCenter)
        return self._hyperbolicTrendFunction_vectorized(
            parameters_for_trend_calc, x1_vec, y1_vec, z1_vec
        )

    def _trendValueCalculationSimBox(
        self,
        parameters_for_trend_calc: HyperbolicTrendParameters,
        i: int,
        j: int,
        k: float,
        xinc: float,
        yinc: float,
        zinc: float,
    ) -> np.float64:
        # Hyperbolic

        # Calculate x,y,z in sim box coordinates with origin in reference point
        z = (k - self._start_layer + 0.5) * zinc - self._z_center_in_sim_box_coordinates
        x = (i + 0.5) * xinc - self._x_center_in_sim_box_coordinates
        y = (j + 0.5) * yinc - self._y_center_in_sim_box_coordinates

        # Calculate trend value for point(x,y,z) relative to reference point (xCenterInSimBox, yCenterInSimBox, zCenterInSimBox)
        return self._hyperbolicTrendFunction(parameters_for_trend_calc, x, y, z)

    def _hyperbolicTrendFunction(
        self,
        parameters_for_trend_calc: HyperbolicTrendParameters,
        x: float,
        y: float,
        z: float,
    ) -> np.float64:
        # Hyperbolic
        sin_theta, cos_theta, tan_alpha, tan_beta, a, b = parameters_for_trend_calc

        # The center point is changed by depth. There are two angles that can specify this
        # The angle alpha (which is 90 -stacking angle) will shift the center point along azimuth direction.
        # The angle beta (migration angle) will shift the center point orthogonal to azimuth direction.
        # First shift the center point in azimuth direction
        L = -z * tan_alpha
        x_center = L * sin_theta
        y_center = L * cos_theta

        # Secondly, shift the center point further, but now orthogonal to azimuth direction.
        L = -z * tan_beta
        x_center = L * cos_theta + x_center
        y_center = -L * sin_theta + y_center

        x_rel = x - x_center
        y_rel = y - y_center
        x_rotated_by_theta = x_rel * cos_theta - y_rel * sin_theta
        y_rotated_by_theta = x_rel * sin_theta + y_rel * cos_theta

        if x_rotated_by_theta > 0:
            zero_point = a * np.sqrt(1 + np.square(y_rotated_by_theta / b))
        else:
            zero_point = -a * np.sqrt(1 + np.square(y_rotated_by_theta / b))

        return 1.0 - abs(x_rotated_by_theta / zero_point)

    @staticmethod
    def _hyperbolicTrendFunction_vectorized(
        parameters_for_trend_calc: HyperbolicTrendParameters, x_vec, y_vec, z_vec
    ):
        # Hyperbolic
        sin_theta, cos_theta, tan_alpha, tan_beta, a, b = parameters_for_trend_calc

        # The center point is changed by depth. There are two angles that can specify this
        # The angle alpha (which is 90 -stacking angle) will shift the center point along azimuth direction.
        # The angle beta (migration angle) will shift the center point orthogonal to azimuth direction.
        # First shift the center point in azimuth direction
        L = -z_vec * tan_alpha
        x_center = L * sin_theta
        y_center = L * cos_theta

        # Secondly, shift the center point further, but now orthogonal to azimuth direction.
        L = -z_vec * tan_beta
        x_center = L * cos_theta + x_center
        y_center = -L * sin_theta + y_center

        x_rel = x_vec - x_center
        y_rel = y_vec - y_center
        x_rotated_by_theta = x_rel * cos_theta - y_rel * sin_theta
        y_rotated_by_theta = x_rel * sin_theta + y_rel * cos_theta

        zero_point = np.zeros(len(x_rotated_by_theta), np.float32)
        index_vec = np.arange(len(x_rotated_by_theta))

        selected = index_vec[x_rotated_by_theta > 0]
        zero_point[selected] = a * np.sqrt(
            1 + np.square(y_rotated_by_theta[selected] / b)
        )

        selected = index_vec[x_rotated_by_theta <= 0]
        zero_point[selected] = -a * np.sqrt(
            1 + np.square(y_rotated_by_theta[selected] / b)
        )

        return 1.0 - np.abs(x_rotated_by_theta / zero_point)

    def _calculateTrendModelParam(
        self, use_relative_azimuth: bool = False
    ) -> HyperbolicTrendParameters:
        # Calculate the 3D trend values for Hyperbolic
        if not self.curvature.value > 1.0:
            raise ValueError('Curvature value must be strictly larger than 1.0')
        if not abs(self.migration_angle) < 90.0:
            raise ValueError(
                'Migration angles absolute value must be less than 90 degrees'
            )
        if not abs(self.stacking_angle) > 0.0:
            raise ValueError('Stacking angle must be larger than 0 degrees.')
        if use_relative_azimuth:
            theta = self._relative_azimuth * np.pi / 180.0
        else:
            theta = self.azimuth.value * np.pi / 180.0
        beta = self.migration_angle * np.pi / 180.0
        alpha = (
            self.stacking_direction.value
            * (90.0 - self.stacking_angle.value)
            * np.pi
            / 180.0
        )

        # Hyperbolic
        sin_theta = math.sin(theta)
        cos_theta = math.cos(theta)
        tan_beta = math.tan(beta)
        tan_alpha = math.tan(alpha)

        a = self._x_sim_box
        b = self._y_sim_box / np.sqrt(np.square(self.curvature.value) - 1.0)

        parameters_for_trend_calc = (sin_theta, cos_theta, tan_alpha, tan_beta, a, b)

        if self._debug_level >= Debug.VERY_VERBOSE:
            print('--- Calculated parameters for Hyperbolic trend:')
            print(f'---   sinTheta = {sin_theta}')
            print(f'---   cosTheta = {cos_theta}')
            print(f'---   tan_alpha = {tan_alpha}')
            print(f'---   tanBeta  = {tan_beta}')
            print(f'---   a = {a}')
            print(f'---   b = {b}')

        return parameters_for_trend_calc

    def _writeTrendSpecificParam(self) -> None:
        print(f'---  Curvature: {self.curvature}')
        print(f'---  Origin: ({self.origin.x}, {self.origin.y}, {self.origin.z})')
        print(f'---  Origin type: {self.origin_type.name}')
        print(f'---  Migration angle: {self.migration_angle}')

    def XMLAddElement(
        self,
        parent: Element,
        zone_number: int,
        region_number: int,
        gf_name: GaussianFieldName,
        fmu_attributes: List[FmuAttribute],
    ) -> None:
        """
        Add to the parent element a new element with specified tag and attributes.
            The attributes are a dictionary with {name:value}
            After this function is called, the parent element has got a new child element
            for the current class.
        """
        if self._debug_level >= Debug.VERY_VERBOSE:
            print(f'--- call XMLADDElement from {self._class_name}')

        trend_element = Element('Trend')
        parent.append(trend_element)
        hyperbolic_3d_element = Element('Hyperbolic3D')
        trend_element.append(hyperbolic_3d_element)
        super()._XMLAddElementTag(
            hyperbolic_3d_element, zone_number, region_number, gf_name, fmu_attributes
        )

        tags = [
            ('curvature', self.curvature),
            ('migrationAngle', self.migration_angle),
            ('origin_x', self.origin.x),
            ('origin_y', self.origin.y),
            ('origin_z_simbox', self.origin.z),
        ]
        for tag, prop in tags:
            hyperbolic_3d_element.append(
                fmu_xml_element(
                    tag,
                    prop.value,
                    prop.updatable,
                    zone_number,
                    region_number,
                    gf_name,
                    createFMUvariableNameForTrend,
                    fmu_attributes,
                )
            )

        tag = 'origintype'
        obj = Element(tag)
        if self.origin_type == OriginType.RELATIVE:
            obj.text = ' Relative '
        elif self.origin_type == OriginType.ABSOLUTE:
            obj.text = ' Absolute '
        # trendElement.append(obj)
        hyperbolic_3d_element.append(obj)


# ----------------------------------------------------------------------------------------------------------


class Trend3D_rms_param(Trend3D):
    """
    Description: Create a trend 3D object using a specified RMS 3D continuous parameter
    Input is model parameters.
    """

    def __init__(
        self, rms_parameter_name: str, debug_level: Debug = Debug.OFF, **kwargs
    ):
        self._rms_param_name = rms_parameter_name
        self._debug_level = debug_level

    @classmethod
    def from_xml(
        cls,
        trend_rule_xml: Element,
        model_file_name: Optional[str] = None,
        debug_level: Debug = Debug.OFF,
    ) -> 'Trend3D_rms_param':
        trend_parameter_name = getTextCommand(
            trend_rule_xml,
            'TrendParamName',
            'Trend',
            defaultText=None,
            modelFile=model_file_name,
            required=True,
        )
        return cls(
            rms_parameter_name=trend_parameter_name,
            debug_level=debug_level,
        )

    def _writeTrendSpecificParam(self) -> None:
        print(f'---  RMS parameter name for trend values: {self.trend_parameter_name}')

    @property
    def type(self) -> TrendType:
        return TrendType.RMS_PARAM

    @property
    def trend_parameter_name(self) -> str:
        return self._rms_param_name

    @trend_parameter_name.setter
    def trend_parameter_name(self, parameter_name: str):
        self._rms_param_name = parameter_name.strip()

    def XMLAddElement(
        self,
        parent: Element,
        zone_number: int,
        region_number: int,
        gf_name: str,
        fmu_attributes: List[FmuAttribute],
    ) -> None:
        """
        Add to the parent element a new element with specified tag and attributes.
            The attributes are a dictionary with {name:value}
            After this function is called, the parent element has got a new child element
            for the current class.
        """
        if self._debug_level >= Debug.VERY_VERBOSE:
            print(f'--- call XMLADDElement from  {self._class_name}')

        trend_element = Element('Trend')
        parent.append(trend_element)
        rms_parameter_element = Element('RMSParameter')
        trend_element.append(rms_parameter_element)
        trend_param_name_element = Element('TrendParamName')
        if self.trend_parameter_name:
            trend_param_name_element.text = ' ' + self.trend_parameter_name + ' '
        rms_parameter_element.append(trend_param_name_element)

    def as_dict(self):
        return dict(
            rms_param_name=self.trend_parameter_name,
            debug_level=self._debug_level,
        )


# ----------------------------------------------------------------------------------------------------------


class Trend3D_rms_map(Trend3D):
    """
    Description: Create a trend 3D object using a specified RMS 2D continuous trendmap.
    Input is trendmap.
    """

    def __init__(
        self,
        rms_trendmap_name: str,
        rms_trendmap_zone: str,
        debug_level: Debug = Debug.OFF,
        **kwargs,
    ):
        self._rms_trendmap_name = rms_trendmap_name
        self._rms_trendmap_zone = rms_trendmap_zone
        self._debug_level = debug_level

    @classmethod
    def from_xml(
        cls,
        trend_rule_xml: Element,
        model_file_name: Optional[str] = None,
        debug_level: Debug = Debug.OFF,
    ) -> 'Trend3D_rms_map':
        trend_map_name = getTextCommand(
            trend_rule_xml,
            'TrendMapName',
            'Trend',
            defaultText=None,
            modelFile=model_file_name,
            required=True,
        )
        trend_map_zone = getTextCommand(
            trend_rule_xml,
            'TrendMapZone',
            'Trend',
            defaultText=None,
            modelFile=model_file_name,
            required=True,
        )
        if trend_map_name is None or trend_map_zone is None:
            raise ValueError(
                f'Missing input name of trend map and/or zone for {TrendType.RMS_TRENDMAP} '
            )
        return cls(
            rms_trendmap_name=trend_map_name,
            rms_trendmap_zone=trend_map_zone,
            debug_level=debug_level,
        )

    def _writeTrendSpecificParam(self) -> None:
        print(f'---  RMS trend map name for trend values: {self.trend_map_name}')
        print(f'---  RMS trend map zone for trend values: {self.trend_map_zone}')

    @property
    def type(self) -> TrendType:
        return TrendType.RMS_TRENDMAP

    @property
    def trend_map_name(self) -> str:
        return self._rms_trendmap_name

    @trend_map_name.setter
    def trend_map_name(self, trendmap_name: str):
        self._rms_trendmap_name = trendmap_name.strip()

    @property
    def trend_map_zone(self) -> str:
        return self._rms_trendmap_zone

    @trend_map_zone.setter
    def trend_map_zone(self, trendmap_zone: str):
        self._rms_trendmap_zone = trendmap_zone.strip()

    def XMLAddElement(
        self,
        parent: Element,
        zone_number: int,
        region_number: int,
        gf_name: str,
        fmu_attributes: List[FmuAttribute],
    ) -> None:
        """
        Add to the parent element a new element with specified tag and attributes.
            The attributes are a dictionary with {name:value}
            After this function is called, the parent element has got a new child element
            for the current class.
        """
        if self._debug_level >= Debug.VERY_VERBOSE:
            print(f'--- call XMLADDElement from  {self._class_name}')

        trend_element = Element('Trend')
        parent.append(trend_element)
        rms_trendmap_element = Element('RMSTrendMap')
        trend_element.append(rms_trendmap_element)
        trend_map_name_element = Element('TrendMapName')
        trend_map_name_element.text = ' ' + self.trend_map_name + ' '
        trend_map_zone_element = Element('TrendMapZone')
        trend_map_zone_element.text = ' ' + self.trend_map_zone + ' '
        rms_trendmap_element.append(trend_map_name_element)
        rms_trendmap_element.append(trend_map_zone_element)

    def as_dict(self):
        return dict(
            rms_trendmap_name=self.trend_map_name,
            rms_trendmap_zone=self.trend_map_zone,
            debug_level=self._debug_level,
        )


# ----------------------------------------------------------------------------------------------------------


class Trend3D_elliptic_cone(Trend3D_conic):
    """
    Description:
     Create an elliptic cone trend 3D object where the horiontal cross section of
     a iso-surface is elliptic. The ellipse shape is defined by two half axes (a,b).
     The ratio b/a = curvature which is a user specified parameter for this trend typ.
     The relative size of the half axes for a cross section close to z= 0 and close to z= zoneThickness
     (in the zones local simulation box coordinate z for depth from top to base of the zone) may be different.
     This means that it is possible to build an elliptic cone if the relative size is different from 1
     and elliptic cylinder if the relative size is 1. If the migration angle is 0 and stacking angle
     is 90.0 degrees, the cone has a vertical center line.
     If the migration angle is different from 0 and/or stacking angle is different from 90.0 degrees,
     the center line has a slope so that the cone is skewed.
     The migration angle different from 0 means that the center point of the ellipse is shifted orthogonal
     to the  azimuth direction while stacking angle different from 90 degrees means that the center line
     is shifted in azimuth direction. A combination means that the ellipse
     (horizontal intersection of an iso-surface of the trend function) is shifted both along and
     orthogonal to azimuth direction.

    Input is model parameters.
    """

    def __init__(
        self,
        azimuth_angle: float = 0.0,
        azimuth_angle_fmu_updatable: bool = False,
        stacking_angle: float = 0.0001,
        stacking_angle_fmu_updatable: bool = False,
        curvature: float = 0.0001,
        curvature_fmu_updatable: bool = False,
        migration_angle: Optional[float] = None,
        migration_angle_fmu_updatable: bool = False,
        relative_size: float = 1.0,
        relative_size_fmu_updatable: bool = False,
        origin: Tuple[float, float, float] = (0.0, 0.0, 0.0),
        origin_fmu_updatable: Union[bool, Tuple[bool, bool, bool]] = (
            False,
            False,
            False,
        ),
        origin_type: OriginType = OriginType.RELATIVE,
        direction: Direction = Direction.PROGRADING,
        debug_level: Debug = Debug.OFF,
        **kwargs,
    ):
        super().__init__(
            azimuth_angle,
            azimuth_angle_fmu_updatable,
            stacking_angle,
            stacking_angle_fmu_updatable,
            curvature,
            curvature_fmu_updatable,
            migration_angle,
            migration_angle_fmu_updatable,
            origin,
            origin_fmu_updatable,
            origin_type,
            direction,
            debug_level,
            **kwargs,
        )
        self.relative_size_of_ellipse = FmuProperty(
            relative_size, relative_size_fmu_updatable
        )

    relative_size_of_ellipse: FmuProperty[float] = make_ranged_property(
        'relative_size_of_ellipse',
        'The relative size must be between 0, and 1. ',
        minimum=0,
        maximum=1,
    )

    @classmethod
    def from_xml(
        cls,
        trend_rule_xml: Element,
        model_file_name: Optional[str] = None,
        debug_level: Debug = Debug.OFF,
        **kwargs,
    ) -> 'Trend3D_elliptic_cone':
        conic_trunc = super().from_xml(
            trend_rule_xml, model_file_name, debug_level, get_origin_z=True
        )
        # Relative size
        relative_size_of_ellipse, is_relative_size_fmu_updatable = (
            get_fmu_value_from_xml(
                trend_rule_xml,
                'relativeSize',
                modelFile=model_file_name,
                required=False,
                defaultValue=1.0,
            )
        )
        representation = conic_trunc.as_dict()
        representation.update(
            dict(
                relative_size=relative_size_of_ellipse,
                relative_size_fmu_updatable=is_relative_size_fmu_updatable,
            )
        )
        return cls(**representation)

    def XMLAddElement(
        self,
        parent: Element,
        zone_number: int,
        region_number: int,
        gf_name: str,
        fmu_attributes: List[FmuAttribute],
    ) -> None:
        """
        Add to the parent element a new element with specified tag and attributes.
        The attributes are a dictionary with {name:value}
        After this function is called, the parent element has got a new child element
        for the current class.
        """
        if self._debug_level >= Debug.VERY_VERBOSE:
            print(f'--- call XMLADDElement from {self._class_name}')

        trend_element = Element('Trend')
        parent.append(trend_element)
        elliptic_cone_3d_element = Element('EllipticCone3D')
        trend_element.append(elliptic_cone_3d_element)
        super()._XMLAddElementTag(
            elliptic_cone_3d_element,
            zone_number,
            region_number,
            gf_name,
            fmu_attributes,
        )

        tags = [
            ('curvature', self.curvature),
            ('migrationAngle', self.migration_angle),
            ('relativeSize', self.relative_size_of_ellipse),
            ('origin_x', self.origin.x),
            ('origin_y', self.origin.y),
            (
                'origin_z_simbox',
                self.origin.z,
            ),  # Only necessary when running in ERT / FMU / AHM mode
        ]

        for tag, prop in tags:
            elliptic_cone_3d_element.append(
                fmu_xml_element(
                    tag,
                    prop.value,
                    prop.updatable,
                    zone_number,
                    region_number,
                    gf_name,
                    createFMUvariableNameForTrend,
                    fmu_attributes,
                )
            )

        tag = 'origintype'
        obj = Element(tag)
        if self.origin_type == OriginType.RELATIVE:
            obj.text = ' Relative '
        elif self.origin_type == OriginType.ABSOLUTE:
            obj.text = ' Absolute '
        elliptic_cone_3d_element.append(obj)

    def setMigrationAngleFmuUpdatable(self, value):
        self.migration_angle.updatable = value

    @property
    def type(self):
        return TrendType.ELLIPTIC_CONE

    def setRelativeSizeOfEllipseFmuUpdatable(self, value):
        self._isRelativeSizeFMUUpdatable = value

    def _setTrendCenter(
        self,
        x0,
        y0,
        azimuth_angle,
        sim_box_x_length,
        sim_box_y_length,
        sim_box_thickness,
        **kwargs,
    ):
        super()._setTrendCenter(
            x0,
            y0,
            azimuth_angle,
            sim_box_x_length,
            sim_box_y_length,
            sim_box_thickness,
            self._origin_type,
            self._origin,
        )
        self.origin.z = 1.0

    def _trendValueCalculation(self, parameters_for_trend_calc, x, y, k, zinc):
        # Elliptic cone

        # Calculate x,y,z in sim box coordinates with origin in reference point
        z1 = (k - self._start_layer + 0.5) * zinc - self._z_center
        x1 = x - self._x_center
        y1 = y - self._y_center

        # Calculate trend value for point(x,y,z) relative to reference point (xCenter, yCenter, zCenter)
        return self._ellipticConeTrendFunction(
            parameters_for_trend_calc, x1, y1, z1, zinc
        )

    def _trendValueCalculation_vectorized(
        self, parameters_for_trend_calc, x_vec, y_vec, k_vec, zinc
    ):
        # Elliptic cone

        # Calculate x,y,z in sim box coordinates with origin in reference point
        z1 = (k_vec - self._start_layer + 0.5) * zinc - self._z_center
        x1 = x_vec - self._x_center
        y1 = y_vec - self._y_center

        # Calculate trend value for point(x,y,z) relative to reference point (xCenter, yCenter, zCenter)
        return self._ellipticConeTrendFunction_vectorized(
            parameters_for_trend_calc, x1, y1, z1, zinc
        )

    def _trendValueCalculationSimBox(
        self,
        parameters_for_trend_calc: HyperbolicTrendParameters,
        i,
        j,
        k,
        xinc,
        yinc,
        zinc,
    ):
        # Elliptic cone

        # Calculate x,y,z in sim box coordinates with origin in reference point
        z = (k - self._start_layer + 0.5) * zinc - self._z_center_in_sim_box_coordinates
        x = (i + 0.5) * xinc - self._x_center_in_sim_box_coordinates
        y = (j + 0.5) * yinc - self._y_center_in_sim_box_coordinates

        # Calculate trend value for point(x,y,z) relative to reference point (xCenter, yCenter, zCenter)
        return self._ellipticConeTrendFunction(parameters_for_trend_calc, x, y, z, zinc)

    def _ellipticConeTrendFunction(
        self,
        parameters_for_trend_calc: HyperbolicTrendParameters,
        x: float,
        y: float,
        z: float,
        zinc: Union[int, float],
    ) -> float:
        # Elliptic cone
        sin_theta, cos_theta, tan_alpha, tan_beta, a, _ = parameters_for_trend_calc

        z_top = 0.0
        z_thickness = (self._end_layer - self._start_layer + 1) * zinc

        a_base = a
        a_top = a * self.relative_size_of_ellipse.value
        da = a_base - a_top
        a = a_top + da * (z - z_top) / z_thickness
        b = a * self.curvature.value

        # The center point is changed by depth. There are two angles that can specify this
        # The angle alpha (which is 90 -stacking angle) will shift the center point along azimuth direction.
        # The angle beta (migration angle) will shift the center point orthogonal to azimuth direction.
        # First shift the center point in azimuth direction
        L = -z * tan_alpha
        x_center = L * sin_theta
        y_center = L * cos_theta

        # Secondly, shift the center point further, but now orthogonal to azimuth direction.
        L = z * tan_beta
        x_center = L * cos_theta + x_center
        y_center = -L * sin_theta + y_center

        x_rel = x - x_center
        y_rel = y - y_center
        x_rotated_by_theta = x_rel * cos_theta - y_rel * sin_theta
        y_rotated_by_theta = x_rel * sin_theta + y_rel * cos_theta

        return np.sqrt(
            np.square(x_rotated_by_theta / a) + np.square(y_rotated_by_theta / b)
        )

    def _ellipticConeTrendFunction_vectorized(
        self,
        parameters_for_trend_calc: HyperbolicTrendParameters,
        x_vec,
        y_vec,
        z_vec,
        zinc: Union[int, float],
    ):
        # Elliptic cone
        sin_theta, cos_theta, tan_alpha, tan_beta, a, _ = parameters_for_trend_calc

        z_top = 0.0
        z_thickness = (self._end_layer - self._start_layer + 1) * zinc

        a_base = a
        a_top = a * self.relative_size_of_ellipse.value
        da = a_base - a_top
        a = a_top + da * (z_vec - z_top) / z_thickness
        b = a * self.curvature.value

        # The center point is changed by depth. There are two angles that can specify this
        # The angle alpha (which is 90 -stacking angle) will shift the center point along azimuth direction.
        # The angle beta (migration angle) will shift the center point orthogonal to azimuth direction.
        # First shift the center point in azimuth direction
        L = -z_vec * tan_alpha
        x_center = L * sin_theta
        y_center = L * cos_theta

        # Secondly, shift the center point further, but now orthogonal to azimuth direction.
        L = z_vec * tan_beta
        x_center = L * cos_theta + x_center
        y_center = -L * sin_theta + y_center

        x_rel = x_vec - x_center
        y_rel = y_vec - y_center
        x_rotated_by_theta = x_rel * cos_theta - y_rel * sin_theta
        y_rotated_by_theta = x_rel * sin_theta + y_rel * cos_theta

        return np.sqrt(
            np.square(x_rotated_by_theta / a) + np.square(y_rotated_by_theta / b)
        )

    def _calculateTrendModelParam(
        self, use_relative_azimuth: bool = False
    ) -> HyperbolicTrendParameters:
        # Calculate the 3D trend values for Elliptic cone
        assert abs(self.migration_angle) < 90.0
        if abs(self.stacking_angle) <= 0.001:
            self.stacking_angle = 0.001
        assert abs(self.stacking_angle) > 0.0

        if use_relative_azimuth:
            theta = self._relative_azimuth * np.pi / 180.0
        else:
            theta = self.azimuth * np.pi / 180.0
        beta = self.migration_angle * np.pi / 180.0
        alpha = (
            self.stacking_direction.value
            * (90.0 - self.stacking_angle.value)
            * np.pi
            / 180.0
        )

        # Elliptic Cone
        a = 1
        b = self.curvature
        sin_theta = math.sin(theta)
        cos_theta = math.cos(theta)
        tan_beta = math.tan(beta)
        tan_alpha = math.tan(alpha)

        return sin_theta, cos_theta, tan_alpha, tan_beta, a, b

    def _writeTrendSpecificParam(self) -> None:
        # Elliptic cone
        print(f'---  Curvature: {self.curvature}')
        print(f'---  Migration angle: {self.migration_angle}')
        print(f'---  Relative size: {self.relative_size_of_ellipse}')
        print(
            f'---  Origin: ({self.origin.x.value}, {self.origin.y.value}, {self.origin.z.value})'
        )
        print(f'---  Origin type: {self.origin_type.name}')
