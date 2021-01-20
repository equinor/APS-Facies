from aps.utils.constants.simple import Debug
import roxar


def get_grid_ijk_handedness(grid) -> roxar.Direction:
    try:
        # Uses the API from version 11.1.1 and later
        return grid.grid_indexer.ijk_handedness
    except AttributeError:
        # Fallback to old API
        return grid.grid_indexer.handedness


def run(project,
        rms_grid_name: str,
        fmu_mode: bool,
        fmu_simulation_grid_name: str,
        debug_level: Debug,
        **kwargs):

    def _get_grid_ijk_handedness(grid_model_name):
        rms_grid_model = project.grid_models[grid_model_name]
        if rms_grid_model.is_empty():
            raise ValueError(f'Specified grid model: {grid_model_name} is empty.')
        grid = rms_grid_model.get_grid(project.current_realisation)

        grid_ijk_handedness = get_grid_ijk_handedness(grid)

        if debug_level >= Debug.VERBOSE:
            if grid_ijk_handedness == roxar.Direction.left:
                grid_type = 'RMS (lower left corner of non-rotated grids)'
            else:
                grid_type = f'ECLIPSE (upper left corner of non-rotated grids)'
            print(f'-- Grid index origin for {grid_model_name} is standard {grid_type}')

        return grid_ijk_handedness
    # Check the geo-modeling grid
    rms_ijk_handedness = _get_grid_ijk_handedness(rms_grid_name)

    if fmu_mode:
        fmu_ijk_handedness = _get_grid_ijk_handedness(fmu_simulation_grid_name)
        if fmu_ijk_handedness != rms_ijk_handedness:

            try:
                # Use RMS' pop-up error message, if the API is available.
                # Introduced in version 12.1.
                roxar.rms.error('APS workflows require same grid index origin for both modelling grid and ERTBOX grid')
            except AttributeError:
                pass
            raise ValueError(f'''\
Error using grid model: {rms_grid_name} and ERTBOX grid model:{fmu_simulation_grid_name}
APS workflows require that both the modelling grid and the help grid for ERT
uses the same grid index origin.
The grid index origin must be either the standard RMS choice or the standard Eclipse choice''')
