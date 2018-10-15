#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Python3  test preliminary preview
from argparse import ArgumentParser, Namespace

import matplotlib
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Polygon

from src.algorithms.APSModel import APSModel
from src.utils.constants.simple import Debug, CrossSectionType
from src.utils.exceptions.xml import UndefinedZoneError
from src.utils.io import writeFileRTF
from src.utils.methods import get_colors, get_run_parameters
from src.utils.roxar.APSDataFromRMS import APSDataFromRMS
from src.utils.plotting import plot_gaussian_field, cross_plot, plot_facies


def set2DGridDimension(
        nx, ny, nz, previewCrossSectionType, previewLX, previewLY, previewLZ,
        previewScale=False, useBestResolution=True, debug_level=Debug.OFF
):
    MIN_NX = 300
    MAX_NX = 500
    MIN_NY = 300
    MAX_NY = 500
    nx_preview = nx
    ny_preview = ny
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

    x_length = previewLX
    y_length = previewLY
    z_length = previewLZ
    if previewCrossSectionType == CrossSectionType.IJ:
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
                ny_preview = int(previewLY / dy) + 1
            else:
                dx = dy
                nx_preview = int(previewLX / dx) + 1
        else:
            if nx > MAX_NX:
                nx = MAX_NX
                dx = previewLX / nx
            if ny > MAX_NY:
                ny = MAX_NY
                dy = previewLY / ny

            if dx < dy:
                dx = dy
                nx_preview = int(previewLX / dx) + 1
            else:
                dy = dx
                ny_preview = int(previewLY / dy) + 1
        if debug_level >= Debug.VERY_VERBOSE:
            print('Debug output:  dx = {}   dy= {}'.format(dx, dy))
            print('Debug output:  nxPreview = {}  nyPreview = {}'.format(nx_preview, ny_preview))

        x_length = previewLX
        y_length = previewLY

    else:
        if not previewScale:
            # Rescale to same size as horizontal
            if previewCrossSectionType == CrossSectionType.IK:
                nzPreview = nx_preview
                z_length = x_length
            if previewCrossSectionType == CrossSectionType.JK:
                nzPreview = ny_preview
                z_length = y_length

            if debug_level >= Debug.VERY_VERBOSE:
                dx = x_length / nx_preview
                dy = y_length / ny_preview
                print('Debug output:  dx = {}   dy= {}'.format(dx, dy))
                print('Debug output:  nxPreview = {}  nyPreview = {}'.format(nx_preview, ny_preview))

        else:
            # Keep ratio between lateral and vertical scale including scaling factor
            # and define nzPreview to follow this constraint
            if previewCrossSectionType == CrossSectionType.IK:
                ratio = previewLZ / previewLX
                nzPreview = int(nx_preview * ratio) + 1

                if debug_level >= Debug.VERY_VERBOSE:
                    dx = previewLX / nx_preview
                    dz = previewLZ / nzPreview
                    print('Debug output:  dx = {}   dz= {}'.format(dx, dz))

            if previewCrossSectionType == CrossSectionType.JK:
                ratio = previewLZ / previewLY
                nzPreview = int(ny_preview * ratio) + 1

                if debug_level >= Debug.VERY_VERBOSE:
                    dy = previewLY / ny_preview
                    dz = previewLZ / nzPreview
                    print('Debug output:  dy = {}   dz= {}'.format(dy, dz))

    preview_size = (nx_preview, ny_preview, nzPreview)
    lengths = (x_length, y_length, z_length)
    return preview_size, lengths


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
        apsModel = APSModel(model_file_name=model)
    elif isinstance(model, APSModel):
        apsModel = model
    else:
        raise ValueError("The given model format is not recognized.")
    debug_level = apsModel.debug_level
    preview_zone_number = apsModel.getPreviewZoneNumber()
    preview_region_number = apsModel.getPreviewRegionNumber()
    preview_cross_section = apsModel.preview_cross_section
    preview_scale = apsModel.preview_scale
    if debug_level >= Debug.VERY_VERBOSE:
        print(
            'Debug output: previewZoneNumber:       {previewZoneNumber}\n'
            'Debug output: previewRegionNumber:     {previewRegionNumber}\n'
            'Debug output: previewCrossSectionType: {previewCrossSectionType}\n'
            'Debug output: previewCrossSectionRelativePos: {previewCrossSectionRelativePos}\n'
            'Debug output: previewScale:            {previewScale}\n\n'.format(
                previewZoneNumber=preview_zone_number,
                previewRegionNumber=preview_region_number,
                previewCrossSectionType=preview_cross_section.type.name,
                previewCrossSectionRelativePos=preview_cross_section.relative_position,
                previewScale=preview_scale
            )
        )

    rmsData = APSDataFromRMS()
    if debug_level >= Debug.SOMEWHAT_VERBOSE:
        print('- Read file: {rms_data_file_name}'.format(rms_data_file_name=rms_data_file_name))
    rmsData.readRMSDataFromXMLFile(rms_data_file_name)
    [
        nxFromGrid, nyFromGrid, _, _, simBoxXsize, simBoxYsize, _, _, azimuthGridOrientation
    ] = rmsData.getGridSize()
    if not 0.0 <= azimuthGridOrientation <= 360.0:
        azimuthGridOrientation = azimuthGridOrientation % 360.0


    nzFromGrid = rmsData.getNumberOfLayersInZone(preview_zone_number)
    nx = int(nxFromGrid)
    ny = int(nyFromGrid)
    nz = int(nzFromGrid)
    zoneNumber = preview_zone_number
    regionNumber = preview_region_number
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
                previewCrossSectionType=preview_cross_section.type.name,
                previewCrossSectionRelativePos=preview_cross_section.relative_position
            )
        )

    preview_size, lengths = set2DGridDimension(
        nx, ny, nz, preview_cross_section.type,
        simBoxXsize, simBoxYsize, simBoxZsize, preview_scale, debug_level=debug_level
    )

    truncObject = zoneModel.truncation_rule
    faciesNames = zoneModel.getFaciesInZoneModel()
    gaussFieldNamesInModel = zoneModel.used_gaussian_field_names
    gaussFieldIndxList = zoneModel.getGaussFieldIndexListInZone()
    nGaussFieldsInTruncRule = len(gaussFieldIndxList)
    if debug_level >= Debug.VERBOSE:
        print('Gauss fields in truncation rule:')
        for i in range(len(gaussFieldIndxList)):
            index = gaussFieldIndxList[i]
            print('Gauss field number {}:  {}'
                  ''.format(str(i + 1), gaussFieldNamesInModel[index]))

    assert len(gaussFieldNamesInModel) >= 2
    nFacies = len(faciesNames)

    useConstProb = zoneModel.useConstProb()

    if not useConstProb and debug_level >= Debug.SOMEWHAT_VERBOSE:
        print('Error: Preview plots require constant facies probabilities')
        print('       Use arbitrary constant values')
    if debug_level >= Debug.SOMEWHAT_VERBOSE:
        print('\n ---------  Zone number : ' + str(zoneNumber) + ' -----------------')
    faciesProb = []
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

    # simulate gauss fields
    nx_preview, ny_preview, nz_preview = preview_size
    if debug_level >= Debug.VERBOSE:
        print('Debug output: nxPreview, nyPreview, nzPreview ({},{},{}): '.format(nx_preview, ny_preview, nz_preview))
        print('Debug output: azimuthGridOrientation: ' + str(azimuthGridOrientation))
    gauss_field_items = zoneModel.simGaussFieldWithTrendAndTransform(
        lengths, preview_size, azimuthGridOrientation, preview_cross_section
    )

    grid_dimensions, increments = get_dimensions(
        preview_cross_section.type, preview_size, (simBoxXsize, simBoxYsize, simBoxZsize)
    )

    facies, facies_fraction = create_facies_map(gauss_field_items, truncObject)

    if write_simulated_fields_to_file:
        x0 = 0.0
        y0 = 0.0
        if debug_level >= Debug.VERBOSE:
            print('Debug output: Write 2D simulated gauss fields:')
            for gaussian_field in gauss_field_items:
                file_name = gaussian_field.name + '_' + preview_cross_section.type.name + '.dat'
                writeFileRTF(file_name, gaussian_field.field, grid_dimensions, increments, x0, y0, debug_level=debug_level)
        writeFileRTF('facies2D.dat', facies, grid_dimensions, increments, x0, y0)

    if debug_level >= Debug.VERY_VERBOSE:
        print('\nFacies name:   Simulated fractions:    Specified fractions:')
        for i in range(nFacies):
            f = facies_fraction[i]
            fraction = float(f) / float(len(facies))
            print('{0:10}  {1:.3f}   {2:.3f}'.format(faciesNames[i], fraction, faciesProb[i]))
        print('')

    # Plot the result
    if debug_level >= Debug.SOMEWHAT_VERBOSE:
        print('Make plots')
    fig = plt.figure(figsize=[20.0, 10.0])

    # Figure containing the transformed Gaussian fields and facies realization

    plot_gaussian_fields(
        fig, gaussFieldIndxList, gauss_field_items, grid_dimensions,
        lengths, preview_cross_section, azimuthGridOrientation
    )

    # Figure containing truncation map and facies

    colors = get_colors(nFacies)
    # Create the colormap
    cm = matplotlib.colors.ListedColormap(colors, name='Colormap', N=nFacies)
    bounds = np.linspace(0.5, 0.5 + nFacies, nFacies + 1)
    labels = faciesNames
    ax_trunc = plt.subplot(2, 6, 10)
    plot_truncation_map(truncObject, ax=ax_trunc, num_facies=nFacies, debug_level=debug_level)

    fmap = np.reshape(facies, grid_dimensions[::-1], 'C')  # Reshape to a 2D matrix (gridDim2 = nRows, gridDim1 = nColumns)
    # Facies map is plotted
    axFacies = plt.subplot(2, 6, 11)
    imFac = plot_facies(axFacies, fmap, nFacies, cm, preview_cross_section.type, lengths, plot_ticks=False)

    # Plot crossplot between GRF1 and GRF2,3,4,5
    cross_plots = [
        (0, 1, (2, 6, 4)),
        (0, 2, (2, 6, 5)),
        (0, 3, (2, 6, 6)),
        (0, 4, (2, 6, 12)),
    ]

    for base_field_index, compare_field_index, placement in cross_plots:
        if base_field_index < nGaussFieldsInTruncRule and compare_field_index < nGaussFieldsInTruncRule:
            ax = plt.subplot(*placement)
            field_1 = gauss_field_items[base_field_index]
            field_2 = gauss_field_items[compare_field_index]
            cross_plot(ax, field_1, field_2)

    # Color legend for the truncation map and facies plots
    cax2 = fig.add_axes([0.94, 0.05, 0.02, 0.4])
    fig.colorbar(imFac, cax=cax2, ticks=bounds + 0.5, boundaries=bounds, drawedges=True)
    cax2.set_yticklabels(labels)

    # Adjust subplots
    plt.subplots_adjust(
        left=0.10, wspace=0.15, hspace=0.20, bottom=0.05, top=0.92
    )
    # Label the rows and columns of the table
    cross_section = preview_cross_section.type.name
    if regionNumber > 0:
        text = 'Zone number: ' + str(zoneNumber) + '  Region number: ' + str(regionNumber) + '  Cross section: ' + cross_section
    else:
        text = 'Zone number: ' + str(zoneNumber) + '  Cross section: ' + cross_section
    if preview_scale and (cross_section == 'IK' or cross_section == 'JK'):
        text += '  Vertical scale: ' + str(preview_scale)
    if cross_section == 'IJ':
        text += '  Cross section for K = ' + str(preview_cross_section.relative_position * nz_preview)
    elif cross_section == 'IK':
        text += '  Cross section for J = ' + str(preview_cross_section.relative_position * ny_preview)
    else:
        text += '  Cross section for I = ' + str(preview_cross_section.relative_position * nx_preview)

    fig.text(0.50, 0.98, text, ha='center')
    for i in range(nFacies):
        p = int(faciesProb[i] * 1000 + 0.5)
        faciesProb[i] = float(p) / 1000.0
        text = faciesNames[i] + ':  ' + str(faciesProb[i])
        fig.text(0.02, 0.40 - 0.03 * i, text, ha='left')

    plt.show()
    if debug_level >= Debug.SOMEWHAT_VERBOSE:
        print('Finished testPreview')


def get_dimensions(preview_cross_section_type, preview_size, simulation_box_size):
    x_preview, y_preview, z_preview = preview_size
    x_simulation, y_simulation, z_simulation = simulation_box_size
    if preview_cross_section_type == CrossSectionType.IJ:
        grid_dimensions = (x_preview, y_preview)
        increments = (x_simulation / x_preview, y_simulation / y_preview)
    elif preview_cross_section_type == CrossSectionType.IK:
        grid_dimensions = (x_preview, z_preview)
        increments = (x_simulation / x_preview, z_simulation / z_preview)
    elif preview_cross_section_type == CrossSectionType.JK:
        grid_dimensions = (y_preview, z_preview)
        increments = (y_simulation / y_preview, z_simulation / z_preview)
    else:
        raise ValueError("Invalid Cross Section Type ({})".format(preview_cross_section_type))
    return grid_dimensions, increments


def plot_truncation_map(truncation_rule, ax=None, fig=None, num_facies=None, debug_level=Debug.OFF):
    if num_facies is None:
        num_facies = truncation_rule.num_facies_in_zone
    if ax is None:
        fig, ax = plt.subplots()
    facies_ordering = truncation_rule.getFaciesOrderIndexList()

    # Calculate polygons for truncation map for current facies probability
    # as specified when calling setTruncRule(faciesProb)
    facies_polygons = truncation_rule.truncMapPolygons()
    facies_index_per_polygon = truncation_rule.faciesIndxPerPolygon()
    # Truncation map is plotted
    colors = get_colors(num_facies)
    if debug_level >= Debug.SOMEWHAT_VERBOSE:
        print(
            'Number of facies:          {num_facies}\n'
            'Number of facies polygons: {num_polygons}'.format(num_facies=num_facies, num_polygons=len(facies_polygons))
        )
    for i in range(len(facies_polygons)):
        index = facies_index_per_polygon[i]
        facies_index = facies_ordering[index]
        poly = facies_polygons[i]
        polygon = Polygon(poly, closed=True, facecolor=colors[facies_index])
        ax.add_patch(polygon)
    ax.set_title('Truncation Map')
    ax.set_aspect('equal', 'box')
    return fig, ax


def create_facies_map(gauss_fields, truncation_rule):
    grid_sizes = set([gf.field.size for gf in gauss_fields])
    assert len(grid_sizes) == 1
    num_grid_cells = grid_sizes.pop()
    facies = np.zeros(num_grid_cells, int)
    facies_fraction = {}
    # Find one realization to get the grid size
    alpha_coord = np.zeros(len(gauss_fields), np.float32)
    for i in range(num_grid_cells):
        for m in range(len(gauss_fields)):
            item = gauss_fields[m]
            alpha_realization = item.field
            alpha_coord[m] = alpha_realization[i]
        facies_code, facies_index = truncation_rule.defineFaciesByTruncRule(alpha_coord)

        facies[i] = facies_index + 1  # Use fIndx+1 as values in the facies plot
        if facies_index not in facies_fraction:
            facies_fraction[facies_index] = 0
        facies_fraction[facies_index] += 1
    return facies, facies_fraction


def plot_gaussian_fields(fig, gauss_field_index_list, gauss_field_items, grid_dimension,
                         lengths, preview_cross_section, azimuth_grid_orientation=None):
    # Gauss 1 - 6 transformed is plotted
    plots = []
    truncation_rules = [
        (0, plt.subplot(2, 6, 1), True),
        (1, plt.subplot(2, 6, 2), False),
        (2, plt.subplot(2, 6, 3), False),
        (3, plt.subplot(2, 6, 7), False),
        (4, plt.subplot(2, 6, 8), False),
        (5, plt.subplot(2, 6, 9), False),
    ]
    for number_in_trunc_rule, ax, ticks in truncation_rules:
        gaussian_field = _get_gaussian_field(gauss_field_index_list, gauss_field_items, number_in_trunc_rule)
        plots.append(plot_gaussian_field(
            gaussian_field, lengths=lengths, grid_dimensions=grid_dimension, ax=ax,
            plot_ticks=ticks, azimuth_grid_orientation=azimuth_grid_orientation, grid_index_order='C'
        ))
    # Color legend for the transformed Gaussian fields
    cax1 = fig.add_axes([0.94, 0.52, 0.02, 0.4])
    fig.colorbar(plots[0], cax=cax1)


def _get_gaussian_field(gauss_field_index_list, gauss_field_items, number_in_trunc_rule):
    try:
        return gauss_field_items[gauss_field_index_list[number_in_trunc_rule]]
    except (IndexError, KeyError):
        return None


def get_argument_parser() -> ArgumentParser:
    parser = ArgumentParser(description="A preliminary previewer for APS GUI")
    parser.add_argument('model', metavar='FILE', type=str, nargs='?', default='APS.xml', help="The model file to be viewed (default: APS.xml)")
    parser.add_argument('rms_data_file_name', metavar='DATA', type=str, nargs='?', default='rms_project_data_for_APS_gui.xml', help="The rms data file (default: rms_project_data_for_APS_gui.xml)")
    parser.add_argument('-r', '--rotate-plot', type=bool, default=False, help="Toggles rotation of plot (default: False)")
    parser.add_argument('-w', '--write-simulated-fields-to-file', nargs='?', type=bool, default=False, help="Toggles whether the simulated fileds should be dumped to disk (default: False)")
    parser.add_argument('-d', '--debug-level', type=int, default=0, help="Sets the verbosity. 0-4, where 0 is least verbose (default: 0)")
    return parser


def run(roxar=None, project=None, **kwargs):
    params = get_run_parameters(**kwargs)
    model = params['model_file']
    rms_data_file_name = params['rms_data_file']
    debug_level = params['debug_level']
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
