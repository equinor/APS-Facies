#!/bin/env python
# -*- coding: utf-8 -*-
import aps.toolbox.check_and_normalise_probability as check_and_normalise_probability
from aps.utils.constants.simple import Debug, ProbabilityTolerances
from aps.utils.methods import get_specification_file, get_debug_level
from aps.utils.roxar.progress_bar import APSProgressBar

def run(
        project,
        tolerance_of_probability_normalisation=ProbabilityTolerances.MAX_ALLOWED_DEVIATION_BEFORE_ERROR,
        overwrite=True,
        max_allowed_fraction_of_values_outside_tolerance=ProbabilityTolerances.MAX_ALLOWED_FRACTION_OF_VALUES_OUTSIDE_TOLERANCE,
        **kwargs
):
    params ={
        "project": project,
        "debug_level": Debug.ON,
        "aps_model_file": get_specification_file(**kwargs),
        "overwrite":  overwrite,
        "tolerance_of_probability_normalisation": tolerance_of_probability_normalisation,
        "max_allowed_fraction_of_values_outside_tolerance": max_allowed_fraction_of_values_outside_tolerance,
    }
    check_and_normalise_probability.run(params)
    APSProgressBar.increment()
    return
