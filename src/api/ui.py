# -*- coding: utf-8 -*-
from src.utils.roxar.rms_project_data import RMSData
import roxar


def call(method_name, *args, **kwargs):
    # TODO: Separate rms methods from 'static' methods
    func = getattr(RMSData(roxar, project), method_name)
    return func(*args, **kwargs)
