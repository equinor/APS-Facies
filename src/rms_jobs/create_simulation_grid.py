import xtgeo

from src.algorithms.APSModel import APSModel
from src.utils.fmu import get_grid
from src.utils.methods import get_specification_file


def run(roxar=None, project=None, **kwargs):
    aps_model = APSModel(get_specification_file(**kwargs))
    simulation_grid_name = kwargs.get('fmu_simulation_grid_name')
    max_fmu_grid_depth = kwargs.get('max_fmu_grid_depth')

    reference_grid = get_grid(project, aps_model)
    nx, ny, _ = reference_grid.grid_indexer.dimensions
    dimension = nx, ny, max_fmu_grid_depth

    simulation_grid = xtgeo.Grid()
    simulation_grid.create_box(

    )


if __name__ == '__main__':
    import roxar

    run(roxar, project)
