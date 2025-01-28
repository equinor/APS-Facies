import xtgeo

from aps.algorithms.APSModel import APSModel
from aps.utils.fmu import get_export_location
from aps.utils.methods import get_specification_file
from aps.utils.constants.simple import Debug
from aps.utils.roxar.progress_bar import APSProgressBar


def run(project, **kwargs):
    export_grid = kwargs.get('export_ertbox_grid', True)
    debug_level = kwargs.get('debug_level', Debug.OFF)
    if not export_grid:
        if debug_level >= Debug.ON:
            print(' ')
            print('- ERT box grid is not exported.')
        return

    model_file = get_specification_file(**kwargs)
    aps_model = APSModel(model_file)
    aps_grid_name = aps_model.grid_model_name

    field_location = get_export_location()
    if debug_level >= Debug.ON:
        print(' ')
        print(f"- Export ERT box grid {aps_grid_name} to '{field_location}'")

    aps_grid = xtgeo.grid_from_roxar(
        project, aps_grid_name, project.current_realisation
    )

    aps_grid.to_file(
        str(field_location / '{}.EGRID'.format(aps_grid_name)),
        fformat='egrid',
    )
    APSProgressBar.increment()
