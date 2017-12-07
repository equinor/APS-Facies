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


def isVariogramTypeOK(variogramType, debug_level=Debug.OFF):
    if variogramType in VariogramType:
        return True
    elif debug_level >= Debug.VERY_VERBOSE:
        print('Error: Specified variogram : ' + variogramType.name + ' is not implemented')
        print('Error: Allowed variograms are: ')
        print('       SPHERICAL')
        print('       EXPONENTIAL')
        print('       GAUSSIAN')
        print('       GENERAL_EXPONENTIAL')
        return False
