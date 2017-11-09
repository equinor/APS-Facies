from enum import Enum


VERSION_HASH = ''  # Set automatically


class DrawingLibrary(Enum):
    LIBRARY_FOLDER = ''  # Set automatically by make
    NAME = 'libdraw2D.so'
    LIBRARY_PATH = LIBRARY_FOLDER + '/' + NAME


class ExampleFiles(Enum):
    EXAMPLE_FOLDER = ''  # Set automatically by make
    MODEL = EXAMPLE_FOLDER + '/APS.xml'
    RMS = EXAMPLE_FOLDER + '/rms_project_data_for_APS_gui.xml'
