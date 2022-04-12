''' This module is used in FMU workflows to copy gaussian field values from
    geomodel grid to ERTBOX grid and extrapolate values that are undefined
    in ERTBOX grid. This functionality is used when the user wants to
    apply customized trends for GRF's in APS and run this in FMU with AHM.
'''

import numpy as np
import numpy.ma as ma
import roxar

from roxar import Direction
from aps.algorithms.APSModel import APSModel
from aps.utils.constants.simple import (
    Debug, TrendType, Conform, 
    ExtrapolationMethod, GridModelConstants,
)
from aps.utils.roxar.grid_model import get_zone_layer_numbering, get_zone_names


def get_grid_model(project,grid_model_name: str):
    """
    For given grid model name, return grid_model and grid objects.
    """
    if grid_model_name not in project.grid_models:
        raise ValueError(
            f"Grid model {grid_model_name} does not exist."
        )
    grid_model = project.grid_models[grid_model_name]
    if grid_model.is_empty():
        raise ValueError(
            f"Grid model {grid_model_name} is empty. "
        )
    grid = grid_model.get_grid()
    return grid_model, grid


def check_and_get_grid_dimensions(
        geogrid,ertboxgrid,
        geo_grid_model_name, ertbox_grid_model_name
    ):
    """
    For a given geogrid and ertbox grid return grid dimensions.
    """
    geogrid_dims = geogrid.simbox_indexer.dimensions
    ertbox_dims = ertboxgrid.simbox_indexer.dimensions
    nx = geogrid_dims[0]
    ny = geogrid_dims[1]
    nz = geogrid_dims[2]
    if ertbox_dims[0] != nx or ertbox_dims[1] !=ny:
        raise ValueError(
            f"Grid dimensions nx and ny for geogrid {geo_grid_model_name} "
            f"and ertbox grid {ertbox_grid_model_name} must be equal."
    )
    nz_ertbox = ertbox_dims[2]
    return nx, ny, nz, nz_ertbox


def get_trend_param_names_from_aps_model(
        project,
        aps_model: APSModel,
        ertbox_grid_model_name: str,
        debug_level: Debug,
    ):
    """
    Returns a dict where key is zone name and the value is a tuple with zone related data.
    """
    geo_grid_model_name = aps_model.grid_model_name
    geogrid_model, geogrid = get_grid_model(project,geo_grid_model_name)
    _, ertboxgrid = get_grid_model(project,ertbox_grid_model_name)
    zone_names = get_zone_names(geogrid_model)
    number_layers_per_zone, _ , _  = get_zone_layer_numbering(geogrid)
    nz_ertbox = ertboxgrid.simbox_indexer.dimensions[2]

    
    # Get trend parameter names from model specification
    zone_dict = {} 
    use_rms_param_trend = False
    all_zone_models = aps_model.sorted_zone_models
    for key, zone_model in all_zone_models.items():
        zone_number, region_number = key
        if not aps_model.isSelected(zone_number, region_number):
            continue
        zone_index = zone_number - 1
        zone_name = zone_names[zone_index]

        number_layers = number_layers_per_zone[zone_number-1]

        if number_layers > nz_ertbox:
            raise ValueError(
                f"Number of layers nz of {ertbox_grid_model_name} "
                f"is less than number of layers in {geo_grid_model_name} "
                f"for zone {zone_name}"
            )
        if debug_level >= Debug.VERY_VERBOSE:
            print(
                f"--- zone_number:{zone_number}\n"
                f"--- zone name:{zone_name}\n"
                f"--- region_number: {region_number}\n"
                f"--- zone conformity:{zone_model.grid_layout}\n"
            )

        gauss_field_names = zone_model.gaussian_fields_in_truncation_rule
        param_name_list = []
        for gauss_field_name in gauss_field_names:
            if zone_model.hasTrendModel(gauss_field_name):
                _, trend_model, _,_ = zone_model.getTrendModel(gauss_field_name)
                trend_type = trend_model.type
                if trend_type == TrendType.RMS_PARAM:
                    trend_param_name = trend_model.trend_parameter_name
                    if trend_param_name not in geogrid_model.properties:
                        raise ValueError(
                            f"The 3D parameter {trend_param_name} does not exist "
                            f"in grid model {geo_grid_model_name}"
                        )

                    trend_param = geogrid_model.properties[trend_param_name]
                    if trend_param.is_empty():
                        raise ValueError(
                            f"Grid parameter {trend_param_name} for {geo_grid_model_name} "
                            "is empty. Must be non-empty."
                        )
                    param_name_list.append(trend_param_name)
        zone_dict[zone_name] = (zone_number, region_number, zone_model.grid_layout, param_name_list)
        if len(param_name_list) > 0:
            use_rms_param_trend = True
    return zone_dict, use_rms_param_trend


def assign_undefined_constant(ertbox_values_3d_masked, value, debug_level):
    if debug_level >= Debug.VERY_VERBOSE:
        print(f"--- All inactive values set to:{value}")
    ertbox_values_3d = ertbox_values_3d_masked.filled(value)
    return ertbox_values_3d


def fill_remaining_masked_values_within_colum(column_values_masked, nz_ertbox):
    if not ma.is_masked(column_values_masked):
        return column_values_masked
    else: 
        index_array = np.arange(nz_ertbox)
        work_array = column_values_masked.copy()
        list_of_unmasked_intervals = ma.notmasked_contiguous(column_values_masked)
        current_slice = list_of_unmasked_intervals[0]
        current_index_interval = index_array[current_slice]
        last_index = current_index_interval[-1]
        v1 = work_array[last_index]
        for number in range(1,len(list_of_unmasked_intervals)):
            prev_last_index = last_index
            current_slice = list_of_unmasked_intervals[number]
            indices = index_array[current_slice]
            first_index = indices[0]
            last_index = indices[-1]
            n = first_index - prev_last_index +  1
            v0 = work_array[prev_last_index]
            v1 = work_array[first_index]
            # Linear interpolate and assign to masked values
            n = first_index - prev_last_index
            indx = 1
            for k in range(prev_last_index + 1,first_index):
                column_values_masked[k] = v0 + (v1-v0)*indx/n
                indx += 1

        return column_values_masked       


def assign_undefined_vertical(method, nx, ny, nz_ertbox, ertbox_values_3d_masked, fill_value):
    k_indices = np.arange(nz_ertbox)
    for i in range(nx):
        for j in range(ny):
            column_values_masked = ertbox_values_3d_masked[i,j,:]
            defined_k_indices = k_indices[~column_values_masked.mask]

            if len(defined_k_indices) > 0:
                top_k = defined_k_indices[0]
                bottom_k = defined_k_indices[-1]
                top_value = column_values_masked[top_k]
                bottom_value = column_values_masked[bottom_k]
                undefined_k_indices_top = np.arange(top_k)
                undefined_k_indices_bottom = np.arange(bottom_k+1, nz_ertbox)
                if method in (ExtrapolationMethod.EXTEND, ExtrapolationMethod.EXTEND_LAYER_MEAN):
                    column_values_masked[undefined_k_indices_top] = top_value
                    column_values_masked[undefined_k_indices_bottom] = bottom_value
                    column_values_masked = \
                            fill_remaining_masked_values_within_colum(column_values_masked, nz_ertbox)
                    ertbox_values_3d_masked[i,j,:] = column_values_masked

                elif method in (ExtrapolationMethod.REPEAT, ExtrapolationMethod.REPEAT_LAYER_MEAN):
                    if len(undefined_k_indices_top) > 0:
                        m = len(undefined_k_indices_top)
                        n = len(defined_k_indices)
                        values_for_undefined = column_values_masked[undefined_k_indices_top]
                        values_for_undefined[:] = bottom_value
                        if m > n:
                            values_for_undefined[:n] = column_values_masked[defined_k_indices]
                        elif m < n:
                            tmp = column_values_masked[defined_k_indices]
                            values_for_undefined = tmp[:m]
                        else:
                            values_for_undefined = column_values_masked[defined_k_indices]

                        reverse_values_for_undefined = np.flip(values_for_undefined, axis=0)
                        column_values_masked[undefined_k_indices_top] = reverse_values_for_undefined
                    if len(undefined_k_indices_bottom) > 0:
                        m = len(undefined_k_indices_bottom)
                        n = len(defined_k_indices)
                        values_for_undefined = column_values_masked[undefined_k_indices_bottom].copy()
                        values_for_undefined[:] = top_value
                        if m > n:
                            values_for_undefined[(m-n):] = column_values_masked[defined_k_indices]
                        elif m < n:
                            tmp = column_values_masked[defined_k_indices]
                            values_for_undefined = tmp[(n-m):]
                        else:
                            values_for_undefined = column_values_masked[defined_k_indices]

                        reverse_values_for_undefined = np.flip(values_for_undefined,axis=0)
                        column_values_masked[undefined_k_indices_bottom] = reverse_values_for_undefined

                    column_values_masked = \
                            fill_remaining_masked_values_within_colum(column_values_masked, nz_ertbox)
                    ertbox_values_3d_masked[i,j,:] = column_values_masked

    ertbox_values_3d = ertbox_values_3d_masked.filled(fill_value) 
    return ertbox_values_3d


def assign_undefined_lateral(nz_ertbox, ertbox_values_3d_masked):
    for k in range(nz_ertbox):
        layer_values = ertbox_values_3d_masked[:,:,k]
        if layer_values.count() > 0:
            mean = ma.mean(ertbox_values_3d_masked[:,:,k])
            filled_layer_values = layer_values.filled(mean)
            ertbox_values_3d_masked[:,:,k] = filled_layer_values
    return ertbox_values_3d_masked


def get_param_values(
        geo_grid_model_name: str,
        geogrid_model,
        param_name: str,
):
    if param_name not in geogrid_model.properties:
        raise ValueError(
            f"The 3D parameter {param_name} does not exist "
            f"in grid model {geo_grid_model_name}"
        )

    param = geogrid_model.properties[param_name]
    if param.is_empty():
        raise ValueError(
            f"Grid parameter {param_name} for {geo_grid_model_name} is empty.\n"
        )
    param_values_active = param.get_values()
    return param_values_active


def get_grid_indices(geogrid, nx, ny,start_layer, end_layer):
    start = (0,0,start_layer)
    end = (nx,ny,end_layer+1)
    indexer = geogrid.simbox_indexer
    try:
            ijk_handedness = indexer.ijk_handedness
    except AttributeError:
            ijk_handedness = indexer.handedness

    zone_cell_numbers = geogrid.simbox_indexer.get_cell_numbers_in_range(start,end)
    defined_cell_indices = geogrid.simbox_indexer.get_indices(zone_cell_numbers)
    if ijk_handedness == Direction.right:
        i_indices = defined_cell_indices[:, 0]
        j_indices = -defined_cell_indices[:, 1] + ny -1
    else:
        i_indices = defined_cell_indices[:, 0]
        j_indices = defined_cell_indices[:, 1]
    k_indices = defined_cell_indices[:, 2]
    return i_indices, j_indices, k_indices, zone_cell_numbers


def copy_from_geo_to_ertbox_grid(
        project,
        geo_grid_model_name: str,
        ertbox_grid_model_name: str,
        zone_dict: dict,
        extrapolation_method: ExtrapolationMethod,
        debug_level: Debug,
        save_active_param=False,
        normalize_trend=False,
        not_aps_workflow=False,
):
    """
    zone_dict[zone_name] = (zone_number, region_number, conformity, param_name_list)
    extrapolation_method is one of: 
        ZERO -  where all undefined cells get 0 as value
        MEAN - where all undefined cells get mean value of defined cell values
        EXTEND_LAYER_MEAN - where all undefined values in a layer is replaced by the
                           layer average. For undefined grid cells above or below the layers
                           having some defined values, the upper most defined cell value
                           is copied to all undefined cell values above this cell
                           for each cell column and bottom most defined cell value
                           is copied to all undefined cell values below this cell
                           for each cell column.
        REPEAT_LAYER_MEAN - where all undefined values in a layer is replaced by the
                           layer average. For undefined cells above the uppermost active cell
                           are assigned the values of the active cells in the same
                           column but in reverse order to avoid discontinuity at
                           at the border between the initially active and undefined cell values.
                           If the number of active cells in a column is less than the undefined
                           cells above the uppermost active cell, they will be assigned a constant
                           value in the same way as option EXTEND_LAYER_MEAN. The same procedure
                           is used to fill in inactive cell values below lowermost active cell.  
     """
    if project.current_realisation > 0:
        raise ValueError('In RMS models to be used with a FMU loop in ERT,'
                         'the grid and parameters should be shared and realisation = 1'
        )

    geogrid_model, geogrid = get_grid_model(project,geo_grid_model_name)
    ertbox_grid_model, ertboxgrid = get_grid_model(project,ertbox_grid_model_name)

    # Both ERTBOX grid and geogrid should have same nx, ny dimensions
    # nz is here the geogrid number of layers for all zones
    # nz_ertbox is number of layers in total in ERTBOX grid
    nx, ny, nz, nz_ertbox = check_and_get_grid_dimensions(
        geogrid,ertboxgrid,
        geo_grid_model_name, ertbox_grid_model_name)

    number_layers_per_zone, start_layers_per_zone, end_layers_per_zone = get_zone_layer_numbering(geogrid)


    # Get parameter names from model specification
    for zone_name, zone_item in zone_dict.items():
        zone_number, _ , conformity, param_name_list = zone_item
        zone_index = zone_number - 1
        number_layers = number_layers_per_zone[zone_index]
        start_layer = start_layers_per_zone[zone_index]
        end_layer = end_layers_per_zone[zone_index]
        if number_layers > nz_ertbox:
            raise ValueError(
                f"Number of layers of {ertbox_grid_model_name} ({nz_ertbox}) "
                f"is less than number of layers in {geo_grid_model_name} ({number_layers})"
                f"for zone {zone_name}."
            )
        if debug_level >= Debug.VERY_VERBOSE:
            print(
                f"--- zone name: {zone_name}\n"
                f"--- number_layers: {number_layers}\n"
                f"--- start_layer: {start_layer}  end_layer: {end_layer}\n"
            )

        i_indices, j_indices, k_indices, zone_cell_numbers = \
            get_grid_indices(geogrid, nx, ny, start_layer, end_layer)

        for param_name in param_name_list:
            param_values_active = get_param_values(
                geo_grid_model_name, 
                geogrid_model,
                param_name)

            if debug_level >= Debug.VERBOSE:
                print(f"-- Zone: {zone_name} Parameter:{param_name} ")

            # Define active parameter for geogrid
            active_3d = np.zeros((nx,ny,nz),dtype=np.int32)
            active_3d[i_indices,j_indices,k_indices] = 1

            # Mask all values for geogrid parameter except the active values within the zone
            param_values_3d_all = ma.masked_all((nx, ny, nz), dtype=np.float32)
            param_values_3d_all[i_indices,j_indices,k_indices] = param_values_active[zone_cell_numbers]

            # Initially mask all values for ertbox parameter
            ertbox_values_3d_masked = ma.masked_all((nx,ny,nz_ertbox), dtype=np.float32)
            ertbox_active_3d = np.zeros((nx,ny,nz_ertbox), dtype=np.uint8)

            if debug_level >= Debug.VERY_VERBOSE:
                print(
                    f"--- Parameter {param_name}  for zone: {zone_name} "
                    f"is copied to {ertbox_grid_model_name}."
                )

            # The RMS simbox layers (num_layers) are copied into ertbox grid 
            # at top if grid layout is top conform or proportional and
            # at the bottom if grid layout is base conform.
            # Must be consistent with 'extract_values_from_fmu_grid_to_geogrid_simbox' 
            # in export_fields_to_disk.py
            if conformity in [Conform.BaseConform]:
                # Only copy the geogrid layers for the zone into the lowermost ertbox layers
                ertbox_values_3d_masked[:,:,-number_layers:] = \
                    param_values_3d_all[:,:,start_layer:(end_layer+1)]

                ertbox_active_3d[:,:,-number_layers:] = \
                        active_3d[:,:,start_layer:(end_layer+1)]

            elif conformity in[Conform.TopConform, Conform.Proportional]:
                # Only copy the geogrid layers for the zone into the uppermost ertbox layers
                ertbox_values_3d_masked[:,:,0:number_layers] = \
                    param_values_3d_all[:,:,start_layer:(end_layer+1)]

                ertbox_active_3d[:,:,0:number_layers] = \
                        active_3d[:,:,start_layer:(end_layer+1)]

            else:
                raise NotImplementedError(
                    f"Grid conformity: {conformity} is not supported."
                )

            mean = ma.mean(ertbox_values_3d_masked)
            if debug_level >= Debug.VERBOSE:
                if extrapolation_method is not None:
                    print(f"-- Extrapolate parameter using option: {extrapolation_method}")


            vertical_methods = \
                (ExtrapolationMethod.EXTEND,ExtrapolationMethod.REPEAT)
            vertical_horizontal_methods = \
                (ExtrapolationMethod.EXTEND_LAYER_MEAN,ExtrapolationMethod.REPEAT_LAYER_MEAN)
            if extrapolation_method in vertical_horizontal_methods:
                ertbox_values_3d_masked = \
                assign_undefined_lateral(nz_ertbox, ertbox_values_3d_masked)

            if extrapolation_method == ExtrapolationMethod.ZERO:
                ertbox_values_3d = assign_undefined_constant(
                        ertbox_values_3d_masked, 0.0, debug_level)

            elif extrapolation_method == ExtrapolationMethod.MEAN:
                ertbox_values_3d = assign_undefined_constant(
                        ertbox_values_3d_masked, mean, debug_level)

            elif (extrapolation_method in vertical_methods) or \
                    (extrapolation_method in vertical_horizontal_methods):
                ertbox_values_3d = assign_undefined_vertical(
                        extrapolation_method, nx, ny, nz_ertbox, ertbox_values_3d_masked, mean)

            else:
                raise ValueError(
                    f"Extrapolation method:{extrapolation_method} is not implemented."
                )
            ertbox_active = np.reshape(ertbox_active_3d, nx*ny*nz_ertbox)
            ertbox_values = np.reshape(ertbox_values_3d, nx*ny*nz_ertbox)

            # Create and save a parameter for grid cells in ERTBOX 
            # corresponding to active cells from geomodel for current geomodel zone
            prefix = "aps_"
            if not_aps_workflow:
                prefix = ""
            if save_active_param:
                active_param_name = prefix + zone_name + "_active"
                ertbox_active_param = ertbox_grid_model.properties.create(active_param_name,
                    property_type=roxar.GridPropertyType.discrete,
                    data_type=np.uint8)

                if debug_level >= Debug.VERBOSE:
                    print(f"-- Update parameter: {active_param_name}")
                ertbox_active_param.set_values(ertbox_active)


            # Normalize values to be between 0 and 1 within this zone
            if normalize_trend:
                if debug_level >= Debug.VERBOSE:
                    print(f"-- Normalize parameter: {param_name} ")
                selected_values = ertbox_values[ertbox_active == 1]
                minval = selected_values.min()
                maxval = selected_values.max()
                minmax_diff = maxval - minval
                if minmax_diff > 0.000001:
                    ertbox_values = (ertbox_values - minval)/(minmax_diff)


            # Create ertbox properties if not already existing
            full_param_name = prefix + zone_name + "_" + param_name
            ertbox_param = ertbox_grid_model.properties.create(full_param_name,
                property_type=roxar.GridPropertyType.continuous,
                data_type=np.float32)
            if debug_level >= Debug.VERBOSE:
                if normalize_trend:
                    print(f"-- Update parameter (normalized): {full_param_name}")
                else:
                    print(f"-- Update parameter: {full_param_name}")
            ertbox_param.set_values(ertbox_values)


def run(*, project, 
    save_active_param=True,
    normalize_trend=True, 
        **kwargs):
    """
    Read the APS model and find specifications of user defined trends
    for GRF fields and copy the trend parameters from geomodel to ertbox model.
    The undefined grid cell values in ertbox grid is assigned values. The method
    for assigning values to undefined grid cell values is choosen by the user,
    and the implemented methods are:
    ZERO - All undefined cell values are assigned 0 as value.
    MEAN - All undefined cell values are assigned the mean value calculated 
           by using the defined cell values.
    EXTEND_LAYER_MEAN -  See doc string for copy_from_geo_to_ertbox_grid.
    REPEAT_LAYER_MEAN - See doc string for copy_from_geo_to_ertbox_grid.
    """
    if not (kwargs['fmu_mode'] and kwargs['fmu_simulate_fields']):
            return

    if project.current_realisation > 0:
        raise ValueError(f'In RMS models to be used with a FMU loop in ERT,'
                         'the grid and parameters should be shared and realisation = 1'
        )

    aps_model = kwargs['aps_model']
    geo_grid_model_name = aps_model.grid_model_name
    ertbox_grid_model_name = kwargs['fmu_simulation_grid_name']
    debug_level = kwargs['debug_level']
    trend_extrapolation_method = kwargs['extrapolation_method']
    zone_dict, use_rms_param_trend = get_trend_param_names_from_aps_model(
            project,
            aps_model,
            ertbox_grid_model_name,
            debug_level)

    if not use_rms_param_trend: 
        return


    print(
        f"\nCopy RMS 3D trend parameters from {geo_grid_model_name} "
        f"to {ertbox_grid_model_name}"
    )
    copy_from_geo_to_ertbox_grid(
            project,
            geo_grid_model_name,
            ertbox_grid_model_name,
            zone_dict,
            trend_extrapolation_method,
            debug_level,
            save_active_param=save_active_param,
            normalize_trend=normalize_trend)

    if debug_level >= Debug.ON:
        print(f"- Finished copy rms trend parameters to {ertbox_grid_model_name} ")

