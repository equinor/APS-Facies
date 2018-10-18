#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.rms_jobs.bitmap2rms import run as main


def run(roxar=None, project=None, **kwargs):
    kwargs['facies_code'] = False
    main(roxar, project, **kwargs)
