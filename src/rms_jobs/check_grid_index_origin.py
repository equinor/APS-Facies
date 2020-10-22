from src.algorithms.APSModel import APSModel
from src.utils.constants.simple import Debug
import roxar

def run(project,
        rms_grid_name: str,
        fmu_mode: bool,
        fmu_simulation_grid_name: str,
        debug_level: Debug,
        **kwargs):
    current_version = roxar.rms.get_version()
    version_having_rms_error_functions = '12.1'
    version_having_ijk_handedness_function = '11.1.1'
    
    # Check the geomodelling grid
    rms_grid_model = project.grid_models[rms_grid_name]
    if rms_grid_model.is_empty():
        raise ValueError(f'Specified grid model: {rms_grid_name} is empty.')
    rms_grid3D = rms_grid_model.get_grid(project.current_realisation)
    if current_version < version_having_ijk_handedness_function:
        rms_ijk_handedness = rms_grid3D.grid_indexer.handedness
    else:
        rms_ijk_handedness = rms_grid3D.grid_indexer.ijk_handedness

    if debug_level >= Debug.VERBOSE:
        if rms_ijk_handedness == roxar.Direction.left:
            print(f'-- Grid index origin for {rms_grid_name} is standard RMS (lower left corner of non-rotated grids)') 
        else:
            print(f'-- Grid index origin for {rms_grid_name} is standard ECLIPSE (upper left corner of non-rotated grids)')

    if fmu_mode:
        fmu_grid_model = project.grid_models[fmu_simulation_grid_name]
        if fmu_grid_model.is_empty():
            raise ValueError(f'Specified grid model: {fmu_simulation_grid_name} is empty.')
        fmu_grid3D = fmu_grid_model.get_grid(project.current_realisation)
        if current_version < version_having_ijk_handedness_function:
            fmu_ijk_handedness = fmu_grid3D.grid_indexer.handedness
        else:
            fmu_ijk_handedness = fmu_grid3D.grid_indexer.ijk_handedness

        if debug_level >= Debug.VERBOSE:
            if fmu_ijk_handedness == roxar.Direction.left:
                print(f'-- Grid index origin for {fmu_simulation_grid_name} is standard RMS (lower left corner of non-rotated grids)') 
            else:
                print(f'-- Grid index origin for {fmu_simulation_grid_name} is standard ECLIPSE (upper left corner of non-rotated grids)')

        if fmu_ijk_handedness != rms_ijk_handedness:
            text = \
                'Error using grid model: {} and ERTBOX grid model:{} \n'\
                'APS workflows require that both the modelling grid and the help grid for ERT \n'\
                'uses the same grid index origin. \n'\
                'The grid index origin must be either the standard RMS choice or the standard Eclipse choice'\
                ''.format(rms_grid_name, fmu_simulation_grid_name)

            if current_version >= version_having_rms_error_functions:
                roxar.rms.error('APS workflows require same grid index origin for both modelling grid and ERTBOX grid')
            raise ValueError(text)

