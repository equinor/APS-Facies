#!/bin/bash
# Define environment variables to run the rms installation of python together with APS code and nrlib code
WRITE_SCREEN='TRUE'

# TODO: Ensure that the paths are properly set

# TODO: Ask user if APS_PATH is not set


APS_PATH=/project/idi/personlig/olia/APSGUI
NRLIB_PATH=/project/multiscale/APSGUI/nrlib/nrlib-dist
RMS_VERSION=10.1.1

APS_SRC_PATH=$APS_PATH/src
ROXAR_RMS_ROOT=/prog/roxar/rms/versions/${RMS_VERSION}/linux-amd64-gcc_4_4-release
PYTHONHOME=/prog/roxar/rms/versions/${RMS_VERSION}/linux-amd64-gcc_4_4-release
PYTHONUSERBASE=/private/${USER}/.roxar/rms-10.1/python
export PYTHONPATH=${PYTHONHOME}/bin:${APS_PATH}:${NRLIB_PATH}
export LD_LIBRARY_PATH=/prog/roxar/rms/versions/${RMS_VERSION}/lib/LINUX_64/:${NRLIB_PATH}
export PATH=${ROXAR_RMS_ROOT}/bin:${PYTHONUSERBASE}/bin:${PATH}


if [ $WRITE_SCREEN == 'True' ]
then
    echo 'Python version:  '
    which python
    echo 'PYTHONPATH:' $PYTHONPATH
    echo 'LD_LIBRARY_PATH:' $LD_LIBRARY_PATH
    echo 'PATH:' $PATH
fi

python  ${APS_SRC_PATH}/utils/testPreview.py

echo 'Finished running testPreview'

