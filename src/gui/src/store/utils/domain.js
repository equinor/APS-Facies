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

class Facies extends DiscreteItem {
  constructor ({ code, name, color, _id }) {
    super({ code, name, _id })
    this.color = color
  }
}

class SelectableItem extends DiscreteItem {
  constructor ({ code, name, _id, selected }) {
    super({ code, name, _id })
    this._selected = !!selected
  }

  get selected () { return this._selected }
  set selected (selected) { this._selected = selected }
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
