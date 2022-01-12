from aps.utils.constants.simple import Debug
from aps.utils.grid import update_rms_parameter
from aps.utils.roxar.grid_model import find_defined_cells, create_zone_parameter, getDiscrete3DParameterValues
from aps.utils.simulation import initialize_rms_parameters


def add_trend_to_gauss_field(
        project, aps_model,
        zone_number, region_number, use_regions,
        gauss_field_name,
        gauss_field_values,
        cell_index_defined,
        fmu_mode=False,
):
    '''
    Calculate trend and add trend to simulated gaussian residual field to get the
    gaussian field with trend. Standard deviation for residual field is calculated
    by using the specified relative standard deviation and the
    trend max minus min of trend function. Returns gauss field where the grid
    cells defined by cell_index_defined are updated. All other grid cell values
    are not modified. The lenght of this array is equal to the length of all
    active grid cells in the grid model. Returns also trend values in a separate
    array, but this array has length equal to cell_index_defined and does only
    contain the values for the grid cells that are selected by cell_index_defined.
    '''
    grid_model_name = aps_model.grid_model_name
    realization_number = project.current_realisation
    grid_model = project.grid_models[grid_model_name]
    debug_level = aps_model.debug_level
    key = (zone_number, region_number)
    zone_model = aps_model.sorted_zone_models[key]

    # Get trend model, relative standard deviation
    _, trend_model, rel_std_dev, _ = zone_model.getTrendModel(gauss_field_name)

    if debug_level >= Debug.VERBOSE:
        trend_type = trend_model.type.name
        if use_regions:
            print(
                f'-- Calculate trend for: {gauss_field_name} for (zone,region)=({zone_number}, {region_number})\n'
                f'-- Trend type: {trend_type}'
            )
        else:
            print(
                f'-- Calculate trend for: {gauss_field_name} for zone: {zone_number}\n'
                f'-- Trend type: {trend_type}'
            )

    sim_box_thickness = zone_model.sim_box_thickness
    # trend_values contain trend values for the cells belonging to the set defined by cell_index_defined
    minmax_difference, trend_values = trend_model.createTrend(
        grid_model,
        realization_number,
        cell_index_defined,
        zone_number=1 if fmu_mode else zone_number,
        sim_box_thickness=sim_box_thickness,
    )

    # Calculate trend plus residual for the cells defined by cell_index_defined
    # and replace the residual values by trend + residual in array: gauss_field_values
    sigma = rel_std_dev * minmax_difference
    residual_values = gauss_field_values[cell_index_defined]
    val = trend_values + sigma * residual_values
    # updates array values for the selected grid cells
    gauss_field_values[cell_index_defined] = val
    if debug_level >= Debug.VERY_VERBOSE:
        print(f'--- Number of active cells:{len(cell_index_defined)} ')
        print(f'--- Trend minmax_difference = {minmax_difference}')
        print(f'--- SimBoxThickness = {sim_box_thickness}')
        print(f'--- RelStdDev = {rel_std_dev}')
        print(f'--- Sigma = {sigma}')
        print(f'--- Min trend, max trend    :  {trend_values.min()}  {trend_values.max()}')
        print(f'--- Residual min,max        :  {sigma * residual_values.min()}  {sigma * residual_values.max()}')
        print(f'--- Trend + residual min,max:  {val.min()}  {val.max()}')

    return gauss_field_values


def add_trends(
        project,
        aps_model,
        zone_number,
        region_number,
        write_rms_parameters_for_qc_purpose=False,
        debug_level=Debug.OFF,
        fmu_mode=False,
        is_shared=False,
):
    grid_model = project.grid_models[aps_model.grid_model_name]
    zone_model = aps_model.getZoneModel(zone_number, region_number)
    gf_names_for_zone = zone_model.used_gaussian_field_names
    gf_names_for_truncation_rule = zone_model.getGaussFieldsInTruncationRule()
    realization_number = project.current_realisation
    # Initialize dictionaries keeping gauss field values and trends for all used gauss fields
    if fmu_mode:
        write_rms_parameters_for_qc_purpose = False

    gf_all_values, gf_all_alpha = initialize_rms_parameters(
        project, aps_model, write_rms_parameters_for_qc_purpose, is_shared=is_shared
    )
    cell_index_defined = get_defined_cells(
        project, aps_model, grid_model, region_number, zone_number, debug_level, fmu_mode,
    )

    for gf_name in gf_names_for_zone:
        if gf_name in gf_names_for_truncation_rule:
            gauss_field_values_all = gf_all_values[gf_name]
            if zone_model.hasTrendModel(gf_name):
                add_trends_to_field(
                    project,
                    aps_model,
                    grid_model,
                    cell_index_defined,
                    gauss_field_values_all,
                    gf_name,
                    realization_number,
                    region_number,
                    zone_number,
                    write_rms_parameters_for_qc_purpose,
                    debug_level,
                    fmu_mode=fmu_mode,
                    is_shared=is_shared,
                )


def get_defined_cells(
        project,
        aps_model,
        grid_model,
        region_number,
        zone_number,
        debug_level=Debug.OFF,
        fmu_mode=False,
):
    realization_number = project.current_realisation
    # zone parameter is created if it does not exist
    zone_param = create_zone_parameter(
        grid_model,
        name=aps_model.zone_parameter,
        realization_number=realization_number,
        set_shared=False,
        debug_level=debug_level,
        create_new=fmu_mode,
    )
    region_values = None
    if aps_model.use_regions:
        region_values, _ = getDiscrete3DParameterValues(grid_model, aps_model.region_parameter, realization_number, debug_level)
    zone_values = zone_param.get_values(realization_number)
    if fmu_mode:
        zone_number = 1
    return find_defined_cells(
        zone_values, zone_number, region_values, region_number, debug_level=debug_level,
    )


def add_trends_to_field(
        project,
        aps_model,
        grid_model,
        cell_index_defined,
        gauss_field_values_all,
        gf_name,
        realization_number,
        region_number,
        zone_number,
        write_rms_parameters_for_qc_purpose=False,
        debug_level=Debug.OFF,
        fmu_mode=False,
        is_shared=False,
):
    use_regions = aps_model.use_regions
    gauss_field_values_all = add_trend_to_gauss_field(
        project, aps_model, zone_number, region_number,
        use_regions, gf_name, gauss_field_values_all, cell_index_defined,
        fmu_mode,
    )

    # Write back to RMS project the untransformed gaussian values with trend for the zone
    if debug_level >= Debug.VERBOSE:
        print(f'-- Add trend to: {gf_name}')
    update_rms_parameter(
        grid_model,
        gf_name,
        gauss_field_values_all,
        cell_index_defined,
        realization_number,
        use_regions=use_regions,
        zone_number=zone_number,
        region_number=region_number,
        debug_level=debug_level,
        is_shared=is_shared,
    )

    return gauss_field_values_all
