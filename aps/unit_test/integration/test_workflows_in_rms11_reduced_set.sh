#!/usr/bin/env bash

rm -f statusfile_*.dat

/prog/roxar/site/RMS11_beta_latest/rms/rms -project testAPSWorkflow_new.rms11 -batch Example_APS_gridmodel2_unconditioned
# /prog/roxar/site/RMS11_beta_latest/rms/rms -project testAPSWorkflow_new.rms11 -batch Example_APS_gridmodel2_conditioned
/prog/roxar/site/RMS11_beta_latest/rms/rms -project testAPSWorkflow_new.rms11 -batch Example_APS_gridmodel2_uncond_regions
/prog/roxar/site/RMS11_beta_latest/rms/rms -project testAPSWorkflow_new.rms11 -batch Example_APS_gridmodel1_unconditioned
# /prog/roxar/site/RMS11_beta_latest/rms/rms -project testAPSWorkflow_new.rms11 -batch Test_defineFaciesProbTrend

