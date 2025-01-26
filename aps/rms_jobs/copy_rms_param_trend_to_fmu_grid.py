"""This module is used in FMU workflows to copy gaussian field values from
geomodel grid to ERTBOX grid and extrapolate values that are undefined
in ERTBOX grid. This functionality is used when the user wants to
apply customized trends for GRF's in APS and run this in FMU with AHM.
"""

from aps.algorithms.APSModel import APSModel
from aps.utils.constants.simple import (
    Debug,
    TrendType,
)
from aps.utils.roxar.grid_model import (
    get_zone_layer_numbering,
    get_zone_names,
    get_grid_model,
)
from aps.utils.roxar.progress_bar import APSProgressBar
from aps.utils.roxar.get_conformity_from_rms import check_grid_layout

# The functionality to copy between geogrid and ertbox grid is now placed
# in fmu.tools.rms function
# TODO: This will not work before fmu.tools has merged the copy_rms_param_to_ertbox_grid
from fmu.tools.rms.copy_rms_param_to_ertbox_grid import (
    define_active_parameters_in_ertbox,
    copy_from_geo_to_ertbox_grid,
)


def get_trend_param_names_from_aps_model(
    project,
    aps_model: APSModel,
    ertbox_grid_model_name: str,
    debug_level: Debug = Debug.OFF,
):
    """
    Returns a dict where key is zone name and the value is a tuple with zone related data.
    """
    geo_grid_model_name = aps_model.grid_model_name
    geogrid_model, geogrid = get_grid_model(project, geo_grid_model_name)
    _, ertboxgrid = get_grid_model(project, ertbox_grid_model_name)
    zone_names = get_zone_names(geogrid_model)
    number_layers_per_zone, _, _ = get_zone_layer_numbering(geogrid)
    nz_ertbox = ertboxgrid.simbox_indexer.dimensions[2]
    real_number = project.current_realisation

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
        check_grid_layout(
            geo_grid_model_name,
            zone_number,
            zone_model.grid_layout,
            debug_level=debug_level,
        )

        number_layers = number_layers_per_zone[zone_number - 1]

        if number_layers > nz_ertbox:
            raise ValueError(
                f'Number of layers nz of {ertbox_grid_model_name}: ({nz_ertbox}) '
                f'is less than number of layers in {geo_grid_model_name}: ({number_layers})  '
                f'for zone {zone_name}'
            )
        if debug_level >= Debug.VERY_VERBOSE:
            print(f'--- In module: {__name__} ')
            print(f'--- zone number: {zone_number}')
            print(f'--- zone name: {zone_name}')
            print(f'--- region number: {region_number}')
            print(f'--- zone conformity: {zone_model.grid_layout}')

        gauss_field_names = zone_model.gaussian_fields_in_truncation_rule
        param_name_list = []
        for gauss_field_name in gauss_field_names:
            if zone_model.hasTrendModel(gauss_field_name):
                _, trend_model, _, _ = zone_model.getTrendModel(gauss_field_name)
                trend_type = trend_model.type
                if trend_type == TrendType.RMS_PARAM:
                    trend_param_name = trend_model.trend_parameter_name
                    if trend_param_name not in geogrid_model.properties:
                        raise ValueError(
                            f'The 3D parameter {trend_param_name} does not exist '
                            f'in grid model {geo_grid_model_name}'
                        )

                    trend_param = geogrid_model.properties[trend_param_name]
                    if trend_param.is_empty(realisation=real_number):
                        raise ValueError(
                            f'Grid parameter {trend_param_name} for {geo_grid_model_name} '
                            'is empty. Must be non-empty.'
                        )
                    param_name_list.append(trend_param_name)

        zone_dict[zone_name] = (
            zone_number,
            region_number,
            zone_model.grid_layout.value,
            param_name_list,
        )
        if len(param_name_list) > 0:
            use_rms_param_trend = True
    return zone_dict, use_rms_param_trend


def run(
    *,
    project,
    save_active_param_to_ertbox=True,
    save_region_param_to_ertbox=False,
    normalize_trend=True,
    **kwargs,
):
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
    if 'fmu_mode' in kwargs and 'fmu_simulate_fields' in kwargs:
        if not (kwargs['fmu_mode'] and kwargs['fmu_simulate_fields']):
            return

    aps_model = kwargs['aps_model']
    geo_grid_model_name = aps_model.grid_model_name

    if save_region_param_to_ertbox:
        region_param_name = aps_model.region_parameter
        discrete_param_names = []
        discrete_param_names.append(region_param_name)

    ertbox_grid_model_name = kwargs['fmu_simulation_grid_name']
    debug_level = kwargs['debug_level']
    trend_extrapolation_method = kwargs['extrapolation_method']
    zone_dict, use_rms_param_trend = get_trend_param_names_from_aps_model(
        project, aps_model, ertbox_grid_model_name, debug_level=debug_level
    )

    # Independent of using custom trends or not we can save active parameter in ertbox
    # corresponding to the geomodel zone.
    if save_active_param_to_ertbox:
        define_active_parameters_in_ertbox(
            project,
            geo_grid_model_name,
            ertbox_grid_model_name,
            zone_dict,
            debug_level=int(debug_level),
        )

    if save_region_param_to_ertbox:
        copy_from_geo_to_ertbox_grid(
            project,
            geo_grid_model_name,
            ertbox_grid_model_name,
            zone_dict,
            trend_extrapolation_method.value,
            discrete_param_names=discrete_param_names,
            debug_level=int(debug_level),
        )

    if not use_rms_param_trend:
        # No trend parameters to copy from geogrid to ertbox grid
        return

    print(
        f'\nCopy RMS 3D trend parameters from {geo_grid_model_name} '
        f'to {ertbox_grid_model_name}'
    )
    # Copy and extrapolate the custom trends made in geogrid over to ertbox grid
    # Skip saving active parameter since already done
    copy_from_geo_to_ertbox_grid(
        project,
        geo_grid_model_name,
        ertbox_grid_model_name,
        zone_dict,
        trend_extrapolation_method.value,
        debug_level=int(debug_level),
        normalize_trend=normalize_trend,
    )

    if debug_level >= Debug.ON:
        print(f'- Finished copy rms trend parameters to {ertbox_grid_model_name} ')

    APSProgressBar.increment()
