import xtgeo

from src.algorithms.APSModel import APSModel
from src.utils.fmu import get_export_location
from src.utils.methods import get_specification_file


def run(roxar=None, project=None, **kwargs):
    model_file = get_specification_file(**kwargs)
    aps_model = APSModel(model_file)
    aps_grid_name = aps_model.grid_model_name

    field_location = get_export_location(project)
    print("Exporting the simulation grid to '{}'".format(field_location))

    aps_grid = xtgeo.grid_from_roxar(project, aps_grid_name, project.current_realisation)

    aps_grid.to_file(
        str(field_location / '{}.EGRID'.format(aps_grid_name)),
        fformat='egrid',
    )


if __name__ == '__main__':
    import roxar

    run(
        roxar, project,
    )
