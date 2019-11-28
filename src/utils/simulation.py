from collections import OrderedDict

import numpy as np

from src.utils.constants.simple import Debug
from src.utils.roxar.generalFunctionsUsingRoxAPI import setContinuous3DParameterValues
from src.utils.roxar.grid_model import getContinuous3DParameterValues


def get_all_gauss_field_names_in_model(aps_model):
    '''
    Returns the lists:
         - all gauss field names specified in any zone in the whole model
         - all gauss field names used in one or more zones in the whole model
    Returns also a list with all gauss field names used in at least one zone and which has trend.
    '''
    all_zone_models = aps_model.sorted_zone_models
    gauss_field_names_specified = []
    gauss_field_names_used = []
    gauss_field_names_with_trend = []
    for key, zone_model in all_zone_models.items():
        zone_number = key[0]
        region_number = key[1]
        if not aps_model.isSelected(zone_number, region_number):
            continue

        zone_model = aps_model.getZoneModel(zone_number, region_number)

        # Gauss fields defined for the zone in model file
        gf_names_for_zone = zone_model.used_gaussian_field_names

        # Gauss fields used in truncation rule for the zone in model file
        gf_names_for_truncation_rule = zone_model.getGaussFieldsInTruncationRule()

        for name in gf_names_for_zone:
            if name not in gauss_field_names_specified:
                gauss_field_names_specified.append(name)
            if name in gf_names_for_truncation_rule:
                if name not in gauss_field_names_used:
                    gauss_field_names_used.append(name)
                if zone_model.hasTrendModel(name):
                    if name not in gauss_field_names_with_trend:
                        gauss_field_names_with_trend.append(name)

    return gauss_field_names_specified, gauss_field_names_used, gauss_field_names_with_trend


def initialize_rms_parameters(project, aps_model, write_rms_parameters_for_qc_purpose=False):
    '''
    Returns dictionaries with numpy arrays containing the gauss field values, trend values,
    transformed gauss field values for each gauss field name. The key is gauss field name.
    '''
    grid_model_name = aps_model.getGridModelName()
    realization_number = project.current_realisation
    grid_model = project.grid_models[grid_model_name]
    number_of_active_cells = grid_model.get_grid(realization_number).defined_cell_count
    debug_level = aps_model.debug_level

    def _get_field(name_):
        return getContinuous3DParameterValues(grid_model, name_, realization_number)

    # all_gauss_field_names is a list of all gauss fields used in at least one zone
    # all_gauss_field_names_with_trend is a list of all gauss fields used in at least one zone and which has trend
    (
        gauss_field_names_specified,
        gauss_field_names_used,
        gauss_field_names_with_trend,
    ) = get_all_gauss_field_names_in_model(aps_model)

    # Keeps all simulated gauss fields (residual fields)
    gf_all_values = OrderedDict()

    # Keeps all transformed gauss fields (gauss field with trends that are transformed to [0,1] distribution)
    gf_all_alpha = OrderedDict()

    # Keeps all trend values  and untransformed gauss fields with trend
    gf_all_trend_values = OrderedDict()

    # Initialize all values to 0
    if debug_level >= Debug.VERBOSE:
        print('--- Initialize values for:')
    for name in gauss_field_names_used:
        gf_all_values[name] = np.zeros(number_of_active_cells, np.float32)
        gf_all_alpha[name] = np.zeros(number_of_active_cells, np.float32)
        if debug_level >= Debug.VERBOSE:
            print('---    {}'.format(name))

    # Simulated gauss fields that are used in some zones are read from RMS
    # They are required and must exist.
    for name in gauss_field_names_used:
        try:
            values = _get_field(name)
            gf_all_values[name] = values
        except ValueError:
            setContinuous3DParameterValues(
                grid_model, name, gf_all_values[name], [], realization_number
            )

    # Initialize the RMS 3D parameters for QC with extension _trend, _transf, _untransf
    if write_rms_parameters_for_qc_purpose:
        # Write initial values to transformed gauss parameters
        zone_number_list = []
        for name in gauss_field_names_used:
            parameter_name = name + '_transf'
            input_values = gf_all_alpha[name]
            setContinuous3DParameterValues(
                grid_model, parameter_name, input_values,
                zone_number_list, realization_number
            )

        if len(gauss_field_names_with_trend) > 0:
            if debug_level >= Debug.VERBOSE:
                print('--- Initialize trend values for:')
            for name in gauss_field_names_with_trend:
                gf_all_trend_values[name] = np.zeros(number_of_active_cells, np.float32)
                if debug_level >= Debug.VERBOSE:
                    print('---    {}'.format(name))

            # Write initial values to trend gauss parameters
            for name in gauss_field_names_with_trend:
                parameter_name = name + '_trend'
                input_values = gf_all_trend_values[name]
                setContinuous3DParameterValues(
                    grid_model, parameter_name, input_values,
                    zone_number_list, realization_number
                )

    return gf_all_values, gf_all_alpha, gf_all_trend_values
