module.exports = {
  'DEFAULT_SIZE': {
    'max': {
      'width': Number.POSITIVE_INFINITY,
      'height': Number.POSITIVE_INFINITY,
    },
    'width': 200,
    'height': 200,
  },
  'DEFAULT_POINT_SIZE': 1.2,
  'DEFAULT_COLOR_SCALE': 'Viridis',
  'DEFAULT_CROSS_SECTION': {
    'type': 'IJ',
    'position': 0.5,
  },
  'DEFAULT_CUBIC_LEVELS': 3,
  'DEFAULT_FACIES_REALIZATION_PARAMETER_NAME': 'aps',
  'DEFAULT_FACIES_AUTOFILL': process.env.NODE_ENV === 'develop',
}
