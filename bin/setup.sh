#!/usr/bin/env bash

# Update system
sudo apt-get update && sudo apt-get upgrade --yes
sudo apt-get --yes dist-upgrade

# Install GCC, and it's cousins
sudo apt-get install --yes build-essential
# Git
sudo apt-get install --yes git meld
# SSH
sudo apt-get install --yes ssh

# Pyenv dependencies
sudo apt-get install --yes make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev xz-utils tk-dev

# Install Open GL
sudo apt-get install --yes freeglut3-dev
## Multimedia
sudo apt-get install --yes libgstreamer1.0-dev 
## Misc
sudo apt-get install --yes bison flex gperf

PARALLEL_MAKE="-j $(nproc)"

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

mkdir -p ${SOURCE_OPENSSL}\
         ${BUILD_OPENSSL}

wget https://www.openssl.org/source/openssl-${OPENSSL_VERSION}.tar.gz
tar -xvf openssl-${OPENSSL_VERSION}.tar.gz -C ${SOURCE_OPENSSL} --strip-component=1
rm -f openssl-${OPENSSL_VERSION}.tar.gz

cd ${BUILD_OPENSSL}
${SOURCE_OPENSSL}/config --prefix=${OPENSSL_PREFIX} shared
make depend
make ${PARALLEL_MAKE} all
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

OPENSSL_LIBS='-L/opt/ssl/lib -lssl -lcrypto'

# Installing Python
PYTHON_VERSION="3.6.1"
APSGUI_ENVIRONMENT_NAME="aps-gui"

# Install pyenv
cd $HOME
curl -L --proxy $HTTPS_PROXY https://raw.githubusercontent.com/pyenv/pyenv-installer/master/bin/pyenv-installer | bash

# Install python
PYTHON_CONFIGURE_OPTS="--enable-shared" CFLAGS="-O2" https_proxy=${HTTPS_PROXY} pyenv install ${PYTHON_VERSION}

# Create virtual environment
pyenv virtualenv ${PYTHON_VERSION} ${APSGUI_ENVIRONMENT_NAME}
pyenv activate ${APSGUI_ENVIRONMENT_NAME}

# Using the virtual environment
echo "pyenv activate ${APSGUI_ENVIRONMENT_NAME}" >> $HOME/.profile
echo "pyenv activate ${APSGUI_ENVIRONMENT_NAME}" >> $HOME/.login

pip install setuptools --upgrade

# Download, and install PyLint
# Depends on
# * astroid
# * isort
ASTROID_VERSION=1.5.3
ASTROID_PREFIX=astroid-${ASTROID_VERSION}
mkdir -p ${SOURCE_DIR}/${ASTROID_PREFIX}
wget https://github.com/PyCQA/astroid/archive/${ASTROID_PREFIX}.tar.gz
tar -xvf ${ASTROID_PREFIX}.tar.gz
rm -f ${ASTROID_PREFIX}.tar.gz -C ${SOURCE_DIR}/${ASTROID_PREFIX} --strip-components=1
cd ${ASTROID_PREFIX}
python setup.py install -O2


cd ${SOURCE_DIR}

ISORT_VERSION=4.2.15
ISORT_PREFIX=isort-${ISORT_VERSION}
mkdir -p ${SOURCE_DIR}/${ISORT_PREFIX}
wget https://github.com/timothycrosley/isort/archive/${ISORT_VERSION}.tar.gz --output-document=${SOURCE_DIR}/${ISORT_PREFIX}.tar.gz
tar -xvf ${ISORT_PREFIX}.tar.gz -C ${SOURCE_DIR}/${ISORT_PREFIX} --strip-components=1
rm -f ${ISORT_PREFIX}.tar.gz
cd ${ISORT_PREFIX}
python setup.py install -O2


cd ${SOURCE_DIR}

PYLINT_VERSION=1.7.4
PYLINT_PREFIX=pylint-${PYLINT_VERSION}
mkdir -p ${SOURCE_DIR}/${PYLINT_PREFIX}
wget https://github.com/PyCQA/pylint/archive/${PYLINT_PREFIX}.tar.gz
tar -xvf ${PYLINT_PREFIX}.tar.gz -C ${SOURCE_DIR}/${PYLINT_PREFIX} --strip-components=1
rm -f ${PYLINT_PREFIX}.tar.gz
cd ${PYLINT_PREFIX}
python setup.py install -O2


# Download and install other packages that do not need to be compiled
pip --proxy ${HTTPS_PROXY} install --requirement ${SOURCE_DIR}/requirements.txt

cd ${SOURCE_DIR}

# Clean up
rm -f *.tar.*
rm -rf "${SOURCE_DIR}"
rm -rf "${BUILD_DIR}"
