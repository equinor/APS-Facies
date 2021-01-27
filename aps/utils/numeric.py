# -*- coding: utf-8 -*-
import numpy as np

from aps.algorithms.properties import CrossSection
from aps.utils.constants.simple import CrossSectionType


def isNumber(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False


def flip_if_necessary(data: np.ndarray, cross_section: CrossSection) -> np.ndarray:
    if cross_section.type in [CrossSectionType.IK, CrossSectionType.JK]:
        data = np.flip(data, 0)
    return data
