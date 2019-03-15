import cloneDeep from 'lodash/cloneDeep'

import { ZoneRegionDependent, Named, BaseItem } from '@/store/utils/domain/bases'
import { newSeed } from '@/utils'

const updatableValue = (value = null, updatable = false) => {
  return { value, updatable }
}

const defaultSettings = () => {
  return {
    crossSection: {
      type: 'IJ',
      relativePosition: 0.5,
    },
    gridModel: {
      use: false,
      size: {
        x: 100, y: 100, z: 1,
      },
    },
    seed: newSeed(),
  }
}

class Variogram {
  constructor ({
    type = 'SPHERICAL',
    // Angles
    azimuth = 0,
    azimuthUpdatable = false,
    dip = 0,
    dipUpdatable = false,
    // Ranges
    main = 1000,
    mainUpdatable = false,
    perpendicular = 1000,
    perpendicularUpdatable = false,
    vertical = 5,
    power = 1.5,
    verticalUpdatable = false,
    powerUpdatable = false
  }) {
    this.type = 'SPHERICAL'
    this.angle = {
      azimuth: updatableValue(azimuth, !!azimuthUpdatable),
      dip: updatableValue(dip, !!dipUpdatable),
    }
    this.range = {
      main: updatableValue(main, !!mainUpdatable),
      perpendicular: updatableValue(perpendicular, !!perpendicularUpdatable),
      vertical: updatableValue(vertical, !!verticalUpdatable),
    }
    this.power = updatableValue(power, !!powerUpdatable)
  }
}

class Trend {
  constructor ({
    use = false,
    type = 'LINEAR',
    azimuth = 0,
    azimuthUpdatable = false,
    stackAngle = 2.0,
    stackAngleUpdatable = false,
    migrationAngle = 0,
    migrationAngleUpdatable = false,
    stackingDirection = 'PROGRADING',
    parameter = null,
    curvature = 1,
    curvatureUpdatable = false,
    originX = 0.5,
    originXUpdatable = false,
    originY = 0.5,
    originYUpdatable = false,
    originZ = 0.5,
    originZUpdatable = false,
    originType = 'RELATIVE',
    relativeSize = 0,
    relativeSizeUpdatable = false,
    relativeStdDev = 0.001,
    relativeStdDevUpdatable = false
  }) {
    this.use = use
    this.type = type
    this.angle = {
      azimuth: updatableValue(azimuth, !!azimuthUpdatable),
      stacking: updatableValue(stackAngle, !!stackAngleUpdatable),
      migration: updatableValue(migrationAngle, !!migrationAngleUpdatable)
    }
    this.stackingDirection = stackingDirection
    this.parameter = parameter
    if (this.type === 'HYPERBOLIC' && curvature <= 1) curvature = 1.01
    this.curvature = updatableValue(curvature, !!curvatureUpdatable)
    this.origin = {
      x: updatableValue(originX, !!originXUpdatable),
      y: updatableValue(originY, !!originYUpdatable),
      z: updatableValue(originZ, !!originZUpdatable),
      type: originType
    }
    this.relativeSize = updatableValue(relativeSize, !!relativeSizeUpdatable)
    this.relativeStdDev = updatableValue(relativeStdDev, !!relativeStdDevUpdatable)
  }
}

class GaussianRandomField extends ZoneRegionDependent(Named(BaseItem)) {
  constructor ({ variogram = null, trend = null, settings = null, ...rest }) {
    super(rest)
    this.variogram = variogram || new Variogram({})
    this.trend = trend || new Trend({})
    this.settings = settings || defaultSettings()
    // TODO: Make sure the class knows that the data is actually from the CURRENT specification
    //   E.g. use a hash of the specification (variogram, trend, and settings)
    this._data = []
  }

  get simulated () {
    return this._data.length > 0 && this._data[0].length > 0
  }

  specification ({ rootGetters } = {}) {
    return {
      name: this.name,
      variogram: this.variogram,
      trend: this.trend,
      settings: {
        ...rootGetters ? cloneDeep(rootGetters.simulationSettings()) : {},
        ...this.settings
      },
    }
  }
}

export {
  Variogram,
  Trend,
  GaussianRandomField,
}
