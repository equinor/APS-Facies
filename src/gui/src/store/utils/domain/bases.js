import uuidv4 from 'uuid/v4'
import { isEmpty } from '@/utils'
import { getId } from '@/utils/typing'

class BaseItem {
  constructor ({ _id }) {
    this._id = _id || uuidv4()
  }
  get id () { return this._id }
  set id (value) { throw new Error('id cannot be set') }
}

const Named = superclass => class extends superclass {
  constructor ({ name, ...rest }) {
    super(rest)
    if (!name) throw new Error('Missing \'name\'')
    this.name = name
  }
}

const CodeName = superclass => class extends Discrete(Named(superclass)) {
  constructor ({ ...rest }) {
    super(rest)
  }
}

const Discrete = superclass => class extends superclass {
  constructor ({ code, ...rest }) {
    super(rest)
    if (!code) throw new Error('Missing \'code\'')
    this.code = code
  }
}

const Selectable = superclass => class extends superclass {
  constructor ({ selected = false, ...rest }) {
    super(rest)
    this.selected = selected
  }
}

const ZoneRegionDependent = superclass => class extends superclass {
  constructor ({ zone, region = null, parent = { zone: null, region: null }, ...rest }) {
    super(rest)
    zone = zone || parent.zone
    region = region || parent.region
    zone = getId(zone)
    if (!zone) throw new Error('Missing \'zone\', or \'parent.zone\'')
    this.parent = {
      zone,
      region: isEmpty(region)
        ? null
        : typeof region === 'string' ? region : region.id,
    }
  }
}

const mix = superclass => new MixinBuilder(superclass)

class MixinBuilder {
  constructor (superclass) {
    this.superclass = superclass
  }

  with (...mixins) {
    return mixins.reduce((c, mixin) => mixin(c), this.superclass)
  }
}

export {
  mix,
  BaseItem,
  CodeName,
  Named,
  Discrete,
  Selectable,
  ZoneRegionDependent,
}
