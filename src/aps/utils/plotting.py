# -*- coding: utf-8 -*-
import numpy as np
import scipy
from matplotlib import pyplot as plt

from aps.utils.constants.simple import CrossSectionType


def plot_gaussian_field(
    simulation,
    lengths=None,
    grid_dimensions=None,
    ax=None,
    plot_ticks=True,
    rotate_plot=False,
    azimuth_grid_orientation=None,
    grid_index_order='C',
    vertical_scale=1.0,
):
    if ax is None:
        ax = plt.subplot(1, 1, 1)

    if simulation is None:
        # Used for compatibility with 'testPreviewer'
        assert grid_dimensions is not None
        assert lengths is not None
        alpha_realization = np.zeros(
            grid_dimensions[0] * grid_dimensions[1], np.float32
        )
        gauss_name = 'Not used'
        cross_section_type = CrossSectionType.IJ
        kwargs = _get_grid_kwargs(cross_section_type)
    else:
        gauss_name = simulation.name
        alpha_realization = simulation.field
        cross_section_type = simulation.cross_section.type
        grid_dimensions = get_grid_dimensions(cross_section_type, simulation)
        kwargs = _get_grid_kwargs(cross_section_type)

        lengths = simulation.simulation_box_size

    # Reshape to a 2D matrix where first index is row, second index is column
    alpha_map = resize_data_to_grid(
        alpha_realization, grid_dimensions, grid_index_order
    )

    if rotate_plot:
        assert azimuth_grid_orientation is not None
        alpha_map = scipy.ndimage.interpolation.rotate(
            alpha_map, azimuth_grid_orientation
        )

    extent, size = get_plot_sizing(cross_section_type, lengths, vertical_scale)
    im = ax.imshow(alpha_map, extent=extent, **kwargs)
    plt.axis(size)
    ax.set_title(gauss_name)

    if not plot_ticks:
        _hide_plot_ticks(ax)
    return im


def resize_data_to_grid(alpha_realization, grid_dimensions, grid_index_order):
    assert grid_index_order in ['F', 'C']
    alpha_map = np.reshape(alpha_realization, grid_dimensions[::-1], grid_index_order)
    return alpha_map


def _get_grid_kwargs(cross_section_type):
    kwargs = {'interpolation': 'none', 'aspect': 'equal', 'vmin': 0.0, 'vmax': 1.0}
    if cross_section_type == CrossSectionType.IJ:
        kwargs['origin'] = 'lower'
    elif cross_section_type in [CrossSectionType.IK, CrossSectionType.JK]:
        kwargs['origin'] = 'upper'
    else:
        raise ValueError(
            f'The cross section type, {cross_section_type}, does not exist'
        )
    return kwargs


def get_grid_dimensions(cross_section_type, simulation):
    if cross_section_type == CrossSectionType.IJ:
        # IJ
        grid_dimensions = (simulation.grid_size[0], simulation.grid_size[1])
    elif cross_section_type == CrossSectionType.IK:
        # IK
        grid_dimensions = (simulation.grid_size[0], simulation.grid_size[2])
    elif cross_section_type == CrossSectionType.JK:
        # JK
        grid_dimensions = (simulation.grid_size[1], simulation.grid_size[2])
    else:
        raise ValueError(
            'The cross section type, {}, does not exist'.format(cross_section_type)
        )
    return grid_dimensions


def cross_plot(ax, gaussian_field, other):
    # Plot crossplot between two specified gauss fields

    plt.scatter(gaussian_field.field, other.field, alpha=0.15, marker='.', c='b')
    title = 'Crossplot ' + gaussian_field.name + '  ' + other.name
    ax.set_title(title)
    ax.set_aspect('equal', 'box')
    plt.axis([0, 1, 0, 1])
    return ax


def plot_facies(
    ax,
    fmap,
    nFacies,
    cmap,
    previewCrossSectionType,
    lengths,
    plot_ticks=False,
    rotate_plot=False,
    azimuth_grid_orientation=None,
    vertical_scale=1.0,
):
    facies_map = fmap
    if rotate_plot:
        assert azimuth_grid_orientation is not None
        facies_map = scipy.ndimage.interpolation.rotate(fmap, azimuth_grid_orientation)

    kwargs = {
        'interpolation': 'none',
        'aspect': 'equal',
        'cmap': cmap,
        'clim': (1, nFacies),
        'origin': 'lower',
    }
    extent, size = get_plot_sizing_facies(
        previewCrossSectionType, lengths, vertical_scale
    )
    facies_plot = ax.imshow(facies_map, extent=extent, **kwargs)
    plt.axis(size)
    ax.set_title('Facies')
    if not plot_ticks:
        _hide_plot_ticks(ax)
    return facies_plot


def _hide_plot_ticks(ax):
    plt.setp(ax.get_xticklabels(), visible=False)
    plt.setp(ax.get_yticklabels(), visible=False)


def get_plot_sizing(cross_section_type, lengths, vertical_scale=1.0):
    x_length, y_length, z_length = lengths
    z_length_expanded = z_length * vertical_scale
    if cross_section_type == CrossSectionType.IJ:
        extent = (0.0, x_length, 0.0, y_length)
        size = [0.0, x_length, 0.0, y_length]
    elif cross_section_type == CrossSectionType.IK:
        extent = (0.0, x_length, z_length_expanded, 0.0)
        size = [0.0, x_length, z_length_expanded, 0.0]
    elif cross_section_type == CrossSectionType.JK:
        extent = (0.0, y_length, z_length_expanded, 0.0)
        size = [0.0, y_length, z_length_expanded, 0.0]
    else:
        raise ValueError('Invalid cross section type ({})'.format(cross_section_type))
    return extent, size


def get_plot_sizing_facies(cross_section_type, lengths, vertical_scale=1.0):
    x_length, y_length, z_length = lengths
    z_length_expanded = z_length * vertical_scale
    if cross_section_type == CrossSectionType.IJ:
        extent = (0.0, x_length, 0.0, y_length)
        size = [0.0, x_length, 0.0, y_length]
    elif cross_section_type == CrossSectionType.IK:
        extent = (0.0, x_length, 0.0, z_length_expanded)
        size = [0.0, x_length, z_length_expanded, 0.0]
    elif cross_section_type == CrossSectionType.JK:
        extent = (0.0, y_length, 0.0, z_length_expanded)
        size = [0.0, y_length, z_length_expanded, 0.0]
    else:
        raise ValueError('Invalid cross section type ({})'.format(cross_section_type))
    return extent, size
