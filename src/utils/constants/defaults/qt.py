from PyQt5.QtCore import Qt

from src.utils.constants.defaults.non_qt import Defaults


class Checked(Defaults):
    SEPARATE_ZONE_MODELS = Qt.Unchecked
    FACIES_MODELS = Qt.Unchecked
    GAUSSIAN_TREND = Qt.Unchecked
    CONDITION_TO_WELL = Qt.Unchecked
