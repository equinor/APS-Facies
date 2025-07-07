try:
    import aps._version

    __version__ = aps._version.__version__
    __version_tuple__ = aps._version.__version_tuple__
except ModuleNotFoundError:
    pass
