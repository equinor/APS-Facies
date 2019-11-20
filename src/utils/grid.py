from src.utils.constants.simple import Debug
from src.utils.roxar.generalFunctionsUsingRoxAPI import updateContinuous3DParameterValues


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
):
    # Write back to RMS project the updated rms 3D parameter
    if variable_name_extension is None:
        rms_variable_name = gauss_field_name
    else:
        rms_variable_name = gauss_field_name + '_' + variable_name_extension

    updateContinuous3DParameterValues(
        grid_model,
        rms_variable_name,
        values,
        cell_index_defined,
        realization_number,
        isShared=False, setInitialValues=False,
        debug_level=debug_level
    )
    if debug_level >= Debug.VERBOSE:
        if use_regions:
            print('--- Create or update parameter: {} for (zone,region)= ({},{})'.format(rms_variable_name, zone_number, region_number))
        else:
            print('--- Create or update parameter: {} for zone number: {}'.format(rms_variable_name, zone_number))
