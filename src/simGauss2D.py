#!/bin/env python
import ctypes as ct
import numpy as np

# Variogram type:
#    SPHERICAL      1
#    EXPONENTIAL    2
#    GAUSSIAN       3
#    GENERAL_EXPONENTIAL  4
# Input angle for variogram is asimuth angle in degrees
# Input angle for linear trend direction is asimuth angle in degrees
#
# -----       Functions used to draw gaussian fields: -------------------------

#Global object with c/c++ code for simulation of gaussian fields
_draw2DLib = ct.CDLL('./libdraw2D.so')

# Define input data types
_draw2DLib.draw2DGaussField.argtypes = (ct.c_int, ct.c_int, 
                                        ct.c_double, ct.c_double, 
                                        ct.c_int, ct.c_uint, 
                                        ct.c_double, ct.c_double,
                                        ct.c_double, ct.c_double,ct.c_int)
# Define output data type
floatArrayPointer = ct.POINTER(ct.c_float)
_draw2DLib.draw2DGaussField.restype = floatArrayPointer


# Function simulationg 2D gaussian field
def draw2D(nx,ny,xsize,ysize, variotype, iseed, range1, range2, angle, power,debugPrint):
    global _draw2DLib
    values = []  

    # Define the output variable to contain  nx*ny float values
    arrayPointer = floatArrayPointer*nx*ny

    # Call c/c++ function
    arrayPointer =  _draw2DLib.draw2DGaussField(ct.c_int(nx),ct.c_int(ny),
                                                ct.c_double(xsize), ct.c_double(ysize), 
                                                ct.c_int(variotype), ct.c_uint(iseed), 
                                                ct.c_double(range1), ct.c_double(range2),
                                                ct.c_double(angle), ct.c_double(power),ct.c_int(debugPrint))

    # Assign result to python array
    n=0
    for i in range(nx):
        for j in range(ny):
            v = float(arrayPointer[n])
            values.append(v)
            n = n+1
#            print( 'i,j,value: ' + '(' + str(i) +','+str(j) + '): ' + ' '  + str(values[n-1]))
    return [values]


def simGaussFieldAddTrendAndTransform(iseed,nx,ny,xsize,ysize,
                                      varioType1,range11,range21,varioAngle1,
                                      pow1,useTrend1,trendAsimuth1,relSigma1,printInfo):
    # Residual gaussian fields
    debugPrint = 0
    if printInfo >= 3:
        print( '    - Simulate  2D Gauss field using seed: ' + str(iseed))
        debugPrint = 1    
    # Variogram angle input should be asimuth angle in degrees, but angle in simulation algorithm should be
    # relative to first axis.
    varioAngle1 = 90.0 - varioAngle1
    [v1Residual] = draw2D(nx,ny,xsize,ysize, varioType1, iseed, range11, range21, varioAngle1, pow1,debugPrint)

    # Trends for gaussian fields
    Trend1 = np.zeros(nx*ny,float)
    sigma1 = 1.0
    if useTrend1:
        if printInfo >= 3:
            print( '    - Add trend 2D Gauss field ')
        dx = 1.0/float(nx-1)
        dy = 1.0/float(ny-1)
        ang1 = trendAsimuth1*np.pi/180.0
        sintheta = np.sin(ang1)
        costheta = np.cos(ang1)

        n= 0
        minV = 99999
        maxV = -99999
        for j in range(ny):
            y = float(j)*dy
            for i in range(nx):
                x = float(i)*dx
                x1 = x*sintheta + y*costheta
                Trend1[n] = x1 # Increasing from 0 to in x1 direction
                if x1 > maxV:
                    maxV = x1
                if x1 < minV:
                    minV = x1
                n = n+1

        sigma1 = relSigma1* (maxV-minV)
#        print( 'Sigma1: ' + str(sigma1))

    v1Trend = []
    for n in range(nx*ny):
        w = sigma1*v1Residual[n]
        v1Trend.append(w + Trend1[n])

    # Transform into uniform distribution
    if printInfo >= 3:
        print( '    - Transform 2D Gauss field')
        print( ' ')
    transformedValues = np.zeros(nx*ny,float)
    sort_indx = np.argsort(v1Trend)
    for i in range(len(v1Trend)):
        indx = sort_indx[i]
        u = float(i)/float(nx*ny) 
        transformedValues[indx] = u

    return [transformedValues]


def simGaussFieldAddTrendAndTransform2(iseed,nx,ny,xsize,ysize,
                                      varioType1,range11,range21,varioAngle1,
                                      pow1,useTrend1,trendAsimuth1,relSigma1):
    # Residual gaussian fields
    # Variogram angle input should be asimuth angle in degrees, but angle in simulation algorithm should be
    # relative to first axis.
    varioAngle1 = 90.0 - varioAngle1
    [v1Residual] = draw2D(nx,ny,xsize,ysize, varioType1, iseed, range11, range21, varioAngle1, pow1)

    # Trends for gaussian fields
    Trend1 = np.zeros(nx*ny,float)
    sigma1 = 1.0
    if useTrend1:
        print( '    - Calculate trend for Gauss field')
        dx = 1.0/float(nx-1)
        dy = 1.0/float(ny-1)
        ang1 = trendAsimuth1*np.pi/180.0
        sintheta = np.sin(ang1)
        costheta = np.cos(ang1)

        n= 0
        minV = 99999
        maxV = -99999
        for j in range(ny):
            y = float(j)*dy
            for i in range(nx):
                x = float(i)*dx
                x1 = x*sintheta + y*costheta
                Trend1[n] = x1 # Increasing from 0 to in x1 direction
                if x1 > maxV:
                    maxV = x1
                if x1 < minV:
                    minV = x1
                n = n+1

        sigma1 = relSigma1* (maxV-minV)
#        print( 'Sigma1: ' + str(sigma1))

    v1             = np.zeros(nx*ny,float)
    v1WithTrend    = np.zeros(nx*ny,float)
    cumulativeX    = np.zeros(nx*ny,float)
    cumulativeY    = np.zeros(nx*ny,float)
    for n in range(nx*ny):
        w = sigma1*v1Residual[n]
        v1WithTrend[n] = w + Trend1[n]
        v1[n] = w

    # Transform into uniform distribution
    print( '    - Transform Gauss field')
    print( ' ')
    transformedValues = np.zeros(nx*ny,float)
    sort_indx = np.argsort(v1WithTrend)
    for i in range(len(v1)):
        indx = sort_indx[i]
        u = float(i)/float(nx*ny) 
        transformedValues[indx] = u
        cumulativeX[i] = v1WithTrend[indx]
        cumulativeY[i] = u

    return [v1,v1WithTrend,transformedValues,cumulativeX,cumulativeY]

# ------------  End of functions to draw gaussian fields -----------------------------------
