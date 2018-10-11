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

export {
  Region,
  Zone,
  Facies,
}
