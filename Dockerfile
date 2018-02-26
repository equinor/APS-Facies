FROM git.statoil.no:4567/sdp/sdpsoft/gcc:7.3.0 as gcc
FROM centos:6
LABEL version="2.3.0" \
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

ENV http_proxy=$HTTP_PROXY
ENV https_proxy=$HTTPS_PROXY
ENV ftp_proxy=$FTP_PROXY

# Tell yum to use the proxy as well
RUN echo "proxy=$HTTP_PROXY" >> /etc/yum.conf
# Install wget and tell wget to use the proxy too
RUN yum update -y \
 && yum install -y wget
RUN echo "https_proxy = $HTTP_PROXY" >> /etc/wgetrc \
 && echo "http_proxy = $HTTPS_PROXY" >> /etc/wgetrc \
 && echo "ftp_proxy = $HTTP_PROXY" >> /etc/wgetrc \
 && echo "use_proxy = on" >> /etc/wgetrc \
 && echo "ca-directory = /etc/pki/ca-trust/source/anchors" >> /etc/wgetrc

# Download, and install Statoil's Certificates
ENV STATOIL_CERT="statoil-ca-certificates-1.0-7.el7.noarch.rpm"
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
ENV ENCODING="en_US.UTF-8"
ENV LC_ALL=$ENCODING
ENV LANG=$ENCODING

ENV ROOT_DIR=/software
ENV BUILD_DIR=$ROOT_DIR/build
ENV SOURCE_DIR=$ROOT_DIR/source
ENV INSTALL_DIR=/prog/sdpsoft

ENV GCC_VERSION="7.3.0"
ENV GCC_PREFIX=$INSTALL_DIR/gcc-$GCC_VERSION
COPY --from=gcc $GCC_PREFIX $GCC_PREFIX
ENV PATH="$GCC_PREFIX/bin:$PATH"
ENV LD_LIBRARY_PATH="$GCC_PREFIX/lib:$LD_LIBRARY_PATH"
ENV LD_LIBRARY_PATH="$GCC_PREFIX/lib64:$LD_LIBRARY_PATH"
ENV LD_LIBRARY_PATH="$GCC_PREFIX/lib/gcc/x86_64-unknown-linux-gnu/4.9.4:$LD_LIBRARY_PATH"
ENV LD_LIBRARY_PATH="$GCC_PREFIX/lib/gcc/x86_64-unknown-linux-gnu/lib64:$LD_LIBRARY_PATH"

ENV PYTHON_VERSION="3.6.1"
ENV PYTHON_PREFIX=$INSTALL_DIR/python$PYTHON_VERSION
ENV PIP="$PYTHON_PREFIX/bin/pip3 --proxy $HTTP_PROXY"
ENV PYTHON="$PYTHON_PREFIX/bin/python3"
ENV PYTHONOPTIMIZE=x
# All running python sould be done with optimized bytecode (-O)

# Python dependencies
ENV OPENSSL_VERSION="1.1.0g"
ENV NCURSES_VERSION="6.1"
ENV READLINE_VERSION="7.0"
ENV SQLITE3_VERSION="3210000"
ENV ZLIB_VERSION="1.2.11"
ENV BZIP2_VERSION="1.0.6"

# TCL_VERSION == TK_VERSION
ENV TCL_VERSION="8.6.8"
ENV TK_VERSION=$TCL_VERSION
# APSW (SQLite wrapper)
ENV APSW_VERSION="3.21.0-r1"
ENV APSW_PREFIX=$INSTALL_DIR/apsw-$APSW_VERSION

# Misc. software
RUN yum update -y \
 && yum install -y \
   git \
   graphviz

# Install typical build packages
RUN yum update -y \
 && yum groupinstall -y "Development Tools"

# Install software needed during build of python and pip install
RUN yum update -y \
 && yum install -y \
    freetype-devel \
    libpng-devel \
    libxml2-devel \
    libxslt-devel \
    libX11-devel \
    openmpi-devel \
    lapack-devel \
    libicu-devel \
    libpcap-devel \
    xz-devel \
    expat-devel \
    mesa-libGL-devel


# Precreate all directories to avoid conflicts
RUN mkdir -p $ROOT_DIR \
             $BUILD_DIR \
             $SOURCE_DIR \
             $INSTALL_DIR \
             $PYTHON_PREFIX \
             apsw-$APSW_VERSION

RUN cd $SOURCE_DIR && wget https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tar.xz
RUN cd $SOURCE_DIR && wget https://www.openssl.org/source/openssl-"$OPENSSL_VERSION".tar.gz
RUN cd $SOURCE_DIR && wget http://zlib.net/zlib-$ZLIB_VERSION.tar.gz
RUN cd $SOURCE_DIR && wget http://ftp.gnu.org/pub/gnu/ncurses/ncurses-$NCURSES_VERSION.tar.gz
RUN cd $SOURCE_DIR && wget https://ftp.gnu.org/gnu/readline/readline-$READLINE_VERSION.tar.gz
RUN cd $SOURCE_DIR && wget https://sqlite.org/2017/sqlite-autoconf-$SQLITE3_VERSION.tar.gz
RUN cd $SOURCE_DIR && wget https://sourceforge.net/projects/tcl/files/Tcl/$TCL_VERSION/tcl"$TCL_VERSION"-src.tar.gz
RUN cd $SOURCE_DIR && wget https://sourceforge.net/projects/tcl/files/Tcl/$TK_VERSION/tk"$TK_VERSION"-src.tar.gz
RUN cd $SOURCE_DIR && wget http://www.bzip.org/$BZIP2_VERSION/bzip2-$BZIP2_VERSION.tar.gz
RUN cd $SOURCE_DIR && wget https://github.com/rogerbinns/apsw/archive/$APSW_VERSION.tar.gz --output-document=$SOURCE_DIR/apsw-$APSW_VERSION.tar.gz


 # Create all build directories
RUN cd $BUILD_DIR \
 && mkdir -p \
    python$PYTHON_VERSION \
    openssl-$OPENSSL_VERSION \
    zlib-$ZLIB_VERSION \
    ncurses-$NCURSES_VERSION \
    readline-$READLINE_VERSION \
    tcl-$TCL_VERSION \
    tk-$TK_VERSION \
    bzip2-$BZIP2_VERSION \
    sqlite3-$SQLITE3_VERSION \
    apsw-$APSW_VERSION

# Extract everything into build directories
RUN cd $BUILD_DIR \
 && tar -xvf  $SOURCE_DIR/Python-$PYTHON_VERSION.tar.xz -C python$PYTHON_VERSION --strip-components=1 \
 && tar -xvf  $SOURCE_DIR/openssl-"$OPENSSL_VERSION".tar.gz -C openssl-$OPENSSL_VERSION --strip-components=1 \
 && tar -xvf  $SOURCE_DIR/ncurses-$NCURSES_VERSION.tar.gz -C ncurses-$NCURSES_VERSION --strip-components=1 \
 && tar -xvf  $SOURCE_DIR/readline-$READLINE_VERSION.tar.gz -C readline-$READLINE_VERSION --strip-components=1 \
 && tar -xvf  $SOURCE_DIR/tcl"$TCL_VERSION"-src.tar.gz -C tcl-$TCL_VERSION --strip-components=1 \
 && tar -xvf  $SOURCE_DIR/tk"$TK_VERSION"-src.tar.gz -C tk-$TK_VERSION --strip-components=1 \
 && tar -xvf  $SOURCE_DIR/bzip2-$BZIP2_VERSION.tar.gz -C bzip2-$BZIP2_VERSION --strip-components=1 \
 && tar -xvf  $SOURCE_DIR/sqlite-autoconf-$SQLITE3_VERSION.tar.gz -C sqlite3-$SQLITE3_VERSION --strip-components=1 \
 && tar -xvf  $SOURCE_DIR/apsw-$APSW_VERSION.tar.gz -C apsw-$APSW_VERSION --strip-components=1 \
 && tar -xvf  $SOURCE_DIR/zlib-$ZLIB_VERSION.tar.gz -C zlib-$ZLIB_VERSION --strip-components=1

RUN rm -f $SOURCE_DIR/*.tar.*

#################################
#                               #
# Make prerequisites for Python #
#                               #
#################################

# All of the following envs might not be necessary
# espescially C_INCLUDE_PATH, CPLUS_INCLUDE_PATH, LIBRARY_PATH and LD_RUN_PATH
ENV LD_LIBRARY_PATH "$PYTHON_PREFIX/lib:$LD_LIBRARY_PATH"
ENV PATH "$PYTHON_PREFIX/bin:$PATH"
ENV C_INCLUDE_PATH="$PYTHON_PREFIX/include"
ENV CPLUS_INCLUDE_PATH="$C_INCLUDE_PATH"
ENV LIBRARY_PATH="$PYTHON_PREFIX/lib"
ENV LD_RUN_PATH="$PYTHON_PREFIX/lib"

RUN cd $BUILD_DIR/bzip2-$BZIP2_VERSION \
 # First, build bzip2.so libs
 && make -f Makefile-* \
 && make install prefix=$PYTHON_PREFIX \
 # Then, build bzip2
 && make -f Makefile \
 && make install prefix=$PYTHON_PREFIX

# Make Zlib
RUN cd $BUILD_DIR/zlib-$ZLIB_VERSION \
 # Install to default path to avoid issues with library linker when published to SDPSoft
 && ./configure --64 \
 && make \
 && make install

# Make OpenSSL
RUN cd $BUILD_DIR/openssl-$OPENSSL_VERSION \
 && ./config \
    --prefix=$PYTHON_PREFIX \
    threads \
    shared \
    --openssldir=$PYTHON_PREFIX/openssl \
    zlib \
 && make depend \
 && make all \
 && make install

ENV OPENSSL_LIBS="-L/$OPENSSL_PREFIX/lib -lssl -lcrypto -I$OPENSSL_PREFIX/include/openssl"


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
                CFLAGS="-O2" \
                --enable-readline \
                --enable-threadsafe \
                --enable-dynamic-extensions \
                --enable-fts5 \
                --enable-json1 \
                --enable-session \
                --disable-static \
 && make \
 && make install

RUN cd $BUILD_DIR/tcl-$TCL_VERSION/unix \
 && ./configure --prefix=$PYTHON_PREFIX --enable-threads \
 && make \
 && make install

RUN cd $BUILD_DIR/tk-$TK_VERSION/unix \
 && ./configure \
    --prefix=$PYTHON_PREFIX \
    --with-threads \
    --enable-shared \
    --with-tcl=$BUILD_DIR/tcl-$TCL_VERSION/unix \
 && make \
 && make install

# Build Python
# Useful build information here: https://hg.python.org/cpython/file/2.7/README
RUN cd $BUILD_DIR/python$PYTHON_VERSION \
 && ./configure \
    --prefix=$PYTHON_PREFIX \
    CPPFLAGS="-O2 -I$PYTHON_PREFIX/include/ncurses -I$PYTHON_PREFIX/include/readline -I$PYTHON_PREFIX/include/openssl" \
    LDFLAGS="-L$PYTHON_PREFIX/lib -lssl -lcrypto -lsqlite3" \
    --with-threads \
    --enable-shared \
    --enable-ipv6 \
    --enable-unicode=ucs4 \
    --with-doc-strings \
    --enable-optimizations \
    --enable-profiling  \
    --enable-loadable-sqlite-extensions \
 && make -j $(nproc) \
 && make install

# Upgrade setuptools
RUN $PIP install setuptools --upgrade

# Build, and install APSW binding for SQLite
# Note, APSW cannot be installed via PIP (yet)
RUN cd $BUILD_DIR/apsw-$APSW_VERSION \
 && $PYTHON setup.py build --enable-all-extensions \
 && $PYTHON setup.py install \
 && $PYTHON setup.py test

# Install MKL
ENV INTEL_MKL_VERSION="2018.1.163"
ENV INTEL_MKL="l_mkl_$INTEL_MKL_VERSION"
ENV INTEL_MKL_SEED=12414
ENV INTEL_PREFIX="$SOURCE_DIR/$INTEL_MKL"

RUN mkdir -p $INTEL_PREFIX

# Configure setup
ENV INTEL_CONFIGURATION="$INTEL_PREFIX/config.txt"
RUN echo ACCEPT_EULA=accept >> $INTEL_CONFIGURATION \
 && echo PSET_INSTALL_DIR=/opt/intel >> $INTEL_CONFIGURATION \
 && echo PSET_MODE=install >> $INTEL_CONFIGURATION \
 && echo COMPONENTS="\
;intel-comp-l-all-vars__noarch\
;intel-comp-nomcu-vars__noarch\
;intel-openmp__x86_64\
;intel-tbb-libs__x86_64\
;intel-mkl-common__noarch\
;intel-mkl-installer-license__noarch\
;intel-mkl-core__x86_64\
;intel-mkl-core-rt__x86_64\
;intel-mkl-gnu__x86_64\
;intel-mkl-gnu-rt__x86_64\
;intel-mkl-cluster__x86_64\
;intel-mkl-cluster-common__noarch\
;intel-mkl-cluster-rt__x86_64\
;intel-mkl-common-ps__noarch\
;intel-mkl-core-ps__x86_64\
;intel-mkl-common-c__noarch\
;intel-mkl-core-c__x86_64\
;intel-mkl-common-c-ps__noarch\
;intel-mkl-cluster-c__noarch\
;intel-mkl-tbb__x86_64\
;intel-mkl-tbb-rt__x86_64\
;intel-mkl-gnu-c__x86_64\
;intel-mkl-common-f__noarch\
;intel-mkl-core-f__x86_64\
;intel-mkl-cluster-f__noarch\
;intel-mkl-gnu-f-rt__x86_64\
;intel-mkl-gnu-f__x86_64\
;intel-mkl-f95-common__noarch\
;intel-mkl-f__x86_64\
;intel-mkl-psxe__noarch\
;intel-psxe-common__noarch\
;intel-compxe-pset" >> $INTEL_CONFIGURATION

RUN cd $SOURCE_DIR && wget http://registrationcenter-download.intel.com/akdlm/irc_nas/tec/$INTEL_MKL_SEED/$INTEL_MKL.tgz \
 && tar -xvf $SOURCE_DIR/$INTEL_MKL.tgz -C $INTEL_PREFIX --strip-components=1 \
 && $INTEL_PREFIX/install.sh --silent $INTEL_CONFIGURATION

# PATH updated to inlude openmpi binaries needed to install mpi4py
ENV PATH "/usr/lib64/openmpi/bin:$PATH"

##
# Final clean-up
RUN rm -rf $SOURCE_DIR
RUN rm -rf $BUILD_DIR
