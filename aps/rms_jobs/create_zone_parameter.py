from aps.algorithms.APSModel import APSModel
from aps.utils.constants.simple import GridModelConstants, Debug
from aps.utils.roxar.grid_model import (
    create_zone_parameter,
)
from roxar import GridPropertyType
from fmu.tools.rms.zone_mapping import ZoneMapping


def get_codes_from_zone_param(grid_model, realization_number):
    zone_param_name = GridModelConstants.ZONE_NAME
    zone_property = grid_model.properties[zone_param_name]
    if zone_property.is_empty(realization_number):
        return []
    else:
        if zone_property.type is not GridPropertyType.discrete:
            raise ValueError(
                f'The grid parameter {zone_param_name} is used in APS and is expected to be a discrete parameter.'
                ' Check that it is a discrete parameter.'
            )
        codes = zone_property.code_names.keys()
    return list(codes)


def run(project, aps_model: APSModel, debug_level, **kwargs):
    grid_model = project.grid_models[aps_model.grid_model_name]
    set_shared = grid_model.shared
    realization_number = project.current_realisation
    grid = grid_model.get_grid(realization_number)
    zone_mapping = ZoneMapping(grid_model, grid, real_number=realization_number)
    zone_parameter_name = GridModelConstants.ZONE_NAME
    if debug_level >= Debug.VERBOSE:
        print(f'-- Checking to see whether {zone_parameter_name} must be created')
    must_create = False
    if zone_parameter_name in grid_model.properties:
        codes = get_codes_from_zone_param(grid_model, realization_number)
        if len(codes) > 0:
            # The zone parameter exist for this realization
            zone_names_from_grid = zone_mapping.get_zone_names_from_grid()
            zone_names_from_param_dict = zone_mapping.get_zone_names_from_param()
            zone_names_from_param = list(zone_names_from_param_dict.values())

            if zone_names_from_grid != zone_names_from_param:
                print(
                    f'NOTE:\n'
                    f'There is a mismatch between zone names in grid {aps_model.grid_model_name} '
                    f'and zone names in parameter {zone_parameter_name}.\n'
                    f'Grid has zone names: {zone_names_from_grid}\n'
                    f'Parameter {zone_parameter_name} has zone names:  {zone_names_from_param}\n'
                    f'The zone names used in {zone_parameter_name} will be used.'
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
            create_new=True,
        )
