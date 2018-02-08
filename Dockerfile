FROM centos:6
LABEL version="2.0.0" \
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
ENV STATOIL_CERT="statoil-ca-certificates-1.0-5.noarch.rpm"
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

# Python dependencies
ENV OPENSSL_VERSION="1.1.0f"
ENV NCURSES_VERSION="6.0"
ENV READLINE_VERSION="7.0"
ENV SQLITE3_VERSION=3200100

# PyLint
ENV ASTROID_VERSION="1.5.3"
ENV ISORT_VERSION="4.2.15"
ENV PYLINT_VERSION="1.7.4"

ENV OPENSSL_PREFIX=$INSTALL_DIR/openssl-$OPENSSL_VERSION

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
RUN mkdir -p $ROOT_DIR \
             $BUILD_DIR \
             $SOURCE_DIR \
             $INSTALL_DIR \
             $PYTHON_PREFIX

RUN cd $SOURCE_DIR && wget https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tar.xz
RUN cd $SOURCE_DIR && wget https://www.openssl.org/source/openssl-"$OPENSSL_VERSION".tar.gz
RUN cd $SOURCE_DIR && wget http://ftp.gnu.org/pub/gnu/ncurses/ncurses-$NCURSES_VERSION.tar.gz
RUN cd $SOURCE_DIR && wget https://ftp.gnu.org/gnu/readline/readline-$READLINE_VERSION.tar.gz
RUN cd $SOURCE_DIR && wget https://sqlite.org/2017/sqlite-autoconf-$SQLITE3_VERSION.tar.gz
RUN cd $SOURCE_DIR && wget https://github.com/PyCQA/astroid/archive/astroid-$ASTROID_VERSION.tar.gz
RUN cd $SOURCE_DIR && wget https://github.com/timothycrosley/isort/archive/$ISORT_VERSION.tar.gz --output-document=$SOURCE_DIR/isort-$ISORT_VERSION.tar.gz
RUN cd $SOURCE_DIR && wget https://github.com/PyCQA/pylint/archive/pylint-$PYLINT_VERSION.tar.gz


 # Create all build directories
RUN cd $BUILD_DIR \
 && mkdir -p \
    python$PYTHON_VERSION \
    openssl-$OPENSSL_VERSION \
    ncurses-$NCURSES_VERSION \
    readline-$READLINE_VERSION \
    sqlite3-$SQLITE3_VERSION \
    astroid-$ASTROID_VERSION \
    isort-$ISORT_VERSION \
    pylint-$PYLINT_VERSION \

# Extract everything into build directories
RUN cd $BUILD_DIR \
 && tar -xvf  $SOURCE_DIR/Python-$PYTHON_VERSION.tar.xz -C python$PYTHON_VERSION --strip-components=1 \
 && tar -xvf  $SOURCE_DIR/openssl-"$OPENSSL_VERSION".tar.gz -C openssl-$OPENSSL_VERSION --strip-components=1 \
 && tar -xvf  $SOURCE_DIR/ncurses-$NCURSES_VERSION.tar.gz -C ncurses-$NCURSES_VERSION --strip-components=1 \
 && tar -xvf  $SOURCE_DIR/readline-$READLINE_VERSION.tar.gz -C readline-$READLINE_VERSION --strip-components=1 \
 && tar -xvf  $SOURCE_DIR/sqlite-autoconf-$SQLITE3_VERSION.tar.gz -C sqlite3-$SQLITE3_VERSION --strip-components=1 \
 && tar -xvf  $SOURCE_DIR/astroid-$ASTROID_VERSION.tar.gz -C astroid-$ASTROID_VERSION --strip-components=1 \
 && tar -xvf  $SOURCE_DIR/isort-$ISORT_VERSION.tar.gz -C isort-$ISORT_VERSION --strip-components=1 \
 && tar -xvf  $SOURCE_DIR/pylint-$PYLINT_VERSION.tar.gz -C pylint-$PYLINT_VERSION --strip-components=1

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

#################################
#                               #
# Make prerequisites for Python #
#                               #
#################################

# All of the following envs might not be necessary
# espescially C_INCLUDE_PATH, CPLUS_INCLUDE_PATH, LIBRARY_PATH and LD_RUN_PATH
ENV LD_LIBRARY_PATH "$PYTHON_PREFIX/lib:$LD_LIBRARY_PATH"
ENV PATH "$PYTHON_PREFIX/bin:$PATH"
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
    CPPFLAGS="-I$PYTHON_PREFIX/include/ncurses -I$PYTHON_PREFIX/include/readline -I$OPENSSL_PREFIX/include/openssl" \
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

# Install all python modules
COPY requirements.txt /requirements.txt
RUN $PIP install -r /requirements.txt \
 && rm -f /requirements.txt
