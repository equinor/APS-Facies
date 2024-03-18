# -*- coding: utf-8 -*-
from aps.utils.roxar.rms_project_data import RMSData
import roxar.rms


try:
    # When running in RMS, the current project should be available as `project` in the global scope
    project
except NameError:
    import os
    if 'RMS_PROJECT_PATH' in os.environ:
        # Ensure "project" is available as a global variable
        # similar to what ui.py expects
        project = roxar.Project.open(os.environ['RMS_PROJECT_PATH'])
    else:
        raise RuntimeError('No project available, and RMS_PROJECT_PATH is not set')


def call(method_name, *args, **kwargs):
    # TODO: Separate rms methods from 'static' methods
    func = getattr(RMSData(roxar, project), method_name)
    return func(*args, **kwargs)
