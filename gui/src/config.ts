export function isDevelopmentBuild(): boolean {
  return import.meta.env.NODE_ENV === 'development'
}

export const DEFAULT_SIZE = {
  max: {
    width: Number.POSITIVE_INFINITY,
    height: Number.POSITIVE_INFINITY,
  },
  width: 200,
  height: 200,
}

export const DEFAULT_POINT_SIZE = 1.2

export const DEFAULT_IMPORT_FIELDS_IN_FMU = false

export const DEFAULT_RUN_FMU_MODE = false

export const DEFAULT_RUN_ONLY_FMU_UPDATE = false

export const DEFAULT_CREATE_FMU_GRID = isDevelopmentBuild()

export const DEFAULT_FIELD_FORMAT = 'roff'

export const DEFAULT_EXTRAPOLATION_METHOD = 'extend_layer_mean'

export const DEFAULT_FMU_SIMULATION_GRID_NAME = 'ERTBOX'

export const DEFAULT_COLOR_SCALE = 'Rainbow'

export const DEFAULT_COLOR_LIBRARY = 'Facies'

export const COLOR_SCALES = [
  'Blackbody',
  'Bluered',
  'Blues',
  'Cividis',
  'Earth',
  'Electric',
  'Greens',
  'Greys',
  'Hot',
  'Jet',
  'Picnic',
  'Portland',
  'Rainbow',
  'RdBu',
  'Reds',
  'Viridis',
  'YlGnBu',
  'YlOrRd',
] as const

export type AllowedColorScales = (typeof COLOR_SCALES)[number]

export const DEFAULT_CROSS_SECTION = {
  type: 'IJ',
}

export const DEFAULT_CUBIC_LEVELS = 3

export const DEFAULT_FACIES_REALIZATION_PARAMETER_NAME = 'aps'

export const DEFAULT_FACIES_AUTOFILL = isDevelopmentBuild()

export const DEFAULT_AUTOFILL_OBSERVED_FACIES = true

export const DEFAULT_TIME_UNTIL_MESSAGE_DISMISSAL = 10000

export const ERROR_TOLERANCE = 0.0001

export const DEFAULT_TRUNCATION_RULE_TEMPLATE_PREVIEW_SIZE = {
  width: 100,
  height: 100,
}

export const TREND_NOT_IMPLEMENTED_PREVIEW_VISUALIZATION: (
  | 'RMS_PARAM'
  | 'RMS_TRENDMAP'
  | 'NONE'
  | 'LINEAR'
  | 'ELLIPTIC'
  | 'ELLIPTIC_CONE'
  | 'HYPERBOLIC'
)[] = ['RMS_PARAM', 'RMS_TRENDMAP', 'NONE']

export const DEFAULT_MODEL_FILE_NAMES = {
  model: 'myApsExport.xml',
  fmuConfig: 'aps_fmu_params.yaml',
  probabilityDistribution: 'aps_dist.txt',
}

export const DEFAULT_EXPORT_FMU_CONFIG_FILES = false

export const DEFAULT_USE_RESIDUAL_FIELDS = false

export const DEFAULT_USE_NON_STANDARD_FMU_DIRS = false

export const DEFAULT_EXPORT_ERTBOX_GRID = true
