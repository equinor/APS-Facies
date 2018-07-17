/**
 * Mock of the demo project 'Emerald_10_1.pro'
 */
import {rms as mock} from './roxar'
// eslint-disable-next-line no-undef
const api = typeof rms !== 'undefined' ? rms.uipy : mock.uipy

export default {
  gridModels: () => api.call('get_grid_model_names'),
  zoneParameters: (gridName) => api.call('get_zone_parameters', gridName),
  zones: (gridName, zoneParameter) => api.call('get_zones', gridName, zoneParameter),
  regionParameters: (gridName) => api.call('get_region_parameters', gridName),
  regions: (gridName, zoneName, regionParameter) => api.call('get_regions', gridName, zoneName, regionParameter),
  blockedWellParameters: (gridName) => api.call('get_blocked_well_set_names', gridName),
  blockedWellLogParameters: (gridName, blockedWellName) => api.call('get_blocked_well_logs', gridName, blockedWellName),
  facies: (gridName, blockedWellName, blockedWellLogName) => api.call('get_facies_table_from_blocked_well_log', gridName, blockedWellName, blockedWellLogName),
}
