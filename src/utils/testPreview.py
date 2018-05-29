#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Python3  test preliminary preview
from argparse import ArgumentParser, Namespace

import matplotlib
import numpy as np
import scipy
from matplotlib import pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Polygon

from src.algorithms.APSModel import APSModel
from src.utils.constants.simple import Debug
from src.utils.exceptions.xml import UndefinedZoneError
from src.utils.io import writeFileRTF
from src.utils.methods import get_colors, get_run_parameters
from src.utils.roxar.APSDataFromRMS import APSDataFromRMS


def plotGaussField(subplotAxis, numberInTruncRule, gaussFieldItems, gaussFieldIndxList,
                   azimuthGridOrientation, previewCrossSectionType,
                   xLength, yLength, zLength, gridDim1, gridDim2,
                   plotTicks=True, rotate_plot=False, gridIndexOrder='F'):

    if numberInTruncRule >= len(gaussFieldIndxList):
        alphaReal = np.zeros(gridDim1 * gridDim2, np.float32)
        # Reshape to a 2D matrix where first index is row, second index is column
        if gridIndexOrder=='F':
            alphaMap  = np.reshape(alphaReal, (gridDim2, gridDim1),'F')
        else:
            alphaMap  = np.reshape(alphaReal, (gridDim2, gridDim1),'C')
        gaussName = 'Not used'
    else:
        item = gaussFieldItems[gaussFieldIndxList[numberInTruncRule]]
        gaussName = item[0]
        alphaReal = item[1]
        # Reshape to a 2D matrix where first index is row, second index is column
        if gridIndexOrder=='F':
            alphaMap = np.reshape(alphaReal, (gridDim2, gridDim1),'F')
        else:
            alphaMap = np.reshape(alphaReal, (gridDim2, gridDim1),'C')
    if rotate_plot:
        rot_im = scipy.ndimage.interpolation.rotate(alphaMap, azimuthGridOrientation)
    else:
        rot_im = alphaMap
    if previewCrossSectionType == 'IJ':
        im = subplotAxis.imshow(rot_im, interpolation='none', aspect='equal', extent=(0.0, xLength,0.0, yLength),
                                vmin=0.0, vmax=1.0, origin='lower')
        plt.axis([0.0, xLength, 0.0, yLength])
    elif previewCrossSectionType == 'IK':
        im = subplotAxis.imshow(rot_im, interpolation='none', aspect='equal', extent=(0.0, xLength, 0.0, zLength),
                                vmin=0.0, vmax=1.0, origin='lower')
        plt.axis([0.0, xLength, zLength, 0.0])
    else:
        im = subplotAxis.imshow(rot_im, interpolation='none', aspect='equal', extent=(0.0, yLength, 0.0, zLength),
                                vmin=0.0, vmax=1.0, origin='lower')
        plt.axis([0.0, yLength, zLength, 0.0])
    subplotAxis.set_title(gaussName)
    if not plotTicks:
        plt.setp(subplotAxis.get_xticklabels(), visible=False)
        plt.setp(subplotAxis.get_yticklabels(), visible=False)
    return im


def crossPlot(subplotAxis, numberInTruncRule1, numberInTruncRule2, gaussFieldItems, gaussFieldIndxList):
    # Plot crossplot between two specified gauss fields
    nGaussFieldsInTruncRule = len(gaussFieldIndxList)
    if numberInTruncRule1 < len(gaussFieldIndxList) and numberInTruncRule2 < len(gaussFieldIndxList):
        item1 = gaussFieldItems[gaussFieldIndxList[numberInTruncRule1]]
        gaussName1 = item1[0]
        alphaReal1 = item1[1]
        item2 = gaussFieldItems[gaussFieldIndxList[numberInTruncRule2]]
        gaussName2 = item2[0]
        alphaReal2 = item2[1]

        plt.scatter(alphaReal1, alphaReal2, alpha=0.15, marker='.', c='b')
        title = 'Crossplot ' + gaussName1 + '  ' + gaussName2
        subplotAxis.set_title(title)
        subplotAxis.set_aspect('equal', 'box')
        plt.axis([0, 1, 0, 1])


def plotFacies(subplotAxis, fmap, nFacies, cmap, azimuthGridOrientation, previewCrossSectionType,
                   xLength, yLength, zLength, plotTicks=True, rotate_plot=False):
    if rotate_plot:
        rot_imFac = scipy.ndimage.interpolation.rotate(fmap, azimuthGridOrientation)
    else:
        rot_imFac = fmap

    if previewCrossSectionType == 'IJ':
        imFac = subplotAxis.imshow(
            rot_imFac, interpolation='none', aspect='equal', cmap=cmap, clim=(1, nFacies), origin='lower',
            extent=(0.0, xLength,0.0, yLength)
        )
        plt.axis([0.0, xLength, 0.0, yLength])
    elif previewCrossSectionType == 'IK':
        imFac = subplotAxis.imshow(
            rot_imFac, interpolation='none', aspect='equal', cmap=cmap, clim=(1, nFacies), origin='lower',
            extent=(0.0, xLength,0.0, zLength)
        )
        plt.axis([0.0, xLength, zLength, 0.0])
    else:
        imFac = subplotAxis.imshow(
            rot_imFac, interpolation='none', aspect='equal', cmap=cmap, clim=(1, nFacies), origin='lower',
            extent=(0.0, yLength,0.0, zLength)
        )
        plt.axis([0.0, yLength, zLength, 0.0])
    subplotAxis.set_title('Facies')
    plt.setp(subplotAxis.get_xticklabels(), visible=False)
    plt.setp(subplotAxis.get_yticklabels(), visible=False)
    return imFac


def set2DGridDimension(
        nx, ny, nz, previewCrossSectionType, previewLX, previewLY, previewLZ,
        previewScale=False, useBestResolution=True, debug_level=Debug.OFF
):
    MIN_NZ = 100
    MIN_NX = 300
    MAX_NX = 500
    MIN_NY = 300
    MAX_NY = 500
    nxPreview = nx
    nyPreview = ny
    nzPreview = nz
    if debug_level >= Debug.VERY_VERBOSE:
        print(
            'Debug output: preview LX, LY, LZ, scale: {previewLX},  {previewLY},  {previewLZ},  {previewScale}'.format(
                previewLX=previewLX,
                previewLY=previewLY,
                previewLZ=previewLZ,
                previewScale=previewScale
            )
        )
    if previewScale:
        # Rescale vertical axis
        previewLZ = previewLZ * previewScale
    dx = previewLX / nx
    dy = previewLY / ny

    xLength = previewLX
    yLength = previewLY
    zLength = previewLZ
    if previewCrossSectionType == 'IJ':
        # Use square pixels in IJ plane. Adjust the number of grid cells.
        if useBestResolution:
            if nx < MIN_NX:
                nx = MIN_NX
                dx = previewLX / nx
            if ny < MIN_NY:
                ny = MIN_NY
                dy = previewLY / ny

            if dx < dy:
                dy = dx
                nyPreview = int(previewLY / dy) + 1
            else:
                dx = dy
                nxPreview = int(previewLX / dx) + 1
        else:
            if nx > MAX_NX:
                nx = MAX_NX
                dx = previewLX / nx
            if ny > MAX_NY:
                ny = MAX_NY
                dy = previewLY / ny

            if dx < dy:
                dx = dy
                nxPreview = int(previewLX / dx) + 1
            else:
                dy = dx
                nyPreview = int(previewLY / dy) + 1
        if debug_level >= Debug.VERY_VERBOSE:
            print('Debug output:  dx = {}   dy= {}'.format(str(dx), str(dy)))
            print('Debug output:  nxPreview = {}  nyPreview = {}'.format(str(nxPreview), str(nyPreview)))

        xLength = previewLX
        yLength = previewLY

    else:
        if not previewScale:
            # Rescale to same size as horizontal
            if previewCrossSectionType == 'IK':
                nzPreview = nxPreview
                zLength = xLength
            if previewCrossSectionType == 'JK':
                nzPreview = nyPreview
                zLength = yLength

            if debug_level >= Debug.VERY_VERBOSE:
                dx = xLength/nxPreview
                dy = yLength/nyPreview
                print('Debug output:  dx = {}   dy= {}'.format(str(dx), str(dy)))
                print('Debug output:  nxPreview = {}  nyPreview = {}'.format(str(nxPreview), str(nyPreview)))

        else:
            # Keep ratio between lateral and vertical scale including scaling factor
            # and define nzPreview to follow this constraint
            if previewCrossSectionType == 'IK':
                ratio = previewLZ / previewLX
                nzPreview = int(nxPreview * ratio) + 1

                if debug_level >= Debug.VERY_VERBOSE:
                    dx = previewLX/nxPreview
                    dz = previewLZ/nzPreview
                    print('Debug output:  dx = {}   dz= {}'.format(str(dx), str(dz)))

            if previewCrossSectionType == 'JK':
                ratio = previewLZ / previewLY
                nzPreview = int(nyPreview * ratio) + 1

                if debug_level >= Debug.VERY_VERBOSE:
                    dy = previewLY/nyPreview
                    dz = previewLZ/nzPreview
                    print('Debug output:  dy = {}   dz= {}'.format(str(dy), str(dz)))

    return nxPreview, nyPreview, nzPreview, xLength, yLength, zLength


def defineHorizontalAndVerticalResolutionForPlotting(
        previewCrossSectionType, nxPreview, nyPreview, nzPreview,
        previewLX, previewLY, previewLZ
):
    if previewCrossSectionType == 'IJ':
        return nxPreview, nyPreview, previewLX, previewLY
    elif previewCrossSectionType == 'IK':
        return nxPreview, nzPreview, previewLX, previewLZ
    elif previewCrossSectionType == 'JK':
        return nyPreview, nzPreview, previewLY, previewLZ
    else:
        raise ValueError('Cross section: {} is not defined'.format(previewCrossSectionType))


# Initialise common variables
functionName = 'testPreview.py'


# --------- Main function ----------------
def run_previewer(
        model='APS.xml',
        rms_data_file_name='rms_project_data_for_APS_gui.xml',
        rotate_plot=False,
        no_simulation=False,
        write_simulated_fields_to_file=False,
        debug_level=Debug.OFF,
        **kwargs
) -> None:
    """

    :param model:
    :param rms_data_file_name:
    :param rotate_plot:
    :param no_simulation: Is set to True only if one don't want to simulate 2D fields (for test purpose only)
    :param write_simulated_fields_to_file: Is set to 1 if write out simulated 2D fields
    :type write_simulated_fields_to_file: bool
    :param debug_level:
    :return:
    """
    if debug_level >= Debug.VERBOSE:
        print('matplotlib version: ' + matplotlib.__version__)
        print('Run: testPreview')
        if isinstance(model, str):
            print('- Read file: ' + model)
    if isinstance(model, str):
        apsModel = APSModel(modelFileName=model)
    elif isinstance(model, APSModel):
        apsModel = model
    else:
        raise ValueError("The given model format is not recognized.")
    debug_level = apsModel.debug_level()
    gridModelName = apsModel.getGridModelName()
    previewZoneNumber = apsModel.getPreviewZoneNumber()
    previewRegionNumber = apsModel.getPreviewRegionNumber()
    previewCrossSectionType = apsModel.getPreviewCrossSectionType()
    previewCrossSectionRelativePos = apsModel.getPreviewCrossSectionRelativePos()
    previewScale = apsModel.getPreviewScale()
    if debug_level >= Debug.VERY_VERBOSE:
        print(
            'Debug output: previewZoneNumber:       {previewZoneNumber}\n'
            'Debug output: previewRegionNumber:     {previewRegionNumber}\n'
            'Debug output: previewCrossSectionType: {previewCrossSectionType}\n'
            'Debug output: previewCrossSectionRelativePos: {previewCrossSectionRelativePos}\n'
            'Debug output: previewScale:            {previewScale}\n\n'.format(
                previewZoneNumber=previewZoneNumber,
                previewRegionNumber=previewRegionNumber,
                previewCrossSectionType=previewCrossSectionType,
                previewCrossSectionRelativePos=previewCrossSectionRelativePos,
                previewScale=previewScale
            )
        )

    rmsData = APSDataFromRMS()
    if debug_level >= Debug.SOMEWHAT_VERBOSE:
        print('- Read file: {rms_data_file_name}'.format(rms_data_file_name=rms_data_file_name))
    rmsData.readRMSDataFromXMLFile(rms_data_file_name)
    [
        nxFromGrid, nyFromGrid, _, _, simBoxXsize, simBoxYsize, _, _, azimuthGridOrientation
    ] = rmsData.getGridSize()
    nzFromGrid = rmsData.getNumberOfLayersInZone(previewZoneNumber)
    nx = int(nxFromGrid)
    ny = int(nyFromGrid)
    nz = int(nzFromGrid)
    zoneNumber = previewZoneNumber
    regionNumber = previewRegionNumber
    zoneModel = apsModel.getZoneModel(zoneNumber, regionNumber)
    if zoneModel is None:
        raise UndefinedZoneError(zoneNumber)
    simBoxZsize = zoneModel.getSimBoxThickness()
    if debug_level >= Debug.VERBOSE:
        print(
            '- Grid dimension from RMS grid: nx: {nx} ny:{ny} nz: {nz}\n'
            '- Size of simulation box: LX: {simBoxXsize}    LY:{simBoxYsize}    LZ: {simBoxZsize}\n'
            '- Simulate 2D cross section in: '
            '{previewCrossSectionType} cross section for index: {previewCrossSectionRelativePos}'.format(
                nx=nx,
                ny=ny,
                nz=nz,
                simBoxXsize=simBoxXsize,
                simBoxYsize=simBoxYsize,
                simBoxZsize=simBoxZsize,
                previewCrossSectionType=previewCrossSectionType,
                previewCrossSectionRelativePos=previewCrossSectionRelativePos
            )
        )

    nxPreview, nyPreview, nzPreview, xLength, yLength, zLength = set2DGridDimension(
        nx, ny, nz, previewCrossSectionType,
        simBoxXsize, simBoxYsize, simBoxZsize, previewScale, debug_level=debug_level
    )


    truncObject = zoneModel.getTruncRule()
    faciesNames = zoneModel.getFaciesInZoneModel()
    gaussFieldNamesInModel = zoneModel.getUsedGaussFieldNames()
    gaussFieldIndxList = zoneModel.getGaussFieldIndexListInZone()
    nGaussFieldsInModel = len(gaussFieldNamesInModel)
    nGaussFieldsInTruncRule = len(gaussFieldIndxList)
    if debug_level >= Debug.VERBOSE:
        print('Gauss fields in truncation rule:')
        for i in range(len(gaussFieldIndxList)):
            indx = gaussFieldIndxList[i]
            print('Gauss field number {}:  {}'
                  ''.format(str(i+1), gaussFieldNamesInModel[indx]))

    assert len(gaussFieldNamesInModel) >= 2
    nFacies = len(faciesNames)

    useConstProb = zoneModel.useConstProb()
    cellNumber = 0

    faciesOrdering = truncObject.getFaciesOrderIndexList()
    if not useConstProb and debug_level >= Debug.SOMEWHAT_VERBOSE:
        print('Error: Preview plots require constant facies probabilities')
        print('       Use arbitrary constant values')
    probParamNames = []
    faciesProb = []
    if debug_level >= Debug.SOMEWHAT_VERBOSE:
        print('\n ---------  Zone number : ' + str(zoneNumber) + ' -----------------')
    for fName in faciesNames:
        pName = zoneModel.getProbParamName(fName)
        if useConstProb:
            v = float(pName)
            p = int(v * 1000 + 0.5)
            w = float(p) / 1000.0
            if debug_level >= Debug.SOMEWHAT_VERBOSE:
                print('Zone: ' + str(zoneNumber) + ' Facies: ' + fName + ' Prob: ' + str(w))
        else:
            v = 1.0 / float(len(faciesNames))
            p = int(v * 1000 + 0.5)
            w = float(p) / 1000.0
            if debug_level >= Debug.SOMEWHAT_VERBOSE:
                print('Zone: ' + str(zoneNumber) + ' Facies: ' + fName + ' Prob: ' + str(w))
        faciesProb.append(v)

    # Calculate truncation map for given facies probabilities
    if debug_level >= Debug.SOMEWHAT_VERBOSE:
        print('Facies prob:')
        print(repr(faciesProb))
    truncObject.setTruncRule(faciesProb)

    # Write data structure:
    # truncObject.writeContentsInDataStructure()

    gaussFieldItems = []
    gridDim1 = 0
    gridDim2 = 0
    # simulate gauss fields
    print('nxPreview, nyPreview, nzPreview ({},{},{}): '.format(str(nxPreview), str(nyPreview), str(nzPreview)))
    gaussFieldItems = zoneModel.simGaussFieldWithTrendAndTransform(
        xLength, yLength, zLength,
        nxPreview, nyPreview, nzPreview, azimuthGridOrientation,
        previewCrossSectionType, previewCrossSectionRelativePos
    )
    if previewCrossSectionType == 'IJ':
        gridDim1 = nxPreview
        gridDim2 = nyPreview
        inc1 = simBoxXsize/nxPreview
        inc2 = simBoxYsize/nyPreview
    elif previewCrossSectionType == 'IK':
        gridDim1 = nxPreview
        gridDim2 = nzPreview
        inc1 = simBoxXsize/nxPreview
        inc2 = simBoxZsize/nzPreview
    elif previewCrossSectionType == 'JK':
        gridDim1 = nyPreview
        gridDim2 = nzPreview
        inc1 = simBoxYsize/nyPreview
        inc2 = simBoxZsize/nzPreview

    if write_simulated_fields_to_file:
        if debug_level >= Debug.VERBOSE:
            print('Write 2D simulated gauss fields: ')
            for n in range(nGaussFieldsInModel):
                item = gaussFieldItems[n]
                gfName = item[0]
                gf = item[1]
                fileName = gfName + '_' + previewCrossSectionType + '.dat'
                x0 = 0.0
                y0 = 0.0
                writeFileRTF(fileName, gf, gridDim1, gridDim2, inc1, inc2, x0, y0, debug_level=Debug.OFF)

    facies = np.zeros(gridDim1 * gridDim2, int)
    faciesFraction = np.zeros(nFacies, int)

    # Find one realization to get the grid size
    item = gaussFieldItems[0]
    gfRealization1 = item[1]
    nGridCells = len(gfRealization1)
    alphaCoord = np.zeros(nGaussFieldsInModel, np.float32)
    for i in range(nGridCells):
        for m in range(nGaussFieldsInModel):
            item = gaussFieldItems[m]
            name = item[0]
            alphaReal = item[1]
            alphaCoord[m] = alphaReal[i]
            faciesCode, fIndx = truncObject.defineFaciesByTruncRule(alphaCoord)

        facies[i] = fIndx + 1  # Use fIndx+1 as values in the facies plot
        faciesFraction[fIndx] += 1

    if write_simulated_fields_to_file:
        x0 = 0.0
        y0 = 0.0
        writeFileRTF('facies2D.dat', facies, gridDim1, gridDim2, inc1, inc2, x0, y0)

    if debug_level >= Debug.VERY_VERBOSE:
        print('\nFacies name:   Simulated fractions:    Specified fractions:')
        for i in range(nFacies):
            f = faciesFraction[i]
            fraction = float(f) / float(len(facies))
            print('{0:10}  {1:.3f}   {2:.3f}'.format(faciesNames[i], fraction, faciesProb[i]))
        print('')

    # Calculate polygons for truncation map for current facies probability
    # as specified when calling setTruncRule(faciesProb)
    faciesPolygons = truncObject.truncMapPolygons()
    faciesIndxPerPolygon = truncObject.faciesIndxPerPolygon()

    fmap = np.reshape(facies, (gridDim2, gridDim1),'C')  # Reshape to a 2D matrix (gridDim2 = nRows, gridDim1 = nColumns)

    # Plot the result
    if debug_level >= Debug.SOMEWHAT_VERBOSE:
        print('Make plots')
    fig = plt.figure(figsize=[20.0, 10.0])

    # Figure containing the transformed Gaussian fields and facies realization

    # Gauss1 transformed is plotted
    numberInTruncRule = 0
    ax1 = plt.subplot(2, 6, 1)
    im1 = plotGaussField(ax1, numberInTruncRule, gaussFieldItems, gaussFieldIndxList,
                         azimuthGridOrientation, previewCrossSectionType,
                         xLength, yLength, zLength, gridDim1, gridDim2, gridIndexOrder='C')

    # Gauss2 transformed is plotted
    numberInTruncRule = 1
    ax2 = plt.subplot(2, 6, 2)
    plotGaussField(ax2, numberInTruncRule, gaussFieldItems, gaussFieldIndxList,
                   azimuthGridOrientation, previewCrossSectionType,
                   xLength, yLength, zLength, gridDim1, gridDim2, plotTicks=False, gridIndexOrder='C')

    # Gauss3 transformed is plotted
    numberInTruncRule = 2
    ax3 = plt.subplot(2, 6, 3)
    plotGaussField(ax3, numberInTruncRule, gaussFieldItems, gaussFieldIndxList,
                   azimuthGridOrientation, previewCrossSectionType,
                   xLength, yLength, zLength, gridDim1, gridDim2, plotTicks=False, gridIndexOrder='C')

    # Gauss4 transformed is plotted
    numberInTruncRule = 3
    ax4 = plt.subplot(2, 6, 7)
    plotGaussField(ax4, numberInTruncRule, gaussFieldItems, gaussFieldIndxList,
                   azimuthGridOrientation, previewCrossSectionType,
                   xLength, yLength, zLength, gridDim1, gridDim2, plotTicks=False, gridIndexOrder='C')

    # Gauss5 transformed is plotted
    numberInTruncRule = 4
    ax5 = plt.subplot(2, 6, 8)
    plotGaussField(ax5, numberInTruncRule, gaussFieldItems, gaussFieldIndxList,
                   azimuthGridOrientation, previewCrossSectionType,
                   xLength, yLength, zLength, gridDim1, gridDim2, plotTicks=False, gridIndexOrder='C')

    # Gauss6 transformed is plotted
    numberInTruncRule = 5
    ax6 = plt.subplot(2, 6, 9)
    plotGaussField(ax6, numberInTruncRule, gaussFieldItems, gaussFieldIndxList,
                   azimuthGridOrientation, previewCrossSectionType,
                   xLength, yLength, zLength, gridDim1, gridDim2, plotTicks=False, gridIndexOrder='C')


    # Color legend for the transformed Gaussian fields
    cax1 = fig.add_axes([0.94, 0.52, 0.02, 0.4])
    fig.colorbar(im1, cax=cax1)

    # Figure containing truncation map and facies

    # Truncation map is plotted
    axTrunc = plt.subplot(2, 6, 10)
    colors = get_colors(nFacies)
    cmap_name = 'Colormap'

    # Create the colormap
    cm = matplotlib.colors.ListedColormap(colors, name=cmap_name, N=nFacies)
    bounds = np.linspace(0.5, 0.5 + nFacies, nFacies + 1)
    ticks = bounds
    labels = faciesNames
    colorNumberPerPolygon = []
    patches = []
    if debug_level >= Debug.SOMEWHAT_VERBOSE:
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
    axTrunc.set_title('TruncMap')
    axTrunc.set_aspect('equal', 'box')

    # Facies map is plotted
    axFacies = plt.subplot(2, 6, 11)
    imFac = plotFacies(axFacies, fmap, nFacies, cm, azimuthGridOrientation, previewCrossSectionType,
                       xLength, yLength, zLength, plotTicks=False)

    # Plot crossplot between GRF1 and GRF2,3,4,5
    numberInTruncRule1 = 0
    numberInTruncRule2 = 1
    if numberInTruncRule1 < nGaussFieldsInTruncRule and numberInTruncRule2 < nGaussFieldsInTruncRule:
        axC1 = plt.subplot(2, 6, 4)
        crossPlot(axC1, numberInTruncRule1, numberInTruncRule2, gaussFieldItems, gaussFieldIndxList)

    numberInTruncRule1 = 0
    numberInTruncRule2 = 2
    if numberInTruncRule1 < nGaussFieldsInTruncRule and numberInTruncRule2 < nGaussFieldsInTruncRule:
        axC2 = plt.subplot(2, 6, 5)
        crossPlot(axC2, numberInTruncRule1, numberInTruncRule2, gaussFieldItems, gaussFieldIndxList)

    numberInTruncRule1 = 0
    numberInTruncRule2 = 3
    if numberInTruncRule1 < nGaussFieldsInTruncRule and numberInTruncRule2 < nGaussFieldsInTruncRule:
        axC3 = plt.subplot(2, 6, 6)
        crossPlot(axC3, numberInTruncRule1, numberInTruncRule2, gaussFieldItems, gaussFieldIndxList)

    numberInTruncRule1 = 0
    numberInTruncRule2 = 4
    if numberInTruncRule1 < nGaussFieldsInTruncRule and numberInTruncRule2 < nGaussFieldsInTruncRule:
        axC4 = plt.subplot(2, 6, 12)
        crossPlot(axC4, numberInTruncRule1, numberInTruncRule2, gaussFieldItems, gaussFieldIndxList)

    # Color legend for the truncation map and facies plots
    cax2 = fig.add_axes([0.94, 0.05, 0.02, 0.4])
    fig.colorbar(imFac, cax=cax2, ticks=bounds + 0.5, boundaries=bounds, drawedges=True)
    cax2.set_yticklabels(labels)

    # Adjust subplots
    plt.subplots_adjust(
        left=0.10, wspace=0.15, hspace=0.20, bottom=0.05, top=0.92
    )
    # Label the rows and columns of the table
    if regionNumber > 0:
        text = 'Zone number: ' + str(zoneNumber) + '  Region number: ' + str(regionNumber)+ '  Cross section: ' + previewCrossSectionType
    else:
        text = 'Zone number: ' + str(zoneNumber) + '  Cross section: ' + previewCrossSectionType
    if previewScale and (previewCrossSectionType=='IK' or previewCrossSectionType=='JK'):
        text = text + '  Vertical scale: ' + str(previewScale)
    if previewCrossSectionType=='IJ':
        text = text + '  Cross section for K = ' + str(previewCrossSectionRelativePos * nzPreview)
    elif previewCrossSectionType=='IK':
        text = text + '  Cross section for J = ' + str(previewCrossSectionRelativePos * nyPreview)
    else:
        text = text + '  Cross section for I = ' + str(previewCrossSectionRelativePos * nxPreview)

    fig.text(0.50, 0.98, text, ha='center')
    for i in range(nFacies):
        p = int(faciesProb[i] * 1000 + 0.5)
        faciesProb[i] = float(p) / 1000.0
        text = faciesNames[i] + ':  ' + str(faciesProb[i])
        fig.text(0.02, 0.40 - 0.03 * i, text, ha='left')

    plt.show()
    if debug_level >= Debug.SOMEWHAT_VERBOSE:
        print('Finished testPreview')


def get_argument_parser() -> ArgumentParser:
    parser = ArgumentParser(description="A preliminary previewer for APS GUI")
    parser.add_argument('model', metavar='FILE', type=str, nargs='?', default='APS.xml', help="The model file to be viewed (default: APS.xml)")
    parser.add_argument('rms_data_file_name', metavar='DATA', type=str, nargs='?', default='rms_project_data_for_APS_gui.xml', help="The rms data file (default: rms_project_data_for_APS_gui.xml)")
    parser.add_argument('-r', '--rotate-plot', type=bool, default=False, help="Toggles rotation of plot (default: False)")
    parser.add_argument('-w', '--write-simulated-fields-to-file', nargs='?', type=bool, default=False, help="Toggles whether the simulated fileds should be dumped to disk (default: False)")
    parser.add_argument('-d', '--debug-level', type=int, default=0, help="Sets the verbosity. 0-4, where 0 is least verbose (default: 0)")
    return parser


def run(roxar=None, project=None, **kwargs):
    model, rms_data_file_name, _, _, debug_level = get_run_parameters(**kwargs)
    [kwargs.pop(item, None) for item in ['model', 'rms_data_file_name', 'debug_level']]
    run_previewer(model=model, rms_data_file_name=rms_data_file_name, debug_level=debug_level, **kwargs)


def get_arguments() -> Namespace:
    parser = get_argument_parser()
    args = parser.parse_args()
    args.debug_level = Debug(args.debug_level)
    return args


if __name__ == '__main__':
    args = get_arguments()
    run(**args.__dict__)
