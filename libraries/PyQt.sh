#!/usr/bin/env bash

VENV="$(pwd)/../.venv"

# Using the virtual environment
source ./../.venv/bin/activate

QT_PREFIX="/opt/Qt/5.9.1/gcc_64"
QT_BIN_DIR="${QT_PREFIX}/bin"
QT_INCLUDE_DIR="${QT_PREFIX}/include"
QT_LIBRARY_PATH="${QT_PREFIX}/lib"
QMAKE_PATH="${QT_BIN_DIR}/qmake"
PATH=${QT_BIN_DIR}:${PATH}

# Setting the working directory
SOURCE=$(pwd)/source
mkdir -p "${SOURCE}" && cd "${SOURCE}"

# Download and install SIP
SIP_VERSION="4.19.2"
SIP_PREFIX="sip-${SIP_VERSION}"
wget https://sourceforge.net/projects/pyqt/files/sip/${SIP_PREFIX}/${SIP_PREFIX}.tar.gz
tar -xvf ${SIP_PREFIX}.tar.gz
cd ${SIP_PREFIX}
python configure.py --sysroot "${VENV}"  --confirm-license
make
make install

cd ${SOURCE}

# Download and install PyQt
PYQT_VERSION="5.8.2"
PYQT_PREFIX="PyQt-${PYQT_VERSION}"
PYQT_GPL_PREFIX="PyQt5_gpl-${PYQT_VERSION}"
wget https://sourceforge.net/projects/pyqt/files/PyQt5/${PYQT_PREFIX}/${PYQT_GPL_PREFIX}.tar.gz
tar -xvf ${PYQT_GPL_PREFIX}.tar.gz
cd ${PYQT_GPL_PREFIX}
python configure.py --sysroot "${VENV}" --qmake=${QMAKE_PATH}  --confirm-license
make
make install

cd ${SOURCE}

## Download and install dip
#DIP_VERSION="0.4.6"
#DIP_PREFIX="dip-${DIP_VERSION}"
#wget https://www.riverbankcomputing.com/static/Downloads/dip/${DIP_PREFIX}.tar.gz
#tar -xvf ${DIP_PREFIX}.tar.gz
#cd ${DIP_PREFIX}
#python setup.py install
#
#cd ${SOURCE}

# Download and install QCustomPlot for python
export LD_LIBRARY_PATH=${QT_LIBRARY_PATH}:${LD_LIBRARY_PATH}
export LIBRARY_PATH=${QT_LIBRARY_PATH}:${LIBRARY_PATH}
git clone https://github.com/dimv36/QCustomPlot-PyQt5.git
cd QCustomPlot-PyQt5
python setup.py build_ext --qmake "${QMAKE_PATH}" --qt-include-dir "${QT_INCLUDE_DIR}"

# Clean up
rm -f *.tar.*
