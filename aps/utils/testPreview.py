#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Python3  test preliminary preview
from argparse import ArgumentParser, Namespace

import matplotlib
matplotlib.use('Tkagg')
from matplotlib import pyplot as plt

import collections
import numpy as np
from matplotlib.patches import Polygon

from aps.algorithms.APSModel import APSModel
from aps.utils.constants.simple import Debug, CrossSectionType
from aps.utils.exceptions.xml import UndefinedZoneError
from aps.utils.io import writeFileRTF
from aps.utils.methods import get_colors, get_run_parameters, get_debug_level
from aps.utils.roxar.APSDataFromRMS import APSDataFromRMS
from aps.utils.plotting import plot_gaussian_field, cross_plot, plot_facies
from aps.utils.facies_map import create_facies_map


def high_resolution_2D_grids(
    nx, ny, nz,
    preview_cross_section_type,
    original_simulation_box_size,
    preview_scale=False,
    debug_level=Debug.OFF
):

    previewLX, previewLY, previewLZ = original_simulation_box_size
    # Calculate grid resolution for the cross section when choosing high resolution
    # First redefine lateral grid resolution
    MIN_NX = 200
    MIN_NY = 200
    if nx < MIN_NX:
        nx_preview = MIN_NX
    else:
        nx_preview = nx

    if ny < MIN_NY:
        ny_preview = MIN_NY
    else:
        ny_preview = ny

    nz_preview = nz
    if preview_scale:
        # Rescale vertical axis
        previewLZ = previewLZ * preview_scale

    if preview_cross_section_type == CrossSectionType.IJ:
        # Use square pixels in IJ plane. Adjust the number of grid cells.
        dx = previewLX / nx_preview
        dy = previewLY / ny_preview

        if dx < dy:
            dy = dx
            ny_preview = int(previewLY / dy) + 1
        else:
            dx = dy
            nx_preview = int(previewLX / dx) + 1

        if debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: Cross section: IJ')
            print('Debug output:  Grid increment for high resolution preview: dx = {}   dy= {}'
                  ''.format(dx, dy))
            print('Debug output:  Grid size for high resolution preview: nxPreview = {}  nyPreview = {}'
                  ''.format(nx_preview, ny_preview))

    else:
        # Ratio between vertical length multiplied by scaling factor and horizontal length should be the same as the ratio between
        # number of grid cells vertically and horizontally to keep the grid cells or pixels as close to squares as possible.
        if preview_cross_section_type == CrossSectionType.IK:
            ratio = previewLZ / previewLX
            # Redefine vertical grid resolution
            nz_preview = int(nx_preview * ratio) + 1
            dx = previewLX / nx_preview
            dz = previewLZ / nz_preview

            if debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: Cross section: IK')
                print('Debug output:  Grid increment for high resolution preview: dx = {}   dz= {}'
                      ''.format(dx, dz))
                print('Debug output:  Grid size for high resolution preview: nxPreview = {}  nzPreview = {}'
                      ''.format(nx_preview, nz_preview))

        if preview_cross_section_type == CrossSectionType.JK:
            ratio = previewLZ / previewLY
            # Redefine vertical grid resolution
            nz_preview = int(ny_preview * ratio) + 1
            dy = previewLY / ny_preview
            dz = previewLZ / nz_preview
            if debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: Cross section: JK')
                print('Debug output:  Grid increment for high resolution preview: dy = {}   dz= {}'
                      ''.format(dy, dz))
                print('Debug output:  Grid size for high resolution preview: nyPreview = {}  nzPreview = {}'
                      ''.format(ny_preview, nz_preview))

    preview_grid_size = (nx_preview, ny_preview, nz_preview)
    return preview_grid_size


def set2DGridDimension(
        nx, ny, nz,
        preview_cross_section_type,
        original_simulation_box_size,
        preview_scale=False,
        use_high_resolution=False,
        debug_level=Debug.OFF
):
    '''
    Returns a tuple with number of grid cells (nx, ny, nz) for each coordinate direction.
    The output is identical to input if useHighResolution=False and the number of grid cells is
    re-calculated to a higher vertical resolution and possibly higher lateral resolution if
    useHighResolution = True. It is only the number of grid cells in the specified cross section that is re-calculated
    and not the number of cells in the third dimension orthogonal to the cross section.
    '''
    if not use_high_resolution:
        # Default is to use the grid resolution from the RMS grid model
        grid_size = (nx, ny, nz)
    else:
        # Increase resolution (preview_size), but no vertical scaling
        grid_size = high_resolution_2D_grids(
            nx, ny, nz,
            preview_cross_section_type,
            original_simulation_box_size,
            preview_scale=preview_scale,
            debug_level=debug_level)

    return grid_size


# --------- Main function ----------------
def run_previewer(
        model='APS.xml',
        rms_data_file_name='rms_project_data_for_APS_gui.xml',
        rotate_plot=False,
        no_simulation=False,
        write_simulated_fields_to_file=False,
        plot_to_file=False,
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
        print('Backend: {}'.format(matplotlib.get_backend()))
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
    if apsModel.preview_resolution == 'High':
        use_high_resolution = True
    else:
        use_high_resolution = False

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
    # This script read the information about the grid model from a file that is previously written to disk
    # This can now be replaced by Roxar API functions instead:
    # TODO
    rmsData = APSDataFromRMS()
    if debug_level >= Debug.SOMEWHAT_VERBOSE:
        print('- Read file: {rms_data_file_name}'.format(rms_data_file_name=rms_data_file_name))
    rmsData.readRMSDataFromXMLFile(rms_data_file_name)
    [
        nxFromGrid, nyFromGrid, simBoxOrigoX, simBoxOrigoY, simBoxXsize, simBoxYsize, _, _, azimuthGridOrientation
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
    simBoxZsize = zoneModel.sim_box_thickness

    # The lengths of the simulation box taken from the RMS grid model
    original_simulation_box_size = (simBoxXsize, simBoxYsize, simBoxZsize)
    original_simulation_box_origin = (simBoxOrigoX, simBoxOrigoY)

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

    preview_grid_size = set2DGridDimension(
        nx, ny, nz, preview_cross_section.type,
        original_simulation_box_size,
        preview_scale=preview_scale,
        use_high_resolution=use_high_resolution,
        debug_level=debug_level
    )
    truncObject = zoneModel.truncation_rule
    faciesNames = zoneModel.facies_in_zone_model
    gaussFieldNamesInModel = zoneModel.used_gaussian_field_names
    gaussFieldIndxList = zoneModel.getGaussFieldIndexListInZone()
    nGaussFieldsInTruncRule = len(gaussFieldIndxList)
    if debug_level >= Debug.VERBOSE:
        print('Gauss fields in truncation rule:')
        for i in range(len(gaussFieldIndxList)):
            index = gaussFieldIndxList[i]
            print(f'Gauss field number {i + 1}:  {gaussFieldNamesInModel[index]}')

    assert len(gaussFieldNamesInModel) >= 2
    nFacies = len(faciesNames)

    if not zoneModel.use_constant_probabilities:
        print('Warning: Preview plots require constant facies probabilities')
        print('       Use arbitrary constant values')
    if debug_level >= Debug.SOMEWHAT_VERBOSE:
        print(f'\n ---------  Zone number : {zoneNumber} -----------------')
    faciesProb = np.zeros(nFacies, np.float32)
    for fName in faciesNames:
        pName = zoneModel.getProbParamName(fName)
        if zoneModel.use_constant_probabilities:
            v = float(pName)
            p = int(v * 1000 + 0.5)
            w = float(p) / 1000.0
            if debug_level >= Debug.SOMEWHAT_VERBOSE:
                print('Zone: ' + str(zoneNumber) + ' Facies: ' + fName + ' Prob: ' + str(w))
        else:
            v = 1.0 / float(nFacies)
            p = int(v * 1000 + 0.5)
            w = float(p) / 1000.0
            if debug_level >= Debug.SOMEWHAT_VERBOSE:
                print(f'Zone: {zoneNumber} Facies: {fName} Prob: {w}')
        faciesProb[i] = v

    # Calculate truncation map for given facies probabilities
    if debug_level >= Debug.SOMEWHAT_VERBOSE:
        print('Facies prob:')
        print(repr(faciesProb))
    truncObject.setTruncRule(faciesProb)

    # Write data structure:
    # truncObject.writeContentsInDataStructure()

    # Use original_simulation_box_size and not the rescaled lengths of the simulation box in the simulation
    # in order to get correct representation of trends and spatial correlations.
    gauss_field_items = zoneModel.simGaussFieldWithTrendAndTransform(
        original_simulation_box_size, preview_grid_size,
        azimuthGridOrientation, preview_cross_section, original_simulation_box_origin
    )

    grid2D_dimensions, increments = get_dimensions(
        preview_cross_section.type, preview_grid_size, original_simulation_box_size
    )
    facies, facies_fraction = create_facies_map(gauss_field_items, truncObject)

    if write_simulated_fields_to_file:
        x0 = 0.0
        y0 = 0.0
        if debug_level >= Debug.VERBOSE:
            print('Debug output: Write 2D simulated gauss fields:')
            for gaussian_field in gauss_field_items:
                file_name = gaussian_field.name + '_' + preview_cross_section.type.name + '.dat'
                writeFileRTF(file_name, gaussian_field.field, grid2D_dimensions, increments, x0, y0, debug_level=debug_level)
        writeFileRTF('facies2D.dat', facies, grid2D_dimensions, increments, x0, y0)

    if debug_level >= Debug.VERY_VERBOSE:
        facies_fraction_sorted = collections.OrderedDict(sorted(facies_fraction.items()))
        print('\nFacies name:   Simulated fractions:    Specified fractions:')
        for i, f in facies_fraction_sorted.items():
            fraction = float(f) / float(len(facies))
            print('{0:10}  {1:.3f}   {2:.3f}'.format(faciesNames[i], fraction, faciesProb[i]))
        print('')

    # Plot the result

    if debug_level >= Debug.SOMEWHAT_VERBOSE:
        print('Make plots')
    fig = plt.figure(figsize=[20.0, 10.0])

    # Figure containing the transformed Gaussian fields and facies realization
    plot_gaussian_fields(
        fig, gaussFieldIndxList, gauss_field_items,
        grid2D_dimensions, original_simulation_box_size,
        preview_cross_section,
        vertical_scale=preview_scale,
        azimuth_grid_orientation=azimuthGridOrientation
    )

    # Figure containing truncation map and facies

    colors = get_colors(nFacies)
    # Create the colormap
    cm = matplotlib.colors.ListedColormap(colors, name='Colormap', N=nFacies)
    bounds = np.linspace(0.5, 0.5 + nFacies, nFacies + 1)
    labels = faciesNames
    ax_trunc = plt.subplot(2, 6, 10)
    plot_truncation_map(truncObject, ax=ax_trunc, num_facies=nFacies, debug_level=debug_level)
    fmap = np.reshape(facies, grid2D_dimensions[::-1], 'C')  # Reshape to a 2D matrix (gridDim2 = nRows, gridDim1 = nColumns)
    # Facies map is plotted
    axFacies = plt.subplot(2, 6, 11)
    imFac = plot_facies(axFacies, fmap, nFacies, cm,
                        preview_cross_section.type,
                        original_simulation_box_size,
                        plot_ticks=True,
                        vertical_scale=preview_scale)

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
    nx_preview, ny_preview, nz_preview = preview_grid_size
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

    if plot_to_file:
        file_name = 'plot.pdf'
        fig.savefig(file_name)
        print('Finished creating plot: {}'.format(file_name))
        plt.close(fig)
    else:
        plt.show()
    print('Finished testPreview')


def get_dimensions(preview_cross_section_type, preview_grid_size, simulation_box_size):
    x_preview, y_preview, z_preview = preview_grid_size
    x_simulation, y_simulation, z_simulation = simulation_box_size
    if preview_cross_section_type == CrossSectionType.IJ:
        grid2D_dimensions = (x_preview, y_preview)
        increments = (x_simulation / x_preview, y_simulation / y_preview)
    elif preview_cross_section_type == CrossSectionType.IK:
        grid2D_dimensions = (x_preview, z_preview)
        increments = (x_simulation / x_preview, z_simulation / z_preview)
    elif preview_cross_section_type == CrossSectionType.JK:
        grid2D_dimensions = (y_preview, z_preview)
        increments = (y_simulation / y_preview, z_simulation / z_preview)
    else:
        raise ValueError("Invalid Cross Section Type ({})".format(preview_cross_section_type))
    return grid2D_dimensions, increments


def plot_truncation_map(truncation_rule, ax=None, fig=None, num_facies=None, facies_colors=None, title='Truncation Map', debug_level=Debug.OFF):
    if num_facies is None:
        num_facies = truncation_rule.num_facies_in_zone
    if ax is None:
        fig, ax = plt.subplots()
    if facies_colors is None:
        facies_colors = get_colors(num_facies)
    facies_ordering = truncation_rule.getFaciesOrderIndexList()

    # Calculate polygons for truncation map for current facies probability
    # as specified when calling setTruncRule(faciesProb)
    facies_polygons = truncation_rule.truncMapPolygons()
    facies_index_per_polygon = truncation_rule.faciesIndxPerPolygon()
    # Truncation map is plotted
    if debug_level >= Debug.SOMEWHAT_VERBOSE:
        print(
            'Number of facies:          {num_facies}\n'
            'Number of facies polygons: {num_polygons}'.format(num_facies=num_facies, num_polygons=len(facies_polygons))
        )
    for i in range(len(facies_polygons)):
        index = facies_index_per_polygon[i]
        facies_index = facies_ordering[index]
        poly = facies_polygons[i]
        polygon = Polygon(poly, closed=True, facecolor=facies_colors[facies_index])
        ax.add_patch(polygon)
    if title is not None:
        ax.set_title(title)
    ax.axes.set_axis_off()
    ax.set_aspect('equal', 'box')
    return fig, ax


def plot_gaussian_fields(fig, gauss_field_index_list, gauss_field_items, grid_dimension,
                         simulation_box_size, preview_cross_section, vertical_scale=1.0, azimuth_grid_orientation=None):
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
            gaussian_field, lengths=simulation_box_size, grid_dimensions=grid_dimension, ax=ax,
            plot_ticks=ticks, azimuth_grid_orientation=azimuth_grid_orientation, grid_index_order='C',vertical_scale=vertical_scale
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
    debug_level = get_debug_level(**kwargs)
    [kwargs.pop(item, None) for item in ['model', 'rms_data_file_name', 'debug_level']]
    plot_to_file = False
    run_previewer(model=model, rms_data_file_name=rms_data_file_name, plot_to_file=plot_to_file, debug_level=debug_level, **kwargs)


def get_arguments() -> Namespace:
    parser = get_argument_parser()
    args = parser.parse_args()
    args.debug_level = Debug(args.debug_level)
    return args


if __name__ == '__main__':
    args = get_arguments()
    run(**args.__dict__)
