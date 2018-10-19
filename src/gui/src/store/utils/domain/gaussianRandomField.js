import uuidv4 from 'uuid/v4'

class DiscreteItem {
  constructor ({ code, name, _id }) {
    this._id = _id || uuidv4()
    this.code = code
    this.name = name
  }
  get id () { return this._id }
  set id (value) { throw new Error('id cannot be set') }
}

class SelectableItem extends DiscreteItem {
  constructor ({ code, name, _id, selected }) {
    super({ code, name, _id })
    this.selected = selected
  }
}

class Facies extends SelectableItem {
  constructor ({ code, name, color, selected, _id, probabilityCube = null, previewProbability = null }) {
    super({ code, name, selected, _id })
    this.color = color
    // this.probability = {
    //   cubeParameter: probabilityCube,
    //   preview: previewProbability,
    // }
    this.probabilityCube = probabilityCube
    this.previewProbability = previewProbability
  }
}

class Region extends SelectableItem {
  constructor ({ code, name, _id, selected }) {
    super({ code, name, _id, selected })
  }
}

class Zone extends SelectableItem {
  constructor ({ code, name, selected }) {
    super({ code, name, selected })
    this.regions = {}
  }
}

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

export class GaussianRandomField {
  constructor ({ name, zone, region = null }) {
    this.name = name
    this.variogram = new Variogram({})
    this.trend = new Trend()
    this.settings = defaultSettings()
    this.parent = {
      zone: typeof zone === 'string' ? zone : zone.id,
      region: typeof region === 'string' ? region : region.id,
    }
  }
}
