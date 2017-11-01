from enum import Enum


class DrawingLibrary(Enum):
    LIBRARY_FOLDER = '/home/aps-gui/APS-GUI/libraries'  # Set automatically by make
    NAME = 'libdraw2D.so'
    LIBRARY_PATH = LIBRARY_FOLDER + '/' + NAME
