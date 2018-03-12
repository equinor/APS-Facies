#  Description:
#    This script compiles the c/c++ functions and classes that are used to draw 2D gaussian fields
#    draw2DGaussField.C implements a function that is called in the python ctype script
#    simGauss2D.C implements the 2D simulation class and is called from draw2DGaussField
#    The other files contain functions used by simGauss2D such as variogram in vario2D
#    About variogram specification: The input angle for anisotropy is measured anti-clockwise from x-axis
#    The anisotrpy direction define the direction for main range  (range1) while range2 is in the orthogonal direction
OS := $(shell uname)

COMMON_ARGS := -shared -lc
ifeq ($(OS),Darwin)
COMPILE_ARGS := $(COMMON_ARGS)
else
COMPILE_ARGS := $(COMMON_ARGS) -Wl,-soname,libdraw2D.so.1
endif

LIBRARY_NAME := libdraw2D.so

CC ?= gcc
CXX ?= g++
OPTIMIZE := -O3
DEBUG := -g

CODE_DIR ?= $(shell pwd)

ARGS := -fPIC $(OPTIMIZE) -c -Wall

.PHONY: *.o

simGauss2D.o:
	$(CXX) $(ARGS) -I. -I.. $(CODE_DIR)/simGauss2D.cpp

vario2D.o:
	$(CXX) $(ARGS) $(CODE_DIR)/vario2D.cpp

randomFuncs.o:
	$(CXX) $(ARGS) $(CODE_DIR)/randomFuncs.cpp

linearsolver.o:
	$(CXX) $(ARGS) $(CODE_DIR)/linearsolver.cpp

message.o:
	$(CXX) $(ARGS) $(CODE_DIR)/message.cpp

lib_matr.o:
	$(CC) $(ARGS) $(CODE_DIR)/lib_matr.c

lib_ran.o:
	$(CC) $(ARGS) $(CODE_DIR)/lib_ran.c

lib_message.o:
	$(CC) $(ARGS) $(CODE_DIR)/lib_message.c

utl_malloc.o:
	$(CC) $(ARGS) $(CODE_DIR)/utl_malloc.c

draw2DGaussField.o:
	$(CXX) $(ARGS) $(CODE_DIR)/draw2DGaussField.cpp


build: simGauss2D.o vario2D.o randomFuncs.o linearsolver.o message.o lib_matr.o lib_ran.o lib_message.o utl_malloc.o draw2DGaussField.o
	$(CXX) $(COMPILE_ARGS) -o $(LIBRARY_NAME) draw2DGaussField.o simGauss2D.o vario2D.o randomFuncs.o linearsolver.o message.o lib_matr.o lib_ran.o lib_message.o utl_malloc.o

clean:
	rm -f $(CODE_DIR)/*.o

clean-all: clean
	rm -f $(LIBRARY_NAME)