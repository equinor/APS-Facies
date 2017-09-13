#!/bin/env python
# Python3  test preliminary preview 
import sys

import importlib
import matplotlib
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Polygon

# Base class for Trunc2D_Cubic
from src import (
    APSDataFromRMS, APSGaussFieldJobs, APSMainFaciesTable, APSModel, APSZoneModel, Trend3D_linear_model_xml,
    Trunc2D_Cubic_xml, Trunc3D_bayfill_xml, simGauss2D
)

# To be phases out and Trunc2D_Cubic is replacing it
# import scipy.ndimage

importlib.reload(APSModel)
importlib.reload(APSZoneModel)
importlib.reload(APSMainFaciesTable)
importlib.reload(APSGaussFieldJobs)
importlib.reload(APSDataFromRMS)

importlib.reload(simGauss2D)
importlib.reload(Trunc2D_Cubic_xml)
importlib.reload(Trunc3D_bayfill_xml)
importlib.reload(Trend3D_linear_model_xml)


def defineColors(nFacies):
    # --- Colormaps from a list ---
    if nFacies == 2:
        colors = ['lawngreen', 'grey']
    elif nFacies == 3:
        colors = ['lawngreen', 'grey', 'dodgerblue']
    elif nFacies == 4:
        colors = ['lawngreen', 'grey', 'dodgerblue', 'gold']
    elif nFacies == 5:
        colors = ['lawngreen', 'grey', 'dodgerblue', 'gold', 'darkorchid']
    elif nFacies == 6:
        colors = ['lawngreen', 'grey', 'dodgerblue', 'gold', 'darkorchid', 'cyan']
    elif nFacies == 7:
        colors = ['lawngreen', 'grey', 'dodgerblue', 'gold', 'darkorchid', 'cyan', 'firebrick']
    elif nFacies == 8:
        colors = ['lawngreen', 'grey', 'dodgerblue', 'gold', 'darkorchid', 'cyan', 'firebrick', 'olivedrab']
    elif nFacies == 9:
        colors = ['lawngreen', 'grey', 'dodgerblue', 'gold', 'darkorchid', 'cyan', 'firebrick', 'olivedrab', 'blue']
    elif nFacies == 10:
        colors = ['lawngreen', 'grey', 'dodgerblue', 'gold', 'darkorchid', 'cyan', 'firebrick', 'olivedrab', 'blue',
                  'crimson']
    elif nFacies == 11:
        colors = ['lawngreen', 'grey', 'dodgerblue', 'gold', 'darkorchid', 'cyan', 'firebrick', 'olivedrab', 'blue',
                  'crimson', 'darkorange']
    elif nFacies == 12:
        colors = ['lawngreen', 'grey', 'dodgerblue', 'gold', 'darkorchid', 'cyan', 'firebrick', 'olivedrab', 'blue',
                  'crimson', 'darkorange', 'red']
    return colors


def writeFile(fileName, a, nx, ny):
    with open(fileName, 'w') as file:
        # Choose an arbitary heading
        outstring = '-996  ' + str(ny) + '  50.000000     50.000000\n'
        outstring = outstring + '637943.187500   678043.187500  4334008.000000  4375108.000000\n'
        outstring = outstring + ' ' + str(nx) + ' ' + ' 0.000000   637943.187500  4334008.000000\n'
        outstring = outstring + '0     0     0     0     0     0     0\n'

        count = 0
        text = ''
        print('len(a): ' + str(len(a)))
        for j in range(len(a)):
            text = text + str(a[j]) + '  '
            count += 1
            if count >= 5:
                text = text + '\n'
                outstring += text
                count = 0
                text = ''
        if count > 0:
            outstring += text + '\n'
        file.write(outstring)
    print('Write file: ' + fileName)
    return


def readFile(fileName):
    print('Read file: ' + fileName)
    with open(fileName, 'r') as file:
        inString = file.read()
        words = inString.split()
        n = len(words)
        print('Number of words: ' + str(n))

        ny = int(words[1])
        nx = int(words[8])
        print('nx,ny: ' + str(nx) + ' ' + str(ny))
        print('Number of values: ' + str(len(words) - 19))
        a = np.zeros(nx * ny, float)
        for i in range(19, len(words)):
            a[i - 19] = float(words[i])

    return [a, nx, ny]


# Initialise common variables
functionName = 'testPreview.py'
rotatePlot = 0
useBestResolution = 0
noSim = 0  # Is set to 1 only if one don't want to simulate 2D fields (for test purpose only)
setWrite = 1  # Is set to 1 if write out simulated 2D fields
# --------- Main test program ----------------
print('matplotlib version: ' + matplotlib.__version__)
print('Run: testPreview')
modelFileName = 'APS.xml'
inputRMSDataFileName = 'rms_project_data_for_APS_gui.xml'
nArgv = len(sys.argv)
modelName = ' '
if nArgv > 1:
    modelName = sys.argv[1]

print('- Read file: ' + modelFileName)
apsModel = APSModel.APSModel(modelFileName)
printInfo = apsModel.printInfo()
zoneParamName = apsModel.getZoneParamName()
mainFaciesTable = apsModel.getMainFaciesTable()

gridModelName = apsModel.getGridModelName()
previewZoneNumber = apsModel.getPreviewZoneNumber()

rmsData = APSDataFromRMS.APSDataFromRMS()
print('Read file: ' + inputRMSDataFileName)
rmsData.readRMSDataFromXMLFile(inputRMSDataFileName)
[nx, ny, x0, y0, previewDX, previewDY, xinc, yinc, previewTheta] = rmsData.getGridSize()

if useBestResolution:
    if nx < ny:
        nMin = nx
        nxPreview = nx
        # Use square pixels
        nyPreview = int(nxPreview * previewDY / previewDX)
    else:
        nMin = ny
        nyPreview = ny
        nxPreview = int(nyPreview * previewDX / previewDY)
else:
    if nx < ny:
        if ny > 600:
            nyPreview = 600
        else:
            nyPreview = ny
        nxPreview = int(nyPreview * previewDX / previewDY)
    else:
        if nx > 600:
            nxPreview = 600
        else:
            nyPreview = ny
        nyPreview = int(nxPreview * previewDY / previewDX)

print('nxPreview: ' + str(nxPreview))
print('nyPreview: ' + str(nyPreview))

# print('Theta: ' + str(180.0*theta/np.pi))
# print('CosTheta: ' + str(cosTheta))
# print('SinTheta: ' + str(sinTheta))
# print('LX: ' + str(DX))
# print('LY: ' + str(DY))


zoneNumber = previewZoneNumber
zoneModel = apsModel.getZoneModel(zoneNumber)
if zoneModel == None:
    print('Error: Zone number: ' + str(zoneNumber) + ' is not defined')
    sys.exit()
truncObject = zoneModel.getTruncRule()
faciesNames = zoneModel.getFaciesInZoneModel()
gaussFieldNames = zoneModel.getUsedGaussFieldNames()
nFacies = len(faciesNames)

nGaussFields = len(gaussFieldNames)
useConstProb = zoneModel.useConstProb()
cellNumber = 0
if useConstProb == 0:
    print('Error: Preview plots require constant facies probabilities')
    print('       Use arbitrary constant values')

faciesOrdering = truncObject.getFaciesOrderIndexList()

probParamNames = []
faciesProb = []
print(' ')
print(' ---------  Zone number : ' + str(zoneNumber) + ' -----------------')
for fName in faciesNames:
    pName = zoneModel.getProbParamName(fName)
    if useConstProb == 1:
        v = float(pName)
        p = int(v * 1000 + 0.5)
        w = float(p) / 1000.0
        print('Zone: ' + str(zoneNumber) + ' Facies: ' + fName + ' Prob: ' + str(w))
    else:
        v = 1.0 / float(len(faciesNames))
        p = int(v * 1000 + 0.5)
        w = float(p) / 1000.0
        print('Zone: ' + str(zoneNumber) + ' Facies: ' + fName + ' Prob: ' + str(w))
    faciesProb.append(v)

# Calculate truncation map for given facies probabilities
# print('Facies prob:')
# print(repr(faciesProb))
# truncObject.setTruncRule(faciesProb)

# Calculate polygons for truncation map for current facies probability
# as specified when calling setTruncRule(faciesProb)
# [faciesPolygons]    = truncObject.truncMapPolygons()
# faciesIndxPerPolygon = truncObject.faciesIndxPerPolygon()

# Write datastructure:
truncObject.writeContentsInDataStructure()

# print('FaciesIndexPerPolygon:')
# print(repr(faciesIndxPerPolygon))
# Simulate three 2D gaussian fields
gaussFieldParamNamesToSimulate = gaussFieldNames
nx = int(nxPreview)
ny = int(nyPreview)
gridXSize = previewDX
gridYSize = previewDY
gaussFields = []
if noSim == 1:
    if nGaussFields == 3:
        a1 = readFile('a1.dat')
        a2 = readFile('a2.dat')
        a3 = readFile('a3.dat')
else:
    gaussFields = zoneModel.simGaussFieldWithTrendAndTransform(nGaussFields, nx, ny,
                                                               gridXSize, gridYSize, previewTheta)
    if setWrite == 1:
        print('Write 2D simulated gauss fields: ')
        for n in range(nGaussFields):
            gf = gaussFields[n]
            fileName = 'a' + str(n + 1) + '.dat'
            writeFile(fileName, gf, nx, ny)

facies = np.zeros(nx * ny, int)
faciesFraction = np.zeros(nFacies, int)

gfRealization1 = gaussFields[0]
nGridCells = len(gfRealization1)
alphaCoord = np.zeros(nGaussFields, np.float32)
for i in range(nGridCells):
    truncObject.setTruncRule(faciesProb)
    for m in range(nGaussFields):
        alphaReal = gaussFields[m]
        alphaCoord[m] = alphaReal[i]
    [faciesCode, fIndx] = truncObject.defineFaciesByTruncRule(alphaCoord)

    facies[i] = fIndx + 1  # Use fIndx+1 as values in the facies plot
    faciesFraction[fIndx] += 1

writeFile('facies2D.dat', facies, nx, ny)
print(' ')
print('Facies name:   Simulated fractions:    Specified fractions:')
for i in range(nFacies):
    f = faciesFraction[i]
    fraction = float(f) / float(len(facies))
    print('{0:10}  {1:.3f}   {2:.3f}'.format(faciesNames[i], fraction, faciesProb[i]))
print(' ')

if truncObject.getClassName() == 'Trunc2D_Angle':
    nCalc = truncObject.getNCalcTruncMap()
    nLookup = truncObject.getNLookupTruncMap()
    print('Number of calculations of truncation map: ' + str(nCalc))
    print('Number of lookup of truncation map: ' + str(nLookup))

# Calculate polygons for truncation map for current facies probability
# as specified when calling setTruncRule(faciesProb)
[faciesPolygons] = truncObject.truncMapPolygons()
faciesIndxPerPolygon = truncObject.faciesIndxPerPolygon()

fmap = np.reshape(facies, (ny, nx))  # Reshape to a 2D array with c-index ordering
alphaMapList = []
for m in range(nGaussFields):
    alphaReal = gaussFields[m]
    alphaMap = np.reshape(alphaReal, (ny, nx))
    alphaMapList.append(alphaMap)

# Plot the result
print('Make plots')
fig = plt.figure(figsize=[25.0, 15.0])

# Figure containing the transformed Gaussian fields and facies realization

# figGauss,(ax1,ax2,ax3,ax4,ax5,ax6) = plt.subplots(1, 6,sharey=True)

# Gauss1 transformed is plotted
ax1 = plt.subplot(2, 6, 1)
alphaMap = alphaMapList[0]
if rotatePlot:
    rot_im1 = scipy.ndimage.interpolation.rotate(alphaMap, previewTheta)
else:
    rot_im1 = alphaMap
im1 = ax1.imshow(rot_im1, interpolation='none', aspect='equal', vmin=0.0, vmax=1.0, origin='lower')
ax1.set_title('GRF1')

# Gauss2 transformed is plotted
ax2 = plt.subplot(2, 6, 2)
alphaMap = alphaMapList[1]
if rotatePlot:
    rot_im2 = scipy.ndimage.interpolation.rotate(alphaMap, previewTheta)
else:
    rot_im2 = alphaMap
im2 = ax2.imshow(rot_im2, interpolation='none', vmin=0.0, vmax=1.0, origin='lower')
ax2.set_title('GRF2')
plt.setp(ax2.get_xticklabels(), visible=False)
plt.setp(ax2.get_yticklabels(), visible=False)

# Gauss3 transformed is plotted
ax3 = plt.subplot(2, 6, 3)
alphaReal = np.zeros(nx * ny, np.float32)
alphaMap = np.reshape(alphaReal, (ny, nx))
if nGaussFields >= 3:
    alphaMap = alphaMapList[2]
if rotatePlot:
    rot_im3 = scipy.ndimage.interpolation.rotate(alphaMap, previewTheta)
else:
    rot_im3 = alphaMap
im3 = ax3.imshow(rot_im3, interpolation='none', vmin=0.0, vmax=1.0, origin='lower')
ax3.set_title('GRF3')
plt.setp(ax3.get_xticklabels(), visible=False)
plt.setp(ax3.get_yticklabels(), visible=False)

# Gauss4 transformed is plotted
ax4 = plt.subplot(2, 6, 4)
alphaReal = np.zeros(nx * ny, np.float32)
alphaMap = np.reshape(alphaReal, (ny, nx))
if nGaussFields >= 4:
    alphaMap = alphaMapList[3]
if rotatePlot:
    rot_im4 = scipy.ndimage.interpolation.rotate(alphaMap, previewTheta)
else:
    rot_im4 = alphaMap
im4 = ax4.imshow(rot_im4, interpolation='none', vmin=0.0, vmax=1.0, origin='lower')
ax4.set_title('GRF4')
plt.setp(ax4.get_xticklabels(), visible=False)
plt.setp(ax4.get_yticklabels(), visible=False)

# Gauss5 transformed is plotted
ax5 = plt.subplot(2, 6, 5)
alphaReal = np.zeros(nx * ny, np.float32)
alphaMap = np.reshape(alphaReal, (ny, nx))
if nGaussFields >= 5:
    alphaMap = alphaMapList[4]
if rotatePlot:
    rot_im5 = scipy.ndimage.interpolation.rotate(alphaMap, previewTheta)
else:
    rot_im5 = alphaMap
im5 = ax5.imshow(rot_im5, interpolation='none', vmin=0.0, vmax=1.0, origin='lower')
ax5.set_title('GRF5')
plt.setp(ax5.get_xticklabels(), visible=False)
plt.setp(ax5.get_yticklabels(), visible=False)

# Gauss6 transformed is plotted
ax6 = plt.subplot(2, 6, 6)
alphaReal = np.zeros(nx * ny, np.float32)
alphaMap = np.reshape(alphaReal, (ny, nx))
if nGaussFields >= 6:
    alphaMap = alphaMapList[5]
if rotatePlot:
    rot_im6 = scipy.ndimage.interpolation.rotate(alphaMap, previewTheta)
else:
    rot_im6 = alphaMap
im6 = ax6.imshow(rot_im6, interpolation='none', vmin=0.0, vmax=1.0, origin='lower')
ax6.set_title('GRF6')
plt.setp(ax6.get_xticklabels(), visible=False)
plt.setp(ax6.get_yticklabels(), visible=False)

# Color legend for the transformed Gaussian fields
cax1 = fig.add_axes([0.94, 0.52, 0.02, 0.4])
fig.colorbar(im1, cax=cax1)

# Figure containing truncation map and facies

# Truncation map is plotted
axTrunc = plt.subplot(2, 6, 7)
colors = defineColors(nFacies)
cmap_name = 'Colormap'

# Create the colormap
cm = matplotlib.colors.ListedColormap(colors, name=cmap_name, N=nFacies)
bounds = np.linspace(0.5, 0.5 + nFacies, nFacies + 1)
ticks = bounds
labels = faciesNames
colorNumberPerPolygon = []
patches = []
print('Number of facies:          ' + str(nFacies))
print('Number of facies polygons: ' + str(len(faciesPolygons)))
maxfIndx = 0
colorForFacies = []
for i in range(len(faciesPolygons)):
    indx = faciesIndxPerPolygon[i]
    fIndx = faciesOrdering[indx]
    poly = faciesPolygons[i]
    polygon = Polygon(poly, closed=True, facecolor=colors[fIndx])
    axTrunc.add_patch(polygon)
    fName = faciesNames[fIndx]
# print('Polygon:{0:2d} Facies: {1:7}  Color: {2:12} Facies index(zone): {3:2d}'.format(i,fName,colors[fIndx],fIndx))
#    print('Polygon Points:')
#    print(repr(poly))
axTrunc.set_title('TruncMap')

# Facies map is plotted
axFacies = plt.subplot(2, 6, 8)
if rotatePlot:
    rot_imFac = scipy.ndimage.interpolation.rotate(fmap, previewTheta)
else:
    rot_imFac = fmap
imFac = axFacies.imshow(rot_imFac, interpolation='none', cmap=cm, clim=(1, nFacies), origin='lower')
axFacies.set_title('Facies')

# Plot crossplot between GRF1 and GRF2,3,4,5
if nGaussFields >= 2:
    # Cross plot between G1 and G2
    alphaReal1 = gaussFields[0]
    alphaReal2 = gaussFields[1]
    axC1 = plt.subplot(2, 6, 9)
    plt.scatter(alphaReal1, alphaReal2, alpha=0.15, marker='.', c='b')
    axC1.set_title('Crossplot GRF1 GRF2')
    plt.axis([0, 1, 0, 1])
if nGaussFields >= 3:
    # Cross plot between G1 and G3
    alphaReal1 = gaussFields[0]
    alphaReal3 = gaussFields[2]
    axC2 = plt.subplot(2, 6, 10)
    plt.scatter(alphaReal1, alphaReal3, alpha=0.15, marker='.', c='b')
    axC2.set_title('Crossplot GRF1 GRF3')
    plt.axis([0, 1, 0, 1])
    plt.setp(axC2.get_xticklabels(), visible=False)
    plt.setp(axC2.get_yticklabels(), visible=False)
if nGaussFields >= 4:
    # Cross plot between G1 and G4
    alphaReal1 = gaussFields[0]
    alphaReal4 = gaussFields[3]
    axC3 = plt.subplot(2, 6, 11)
    plt.scatter(alphaReal1, alphaReal4, alpha=0.15, marker='.', c='b')
    axC3.set_title('Crossplot GRF1 GRF4')
    plt.axis([0, 1, 0, 1])
    plt.setp(axC3.get_xticklabels(), visible=False)
    plt.setp(axC3.get_yticklabels(), visible=False)
if nGaussFields >= 5:
    # Cross plot between G1 and G5
    alphaReal1 = gaussFields[0]
    alphaReal5 = gaussFields[4]
    axC4 = plt.subplot(2, 6, 12)
    plt.scatter(alphaReal1, alphaReal5, alpha=0.15, marker='.', c='b')
    axC4.set_title('Crossplot GRF1 GRF5')
    plt.axis([0, 1, 0, 1])
    plt.setp(axC4.get_xticklabels(), visible=False)
    plt.setp(axC4.get_yticklabels(), visible=False)

# Color legend for the truncation map and facies plots
cax2 = fig.add_axes([0.94, 0.05, 0.02, 0.4])
fig.colorbar(imFac, cax=cax2, ticks=bounds + 0.5, boundaries=bounds, drawedges=True)
cax2.set_yticklabels(labels)

# Adjust subplots
plt.subplots_adjust(left=0.10, wspace=0.15, hspace=0.20,
                    bottom=0.05, top=0.92)
# Label the rows and columns of the table
if nArgv > 1:
    text = 'Model name: ' + modelName + '  Zone number: ' + str(zoneNumber)
else:
    text = 'Zone number: ' + str(zoneNumber)
fig.text(0.50, 0.98, text, ha='center')
for i in range(nFacies):
    p = int(faciesProb[i] * 1000 + 0.5)
    faciesProb[i] = float(p) / 1000.0
    text = faciesNames[i] + ':  ' + str(faciesProb[i])
    fig.text(0.02, 0.40 - 0.03 * i, text, ha='left')

plt.show()
print('Finished testPreview')
