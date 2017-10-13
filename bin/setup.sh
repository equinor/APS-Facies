#!/usr/bin/env bash

# Update system
sudo apt-get update && sudo apt-get upgrade --yes
sudo apt-get --yes dist-upgrade

# Install GCC, and it's cusins
sudo apt-get install --yes build-essential
# Git
sudo apt-get install --yes git meld
# SSH
sudo apt-get install --yes ssh

# Pyenv dependencies
sudo apt-get install --yes make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev xz-utils tk-dev

# Install Qt dependencies
# Install Open GL
sudo apt-get install --yes freeglut3-dev
## Qt for X11
sudo apt-get install --yes libfontconfig1-dev libfreetype6-dev libx11-dev libxext-dev libxfixes-dev libxi-dev libxrender-dev libxcb1-dev libx11-xcb-dev libxcb-glx0-dev libxcb-keysyms1-dev libxcb-image0-dev libxcb-shm0-dev libxcb-icccm4-dev libxcb-sync-dev libxcb-xfixes0-dev libxcb-shape0-dev libxcb-randr0-dev libxcb-render-util0-dev libproxy-dev
## Multimedia
sudo apt-get install --yes libgstreamer1.0-dev 
## Qt WebKit
sudo apt-get install --yes dbus dbus-x11 libdbus-1-dev fontconfig libdrm-dev libxcomposite-dev libxcursor-dev libxi-dev libxrandr-dev xscreensaver libxtst-dev libcap-dev libegl1-mesa-dev
## Misc
sudo apt-get install --yes bison flex gperf

PARALELL_MAKE="-j $(nproc)"

BUILD_DIR="$HOME/build"
SOURCE_DIR="$HOME/source"

mkdir -p $BUILD_DIR \
         $SOURCE_DIR

HTTPS_PROXY="http://www-proxy.statoil.no:80"

# Download and install OpenSSL
OPENSSL_VERSION="1.1.0f"
OPENSSL_BUILD_PREFIX="$BUILD_DIR/openssl-$OPENSSL_VERSION"
OPENSSL_PREFIX="/opt/ssl"

SOURCE_OPENSSL="$SOURCE_DIR/openssl-$OPENSSL_VERSION"
BUILD_OPENSSL="$BUILD_DIR/openssl-$OPENSSL_VERSION"

mkdir -p $SOURCE_OPENSSL\
         $BUILD_OPENSSL

wget https://www.openssl.org/source/openssl-$OPENSSL_VERSION.tar.gz
tar -xvf openssl-$OPENSSL_VERSION.tar.gz -C $SOURCE_OPENSSL --strip-component=1
rm -f openssl-$OPENSSL_VERSION.tar.gz

cd $BUILD_OPENSSL
$SOURCE_OPENSSL/config --prefix=$OPENSSL_PREFIX shared
make depend
make $PARALELL_MAKE all
make test
sudo make install


cd ${SOURCE_DIR}

# Download and install SQLite
SQLITE3_VERSION=3200100
wget https://sqlite.org/2017/sqlite-autoconf-${SQLITE3_VERSION}.tar.gz
tar -xvf sqlite-autoconf-${SQLITE3_VERSION}.tar.gz
rm -f sqlite-autoconf-${SQLITE3_VERSION}.tar.gz
cd sqlite-autoconf-${SQLITE3_VERSION}
./configure --enable-readline \
            --enable-threadsafe \
            --enable-dynamic-extensions \
            --enable-fts5 \
            --enable-json1 \
            --enable-session
make
make install

# Download and install Qt
QT_VERSION_MAJOR="5"
QT_VERSION_MINOR="9"
QT_VERSION_REVISION="1"
QT_VERSION=$QT_VERSION_MAJOR.$QT_VERSION_MINOR.$QT_VERSION_REVISION
QT_PREFIX="/opt/Qt/${QT_VERSION}"

SOURCE_QT="$SOURCE_DIR/qt-$QT_VERSION"
BUILD_QT="$BUILD_DIR/qt-$QT_VERSION"

QT_BIN_DIR="${QT_PREFIX}/bin"
QT_INCLUDE_DIR="${QT_PREFIX}/include"
QT_LIBRARY_PATH="${QT_PREFIX}/lib"

QMAKE="${QT_BIN_DIR}/qmake"
PATH=${QT_BIN_DIR}:${PATH}

OPENSSL_LIBS='-L/opt/ssl/lib -lssl -lcrypto' 

sudo mkdir -p $QT_PREFIX
mkdir -p $SOURCE_QT \
         $BUILD_QT


wget http://download.qt.io/archive/qt/$QT_VERSION_MAJOR.$QT_VERSION_MINOR/$QT_VERSION/single/qt-everywhere-opensource-src-$QT_VERSION.tar.xz
tar -xJvf qt-everywhere-opensource-src-$QT_VERSION.tar.xz -C $SOURCE_QT --strip-components=1
rm -f qt-everywhere-opensource-src-$QT_VERSION.tar.xz

cd $BUILD_QT
$SOURCE_QT/configure \
    -prefix $QT_PREFIX \
    -opengl \
    -shared \
    -no-strip \
    -opensource \
    -confirm-license \
    -developer-build \
    -nomake examples \
    -nomake tests \
    -qt-zlib \
    -qt-libpng \
    -qt-libjpeg \
    -qt-freetype \
    -qt-harfbuzz \
    -qt-pcre \
    -qt-xcb \
    -qt-xkbcommon \
    -openssl-linked

sudo make
sudo make install

echo "export PATH=$QT_PREFIX/bin:$PATH" >> $HOME/.profile
echo "export LD_LIBRARY_PATH=$QT_LIBRARY_PATH:$LD_LIBRARY_PATH" >> $HOME/.profile

echo "setenv PATH $QT_PREFIX/bin:$PATH" >> $HOME/.login
echo "setenv LD_LIBRARY_PATH $QT_LIBRARY_PATH:$LD_LIBRARY_PATH" >> $HOME/.login

sudo echo "PATH=$QT_PREFIX/bin:$PATH" >> /etc/environment
sudo echo "export LD_LIBRARY_PATH=$QT_LIBRARY_PATH:$LD_LIBRARY_PATH" >> /etc/environment

# Installing Python, and PyQt
PYTHON_VERSION="3.6.1"
APSGUI_ENVIRONMENT_NAME="aps-gui"

# Install pyenv
cd $HOME
curl -L --proxy $HTTPS_PROXY https://raw.githubusercontent.com/pyenv/pyenv-installer/master/bin/pyenv-installer | bash

# Install python
PYTHON_CONFIGURE_OPTS="--enable-shared" CFLAGS="-O2" https_proxy=$HTTPS_PROXY pyenv install $PYTHON_VERSION

# Create virtual environment
pyenv virtualenv ${PYTHON_VERSION} ${APSGUI_ENVIRONMENT_NAME}
pyenv activate ${APSGUI_ENVIRONMENT_NAME}

# Using the virtual environment
echo "pyenv activate ${APSGUI_ENVIRONMENT_NAME}" >> $HOME/.profile
echo "pyenv activate ${APSGUI_ENVIRONMENT_NAME}" >> $HOME/.login

pip install setuptools --upgrade

# Download and install SIP
SIP_VERSION="4.19.3"
SIP_PREFIX="sip-${SIP_VERSION}"

SOURCE_SIP="$SOURCE_DIR/sip-$SIP_VERSION"
BUILD_SIP="$BUILD_DIR/sip-$SIP_VERSION"

mkdir -p $SOURCE_SIP \
         $BUILD_SIP

wget https://sourceforge.net/projects/pyqt/files/sip/${SIP_PREFIX}/${SIP_PREFIX}.tar.gz
tar -xvf ${SIP_PREFIX}.tar.gz -C ${SOURCE_SIP} --strip-components 1
rm -f $SIP_PREFIX.tar.gz

cd ${BUILD_SIP}
python $SOURCE_SIP/configure.py
make $PARALELL_MAKE
make install

cd ${SOURCE_DIR}

# Download and install QScintilla
QSCINTILLA_VERSION="2.10.1"
QSCINTILLA_PREFIX="QScintilla-${QSCINTILLA_VERSION}"

SOURCE_QSCINTILLA="$SOURCE_DIR/QScintilla_gpl-${QSCINTILLA_VERSION}"
BUILD_QSCINTILLA="$BUILD_DIR/QScintilla-${QSCINTILLA_VERSION}"

mkdir -p $SOURCE_QSCINTILLA \
         $BUILD_QSCINTILLA \
         $BUILD_QSCINTILLA/Qt4Qt5 \
         $BUILD_QSCINTILLA/Python \
         $BUILD_QSCINTILLA/designer-Qt4Qt5

wget "https://sourceforge.net/projects/pyqt/files/QScintilla2/${QSCINTILLA_PREFIX}/QScintilla_gpl-${QSCINTILLA_VERSION}.tar.gz"
tar -xvf QScintilla_gpl-${QSCINTILLA_VERSION}.tar.gz  -C ${SOURCE_QSCINTILLA} --strip-components=1
rm -f QScintilla_gpl-${QSCINTILLA_VERSION}.tar.gz

# Make QScintilla binaries
# FIXME: Error when building in different directory than the source directory.
cd "${SOURCE_QSCINTILLA}/Qt4Qt5"
$QMAKE
make $PARALELL_MAKE
sudo make install


cd ${SOURCE_DIR}

PYQT_VERSION="5.9"
# Download and install PyQt, and its modules
declare -a pyqt_modules
pyqt_modules=("PyQt5" "PyQt3D" "PyQtChart" "PyQtDataVisualization" "PyQtPurchasing")
for module_name in ${pyqt_modules}; do
    if [[ $module_name == "PyQt5" ]]; then
        PyQt_module_prefix="PyQt-${PYQT_VERSION}"
        confirm="--confirm-license"
    else
        PyQt_module_prefix="${module_name}-${PYQT_VERSION}"
        confirm=""
    fi
    PyQt_module_gps_prefix="${module_name}_gpl-${PYQT_VERSION}"

    mkdir -p ${SOURCE_DIR}/${PyQt_module_prefix} ${BUILD_DIR}/${PyQt_module_prefix}

    wget https://sourceforge.net/projects/pyqt/files/${module_name}/${PyQt_module_prefix}/${PyQt_module_gps_prefix}.tar.gz
    tar -xvf ${PyQt_module_gps_prefix}.tar.gz -C ${SOURCE_DIR}/${PyQt_module_prefix} --strip-components 1
    rm -f ${PyQt_module_gps_prefix}.tar.gz

    # FIXME: Fails when trying to build from other directory
    cd ${SOURCE_DIR}/${PyQt_module_prefix}
    python configure.py --qmake=${QMAKE} $confirm
    sudo make
    sudo make install
done

# Make the Python bindings for QScintilla
cd "${SOURCE_QSCINTILLA}/Python"
python configure.py --pyqt=PyQt5 --qmake="${QMAKE}"
make
sudo make install
# Make the Qt Designer plugin
cd "${SOURCE_QSCINTILLA}/designer-Qt4Qt5"
$QMAKE
make
sudo make install

## Download and install dip
DIP_VERSION="0.4.6"
DIP_PREFIX="dip-${DIP_VERSION}"

SOURCE_DIP=${SOURCE_DIR}/${DIP_PREFIX}
BUILD_DIP=${BUILD_DIR}/${DIP_PREFIX}

mkdir -p $SOURCE_DIP $BUILD_DIP

cd ${SOURCE_DIR}

wget "https://www.riverbankcomputing.com/static/Downloads/dip/${DIP_PREFIX}.tar.gz"
tar -xvf ${DIP_PREFIX}.tar.gz -C $SOURCE_DIP --strip-components=1
rm ${DIP_PREFIX}.tar.gz
cd ${SOURCE_DIP}
# Install
python setup.py install
# Test
python test/runtests.py


cd ${SOURCE_DIR}

# Download and install latest (before 3.3) PyInstaller
git clone https://github.com/pyinstaller/pyinstaller.git
cd ${SOURCE_DIR}/pyinstaller/bootloader
python ./waf distclean all
cd ${SOURCE_DIR}/pyinstaller
pip --proxy $HTTPS_PROXY install macholib
python setup.py install


cd ${SOURCE_DIR}

# Download, and install PyLint
# Depends on
# * astroid
# * isort
ASTROID_VERSION=1.5.3
ASTROID_PREFIX=astroid-$ASTROID_VERSION
mkdir -p $SOURCE_DIR/$ASTROID_PREFIX
wget https://github.com/PyCQA/astroid/archive/$ASTROID_PREFIX.tar.gz
tar -xvf $ASTROID_PREFIX.tar.gz
rm -f $ASTROID_PREFIX.tar.gz -C $SOURCE_DIR/$ASTROID_PREFIX --strip-components=1
cd $ASTROID_PREFIX
python setup.py install -O2


cd ${SOURCE_DIR}

ISORT_VERSION=4.2.15
ISORT_PREFIX=isort-$ISORT_VERSION
mkdir -p $SOURCE_DIR/$ISORT_PREFIX
wget https://github.com/timothycrosley/isort/archive/$ISORT_VERSION.tar.gz --output-document=$SOURCE_DIR/$ISORT_PREFIX.tar.gz
tar -xvf $ISORT_PREFIX.tar.gz -C $SOURCE_DIR/$ISORT_PREFIX --strip-components=1
rm -f $ISORT_PREFIX.tar.gz
cd $ISORT_PREFIX
python setup.py install -O2


cd ${SOURCE_DIR}

PYLINT_VERSION=1.7.4
PYLINT_PREFIX=pylint-$PYLINT_VERSION
mkdir -p $SOURCE_DIR/$PYLINT_PREFIX
wget https://github.com/PyCQA/pylint/archive/$PYLINT_PREFIX.tar.gz
tar -xvf $PYLINT_PREFIX.tar.gz -C $SOURCE_DIR/$PYLINT_PREFIX --strip-components=1
rm -f $PYLINT_PREFIX.tar.gz
cd $PYLINT_PREFIX
python setup.py install -O2




# Download and install other packages that do not need to be compiled
# TODO: Add pyqtdeploy==1.3.2 to requiremens.txt
pip --proxy $HTTPS_PROXY install --requirement ${SOURCE_DIR}/requirements.txt

cd ${SOURCE_DIR}


# Download and install UPX
## Prerequisite; UCL
UCL_VERSION="1.03"
export UPX_UCLDIR=${SOURCE_DIR}/ucl-${UCL_VERSION}
wget http://www.oberhumer.com/opensource/ucl/download/ucl-${UCL_VERSION}.tar.gz
tar -xvf ucl-${UCL_VERSION}.tar.gz
rm -f ucl-${UCL_VERSION}.tar.gz
cd ucl-${UCL_VERSION}
./configure --enable-shared CFLAGS='-std=gnu90' --prefix='${HOME}/workspace/APS-GUI/.venv'
make
make install

git clone https://github.com/upx/upx.git
cd upx
git submodule update --init --recursive
make all
mv src/upx.out /usr/local/bin/upx

# Fix fonts
sudo apt-get install --yes ttf-dejavu
cp -R /usr/share/fonts/truetype $QT_LIBRARY_PATH/fonts
cd $QT_LIBRARY_PATH/fonts
for folder in $(ls -d */); do
    mv $folder/* .
    rmdir $folder
done

# Clean up
rm -f *.tar.*
rm -rf "${SOURCE_DIR}"
rm -rf "${BUILD_DIR}"
