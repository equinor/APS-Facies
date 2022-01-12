from aps.utils.constants.simple import Debug
from aps.utils.roxar.generalFunctionsUsingRoxAPI import update_continuous_3d_parameter_values


def update_rms_parameter(
        grid_model,
        gauss_field_name,
        values,
        cell_index_defined,
        realization_number,
        variable_name_extension=None,
        use_regions=False,
        zone_number=0,
        region_number=0,
        debug_level=Debug.OFF,
        is_shared=False,
):
    # Write back to RMS project the updated rms 3D parameter
    if variable_name_extension is None:
        rms_variable_name = gauss_field_name
    else:
        rms_variable_name = gauss_field_name + '_' + variable_name_extension

    update_continuous_3d_parameter_values(
        grid_model,
        rms_variable_name,
        values,
        cell_index_defined,
        realization_number,
        is_shared=is_shared,
        set_initial_values=False,
        debug_level=debug_level
    )
    if debug_level >= Debug.VERY_VERBOSE:
        if use_regions:
            print(f'--- Create or update parameter: {rms_variable_name} for (zone,region)= ({zone_number}, {region_number}')
        else:
            print(f'--- Create or update parameter: {rms_variable_name} for zone number: {zone_number}')
