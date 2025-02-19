/**
 * Mock of the rms.uipy object available in RMS 11
 */
import type {
  AverageParameterProbabilities,
  CodeName,
  RmsFacies,
  Constants,
  PolygonDescription,
  SimulationBoxSize,
  RmsGridModel,
  Paths,
  Job,
} from '@/api/types'
import type { TruncationRuleDescription } from '@/utils'
import type { GaussianRandomFieldSpecification } from '@/utils/domain/gaussianRandomField'
import type { ZoneConfiguration } from '@/utils/domain/zone'
import type { Optional } from '@/utils/typing'

import { rms as mock } from './roxar'
import type { PolygonSpecification } from '@/utils/domain/polygon/base'
import type { ProbabilityCube } from '@/utils/domain/facies/local'
const api = (typeof rms !== 'undefined' ? rms.uipy : mock.uipy) as {
  call: <T>(name: string, ...args: any[]) => Promise<T>
}

export default {
  projectName: (): Promise<string> => api.call('get_project_name'),
  projectDirectory: (): Promise<string> => api.call('get_project_dir'),
  rmsVersion: (): Promise<string> => api.call('get_rms_version'),
  fmuParameterList: (): Promise<string> =>
    api.call('get_fmu_parameter_list_dir'),
  currentWorkflowName: (): Promise<string> =>
    api.call('get_current_workflow_name'),
  gridModels: (): Promise<RmsGridModel[]> => api.call('get_grid_models'),
  createErtBoxGrid: (
    gridNameGeo: string,
    gridNameErtBox: string,
    nLayers: Optional<number>,
    debugLevel: number,
  ): Promise<boolean> =>
    api.call(
      'create_ertbox_grid',
      gridNameGeo,
      gridNameErtBox,
      nLayers,
      debugLevel,
    ),
  zones: (gridName: string): Promise<ZoneConfiguration[]> =>
    api.call('get_zones', gridName),
  regionParameters: (gridName: string): Promise<string[]> =>
    api.call('get_region_parameters', gridName),
  regions: (
    gridName: string,
    zoneName: string,
    regionParameter: string,
  ): Promise<CodeName[]> =>
    api.call('get_regions', gridName, zoneName, regionParameter),
  blockedWellParameters: (gridName: string): Promise<string[]> =>
    api.call('get_blocked_well_set_names', gridName),
  realizationParameters: (gridName: string): Promise<string[]> =>
    api.call('get_realization_parameters', gridName),
  blockedWellLogParameters: (
    gridName: string,
    blockedWellName: string,
  ): Promise<string[]> =>
    api.call('get_blocked_well_logs', gridName, blockedWellName),
  facies: (
    gridName: string,
    blockedWellName: string,
    blockedWellLogName: string,
    regionParameter: Optional<string>,
  ): Promise<RmsFacies[]> =>
    api.call(
      'get_facies_table_from_blocked_well_log',
      gridName,
      blockedWellName,
      blockedWellLogName,
      regionParameter,
    ),
  truncationPolygons: <
    P extends PolygonSpecification,
    T extends TruncationRuleDescription<P>,
  >(
    specification: T,
  ): Promise<PolygonDescription[]> =>
    api.call('get_truncation_map_polygons', specification),
  trendParameters: (gridName: string): Promise<string[]> =>
    api.call('get_rms_trend_parameters', gridName),
  trendMapZones: (): Promise<Record<string, string[]>> =>
    api.call('get_rms_trend_map_zones'),
  probabilityCubeParameters: (gridName: string): Promise<ProbabilityCube[]> =>
    api.call('get_probability_cube_parameters', gridName),
  constants: (constantName: string, constantType: string): Promise<Constants> =>
    api.call('get_constant', constantName, constantType),
  options: (name: string): Promise<string[]> => api.call('get_options', name),
  gridSize: (name: string): Promise<[number, number, number]> =>
    api.call('get_grid_size', name),
  simulationBoxOrigin: (
    name: string,
    rough = false,
  ): Promise<SimulationBoxSize> =>
    api.call('get_simulation_box_size', name, rough),
  simulateGaussianField: (
    field: GaussianRandomFieldSpecification,
  ): Promise<number[][]> => api.call('simulate_gaussian_field', field),
  simulateRealization: <P extends PolygonSpecification>(
    fields: GaussianRandomFieldSpecification[],
    truncationRule: TruncationRuleDescription<P>,
  ): Promise<{
    faciesMap: number[][]
    fields: { name: string; data: number[][] }[]
  }> => api.call('simulate_realization', fields, truncationRule),
  averageProbabilityCubes: (
    gridName: string,
    probabilityCubeParameters: string[],
    zoneNumber: number,
    regionParameter: Optional<string> = null,
    regionNumber: Optional<number> = null,
  ): Promise<AverageParameterProbabilities> =>
    api.call(
      'calculate_average_of_probability_cube',
      gridName,
      probabilityCubeParameters,
      zoneNumber,
      regionParameter,
      regionNumber,
    ),
  openWikiHelp: (): Promise<void> => api.call('open_wiki_help'),
  isApsModelValid: (
    fileContent: string,
  ): Promise<{ valid: boolean; error: string }> =>
    api.call('is_aps_model_valid', fileContent),
  exists: (path: string, hasParent = false): Promise<boolean> =>
    api.call('exists', path, hasParent),
  save: (path: string, content: string, prettify = true): Promise<boolean> =>
    api.call(prettify ? 'save_model' : 'save_file', path, content),
  saveModel: (model: string, paths: Paths): Promise<boolean> =>
    api.call(
      'dump_aps_model',
      model,
      paths.model,
      paths.fmuConfig,
      paths.probabilityDistribution,
    ),
  hasFmuUpdatableValues: (model: string): Promise<boolean> =>
    api.call('has_fmu_updatable_values', model),
  loadFile: (path: string): Promise<string | null> =>
    api.call('load_file', path),
  apsFmuConfig: (useConfig: boolean): Promise<[string, string, string]> =>
    api.call('get_aps_fmu_config', useConfig),
  createAPSFmuConfigFile: (setApsFmuConfig: boolean): Promise<void> =>
    api.call('set_aps_fmu_config', setApsFmuConfig),
  chooseDir: (
    mode: 'save' | 'load',
    suggestion = '',
  ): Promise<string | null> =>
    typeof rms !== 'undefined'
      ? rms.chooseDir(mode, suggestion)
      : new Promise((resolve) => resolve(null)),
  chooseFile: (
    mode: 'save' | 'load',
    filter: string,
    suggestion = '',
  ): Promise<string | null> =>
    typeof rms !== 'undefined'
      ? rms.chooseFile(mode, filter, suggestion)
      : new Promise((resolve) => resolve(null)),
  // Methods related to state migration
  canMigrate: (
    fromVersion: string | undefined,
    toVersion: string,
  ): Promise<boolean> => api.call('can_migrate_state', fromVersion, toVersion),
  migrate: (
    state: string,
    fromVersion: string,
    toVersion: string | null,
  ): Promise<{ state: any; errors: string }> =>
    api.call('migrate_state', state, fromVersion, toVersion),

  // Methods that are ONLY intended to be available in development mode, or when running the plugin locally
  loadPluginDotMaster: (): Promise<{ parameters: Job[] }> =>
    api.call('load_dot_master'),
  runAPSWorkflow: (state: string): Promise<void> =>
    api.call('run_aps_workflow', state),
}
