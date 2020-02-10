# -*- coding: utf-8 -*-
import numpy as np

from src.algorithms.properties import CrossSection

def isNumber(s: str) -> bool: ...
def flip_if_necessary(data: np.ndarray, cross_section: CrossSection) -> np.ndarray: ...
