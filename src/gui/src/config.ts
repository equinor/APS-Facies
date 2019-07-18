export const DEFAULT_SIZE = {
  'max': {
    'width': Number.POSITIVE_INFINITY,
    'height': Number.POSITIVE_INFINITY,
  },
  'width': 200,
  'height': 200,
}

export const DEFAULT_POINT_SIZE = 1.2

export const DEFAULT_COLOR_SCALE = 'Viridis'

export const DEFAULT_CROSS_SECTION = {
  'type': 'IJ',
  'position': 0.5,
}

export const DEFAULT_CUBIC_LEVELS = 3

export const DEFAULT_FACIES_REALIZATION_PARAMETER_NAME = 'aps'

export const DEFAULT_FACIES_AUTOFILL = process.env.NODE_ENV === 'develop'

export const DEFAULT_TIME_UNTIL_MESSAGE_DISMISSAL = 10000
