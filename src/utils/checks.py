from os.path import isfile

from src.utils.constants.defaults.non_qt import APSModelFile
from src.utils.constants.simple import VariogramType, Debug


def is_valid_path(path: str) -> bool:
    if path and isfile(path) and has_valid_extension(path):
        return True
    else:
        return False


def has_valid_extension(path: str) -> bool:
    if path:
        return path.split('.')[-1] == APSModelFile.FILE_EXTENSION
    return False


def isVariogramTypeOK(variogramType: VariogramType, debug_level: Debug=Debug.OFF):
    if variogramType in VariogramType:
        return True
    elif variogramType._name_ in VariogramType._member_map_:
        # Hack because of some strange bug (apparently variogramType is not an instance in VariogramType (class-wise))
        # even though they are
        return True
    elif debug_level >= Debug.VERY_VERBOSE:
        print('Error: Specified variogram : ' + variogramType.name + ' is not implemented')
        print('Error: Allowed variograms are: ')
        print('       SPHERICAL')
        print('       EXPONENTIAL')
        print('       GAUSSIAN')
        print('       GENERAL_EXPONENTIAL')
        print('       MATERN32')
        print('       MATERN52')
        print('       MATERN72')
        print('       CONSTANT')
    return False
