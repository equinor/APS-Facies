#!/usr/bin/env bash
if [[ "$1" == "--no-optimizations" ]]; then
  args=""
elif [[ "$1" == "-O" ]]; then
  args="-O"
elif [[ "$1" == "-O2" ]]; then
  args="-O2"
elif [[ "$1" == "-O3" || "$1" == "--optimize" ]]; then
  args="-O3"
elif [[ "$1" == "-g" || "$1" == "--debug" ]]; then
  args="-g"
elif [[ "$1" == "--description" ]]; then
  echo "Description: "
  echo "    This script compiles the c/c++ functions and classes that are used to draw 2D gaussian fields"
  echo "    draw2DGaussField.C implements a function that is called in the python ctype script"
  echo "    simGauss2D.C implements the 2D simulation class and is called from draw2DGaussField"
  echo "    The other files contain functions used by simGauss2D such as variogram in vario2D "
  echo "    About variogram specification: The input angle for anisotropy is measured anti-clockwise from x-axis"
  echo "    The anisotrpy direction define the direction for main range  (range1) while range2 is in the orthogonal direction"
  exit 0
else
  echo "Usage: buildSharedlib.sh --no-optimizations: Does not use any optimizations"
  echo "                         -O:  Optimizes the compiled library"
  echo "                         -O2: More optimizations. Takes longer to compile"
  echo "                         -O3: Even more optimizations"
  echo "                         --optimize: Same as -O3"
  echo "                         -g:  Enables debug symbols"
  echo "                         --debug: Same as -g"
  echo "                         --description: Shows a description of this library"
  exit 0
fi

LIB="$(pwd)"
PREFIX="${LIB}/libgaussField"
LIBRARY_NAME="libdraw2D.so"

if [[ -f ${LIB}/${LIBRARY_NAME} ]]; then
    echo "${LIBRARY_NAME} has already been compiled."
    exit 0
fi

mkdir -p "${PREFIX}/"build
cd "${PREFIX}/"build

g++ -fPIC $args -c -Wall -I. -I.. "${PREFIX}/simGauss2D.cpp"
g++ -fPIC $args -c -Wall "${PREFIX}/vario2D.cpp"
g++ -fPIC $args -c -Wall "${PREFIX}/randomFuncs.cpp"
g++ -fPIC $args -c -Wall "${PREFIX}/linearsolver.cpp"
g++ -fPIC $args -c -Wall "${PREFIX}/message.cpp"
gcc -fPIC $args -c -Wall "${PREFIX}/lib_matr.c"
gcc -fPIC $args -c -Wall "${PREFIX}/lib_ran.c"
gcc -fPIC $args -c -Wall "${PREFIX}/lib_message.c"
gcc -fPIC $args -c -Wall "${PREFIX}/utl_malloc.c"
g++ -fPIC $args -c -Wall "${PREFIX}/draw2DGaussField.cpp"

g++ -shared -Wl,-soname,libdraw2D.so.1 -o "${LIBRARY_NAME}" draw2DGaussField.o simGauss2D.o vario2D.o randomFuncs.o linearsolver.o message.o lib_matr.o lib_ran.o lib_message.o utl_malloc.o -lc

mv "${PREFIX}/build/${LIBRARY_NAME}" ${LIB}
echo "The shared library 'libdraw2D.so' is created"
