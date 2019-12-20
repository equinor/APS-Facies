from src.utils.constants.simple import Debug
from src.utils.grid import update_rms_parameter
from src.utils.roxar.grid_model import find_defined_cells, create_zone_parameter, getDiscrete3DParameterValues
from src.utils.simulation import initialize_rms_parameters


def add_trend_to_gauss_field(
        project, aps_model,
        zone_number, region_number, use_regions,
        gauss_field_name,
        gauss_field_values,
        cell_index_defined,
        fmu_mode=False,
):
    '''
    Calculate trend and add trend to simulated gaussian residual field to get the gaussian field with trend.
    Standard deviation for residual field is calculated by using the specified relative standard deviation and the trend max minus min of trend function.
    Returns gauss field where the grid cells defined by cell_index_defined are updated. All other grid cell values are not modified.
    The lenght of this array is equal to the length of all active grid cells in the grid model.
    Returns also trend values in a separate array, but this array has length equal to cell_index_defined and does only contain the values for the grid cells
    that are selected by cell_index_defined.
    '''
    grid_model_name = aps_model.getGridModelName()
    realization_number = project.current_realisation
    grid_model = project.grid_models[grid_model_name]
    debug_level = aps_model.debug_level
    key = (zone_number, region_number)
    zone_model = aps_model.sorted_zone_models[key]

    # Get trend model, relative standard deviation
    use_trend, trend_model, rel_std_dev, rel_std_dev_fmu = zone_model.getTrendModel(gauss_field_name)

    if debug_level >= Debug.VERBOSE:
        trend_type = trend_model.type.name
        if use_regions:
            print(
                '--- Calculate trend for: {} for (zone,region)=({},{})\n'
                '--- Trend type: {}'
                ''.format(gauss_field_name, zone_number, region_number, trend_type)
            )
        else:
            print(
                '--- Calculate trend for: {} for zone: {}\n'
                '--- Trend type: {}'
                ''.format(gauss_field_name, zone_number, trend_type)
            )

    sim_box_thickness = zone_model.getSimBoxThickness()
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
        print('Debug output: Trend minmax_difference = ' + str(minmax_difference))
        print('Debug output: SimBoxThickness = ' + str(sim_box_thickness))
        print('Debug output: RelStdDev = ' + str(rel_std_dev))
        print('Debug output: Sigma = ' + str(sigma))
        print('Debug output: Min trend, max trend    : ' + str(trend_values.min()) + ' ' + str(trend_values.max()))
        print('Debug output: Residual min,max        : ' + str(sigma * residual_values.min()) + ' ' + str(sigma * residual_values.max()))
        print('Debug output: trend + residual min,max: ' + str(val.min()) + ' ' + str(val.max()))

    return gauss_field_values, trend_values


def add_trends(
        project,
        aps_model,
        zone_number,
        region_number,
        write_rms_parameters_for_qc_purpose=False,
        debug_level=Debug.OFF,
        fmu_mode=False,
):
    grid_model = project.grid_models[aps_model.getGridModelName()]
    zone_model = aps_model.getZoneModel(zone_number, region_number)
    gf_names_for_zone = zone_model.used_gaussian_field_names
    gf_names_for_truncation_rule = zone_model.getGaussFieldsInTruncationRule()
    realization_number = project.current_realisation
    # Initialize dictionaries keeping gauss field values and trends for all used gauss fields
    if fmu_mode:
        write_rms_parameters_for_qc_purpose = False
    gf_all_values, gf_all_alpha, gf_all_trend_values = initialize_rms_parameters(
        project, aps_model, write_rms_parameters_for_qc_purpose
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
                    gf_all_trend_values,
                    gf_name,
                    realization_number,
                    region_number,
                    zone_number,
                    write_rms_parameters_for_qc_purpose,
                    debug_level,
                    fmu_mode=fmu_mode,
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
    zone_param = create_zone_parameter(
        grid_model,
        name=aps_model.zone_parameter,
        realization_number=realization_number,
        set_shared=False,
        debug_level=debug_level,
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
        gf_all_trend_values,
        gf_name,
        realization_number,
        region_number,
        zone_number,
        write_rms_parameters_for_qc_purpose=False,
        debug_level=Debug.OFF,
        fmu_mode=False,
):
    use_regions = aps_model.use_regions
    gauss_field_values_all, trend_values_for_zone = add_trend_to_gauss_field(
        project, aps_model, zone_number, region_number,
        use_regions, gf_name, gauss_field_values_all, cell_index_defined,
        fmu_mode
    )

    # Write back to RMS project the untransformed gaussian values with trend for the zone
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
    )
    if write_rms_parameters_for_qc_purpose:
        # Update array trend for the selected grid cells
        # Note that the numpy vector trend contains values for all active grid cells
        # while trend_values_for_zone contain values calculated for the current zone and current parameter
        trend_values_all = gf_all_trend_values[gf_name]
        trend_values_all[cell_index_defined] = trend_values_for_zone
        gf_all_trend_values[gf_name] = trend_values_all

        # Write back to RMS project the trend values for the zone
        update_rms_parameter(
            grid_model,
            gf_name,
            trend_values_all,
            cell_index_defined,
            realization_number,
            variable_name_extension='trend',
            use_regions=use_regions,
            zone_number=zone_number,
            region_number=region_number,
            debug_level=debug_level,
        )

    return gauss_field_values_all
