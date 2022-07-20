"""Sample a map to a 3D grid (zone) so the e.g. a map trend can be taken in.

JRIV/OLIA
"""
import numpy as np
import xtgeo
from aps.utils.constants.simple import Debug, GridModelConstants

def check_existence_of_map(project, zone_name, map_name):
    exists = False
    if zone_name in project.zones:
        if map_name in project.zones[zone_name]:
            surface = project.zones[zone_name][map_name] 
            if surface:
                if not surface.is_empty():
                    exists = True
    return exists


def trend_map_to_grid_param(project, grid_model_name, trend_map_name, zone_name,
    result_param_name, zone_number=1,
    zone_param_name=GridModelConstants.ZONE_NAME, debug_level=Debug.OFF):

    grid, zone_param = _read_grid(project, grid_model_name, zone_param_name)
    grid, grid_points, kminmax = _derive_gridcells_points(grid, zone_param, zone_number)
    grid_points = _snap_points_to_surface(project, grid_points, trend_map_name, zone_name)
    if debug_level >= Debug.VERBOSE:
        print(
            f"-- Create temporary 3D parameter {result_param_name} as trend "
            f"using 2D trend map {trend_map_name} for zone {zone_number}"
        )
    _create_property_and_store(project, grid_model_name, grid, grid_points, kminmax, result_param_name)

def _read_grid(project, grid_model_name, zone_param_name):
    """Read 3D grid and zone property"""

    grd = xtgeo.grid_from_roxar(project, grid_model_name)
    zone = xtgeo.gridproperty_from_roxar(project, grid_model_name, zone_param_name)
    return grd, zone


def _derive_gridcells_points(grd, zone, zoneno):
    """Derive XYZ locations from grid (zone) as a Point set."""

    # find mid K index for given zone
    indices = np.where(zone.values == zoneno)
    kind_avg = int(indices[2].mean())
    kminmax = [int(indices[2].min()), int(indices[2].max())]  # range for K

    dfr = grd.get_dataframe(activeonly=False)
    # filter dataframe so it gets only for kind_avg
    dfr = dfr.loc[dfr["KZ"] == kind_avg].reset_index()
    dfr = dfr[["X_UTME", "Y_UTMN", "Z_TVDSS", "IX", "JY"]]

    gpoints = xtgeo.Points()
    gpoints.dataframe = dfr
    gpoints.zname = "VAL"

    return grd, gpoints, kminmax


def _snap_points_to_surface(project, gpoints, trend_map_name, zone_name):
    """Take the pointset and snap the Z values to the trend map."""
    surf = xtgeo.surface_from_roxar(project, zone_name, trend_map_name,
        stype='zones',realisation=project.current_realisation)
    gpoints.snap_surface(surf)

    return gpoints


def _create_property_and_store(project, grid_model_name, grid, gridpoints, kminmax, result_param_name):
    """Create the property by some clever numpy mapping."""

    ixn = gridpoints.dataframe["IX"].values.astype("int") - 1  # -1 since df has 1 based index
    jyn = gridpoints.dataframe["JY"].values.astype("int") - 1
    zvalues = gridpoints.dataframe["VAL"].values

    try:
        newprop = xtgeo.gridproperty_from_roxar(project, grid_model_name, result_param_name,
            realisation=project.current_realisation)
    except ValueError as verror:
        if "No property in" in str(verror) or "The requested grid property has no data." in str(verror):
            newprop = xtgeo.GridProperty(grid)
        else:
            raise
    krange = np.linspace(kminmax[0], kminmax[1], kminmax[1] - kminmax[0] + 1, dtype=np.int)

    for klay in krange:
        newprop.values[ixn, jyn, klay] = zvalues

    newprop.to_roxar(project, grid_model_name, result_param_name)


