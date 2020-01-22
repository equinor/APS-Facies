# -*- coding: utf-8 -*-
import numpy as np

from src.utils.constants.simple import CrossSectionType


def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def flip_if_necessary(data, cross_section):
    if cross_section.type in [CrossSectionType.IK, CrossSectionType.JK]:
        data = np.flip(data, 0)
    return data
