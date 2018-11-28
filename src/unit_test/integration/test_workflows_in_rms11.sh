#!/usr/bin/env bash

rm -f statusfile_*.dat

if [ -z "${RMS_PROJECT}" ]; then
RMS_PROJECT="testAPSWorkflow_new.rms11"
fi
if [ -z "${RMS}" ]; then
    if [ -z "${RMS_VERSION}" ]; then
        RMS_VERSION=11.0.0
    fi
RMS="/prog/roxar/site/RMS${RMS_VERSION}/rms/rms"
fi

# Test_APS_deterministic_interpretation
# Example_APS
# De andre kan sjekkes manuelt, dvs
#   Test_Update_FMU_parameters
#   Test_APS_uncertainty_workflow
#   Test_defineFaciesProbTrend
#   Example_APS_workflow_multi_process

# TODO: Make sure the workflow "Test_defineFaciesProbTrend" works as intended
for workflow in "Example_APS_Coarse_unconditioned" \
                "Example_APS_Coarse_conditioned" \
                "Example_APS_Coarse_uncond_regions" \
                "Example_APS_Fine_unconditioned" \
                "Test_Update_FMU_parameters" \
                "Test_APS_deterministic_interpretation" \
                "Test_APS_uncertainty_workflow"
do
    status_file="statusfile_${workflow}.dat"
    ${RMS} -project "${RMS_PROJECT}" \
           -batch "${workflow}" \
           -readonly
           # TODO: Add '-readonly'?

    if [ ! -f "${status_file}" ]; then
        echo "The workflow (${workflow}) did not complete. Exiting"
        echo "That is, the file '${status_file}' does not exist"
        exit 1
        break
    fi
    if grep -q 0 "${status_file}"; then
        echo "The workflow (${workflow}) has failed. See logs for more details. Exiting"
        exit 1
        break
    fi
done
