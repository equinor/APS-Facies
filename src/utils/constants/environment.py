import sys
from enum import Enum
from pathlib import Path

from src.utils.constants.autogenerated import (
    BRANCH_NAME, BUILD_NUMBER, EXAMPLE_FOLDER, EXAMPLE_FOLDER_APP,
    LATEST_COMMIT_HASH, LATEST_VERSION, LIBRARY_FOLDER, LIBRARY_FOLDER_APP,
)


def get_build_number() -> int:
    if BUILD_NUMBER:
        return int(BUILD_NUMBER)
    else:
        return -1


def resource_path(relative_path) -> str:
    """
    Get absolute path to resource, works for dev and for PyInstaller
    Shamelessly inspired from https://stackoverflow.com/questions/7674790/bundling-data-files-with-pyinstaller-onefile
    """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path('.')  # FIXME: Make more generic; abs path to source root?

    return str(base_path.joinpath(relative_path).absolute())


def get_path_to_example_files() -> str:
    return _get_path_to(EXAMPLE_FOLDER, EXAMPLE_FOLDER_APP)


def get_commit_hash() -> str:
    return LATEST_COMMIT_HASH


def get_version_tag() -> str:
    if LATEST_VERSION:
        return 'version {latest_version}'.format(latest_version=LATEST_VERSION)
    build_number = get_build_number()
    if build_number > 0:
        return "build {build_number}, on branch '{branch_name}'".format(
            build_number=get_build_number(),
            branch_name=BRANCH_NAME
        )
    else:
        # TODO: other name
        return "unknown build, on branch '{branch_name}'".format(branch_name=BRANCH_NAME)


def get_path_to_libraries() -> str:
    return _get_path_to(LIBRARY_FOLDER, LIBRARY_FOLDER_APP)


def _get_path_to(primary_path, secondary_path):
    path = Path(primary_path)
    if path.is_dir():
        return str(path)
    else:
        return resource_path(secondary_path)


class ExampleFiles(Enum):
    MODEL = get_path_to_example_files() + '/APS.xml'
    RMS = get_path_to_example_files() + '/rms_project_data_for_APS_gui.xml'


class DrawingLibrary(Enum):
    LIBRARY_PATH = get_path_to_libraries() + '/libdraw2D.so'


class API(Enum):
    URL = 'rms/api/'