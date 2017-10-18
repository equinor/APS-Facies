FROM centos:6
LABEL version="1.7.2" \
      maintainer="snis@statoil.com" \
      description="This is the Docker image for building, and testing the APS-GUI." \
      "com.statoil.vendor"="Statoil ASA"

######################################################################
#  ___ ___  _____  ____   __  ___ ___ _____ _____ ___ _  _  ___ ___
# | _ \ _ \/ _ \ \/ /\ \ / / / __| __|_   _|_   _|_ _| \| |/ __/ __|
# |  _/   / (_) >  <  \ V /  \__ \ _|  | |   | |  | || .` | (_ \__ \
# |_| |_|_\\___/_/\_\  |_|   |___/___| |_|   |_| |___|_|\_|\___|___/
#
######################################################################
ENV PROXY_SCHEME=http
ENV PROXY_HOST=www-proxy.statoil.no
ENV PROXY_PORT=80
ENV HTTP_PROXY=$PROXY_SCHEME://$PROXY_HOST:$PROXY_PORT
ENV HTTPS_PROXY=$PROXY_SCHEME://$PROXY_HOST:$PROXY_PORT
ENV FTP_PROXY=$PROXY_SCHEME://$PROXY_HOST:$PROXY_PORT
# Tell yum to use the proxy as well
RUN echo "proxy=$HTTP_PROXY" >> /etc/yum.conf
# Install wget and tell wget to use the proxy too
RUN yum update -y \
 && yum install -y wget
RUN echo "https_proxy = $HTTP_PROXY" >> /etc/wgetrc \
 && echo "http_proxy = $HTTPS_PROXY" >> /etc/wgetrc \
 && echo "ftp_proxy = $HTTP_PROXY" >> /etc/wgetrc \
 && echo "use_proxy = on" >> /etc/wgetrc

# Download, and install Statoil's Certificates
ENV STATOIL_CERT="statoil-ca-certificates.el6.rpm"
RUN wget http://st-linrhn01.st.statoil.no/pub/$STATOIL_CERT \
 && yum install -y $STATOIL_CERT \
 && rm -f $STATOIL_CERT

#################################################
#  __  __ ___ ___  ___     __  ___ _  ___   __
# |  \/  |_ _/ __|/ __|   / / | __| \| \ \ / /
# | |\/| || |\__ \ (__   / /  | _|| .` |\ V /
# |_|  |_|___|___/\___| /_/   |___|_|\_| \_/
#
#################################################
ENV CODE_DIR="/code"
ENV PYTHONPATH="$CODE_DIR:$PYTHONPATH"
ENV ENCODING="en_US.UTF-8"
ENV LC_ALL=$ENCODING
ENV LANG=$ENCODING

ENV ROOT_DIR=/software
ENV BUILD_DIR=$ROOT_DIR/build
ENV SOURCE_DIR=$ROOT_DIR/source
ENV INSTALL_DIR=/prog/sdpsoft

ENV GCC_VERSION="4.9.4"
ENV GCC_PREFIX=$INSTALL_DIR/gcc-$GCC_VERSION
COPY ./gcc-$GCC_VERSION $GCC_PREFIX
ENV PATH="$GCC_PREFIX/bin:$PATH"
ENV LD_LIBRARY_PATH="$GCC_PREFIX/lib:$LD_LIBRARY_PATH"
ENV LD_LIBRARY_PATH="$GCC_PREFIX/lib64:$LD_LIBRARY_PATH"
ENV LD_LIBRARY_PATH="$GCC_PREFIX/lib/gcc/x86_64-unknown-linux-gnu/4.9.4:$LD_LIBRARY_PATH"
ENV LD_LIBRARY_PATH="$GCC_PREFIX/lib/gcc/x86_64-unknown-linux-gnu/lib64:$LD_LIBRARY_PATH"

ENV PYTHON_VERSION="3.6.1"
ENV PYTHON_PREFIX=$INSTALL_DIR/python$PYTHON_VERSION
ENV PIP="$PYTHON_PREFIX/bin/pip3 --proxy $http_proxy install"
ENV PYTHON="$PYTHON_PREFIX/bin/python3"
# Fetch Qt from SDPSoft or software_build repo
# Or, build it from scratch and document the steps and add it to software_build repo
# Qt is needed to get the qmake binary which again is used when building pyqt
ENV QT_VERSION="5.9.1"
ENV QT_PREFIX=$INSTALL_DIR/qt-x11-$QT_VERSION
COPY ./qt-x11-$QT_VERSION $QT_PREFIX
ENV PATH="$QT_PREFIX/bin:$PATH"
ENV LD_LIBRARY_PATH="$QT_PREFIX/lib:$LD_LIBRARY_PATH"
ENV LIBRARY_PATH="$QT_PREFIX/lib:$LIBRARY_PATH"

ENV QMAKE=$QT_PREFIX/bin/qmake

## PyQt ##
ENV PYQT_VERSION_MAJOR="5"
ENV PYQT_VERSION_MINOR="9"
ENV PYQT_VERSION=$PYQT_VERSION_MAJOR.$PYQT_VERSION_MINOR

ENV SIP_VERSION="4.19.3"
ENV DIP_VERSION="0.4.6"

ENV PYQTCHARTS_VERSION=$PYQT_VERSION
ENV PYQT3D_VERSION=$PYQT_VERSION
ENV PYQTDATAVISUALIZATION_VERSION=$PYQT_VERSION
ENV PYQTPURCHASING_VERSION=$PYQT_VERSION

ENV QSCINTILLA_VERSION="2.10.1"
ENV PYQTDEPLOY_VERSION="1.3.2"

# Python dependencies
ENV OPENSSL_VERSION="1.1.0f"
ENV NCURSES_VERSION="6.0"
ENV READLINE_VERSION="7.0"
ENV SQLITE3_VERSION=3200100

# PyLint
ENV ASTROID_VERSION="1.5.3"
ENV ISORT_VERSION="4.2.15"
ENV PYLINT_VERSION="1.7.4"

# UPX: Binary compression
ENV UCL_VERSION="1.03"
ENV UPX_VERSION="3.94"
ENV UCL_PREFIX=$INSTALL_DIR/ucl-$UCL_VERSION
ENV UPX_PREFIX=$INSTALL_DIR/upx-$UPX_VERSION

ENV OPENSSL_PREFIX=$INSTALL_DIR/openssl-$OPENSSL_VERSION

VOLUME $CODE_DIR

# Misc. software
RUN yum update -y \
 && yum install -y \
   git \
   graphviz

# Install typical build packages
RUN yum update -y \
 && yum groupinstall -y "Development Tools"
# GCC dependencies
RUN yum update -y \
 && yum install -y \
    bzip2-devel \
    zlib-devel

# Install software needed during build of python and pip install
RUN yum update -y \
 && yum install -y \
    freetype-devel \
    libpng-devel \
    libxml2-devel \
    libxslt-devel \
    libX11-devel \
    libpcap-devel \
    xz-devel \
    expat-devel \
    mesa-libGL-devel


# Precreate all directories to avoid conflicts
RUN mkdir -p $CODE_DIR \
             $ROOT_DIR \
             $BUILD_DIR \
             $SOURCE_DIR \
             $INSTALL_DIR \
             $PYTHON_PREFIX \
             $QT_PREFIX \
             $UCL_PREFIX \
             $UPX_PREFIX/bin

RUN cd $SOURCE_DIR && wget https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tar.xz
RUN cd $SOURCE_DIR && wget https://sourceforge.net/projects/pyqt/files/sip/sip-$SIP_VERSION/sip-$SIP_VERSION.tar.gz
RUN cd $SOURCE_DIR && wget https://sourceforge.net/projects/pyqt/files/PyQt${PYQT_VERSION_MAJOR}/PyQt-$PYQT_VERSION/PyQt5_gpl-$PYQT_VERSION.tar.gz
RUN cd $SOURCE_DIR && wget https://www.openssl.org/source/openssl-"$OPENSSL_VERSION".tar.gz
RUN cd $SOURCE_DIR && wget http://ftp.gnu.org/pub/gnu/ncurses/ncurses-$NCURSES_VERSION.tar.gz
RUN cd $SOURCE_DIR && wget https://ftp.gnu.org/gnu/readline/readline-$READLINE_VERSION.tar.gz
RUN cd $SOURCE_DIR && wget https://sqlite.org/2017/sqlite-autoconf-$SQLITE3_VERSION.tar.gz
RUN cd $SOURCE_DIR && wget https://sourceforge.net/projects/pyqt/files/PyQtChart/PyQtChart-$PYQTCHARTS_VERSION/PyQtChart_gpl-$PYQTCHARTS_VERSION.tar.gz
RUN cd $SOURCE_DIR && wget https://sourceforge.net/projects/pyqt/files/PyQt3D/PyQt3D-$PYQT3D_VERSION/PyQt3D_gpl-$PYQT3D_VERSION.tar.gz
RUN cd $SOURCE_DIR && wget https://sourceforge.net/projects/pyqt/files/PyQtDataVisualization/PyQtDataVisualization-$PYQTDATAVISUALIZATION_VERSION/PyQtDataVisualization_gpl-$PYQTDATAVISUALIZATION_VERSION.tar.gz
RUN cd $SOURCE_DIR && wget https://sourceforge.net/projects/pyqt/files/PyQtPurchasing/PyQtPurchasing-$PYQTPURCHASING_VERSION/PyQtPurchasing_gpl-$PYQTPURCHASING_VERSION.tar.gz
RUN cd $SOURCE_DIR && wget https://sourceforge.net/projects/pyqt/files/QScintilla2/QScintilla-$QSCINTILLA_VERSION/QScintilla_gpl-$QSCINTILLA_VERSION.tar.gz
RUN cd $SOURCE_DIR && wget https://www.riverbankcomputing.com/static/Downloads/dip/dip-$DIP_VERSION.tar.gz
RUN cd $SOURCE_DIR && wget https://www.riverbankcomputing.com/hg/pyqtdeploy/archive/$PYQTDEPLOY_VERSION.tar.gz --output-document=$SOURCE_DIR/pyqt-deploy-$PYQTDEPLOY_VERSION.tar.gz
RUN cd $SOURCE_DIR && wget https://github.com/PyCQA/astroid/archive/astroid-$ASTROID_VERSION.tar.gz
RUN cd $SOURCE_DIR && wget https://github.com/timothycrosley/isort/archive/$ISORT_VERSION.tar.gz --output-document=$SOURCE_DIR/isort-$ISORT_VERSION.tar.gz
RUN cd $SOURCE_DIR && wget https://github.com/PyCQA/pylint/archive/pylint-$PYLINT_VERSION.tar.gz
RUN cd $SOURCE_DIR && wget http://www.oberhumer.com/opensource/ucl/download/ucl-$UCL_VERSION.tar.gz
RUN cd $SOURCE_DIR && wget https://github.com/upx/upx/archive/v$UPX_VERSION.tar.gz --output-document=$SOURCE_DIR/upx-$UPX_VERSION.tar.gz
RUN cd $SOURCE_DIR && wget https://github.com/upx/upx-lzma-sdk/archive/v$UPX_VERSION.tar.gz --output-document=$SOURCE_DIR/upx-lzma-sdk-$UPX_VERSION.tar.gz


 # Create all build directories
RUN cd $BUILD_DIR \
 && mkdir -p \
    python$PYTHON_VERSION \
    sip-$SIP_VERSION \
    pyqt-gpl-$PYQT_VERSION \
    openssl-$OPENSSL_VERSION \
    ncurses-$NCURSES_VERSION \
    readline-$READLINE_VERSION \
    sqlite3-$SQLITE3_VERSION \
    pyqt-chart-$PYQTCHARTS_VERSION \
    pyqt-3d-$PYQT3D_VERSION \
    pyqt-data-visualization-$PYQTDATAVISUALIZATION_VERSION \
    pyqt-purchasing-$PYQTPURCHASING_VERSION \
    qscintilla-$QSCINTILLA_VERSION \
    dip-$DIP_VERSION \
    pyqt-deploy-$PYQTDEPLOY_VERSION \
    astroid-$ASTROID_VERSION \
    isort-$ISORT_VERSION \
    pylint-$PYLINT_VERSION \
    ucl-$UCL_VERSION \
    upx-$UPX_VERSION \
    upx-$UPX_VERSION/src/lzma-sdk

# Extract everything into build directories
RUN cd $BUILD_DIR \
 && tar -xvf  $SOURCE_DIR/Python-$PYTHON_VERSION.tar.xz -C python$PYTHON_VERSION --strip-components=1 \
 && tar -xvf  $SOURCE_DIR/sip-$SIP_VERSION.tar.gz -C sip-$SIP_VERSION --strip-components=1 \
 && tar -xvf  $SOURCE_DIR/PyQt${PYQT_VERSION_MAJOR}_gpl-$PYQT_VERSION.tar.gz -C pyqt-gpl-$PYQT_VERSION --strip-components=1 \
 && tar -xvf  $SOURCE_DIR/openssl-"$OPENSSL_VERSION".tar.gz -C openssl-$OPENSSL_VERSION --strip-components=1 \
 && tar -xvf  $SOURCE_DIR/ncurses-$NCURSES_VERSION.tar.gz -C ncurses-$NCURSES_VERSION --strip-components=1 \
 && tar -xvf  $SOURCE_DIR/readline-$READLINE_VERSION.tar.gz -C readline-$READLINE_VERSION --strip-components=1 \
 && tar -xvf  $SOURCE_DIR/sqlite-autoconf-$SQLITE3_VERSION.tar.gz -C sqlite3-$SQLITE3_VERSION --strip-components=1 \
 && tar -xvf  $SOURCE_DIR/pyqt-deploy-$PYQTDEPLOY_VERSION.tar.gz -C pyqt-deploy-$PYQTDEPLOY_VERSION --strip-components=1 \
 && tar -xvf  $SOURCE_DIR/PyQt3D_gpl-$PYQT3D_VERSION.tar.gz -C pyqt-3d-$PYQT3D_VERSION --strip-components=1 \
 && tar -xvf  $SOURCE_DIR/PyQtChart_gpl-$PYQTCHARTS_VERSION.tar.gz -C pyqt-chart-$PYQTCHARTS_VERSION --strip-components=1 \
 && tar -xvf  $SOURCE_DIR/PyQtDataVisualization_gpl-$PYQTDATAVISUALIZATION_VERSION.tar.gz -C pyqt-data-visualization-$PYQTDATAVISUALIZATION_VERSION --strip-components=1 \
 && tar -xvf  $SOURCE_DIR/PyQtPurchasing_gpl-$PYQTPURCHASING_VERSION.tar.gz -C pyqt-purchasing-$PYQTPURCHASING_VERSION --strip-components=1 \
 && tar -xvf  $SOURCE_DIR/QScintilla_gpl-$QSCINTILLA_VERSION.tar.gz -C qscintilla-$QSCINTILLA_VERSION --strip-components=1 \
 && tar -xvf  $SOURCE_DIR/dip-$DIP_VERSION.tar.gz -C dip-$DIP_VERSION --strip-components=1 \
 && tar -xvf  $SOURCE_DIR/astroid-$ASTROID_VERSION.tar.gz -C astroid-$ASTROID_VERSION --strip-components=1 \
 && tar -xvf  $SOURCE_DIR/isort-$ISORT_VERSION.tar.gz -C isort-$ISORT_VERSION --strip-components=1 \
 && tar -xvf  $SOURCE_DIR/pylint-$PYLINT_VERSION.tar.gz -C pylint-$PYLINT_VERSION --strip-components=1 \
 && tar -xvf  $SOURCE_DIR/ucl-$UCL_VERSION.tar.gz -C ucl-$UCL_VERSION --strip-components=1 \
 && tar -xvf  $SOURCE_DIR/upx-$UPX_VERSION.tar.gz -C upx-$UPX_VERSION --strip-components=1 \
 && tar -xvf  $SOURCE_DIR/upx-lzma-sdk-$UPX_VERSION.tar.gz -C upx-$UPX_VERSION/src/lzma-sdk --strip-components=1

RUN rm -f $SOURCE_DIR/*.tar.*

# Make OpenSSL
RUN cd $BUILD_DIR/openssl-$OPENSSL_VERSION \
 && ./config \
    --prefix=$OPENSSL_PREFIX \
    threads \
    shared \
    zlib \
 && make depend \
 && make all \
 && make install

ENV OPENSSL_LIBS="-L/$OPENSSL_PREFIX/lib -lssl -lcrypto -I$OPENSSL_PREFIX/include/openssl"

# Build UCL library (a dependency for UPX)
RUN cd $BUILD_DIR/ucl-$UCL_VERSION \
 && ./configure --enable-shared CFLAGS='-std=gnu90' --prefix=${UCL_PREFIX} \
 && make \
 && make install

ENV LD_LIBRARY_PATH=$UCL_PREFIX/lib:$LD_LIBRARY_PATH
ENV UPX_UCLDIR=$BUILD_DIR/ucl-$UCL_VERSION

# Download necessary dependency, lzma-sdk
#RUN git clone https://github.com/upx/upx-lzma-sdk.git $BUILD_DIR/upx-$UPX_VERSION/src/lzma-sdk

# Install UPX
RUN cd $BUILD_DIR/upx-$UPX_VERSION \
 && make CHECK_WHITESPACE=/bin/true all \
 && mv $BUILD_DIR/upx-$UPX_VERSION/src/upx.out $UPX_PREFIX/bin/upx

ENV PATH=$UPX_PREFIX/bin:$PATH

#################################
#                               #
# Make prerequisites for Python #
#                               #
#################################

# All of the following envs might not be necessary
# espescially C_INCLUDE_PATH, CPLUS_INCLUDE_PATH, LIBRARY_PATH and LD_RUN_PATH
ENV LD_LIBRARY_PATH "$PYTHON_PREFIX/lib:$LD_LIBRARY_PATH"
ENV PATH "$PYTHON_PREFIX/bin:$PATH"
# QT_PREFIX/include/Qt added to get QtOpenGL
ENV C_INCLUDE_PATH="$PYTHON_PREFIX/include:$QT_PREFIX/include/Qt"
ENV CPLUS_INCLUDE_PATH=$C_INCLUDE_PATH
ENV LIBRARY_PATH="$PYTHON_PREFIX/lib"
ENV LD_RUN_PATH="$PYTHON_PREFIX/lib"

RUN cd $BUILD_DIR/ncurses-$NCURSES_VERSION \
 && ./configure \
    --with-shared \
    --prefix=$PYTHON_PREFIX \
    --enable-sp-funcs \
    --enable-const \
    --enable-rpath \
    --enable-ext-mouse \
 && make \
 && make install

RUN cd $BUILD_DIR/readline-$READLINE_VERSION \
 && ./configure --prefix=$PYTHON_PREFIX \
 && make \
 && make install

RUN cd $BUILD_DIR/sqlite3-$SQLITE3_VERSION \
 && ./configure --prefix=$PYTHON_PREFIX \
                --enable-readline \
                --enable-threadsafe \
                --enable-dynamic-extensions \
                --enable-fts5 \
                --enable-json1 \
                --enable-session \
 && make \
 && make install

# Build Python
# Useful build information here: https://hg.python.org/cpython/file/2.7/README
ENV LD_RIBRARY_PATH="$OPENSSL_PREFIX/lib:$LD_LIBRARY_PATH"
# Add links to OpenSSL for Python
RUN cd $OPENSSL_PREFIX \
 && for folder in $(ls); do \
      mkdir -p $PYTHON_PREFIX/$folder; \
      \cp -Rl $folder/* $PYTHON_PREFIX/$folder/; \
    done
RUN cd $BUILD_DIR/python$PYTHON_VERSION \
 && ./configure \
    --prefix=$PYTHON_PREFIX \
    CPPFLAGS="-I$PYTHON_PREFIX/include/ncurses -I$PYTHON_PREFIX/include/readline -I$OPENSSL_PREFIX/include/openssl -I$QT_PREFIX/include/Qt" \
    --with-threads \
    --enable-shared \
    --enable-ipv6 \
    --enable-unicode=ucs4 \
    --with-doc-strings \
    --with-ssl \
 && make \
 && make install

# Upgrade setuptools
RUN $PIP install setuptools --upgrade

RUN cd $BUILD_DIR/sip-$SIP_VERSION \
 && $PYTHON configure.py \
 && make \
 && make install

RUN yum install -y \
    libicu \
    dbus-devel

RUN cd $BUILD_DIR/pyqt-gpl-$PYQT_VERSION \
 && $PYTHON configure.py \
       --confirm-license \
       --qmake $QMAKE \
       --sip $PYTHON_PREFIX/bin/sip \
       --disable QtNetwork \
       --disable QtWebSockets \
       --disable QtWebKit \
       --disable QtWebKitWidgets \
       --disable QtWebEngine \
       --disable QtWebEngineCore \
       --disable QtWebEngineWidgets \
       --disable QtWebChannel \
 && make -j $(nproc) \
 && make install

# Build PyQt3D
RUN cd $BUILD_DIR/pyqt-3d-$PYQT3D_VERSION \
 && $PYTHON configure.py --qmake=$QMAKE \
 && make -j $(nproc) \
 && make install

# Build PyQtChart
RUN cd $BUILD_DIR/pyqt-chart-$PYQTCHARTS_VERSION \
 && $PYTHON configure.py --qmake=$QMAKE --sip $PYTHON_PREFIX/bin/sip \
 && make -j $(nproc) \
 && make install

RUN cd $BUILD_DIR/pyqt-data-visualization-$PYQTDATAVISUALIZATION_VERSION \
 && $PYTHON configure.py --qmake=$QMAKE --sip $PYTHON_PREFIX/bin/sip \
 && make -j $(nproc) \
 && make install

RUN cd $BUILD_DIR/pyqt-purchasing-$PYQTPURCHASING_VERSION \
 && $PYTHON configure.py --qmake=$QMAKE --sip $PYTHON_PREFIX/bin/sip \
 && make -j $(nproc) \
 && make install

# Make QScintilla binaries
RUN cd $BUILD_DIR/qscintilla-$QSCINTILLA_VERSION/Qt4Qt5 \
 && $QMAKE \
 && make -j $(nproc) \
 && make install

# Make the Python bindings for QScintilla
RUN cd $BUILD_DIR/qscintilla-$QSCINTILLA_VERSION/Python \
 && $PYTHON configure.py --pyqt=PyQt5 --qmake=$QMAKE \
 && make \
 && make install

# Make the Qt Designer plugin
RUN cd $BUILD_DIR/qscintilla-$QSCINTILLA_VERSION/designer-Qt4Qt5 \
 && $QMAKE \
 && make \
 && make install

# Make DIP
RUN cd $BUILD_DIR/dip-$DIP_VERSION \
 && $PYTHON setup.py install

# Make PyQt-deploy
RUN cd $BUILD_DIR/pyqt-deploy-$PYQTDEPLOY_VERSION \
 && $PYTHON setup.py install

# Download, and install PyLint
# Depends on
# * astroid
# * isort
RUN cd $BUILD_DIR/astroid-$ASTROID_VERSION \
 && $PYTHON setup.py install -O2

RUN cd $BUILD_DIR/isort-$ISORT_VERSION \
 && $PYTHON setup.py install -O2

RUN cd $BUILD_DIR/pylint-$PYLINT_VERSION \
 && $PYTHON setup.py install -O2

##
# Final clean-up
RUN rm -rf $SOURCE_DIR
RUN rm -rf $BUILD_DIR

#####################
#                   #
#  Adding the repo  #
#                   #
#####################

RUN mkdir -p $CODE_DIR
VOLUME $CODE_DIR

# Install all python modules

COPY requirements.txt /requirements.txt
RUN $PIP install -r /requirements.txt \
 && rm -f /requirements.txt
