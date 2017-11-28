#!/bin/env python
# Python3  test preliminary preview

import matplotlib
import numpy as np
import scipy

from matplotlib import pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Polygon

from src.APSDataFromRMS import APSDataFromRMS
from src.APSModel import APSModel
from src.utils.exceptions.xml import CrossSectionOutsideRange, UndefinedZoneError
from src.utils.constants.simple import Debug
from src.utils.io import readFile, writeFile


def defineColors(nFacies):
    """

    :param nFacies:
    :type nFacies:
    :return:
    :rtype:
    """
    colors = [
        'lawngreen', 'grey', 'dodgerblue', 'gold', 'darkorchid', 'cyan', 'firebrick',
        'olivedrab', 'blue', 'crimson', 'darkorange', 'red'
    ]
    if 2 <= nFacies <= len(colors):
        return colors[:nFacies]
    else:
        return []


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
    if debug_level >= Debug.VERBOSE:
        print(
            'preview LX, LY, LZ, scale: {previewLX}, {previewLY}, {previewLZ}, {previewScale}'.format(
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
        print('dx = {dx}  dy= {dy}'.format(dx=dx, dy=dy))

    if not previewScale:
        # Rescale to same size as horizontal
        if previewCrossSectionType == 'IK':
            nzPreview = nxPreview
        if previewCrossSectionType == 'JK':
            nzPreview = nyPreview

        if nzPreview < MIN_NZ:
            nzPreview = MIN_NZ
    else:
        # Keep ratio between lateral and vertical scale including scaling factor
        if previewCrossSectionType == 'IK':
            ratio = previewLZ / previewLX
            nzPreview = int(nxPreview * ratio) + 1
        if previewCrossSectionType == 'JK':
            ratio = previewLZ / previewLY
            nzPreview = int(nyPreview * ratio) + 1

    if debug_level >= Debug.VERY_VERY_VERBOSE:
        print(
            'nxPreview, nyPreview, nzPreview: {nxPreview}, {nyPreview}, {nzPreview}'.format(
                nxPreview=nxPreview,
                nyPreview=nyPreview,
                nzPreview=nzPreview
            )
        )
    return [nxPreview, nyPreview, nzPreview]


def defineHorizontalAndVerticalResolutionForPlotting(
        previewCrossSectionType, nxPreview, nyPreview, nzPreview,
        previewLX, previewLY, previewLZ
):
    if previewCrossSectionType == 'IJ':
        return [nxPreview, nyPreview, previewLX, previewLY]
    elif previewCrossSectionType == 'IK':
        return [nxPreview, nzPreview, previewLX, previewLZ]
    elif previewCrossSectionType == 'JK':
        return [nyPreview, nzPreview, previewLY, previewLZ]
    else:
        raise ValueError('Cross section: {} is not defined'.format(previewCrossSectionType))


# Initialise common variables
functionName = 'testPreview.py'


# --------- Main function ----------------
def run_previewer(
        model='APS.xml',
        rms_data_file_name='rms_project_data_for_APS_gui.xml',
        rotate_plot=False,
        no_sim=False,
        write_simulated_fields_to_file=False,
        debug_level=Debug.OFF
) -> None:
    """

    :param model:
    :param rms_data_file_name:
    :param rotate_plot:
    :param no_sim: Is set to True only if one don't want to simulate 2D fields (for test purpose only)
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

    previewZoneNumber = apsModel.getPreviewZoneNumber()
    previewCrossSectionType = apsModel.getPreviewCrossSectionType()
    previewCrossSectionIndx = apsModel.getPreviewCrossSectionIndx()
    previewScale = apsModel.getPreviewScale()
    if debug_level >= Debug.VERY_VERBOSE:
        print(
            'Debug output: previewZoneNumber:       {previewZoneNumber}\n'
            'Debug output: previewCrossSectionType: {previewCrossSectionType}\n'
            'Debug output: previewCrossSectionIndx: {previewCrossSectionIndx}\n'
            'Debug output: previewScale:            {previewScale}\n\n'.format(
                previewZoneNumber=previewZoneNumber,
                previewCrossSectionType=previewCrossSectionType,
                previewCrossSectionIndx=previewCrossSectionIndx,
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
    zoneModel = apsModel.getZoneModel(zoneNumber)
    if zoneModel is None:
        raise UndefinedZoneError(zoneNumber)
    simBoxZsize = zoneModel.getSimBoxThickness()
    if debug_level >= Debug.VERBOSE:
        print(
            '- Grid dimension from RMS grid: nx: {nx} ny:{ny} nz: {nz}\n'
            '- Size of simulation box: LX: {simBoxXsize} LY:{simBoxYsize} LZ: {simBoxZsize}\n'
            '- Simulate 2D cross section in: '
            '{previewCrossSectionType} cross section for index: {previewCrossSectionIndx}'.format(
                nx=nx,
                ny=ny,
                nz=nz,
                simBoxXsize=simBoxXsize,
                simBoxYsize=simBoxYsize,
                simBoxZsize=simBoxZsize,
                previewCrossSectionType=previewCrossSectionType,
                previewCrossSectionIndx=previewCrossSectionIndx
            )
        )

    [nxPreview, nyPreview, nzPreview] = set2DGridDimension(
        nx, ny, nz, previewCrossSectionType,
        simBoxXsize, simBoxYsize, simBoxZsize, previewScale, debug_level=debug_level
    )
    _check_preview_section(
        nx, nxPreview, ny, nyPreview, nz, nzPreview, previewCrossSectionIndx, previewCrossSectionType, debug_level
    )

    truncObject = zoneModel.getTruncRule()
    faciesNames = zoneModel.getFaciesInZoneModel()
    gaussFieldNames = zoneModel.getUsedGaussFieldNames()
    if debug_level >= Debug.VERBOSE:
        print('Gauss field names:')
        print(repr(gaussFieldNames))
    assert len(gaussFieldNames) >= 2
    nFacies = len(faciesNames)

    nGaussFields = len(gaussFieldNames)
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

    gaussFields = []
    gridDim1 = 0
    gridDim2 = 0
    if no_sim:
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
        gaussFields = zoneModel.simGaussFieldWithTrendAndTransform(
            nGaussFields, simBoxXsize, simBoxYsize, simBoxZsize,
            nxPreview, nyPreview, nzPreview, azimuthGridOrientation,
            previewCrossSectionType, previewCrossSectionIndx
        )

        if previewCrossSectionType == 'IJ':
            gridDim1 = nxPreview
            gridDim2 = nyPreview
        elif previewCrossSectionType == 'IK':
            gridDim1 = nxPreview
            gridDim2 = nzPreview
        elif previewCrossSectionType == 'JK':
            gridDim1 = nyPreview
            gridDim2 = nzPreview

        if write_simulated_fields_to_file:
            if debug_level >= Debug.VERBOSE:
                print('Write 2D simulated gauss fields: ')
            for n in range(nGaussFields):
                gf = gaussFields[n]
                fileName = 'a' + str(n + 1) + '_' + previewCrossSectionType + '.dat'
                writeFile(fileName, gf, gridDim1, gridDim2, debug_level)

    facies = np.zeros(gridDim1 * gridDim2, int)
    faciesFraction = np.zeros(nFacies, int)

    gfRealization1 = gaussFields[0]
    nGridCells = len(gfRealization1)
    alphaCoord = np.zeros(nGaussFields, np.float32)
    for i in range(nGridCells):
        for m in range(nGaussFields):
            alphaReal = gaussFields[m]
            alphaCoord[m] = alphaReal[i]
        [_, fIndx] = truncObject.defineFaciesByTruncRule(alphaCoord)

        facies[i] = fIndx + 1  # Use fIndx+1 as values in the facies plot
        faciesFraction[fIndx] += 1

    if write_simulated_fields_to_file:
        writeFile('facies2D.dat', facies, gridDim1, gridDim2)
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

    fmap = np.reshape(facies, (gridDim2, gridDim1))  # Reshape to a 2D array with c-index ordering
    alphaMapList = []
    for m in range(nGaussFields):
        alphaReal = gaussFields[m]
        alphaMap = np.reshape(alphaReal, (gridDim2, gridDim1))
        alphaMapList.append(alphaMap)

    # Plot the result
    if debug_level >= Debug.SOMEWHAT_VERBOSE:
        print('Make plots')
    fig = plt.figure(figsize=[20.0, 10.0])

    # Figure containing the transformed Gaussian fields and facies realization

    # figGauss,(ax1,ax2,ax3,ax4,ax5,ax6) = plt.subplots(1, 6,sharey=True)

    # Gauss1 transformed is plotted
    ax1 = plt.subplot(2, 6, 1)
    alphaMap = alphaMapList[0]
    gaussName = gaussFieldNames[0]
    if rotate_plot:
        rot_im1 = scipy.ndimage.interpolation.rotate(alphaMap, azimuthGridOrientation)
    else:
        rot_im1 = alphaMap
    if previewCrossSectionType == 'IJ':
        im1 = ax1.imshow(rot_im1, interpolation='none', aspect='equal', vmin=0.0, vmax=1.0, origin='lower')
        ax1.set_title(gaussName)
    else:
        im1 = ax1.imshow(rot_im1, interpolation='none', aspect='equal', vmin=0.0, vmax=1.0, origin='upper')
        ax1.set_title(gaussName)

    # Gauss2 transformed is plotted
    ax2 = plt.subplot(2, 6, 2)
    alphaMap = alphaMapList[1]
    gaussName = gaussFieldNames[1]
    if rotate_plot:
        rot_im2 = scipy.ndimage.interpolation.rotate(alphaMap, azimuthGridOrientation)
    else:
        rot_im2 = alphaMap
    if previewCrossSectionType == 'IJ':
        im2 = ax2.imshow(rot_im2, interpolation='none', aspect='equal', vmin=0.0, vmax=1.0, origin='lower')
        ax2.set_title(gaussName)
    else:
        im2 = ax2.imshow(rot_im2, interpolation='none', aspect='equal', vmin=0.0, vmax=1.0, origin='upper')
        ax2.set_title(gaussName)
    plt.setp(ax2.get_xticklabels(), visible=False)
    plt.setp(ax2.get_yticklabels(), visible=False)

    # Gauss3 transformed is plotted
    ax3 = plt.subplot(2, 6, 3)
    alphaReal = np.zeros(gridDim1 * gridDim2, np.float32)
    alphaMap = np.reshape(alphaReal, (gridDim2, gridDim1))

    if nGaussFields >= Debug.VERY_VERBOSE:
        gaussName = gaussFieldNames[2]
        alphaMap = alphaMapList[2]
    if rotate_plot:
        rot_im3 = scipy.ndimage.interpolation.rotate(alphaMap, azimuthGridOrientation)
    else:
        rot_im3 = alphaMap
    if previewCrossSectionType == 'IJ':
        im3 = ax3.imshow(rot_im3, interpolation='none', aspect='equal', vmin=0.0, vmax=1.0, origin='lower')
        ax3.set_title(gaussName)
    else:
        im3 = ax3.imshow(rot_im3, interpolation='none', aspect='equal', vmin=0.0, vmax=1.0, origin='upper')
        ax3.set_title(gaussName)
    plt.setp(ax3.get_xticklabels(), visible=False)
    plt.setp(ax3.get_yticklabels(), visible=False)

    # Gauss4 transformed is plotted
    ax4 = plt.subplot(2, 6, 7)
    alphaReal = np.zeros(gridDim1 * gridDim2, np.float32)
    alphaMap = np.reshape(alphaReal, (gridDim2, gridDim1))

    if nGaussFields >= 4:
        gaussName = gaussFieldNames[3]
        alphaMap = alphaMapList[3]
    if rotate_plot:
        rot_im4 = scipy.ndimage.interpolation.rotate(alphaMap, azimuthGridOrientation)
    else:
        rot_im4 = alphaMap
    if previewCrossSectionType == 'IJ':
        im4 = ax4.imshow(rot_im4, interpolation='none', aspect='equal', vmin=0.0, vmax=1.0, origin='lower')
        ax4.set_title(gaussName)
    else:
        im4 = ax4.imshow(rot_im4, interpolation='none', aspect='equal', vmin=0.0, vmax=1.0, origin='upper')
        ax4.set_title(gaussName)
    plt.setp(ax4.get_xticklabels(), visible=False)
    plt.setp(ax4.get_yticklabels(), visible=False)

    # Gauss5 transformed is plotted
    ax5 = plt.subplot(2, 6, 8)
    alphaReal = np.zeros(gridDim1 * gridDim2, np.float32)
    alphaMap = np.reshape(alphaReal, (gridDim2, gridDim1))

    if nGaussFields >= 5:
        gaussName = gaussFieldNames[4]
        alphaMap = alphaMapList[4]
    if rotate_plot:
        rot_im5 = scipy.ndimage.interpolation.rotate(alphaMap, azimuthGridOrientation)
    else:
        rot_im5 = alphaMap
    if previewCrossSectionType == 'IJ':
        im5 = ax5.imshow(rot_im5, interpolation='none', aspect='equal', vmin=0.0, vmax=1.0, origin='lower')
        ax5.set_title(gaussName)
    else:
        im5 = ax5.imshow(rot_im5, interpolation='none', aspect='equal', vmin=0.0, vmax=1.0, origin='upper')
        ax5.set_title(gaussName)
    plt.setp(ax5.get_xticklabels(), visible=False)
    plt.setp(ax5.get_yticklabels(), visible=False)

    # Gauss6 transformed is plotted
    ax6 = plt.subplot(2, 6, 9)
    alphaReal = np.zeros(gridDim1 * gridDim2, np.float32)
    alphaMap = np.reshape(alphaReal, (gridDim2, gridDim1))

    if nGaussFields >= 6:
        gaussName = gaussFieldNames[5]
        alphaMap = alphaMapList[5]
    if rotate_plot:
        rot_im6 = scipy.ndimage.interpolation.rotate(alphaMap, azimuthGridOrientation)
    else:
        rot_im6 = alphaMap
    if previewCrossSectionType == 'IJ':
        im6 = ax6.imshow(rot_im6, interpolation='none', aspect='equal', vmin=0.0, vmax=1.0, origin='lower')
        ax6.set_title(gaussName)
    else:
        im6 = ax6.imshow(rot_im6, interpolation='none', aspect='equal', vmin=0.0, vmax=1.0, origin='upper')
        ax6.set_title(gaussName)
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
    if rotate_plot:
        rot_imFac = scipy.ndimage.interpolation.rotate(fmap, azimuthGridOrientation)
    else:
        rot_imFac = fmap
    if previewCrossSectionType == 'IJ':
        imFac = axFacies.imshow(
            rot_imFac, interpolation='none', aspect='equal', cmap=cm, clim=(1, nFacies), origin='lower'
        )
        axFacies.set_title('Facies')
    else:
        imFac = axFacies.imshow(
            rot_imFac, interpolation='none', aspect='equal', cmap=cm, clim=(1, nFacies), origin='upper'
        )
        axFacies.set_title('Facies')

    # Plot crossplot between GRF1 and GRF2,3,4,5
    if nGaussFields >= 2:
        # Cross plot between G1 and G2
        alphaReal1 = gaussFields[0]
        alphaReal2 = gaussFields[1]
        axC1 = plt.subplot(2, 6, 4)
        plt.scatter(alphaReal1, alphaReal2, alpha=0.15, marker='.', c='b')
        title = 'Crossplot ' + gaussFieldNames[0] + '  ' + gaussFieldNames[1]
        axC1.set_title(title)
        axC1.set_aspect('equal', 'box')
        plt.axis([0, 1, 0, 1])
    if nGaussFields >= Debug.VERY_VERBOSE:
        # Cross plot between G1 and G3
        alphaReal1 = gaussFields[0]
        alphaReal3 = gaussFields[2]
        axC2 = plt.subplot(2, 6, 5)
        plt.scatter(alphaReal1, alphaReal3, alpha=0.15, marker='.', c='b')
        title = 'Crossplot ' + gaussFieldNames[0] + '  ' + gaussFieldNames[2]
        axC2.set_title(title)
        axC2.set_aspect('equal', 'box')
        plt.axis([0, 1, 0, 1])
        plt.setp(axC2.get_xticklabels(), visible=False)
        plt.setp(axC2.get_yticklabels(), visible=False)
    if nGaussFields >= 4:
        # Cross plot between G1 and G4
        alphaReal1 = gaussFields[0]
        alphaReal4 = gaussFields[3]
        axC3 = plt.subplot(2, 6, 6)
        plt.scatter(alphaReal1, alphaReal4, alpha=0.15, marker='.', c='b')
        title = 'Crossplot ' + gaussFieldNames[0] + '  ' + gaussFieldNames[3]
        axC3.set_title(title)
        axC3.set_aspect('equal', 'box')
        plt.axis([0, 1, 0, 1])
        plt.setp(axC3.get_xticklabels(), visible=False)
        plt.setp(axC3.get_yticklabels(), visible=False)
    if nGaussFields >= 5:
        # Cross plot between G1 and G5
        alphaReal1 = gaussFields[0]
        alphaReal5 = gaussFields[4]
        axC4 = plt.subplot(2, 6, 12)
        plt.scatter(alphaReal1, alphaReal5, alpha=0.15, marker='.', c='b')
        title = 'Crossplot ' + gaussFieldNames[0] + '  ' + gaussFieldNames[4]
        axC4.set_title(title)
        plt.axis([0, 1, 0, 1])
        plt.setp(axC4.get_xticklabels(), visible=False)
        plt.setp(axC4.get_yticklabels(), visible=False)

    # Color legend for the truncation map and facies plots
    cax2 = fig.add_axes([0.94, 0.05, 0.02, 0.4])
    fig.colorbar(imFac, cax=cax2, ticks=bounds + 0.5, boundaries=bounds, drawedges=True)
    cax2.set_yticklabels(labels)

    # Adjust subplots
    plt.subplots_adjust(
        left=0.10, wspace=0.15, hspace=0.20, bottom=0.05, top=0.92
    )
    # Label the rows and columns of the table
    text = 'Zone number: ' + str(zoneNumber) + ' Cross section: ' + previewCrossSectionType
    fig.text(0.50, 0.98, text, ha='center')
    for i in range(nFacies):
        p = int(faciesProb[i] * 1000 + 0.5)
        faciesProb[i] = float(p) / 1000.0
        text = faciesNames[i] + ':  ' + str(faciesProb[i])
        fig.text(0.02, 0.40 - 0.03 * i, text, ha='left')

    plt.show()
    if debug_level >= Debug.SOMEWHAT_VERBOSE:
        print('Finished testPreview')


def _check_preview_section(
        nx, nxPreview, ny, nyPreview, nz, nzPreview, previewCrossSectionIndx,
        previewCrossSectionType, debug_level=Debug.OFF
):
    if previewCrossSectionType == 'IJ':
        if not 0 <= previewCrossSectionIndx < nz:
            raise CrossSectionOutsideRange('IJ', previewCrossSectionIndx, nz - 1)
        if debug_level >= Debug.VERBOSE:
            print(
                '- Preview simulation grid dimension: nx: {nxPreview} ny:{nyPreview}'.format(
                    nxPreview=nxPreview,
                    nyPreview=nyPreview
                )
            )
    elif previewCrossSectionType == 'IK':
        if not 0 <= previewCrossSectionIndx < ny:
            raise CrossSectionOutsideRange('IK', previewCrossSectionIndx, ny - 1)
        if debug_level >= Debug.VERBOSE:
            print(
                '- Preview simulation grid dimension: nx: {nxPreview} nz:{nzPreview}'.format(
                    nxPreview=nxPreview,
                    nzPreview=nzPreview
                )
            )
    elif previewCrossSectionType == 'JK':
        if not 0 <= previewCrossSectionIndx < nx:
            raise CrossSectionOutsideRange('JK', previewCrossSectionIndx, nx - 1)
        if debug_level >= Debug.VERBOSE:
            print(
                '- Preview simulation grid dimension: ny: {nyPreview} nz:{nzPreview}'.format(
                    nyPreview=nyPreview,
                    nzPreview=nzPreview
                )
            )


if __name__ == '__main__':
    run_previewer()
