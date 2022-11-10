#!/bin/env python
# -*- coding: utf-8 -*-
# This module is used in FMU workflows to export gaussian field values to disk to be read by ERT. 
# Here we can assume that the project.current_realisation = 0 always since FMU ONLY run with one 
# realization in the RMS project and should have shared grid and shared parameters only.

import xtgeo
import roxar
import numpy as np
from roxar import Direction

from aps.algorithms.APSModel import APSModel
from aps.utils.fmu import get_export_location
from aps.utils.roxar.grid_model import flip_grid_index_origo
from aps.utils.methods import get_specification_file, get_debug_level
from aps.utils.constants.simple import Debug


def run(project, **kwargs):
    ''' Export simulated GRF fields from ERTBOX grid to file readable by ERT
    '''
    if project.current_realisation > 0:
        raise ValueError(f'In RMS models to be used with a FMU loop in ERT,'
                         'the grid and parameters should be shared and realisation = 1'
        )
    fmu_mode = kwargs.get('fmu_mode', False)
    if not fmu_mode:
        raise ValueError(f'The export of GRF is only available in FMU mode with AHM')
    debug_level = get_debug_level(**kwargs)
    model_file = get_specification_file(**kwargs)
    aps_model = APSModel(model_file)
    fmu_grid_name = kwargs.get('fmu_simulation_grid_name')
    file_format = kwargs.get('field_file_format')

    print(f"Export 3D parameter files from {fmu_grid_name}")

    # Get the ERTBOX grid from RMS
    fmu_grid_model = project.grid_models[fmu_grid_name]
    if fmu_grid_model.is_empty(project.current_realisation):
        raise ValueError(f'Grid model for ERTBOX grid: {fmu_grid_name} is empty for realization {project.current_realisation}.')
    grid3D = fmu_grid_model.get_grid(project.current_realisation)

    # For ERTBOX grid the simulation box dimensions from simbox_indexer and grid_indexer are the same.
    indexer = grid3D.simbox_indexer
    nx, ny, nz  = indexer.dimensions
    handedness = indexer.ijk_handedness

    field_location = kwargs.get('save_dir', None)
    if field_location is None:
        field_location = get_export_location()

    # Loop over all GRF's used in the APS zone model for the current zone
    # and save the simulated GRF to file
    # The simbox_indexer is used and there are only one zone in ERTBOX
    # grid which is re-used for all geomodel grid zones

    # Loop over all zones defined in aps model
    for zone in aps_model.zone_models:
        if aps_model.isSelected(zone.zone_number,0):
            for field_name in zone.gaussian_fields_in_truncation_rule:
                field_properties = fmu_grid_model.properties
                field_property = None
                if field_name in field_properties:
                    field_property = field_properties[field_name]
                    if field_property.is_empty(project.current_realisation):
                        raise ValueError(f'The parameter {field_name} is empty in grid model {fmu_grid_name}')
                else:
                    raise ValueError(f'The parameter  {field_name} does not exist in grid model {fmu_grid_name}')

                file_name = str(field_location / f'{field_name}.{file_format}')
                if debug_level >= Debug.VERY_VERBOSE:
                    print(f'--- Write parameter: {field_name} to file {file_name}')

                if file_format.upper() == 'ROFF':
                    # Use ROFF Binary
                    field_properties.save(file_name, field_name, format=roxar.FileFormat.ROFF_BINARY)
                else:
                    # Use xtgeo for other formats not available from roxar.grids
                    values = field_property.get_values(project.current_realisation)
                    # The current grid model is ERTBOX grid model where all cells are active
                    # Flip the order of the values to be consistent with right-handed if the
                    values3d = np.reshape(values, (nx, ny, nz))

                    if handedness == Direction.right:
                        # Current grid model is right-handed
                        # Need to flip order of the values to get correct export
                        # when using GRDECL format with xtgeo.GridProperty instance
                        values3d_flipped = flip_grid_index_origo(values3d, ny)

                        xtgeo_object = xtgeo.GridProperty(
                            ncol=nx, nrow=ny, nlay=nz,
                            values=values3d_flipped,
                            name=field_name,
                        )
                    else:
                        xtgeo_object = xtgeo.GridProperty(
                            ncol=nx, nrow=ny, nlay=nz,
                            values=values3d,
                            name=field_name,
                        )

                    xtgeo_object.to_file(
                        file_name,
                        fformat=file_format,
                        name=field_name,
                    )
