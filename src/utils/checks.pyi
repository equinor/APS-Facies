# -*- coding: utf-8 -*-
from typing import Union

from src.utils.constants.simple import Debug, VariogramType


def isVariogramTypeOK(
    _type: Union[VariogramType, str],
    debug_level: Debug = Debug.OFF
) -> bool: ...
