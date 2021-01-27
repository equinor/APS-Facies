#!/usr/bin/env bash

rm -f statusfile_*.dat

rms -v 10.1.3 -project testAPSWorkflow_new.rms10.1.3 -batch Example_APS_gridmodel2_unconditioned
rms -v 10.1.3 -project testAPSWorkflow_new.rms10.1.3 -batch Example_APS_gridmodel2_conditioned
rms -v 10.1.3 -project testAPSWorkflow_new.rms10.1.3 -batch Example_APS_gridmodel2_uncond_regions
rms -v 10.1.3 -project testAPSWorkflow_new.rms10.1.3 -batch Example_APS_gridmodel1_unconditioned
rms -v 10.1.3 -project testAPSWorkflow_new.rms10.1.3 -batch Test_defineFaciesProbTrend

