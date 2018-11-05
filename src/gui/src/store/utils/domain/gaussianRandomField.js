import { ZoneRegionDependent } from '@/store/utils/domain/bases'

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
      x: 100, y: 100, z: 1,
    },
    seed: {
      value: 0, autoRenew: true
    },
  }
}

class Variogram {
  constructor ({
    type = 'SPHERICAL',
    // Angles
    azimuth = 0,
    dip = 0,
    // Ranges
    main = 1000,
    perpendicular = 1000,
    vertical = 10,
    power = null,
  }) {
    this.type = 'SPHERICAL'
    this.angle = {
      azimuth: updatableValue(azimuth),
      dip: updatableValue(dip),
    }
    this.range = {
      main: updatableValue(main),
      perpendicular: updatableValue(perpendicular),
      vertical: updatableValue(vertical),
    }
    this.power = updatableValue(power)
  }
}

class Trend {
  constructor () {
    this.use = false
    this.type = null
    this.angle = {
      azimuth: updatableValue(),
      stacking: updatableValue(),
      migration: updatableValue(),
    }
    this.stackingDirection = null
    this.parameter = null
    this.curvature = updatableValue()
    this.origin = {
      x: updatableValue(),
      y: updatableValue(),
      z: updatableValue(),
      type: '',
    }
    this.relativeSize = updatableValue()
    this.relativeStdDev = updatableValue()
  }
}

export class GaussianRandomField extends ZoneRegionDependent {
  constructor ({ name, _id, zone, region = null }) {
    super({ _id, zone, region })
    this.name = name
    this.variogram = new Variogram({})
    this.trend = new Trend()
    this.settings = defaultSettings()
    // TODO: Make sure the class knows that the data is actually from the CURRENT specification
    this._data = []
  }
}
