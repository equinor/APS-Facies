# -*- coding: utf-8 -*-
from src.utils.constants.base import Value
from src.utils.constants import (
    BayfillTruncationRuleElements, CubicTruncationRuleElements, GaussianRandomFieldElements, HideOptions,
    NonCubicTruncationRuleElements,
)
from src.utils.constants.simple import Debug, OperationalMode


class Defaults(Value):
    pass


class GeneralDefaults(Defaults):
    DEBUG = Debug.OFF
    OPERATION_MODE = OperationalMode.EXPERIMENTAL


class APSModelFile(Defaults):
    FILE_EXTENSION = 'xml'
    FILE_FILTER = 'XML files (*.xml)'


class UI(Defaults):
    PREFIX_NAME_OF_BUTTON = 'm_button_'
    NAME_OF_BUTTON_BOX = 'm_buttons_ok_cancel'
    NAME_OF_PROPORTIONS = CubicTruncationRuleElements.PROPORTIONS
    NAME_OF_SLIDERS = CubicTruncationRuleElements.SLIDERS
    NAME_OF_COLOR_BUTTON = CubicTruncationRuleElements.COLOR_BUTTON
    NAME_OF_DROP_DOWN = CubicTruncationRuleElements.DROP_DOWN
    NAME_OF_ANGLES = NonCubicTruncationRuleElements.ANGLES
    NAME_OF_SLANTED_FACTOR = BayfillTruncationRuleElements.SLANT_FACTOR


class Hide(Defaults):
    HIDE = HideOptions.DISABLE


class DatabaseDefaults(Defaults):
    STATE_NAME = 'state.db'
    MAXIMUM_NUMBER_OF_FACIES = GaussianRandomFieldElements.NUMBER_OF_ELEMENTS  # -1 To turn off
    MAXIMUM_NUMBER_OF_APS_MODELS = 1
    USE_CONSTANT_PROBABILITY = True


class ZoneDefaults(Defaults):
    NUMBER = 1


class RegionDefaults(Defaults):
    NUMBER = 1


class FaciesDefaults(Defaults):
    CODE = 1
    NAME = 'F1'


class DefaultGridSize(Defaults):
    X = 200
    Y = 200
    Z = 200


class DefaultOptimizationLevel(Defaults):
    USE = False
    LEVEL = 400
