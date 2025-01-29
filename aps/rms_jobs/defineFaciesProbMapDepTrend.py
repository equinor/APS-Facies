#!/bin/env python
# -*- coding: utf-8 -*-
from aps.algorithms.defineFaciesProbMapDepTrend import DefineFaciesProbMapDep
from aps.utils.methods import SpecificationType, get_debug_level, get_specification_file
from aps.utils.constants.simple import Debug


def run(roxar=None, project=None, **kwargs):
    model_file_name = get_specification_file(
        _type=SpecificationType.PROBABILITY_DEP_TREND, **kwargs
    )
    debug_level = get_debug_level(**kwargs)
    define_facies_trend = DefineFaciesProbMapDep(
        project=project, model_file_name=model_file_name, debug_level=debug_level
    )
    define_facies_trend.calculate_facies_probability_parameter()
    print('Finished running defineFaciesProbMapDepTrend')


if __name__ == '__main__':
    import roxar

    debug_level = Debug.VERBOSE
    run(roxar, project, debug_level=debug_level)
