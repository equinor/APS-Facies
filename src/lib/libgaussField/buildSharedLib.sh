#/bin/tcsh
echo "Description: This script compiles the c/c++ functions and classes that are used to draw 2D gaussian fields"
echo "             draw2DGaussField.C implements a function that is called in the python ctype script"
echo "             simGauss2D.C implements the 2D simulation class and is called from draw2DGaussField"
echo "             The other files contain functions used by simGauss2D such as variogram in vario2D "
echo "             About variogram specification: The input angle for anisotropy is measured anti-clockwise from x-axis"
echo "             The anisotrpy direction define the direction for main range  (range1) while range2 is in the ortogonal direction"
echo "Optimalization: Run the script with one argument: O or Optimize"

if ($1 == "O" ||  $1 == "Optimize") then
      echo "Compile with optimalization option"
      g++ -fPIC -O -c -Wall -I. simGauss2D.C
      g++ -fPIC -O -c -Wall -I. vario2D.C
      g++ -fPIC -O -c -Wall -I. randomFuncs.C
      g++ -fPIC -O -c -Wall -I. linearsolver.C
      g++ -fPIC -O -c -Wall -I. message.C
      gcc -fPIC -O -c -Wall -I. lib_matr.c
      gcc -fPIC -O -c -Wall -I. lib_ran.c
      gcc -fPIC -O -c -Wall -I. lib_message.c
      gcc -fPIC -O -c -Wall -I. utl_malloc.c
      g++ -fPIC -O -c -Wall -I. draw2DGaussField.C
else
      echo "Compile with debug option"
      g++ -fPIC -g -c -Wall -I. simGauss2D.C
      g++ -fPIC -g -c -Wall -I. vario2D.C
      g++ -fPIC -g -c -Wall -I. randomFuncs.C
      g++ -fPIC -g -c -Wall -I. linearsolver.C
      g++ -fPIC -g -c -Wall -I. message.C
      gcc -fPIC -g -c -Wall -I. lib_matr.c
      gcc -fPIC -g -c -Wall -I. lib_ran.c
      gcc -fPIC -g -c -Wall -I. lib_message.c
      gcc -fPIC -g -c -Wall -I. utl_malloc.c
      g++ -fPIC -g -c -Wall -I. draw2DGaussField.C
endif

g++ -shared -Wl,-soname,libdraw2D.so -o libdraw2D.so draw2DGaussField.o simGauss2D.o vario2D.o randomFuncs.o linearsolver.o message.o lib_matr.o lib_ran.o lib_message.o utl_malloc.o -lc
mv libdraw2D.so ../.
echo "  "
echo "Shared library libdraw2D.so is created"


