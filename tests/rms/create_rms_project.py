import rmsapi
import rmsapi.jobs
import numpy as np
import math
from typing import Any, Union
import xtgeo
import shutil
from os.path import isdir
from aps.utils.roxar.grid_model import create_zone_parameter
from aps.utils.constants.simple import Debug

 
def create_wells(
        project: Any,
        nwells: int,
        well_name_prefix: str,
        well_pos: list[tuple[float, float, float, float]],
        nlogpoints: int,
        facies_code_names: dict[int, str],
        facies_intervals: list[list[tuple[float,int]]],
        well_is_vertical: list[bool],
        debug_level: Debug=Debug.OFF
) -> list[str]:
    
    well_list = []
    well_names = []
    for well_indx in range(nwells):
        # well head and name
        well_name = f"{well_name_prefix}_{well_indx}"
        well_names.append(well_name)
        if debug_level > Debug.OFF:
            print(f"Create well:  {well_name}")
        well = project.wells.create(well_name)
        well.rkb = 100
        east = well_pos[well_indx][0]
        north = well_pos[well_indx][1]
        topdepth = well_pos[well_indx][2]
        basedepth = well_pos[well_indx][3]
        npoints = nlogpoints
        loginc = (basedepth - topdepth) / npoints
        well.well_head = (east, north)

        if well_is_vertical[well_indx]:
            # trajectory
            trajectories = well.wellbore.trajectories
            drilled_trajectory = trajectories.create("Drilled trajectory")
            surveypoints = drilled_trajectory.survey_point_series
            array_with_points = surveypoints.generate_survey_points(npoints)
            array_with_points[:, 0] = np.arange(topdepth, basedepth, loginc)
            array_with_points[:, 3].fill(east)
            array_with_points[:, 4].fill(north)
            array_with_points[:, 5] = np.arange(topdepth, basedepth, loginc)  # TVD
            surveypoints.set_survey_points(array_with_points)

            # log curves
            log_run = drilled_trajectory.log_runs.create("Log run 1")
            measured_depths = np.arange(
                topdepth, basedepth, loginc
            )  # MD points for log values
            log_run.set_measured_depths(measured_depths)
            nval = len(measured_depths)

            facies_log_curve = log_run.log_curves.create_discrete("FACIES")
            facies_values = np.zeros(nval, dtype=np.int32)

            start_indx = 0
            for interval in facies_intervals[well_indx]:
                md_length, facies_code = interval
                facies_values[start_indx:] = facies_code
                indx_interval = int(md_length/loginc)
                start_indx += indx_interval

            facies_log_curve.set_values(facies_values)
            code_names = facies_code_names
            facies_log_curve.set_code_names(code_names)
        else:
            # trajectory
            trajectories = well.wellbore.trajectories
            drilled_trajectory = trajectories.create("Drilled trajectory")
            surveypoints = drilled_trajectory.survey_point_series



            points = [
                # X            Y          TVD         MD         INCL         AZIMUTH
                [1114.589,	-381.262,	2028.272],
                [-1364.837,	413.633,	2105.073]
            ]
            npoints = len(points)
            array_with_points = surveypoints.generate_survey_points(npoints)
            # Calculate MD
            x0, y0, z0 = points[0]
            md_rel = 0.0
            for indx in range(npoints):
                pt = points[indx]
                x = pt[0]
                y = pt[1]
                z = pt[2]
                dx = x - x0
                dy = y - y0
                dz = z - z0
                d = math.sqrt(dx*dx + dy*dy + dz*dz)
                md_rel += d
                array_with_points[indx, 0] = md_rel  # MD
                array_with_points[indx, 3] = x  # X
                array_with_points[indx, 4] = y  # Y
                array_with_points[indx, 5] = z  # TVD
                array_with_points[indx, 1] = 89.0  # INCL
                array_with_points[indx, 2] = 300.0  # AXIMUTH
                x0 = x
                y0 = y
                z0 = z
                print(f"MD: {md_rel}")
            surveypoints.set_survey_points(array_with_points)
            md_max = array_with_points[npoints-1, 0]
            md_min = array_with_points[0, 0]
            md = np.arange(md_min,md_max, 25.0)
            npoints_new = len(md)
            new_array_with_points = np.zeros((npoints_new,6), dtype=np.float32)
            for n in range(len(md)):
                d = md[n]
                new_array_with_points[n,:] = surveypoints.interpolate_survey_point(d)
            surveypoints.set_survey_points(new_array_with_points)

            # log curves
            log_run = drilled_trajectory.log_runs.create("Log run 1")
            measured_depths = np.arange(
                md_min, md_max, loginc
            )  # MD points for log values
            log_run.set_measured_depths(measured_depths)
            nval = len(measured_depths)

            facies_log_curve = log_run.log_curves.create_discrete("FACIES")
            facies_values = np.zeros(nval, dtype=np.int32)

            start_indx = 0
            for interval in facies_intervals[well_indx]:
                md_length, facies_code = interval
                facies_values[start_indx:] = facies_code
                indx_interval = int(md_length/loginc)
                start_indx += indx_interval

            facies_log_curve.set_values(facies_values)
            code_names = facies_code_names
            facies_log_curve.set_code_names(code_names)

    well_list.append(well)

    return well_names


def create_bw_job(
    owner_strings: list[str],
    job_type: str,
    job_name: str,
    well_names: list[str],
    bw_set_name: str,
    debug_level: Debug = Debug.OFF,
):
    bw_job = rmsapi.jobs.Job.create(owner=owner_strings, type=job_type, name=job_name)

    params = {
        "BlockedWellsName": bw_set_name,
        "Discrete Blocked Log": [
            {
                "Name": "FACIES",
                "CellLayerAveraging": False,
            },
        ],
        "Wells": [["Wells", well_name] for well_name in well_names],
    }
    check, err_list, warn_list = bw_job.check(params)
    if not check:
        print("Error when creating blocked well job:")
        for i in range(len(err_list)):
            print(f"  {err_list[i]}")
        print("Warnings when creating blocked well job:")
        for i in range(len(warn_list)):
            print(f"  {warn_list[i]}")

    if debug_level > Debug.OFF:
        print(
            f"Create block well job:  {job_name} to make blocked well set: "
            f"{bw_set_name}"
        )
        print(f"Use the wells: {well_names}")

    bw_job.set_arguments(params)
    bw_job.save()

    return bw_job


rms_project_name = 'aps_test.rmsxxx'

# Delete existing rms project before re-create it
if isdir(rms_project_name):
    print(f'Remove existing project: {rms_project_name}')
    shutil.rmtree(rms_project_name)

# Create new RMS project
print('Create rms project')

project = rmsapi.Project.create()
print('Create empty structural model object')
struct_model_name = 'StructModel'
model_box_center = (0.0, 0.0, -2045.0)  # Negative depth due to bug in rmsapi
rms_box = model_box_center
model_box_size = (1500.0, 2500.0, 200.0)

x0 = rms_box[0] - 0.5 * model_box_size[0]
y0 = rms_box[1] - 0.5 * model_box_size[1]
z0 = rms_box[2]  # Have to switch sign due to a bug in rmsapi
print(f'Origo:  ({x0}, {y0}, {z0})')
model_box_origin = (x0, y0, z0)

xinc = 10.0
yinc = 10.0

nx_surf = int(model_box_size[0] / xinc) + 1
ny_surf = int(model_box_size[1] / yinc) + 1
print(f'nx,ny for surfaces:  ({nx_surf}, {ny_surf})')

model_box_rotation = -45.0  # Rotation is clockwise for model box
struct_model = project.structural_models.create(struct_model_name)
struct_model.set_model_box(model_box_center, model_box_size, model_box_rotation)
model_box = struct_model.get_model_box()

print('Get name of initially create horizon model')
struct_models_list = list(project.structural_models.keys())

print(f'Structural models: {struct_models_list}')
horizon_models_list = list(
    project.structural_models[struct_model_name].horizon_models.keys()
)

print(f'Horizon models for the struct model:  {horizon_models_list}')
horizon_model = project.structural_models[struct_model_name].horizon_models[
    'Horizon model 1'
]

print(f'Rename horizon model to: {horizon_model}')
horizon_model_name = 'HorizonModel'
horizon_model.name = horizon_model_name

horizon_model.set_model_box(model_box_center, model_box_size, model_box_rotation)

# Define surface data for use in horizon modelling
surface_names = ['TopErosion', 'TopA', 'TopB', 'TopC', 'BaseC']
zone_names = ['AboveA', 'A', 'B', 'C']
# Create a horizon data type for surface data
surf_representation = project.horizons.representations.create(
    'DepthSurface', rmsapi.GeometryType.surface, rmsapi.VerticalDomain.depth
)


# Create horizon surface
surfaces = []
for i, name in enumerate(surface_names):
    horizon = project.horizons.create(name, rmsapi.HorizonType.calculated)
    surface = project.horizons[horizon.name][surf_representation.name]
    surfaces.append(surface)

# Create a surface grids and assign grid values
surface_grids = []
# Calculate position of new origin for surface maps when modelling box is rotated
# since the modelling box is rotated around the center point not the
# lower left corner as the surface
x0_rel = x0 - rms_box[0]
y0_rel = y0 - rms_box[1]
angle = model_box_rotation * math.pi / 180.0
cosangle = math.cos(angle)
sinangle = math.sin(angle)
x0_rotated = cosangle * x0_rel + sinangle * y0_rel + rms_box[0]
y0_rotated = -sinangle * x0_rel + cosangle * y0_rel + rms_box[1]

nsurfaces = len(surface_names)
for n in range(nsurfaces):
    surface_grid = rmsapi.RegularGrid2D.create(
        x_origin=x0_rotated,
        y_origin=y0_rotated,
        i_inc=xinc,
        j_inc=yinc,
        ni=nx_surf,
        nj=ny_surf,
        rotation=-model_box_rotation,
    )  # Counter clockwise

    values = surface_grid.get_values()
    if n == 0:
        # Erosion surface
        for j in range(ny_surf):
            for k in range(nx_surf):
                values[k, j] = 1985 + 50 * j * k / (nx_surf * ny_surf)
                # values[k,j] = k + j*nx_surf

    elif n < (nsurfaces-1):
        for j in range(ny_surf):
            for k in range(nx_surf):
                # Constant surface
                values[k, j] = (
                    1980 + n * 25 + 30 * (ny_surf - j) * k / (nx_surf * ny_surf)
                )
    else:
        # Base surface
        for j in range(ny_surf):
            for k in range(nx_surf):
                # Constant surface
                values[k, j] = (
                    1980 + n * 25 + 5 * (ny_surf - j) * k / (nx_surf * ny_surf)
                )

    surface_grid.set_values(values)
    surface = surfaces[n]
    print(f'Create surface: {surface_names[n]}')
    surface.set_grid(surface_grid)

# Create a horizon data type for polygon data
poly_representation = project.horizons.representations.create(
    'DepthPolygon', rmsapi.GeometryType.polylines, rmsapi.VerticalDomain.depth
)

# Create polyline
line = np.array(
    [
        [597.653137, 438.980377, 2000.000000],
        [177.211502, 583.722656, 2000.000000],
        [-174.305557, 935.239746, 2000.000000],
        [-422.435242, 1052.412109, 2000.000000],
        [-649.887268, 1004.164673, 2000.000000],
        [-1001.404297, 700.895020, 2000.000000],
        [-980.726807, 115.033424, 2000.000000],
        [-601.640015, -284.730957, 2000.000000],
        [-491.360046, -525.968140, 2000.000000],
        [-188.090622, -739.635254, 2000.000000],
        [4.899200, -1015.334961, 2000.000000],
        [452.910950, -1173.862061, 2000.000000],
        [756.180603, -849.915161, 2000.000000],
        [615.010925, -496.340576, 2000.000000],
        [1101.245605, -315.739105, 2000.000000],
        [823.397278, 45.463821, 2000.000000],
        [667.613525, 317.828186, 2000.000000],
        [625.611328, 401.832397, 2000.000000],
        [597.653137, 438.980377, 2000.000000],
    ]
)

# Assign polygon data to the first Horizon
project.horizons[surface_names[0]]['DepthPolygon'].set_values([line])

# Define job to create horizon model
job_owner = ['Structural models', struct_model_name, horizon_model.name]
job_type = 'Horizon Modeling'
job_name = 'HorizonJob'
horizon_job = rmsapi.jobs.Job.create(job_owner, job_type, job_name)

params = {
    'AlgVersion': 'STANDARD',
    'InputData': [['Horizons', 'DepthSurface']],
    'Layer Model': [
        {},  # overburden
        {
            'Horizon Parameters': [
                {
                    'Type': 'UNCONFORMITY',
                    'ConformalCorrectionRange': 400,
                    'GridXYIncrement': 50,
                    'HardDataCorrectionRange': 300,
                    'Horizon': ['Horizons', surface_names[0]],
                    'InputDataUsage': ['SOFT'],
                    'SoftDataSmoothingRange': 200,
                }
            ]
        },
        {
            'Horizon Parameters': [
                {
                    'ConformalCorrectionRange': 400,
                    'GridXYIncrement': 50,
                    'HardDataCorrectionRange': 300,
                    'Horizon': ['Horizons', surface_names[1]],
                    'InputDataUsage': ['SOFT'],
                    'SoftDataSmoothingRange': 200,
                }
            ]
        },
        {
            'Horizon Parameters': [
                {
                    'ConformalCorrectionRange': 400,
                    'GridXYIncrement': 50,
                    'HardDataCorrectionRange': 300,
                    'Horizon': ['Horizons', surface_names[2]],
                    'InputDataUsage': ['SOFT'],
                    'SoftDataSmoothingRange': 200,
                }
            ]
        },
        {
            'Horizon Parameters': [
                {
                    'ConformalCorrectionRange': 400,
                    'GridXYIncrement': 50,
                    'HardDataCorrectionRange': 300,
                    'Horizon': ['Horizons', surface_names[3]],
                    'InputDataUsage': ['SOFT'],
                    'SoftDataSmoothingRange': 200,
                }
            ]
        },
        {
            'Horizon Parameters': [
                {
                    'ConformalCorrectionRange': 400,
                    'GridXYIncrement': 50,
                    'HardDataCorrectionRange': 300,
                    'Horizon': ['Horizons', surface_names[4]],
                    'InputDataUsage': ['SOFT'],
                    'SoftDataSmoothingRange': 200,
                }
            ]
        },
    ],
    'SurfaceVisualizationResolution': 50,
}
horizon_job.set_arguments(params)
horizon_job.save()
print(f'Run job: {horizon_job.name}')
horizon_job.execute()

# Build grid
grid_model_name = 'GridModel'
print(f'Create grid model:  {grid_model_name}')
grid_model = project.grid_models.create(grid_model_name)
grid = grid_model.get_grid()
job_owner = ['Grid models', grid_model_name, 'Grid']
job_type = 'Create Grid'
job_name = 'Create_grid'
print(f'Create grid job:  {job_name}')
grid_job = rmsapi.jobs.Job.create(job_owner, job_type, job_name)
params = {
    'AirHorizons': [True, False, False, False, False],
    'BottomSurfaces': [[], [], [], []],
    'UseXInc': True,
    'UseYInc': True,
    'XInc': xinc,
    'YInc': yinc,
    'CellsPerZone': [-1, 15, 10, 25],
    'ClearExistingData': True,
    'ClipGrid': True,
    'ClipPolygon': ['Horizons', surface_names[0], 'DepthPolygon'],
    'ConformalMode': [2, 2, 0, 1], # Baseconform, BaseConform, Proportional,TopConform
    'FaultStateMap': [[]],
    'HorizonModel': ['Structural models', struct_model.name, horizon_model.name],
    'JuxtapositionCorrection': False,
    'LayerThickness': [2, 2, 10, 2],
    'XLength': model_box_size[0],
    'YLength': model_box_size[1],
    'Origin': [model_box_center[0], model_box_center[1]],
    'RegularizedGrid': False,
    'RepeatSections': False,
    'Rotation': model_box_rotation,
    'SampledHorizons': [False, False, False, False, False],
    'TopSurfaces': [[], [], [], []],
    'Truncated': [False, False, False, False],
    'UseBottomSurface': [False, False, False, False],
    'UseTopSurface': [False, False, False, False],
    'UsedHorizons': [True, True, True, True, True],
    'ZoneNames': zone_names,
    'VerticalBoundary': False,
}


grid_job.set_arguments(params)
grid_job.save()
print(f'Run grid job: {job_name}')
ok = grid_job.execute(0)

# Define zone parameter values
zone_param = create_zone_parameter(
    grid_model,
    name="Zone")

# Define some wells
nwells = 4
well_name_prefix = "Well"
well_pos = [
        (-635, 360, 1990, 2100),
        (250, -730,1990, 2100),
        (-500, -170, 1990, 2100),
        (-618.455,     856.018,   1990,   2120.0),
    ]
well_is_vertical =[True, True, True, False]
nlogpoints = 1000
facies_code_names = {
    1: "F1",
    2: "F2",
    5: "F5",
    6: "F6",
}
facies_intervals = [
        [
        (5.0,  1),
        (15.0, 2),
        (15.0, 1),
        (25.0, 6),
        (5.0,  1),
        (5.0,  5),
        (15.0, 6),
        (15.0, 2),
        (25.0, 6),
        (15.0, 2),
        (5.0,  1),
        ],
        [
        (7.0,  2),
        (15.0, 1),
        (10.0, 5),
        (5.0,  6),
        (10.0, 1),
        (10.0,  2),
        (10.0, 5),
        (15.0, 2),
        (15.0, 6),
        (5.0, 1),
        (5.0,  2),
        ],
        [
        (15.0,  2),
        (5.0, 1),
        (15.0, 2),
        (25.0, 5),
        (5.0,  6),
        (5.0,  5),
        (15.0, 6),
        (5.0,  2),
        (15.0, 1),
        (15.0, 2),
        (5.0,  1),
        ],
        [
        (50.0,  2),
        (25.0, 1),
        (135.0, 2),
        (450.0, 5),
        (550.0,  6),
        (150.0,  5),
        (350.0, 6),
        (150.0,  2),
        (250.0, 1),
        (450.0, 2),
        (250.0,  5),
        (150.0,  2),
        (350.0,  1),
        (250.0,  5),
        ],
]
well_list = create_wells(
        project,
        nwells,
        well_name_prefix,
        well_pos,
        nlogpoints,
        facies_code_names,
        facies_intervals,
        well_is_vertical,
        debug_level=Debug.ON)

owner_strings = ["Grid models", grid_model_name, "Grid"]
bw_job =create_bw_job(
        owner_strings,
        "Block Wells",
        "BW_job",
        well_list,
        "BW",
        debug_level=Debug.ON)
bw_job.execute()


print('Save rms project and close')
project.save_as(rms_project_name)
project.close()
