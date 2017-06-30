#!/usr/bin/env sh
echo "Description: This script compiles the c/c++ functions and classes that are used to draw 2D gaussian fields"
echo "             draw2DGaussField.C implements a function that is called in the python ctype script"
echo "             simGauss2D.C implements the 2D simulation class and is called from draw2DGaussField"
echo "             The other files contain functions used by simGauss2D such as variogram in vario2D "
echo "             About variogram specification: The input angle for anisotropy is measured anti-clockwise from x-axis"
echo "             The anisotrpy direction define the direction for main range  (range1) while range2 is in the ortogonal direction"

PREFIX="libgaussField"

g++ -fPIC -g -c -Wall -I. -I.. "${PREFIX}/simGauss2D.cpp"
g++ -fPIC -g -c -Wall "${PREFIX}/vario2D.cpp"
g++ -fPIC -g -c -Wall "${PREFIX}/randomFuncs.cpp"
g++ -fPIC -g -c -Wall "${PREFIX}/linearsolver.cpp"
g++ -fPIC -g -c -Wall "${PREFIX}/message.cpp"
gcc -fPIC -g -c -Wall "${PREFIX}/lib_matr.c"
gcc -fPIC -g -c -Wall "${PREFIX}/lib_ran.c"
gcc -fPIC -g -c -Wall "${PREFIX}/lib_message.c"
gcc -fPIC -g -c -Wall "${PREFIX}/utl_malloc.c"
g++ -fPIC -g -c -Wall "${PREFIX}/draw2DGaussField.cpp"

g++ -shared -Wl,-soname,libdraw2D.so.1 -o ../pythonscript/development/libdraw2D.so.1.0 draw2DGaussField.o simGauss2D.o vario2D.o randomFuncs.o linearsolver.o message.o lib_matr.o lib_ran.o lib_message.o utl_malloc.o -lc
