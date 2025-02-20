from rmsapi.jobs import Job
from aps.utils.constants.simple import Conform, Debug
from typing import Optional


def get_conformity(grid_model_name: str, rms_grid_job_name: str) -> tuple[dict, bool]:
    """Function to get conformity from the grid.
    Restrictions:
    - All horizons used are specified to be honored and not sampled.
    - The zones must be defined with Horizon as reference for both
      top and base and no Surface is used to define grid layout.
    - If the two above mentioned criteria is satisfied, it is possible
      to use the 'ConformalMode' list from rmsapi to get conformity status.

    If restrictions above are not satisfied, the current function will return
    undefined for the conformity for all zones.
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

    conformity_dict: dict[int, dict] = {}
    is_defined = True
    # zone_number starts at 1
    if len(zone_names) > len(conformal_mode_list):
        # This indicates that some zone borders are calculated using 'Sample'
        # and not 'Honor'. In this case the conformal_mode_list no longer
        # match the modelling zones since sone zones are merged when
        # defining grid layout.
        is_defined = False
        return conformity_dict, is_defined

    for zone_number, zone_name in enumerate(zone_names, start=1):
        conform_mode = conformal_mode_list[zone_number - 1]
        use_top_surf = use_top_surface[zone_number - 1]
        use_base_surf = use_base_surface[zone_number - 1]
        if use_top_surf or use_base_surf:
            is_defined = False
            return {}, is_defined
        assert conform_mode in [0, 1, 2]
        if conform_mode == 0:
            conform = Conform.Proportional
        elif conform_mode == 1:
            conform = Conform.TopConform
        else:
            conform = Conform.BaseConform

        conformity_dict[zone_number] = {'zone_name': zone_name, 'conformity': conform}
    return conformity_dict, is_defined


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
    debug_level: Debug = Debug.OFF,
) -> None:
    job_names = get_job_name(grid_model_name)
    if job_names is None:
        if debug_level >= Debug.ON:
            print('WARNING: ')
            print(
                f"      No automatic grid conformity check for '{grid_model_name}'"
                f' for zone number {zone_number}.'
            )
            print('      This grid is not created by an RMS grid building job.')
        return

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
        return

    rms_grid_job_name = job_names[0]
    conformity_dict, is_defined = get_conformity(grid_model_name, rms_grid_job_name)
    if not is_defined:
        if debug_level >= Debug.ON:
            print('WARNING: ')
            print(
                f"        The grid definition in the job '{rms_grid_job_name}' "
                f"for the grid model '{grid_model_name}' is not implemented in APS."
            )
            print(
                '        The implemented type of zone boundaries is defined by the option '
                "'Honor' and not 'Sample'."
            )
            print(
                '        The implemented grid conformities is defined by the '
                "option 'Horizon' and not 'Surface'."
            )
            print(
                '        You must in APS gui choose the best of the three possible implemented conformities:'
            )
            print("         'Proportional', 'TopConform' or 'BaseConform')")

            print()
        return

    zone_conformity_dict = conformity_dict[zone_number]  # Zone number start at 1
    zone_name = zone_conformity_dict['zone_name']
    conformity = zone_conformity_dict['conformity']
    if grid_layout != conformity:
        if aps_job_name is not None:
            aps_job_string = f"'APS job '{aps_job_name}'"
        else:
            aps_job_string = 'current APS job'
        raise ValueError(
            '\n'
            f"  Specified zone conformity for zone '{zone_name}' is '{grid_layout}'\n"
            f"  Grid model '{grid_model_name}' has different zone conformity: {conformity}\n"
            f'  Change conformity setting in {aps_job_string} to match the correct one used in the grid model.'
        )
    if debug_level >= Debug.VERY_VERBOSE:
        print(
            '--- Specified grid conformity in APS model '
            f"is consistent with the grid for zone '{zone_name}'"
        )
    return


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
            debug_level=Debug.VERY_VERBOSE,
        )
