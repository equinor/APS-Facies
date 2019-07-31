"""
This is a wrapper for nrlib, for use on RGS nodes.
It selects the correct version of NRlib (which is precompiled on RGS, under /project/res/nrlib)

This is done, so that there is only need for ONE plugin for different versions of RedHat, and RMS.
Otherwise, nrlib would have to be included in EVERY plugin, which adds about 100 MB.
"""


def __bootstrap__():
    from src.utils.roxar import get_nrlib_path
    path = get_nrlib_path()
    if path is None:
        raise ImportError

    import sys
    import importlib.util

    name = 'nrlib'

    del sys.modules[name]

    spec = importlib.util.spec_from_file_location(name, path + '/nrlib.so')
    sys.modules[name] = importlib.util.module_from_spec(spec)


__bootstrap__()
