FROM git.equinor.com:4567/sdp/sdpsoft/centos:6
LABEL version="3.3.1" \
      maintainer="snis@equinor.com" \
      description="This is the Docker image for building, and testing the APS-GUI." \
      "com.statoil.vendor"="Equinor ASA"

# Versions
ENV RMS_VERSION=11.0.1 \
    PYTHON_VERSION=3.6 \
    TCL_VERSION=8.6 \
    INTEL_MKL_VERSION=2018.3.222 \
    INTEL_MKL_SEED=13005 \
    NODE_VERSION=8.12.0 \
    NRLIB_VERSION=1.1-r7 \
    YARN_VERSION=1.9.4
ENV TK_VERSION=${TCL_VERSION}

# Auxillary (version) information
ENV NODE_ARCH='x64' \
    INTEL_MKL="l_mkl_${INTEL_MKL_VERSION}" \
    RMS_LINUX="LINUX_64" \
    RMS_LINUX_LONG="linux-amd64-gcc_4_4-release/" \
    CA_FILE="/etc/ssl/certs/ca-bundle.crt"

# Prefixes
ENV RMS_PREFIX="/prog/roxar/rms/versions/${RMS_VERSION}" \
    DEPENDENCIES_PREFIX="/dependencies" \
    INTEL_PREFIX="${SOURCE_DIR}/${INTEL_MKL}" \
    INTEL_MKL_PREFIX="/opt/intel" \
    NODE_PREFIX="${INSTALL_DIR}/node-${NODE_VERSION}"
ENV RMS_BIN_PREFIX="${RMS_PREFIX}/bin/${RMS_LINUX}" \
    ROXAR_RMS_ROOT="${RMS_PREFIX}/${RMS_LINUX_LONG}"\
    RMS_LIB_PREFIX="${RMS_PREFIX}/lib/${RMS_LINUX}"
ENV PYTHON_LIB_PREFIX=$RMS_LIB_PREFIX/python$PYTHON_VERSION \
    PYTHONUSERBASE="/root/.roxar/rms-11/python" \
    PYTHONPATH=$DEPENDENCIES_PREFIX \
    MKL_ROOT="${INTEL_MKL_PREFIX}/mkl" \
    INTEL_CONFIGURATION="${INTEL_PREFIX}/config.txt"

# RMS License
ENV LM_LICENSE_FILE="/prog/roxar/licensing/geomaticLM.lic"

# Paths for executables, and libraries

ENV PATH="\
/root/.local/bin:\
/global/distbin:\
${NODE_PREFIX}/bin:\
${ROXAR_RMS_ROOT}/bin:\
${RMS_BIN_PREFIX}:\
${PYTHONUSERBASE}/bin:\
${PATH}" \
    LD_LIBRARY_PATH="\
${ROXAR_RMS_ROOT}/lib:\
${ROXAR_RMS_ROOT}/bin:\
${RMS_LIB_PREFIX}:\
${PYTHON_LIB_PREFIX}:\
${LD_LIBRARY_PATH}"

# All of the following envs might not be necessary
# espescially C_INCLUDE_PATH, CPLUS_INCLUDE_PATH, LIBRARY_PATH and LD_RUN_PATH
ENV LIBRARY_PATH="${LD_LIBRARY_PATH}" \
    LDFLAGS="-L${ROXAR_RMS_ROOT}/lib" \
    TCL_LIBRARY="${ROXAR_RMS_ROOT}/lib/tcl${TCL_VERSION}"\
    TK_LIBRARY="${ROXAR_RMS_ROOT}/lib/tk${TK_VERSION}" \
    LD_RUN_PATH="${LD_LIBRARY_PATH}"

# Variables for programs
ENV PYTHON="$RMS_BIN_PREFIX/python" \
    RMS="rms -v ${RMS_VERSION}"\
    NODE="$NODE_PREFIX/bin/node" \
    NPM="$NODE_PREFIX/bin/npm" \
    NPX="$NODE_PREFIX/bin/npx" \
    YARN="$NODE_PREFIX/bin/yarn"
ENV PIP="$PYTHON -m pip --proxy $HTTP_PROXY --cert ${CA_FILE}" \
    REQUESTS_CA_BUNDLE="${CA_FILE}" \
    SSL_CERT_FILE="${CA_FILE}"

# Add external resources
ADD .rms/bundle.rms-${RMS_VERSION}.tar.gz /
ADD .rms/APS-workflows.rms11.tar.gz /

# Misc. software
RUN yum update -y \
 # Install typical build packages
 && yum groupinstall -y "Development Tools" \
 && yum install -y \
    git \
    graphviz \
    # Install software needed during build of python and pip install
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
    mesa-libGL-devel \
    # RMS dependencies
    mesa-libEGL \
    mesa-libGLU \
    libXi \
    libSM \
    libXrender \
    libXrandr \
    libXcomposite \
    libXcursor \
    libXt \
    libXtst \
    libXScrnSaver \
    glibc.i686 \
    fontconfig \
    alsa-lib \
    libgomp \
 && yum clean all \
    # Get GPG keys
 && for key in \
      # NodeJS
      # gpg keys listed at https://github.com/nodejs/node#release-team
      94AE36675C464D64BAFA68DD7434390BDBE9B9C5 \
      FD3A5288F042B6850C66B31F09FE44734EB7990E \
      71DCFD284A79C3B38668286BC97EC7A07EDE3FC1 \
      DD8F2338BAE7501E3DD5AC78C273792F7D83545D \
      C4F0DFFF4E8C1A8236409D08E73BC641CC11F4C8 \
      B9AE9905FFD7803F25714661B63B535A4C206CA9 \
      56730D5401028683275BD23C23EFEFE93C4CFFFE \
      77984A986EBC2AA786BC0F66B01FBB92821C587A \
      # Yarn
      6A010C5166006599AA17F08146C2130DFD2497F5 \
    ; do \
      gpg --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys "$key" || \
      gpg --keyserver hkp://ipv4.pool.sks-keyservers.net --recv-keys "$key" || \
      gpg --keyserver hkp://pgp.mit.edu:80 --recv-keys "$key" ; \
    done \
    # Precreate all directories to avoid conflicts
 && mkdir -p $ROOT_DIR \
             $BUILD_DIR \
             $SOURCE_DIR \
             $NODE_PREFIX \
             $INSTALL_DIR \
             $DEPENDENCIES_PREFIX \
             $NRLIB_PREFIX \
             $INTEL_PREFIX \
 && cd ${SOURCE_DIR} \
    # Intel MKL
 && wget http://registrationcenter-download.intel.com/akdlm/irc_nas/tec/${INTEL_MKL_SEED}/${INTEL_MKL}.tgz \
    # Node JS
 && wget https://nodejs.org/dist/v${NODE_VERSION}/node-v${NODE_VERSION}-linux-${NODE_ARCH}.tar.xz \
    # Yarn
 && wget https://yarnpkg.com/downloads/${YARN_VERSION}/yarn-v${YARN_VERSION}.tar.gz \
    # NRlib
 && wget https://git.equinor.com/sdp/nrlib/repository/v${NRLIB_VERSION}/archive.tar.gz --output-document=${SOURCE_DIR}/nrlib-${NRLIB_VERSION}.tar.gz \
    ## Verify Downloads
    # Node JS
 && wget https://nodejs.org/dist/v${NODE_VERSION}/SHASUMS256.txt.asc --output-document=${SOURCE_DIR}/NODE_SHASUMS256.txt.asc \
 && gpg --batch --decrypt --output NODE_SHASUMS256.txt NODE_SHASUMS256.txt.asc \
 && grep " node-v${NODE_VERSION}-linux-${NODE_ARCH}.tar.xz\$" NODE_SHASUMS256.txt | sha256sum -c - \
    # Yarn
 && wget https://yarnpkg.com/downloads/${YARN_VERSION}/yarn-v${YARN_VERSION}.tar.gz.asc \
 && gpg --batch --verify yarn-v${YARN_VERSION}.tar.gz.asc yarn-v${YARN_VERSION}.tar.gz \
    # Create all build directories
 && cd ${BUILD_DIR} \
 && mkdir -p \
    nrlib-${NRLIB_VERSION} \
    # Extract all downloaded archives
 && tar -xvf  ${SOURCE_DIR}/${INTEL_MKL}.tgz -C ${INTEL_PREFIX} --strip-components=1 \
 && tar -xJf  ${SOURCE_DIR}/node-v${NODE_VERSION}-linux-${NODE_ARCH}.tar.xz -C ${NODE_PREFIX} --strip-components=1 --no-same-owner \
 && tar -xzf  ${SOURCE_DIR}/yarn-v${YARN_VERSION}.tar.gz -C ${NODE_PREFIX} --strip-components=1 \
 && tar -xvf  ${SOURCE_DIR}/nrlib-${NRLIB_VERSION}.tar.gz -C nrlib-${NRLIB_VERSION} --strip-components=1 \
 # Remove downloaded archives
 && rm -f ${SOURCE_DIR}/*.txt* \
 && rm -f ${SOURCE_DIR}/*.tar.* \
    # Install MKL (prerequisite for nrlib)
    # Configure setup
 && echo ACCEPT_EULA=accept                     >> $INTEL_CONFIGURATION \
 && echo PSET_INSTALL_DIR=${INTEL_MKL_PREFIX}   >> $INTEL_CONFIGURATION \
 && echo PSET_MODE=install                      >> $INTEL_CONFIGURATION \
 && echo SIGNING_ENABLED=yes                    >> $INTEL_CONFIGURATION \
 && echo ARCH_SELECTED=INTEL64                  >> $INTEL_CONFIGURATION \
 && echo COMPONENTS="\
;intel-comp-l-all-vars__noarch\
;intel-comp-nomcu-vars__noarch\
;intel-mkl-common__noarch\
;intel-mkl-installer-license__noarch\
;intel-mkl-core__x86_64\
;intel-mkl-core-rt__x86_64\
;intel-mkl-gnu__x86_64\
;intel-mkl-gnu-rt__x86_64\
;intel-mkl-common-ps__noarch\
;intel-mkl-core-ps__x86_64\
;intel-mkl-common-c__noarch\
;intel-mkl-core-c__x86_64\
;intel-mkl-common-c-ps__noarch\
;intel-mkl-gnu-c__x86_64\
;intel-mkl-common-f__noarch\
;intel-mkl-core-f__x86_64\
;intel-mkl-gnu-f-rt__x86_64\
;intel-mkl-gnu-f__x86_64\
;intel-mkl-f95-common__noarch\
;intel-mkl-f__x86_64\
;intel-mkl-psxe__noarch\
;intel-psxe-common__noarch\
;intel-compxe-pset\
"                                               >> $INTEL_CONFIGURATION \
 && $INTEL_PREFIX/install.sh --silent $INTEL_CONFIGURATION \
    ###################
    #                 #
    # Python packages #
    #                 #
    ###################
    # Install pipenv
 && $PIP install --user pipenv \
    # FIXME: Backup distutils/__init__.py, as the compilation of nrlib changes it for some reason
  && cp "/prog/roxar/rms/versions/${RMS_VERSION}/linux-amd64-gcc_4_4-release/lib/python${PYTHON_VERSION}/distutils/__init__.py" /distutils.py.bak \
    # Install NRlib to dependencies collection
 && cd ${BUILD_DIR}/nrlib-${NRLIB_VERSION} \
 && MKLROOT=/opt/intel/mkl \
    USE_SITE_PACKAGES=yes \
    make build \
         tests \
 && mv nrlib.*.so $DEPENDENCIES_PREFIX \
 # FIXME: Restore distutils from backup
 && cp -f /distutils.py.bak "/prog/roxar/rms/versions/${RMS_VERSION}/linux-amd64-gcc_4_4-release/lib/python${PYTHON_VERSION}/distutils/__init__.py" \
    ##
    # Final clean-up
 && rm -rf $SOURCE_DIR \
           $BUILD_DIR \
           $INTEL_MKL_PREFIX \
           /root/anaconda-ks.cfg \
           /root/*.log* \
           /root/.virtualenvs \
           /root/.local \
           /root/.cache \
           $(find $NODE_PREFIX -name *.cmd) \
           $NODE_PREFIX/CHANGELOG.md \
           $NODE_PREFIX/LICENSE \
           $NODE_PREFIX/README.md \
           $NODE_PREFIX/package.json
