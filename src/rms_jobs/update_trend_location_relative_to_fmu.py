from src.algorithms.APSModel import ApsModel
from src.algorithms.APSZoneModel import Conform
from src.algorithms.Trend3D import ConicTrend
from src.utils.constants.simple import OriginType
from src.utils.exceptions.zone import MissingConformityException
from src.utils.fmu import get_grid
from src.utils.methods import get_specification_file, get_output_model_file

import roxar


def run(roxar=None, project=None, **kwargs):
    model_file = get_specification_file(**kwargs)
    model = ApsModel(model_file)
    nz_fmu = kwargs.get('max_fmu_grid_depth')
    indexer = get_grid(project, model.grid_model_name).simbox_indexer

    necessary = False
    for zone in model.sorted_zone_models.values():
        zonation, *_reverse = indexer.zonation[zone.zone_number - 1]
        nz_zone = zonation.stop - zonation.start

        for field in zone.gaussian_fields:
            if field.trend and field.trend.use_trend:
                trend = field.trend.model
                if isinstance(trend, ConicTrend) and trend.origin_type == OriginType.RELATIVE:
                    # Update trend
                    necessary = True
                    if zone.grid_layout is None:
                        raise MissingConformityException(zone)
                    if zone.grid_layout in [Conform.TopConform, Conform.Proportional]:
                        trend.origin.z = trend.origin.z * nz_zone / nz_fmu
                    elif zone.grid_layout in [Conform.BaseConform]:
                        abs_nz = trend.origin.z * nz_zone
                        n_above = nz_fmu - nz_zone
                        trend.origin.z = (abs_nz + n_above) / nz_fmu
                    else:
                        raise NotImplementedError('{} is not supported'.format(zone.grid_layout))

    if necessary:
        print('Updating the location of relative trends')
    output_file = get_output_model_file(**kwargs)
    model.dump(output_file)


if __name__ == '__main__':
    run(roxar, project)
