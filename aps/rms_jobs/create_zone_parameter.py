from aps.algorithms.APSModel import APSModel
from aps.utils.constants.simple import GridModelConstants, Debug
from aps.utils.roxar.grid_model import create_zone_parameter


def get_zone_number(project, grid_model):
    zonations = grid_model.get_grid(project.current_realisation).simbox_indexer.zonation
    return [key + 1 for key in zonations.keys()]


def get_codes(grid_model, zone_parameter_name, realization_number):
    zone_property = grid_model.properties[zone_parameter_name]
    if zone_property.is_empty(realization_number):
        return []
    else:
        codes = zone_property.code_names.keys()
    return list(codes)


def run(project, aps_model: APSModel, debug_level, **kwargs):
    grid_model = project.grid_models[aps_model.grid_model_name]
    set_shared = grid_model.shared
    realization_number = project.current_realisation
    zone_parameter_name = GridModelConstants.ZONE_NAME
    if debug_level >= Debug.VERBOSE:
        print(f'-- Checking to see whether {zone_parameter_name} must be created')
    must_create = False
    if zone_parameter_name in grid_model.properties:
        codes = get_codes(grid_model, zone_parameter_name, realization_number)
        if len(codes) > 0:
            # The zone parameter exist for this realization
            zone_numbers = get_zone_number(project, grid_model)
            if set(zone_numbers) != set(codes):
                raise ValueError(
                    f'There is a mismatch between the zone numbers as defined in {zone_parameter_name} '
                    f'({codes}), and in the grids\' zonation ({zone_numbers}).\n'
                    f'A solution to this, is to delete the {zone_parameter_name} property from {aps_model.grid_model_name}.'
            )
        else:
            must_create = True
    else:
        must_create = True

    if must_create:
        if debug_level >= Debug.ON:
            print(f'- Creating the zone property / parameter ({zone_parameter_name})')
        create_zone_parameter(
            grid_model,
            zone_parameter_name,
            realization_number=project.current_realisation,
            set_shared=set_shared,
            debug_level=debug_level,
        )
