#/bin/tcsh
echo "Description: This script compiles the c/c++ functions and classes that are used to draw 2D gaussian fields"
echo "             draw2DGaussField.C implements a function that is called in the python ctype script"
echo "             simGauss2D.C implements the 2D simulation class and is called from draw2DGaussField"
echo "             The other files contain functions used by simGauss2D such as variogram in vario2D "
echo "             About variogram specification: The input angle for anisotropy is measured anti-clockwise from x-axis"
echo "             The anisotrpy direction define the direction for main range  (range1) while range2 is in the ortogonal direction"
cd ../../libgaussField
g++ -fPIC -g -c -Wall -I. -I.. simGauss2D.C
g++ -fPIC -g -c -Wall vario2D.C
g++ -fPIC -g -c -Wall randomFuncs.C
g++ -fPIC -g -c -Wall linearsolver.C
g++ -fPIC -g -c -Wall message.C
gcc -fPIC -g -c -Wall lib_matr.c
gcc -fPIC -g -c -Wall lib_ran.c
gcc -fPIC -g -c -Wall lib_message.c
gcc -fPIC -g -c -Wall utl_malloc.c
g++ -fPIC -g -c -Wall draw2DGaussField.C

g++ -shared -Wl,-soname,libdraw2D.so.1 -o ../pythonscript/development/libdraw2D.so.1.0 draw2DGaussField.o simGauss2D.o vario2D.o randomFuncs.o linearsolver.o message.o lib_matr.o lib_ran.o lib_message.o utl_malloc.o -lc
