from src.utils.constants import ModeOptions


def is_reading_mode(mode):
    return mode == ModeOptions.READING_MODE


def is_experimental_mode(mode):
    return mode == ModeOptions.EXPERIMENTAL_MODE
