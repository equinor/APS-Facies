"""
This is a wrapper for PyYaml (yaml), for use on RGS nodes.
It imports the version of PyYaml included in Equinor's RMS distribution

This is done, to save space, and to simplify the usage of the APS GUI.
"""


def __bootstrap__():
    from src.utils.roxar import import_module
    import_module('yaml')


__bootstrap__()