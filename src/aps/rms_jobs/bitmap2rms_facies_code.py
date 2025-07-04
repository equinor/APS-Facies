#!/usr/bin/env python
# -*- coding: utf-8 -*-
from aps.rms_jobs.bitmap2rms import run as main


def run(roxar=None, project=None, **kwargs):
    kwargs['facies_code'] = True
    main(roxar, project, **kwargs)
