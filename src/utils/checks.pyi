# -*- coding: utf-8 -*-
from src.utils.constants.simple import Debug, VariogramType


def isVariogramTypeOK(
    variogramType: VariogramType,
    debug_level: Debug = Debug.OFF
) -> bool: ...
