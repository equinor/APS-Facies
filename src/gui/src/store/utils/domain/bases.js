import uuidv4 from 'uuid/v4'
import { isEmpty } from '@/utils'

class DistinctItem {
  constructor ({ _id }) {
    this._id = _id || uuidv4()
  }
  get id () { return this._id }
  set id (value) { throw new Error('id cannot be set') }
}

class DiscreteItem extends DistinctItem {
  constructor ({ code, name, _id }) {
    super({ _id })
    this.code = code
    this.name = name
  }
}

class SelectableItem extends DiscreteItem {
  constructor ({ code, name, _id, selected }) {
    super({ code, name, _id })
    this.selected = selected
  }
}

class ZoneRegionDependent extends DistinctItem {
  constructor ({ _id, zone, region = null }) {
    super({ _id })
    this.parent = {
      zone: typeof zone === 'string' ? zone : zone.id,
      region: isEmpty(region)
        ? null
        : typeof region === 'string' ? region : region.id,
    }
  }
}

export {
  DiscreteItem,
  SelectableItem,
  ZoneRegionDependent,
}
