/**
 * Mock of the rms.uipy object available in RMS 11
 */
import { rms as mock } from './roxar'
// eslint-disable-next-line no-undef
const api = typeof rms !== 'undefined' ? rms.uipy : mock.uipy

export default {
  gridModels: () => api.call('get_grid_model_names'),
  zones: (gridName) => api.call('get_zones', gridName),
  regionParameters: (gridName) => api.call('get_region_parameters', gridName),
  regions: (gridName, zoneName, regionParameter) => api.call('get_regions', gridName, zoneName, regionParameter),
  blockedWellParameters: (gridName) => api.call('get_blocked_well_set_names', gridName),
  blockedWellLogParameters: (gridName, blockedWellName) => api.call('get_blocked_well_logs', gridName, blockedWellName),
  facies: (gridName, blockedWellName, blockedWellLogName) => api.call('get_facies_table_from_blocked_well_log', gridName, blockedWellName, blockedWellLogName),
  truncationPolygons: (specification) => api.call('get_truncation_map_polygons', specification),
  trendParameters: (gridName) => api.call('get_rms_trend_parameters', gridName),
  probabilityCubeParameters: (gridName) => api.call('get_probability_cube_parameters', gridName),
  constants: (constantName, constantType) => api.call('get_constant', constantName, constantType),
  options: (name) => api.call('get_options', name),
  gridSize: (name) => api.call('get_grid_size', name),
  simulationBoxOrigin: (name) => api.call('get_simulation_box_size', name),
  simulateGaussianField: (field) => api.call('simulate_gaussian_field', field),
  simulateRealization: (fields, truncationRule) => api.call('simulate_realization', fields, truncationRule),
  averageProbabilityCubes: (gridName, probabilityCubeParameters, ZoneNumbers) => api.call('calculate_average_of_probability_cube', gridName, probabilityCubeParameters, ZoneNumbers),
  isApsModelValid: (fileContent) => api.call('is_aps_model_valid', fileContent),
}
