import rmsapi
import rmsapi.jobs
import numpy as np
import math

# import xtgeo
import shutil
from os.path import isdir

rms_project_name = 'aps_test.rmsxxx'

# Delete existing rms project before re-create it
if isdir(rms_project_name):
    print(f'Remove existing project: {rms_project_name}')
    shutil.rmtree(rms_project_name)

# Create new RMS project
print('Create rms project')

project = rmsapi.Project.create()
# rox = xtgeo.RoxUtils(project)
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

xinc = 50.0
yinc = 50.0

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
    'XInc': 50.0,
    'YInc': 50.0,
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

# Zone parameter
grid_model.properties.create("Zone",
        property_type=rmsapi.GridPropertyType.discrete,
        data_type=np.uint8)
grid = grid_model.get_grid()
dimensions = grid.simbox_indexer.dimensions
nx, ny, nz = dimensions
zonation = grid.get_zonation()

# Define zone parameter values
zone_values3d = np.zeros(dimensions,dtype=np.uint8)
zone_number = 1
code_names = {}
for start_layer, zone_name in zonation.items():
    zone_values3d[:,:,start_layer:] = zone_number
    code_names[zone_number] = zone_name
    zone_number += 1
zone_values = zone_values3d.reshape(len(zone_values3d))
grid_model.properties["Zone"].set_values(zone_values)
zone_property = grid_model.properties["Zone"]
zone_property.code_names = code_names

print('Save rms project and close')
project.save_as(rms_project_name)
project.close()
