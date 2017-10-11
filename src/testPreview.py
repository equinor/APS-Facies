#!/bin/env python
# Python3  test preliminary preview 
import sys

import importlib
import matplotlib
import numpy as np
import scipy
from matplotlib import pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Polygon

from src import (
    APSDataFromRMS, APSGaussFieldJobs, APSMainFaciesTable, APSModel, APSZoneModel, APSFaciesProb, APSGaussModel,
    Trend3D_linear_model_xml, Trunc2D_Angle_xml, Trunc2D_Cubic_xml, Trunc3D_bayfill_xml, simGauss2D
)
from src.utils.methods import writeFile

importlib.reload(APSModel)
importlib.reload(APSZoneModel)
importlib.reload(APSFaciesProb)
importlib.reload(APSMainFaciesTable)
importlib.reload(APSGaussFieldJobs)
importlib.reload(APSGaussModel)
importlib.reload(APSDataFromRMS)

importlib.reload(simGauss2D)
importlib.reload(Trunc2D_Cubic_xml)
importlib.reload(Trunc2D_Angle_xml)
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
        colors = ['lawngreen', 'grey', 'dodgerblue', 'gold', 'darkorchid', 'cyan', 'firebrick', 'olivedrab', 'blue', 'crimson']
    elif nFacies == 11:
        colors = ['lawngreen', 'grey', 'dodgerblue', 'gold', 'darkorchid', 'cyan', 'firebrick', 'olivedrab', 'blue', 'crimson', 'darkorange']
    elif nFacies == 12:
        colors = ['lawngreen', 'grey', 'dodgerblue', 'gold', 'darkorchid', 'cyan', 'firebrick', 'olivedrab', 'blue', 'crimson', 'darkorange', 'red']
    return colors


def set2DGridDimension(nx, ny, nz, previewCrossSection, previewLX, previewLY, previewLZ, previewScale=0, printInfo=0):
    MIN_NZ = 100
    MAX_NZ = 500
    MIN_NX = 300
    MAX_NX = 500
    MIN_NY = 300
    MAX_NY = 500
    nxPreview = nx
    nyPreview = ny
    nzPreview = nz
    print('previewLX,LY,LZ,scale:' + str(previewLX) + ' ' + str(previewLY) + ' ' + str(previewLZ) + ' ' + str(
        previewScale))
    if previewScale > 0:
        # Rescale vertical axis
        previewLZ = previewLZ * previewScale
    dx = previewLX / nx
    dy = previewLY / ny
    dz = previewLZ / nz
    # Use square pixels in IJ plane
    if useBestResolution:
        if nx < MIN_NX:
            nx = MIN_NX
            dx = previewLX / nx
        if ny < MIN_NY:
            ny = MIN_NY
            dy = previewLY / ny

        if dx < dy:
            dy = dx
            nyPreview = int(previewLY / dy)
        else:
            dx = dy
            nxPreview = int(previewLX / dx)
    else:
        if nx > MAX_NX:
            nx = MAX_NX
            dx = previewLX / nx
        if ny > MAX_NY:
            ny = MAX_NY
            dy = previewLY / ny

        if dx < dy:
            dx = dy
            nxPreview = int(previewLX / dx)
        else:
            dy = dx
            nyPreview = int(previewLY / dy)
    if printInfo >= 3:
        print('dx = {}  dy= {}'.format(str(dx),str(dy)))
        
    if previewScale == 0:
        # Rescale to same size as horizontal
        if previewCrossSection == 'IK':
            nzPreview = nxPreview
        if previewCrossSection == 'JK':
            nzPreview = nyPreview

        if nzPreview < MIN_NZ:
            nzPreview = MIN_NZ
    else:
        # Keep ratio between lateral and vertical scale including scaling factor
        if previewCrossSection == 'IK':
            ratio = previewLZ / previewLX
            nzPreview = int(nxPreview * ratio)
        if previewCrossSection == 'JK':
            ratio = previewLZ / previewLY
            nzPreview = int(nyPreview * ratio)

    print('nxPreview,nyPreview,nzPreview: ' + str(nxPreview) + ' ' + str(nyPreview) + ' ' + str(nzPreview))
    return [nxPreview, nyPreview, nzPreview]


def defineHorizontalAndVerticalResolutionForPlotting(
        previewCrossSection, nxPreview, nyPreview, nzPreview,
        previewLX, previewLY, previewLZ):
    if previewCrossSection == 'IJ':
        return [nxPreview, nyPreview, previewLX, previewLY]
    elif previewCrossSection == 'IK':
        return [nxPreview, nzPreview, previewLX, previewLZ]
    elif previewCrossSection == 'JK':
        return [nyPreview, nzPreview, previewLY, previewLZ]
    else:
        raise ValueError('Cross section: {} is not defined'.format(previewCrossSection))


# Initialise common variables
functionName = 'testPreview.py'
rotatePlot = 0
useBestResolution = 1
noSim = 0  # Is set to 1 only if one don't want to simulate 2D fields (for test purpose only)
setWrite = 0  # Is set to 1 if write out simulated 2D fields


# --------- Main function ----------------
def main():
    print('matplotlib version: ' + matplotlib.__version__)
    print('Run: testPreview')
    modelFileName = 'APS.xml'
    inputRMSDataFileName = 'rms_project_data_for_APS_gui.xml'

    print('- Read file: ' + modelFileName)
    apsModel = APSModel.APSModel(modelFileName)
    printInfo = apsModel.printInfo()
    zoneParamName = apsModel.getZoneParamName()
    mainFaciesTable = apsModel.getMainFaciesTable()

    gridModelName = apsModel.getGridModelName()
    previewZoneNumber = apsModel.getPreviewZoneNumber()
    previewCrossSection = apsModel.getPreviewCrossSection()
    previewScale = apsModel.getPreviewScale()
    if printInfo >= 3:
        print('Debug output: previewZoneNumber: ' + ' ' + str(previewZoneNumber))
        print('Debug output: previewCrossSection: ' + ' ' + str(previewCrossSection))
        print('Debug output: previewScale: ' + str(previewScale))
        print(' \n')

    rmsData = APSDataFromRMS.APSDataFromRMS()
    print('- Read file: ' + inputRMSDataFileName)
    rmsData.readRMSDataFromXMLFile(inputRMSDataFileName)
    [nxFromGrid, nyFromGrid, x0, y0, simBoxXsize, simBoxYsize, xinc, yinc, asimuthGridOrientation] = rmsData.getGridSize()
    nzFromGrid = rmsData.getNumberOfLayersInZone(previewZoneNumber)
    nx = int(nxFromGrid)
    ny = int(nyFromGrid)
    nz = int(nzFromGrid)
    zoneNumber = previewZoneNumber
    zoneModel = apsModel.getZoneModel(zoneNumber)
    if zoneModel == None:
        print('Error: Zone number: ' + str(zoneNumber) + ' is not defined')
        sys.exit()
    simBoxZsize = zoneModel.getSimBoxThickness()
    print('- Grid dimension from RMS grid: nx: {0} ny:{1} nz: {2}'.format(str(nx), str(ny), str(nz)))
    print('- Size of simulation box: LX: {0} LY:{1} LZ: {2}'.format(str(simBoxXsize), str(simBoxYsize), str(simBoxZsize)))
    print('- Simulate 2D cross section in: {} cross section'.format(previewCrossSection))

    [nxPreview, nyPreview, nzPreview] = set2DGridDimension(nx, ny, nz, previewCrossSection,
                                                           simBoxXsize, simBoxYsize, simBoxZsize, previewScale,printInfo)
    if previewCrossSection == 'IJ':
        print('- Preview simulation grid dimension: nx: {0} ny:{1}'.format(str(nxPreview), str(nyPreview)))
    elif previewCrossSection == 'IK':
        print('- Preview simulation grid dimension: nx: {0} nz:{1}'.format(str(nxPreview), str(nzPreview)))
    elif previewCrossSection == 'JK':
        print('- Preview simulation grid dimension: ny: {0} nz:{1}'.format(str(nyPreview), str(nzPreview)))

    truncObject = zoneModel.getTruncRule()
    faciesNames = zoneModel.getFaciesInZoneModel()
    gaussFieldNames = zoneModel.getUsedGaussFieldNames()
    nFacies = len(faciesNames)

    nGaussFields = len(gaussFieldNames)
    useConstProb = zoneModel.useConstProb()
    cellNumber = 0

    faciesOrdering = truncObject.getFaciesOrderIndexList()
    if useConstProb == 0:
        print('Error: Preview plots require constant facies probabilities')
        print('       Use arbitrary constant values')
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
    print('Facies prob:')
    print(repr(faciesProb))
    truncObject.setTruncRule(faciesProb)

    # Write datastructure:
    # truncObject.writeContentsInDataStructure()

    gaussFields = []
    if noSim == 1:
        # Read the gauss fields from files
        if nGaussFields >= 2:
            a1 = readFile('a1.dat')
            a2 = readFile('a2.dat')
        if nGaussFields >= 3:
            a3 = readFile('a3.dat')
        if nGaussFields >= 4:
            a4 = readFile('a4.dat')
        if nGaussFields >= 5:
            a5 = readFile('a5.dat')
        if nGaussFields >= 6:
            a6 = readFile('a6.dat')
    else:
        # simulate gauss fields
        gaussFields = zoneModel.simGaussFieldWithTrendAndTransformNew(
            nGaussFields, simBoxXsize, simBoxYsize, simBoxZsize,
            nxPreview, nyPreview, nzPreview, asimuthGridOrientation,
            previewCrossSection
        )
        if previewCrossSection == 'IJ':
            gridDim1 = nxPreview
            gridDim2 = nyPreview
        elif previewCrossSection == 'IK':
            gridDim1 = nxPreview
            gridDim2 = nzPreview
        elif previewCrossSection == 'JK':
            gridDim1 = nyPreview
            gridDim2 = nzPreview

        if setWrite == 1:
            print('Write 2D simulated gauss fields: ')
            for n in range(nGaussFields):
                gf = gaussFields[n]
                fileName = 'a' + str(n + 1) + '_' + previewCrossSection + '.dat'
                writeFile(fileName, gf, gridDim1, gridDim2)

    facies = np.zeros(gridDim1 * gridDim2, int)
    faciesFraction = np.zeros(nFacies, int)

    gfRealization1 = gaussFields[0]
    nGridCells = len(gfRealization1)
    alphaCoord = np.zeros(nGaussFields, np.float32)
    for i in range(nGridCells):
        for m in range(nGaussFields):
            alphaReal = gaussFields[m]
            alphaCoord[m] = alphaReal[i]
        [faciesCode, fIndx] = truncObject.defineFaciesByTruncRule(alphaCoord)

        facies[i] = fIndx + 1  # Use fIndx+1 as values in the facies plot
        faciesFraction[fIndx] += 1

    if setWrite == 1:
        writeFile('facies2D.dat', facies, gridDim1, gridDim2)
    if printInfo >= 3:
        print(' ')
        print('Facies name:   Simulated fractions:    Specified fractions:')
        for i in range(nFacies):
            f = faciesFraction[i]
            fraction = float(f) / float(len(facies))
            print('{0:10}  {1:.3f}   {2:.3f}'.format(faciesNames[i], fraction, faciesProb[i]))
        print(' ')


    # Calculate polygons for truncation map for current facies probability
    # as specified when calling setTruncRule(faciesProb)
    [faciesPolygons] = truncObject.truncMapPolygons()
    faciesIndxPerPolygon = truncObject.faciesIndxPerPolygon()

    fmap = np.reshape(facies, (gridDim2, gridDim1))  # Reshape to a 2D array with c-index ordering
    alphaMapList = []
    for m in range(nGaussFields):
        alphaReal = gaussFields[m]
        alphaMap = np.reshape(alphaReal, (gridDim2, gridDim1))
        alphaMapList.append(alphaMap)

    # Plot the result
    print('Make plots')
    fig = plt.figure(figsize=[20.0, 10.0])

    # Figure containing the transformed Gaussian fields and facies realization

    # figGauss,(ax1,ax2,ax3,ax4,ax5,ax6) = plt.subplots(1, 6,sharey=True)

    # Gauss1 transformed is plotted
    ax1 = plt.subplot(2, 6, 1)
    alphaMap = alphaMapList[0]
    if rotatePlot:
        rot_im1 = scipy.ndimage.interpolation.rotate(alphaMap, asimuthGridOrientation)
    else:
        rot_im1 = alphaMap
    if previewCrossSection == 'IJ':
        im1 = ax1.imshow(rot_im1, interpolation='none', aspect='equal', vmin=0.0, vmax=1.0, origin='lower')
        ax1.set_title('GRF1')
    else:
        im1 = ax1.imshow(rot_im1, interpolation='none', aspect='equal', vmin=0.0, vmax=1.0, origin='upper')
        ax1.set_title('GRF1')

    # Gauss2 transformed is plotted
    ax2 = plt.subplot(2, 6, 2)
    alphaMap = alphaMapList[1]
    if rotatePlot:
        rot_im2 = scipy.ndimage.interpolation.rotate(alphaMap, asimuthGridOrientation)
    else:
        rot_im2 = alphaMap
    if previewCrossSection == 'IJ':
        im2 = ax2.imshow(rot_im2, interpolation='none', aspect='equal', vmin=0.0, vmax=1.0, origin='lower')
        ax2.set_title('GRF2')
    else:
        im2 = ax2.imshow(rot_im2, interpolation='none', aspect='equal', vmin=0.0, vmax=1.0, origin='upper')
        ax2.set_title('GRF2')
    plt.setp(ax2.get_xticklabels(), visible=False)
    plt.setp(ax2.get_yticklabels(), visible=False)

    # Gauss3 transformed is plotted
    ax3 = plt.subplot(2, 6, 3)
    alphaReal = np.zeros(gridDim1 * gridDim2, np.float32)
    alphaMap = np.reshape(alphaReal, (gridDim2, gridDim1))
    if nGaussFields >= 3:
        alphaMap = alphaMapList[2]
    if rotatePlot:
        rot_im3 = scipy.ndimage.interpolation.rotate(alphaMap, asimuthGridOrientation)
    else:
        rot_im3 = alphaMap
    if previewCrossSection == 'IJ':
        im3 = ax3.imshow(rot_im3, interpolation='none', aspect='equal', vmin=0.0, vmax=1.0, origin='lower')
        ax3.set_title('GRF3')
    else:
        im3 = ax3.imshow(rot_im3, interpolation='none', aspect='equal', vmin=0.0, vmax=1.0, origin='upper')
        ax3.set_title('GRF3')
    plt.setp(ax3.get_xticklabels(), visible=False)
    plt.setp(ax3.get_yticklabels(), visible=False)

    # Gauss4 transformed is plotted
    ax4 = plt.subplot(2, 6, 7)
    alphaReal = np.zeros(gridDim1 * gridDim2, np.float32)
    alphaMap = np.reshape(alphaReal, (gridDim2, gridDim1))
    if nGaussFields >= 4:
        alphaMap = alphaMapList[3]
    if rotatePlot:
        rot_im4 = scipy.ndimage.interpolation.rotate(alphaMap, asimuthGridOrientation)
    else:
        rot_im4 = alphaMap
    if previewCrossSection == 'IJ':
        im4 = ax4.imshow(rot_im4, interpolation='none', aspect='equal', vmin=0.0, vmax=1.0, origin='lower')
        ax4.set_title('GRF4')
    else:
        im4 = ax4.imshow(rot_im4, interpolation='none', aspect='equal', vmin=0.0, vmax=1.0, origin='upper')
        ax4.set_title('GRF4')
    plt.setp(ax4.get_xticklabels(), visible=False)
    plt.setp(ax4.get_yticklabels(), visible=False)

    # Gauss5 transformed is plotted
    ax5 = plt.subplot(2, 6, 8)
    alphaReal = np.zeros(gridDim1 * gridDim2, np.float32)
    alphaMap = np.reshape(alphaReal, (gridDim2, gridDim1))
    if nGaussFields >= 5:
        alphaMap = alphaMapList[4]
    if rotatePlot:
        rot_im5 = scipy.ndimage.interpolation.rotate(alphaMap, asimuthGridOrientation)
    else:
        rot_im5 = alphaMap
    if previewCrossSection == 'IJ':
        im5 = ax5.imshow(rot_im5, interpolation='none', aspect='equal', vmin=0.0, vmax=1.0, origin='lower')
        ax5.set_title('GRF5')
    else:
        im5 = ax5.imshow(rot_im5, interpolation='none', aspect='equal', vmin=0.0, vmax=1.0, origin='upper')
        ax5.set_title('GRF5')
    plt.setp(ax5.get_xticklabels(), visible=False)
    plt.setp(ax5.get_yticklabels(), visible=False)

    # Gauss6 transformed is plotted
    ax6 = plt.subplot(2, 6, 9)
    alphaReal = np.zeros(gridDim1 * gridDim2, np.float32)
    alphaMap = np.reshape(alphaReal, (gridDim2, gridDim1))
    if nGaussFields >= 6:
        alphaMap = alphaMapList[5]
    if rotatePlot:
        rot_im6 = scipy.ndimage.interpolation.rotate(alphaMap, asimuthGridOrientation)
    else:
        rot_im6 = alphaMap
    if previewCrossSection == 'IJ':
        im6 = ax6.imshow(rot_im6, interpolation='none', aspect='equal', vmin=0.0, vmax=1.0, origin='lower')
        ax6.set_title('GRF6')
    else:
        im6 = ax6.imshow(rot_im6, interpolation='none', aspect='equal', vmin=0.0, vmax=1.0, origin='upper')
        ax6.set_title('GRF6')
    plt.setp(ax6.get_xticklabels(), visible=False)
    plt.setp(ax6.get_yticklabels(), visible=False)

    # Color legend for the transformed Gaussian fields
    cax1 = fig.add_axes([0.94, 0.52, 0.02, 0.4])
    fig.colorbar(im1, cax=cax1)

    # Figure containing truncation map and facies

    # Truncation map is plotted
    axTrunc = plt.subplot(2, 6, 10)
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
        # print('Polygon:{0:2d} Facies: {1:7}  Color: {2:12} Facies index(zone): {3:2d}'.format(i,fName,colors[fIndx],
        # fIndx))
    #    print('Polygon Points:')
    #    print(repr(poly))
    axTrunc.set_title('TruncMap')
    axTrunc.set_aspect('equal','box')
    # Facies map is plotted
    axFacies = plt.subplot(2, 6, 11)
    if rotatePlot:
        rot_imFac = scipy.ndimage.interpolation.rotate(fmap, asimuthGridOrientation)
    else:
        rot_imFac = fmap
    if previewCrossSection == 'IJ':
        imFac = axFacies.imshow(rot_imFac, interpolation='none', aspect='equal', cmap=cm, clim=(1, nFacies), origin='lower')
        axFacies.set_title('Facies')
    else:
        imFac = axFacies.imshow(rot_imFac, interpolation='none', aspect='equal', cmap=cm, clim=(1, nFacies), origin='upper')
        axFacies.set_title('Facies')
        
    # Plot crossplot between GRF1 and GRF2,3,4,5
    if nGaussFields >= 2:
        # Cross plot between G1 and G2
        alphaReal1 = gaussFields[0]
        alphaReal2 = gaussFields[1]
        axC1 = plt.subplot(2, 6, 4)
        plt.scatter(alphaReal1, alphaReal2, alpha=0.15, marker='.', c='b')
        axC1.set_title('Crossplot GRF1 GRF2')
        axC1.set_aspect('equal','box')
        plt.axis([0, 1, 0, 1])
    if nGaussFields >= 3:
        # Cross plot between G1 and G3
        alphaReal1 = gaussFields[0]
        alphaReal3 = gaussFields[2]
        axC2 = plt.subplot(2, 6, 5)
        plt.scatter(alphaReal1, alphaReal3, alpha=0.15, marker='.', c='b')
        axC2.set_title('Crossplot GRF1 GRF3')
        axC2.set_aspect('equal','box')
        plt.axis([0, 1, 0, 1])
        plt.setp(axC2.get_xticklabels(), visible=False)
        plt.setp(axC2.get_yticklabels(), visible=False)
    if nGaussFields >= 4:
        # Cross plot between G1 and G4
        alphaReal1 = gaussFields[0]
        alphaReal4 = gaussFields[3]
        axC3 = plt.subplot(2, 6, 6)
        plt.scatter(alphaReal1, alphaReal4, alpha=0.15, marker='.', c='b')
        axC3.set_title('Crossplot GRF1 GRF4')
        axC3.set_aspect('equal','box')
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
    text = 'Zone number: ' + str(zoneNumber) + ' Cross section: ' + previewCrossSection
    fig.text(0.50, 0.98, text, ha='center')
    for i in range(nFacies):
        p = int(faciesProb[i] * 1000 + 0.5)
        faciesProb[i] = float(p) / 1000.0
        text = faciesNames[i] + ':  ' + str(faciesProb[i])
        fig.text(0.02, 0.40 - 0.03 * i, text, ha='left')

    plt.show()
    print('Finished testPreview')


if __name__ == '__main__':
    main()
