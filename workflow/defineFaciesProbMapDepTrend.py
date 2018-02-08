#!/bin/env python
# -*- coding: utf-8 -*-

import roxar

from src.algorithms.defineFaciesProbMapDepTrend import DefineFaciesProbMapDep
from src.utils.constants.simple import Debug


def run():
    model_file_name = 'APS_prob_mapdep.xml'
    debug_level = Debug.OFF
    define_facies_trend = DefineFaciesProbMapDep(model_file_name, project)
    define_facies_trend.calculate_facies_probability_parameter()
    if debug_level >= Debug.ON:
        print('Finished running defineFaciesProbTrend')


if __name__ == '__main__':
    run()
