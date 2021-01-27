#!/bin/env python
# -*- coding: utf-8 -*-


class OverlayGroupIndices:
    """ Indices in array for one overlay group:
            [alphaList, backgroundFaciesList]
    """
    ALPHA_LIST_INDX = 0
    BACKGROUND_LIST_INDX = 1


class OverlayPolygonIndices:
    """ Indices in array for one polygon in alpha space in an overlay group:
            [alphaName, faciesName, probFraction, centerOfTruncationInterval]
    """
    ALPHA_NAME_INDX = 0
    FACIES_NAME_INDX = 1
    PROB_FRAC_INDX = 2
    CENTER_INTERVAL_INDX = 3


class CubicStructIndices:
    """ Index in array representing Cubic truncation settings:
            [direction, polygon, polygon,...]
    """
    DIRECTION_INDX = 0


class CubicPolygonIndices:
    """ Indices in array representing one polygon for background facies truncation type Cubic:
            [faciesName, probFraction, L1, L2, L3]
    """
    FACIES_NAME_INDX = 0
    PROB_FRAC_INDX = 1
    L1_INDX = 2
    L2_INDX = 3
    L3_INDX = 4


class NonCubicPolygonIndices:
    """ Indices in array representing one polygon for background facies truncation type NonCubic:
           [faciesName, angle, probFraction]
    """
    FACIES_NAME_INDX = 0
    ANGLE_INDX = 1
    PROB_FRAC_INDX = 2


class CubicAndOverlayIndices:
    """ Indices in array representing settings for truncation rule where overlay facies truncations are defined and
        where background facies is defined by Cubic type:
            [nameBG, nameOL, itemCubic, overlayGroups]
    """
    NAME_BG_INDX = 0
    NAME_OL_INDX = 1
    STRUCT_CUBIC_INDX = 2
    OVERLAYGROUP_INDX = 3


class NonCubicAndOverlayIndices:
    """ Indices in array representing settings for truncation rule where overlay facies truncations are defined and
        where background facies is defined by NonCubic type:
            [nameBG, nameOL, itemNonCubic, overlayGroups]
    """
    NAME_BG_INDX = 0
    NAME_OL_INDX = 1
    STRUCT_NONCUBIC_INDX = 2
    OVERLAYGROUP_INDX = 3

