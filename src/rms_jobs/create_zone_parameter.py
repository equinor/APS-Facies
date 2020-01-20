from src.algorithms.APSModel import APSModel
from src.utils.constants.simple import GridModelConstants, Debug
from src.utils.roxar.grid_model import create_zone_parameter


def get_zone_number(project, grid):
    zonations = grid.get_grid(project.current_realisation).simbox_indexer.zonation
    return [key + 1 for key in zonations.keys()]


def run(roxar, project, aps_model: APSModel, debug_level, **kwargs):
    grid = project.grid_models[aps_model.grid_model_name]
    zone_parameter = GridModelConstants.ZONE_NAME
    if debug_level >= Debug.ON:
        print(f'Checking to see whether {zone_parameter} must be created')

    if zone_parameter in grid.properties:
        zone_numbers = get_zone_number(project, grid)
        zone = grid.properties[zone_parameter]
        if set(zone_numbers) != set(zone.code_names.keys()):
            raise ValueError(
                f'There is a mismatch between the zone numbers as defined in {zone_parameter} '
                f'({zone.code_names.keys()}), and in the grids\' zonation ({zone_numbers}).\n'
                f'A solution to this, is to delete the {zone_parameter} property from {aps_model.grid_model_name}.'
            )
    else:
        if debug_level >= Debug.ON:
            print(f'Creating the zone property / parameter ({zone_parameter})')
        create_zone_parameter(
            grid,
            zone_parameter,
            realization_number=project.current_realisation,
            debug_level=debug_level,
        )
