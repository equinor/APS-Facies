#!/bin/env python
# -*- coding: utf-8 -*-

import roxar

from src.algorithms.defineFaciesProbTrend import DefineFaciesProb
from src.utils.constants.simple import Debug


def run():
    model_file_name = 'defineProbTrend.xml'
    define_facies_trend = DefineFaciesProb(model_file_name, project, debug_level=Debug.OFF)
    define_facies_trend.calculate_facies_probability_parameter()
    print('Finished running defineFaciesProbTrend')


if __name__ == "__main__":
    run()
