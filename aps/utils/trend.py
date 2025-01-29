from aps.utils.constants.simple import Debug
from aps.utils.grid import update_rms_parameter
from aps.utils.roxar.grid_model import (
    find_defined_cells,
    create_zone_parameter,
    getDiscrete3DParameterValues,
)
from aps.utils.roxar.progress_bar import APSProgressBar
from aps.utils.simulation import initialize_rms_parameters


def add_trend_to_gauss_field(
    project,
    aps_model,
    zone_number,
    region_number,
    use_regions,
    gauss_field_name,
    gauss_field_values,
    cell_index_defined,
    gauss_field_trend_values=None,
    gauss_field_residual_values=None,
    fmu_mode=False,
    debug_level=Debug.OFF,
):
    """
    Calculate trend and add trend to simulated gaussian residual field to get the
    gaussian field with trend. Standard deviation for residual field is calculated
    by using the specified relative standard deviation and the
    trend max minus min of trend function. Returns gauss field where the grid
    cells defined by cell_index_defined are updated. All other grid cell values
    are not modified. The lenght of this array is equal to the length of all
    active grid cells in the grid model. Returns also trend values in a separate
    array, but this array has length equal to cell_index_defined and does only
    contain the values for the grid cells that are selected by cell_index_defined.
    """
    grid_model_name = aps_model.grid_model_name
    realization_number = project.current_realisation
    grid_model = project.grid_models[grid_model_name]
    key = (zone_number, region_number)
    zone_model = aps_model.sorted_zone_models[key]

    # Get trend model, relative standard deviation
    _, trend_model, rel_std_dev, _ = zone_model.getTrendModel(gauss_field_name)

    if debug_level >= Debug.VERY_VERBOSE:
        trend_type = trend_model.type.name
        if use_regions:
            print(
                f'--- Calculate trend for: {gauss_field_name} for (zone,region)=({zone_number}, {region_number})'
            )
            print(f'--- Trend type: {trend_type}')

        else:
            print(
                f'--- Calculate trend for: {gauss_field_name} for zone: {zone_number}'
            )
            print(f'--- Trend type: {trend_type}')

    sim_box_thickness = zone_model.sim_box_thickness
    # trend_values contain trend values for the cells belonging to the set defined by cell_index_defined
    minmax_difference, trend_values = trend_model.createTrend(
        grid_model,
        realization_number,
        cell_index_defined,
        zone_number=1 if fmu_mode else zone_number,
        sim_box_thickness=sim_box_thickness,
        project=project,
        keep_temporary_trend_param=fmu_mode,
        debug_level=debug_level,
    )

    # Calculate trend plus residual for the cells defined by cell_index_defined
    # and replace the residual values by trend + residual in array: gauss_field_values
    sigma = rel_std_dev * minmax_difference
    residual_values = gauss_field_values[cell_index_defined]
    val = trend_values + sigma * residual_values

    # Update array values for the selected grid cells
    if gauss_field_trend_values is not None:
        gauss_field_trend_values[cell_index_defined] = trend_values

    if gauss_field_residual_values is not None:
        gauss_field_residual_values[cell_index_defined] = residual_values

    gauss_field_values[cell_index_defined] = val

    if debug_level >= Debug.VERY_VERBOSE:
        print(f'--- Number of active cells:{len(cell_index_defined)} ')
        print(f'--- Trend minmax_difference = {minmax_difference}')
        print(f'--- SimBoxThickness = {sim_box_thickness}')
        print(f'--- RelStdDev = {rel_std_dev}')
        print(f'--- Sigma = {sigma}')
        print(
            f'--- Min trend, max trend    :  {trend_values.min()}  {trend_values.max()}'
        )
        print(
            f'--- Residual min,max        :  {sigma * residual_values.min()}  {sigma * residual_values.max()}'
        )
        print(f'--- Trend + residual min,max:  {val.min()}  {val.max()}')

    # Updated versions of these are returned
    return gauss_field_values, gauss_field_trend_values, gauss_field_residual_values


def add_trends(
    project,
    aps_model,
    zone_number,
    region_number=0,
    write_rms_parameters_for_qc_purpose=False,
    debug_level=Debug.OFF,
    fmu_mode=False,
    is_shared=False,
    fmu_with_residual_grf=False,
    fmu_add_trend_if_use_residual=False,
):
    grid_model = project.grid_models[aps_model.grid_model_name]
    zone_model = aps_model.getZoneModel(zone_number, region_number)
    gf_names_for_zone = zone_model.used_gaussian_field_names
    gf_names_for_truncation_rule = zone_model.getGaussFieldsInTruncationRule()
    realization_number = project.current_realisation

    # Initialize dictionaries keeping gauss field values and trends for all used gauss fields
    gf_all_values, _, gf_all_trend_values, gf_all_residual_values = (
        initialize_rms_parameters(
            project,
            aps_model,
            [1, 0, 1, 1],
            write_rms_parameters_for_qc_purpose,
            is_shared=is_shared,
            debug_level=debug_level,
            fmu_with_residual_grf=fmu_with_residual_grf,
        )
    )
    cell_index_defined = get_defined_cells(
        project,
        aps_model,
        grid_model,
        region_number,
        zone_number,
        debug_level,
        fmu_mode,
    )

    for gf_name in gf_names_for_zone:
        if gf_name in gf_names_for_truncation_rule:
            gauss_field_values_all = gf_all_values[gf_name]
            if zone_model.hasTrendModel(gf_name):
                gauss_field_trend_values_all = gf_all_trend_values[gf_name]
                gauss_field_residual_values_all = None
                if fmu_with_residual_grf:
                    gauss_field_residual_values_all = gf_all_residual_values[gf_name]
                add_trends_to_field(
                    project,
                    aps_model,
                    grid_model,
                    cell_index_defined,
                    gauss_field_values_all,
                    gauss_field_trend_values_all,
                    gauss_field_residual_values_all,
                    gf_name,
                    realization_number,
                    region_number,
                    zone_number,
                    debug_level,
                    fmu_mode=fmu_mode,
                    is_shared=is_shared,
                    fmu_with_residual_grf=fmu_with_residual_grf,
                    fmu_add_trend_if_use_residual=fmu_add_trend_if_use_residual,
                    write_rms_parameters_for_qc_purpose=write_rms_parameters_for_qc_purpose,
                )
                APSProgressBar.increment()


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
    use_regions = aps_model.use_regions
    if fmu_mode:
        zone_number = 1
        region_number = 0
        use_regions = False

    # Get zone parameter. Create and/or fill it with values if it does not exist
    zone_param = create_zone_parameter(
        grid_model,
        realization_number=realization_number,
        create_new=fmu_mode,
    )
    region_values = None
    if use_regions:
        region_values, _ = getDiscrete3DParameterValues(
            grid_model, aps_model.region_parameter, realization_number
        )
    zone_values = zone_param.get_values(realization_number)
    return find_defined_cells(
        zone_values,
        zone_number,
        region_values,
        region_number,
        debug_level=Debug.OFF,
    )


def add_trends_to_field(
    project,
    aps_model,
    grid_model,
    cell_index_defined,
    gauss_field_values_all,
    gauss_field_trend_values_all,
    gauss_field_residual_values_all,
    gf_name,
    realization_number,
    region_number,
    zone_number,
    debug_level=Debug.OFF,
    fmu_mode=False,
    is_shared=False,
    fmu_with_residual_grf=False,
    fmu_add_trend_if_use_residual=True,
    write_rms_parameters_for_qc_purpose=False,
):
    use_regions = aps_model.use_regions
    (
        gauss_field_values_all,
        gauss_field_trend_values_all,
        gauss_field_residual_values_all,
    ) = add_trend_to_gauss_field(
        project,
        aps_model,
        zone_number,
        region_number,
        use_regions,
        gf_name,
        gauss_field_values_all,
        cell_index_defined,
        gauss_field_trend_values_all,
        gauss_field_residual_values_all,
        fmu_mode,
        debug_level,
    )

    # Write back to RMS project:
    # - the untransformed gaussian values with trend for the zone
    # - the untransformed gaussian values without trend (residuals) for the zone
    # - the trend values for the zone
    # Gauss fields with trend
    if fmu_add_trend_if_use_residual or not fmu_with_residual_grf:
        if debug_level >= Debug.VERBOSE:
            print(f'-- Add trend and save field to: {grid_model.name}  for: {gf_name}')
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
    else:
        if debug_level >= Debug.VERBOSE:
            print(f'-- Save residual field to {grid_model.name}  for: {gf_name}')
        update_rms_parameter(
            grid_model,
            gf_name,
            gauss_field_residual_values_all,
            cell_index_defined,
            realization_number,
            variable_name_extension='residual',
            use_regions=use_regions,
            zone_number=zone_number,
            region_number=region_number,
            debug_level=debug_level,
            is_shared=is_shared,
        )
    if write_rms_parameters_for_qc_purpose:
        if debug_level >= Debug.VERBOSE:
            print(f'-- Save trend field to {grid_model.name}  for: {gf_name}')
        # Trend values
        update_rms_parameter(
            grid_model,
            gf_name,
            gauss_field_trend_values_all,
            cell_index_defined,
            realization_number,
            variable_name_extension='trend',
            use_regions=use_regions,
            zone_number=zone_number,
            region_number=region_number,
            debug_level=debug_level,
            is_shared=is_shared,
        )
