from os.path import isfile

from src.utils.constants import Defaults


def is_valid_path(path: str) -> bool:
    if path and isfile(path) and has_valid_extension(path):
        return True
    else:
        return False


def has_valid_extension(path: str) -> bool:
    if path:
        return path.split('.')[-1] == Defaults.FILE_EXTENSION
    return False
