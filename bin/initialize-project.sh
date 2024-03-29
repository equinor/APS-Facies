#!/usr/bin/env bash

##
# initialize-project.sh
# This script is made to add the auxiliary Python jobs to a given RMS project.
#
# Author: Sindre Nistad <snis@equinor.com>
# Version: 1.0.2
##

RMS_VERSION="13.1.2"
RMS_ROOT="/prog/roxar/rms/versions/${RMS_VERSION}"
RMS_LIB="${RMS_ROOT}/lib/LINUX_64"
RMS_PYTHON="${RMS_ROOT}/bin/LINUX_64/python"


usage="./initialize-project.sh [--unstable] <path to RMS project>"

use_unstable=false

if [[ "${1}" == "--unstable" ]]; then
    shift
    use_unstable=true
fi

if [[ "$#" -ne 1 ]]; then
    echo "${usage}"
    echo "Optionally, the variable 'APS_PROJECT_DIR' may be set to use a custom location of the APS repo"
    exit 1
fi

get_abs_filename() {
  # Taken from https://stackoverflow.com/a/21188136
  # $1 : relative filename
  echo "$(cd "$(dirname "$1")" && pwd)/$(basename "$1")" | sed -E 's|^/+|/|g'
}

project=$(get_abs_filename "$1")

if [ ! -f "${project}/.master" ]; then
    echo "The given directory is not an RMS project"
    exit 1
fi

aps_project_root="/project/res/APSGUI"
if [[ ${use_unstable} == true ]]; then
    make_dir="${aps_project_root}/DevelopmentBranch/APSGUI"
else
    make_dir="${aps_project_root}/MasterBranch"
fi

if [ -n "$APS_PROJECT_DIR" ]; then
  make_dir=$(get_abs_filename "$APS_PROJECT_DIR")
  echo "Directory: " $make_dir
fi

WRITE_WORKFLOW_FILES_TO_PROJECT="yes" \
RMS_PROJECT="${project}" \
USE_TEMORARY_DIR="${USE_TEMORARY_DIR:-yes}" \
PYTHON=${RMS_PYTHON} \
PYTHONPATH="${make_dir}:$PYTHONPATH" \
LD_LIBRARY_PATH=${RMS_LIB}:${LD_LIBRARY_PATH} \
STUB_SUFFIX="${STUB_SUFFIX:-.stub.py}" \
make -C "${make_dir}" generate-workflow-files
