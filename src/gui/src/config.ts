export const DEFAULT_SIZE = {
  'max': {
    'width': Number.POSITIVE_INFINITY,
    'height': Number.POSITIVE_INFINITY,
  },
  'width': 200,
  'height': 200,
}

export const DEFAULT_POINT_SIZE = 1.2

export const DEFAULT_RUN_FMU_MODE = false

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
]

export const DEFAULT_CROSS_SECTION = {
  'type': 'IJ',
}

export const DEFAULT_CUBIC_LEVELS = 3

export const DEFAULT_FACIES_REALIZATION_PARAMETER_NAME = 'aps'

export const DEFAULT_FACIES_AUTOFILL = process.env.NODE_ENV === 'develop'

export const DEFAULT_TIME_UNTIL_MESSAGE_DISMISSAL = 10000

export const ERROR_TOLERENCE = 0.0001

export const DEFAULT_TRUNCATION_RULE_TEMPLATE_PREVIEW_SIZE = {
  width: 100,
  height: 100,
}

export const TREND_NOT_IMPLEMENTED_PREVIEW_VISUALIZATION = [
  'RMS_PARAM',
  'NONE',
]