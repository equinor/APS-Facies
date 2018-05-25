#!/bin/env python
# -*- coding: utf-8 -*-

from src.algorithms.defineFaciesProbMapDepTrend import DefineFaciesProbMapDep
from src.utils.constants.simple import Debug
from src.utils.methods import get_debug_level, get_prefix


def run(roxar=None, project=None, **kwargs):
    model_file_name = get_prefix(**kwargs) + '/' + 'APS_prob_mapdep.xml'
    debug_level = get_debug_level(**kwargs)
    define_facies_trend = DefineFaciesProbMapDep(model_file_name, project)
    define_facies_trend.calculate_facies_probability_parameter()
    if debug_level >= Debug.ON:
        print('Finished running defineFaciesProbTrend')


if __name__ == '__main__':
    import roxar
    run(roxar, project)
