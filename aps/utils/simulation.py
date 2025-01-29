from collections import OrderedDict
import numpy as np

from aps.utils.constants.simple import Debug
from aps.utils.roxar.generalFunctionsUsingRoxAPI import (
    set_continuous_3d_parameter_values,
)
from aps.utils.roxar.grid_model import getContinuous3DParameterValues


def get_all_gauss_field_names_in_model(aps_model):
    """
    Returns the lists:
        - all gauss field names used in one or more zones in the whole model
        - all gauss field names used in at least one zone and which has trend.
    """
    all_zone_models = aps_model.sorted_zone_models
    gauss_field_names_used = []
    gauss_field_names_with_trend = []
    for key, zone_model in all_zone_models.items():
        zone_number, region_number = key
        if not aps_model.isSelected(zone_number, region_number):
            continue

        zone_model = aps_model.getZoneModel(zone_number, region_number)

        # Gauss fields defined for the zone in model file
        gf_names_for_zone = zone_model.used_gaussian_field_names

        # Gauss fields used in truncation rule for the zone in model file
        gf_names_for_truncation_rule = zone_model.getGaussFieldsInTruncationRule()

        for name in gf_names_for_zone:
            if name in gf_names_for_truncation_rule:
                if name not in gauss_field_names_used:
                    gauss_field_names_used.append(name)
                if (
                    zone_model.hasTrendModel(name)
                    and name not in gauss_field_names_with_trend
                ):
                    gauss_field_names_with_trend.append(name)

    return gauss_field_names_used, gauss_field_names_with_trend


def init_rms_param(
    grid_model,
    name,
    param_type_name,
    number_of_active_cells,
    realization_number,
    set_rms_param=False,
    is_shared=False,
    debug_level=Debug.OFF,
):
    parameter_name = name if param_type_name is None else name + param_type_name
    try:
        # Check if values exists and get it, otherwise use the initial values
        values = getContinuous3DParameterValues(
            grid_model, parameter_name, realization_number
        )
    except ValueError:
        # Set initial values for parameters that are not simulated
        values = np.zeros(number_of_active_cells, np.float32)
        if set_rms_param:
            set_continuous_3d_parameter_values(
                grid_model,
                parameter_name,
                values,
                [],
                realization_number,
                is_shared=is_shared,
                debug_level=debug_level,
            )
    return values


def initialize_rms_parameters(
    project,
    aps_model,
    active_output_variable_list,
    write_rms_parameters_for_qc_purpose=False,
    is_shared=True,
    debug_level=Debug.OFF,
    fmu_with_residual_grf=False,
):
    """
    Returns dictionaries with numpy arrays containing the gauss field values, trend values,
    transformed gauss field values for each gauss field name. The key is gauss field name.
    The return parameters are of length equal to number of active cells.

    """
    if len(active_output_variable_list) == 0:
        raise ValueError(f'Need to specify which variables to initialize')
    grid_model_name = aps_model.grid_model_name
    realization_number = project.current_realisation
    grid_model = project.grid_models[grid_model_name]
    number_of_active_cells = grid_model.get_grid(realization_number).defined_cell_count

    # all_gauss_field_names is a list of all gauss fields used in at least one zone
    # all_gauss_field_names_with_trend is a list of all gauss fields used in at least one zone and which has trend
    gauss_field_names_used, gauss_field_names_with_trend = (
        get_all_gauss_field_names_in_model(aps_model)
    )

    # Keeps all simulated gauss fields (residual fields)
    gf_all_values = OrderedDict()

    # Keeps all transformed gauss fields (gauss field with trends that are transformed to [0,1] distribution)
    gf_all_alpha = OrderedDict()

    # Keeps all trend values  and untransformed gauss fields with trend
    gf_all_trend_values = OrderedDict()

    # Keeps all GRF without added trend
    gf_all_residual_values = OrderedDict()

    # Initialize to 0 or read from RMS simulated gauss fields, trends, transformed values
    # that are used.
    set_rms_param = write_rms_parameters_for_qc_purpose
    for name in gauss_field_names_used:
        if active_output_variable_list[0]:
            # Simulated GRF
            gf_all_values[name] = init_rms_param(
                grid_model,
                name,
                None,
                number_of_active_cells,
                realization_number,
                True,
                is_shared,
                debug_level=debug_level,
            )
        if active_output_variable_list[1]:
            # Transformed GRF
            gf_all_alpha[name] = init_rms_param(
                grid_model,
                name,
                '_transf',
                number_of_active_cells,
                realization_number,
                set_rms_param,
                is_shared,
                debug_level=debug_level,
            )

    for name in gauss_field_names_with_trend:
        if active_output_variable_list[2]:
            # Trend for GRF
            gf_all_trend_values[name] = init_rms_param(
                grid_model,
                name,
                '_trend',
                number_of_active_cells,
                realization_number,
                set_rms_param,
                is_shared,
                debug_level=debug_level,
            )
        if fmu_with_residual_grf and active_output_variable_list[3]:
            # Residual GRF
            gf_all_residual_values[name] = init_rms_param(
                grid_model,
                name,
                '_residual',
                number_of_active_cells,
                realization_number,
                set_rms_param,
                is_shared,
                debug_level=debug_level,
            )

    return gf_all_values, gf_all_alpha, gf_all_trend_values, gf_all_residual_values
