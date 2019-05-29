# -*- coding: utf-8 -*-
from typing import Union

from src.utils.constants.simple import Debug, VariogramType


def isVariogramTypeOK(
    _type:                                                Union[VariogramType, str],
    debug_level:                                          Debug      = Debug.OFF
) -> bool: ...

def check_probability_values(
        prob_values,
        tolerance_of_probability_normalisation,
        facies_name:                                      str        = " ",
        parameter_name:                                   str        = " ",
        max_allowed_fraction_of_values_outside_tolerance: float      = 0.1,
): ...


def check_probability_normalisation(
        sum_probability_values,
        eps,
        tolerance_of_probability_normalisation,
        max_allowed_fraction_of_values_outside_tolerance: float      = 0.1,
): ...
