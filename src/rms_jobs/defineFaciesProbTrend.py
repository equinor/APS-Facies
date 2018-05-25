#!/bin/env python
# -*- coding: utf-8 -*-

from src.algorithms.defineFaciesProbTrend import DefineFaciesProb
from src.utils.constants.simple import Debug
from src.utils.methods import get_prefix, get_debug_level


def run(roxar=None, project=None, **kwargs):
    model_file_name = get_prefix(**kwargs) + '/' + 'defineProbTrend.xml'
    debug_level = get_debug_level(**kwargs)
    define_facies_trend = DefineFaciesProb(model_file_name, project, debug_level=debug_level)
    define_facies_trend.calculate_facies_probability_parameter()
    print('Finished running defineFaciesProbTrend')


if __name__ == "__main__":
    import roxar
    run(roxar, project)
