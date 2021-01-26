"""
This is a wrapper for xtgeo, for use on RGS nodes.
It selects the correct version of XtGeo (which is precompiled on RGS, under /project/res/roxapi)

This is done, so that there is only need for ONE plugin for different versions of RedHat, and RMS.
"""


def __bootstrap__():
    from src.utils.roxar import import_module
    import_module('xtgeo', dependencies=['shapely', 'segyio'], min_version='2.5.0')


__bootstrap__()
del __bootstrap__
