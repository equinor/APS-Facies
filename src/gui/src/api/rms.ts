/**
 * Mock of the rms.uipy object available in RMS 11
 */
import { AverageParameterProbabilities, CodeName, Constants, PolygonDescription, SimulationBoxSize } from '@/api/types'
import { TruncationRuleDescription } from '@/utils'
import { GaussianRandomFieldSpecification } from '@/utils/domain/gaussianRandomField'
import { Optional } from '@/utils/typing'

import { rms as mock } from './roxar'
/* eslint-disable @typescript-eslint/ban-ts-ignore */
// @ts-ignore
const api = typeof rms !== 'undefined' ? rms.uipy : mock.uipy

export default {
  projectName: (): Promise<string> => api.call('get_project_name'),
  projectDirectory: (): Promise<string> => api.call('get_project_dir'),
  fmuParameterList: (): Promise<string> => api.call('get_fmu_parameter_list_dir'),
  currentWorkflowName: (): Promise<string> => api.call('get_current_workflow_name'),
  gridModels: (): Promise<{ name: string, exists: boolean}[]> => api.call('get_grid_model_names'),
  zones: (gridName: string): Promise<string[]> => api.call('get_zones', gridName),
  regionParameters: (gridName: string): Promise<string[]> => api.call('get_region_parameters', gridName),
  regions: (gridName: string, zoneName: string, regionParameter: string): Promise<CodeName[]> => api.call('get_regions', gridName, zoneName, regionParameter),
  blockedWellParameters: (gridName: string): Promise<string[]> => api.call('get_blocked_well_set_names', gridName),
  realizationParameters: (gridName: string): Promise<string[]> => api.call('get_realization_parameters', gridName),
  blockedWellLogParameters: (gridName: string, blockedWellName: string): Promise<string[]> => api.call('get_blocked_well_logs', gridName, blockedWellName),
  facies: (gridName: string, blockedWellName: string, blockedWellLogName: string): Promise<CodeName[]> => api.call('get_facies_table_from_blocked_well_log', gridName, blockedWellName, blockedWellLogName),
  truncationPolygons: <T extends TruncationRuleDescription>(specification: T): Promise<PolygonDescription[]> => api.call('get_truncation_map_polygons', specification),
  trendParameters: (gridName: string): Promise<string[]> => api.call('get_rms_trend_parameters', gridName),
  probabilityCubeParameters: (gridName: string): Promise<string[]> => api.call('get_probability_cube_parameters', gridName),
  constants: (constantName: string, constantType: string): Promise<Constants> => api.call('get_constant', constantName, constantType),
  options: (name: string): Promise<string[]> => api.call('get_options', name),
  gridSize: (name: string): Promise<number[]> => api.call('get_grid_size', name),
  simulationBoxOrigin: (name: string, rough = false): Promise<SimulationBoxSize> => api.call('get_simulation_box_size', name, rough),
  simulateGaussianField: (field: GaussianRandomFieldSpecification): Promise<number[][]> => api.call('simulate_gaussian_field', field),
  simulateRealization: (fields: GaussianRandomFieldSpecification[], truncationRule: TruncationRuleDescription): Promise<number[][]> => api.call('simulate_realization', fields, truncationRule),
  averageProbabilityCubes: (gridName: string, probabilityCubeParameters: string, zoneNumber: number, regionParameter: Optional<string> = null, regionNumber: Optional<number> = null): Promise<AverageParameterProbabilities> => api.call('calculate_average_of_probability_cube', gridName, probabilityCubeParameters, zoneNumber, regionParameter, regionNumber),
  openWikiHelp: (): Promise<void> => api.call('open_wiki_help'),
  isApsModelValid: (fileContent: string): Promise<{ valid: boolean, error: string }> => api.call('is_aps_model_valid', fileContent),
  save: (path: string, content: string, prettify = true): Promise<boolean> => api.call(prettify ? 'save_model' : 'save_file', path, content),
  // @ts-ignore
  chooseDir: (mode: string, suggestion = ''): Promise<string> => typeof rms !== 'undefined' ? rms.chooseDir(mode, suggestion) : new Promise((resolve, reject) => resolve(null)),
  // @ts-ignore
  chooseFile: (mode: string, filter: string, suggestion = ''): Promise<string> => typeof rms !== 'undefined' ? rms.chooseFile(mode, filter, suggestion) : new Promise((resolve, reject) => resolve(null)),
}
