# -*- coding: utf-8 -*-
from src.utils.roxar.rms_project_data import RMSData
try:
    # TODO: Ensure this works on RGS
    import roxar
except ImportError:
    from src.utils.roxar.mock import Project, Roxar
    roxar = Roxar()
    project = Project()


def call(method_name, *args, **kwargs):
    func = getattr(RMSData(roxar, project), method_name)
    return func(*args, **kwargs)
