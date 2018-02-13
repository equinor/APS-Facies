#!/bin/bash
# Define environment variables to run the rms installation of python together with APS code and nrlib code
#remove_tmpdir='FALSE'
remove_tmpdir='TRUE'
TMPDIR=tmp_gauss_sim
if [ $remove_tmpdir == 'TRUE' ]
then
   rm -rf $TMPDIR
   echo 'Removed temporary directory: ' $TMPDIR
fi
echo ' '