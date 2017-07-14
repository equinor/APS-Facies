#!/usr/bin/env bash

VENV="$(pwd)/../.venv"

# Using the virtual environment
source "${VENV}/bin/activate"

QT_PREFIX="/opt/Qt/5.9.1/gcc_64"
QT_BIN_DIR="${QT_PREFIX}/bin"
QT_INCLUDE_DIR="${QT_PREFIX}/include"
QT_LIBRARY_PATH="${QT_PREFIX}/lib"
QMAKE_PATH="${QT_BIN_DIR}/qmake"
PATH=${QT_BIN_DIR}:${PATH}

# Setting the working directory
SOURCE=$(pwd)/source
DOCUMENTATION=$(pwd)/../documentation
mkdir -p "${SOURCE}" && cd "${SOURCE}"

# Download and install SIP
SIP_VERSION="4.19.2"
SIP_PREFIX="sip-${SIP_VERSION}"
wget https://sourceforge.net/projects/pyqt/files/sip/${SIP_PREFIX}/${SIP_PREFIX}.tar.gz
tar -xvf ${SIP_PREFIX}.tar.gz -C ${SIP_PREFIX} --strip-components 1
rm -f ${SIP_PREFIX}.tar.gz
cd ${SIP_PREFIX}
python configure.py --sysroot "${VENV}"  --confirm-license
make && make install
# Move documentation
mv sphinx doc
mv doc "${DOCUMENTATION}/${SIP_PREFIX}"

cd ${SOURCE}

# Download and install PyQt
PYQT_VERSION="5.8.2"
PYQT_PREFIX="PyQt-${PYQT_VERSION}"
PYQT_GPL_PREFIX="PyQt5_gpl-${PYQT_VERSION}"
wget https://sourceforge.net/projects/pyqt/files/PyQt5/${PYQT_PREFIX}/${PYQT_GPL_PREFIX}.tar.gz
tar -xvf ${PYQT_GPL_PREFIX}.tar.gz -C ${PYQT_PREFIX} --strip-components 1
rm -f ${PYQT_GPL_PREFIX}.tar.gz
cd ${PYQT_GPL_PREFIX}
python configure.py --sysroot "${VENV}" --qmake=${QMAKE_PATH}  --confirm-license
make && make install
# Move documentation
mv examples doc
mv doc "${DOCUMENTATION}/${PYQT_PREFIX}"

cd ${SOURCE}

## Download and install dip
#DIP_VERSION="0.4.6"
#DIP_PREFIX="dip-${DIP_VERSION}"
#wget "https://www.riverbankcomputing.com/static/Downloads/dip/${DIP_PREFIX}.tar.gz"
#rm -f "${DIP_PREFIX}.tar.gz"
#tar -xvf ${DIP_PREFIX}.tar.gz
#cd ${DIP_PREFIX}
# TODO: Something causes an error when trying to install...
#python setup.py install
#
#cd ${SOURCE}

# Download and install
QSCINTILLA_VERSION="2.10.1"
QSCINTILLA_PREFIX="QScintilla-${QSCINTILLA_VERSION}"
BASE_DIR="$(pwd)/${QSCINTILLA_PREFIX}"
wget "https://sourceforge.net/projects/pyqt/files/QScintilla2/${QSCINTILLA_PREFIX}/QScintilla_gpl-${QSCINTILLA_VERSION}.tar.gz"
tar -xvf QScintilla_gpl-${QSCINTILLA_VERSION}.tar.gz
rm QScintilla_gpl-${QSCINTILLA_VERSION}.tar.gz -C ${QSCINTILLA_PREFIX} --strip-components 1
# Make QScintilla binaries
cd "${BASE_DIR}/Qt4Qt5"
qmake && make
sudo make install
# Make the Python bindings
cd "${BASE_DIR}/Python"
python configure.py --pyqt=PyQt5 --qmake="${QMAKE_PATH}" --sysroot="${VENV}"
make
sudo make install
# Make the Qt Designer plugin
cd "${BASE_DIR}/designer-Qt4Qt5"
qmake && make
sudo make install
# Move documentation
mv example-Qt4Qt5 doc
mv doc "${DOCUMENTATION}/${QSCINTILLA_PREFIX}"

cd ${SOURCE}

# Download and install QCustomPlot for python
export LD_LIBRARY_PATH=${QT_LIBRARY_PATH}:${LD_LIBRARY_PATH}
export LIBRARY_PATH=${QT_LIBRARY_PATH}:${LIBRARY_PATH}
git clone https://github.com/dimv36/QCustomPlot-PyQt5.git
cd QCustomPlot-PyQt5
python setup.py build_ext --qmake "${QMAKE_PATH}" --qt-include-dir "${QT_INCLUDE_DIR}"
# Move examples
mv examples "${DOCUMENTATION}/${QSCINTILLA_PREFIX}"

cd ${SOURCE}

# Clean up
rm -f *.tar.*
rm -rf "${SOURCE}"
