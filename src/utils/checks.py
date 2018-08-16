# -*- coding: utf-8 -*-
from src.utils.constants.simple import VariogramType, Debug


def isVariogramTypeOK(_type, debug_level=Debug.OFF):
    if isinstance(_type, str):
        try:
            VariogramType[_type]
        except KeyError:
            return False
        return True
    elif _type in VariogramType:
        return True
    elif _type._name_ in VariogramType._member_map_:
        # Hack because of some strange bug (apparently variogramType is not an instance in VariogramType (class-wise))
        # even though they are
        return True
    elif debug_level >= Debug.VERY_VERBOSE:
        print('''Error: Specified variogram : {variogram_type} is not implemented
Error: Allowed variograms are:
       SPHERICAL
       EXPONENTIAL
       GAUSSIAN
       GENERAL_EXPONENTIAL
       MATERN32
       MATERN52
       MATERN72
       CONSTANT
'''.format(variogram_type=_type.name))
    return False
