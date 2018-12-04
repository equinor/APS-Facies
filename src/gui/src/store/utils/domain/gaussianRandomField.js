import { ZoneRegionDependent } from '@/store/utils/domain/bases'
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
    gridAzimuth: 0.0,
    gridSize: {
      x: 100, y: 100, z: 1,
    },
    simulationBox: {
      x: 1000, y: 1000, z: 10,
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
    vertical = 10,
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
    type = null,
    azimuth = 0,
    azimuthUpdatable = false,
    stackAngle = 0,
    stackAngleUpdatable = false,
    migrationAngle = 0,
    migrationAngleUpdatable = false,
    stackingDirection = null,
    parameter = null,
    curvature = 0,
    curvatureUpdatable = false,
    originX = 0,
    originXUpdatable = false,
    originY = 0,
    originYUpdatable = false,
    originZ = 0,
    originZUpdatable = false,
    originType = 'ABSOLUTE',
    relativeSize = 0,
    relativeSizeUpdateble = false,
    relativeStdDev = 0,
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
    this.curvature = updatableValue(curvature, !!curvatureUpdatable)
    this.origin = {
      x: updatableValue(originX, !!originXUpdatable),
      y: updatableValue(originY, !!originYUpdatable),
      z: updatableValue(originZ, !!originZUpdatable),
      type: originType
    }
    this.relativeSize = updatableValue(relativeSize, !!relativeSizeUpdateble)
    this.relativeStdDev = updatableValue(relativeStdDev, !!relativeStdDevUpdatable)
  }
}

class GaussianRandomField extends ZoneRegionDependent {
  constructor ({ name, variogram = null, trend = null, settings = null, _id, zone, region = null }) {
    super({ _id, zone, region })
    this.name = name
    this.variogram = variogram || new Variogram({})
    this.trend = trend || new Trend({})
    this.settings = settings || defaultSettings()
    // TODO: Make sure the class knows that the data is actually from the CURRENT specification
    this._data = []
  }
}

export {
  Variogram,
  Trend,
  GaussianRandomField,
}
