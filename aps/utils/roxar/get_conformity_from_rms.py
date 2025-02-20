from rmsapi.jobs import Job
from aps.utils.constants.simple import Conform, Debug
from typing import Optional, Union


def get_conformity(
    grid_model_name: str, zone_number: int, rms_grid_job_name: str
) -> tuple[dict, bool]:
    """Function to get conformity from the grid.
    Restrictions:
    - All horizons used are specified to be honored and not sampled.
    - The zones must be defined with Horizon as reference for both
      top and base and no Surface is used to define grid layout.
    - If the two above mentioned criteria is satisfied, it is possible
      to use the 'ConformalMode' list from rmsapi to get conformity status.

    If restrictions above are not satisfied, the current function will return:
        - empty dict and not defined if 'Sample' is used
        - dict with conformity assigned to 'Conform.UNDEFINED' for the zone
          and is_defined = False if 'Surface' is reference and not 'Horizon'
          for the zone this happens.
    If everything is ok for all zones, the dict with conformity is assigned
    and is_defined = True
    """
    owner_strings = ['Grid models', grid_model_name, 'Grid']
    type_string = 'Create Grid'
    name = rms_grid_job_name
    grid_job = Job.get_job(owner_strings, type_string, name)
    arguments = grid_job.get_arguments()
    conformal_mode_list = arguments['ConformalMode']
    zone_names = arguments['ZoneNames']
    use_base_surface = arguments['UseBottomSurface']
    use_top_surface = arguments['UseTopSurface']

    conform_dict: dict[int, dict] = {}
    boundary_is_sampled = False
    # zone_number starts at 1
    if len(zone_names) > len(conformal_mode_list):
        # This indicates that some zone borders are calculated using 'Sample'
        # and not 'Honor'. In this case the conformal_mode_list no longer
        # match the modelling zones since sone zones are merged when
        # defining grid layout.
        # return empty dict and is_defined = False
        boundary_is_sampled = True
        conform_dict = {
            'zone_name': zone_names[zone_number - 1],
            'conformity': Conform.Undefined,
        }
        return conform_dict, boundary_is_sampled

    conform_mode = conformal_mode_list[zone_number - 1]
    use_top_surf = use_top_surface[zone_number - 1]
    use_base_surf = use_base_surface[zone_number - 1]
    assert conform_mode in [0, 1, 2]
    if conform_mode == 0:
        conform = Conform.Proportional
    elif conform_mode == 1:
        conform = Conform.TopConform
    else:
        conform = Conform.BaseConform
    if use_top_surf or use_base_surf:
        conform = Conform.Undefined

    conform_dict = {
        'zone_name': zone_names[zone_number - 1],
        'conformity': conform,
    }

    return conform_dict, boundary_is_sampled


def get_job_name(grid_model_name: str) -> Optional[str]:
    """Get job name for a specified grid model.
    Return None if no job found , the job name if found
    and error if multiple job names are found.
    """
    owner_strings = ['Grid models', grid_model_name, 'Grid']
    type_string = 'Create Grid'
    job_names = Job.get_job_names(owner_strings, type_string)
    if len(job_names) == 0:
        return None
    return job_names


def check_grid_layout(
    grid_model_name,
    zone_number: int,
    grid_layout: Conform,
    aps_job_name: str = None,
    return_grid_layout: bool = False,
    debug_level: Debug = Debug.OFF,
) -> Union[None, Conform]:
    job_names = get_job_name(grid_model_name)
    if job_names is None:
        if debug_level >= Debug.ON:
            print('WARNING: ')
            print(
                f"      No automatic grid conformity check for '{grid_model_name}'"
                f' for zone number {zone_number}.'
            )
            print('      This grid is not created by an RMS grid building job.')
        return None

    elif len(job_names) > 1:
        if debug_level >= Debug.ON:
            print('WARNING:')
            print(
                f"        No automatic grid conformity check for '{grid_model_name}'"
                f' for zone number {zone_number}.'
            )
            print('        There exists multiple grid building jobs for this grid.')
            print('       Cannot know which one to use to check grid conformity.')
            print('       The jobs are:')
            print(f'       {job_names}')
        return None

    rms_grid_job_name = job_names[0]
    zone_conformity_dict, boundary_is_sampled = get_conformity(
        grid_model_name, zone_number, rms_grid_job_name
    )
    if boundary_is_sampled:
        if debug_level >= Debug.ON:
            print('WARNING: ')
            print(
                f"        The grid definition in the job '{rms_grid_job_name}' "
                f"for the grid model '{grid_model_name}' is not implemented in APS."
            )
            print(
                "        Only zone boundaries defined by option 'Honor' is implemented."
            )
            print(
                '        You must in APS gui choose the best of the three possible implemented conformities:'
            )
            print("         'Proportional', 'TopConform' or 'BaseConform')")
        return None

    zone_name = zone_conformity_dict['zone_name']
    conformity = zone_conformity_dict['conformity']

    if conformity == Conform.Undefined:
        if debug_level >= Debug.ON:
            print('WARNING: ')
            print(
                f"        The grid definition in the job '{rms_grid_job_name}' "
                f"for the grid model '{grid_model_name}' for zone {zone_name} "
                'is not implemented in APS.'
            )
            print(
                "        APS has only implemented conformities using option 'Horizon' and not 'Surface'."
            )
            print(
                '        You must in APS gui choose the best of the three possible implemented conformities:'
            )
            print("         'Proportional', 'TopConform' or 'BaseConform')")

            print()
        return None

    if grid_layout != conformity:
        if aps_job_name is not None:
            aps_job_string = f"'APS job '{aps_job_name}'"
        else:
            aps_job_string = 'current APS job'
        if not return_grid_layout:
            raise ValueError(
                '\n'
                f"  Specified zone conformity for zone '{zone_name}' is '{grid_layout}'\n"
                f"  Grid model '{grid_model_name}' has different zone conformity: {conformity}\n"
                f'  Change conformity setting in {aps_job_string} to match the correct one used in the grid model.'
            )
        else:
            return conformity

    if debug_level >= Debug.VERY_VERBOSE:
        print(
            '--- Specified grid conformity in APS model '
            f"is consistent with the grid for zone '{zone_name}'"
        )
    return conformity


if __name__ == '__main__':
    # A test case
    grid_model_name = 'GridModelCoarse'
    aps_job_name = 'APS_job'
    grid_model = project.grid_models[grid_model_name]
    zone_numbers = [1, 2, 3]
    grid_layouts = [
        Conform.Proportional,
        Conform.TopConform,
        Conform.BaseConform,
    ]
    for zone_number in zone_numbers:
        grid_layout = grid_layouts[zone_number - 1]
        check_grid_layout(
            grid_model_name,
            zone_number,
            grid_layout,
            aps_job_name=aps_job_name,
            return_grid_layout=False,
            debug_level=Debug.VERY_VERBOSE,
        )
