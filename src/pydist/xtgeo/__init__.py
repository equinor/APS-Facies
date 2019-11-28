"""
This is a wrapper for xtgeo, for use on RGS nodes.
It selects the correct version of XtGeo (which is precompiled on RGS, under /project/res/roxapi)

This is done, so that there is only need for ONE plugin for different versions of RedHat, and RMS.
"""


def __bootstrap__():
    from src.utils.roxar import get_common_python_packages_path
    path = get_common_python_packages_path()
    if path is None:
        raise ImportError

    import sys
    import importlib.machinery

    dependencies = [
        'shapely',
        'segyio',
        'xtgeo',
    ]

    for name in dependencies:
        try:
            del sys.modules[name]
        except KeyError:
            pass

        # module = importlib.import_module(name, path)
        # sys.modules[name] = module

        spec = importlib.util.spec_from_file_location(name, path + '/{}/__init__.py'.format(name))
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)


__bootstrap__()
