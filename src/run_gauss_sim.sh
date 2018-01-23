#!/bin/bash
# Define environment variables to run the rms installation of python together with APS code and nrlib code
#remove_tmpdir='FALSE'
remove_tmpdir='TRUE'
fixed_tmp_dir='TRUE'
WRITE_SCREEN='TRUE'

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

echo ' '
echo 'Start running Gauss field simulations by running APS_simulate_gauss_multiprocessing.py'

# Create a tmp directory for simulated results exists, if it exist remove it and create it again.
if [ $fixed_tmp_dir == 'TRUE' ]; then
   TMPDIR=tmp_gauss_sim
   mkdir -p $TMPDIR
   echo 'TMPDIR: ' $TMPDIR
else
   TMPDIR=$(mktemp -d  tmp_gauss_simXXXXXXXXXX)
   echo 'TMPDIR: ' $TMPDIR
fi


python ${APS_SRC_PATH}/APS_simulate_gauss_multiprocessing.py


echo 'Finished running Gauss field simulations'
