from src.algorithms.APSModel import ApsModel
from src.algorithms.Trend3D import ConicTrend
from src.utils.constants.simple import OriginType
from src.utils.methods import get_specification_file, get_output_model_file
from src.utils.roxar.generalFunctionsUsingRoxAPI import get_grid_dimension

import roxar


def run(roxar=None, project=None, **kwargs):
    model_file = get_specification_file(**kwargs)
    model = ApsModel(model_file)
    nz_fmu = kwargs.get('max_fmu_grid_depth')
    _, _, nz_grid = get_grid_dimension(project, model.grid_model_name)

    for zone in model.sorted_zone_models.values():
        for field in zone.gaussian_fields:
            if field.trend and field.trend.use_trend:
                trend = field.trend.model
                if isinstance(trend, ConicTrend) and trend.origin_type == OriginType.RELATIVE:
                    # Update trend
                    trend.origin.z = trend.origin.z * nz_fmu / nz_grid

    output_file = get_output_model_file(**kwargs)
    model.dump(output_file)


if __name__ == '__main__':
    run(roxar, project)
